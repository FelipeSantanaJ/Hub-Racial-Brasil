"""Testes do B3: FDR (Benjamini-Hochberg) por família e Welch com EP da média."""
import numpy as np
import pandas as pd
import pytest
from statsmodels.stats.multitest import multipletests

from src.inference.multiplicidade import adicionar_fdr
from src.utils import pnadc_core


def test_fdr_por_familia_bate_com_statsmodels():
    df = pd.DataFrame({
        "ano": [1, 1, 1, 2, 2],
        "p_valor": [0.01, 0.04, 0.03, 0.04, np.nan],
    })
    out = adicionar_fdr(df, ["ano"])
    esperado_1 = multipletests([0.01, 0.04, 0.03], method="fdr_bh")[1]
    assert out.loc[[0, 1, 2], "p_valor_bh"].to_numpy() == pytest.approx(esperado_1)
    # família de tamanho 1: ajustado = nominal; NaN fica fora e não é significativo
    assert out.loc[3, "p_valor_bh"] == pytest.approx(0.04)
    assert np.isnan(out.loc[4, "p_valor_bh"]) and not out.loc[4, "significativo_fdr"]
    assert out["significativo_nominal"].tolist() == [True, True, True, True, False]


def test_fdr_tabela_inteira_e_prefixo():
    df = pd.DataFrame({"did_p_valor": [0.001] + [0.5] * 39})
    out = adicionar_fdr(df, None, coluna_p="did_p_valor", prefixo="did_")
    assert out["did_p_valor_bh"].iloc[0] == pytest.approx(0.04)
    assert out["did_significativo_fdr"].sum() == 1


def test_fdr_quarenta_testes_marginais_nao_sobrevivem():
    """Padrão do Desenho B (R3): 4 de 40 com p≈0,03-0,04 não sobrevivem ao BH."""
    p = np.r_[[0.041, 0.030, 0.035, 0.044], np.linspace(0.06, 0.99, 36)]
    out = adicionar_fdr(pd.DataFrame({"p_valor": p}), None)
    assert out["significativo_nominal"].sum() == 4
    assert out["significativo_fdr"].sum() == 0


def test_tabela_hiatos_gl_welch_e_colunas_novas():
    rng = np.random.default_rng(11)
    n = 600
    df = pd.DataFrame({
        "y": np.r_[rng.normal(10, 2, n // 2), rng.normal(11, 2, n // 2)],
        "g": ["A"] * (n // 2) + ["B"] * (n // 2), "w": 1.0,
        "upa": np.arange(n), "est": 0,
    })
    t = pnadc_core.tabela_hiatos_significancia(df, "y", "g", "A", peso="w", upa="upa", estrato="est")
    # AAS e pesos iguais: n_ef = n − 1 por grupo, ep iguais => df ≈ 2(n_ef − 1) ~ 596
    assert t.loc["B", "gl_welch"] == pytest.approx(2 * (n // 2 - 2), rel=0.05)
    for c in ("ep_media", "ep_hiato", "n_amostra"):
        assert c in t.columns
    assert t.loc["B", "n_amostra"] == n // 2
