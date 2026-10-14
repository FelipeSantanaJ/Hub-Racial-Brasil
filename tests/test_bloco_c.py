"""Bloco C (Onda 2): combinações de médias de células, WLS design-based, delta numérico, Kitagawa."""
import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm

from src.processing import bloco_c as C


def _micro(seed=0, n=12000):
    rng = np.random.default_rng(seed)
    estrato = rng.integers(0, 40, n)
    raca = rng.choice(["Branca", "Negra", "Indígena"], p=[0.45, 0.5, 0.05], size=n)
    sexo = rng.choice(["Homem", "Mulher"], size=n)
    y = np.exp(7.3 + 0.45 * (raca == "Branca") - 0.25 * (sexo == "Mulher") + 0.1 * (raca == "Branca") * (sexo == "Mulher")
               + rng.normal(0, 0.6, n))
    return y, rng.uniform(100, 900, n), estrato * 10 + rng.integers(0, 4, n), estrato, raca, sexo


def test_shapley_e_ordens_somam_o_total():
    y, w, upa, est, raca, sexo = _micro()
    df = pd.DataFrame(C.celulas_c123(y, w, raca, sexo, np.ones(len(y), bool), upa, est, {"ano": 2026}))
    v = df.set_index(["metrica", "escala"])["estimativa"]
    for esc in ("log-pontos", "R$"):
        tot = v[("C3 total HB − mulher·Negra", esc)]
        assert v[("C3 Shapley raça·Negra", esc)] + v[("C3 Shapley gênero·Negra", esc)] == pytest.approx(tot)
        assert (v[("C3 sequencial raça primeiro: raça·Negra", esc)] + v[("C3 sequencial raça primeiro: gênero·Negra", esc)]
                == pytest.approx(tot))
        # a dependência de ordem é exatamente metade da interação
        dif = v[("C3 sequencial raça primeiro: raça·Negra", esc)] - v[("C3 Shapley raça·Negra", esc)]
        assert dif == pytest.approx(v[("C2 interação DiD·Negra", esc)] / 2)
    # log HB/célula bate com as médias
    med = df[df["metrica"].str.startswith("média")].set_index("celula")["estimativa"]
    assert v[("C1 log HB/MN", "log-pontos")] == pytest.approx(np.log(med["HB"] / med["MN"]))


def test_wls_design_igual_sanduiche_hc0_quando_cada_obs_e_sua_upa():
    rng = np.random.default_rng(1)
    n = 3000
    X = np.column_stack([np.ones(n), rng.normal(size=n), rng.integers(0, 2, n)])
    y = X @ [1.0, 0.5, -0.3] + rng.normal(0, 1 + 0.5 * X[:, 2], n)
    w = rng.uniform(1, 3, n)
    beta, ep, _ = C.wls_design(y, X, w, np.arange(n), np.zeros(n))
    ref = sm.WLS(y, X, weights=w).fit(cov_type="HC0")
    assert beta == pytest.approx(ref.params, rel=1e-8)
    assert ep == pytest.approx(ref.bse * np.sqrt(n / (n - 1)), rel=1e-6)


def test_delta_generico_igual_ao_analitico_da_razao():
    y, w, upa, est, raca, _ = _micro(2)
    from src.inference import variancia
    za, ma = variancia.influencia_media(y, w, raca == "Branca")
    zb, mb = variancia.influencia_media(y, w, raca == "Negra")
    r = C.delta_generico({"razao": lambda th: th[0] / th[1]}, np.array([ma, mb]), np.column_stack([za, zb]), upa, est)
    ep_an = variancia.razao_delta_design(za, zb, ma, mb, upa, est)
    assert r["estimativa"].iloc[0] == pytest.approx(ma / mb)
    assert r["ep"].iloc[0] == pytest.approx(ep_an, rel=1e-4)


