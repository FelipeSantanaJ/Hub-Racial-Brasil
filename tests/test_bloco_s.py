"""Bloco S (pendências da Onda 1): limites do S1.3, margens do S1.4, tendência HAC do S1.5."""
import numpy as np
import pandas as pd
import pytest

from src.inference import tendencia
from src.processing import bloco_s as S
from src.utils import pnadc_core


# --------------------------------------------------------------------------- S1.3
def test_quantil_ord_igual_ao_pnadc_core():
    rng = np.random.default_rng(0)
    y = np.round(rng.lognormal(7, 0.6, 3000), -2)
    w = rng.uniform(50, 500, 3000)
    o = np.argsort(y, kind="stable")
    cum = np.cumsum(w[o]) / w.sum()
    for q in (0.1, 0.25, 0.5, 0.9):
        assert S.quantil_ord(y[o], cum, q) == pnadc_core.quantil_ponderado(y, w, q)


def test_media_aparada_resposta_conhecida():
    v, w = np.arange(1, 11, dtype=float), np.ones(10)
    assert S.media_aparada(v, w, 0.2, "topo") == pytest.approx(4.5)   # 1..8
    assert S.media_aparada(v, w, 0.2, "base") == pytest.approx(6.5)   # 3..10
    assert S.media_aparada(v, w, 0.15, "topo") == pytest.approx((36 + 0.5 * 9) / 8.5)  # 9 pela metade
    assert S.media_aparada(v, w, 0.0, "topo") == pytest.approx(5.5)


def test_limites_colapsam_quando_todos_sao_observados():
    rng = np.random.default_rng(1)
    v = np.sort(rng.lognormal(7, 0.5, 2000))
    w = np.ones_like(v)
    lim = S.limites_grupo(1.0, v, w, y_max=v.max())
    m = v.mean()
    for k, (lo, hi) in lim.items():
        if k.startswith("media|"):
            assert lo == pytest.approx(m) and hi == pytest.approx(m)
        else:
            assert lo == pytest.approx(hi)


def test_limites_contem_o_hiato_verdadeiro_sob_selecao_positiva():
    """Renda potencial conhecida; quem fica de fora é sorteado com mais chance na base (seleção
    positiva). O hiato verdadeiro de todo o grupo tem de estar dentro dos limites S-b e S-c."""
    rng = np.random.default_rng(2)
    n = 40000
    pot_b = rng.lognormal(7.6, 0.6, n)
    pot_n = rng.lognormal(7.2, 0.6, n)

    def observa(pot, p_alvo):
        rank = pot.argsort().argsort() / len(pot)
        prob = np.clip(p_alvo + 0.5 * (rank - 0.5), 0.02, 0.98)  # mais chance de trabalhar no topo
        return rng.random(len(pot)) < prob

    ob, on = observa(pot_b, 0.7), observa(pot_n, 0.6)
    p = {"Branca": ob.mean(), "Negra": on.mean()}
    ords = {"Branca": (np.sort(pot_b[ob]), np.ones(ob.sum())), "Negra": (np.sort(pot_n[on]), np.ones(on.sum()))}
    y_max = np.quantile(np.r_[pot_b[ob], pot_n[on]], 0.99)
    lim = S._limites_todas(p, ords, y_max, "Negra")
    verdadeiro = 100 * (pot_b.mean() / pot_n.mean() - 1)
    for k in ("media|S-b seleção positiva", "media|S-c seleção positiva com piso no P10"):
        lo, hi = lim[k]
        assert lo <= verdadeiro <= hi, (k, lo, verdadeiro, hi)
    assert lim["media|S-a sem suposição (suporte [0, P99])"][0] <= lim["media|S-b seleção positiva"][0]


def test_c_imbens_manski():
    assert S.c_imbens_manski(0.0, 1.0) == pytest.approx(1.959964, abs=1e-4)
    assert S.c_imbens_manski(100.0, 1.0) == pytest.approx(1.644854, abs=1e-4)


def test_limites_hiato_com_zero_no_denominador():
    lo, hi = S.limites_hiato((100.0, 200.0), (0.0, 50.0))
    assert lo == pytest.approx(100.0) and np.isinf(hi)


# --------------------------------------------------------------------------- S1.4
def _micro_s14(seed=0, n=8000):
    rng = np.random.default_rng(seed)
    estrato = rng.integers(0, 40, n)
    raca = rng.choice(["Branca", "Negra", "Indígena"], p=[0.45, 0.5, 0.05], size=n)
    sexo = rng.choice(["Homem", "Mulher"], size=n)
    p1 = rng.random(n) < np.where(raca == "Branca", 0.65, 0.6)
    horas = np.where(p1, rng.choice([20, 30, 40, 44], size=n), np.nan)
    renda = np.where(p1, np.exp(7.4 + 0.4 * (raca == "Branca") + rng.normal(0, 0.6, n)), np.nan)
    return pd.DataFrame({"peso": rng.uniform(100, 900, n), "upa": estrato * 10 + rng.integers(0, 4, n),
                         "estrato": estrato, "raca": raca, "sexo": sexo, "em_p1": p1, "horas": horas,
                         "renda_principal": renda})


