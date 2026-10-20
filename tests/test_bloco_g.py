"""Bloco G (Onda 5): os estimadores recuperam efeitos conhecidos em dados simulados e o EMD analítico bate com a
simulação."""
import numpy as np
import pandas as pd
import pytest

from src.processing import bloco_g as G


def _painel_es(efeito: float, n: int = 60, semente: int = 1) -> pd.DataFrame:
    rng = np.random.default_rng(semente)
    linhas = []
    for i in range(n):
        trat = int(i < n // 2)
        a_i = rng.normal(40, 8)
        for ano in G.ANOS:
            y = a_i + 0.3 * (ano - 2009) + efeito * trat * (ano >= 2013) + rng.normal(0, 1)
            linhas.append({"CO_IES": f"i{i}", "_u": f"i{i}", "ano": ano, "tratada": trat, "peso": 100 + 10 * i, "Y1": y,
                           "coorte": 2013 if trat else 0})
    return pd.DataFrame(linhas)


def test_event_study_recupera_efeito_e_sem_pre_tendencia():
    df = _painel_es(5.0)
    res = G.event_study(df, "Y1")
    est, ep = G.contraste(res, G.JANELAS_G1["2016–2019"])
    assert est == pytest.approx(5.0, abs=4 * ep)
    pre, _ = G.contraste(res, [2009, 2010, 2011])
    assert abs(pre) < 4 * ep
    assert 0 < ep < 1


def test_bootstrap_proximo_do_cr1():
    df = _painel_es(0.0)
    res = G.event_study(df, "Y1")
    _, ep = G.contraste(res, G.JANELAS_G1["2016–2019"])
    b = G.bootstrap_es(df, "Y1", {"2016–2019": G.JANELAS_G1["2016–2019"]}, n_boot=150)
    assert np.std(b["2016–2019"], ddof=1) == pytest.approx(ep, rel=0.4)


@pytest.mark.parametrize("rho", [0.0, 0.7])
def test_var_ar1_bate_com_simulacao(rho):
    rng = np.random.default_rng(3)
    unidade = np.repeat(np.arange(30), 15)
    tempo = np.tile(np.arange(2009, 2024), 30)
    a = rng.normal(size=len(unidade))
    s2 = rng.uniform(0.5, 2.0, 30)
    dp = np.sqrt(G.var_ar1(a, unidade, tempo, s2, rho))
    assert G.simular_ar1(a, unidade, tempo, s2, rho, n_sim=4000) == pytest.approx(dp, rel=0.06)


def test_callaway_santanna_recupera_efeito_escalonado():
    rng = np.random.default_rng(2)
    linhas = []
    for i in range(90):
        coorte = [0, 2011, 2014][i % 3]
        a_i = rng.normal(40, 5)
        for ano in G.ANOS:
            y = a_i + 0.5 * (ano - 2009) + (3.0 if coorte and ano >= coorte else 0.0) + rng.normal(0, 0.5)
            linhas.append({"CO_IES": f"i{i}", "ano": ano, "coorte": coorte, "peso": 1.0, "Y1": y})
    att = G.cs_att(pd.DataFrame(linhas), "Y1", "nunca")
    ag = G.cs_agregado(att)
    assert ag["pós (t ≥ g, até 2019)"] == pytest.approx(3.0, abs=0.3)
    assert ag["e=-2"] == pytest.approx(0.0, abs=0.3)


def test_g4_recupera_beta():
    rng = np.random.default_rng(4)
    linhas = []
    expo = rng.uniform(0.0, 0.2, 27)
    for u in range(27):
        for t in range(40):
            lsm = 6.5 + 0.01 * t + 0.03 * np.sin(t / 3)
            h = 0.4 + 0.02 * u - 1.0 * expo[u] * lsm + 0.002 * t + rng.normal(0, 0.003)
            linhas.append({"uf": u + 11, "t": t, "ano": 2012 + t // 4, "pop2012": 1.0 + u, "E105": expo[u],
                           "ln_sm_real": lsm, "hiato": h, "amostra_ok": True})
    r = G.g4_estimar(pd.DataFrame(linhas), n_wild=199)
    assert r["beta"] == pytest.approx(-1.0, abs=4 * r["ep_cr1"])
    assert r["p_wild"] < 0.05
    assert r["ic_inferior"] <= -1.0 <= r["ic_superior"] or abs(r["beta"] + 1) < 4 * r["ep_cr1"]
