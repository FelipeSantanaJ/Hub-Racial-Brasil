"""Testes da população/renda de referência (Fase 2, item 7; Bloco F)."""
import duckdb
import numpy as np
import pandas as pd
import pytest

from src.processing import agregacoes_pnadc as ag
from src.utils import populacao as pop


def _bruto():
    return pd.DataFrame({
        "VD4002": ["1", "1", "1", "1", "2", None, "1", "1"],
        "V2009": [30.0, 17.0, 18.0, 45.0, 30.0, 70.0, 16.0, 64.0],
        "VD4016": [1000.0, 800.0, 0.0, np.nan, np.nan, np.nan, 500.0, 2500.0],
        "V1028": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
    })


def test_mascara_referencia_18mais():
    m = pop.na_populacao_referencia(_bruto())
    # 30 anos com renda: dentro; 17 anos: fora (idade); renda 0: fora; VD4016 nulo: fora
    assert m.tolist() == [True, False, False, False, False, False, False, True]


def test_mascara_sensibilidade_14mais():
    m = pop.na_populacao_referencia(_bruto(), idade_minima=14)
    assert m.tolist() == [True, True, False, False, False, False, True, True]


@pytest.mark.parametrize("definicao", [pop.REFERENCIA, pop.REFERENCIA_14MAIS])
def test_sql_e_pandas_sao_a_mesma_definicao(definicao):
    df = _bruto()
    via_sql = duckdb.connect().execute(f"SELECT COALESCE({definicao.sql('m')}, FALSE) AS f FROM df AS m").df()["f"]
    assert via_sql.tolist() == definicao.mascara(df).tolist()


def test_resumo_exclusoes_soma_100():
    r = pop.resumo_exclusoes(_bruto())
    assert r.sum() == pytest.approx(100.0)
    assert r["populacao_referencia"] == pytest.approx(100 * 9 / 27)  # pesos 1 e 8 entre os 18+ (1+3+4+5+6+8 = 27)


def test_filtro_sql_idade_invalida():
    with pytest.raises(ValueError):
        pop.filtro_sql(25)


def test_criar_base_tem_colunas_de_referencia():
    for col in (pop.COLUNA_RENDA_REAL, pop.COLUNA_RENDA_NOMINAL, pop.COLUNA_FLAG, pop.COLUNA_FLAG_14):
        assert f"AS {col}," in ag.CRIAR_BASE


def test_tabelas_principais_usam_a_mesma_populacao():
    """Gini, Theil, hiato e Oaxaca-Blinder filtram pela mesma função (fecha E3/R1)."""
    import inspect
    for fn in (ag.gerar_hiato_racial, ag.gerar_gini_por_raca, ag.gerar_theil_racial,
               ag.gerar_decomposicao_oaxaca_blinder, ag.gerar_decomposicao_oaxaca_blinder_indigena,
               ag.gerar_decomposicao_oaxaca_blinder_preta_parda):
        codigo = inspect.getsource(fn)
        assert "pop.filtro_sql()" in codigo and "renda_habitual_real" not in codigo, fn.__name__
