"""Bloco A (Onda 1): métricas do hiato, Theil L, quantis e bootstrap Rao-Wu."""
import numpy as np
import pandas as pd
import pytest

from src.processing import bloco_a as A
from src.utils import pnadc_core


def _dados(seed=0, n=6000):
    rng = np.random.default_rng(seed)
    estrato = rng.integers(0, 30, n)
    upa = estrato * 10 + rng.integers(0, 4, n)
    raca = rng.choice(["Branca", "Negra", "Indígena"], p=[0.45, 0.5, 0.05], size=n)
    y = np.round(np.exp(7.5 + 0.45 * (raca == "Branca") + rng.normal(0, 0.7, n)), -1)
    return y, rng.uniform(100, 900, n), upa, estrato, raca


def test_metricas_sao_coerentes():
    y, w, upa, est, raca = _dados()
    d = A.metricas_hiato(y, w, upa, est, raca == "Branca", raca == "Negra")
    assert d["razao"] == pytest.approx(d["media_branca"] / d["media_grupo"])
    assert d["log_pontos"] == pytest.approx(np.log(d["razao"]))
    assert d["pct_da_renda_branca"] == pytest.approx(100 / d["razao"])
    assert d["hiato_percentual"] == pytest.approx(100 * (d["razao"] - 1))
    assert d["diferenca_rs"] == pytest.approx(d["media_branca"] - d["media_grupo"])
    assert d["ep_hiato_percentual"] == pytest.approx(100 * d["ep_razao"])
    assert d["hiato_percentual_ic_inferior"] < d["hiato_percentual"] < d["hiato_percentual_ic_superior"]


def test_theil_l_entre_mais_dentro_igual_total():
    y, w, _, _, raca = _dados(1)
    t = A.theil_l_entre_dentro(y, w, raca)
    assert t["theil_l_entre"] + t["theil_l_dentro"] == pytest.approx(t["theil_l_total"], rel=1e-10)
    assert t["theil_l_entre"] > 0


def test_quantis_iguais_ao_pnadc_core():
    y, w, *_ = _dados(2)
    o = np.argsort(y, kind="stable")
    q = A._quantis(y[o], w[o], A.QUANTIS)
    assert np.allclose(q, [pnadc_core.quantil_ponderado(y, w, p) for p in A.QUANTIS])


def test_multiplicadores_rao_wu():
    _, _, upa, est, _ = _dados(3)
    cod, mult = A.multiplicadores_rao_wu(upa, est, n_boot=300)
    assert mult.shape[1] == 300 and len(cod) == len(upa)
    assert mult.mean() == pytest.approx(1.0, abs=0.02)  # reescala n_h/(n_h−1) preserva o total esperado
    assert (mult >= 0).all()