def test_s14_identidade_exata_e_ic():
    m = _micro_s14()
    for linha in S.margens_s14(m, 2026, 2):
        soma = linha["ln_pr_p1"] + linha["ln_horas"] + linha["ln_renda_hora"]
        assert soma == pytest.approx(linha["ln_renda_por_adulto"], abs=1e-12)
        for k in S.TERMOS_S14:
            assert linha[f"{k}_ic_inferior"] < linha[k] < linha[f"{k}_ic_superior"]
    # renda por adulto = Pr(P1) × horas × renda por hora × 4,345, nos níveis
    b = S.margens_s14(m, 2026, 2)[0]
    assert b["renda_por_adulto_branca"] == pytest.approx(
        b["pr_p1_pct_branca"] / 100 * b["horas_semanais_branca"] * b["renda_hora_branca"] * 4.345)


def test_s14_ep_contra_bootstrap_de_upa():
    """EP linearizado do termo de Pr(P1) ≈ bootstrap simples de UPAs (um estrato, muitas UPAs)."""
    rng = np.random.default_rng(5)
    n_upa, por = 400, 15
    upa = np.repeat(np.arange(n_upa), por)
    ef = rng.normal(0, 0.15, n_upa)[upa]
    raca = rng.choice(["Branca", "Negra"], size=len(upa))
    p1 = rng.random(len(upa)) < np.clip(0.6 + ef + 0.05 * (raca == "Branca"), 0, 1)
    m = pd.DataFrame({"peso": 1.0, "upa": upa, "estrato": 0, "raca": raca, "sexo": "Homem", "em_p1": p1,
                      "horas": np.where(p1, 40.0, np.nan), "renda_principal": np.where(p1, 1000.0, np.nan)})
    lin = S.margens_s14(m, 2026, 2)[0]
    ep_lin = (lin["ln_pr_p1_ic_superior"] - lin["ln_pr_p1_ic_inferior"]) / (2 * 1.959964)
    reps = []
    for _ in range(300):
        s = rng.integers(0, n_upa, n_upa)
        linhas = np.concatenate([np.arange(u * por, (u + 1) * por) for u in s])
        mm = m.iloc[linhas].assign(upa=np.repeat(np.arange(n_upa), por))
        reps.append(S.margens_s14(mm, 2026, 2)[0]["ln_pr_p1"])
    assert ep_lin == pytest.approx(np.std(reps, ddof=1), rel=0.15)


# --------------------------------------------------------------------------- tendência HAC
def test_tendencia_exata():
    t = tendencia.tempo_anos(np.repeat(np.arange(2012, 2026), 4), np.tile([1, 2, 3, 4], 14))
    r = tendencia.tendencia_hac(t, 50 - 1.5 * (t - 2012))
    assert r["inclinacao_por_ano"] == pytest.approx(-1.5)
    assert r["ep_ewc"] == pytest.approx(0.0, abs=1e-8)
    assert r["gl_ewc"] == 5 and r["defasagem_newey_west"] == 4


def test_hac_maior_que_iid_com_autocorrelacao_e_cobertura():
    rng = np.random.default_rng(3)
    t = tendencia.tempo_anos(np.repeat(np.arange(2012, 2027), 4)[:58], np.tile([1, 2, 3, 4], 15)[:58])
    cobre, razoes = 0, []
    for _ in range(400):
        e = np.zeros(58)
        e[0] = rng.normal() / np.sqrt(1 - 0.7**2)
        for i in range(1, 58):
            e[i] = 0.7 * e[i - 1] + rng.normal()
        r = tendencia.tendencia_hac(t, 2 + 0.3 * (t - 2012) + e)
        cobre += r["ic_inferior"] <= 0.3 <= r["ic_superior"]
        razoes.append(r["razao_ep_ewc_iid"])
    assert np.median(razoes) > 1.3          # i.i.d. subestima com AR(1) de 0,7
    assert 0.85 <= cobre / 400 <= 0.98       # EWC: ≈ 89% com ρ = 0,7 e T = 58 (NW com L = 4: ≈ 78%)


def test_medias_episodios():
    ano = np.repeat(np.arange(2012, 2027), 4)[:58]
    tri = np.tile([1, 2, 3, 4], 15)[:58]
    ep = tendencia.episodio_de(ano, tri)
    nivel = {e: i for i, e in enumerate(tendencia.EPISODIOS_PADRAO)}
    y = np.array([nivel[e] * 2.0 for e in ep])
    r = tendencia.medias_episodios_hac(ano, tri, y)
    assert r["media"].tolist() == pytest.approx([0, 2, 4, 6, 8])
    assert r["dif_vs_referencia"].tolist() == pytest.approx([0, 2, 4, 6, 8])
    assert r["n_periodos"].tolist() == [12, 8, 12, 8, 18]
