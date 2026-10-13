"""Colunas de precisão (n_*, cv_*, publicavel*) nas tabelas de nível, sobre o microdado
sintético do golden-file (R8; Ponto de parada 3). Só confere estrutura e coerência: os
valores do CV são testados contra a linearização em tests/test_precisao.py."""
import duckdb
import numpy as np
import pandas as pd
import pytest

from src.processing import agregacoes_pnadc as ag
from tests.golden.microdado_sintetico import gerar_deflator, gerar_microdado, gravar_extrato

# gerador → (arquivo, indicadores, coluna do valor do primeiro indicador)
TABELAS = {
    "gerar_renda": ("renda", ["renda"], "renda_habitual_real_media"),
    "gerar_renda_por_escolaridade": ("renda_por_escolaridade", ["renda"], "renda_habitual_real_media"),
    "gerar_renda_por_geracao": ("renda_por_geracao", ["renda"], "renda_habitual_real_media"),
    "gerar_renda_completa": ("renda_completa", ["renda"], "renda_habitual_real_media"),
    "gerar_renda_completa_geracao": ("renda_completa_geracao", ["renda"], "renda_habitual_real_media"),
    "gerar_renda_multidimensional_faixa": ("renda_multidimensional_faixa", ["renda"], "renda_habitual_real_media"),
    "gerar_renda_multidimensional_geracao": ("renda_multidimensional_geracao", ["renda"], "renda_habitual_real_media"),
    "gerar_escolaridade": ("escolaridade", ["populacao"], "populacao_estimada"),
    "gerar_ocupacao": ("ocupacao", ["desocupacao"], "taxa_desocupacao_pct"),
    "gerar_informalidade": ("informalidade", ["carteira", "estatutario_militar", "previdencia"], "pct_com_carteira"),
    "gerar_horas_trabalhadas": ("horas_trabalhadas", ["horas", "renda_hora"], "horas_semanais_media"),
    "gerar_alfabetizacao": ("alfabetizacao", ["alfabetizado"], "pct_alfabetizado"),
    "gerar_desalento_subutilizacao": ("desalento_subutilizacao", ["desalento", "forca_potencial"], "pct_desalento"),
    "gerar_sobrequalificacao": ("sobrequalificacao", ["sobrequalificado"], "pct_sobrequalificado"),
    "gerar_desocupacao_por_escolaridade": ("desocupacao_por_escolaridade", ["desocupacao"], "taxa_desocupacao_pct"),
}


@pytest.fixture(scope="module")
def saidas(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("prec")
    glob = gravar_extrato(gerar_microdado(), tmp / "raw")
    deflator = tmp / "deflator.parquet"
    gerar_deflator().to_parquet(deflator, index=False)
    sql = ag.CRIAR_BASE.replace(ag.PARQUET_GLOB, glob.replace("\\", "/")).replace(
        ag.DEFLATOR_PATH, str(deflator).replace("\\", "/"))
    saida = tmp / "processed"
    saida.mkdir()
    original = ag.OUTPUT_DIR
    ag.OUTPUT_DIR = saida
    try:
        con = duckdb.connect()
        con.execute(sql)
        for gerador in TABELAS:
            getattr(ag, gerador)(con)
    finally:
        ag.OUTPUT_DIR = original
    return {arq: pd.read_parquet(saida / f"{arq}.parquet") for arq, _, _ in TABELAS.values()}, saida


@pytest.mark.parametrize("gerador", list(TABELAS))
def test_colunas_e_regra(saidas, gerador):
    dfs, pasta = saidas
    arq, inds, valor = TABELAS[gerador]
    df = dfs[arq]
    for ind in inds:
        assert {f"n_{ind}", f"cv_{ind}", f"publicavel_{ind}"} <= set(df.columns)
        esperado = (df[f"n_{ind}"] >= 30) & (df[f"cv_{ind}"] <= 0.30) & df[f"cv_{ind}"].notna()
        assert (df[f"publicavel_{ind}"] == esperado).all()
        assert (df[f"cv_{ind}"].dropna() >= 0).all()
    assert (df["publicavel"] == df[f"publicavel_{inds[0]}"]).all()
    if "n_amostra" in df.columns:
        assert (df[f"n_{inds[0]}"] <= df["n_amostra"]).all()
    # quem tem valor publicado tem n > 0 no denominador
    assert (df.loc[df[valor].notna() & (df[valor] != 0), f"n_{inds[0]}"] > 0).all()
    import json
    meta = json.loads((pasta / f"{arq}.parquet._meta.json").read_text(encoding="utf-8"))
    assert meta["regra_supressao"]["n_minimo"] == 30 and meta["regra_supressao"]["cv_maximo"] == 0.30


def test_n_renda_conta_so_quem_tem_renda(saidas):
    """R8: n_amostra conta todas as pessoas da célula; n_renda só o denominador da média."""
    df = saidas[0]["renda"]
    assert (df["n_renda"] < df["n_amostra"]).mean() > 0.5


def test_peso_do_denominador(saidas):
    """peso_<ind> = Σ pesos de quem entra no indicador: ≤ população da célula; 14–17 sem renda."""
    df = saidas[0]["renda"]
    assert (df["peso_renda"] <= df["populacao_estimada"] + 1e-6).all()
    assert (df.loc[df["faixa_etaria"] == "14-17", "peso_renda"] == 0).all()
    assert ((df["peso_renda"] > 0) == (df["n_renda"] > 0)).all()
