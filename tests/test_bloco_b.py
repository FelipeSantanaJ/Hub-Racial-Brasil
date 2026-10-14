"""Bloco B (Onda 2): Kitagawa da reclassificação, JMP, Deaton-Paxson, projeção condicional."""
import numpy as np
import pandas as pd
import pytest

from src.processing import bloco_b as B


def test_kitagawa_reclassificacao_soma_exata():
    k0 = {"m_Branca": 3000.0, "s_Preta": 0.15, "m_Preta": 1700.0, "s_Parda": 0.85, "m_Parda": 1800.0}
    k1 = {"m_Branca": 3300.0, "s_Preta": 0.20, "m_Preta": 2000.0, "s_Parda": 0.80, "m_Parda": 2100.0}
    d = B.decompor_kitagawa(k0, k1)
    assert d["composicao_preta_parda"] + d["dentro_dos_subgrupos"] == pytest.approx(d["variacao_ln_media_negra"])
    assert d["variacao_hiato_log"] == pytest.approx(d["variacao_ln_media_branca"] - d["variacao_ln_media_negra"])
    assert d["composicao_preta_parda"] < 0  # mais peso para o subgrupo de menor renda


def _jmp_micro(seed, efeito_negra, beta_educ, n=6000):
    rng = np.random.default_rng(seed)
    raca = rng.choice(["Branca", "Negra"], size=n)
    instr = rng.choice(list("1234567"), size=n, p=[.1, .2, .1, .2, .1, .1, .2])
    idade = rng.integers(18, 65, n)
    m = pd.DataFrame({"raca": raca, "instrucao": instr, "idade": idade, "regiao": rng.choice(list("12345"), size=n),
                      "sexo": rng.choice(["Homem", "Mulher"], size=n)})
    m["renda"] = np.exp(7 + beta_educ * instr.astype(int) / 7 - efeito_negra * (raca == "Negra") + rng.normal(0, .5, n))
    return m, rng.uniform(1, 3, n)


def test_jmp_componentes_somam_a_mudanca():
    m0, w0 = _jmp_micro(0, 0.30, 0.8)
    m1, w1 = _jmp_micro(1, 0.20, 1.0)
    cols = list(B._matriz_x(pd.concat([m0, m1])).columns)
    j0, j1 = B.jmp_componentes(m0, w0, cols), B.jmp_componentes(m1, w1, cols)
    # D = ΔX·β + Δθ·σ exato (regressão dos brancos com constante)
    assert j0["D"] == pytest.approx(float(j0["dX"] @ j0["beta"] + j0["dtheta"] * j0["sigma"]))
    d = B.jmp_mudanca(j0, j1)
    soma = d["caracteristicas"] + d["retornos"] + d["posicao_nao_associada"] + d["dispersao_residual"]
    assert soma == pytest.approx(d["variacao_total"])
    assert d["posicao_nao_associada"] < 0  # o "efeito Negra" simulado caiu de 0,30 para 0,20


def test_deaton_paxson_soma_zero_e_ortogonal_a_tendencia():
    anos = np.arange(2012, 2026)
    P = B.deaton_paxson(anos)
    rng = np.random.default_rng(4)
    gamma = P @ rng.normal(size=P.shape[1])  # efeitos de período implícitos
    assert gamma.sum() == pytest.approx(0.0, abs=1e-10)
    assert (gamma * (anos - anos.mean())).sum() == pytest.approx(0.0, abs=1e-9)


def test_ano_paridade():
    r = B.ano_paridade(60.0, 2026.0, -1.0, -1.5, -0.5)
    assert r["ano_central"] == pytest.approx(2086.0) and r["ano_mais_cedo"] == pytest.approx(2066.0)
    assert r["ano_mais_tarde"] == pytest.approx(2146.0) and r["data_finita"]
    r = B.ano_paridade(60.0, 2026.0, -1.0, -2.0, 0.3)
    assert np.isinf(r["ano_mais_tarde"]) and not r["data_finita"]


def test_apc_recupera_coorte_quando_periodo_e_so_ciclo():
    anos, idades = np.arange(2012, 2026), np.arange(25, 60)
    A, I = np.meshgrid(anos, idades, indexing="ij")
    A, I = A.ravel(), I.ravel()
    nasc = A - I
    ciclo = np.sin(anos)                                   # período: só ciclo ...
    t = anos - anos.mean()
    ciclo = ciclo - ciclo.mean() - t * (ciclo @ t) / (t @ t)  # ... sem nível nem tendência
    coorte_g = (nasc // 5) * 5
    efeito_coorte = -0.01 * (coorte_g - coorte_g.min())   # coortes novas: hiato menor
    efeito_idade = 0.004 * ((I // 5) * 5 - 25)
    y = 0.5 + efeito_idade + efeito_coorte + ciclo[A - anos.min()] * 0.02
    cel = pd.DataFrame({"ano": A, "idade": I, "nascimento": nasc, "log_hiato": y, "ep": 0.01,
                        "idade_grupo": (I // 5) * 5, "coorte_grupo": coorte_g})
    r = B.apc(cel, com_periodo=True).set_index("termo")["estimativa"]
    c0 = coorte_g.min()
    for g in sorted(set(coorte_g))[1:]:
        assert r[f"coorte_{g}"] == pytest.approx(-0.01 * (g - c0), abs=1e-8)
