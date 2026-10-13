"""Hiato em várias populações com covariância (Bloco S1, Onda 1)."""
import numpy as np
import pandas as pd
import pytest

from src.inference import variancia
from src.processing.sensibilidade_populacao import hiatos_populacoes


def _micro(seed=0, n=8000):
    rng = np.random.default_rng(seed)
    estrato = rng.integers(0, 40, n)
    upa = estrato * 10 + rng.integers(0, 5, n)
    raca = rng.choice(["Branca", "Negra"], size=n, p=[0.45, 0.55])
    ocup = rng.random(n) < 0.6
    renda = np.exp(7.6 + 0.4 * (raca == "Branca") + rng.normal(0, 0.7, n))
    sem_renda = ocup & (rng.random(n) < 0.05)
    return pd.DataFrame({"peso": rng.uniform(100, 900, n), "upa": upa, "estrato": estrato, "raca": raca,
                         "ocup": ocup, "renda": np.where(ocup & ~sem_renda, renda, np.nan)})


def test_hiato_e_ep_batem_com_metodo_delta():
    m = _micro()
    dom = m["renda"].notna().to_numpy()
    y = m["renda"].fillna(0).to_numpy()
    a, b = (m["raca"] == "Branca").to_numpy(), (m["raca"] == "Negra").to_numpy()
    df = hiatos_populacoes(m, {"P1": (dom, y)}, a, b)
    za, ma = variancia.influencia_media(y, m["peso"].to_numpy(), dom & a)
    zb, mb = variancia.influencia_media(y, m["peso"].to_numpy(), dom & b)
    ep = variancia.razao_delta_design(za, zb, ma, mb, m["upa"], m["estrato"])
    assert df.loc[0, "hiato_percentual"] == pytest.approx(100 * (ma / mb - 1))
    assert df.loc[0, "ep_hiato_percentual"] == pytest.approx(100 * ep, rel=1e-9)


def test_populacao_igual_a_referencia_tem_diferenca_zero():
    m = _micro(1)
    dom = m["renda"].notna().to_numpy()
    y = m["renda"].fillna(0).to_numpy()
    a, b = (m["raca"] == "Branca").to_numpy(), (m["raca"] == "Negra").to_numpy()
    df = hiatos_populacoes(m, {"P1": (dom, y), "Pcopia": (dom, y)}, a, b).set_index("populacao")
    assert df.loc["Pcopia", "dif_vs_ref_pp"] == pytest.approx(0, abs=1e-9)
    assert df.loc["Pcopia", "ep_dif_vs_ref"] == pytest.approx(0, abs=1e-6)
    assert not df.loc["Pcopia", "diferenca_grande"]


def test_zeros_dos_nao_ocupados_aumentam_o_hiato_quando_ocupacao_difere():
    m = _micro(2)
    rng = np.random.default_rng(3)
    # Negra com menos ocupação: P4 (não ocupados = 0) deve ter hiato maior que P1
    negra_sem = (m["raca"] == "Negra") & (rng.random(len(m)) < 0.15)
    m.loc[negra_sem, ["ocup", "renda"]] = [False, np.nan]
    a, b = (m["raca"] == "Branca").to_numpy(), (m["raca"] == "Negra").to_numpy()
    dom1 = m["renda"].notna().to_numpy()
    pops = {"P1": (dom1, m["renda"].fillna(0).to_numpy()),
            "P4": (np.ones(len(m), bool), m["renda"].fillna(0).to_numpy())}
    df = hiatos_populacoes(m, pops, a, b).set_index("populacao")
    assert df.loc["P4", "hiato_percentual"] > df.loc["P1", "hiato_percentual"]
    assert df.loc["P4", "ep_dif_vs_ref"] > 0


