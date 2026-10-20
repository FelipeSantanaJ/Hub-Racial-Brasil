"""Onda 6: índices de segregação, renda do bairro e variância por conglomerados em exemplos com resposta conhecida."""
import numpy as np
import pandas as pd
import pytest

from src.inference import variancia
from src.processing import bloco_integracao as I


def test_duncan_extremos():
    b = np.array([10.0, 0.0, 5.0])
    n = np.array([0.0, 10.0, 5.0])
    assert I.duncan(b, n) == pytest.approx(0.6667, abs=1e-3)
    assert I.duncan(np.array([5.0, 5.0]), np.array([2.0, 2.0])) == pytest.approx(0.0)


def test_duncan_dentro_ignora_segregacao_entre_municipios():
    # dois municípios, cada um homogêneo internamente mas com composições diferentes
    b = np.array([90.0, 90.0, 10.0, 10.0])
    n = np.array([10.0, 10.0, 90.0, 90.0])
    mun = np.array([0, 0, 1, 1])
    assert I.duncan(b, n) > 0.7
    assert I.duncan_dentro(b, n, mun)[0] == pytest.approx(0.0, abs=1e-12)


def test_isolamento_e_renda_bairro():
    b = np.array([100.0, 0.0])
    n = np.array([0.0, 100.0])
    nn, nb = I.isolamento(b, n)
    assert nn == pytest.approx(1.0) and nb == pytest.approx(0.0)
    r = np.array([2000.0, 1000.0])
    rb, rn, razao, _ = I.renda_bairro(b, n, r, np.array([0, 0]))
    assert (rb, rn, razao) == (pytest.approx(2000.0), pytest.approx(1000.0), pytest.approx(100.0))


def test_linha_base_proxima_de_zero_sem_segregacao():
    rng = np.random.default_rng(0)
    t = rng.integers(200, 400, 300).astype(float)
    n = np.round(t * 0.5)
    b = t - n
    mun = np.repeat(np.arange(30), 10)
    dn, dd = I.linha_base(b, n, mun, reps=20)
    assert dn < 0.06 and dd < 0.06


def test_var_conglomerados_igual_a_variancia_do_hub():
    rng = np.random.default_rng(1)
    z = rng.normal(size=500)
    cl = rng.integers(0, 80, 500)
    est = cl % 5
    esperado, _ = variancia.variancia_linearizada(z, cl, est)
    assert I.var_conglomerados(z, cl, est) == pytest.approx(esperado, rel=1e-10)


def test_estatisticas_razao_e_composicao():
    rng = np.random.default_rng(2)
    n = 4000
    raca = rng.choice([1, 2, 4, 5], n, p=[0.4, 0.1, 0.45, 0.05])
    renda = np.where(raca == 1, 3000.0, 2000.0) * rng.lognormal(0, 0.1, n)
    out = pd.DataFrame(I._estatisticas(raca, np.ones(n), renda, np.ones(n, bool), np.arange(n), np.zeros(n, int)))
    r = out.loc[out["medida"] == "Branca × Negra: razão das médias − 1 (%)", "estimativa"].iloc[0]
    assert r == pytest.approx(50.0, abs=3.0)
    assert out.loc[out["medida"] == "% Negra", "estimativa"].iloc[0] == pytest.approx(55.0, abs=3.0)