def test_c5_kitagawa_soma_a_diferenca_de_medias():
    rng = np.random.default_rng(3)
    n = 8000
    raca = rng.choice(["Branca", "Negra", "Indígena"], p=[0.45, 0.5, 0.05], size=n)
    posicao = np.where(rng.random(n) < np.where(raca == "Branca", 0.08, 0.15), "04", "01")
    renda = np.where(posicao == "04", 1200.0, 3000.0) * np.where(raca == "Branca", 1.3, 1.0) * rng.uniform(0.7, 1.3, n)
    estrato = rng.integers(0, 30, n)
    m = pd.DataFrame({"peso": rng.uniform(50, 500, n), "upa": estrato * 10 + rng.integers(0, 4, n), "estrato": estrato,
                      "sexo": "Mulher", "raca": raca, "renda": renda, "em_p1": True, "posicao": posicao, "ocupado": True})
    df = pd.DataFrame(C.c5_trimestre(m, 2026, 2)).set_index(["indicador", "raca"])["estimativa"]
    total = df[("renda_media_todas_p1", "Branca")] - df[("renda_media_todas_p1", "Negra")]
    k = "Branca − Negra (mulheres)"
    assert df[("kitagawa_diferenca_total_rs", k)] == pytest.approx(total, rel=1e-9)
    assert df[("kitagawa_composicao_rs", k)] + df[("kitagawa_dentro_rs", k)] == pytest.approx(total, rel=1e-9)


def test_wls_design_tolera_coluna_vazia_no_dominio():
    rng = np.random.default_rng(5)
    n = 2000
    X = np.column_stack([np.ones(n), rng.normal(size=n), np.zeros(n)])  # 3ª coluna vazia
    y = X[:, :2] @ [1.0, 2.0] + rng.normal(size=n)
    beta, ep, _ = C.wls_design(y, X, np.ones(n), np.arange(n), np.zeros(n))
    assert beta[:2] == pytest.approx([1.0, 2.0], abs=0.1) and np.isnan(beta[2]) and np.isnan(ep[2])


def test_wls_design_apenas_igual_ao_completo():
    rng = np.random.default_rng(6)
    n = 4000
    X = np.column_stack([np.ones(n), rng.integers(0, 2, n), rng.normal(size=(n, 3))])
    y = X @ [1.0, -0.5, 0.2, 0.1, 0.0] + rng.normal(size=n)
    upa, est, w = rng.integers(0, 300, n), rng.integers(0, 30, n), rng.uniform(1, 3, n)
    b1, e1, _ = C.wls_design(y, X, w, upa, est)
    b2, e2, p2 = C.wls_design(y, X, w, upa, est, apenas=[1])
    assert b2 == pytest.approx(b1) and e2[1] == pytest.approx(e1[1], rel=1e-10)
    assert np.isnan(e2[0]) and (p2[:, 0] == 0).all()


def _micro_c6(correlacionado: bool, seed=7, n=20000):
    rng = np.random.default_rng(seed)
    estrato = rng.integers(0, 40, n)
    raca = rng.choice(["Branca", "Negra"], size=n)
    p_casal = np.where(raca == "Branca", 0.7, 0.4) if correlacionado else np.full(n, 0.55)
    casal = rng.random(n) < p_casal
    renda = np.exp(7.5 - 0.3 * (raca == "Negra") + 0.4 * casal + rng.normal(0, 0.5, n))
    return pd.DataFrame({"peso": rng.uniform(50, 500, n), "upa": estrato * 10 + rng.integers(0, 4, n), "estrato": estrato,
                         "raca": raca, "sexo": rng.choice(["Homem", "Mulher"], size=n), "idade": rng.integers(25, 60, n),
                         "instrucao": rng.choice(list("1234567"), size=n), "regiao": rng.choice(list("12345"), size=n),
                         "em_p1": True, "renda": renda, "chefe": rng.random(n) < 0.5, "em_casal": casal,
                         "filho_0a5": rng.random(n) < 0.2})


def test_c6_hiato_condicional_muda_so_quando_o_controle_se_associa_a_raca():
    for corr in (False, True):
        h = pd.DataFrame(C.hiato_condicional_c6(_micro_c6(corr)))
        mud = h[(h["especificacao"] == "mudança") & (h["sexo"] == "Homem")].iloc[0]
        com = h[(h["especificacao"] != "mudança") & (h["especificacao"] != "controles básicos") & (h["sexo"] == "Homem")]
        assert com["coef_negra_ln_renda"].iloc[0] == pytest.approx(-0.3, abs=0.04)  # com casal no modelo, recupera −0,3
        if corr:
            assert mud["coef_negra_ln_renda"] > 3 * mud["ep"]  # sem casal, o hiato básico era mais negativo
        else:
            assert abs(mud["coef_negra_ln_renda"]) < 3 * mud["ep"]