def test_ep_do_efeito_marginal_bate_com_sanduiche_em_aas():
    """AAS com pesos iguais: o EP linearizado do efeito marginal médio = delta sobre o
    sanduíche HC0 do statsmodels (a menos do fator n/(n−1) da linearização)."""
    import statsmodels.api as sm
    from src.processing.sensibilidade_populacao import efeitos_marginais_entrada
    rng = np.random.default_rng(5)
    n = 6000
    raca = rng.choice(["Branca", "Negra", "Indígena"], size=n, p=[0.45, 0.5, 0.05])
    sexo = rng.choice(["Homem", "Mulher"], size=n)
    idade = rng.integers(18, 70, n)
    lin = -0.2 - 0.3 * (raca == "Negra") - 0.5 * (raca == "Indígena") - 0.6 * (sexo == "Mulher") + 0.01 * (idade - 40)
    em_p1 = rng.random(n) < 1 / (1 + np.exp(-lin))
    m = pd.DataFrame({"raca": raca, "sexo": sexo, "idade": idade, "instrucao": rng.choice(list("1234567"), n),
                      "regiao": rng.choice(list("12345"), n), "peso": 1.0, "upa": np.arange(n), "estrato": 0,
                      "em_p1": em_p1, "renda_principal": 1000.0})
    r = efeitos_marginais_entrada(m).set_index("grupo")
    # referência: mesmo modelo, EP por delta numérico sobre a covariância HC0
    d = m.copy()
    d["faixa"] = pd.cut(d["idade"], [17, 24, 29, 39, 49, 59, 200]).astype(str)
    X = pd.get_dummies(d[["raca", "sexo", "faixa", "instrucao", "regiao"]].astype(str), dtype=float)
    X = sm.add_constant(X.drop(columns=["raca_Branca", "sexo_Homem", X.filter(like="faixa_").columns[0],
                                        X.filter(like="instrucao_").columns[0], X.filter(like="regiao_").columns[0]]))
    fit = sm.Logit(em_p1.astype(float), X).fit(disp=0, cov_type="HC0")
    b, V = fit.params.to_numpy(), fit.cov_params().to_numpy()
    X1, X0 = X.copy(), X.copy()
    X1["raca_Indígena"] = X0["raca_Indígena"] = 0.0
    X1["raca_Negra"], X0["raca_Negra"] = 1.0, 0.0
    f = lambda bb: np.mean(1 / (1 + np.exp(-X1.to_numpy() @ bb)) - 1 / (1 + np.exp(-X0.to_numpy() @ bb)))
    grad = np.array([(f(b + 1e-6 * e) - f(b - 1e-6 * e)) / 2e-6 for e in np.eye(len(b))])
    # o delta "puro" ignora a variabilidade de X (média amostral); a linearização a inclui:
    # comparar só o termo dos coeficientes é o que o delta mede, então tolerância de 10%
    assert r.loc["Negra", "efeito_marginal_pp"] == pytest.approx(100 * f(b), rel=1e-4)
    assert r.loc["Negra", "ep_pp"] == pytest.approx(100 * np.sqrt(grad @ V @ grad), rel=0.10)


def test_decomposicao_heaping_soma_exata():
    """Shift-share do F4: total final − inicial = composição + dentro da faixa."""
    from src.processing.sensibilidade_populacao import decomposicao_heaping
    df = pd.DataFrame({"ano": [2012, 2012, 2026, 2026], "raca": "Total", "faixa_nominal": ["a", "c", "a", "c"],
                       "pct_pessoas_na_faixa": [80.0, 20.0, 30.0, 70.0], "pct_multiplo_1000": [0.0, 50.0, 0.0, 45.0]})
    r = decomposicao_heaping(df, 2012, 2026)
    assert r["total_inicial"] == pytest.approx(10.0) and r["total_final"] == pytest.approx(31.5)
    assert r["efeito_composicao_pp"] == pytest.approx(25.0)       # (0,7 − 0,2) × 50
    assert r["efeito_dentro_da_faixa_pp"] == pytest.approx(-3.5)  # 0,7 × (45 − 50)
    assert r["efeito_composicao_pp"] + r["efeito_dentro_da_faixa_pp"] == pytest.approx(r["total_final"] - r["total_inicial"])
