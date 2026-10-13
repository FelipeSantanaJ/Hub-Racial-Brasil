"""Carteira assinada = só CLT; estatutário/militar à parte (R19; Ponto de parada 3)."""
import duckdb
import pandas as pd
import pytest

from src.processing import agregacoes_pnadc as ag
from tests.golden.microdado_sintetico import gerar_deflator, gerar_microdado, gravar_extrato


@pytest.fixture(scope="module")
def con(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("carteira")
    micro = gerar_microdado()
    ocup = micro["VD4002"] == "1"
    codigos = [f"{i:02d}" for i in range(1, 11)]
    micro.loc[ocup, "VD4009"] = [codigos[i % 10] for i in range(int(ocup.sum()))]
    glob = gravar_extrato(micro, tmp / "raw")
    deflator = tmp / "deflator.parquet"
    gerar_deflator().to_parquet(deflator, index=False)
    c = duckdb.connect()
    c.execute(ag.CRIAR_BASE.replace(ag.PARQUET_GLOB, glob.replace("\\", "/"))
              .replace(ag.DEFLATOR_PATH, str(deflator).replace("\\", "/")))
    return c


def test_mapeamento_vd4009(con):
    pares = con.execute("""SELECT vinculo_trabalho, tem_carteira_assinada, COUNT(*) n FROM base
                           WHERE condicao_ocupacao = '1' GROUP BY 1, 2 ORDER BY 1, 2""").df()
    esperado = {("CLT", True), ("Sem carteira", False), ("Estatutário/militar", None),
                ("Empregador", None), ("Conta própria", None), ("Familiar auxiliar", None)}
    obtido = {(v, None if pd.isna(t) else bool(t)) for v, t in zip(pares["vinculo_trabalho"],
                                                                pares["tem_carteira_assinada"])}
    assert obtido == esperado


def test_pct_com_carteira_so_clt(con, tmp_path):
    original = ag.OUTPUT_DIR
    ag.OUTPUT_DIR = tmp_path
    try:
        ag.gerar_informalidade(con)
    finally:
        ag.OUTPUT_DIR = original
    inf = pd.read_parquet(tmp_path / "informalidade.parquet")
    br = inf[inf["nivel_geografico"] == "brasil"]
    esperado = con.execute("""
        SELECT 100 * SUM(peso) FILTER (WHERE vinculo_trabalho = 'CLT')
                   / SUM(peso) FILTER (WHERE vinculo_trabalho IN ('CLT', 'Sem carteira')) AS clt,
               100 * SUM(peso) FILTER (WHERE vinculo_trabalho = 'Estatutário/militar')
                   / SUM(peso) FILTER (WHERE vinculo_trabalho IN ('CLT', 'Sem carteira', 'Estatutário/militar')) AS est
        FROM base""").fetchone()
    # agregado das células do nível Brasil = conta direta sobre a base
    clt = (br["pct_com_carteira"] * br["pop_empregados"]).sum() / br["pop_empregados"].sum()
    assert clt == pytest.approx(esperado[0])
    assert {"pct_estatutario_militar", "n_estatutario_militar", "publicavel_estatutario_militar"} <= set(inf.columns)
    assert 0 < esperado[1] < 100
