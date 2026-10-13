"""Topo 10% / base 10% / quartis com o peso empatado nos limiares repartido (R9) e Amarela no
escopo 'brasil' de extremos (R10), sobre o microdado sintético do golden-file — cuja renda é
arredondada a R$ 1, logo tem empates."""
import duckdb
import numpy as np
import pandas as pd
import pytest

from src.processing import agregacoes_pnadc as ag
from tests.golden.microdado_sintetico import gerar_deflator, gerar_microdado, gravar_extrato

GERADORES = ["gerar_perfil_topo10_racial", "gerar_perfil_quartis_racial", "gerar_perfil_topo10_quartis_pretaparda",
             "gerar_perfil_topo10_quartis_indigena", "gerar_extremos_racial", "gerar_quartis_multi_racial"]
ARQUIVOS = ["perfil_topo10_racial", "perfil_quartis_racial", "perfil_topo10_racial_pretaparda",
            "perfil_quartis_racial_pretaparda", "perfil_topo10_racial_indigena", "perfil_quartis_racial_indigena",
            "extremos_distribuicao_racial", "extremos_renda_racial", "extremos_composicao_racial",
            "quartis_multi_racial"]


@pytest.fixture(scope="module")
def saidas(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("heaping")
    micro = gerar_microdado()
    # heaping forte: 20% dos ocupados declaram exatamente R$ 3.000
    rng = np.random.default_rng(7)
    com_renda = micro["VD4019"].notna().to_numpy()
    redondo = com_renda & (rng.random(len(micro)) < 0.20)
    for c in ("VD4016", "VD4017", "VD4019", "VD4020"):
        micro.loc[redondo, c] = 3000.0
    glob = gravar_extrato(micro, tmp / "raw")
    deflator = tmp / "deflator.parquet"
    gerar_deflator().assign(deflator_habitual=1.0, deflator_efetivo=1.0).to_parquet(deflator, index=False)
    sql = ag.CRIAR_BASE.replace(ag.PARQUET_GLOB, glob.replace("\\", "/")).replace(
        ag.DEFLATOR_PATH, str(deflator).replace("\\", "/"))
    saida = tmp / "processed"
    saida.mkdir()
    original = ag.OUTPUT_DIR
    ag.OUTPUT_DIR = saida
    try:
        con = duckdb.connect()
        con.execute(sql)
        for g in GERADORES:
            getattr(ag, g)(con)
    finally:
        ag.OUTPUT_DIR = original
    return {a: pd.read_parquet(saida / f"{a}.parquet") for a in ARQUIVOS}


@pytest.mark.parametrize("arquivo,alvo", [
    ("perfil_topo10_racial", 10), ("perfil_quartis_racial", 25), ("perfil_topo10_racial_pretaparda", 10),
    ("perfil_quartis_racial_pretaparda", 25), ("perfil_topo10_racial_indigena", 10),
    ("perfil_quartis_racial_indigena", 25), ("extremos_distribuicao_racial", 10),
    ("extremos_renda_racial", 10), ("quartis_multi_racial", 25)])
def test_fatia_captura_exatamente_o_alvo(saidas, arquivo, alvo):
    df = saidas[arquivo]
    assert len(df) > 0
    assert np.allclose(df["pct_populacao_capturada"], alvo, atol=1e-9)


@pytest.mark.parametrize("arquivo,chaves,col", [
    ("perfil_topo10_racial", ["ano", "trimestre", "raca_cor", "dimensao"], "pct_do_topo10"),
    ("perfil_quartis_racial", ["ano", "trimestre", "raca_cor", "quartil", "dimensao"], "pct_do_quartil"),
    ("quartis_multi_racial", ["ano", "trimestre", "recorte", "grupo", "quartil", "dimensao"], "pct_do_quartil"),
    ("extremos_distribuicao_racial", ["ano", "trimestre", "extremo", "escopo_limiar", "grupo_limiar"], "pct_do_extremo")])
def test_composicao_soma_100(saidas, arquivo, chaves, col):
    df = saidas[arquivo]
    soma = df.groupby(chaves)[col].sum()
    assert np.allclose(soma, 100, atol=1e-6)


def test_quatro_quartis_presentes(saidas):
    df = saidas["perfil_quartis_racial"]
    assert df.groupby(["ano", "trimestre", "raca_cor"])["quartil"].nunique().eq(4).all()


def test_extremos_brasil_inclui_amarela(saidas):
    d = saidas["extremos_distribuicao_racial"]
    br = d[d["escopo_limiar"] == "brasil"]
    assert set(br["raca_cor"]) == {"Branca", "Negra", "Indígena", "Amarela"}
    ge = d[d["escopo_limiar"] == "genero"]
    assert set(ge["raca_cor"]) == {"Branca", "Negra", "Indígena", "Amarela"}
    assert "Ignorado" not in set(d["raca_cor"])
