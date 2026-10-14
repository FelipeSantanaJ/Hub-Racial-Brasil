"""Bloco T: indicadores FGT e composição por fonte (Onda 1)."""
import numpy as np
import pandas as pd
import pytest

from src.processing import bloco_t as T


def _micro(seed=0, n=3000):
    rng = np.random.default_rng(seed)
    raca = rng.choice(["Branca", "Negra"], size=n)
    renda = np.round(np.exp(7 + 0.5 * (raca == "Branca") + rng.normal(0, 0.9, n)))
    return pd.DataFrame({"raca": raca, "sexo": rng.choice(["Homem", "Mulher"], size=n), "peso": rng.uniform(1, 5, n),
                         "upa": rng.integers(0, 300, n), "estrato": 0, "renda_pc": renda})


def test_fgt_bate_com_definicao():
    m = _micro()
    t = T.t2(m, 2025, 1)
    z = T.linhas_pobreza(2025, 0)["1/4 salário mínimo (BPC)"]
    r = t[(t.linha == "1/4 salário mínimo (BPC)") & (t.grupo == "Negra")].iloc[0]
    neg = m[m.raca == "Negra"]
    w, y = neg.peso.to_numpy(), neg.renda_pc.to_numpy()
    assert r.fgt0_pct == pytest.approx(100 * np.average(y < z, weights=w))
    assert r.fgt1_pct == pytest.approx(100 * np.average(np.where(y < z, (z - y) / z, 0), weights=w))
    assert r.fgt2_pct <= r.fgt1_pct <= r.fgt0_pct
    assert r.fgt0_ic_inferior < r.fgt0_pct < r.fgt0_ic_superior


def test_linhas_em_salario_minimo_do_ano():
    l = T.linhas_pobreza(2025, 1000.0)
    assert l["1/4 salário mínimo (BPC)"] == pytest.approx(1518 / 4)
    assert l["50% da mediana"] == pytest.approx(500.0)


def test_t4_decimos_coerentes():
    m = _micro(4, n=6000)
    m.loc[m.index[:300], "renda_pc"] = 0.0           # empates em zero, como na renda domiciliar
    m.loc[m.index[300:330], "raca"] = "Indígena"
    t = pd.DataFrame(T.t4(m, 2025, 1))
    dec = t[t.decimo.str.startswith("D")]
    # participações de cada décimo somam 100% (todas as raças do universo)
    assert dec.groupby("decimo").pct_do_decimo.sum().to_numpy() == pytest.approx(100.0)
    # cada grupo se distribui pelos 10 décimos (somam 100%) e o índice médio ponderado é 1
    for g in ("Branca", "Negra"):
        x = dec[dec.raca == g]
        assert x.prob_no_decimo_pct.sum() == pytest.approx(100.0)
        assert x.indice_representacao.mean() == pytest.approx(1.0)
    topo = t[(t.decimo == "topo10") & (t.raca == "Negra")].iloc[0]
    assert topo.razao_de_chances < 1 and topo.rc_ic_inferior < topo.razao_de_chances < topo.rc_ic_superior
