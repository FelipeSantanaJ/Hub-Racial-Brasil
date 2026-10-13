"""Decomposição raça × gênero (E6 da auditoria Rodada 2).

Até 13/10/2026 o termo de gênero usava sempre Mulher Branca, também para alvos masculinos:
Homem Negro saía com efeito_genero = R$ 1.258 e interacao = −R$ 1.258 em vez de 0.
"""
import numpy as np
import pandas as pd
import pytest

from src.processing.agregacoes_pnadc import decompor_raca_genero

# médias por célula (raça, sexo) do microdado sintético
MEDIAS = {("Branca", "Homem"): 5000.0, ("Branca", "Mulher"): 3800.0,
          ("Negra", "Homem"): 3100.0, ("Negra", "Mulher"): 2300.0}


def _micro(n_por_celula: int = 60, seed: int = 0) -> pd.DataFrame:
    """Cada célula tem média ponderada exatamente igual a MEDIAS (desvios simétricos, pesos iguais
    dentro do par)."""
    rng = np.random.default_rng(seed)
    partes = []
    for (raca, sexo), m in MEDIAS.items():
        desvio = rng.uniform(0, 1500, size=n_por_celula // 2)
        renda = np.concatenate([m - desvio, m + desvio])
        peso = np.tile(rng.uniform(100, 900, size=n_por_celula // 2), 2)
        partes.append(pd.DataFrame({"raca_cor": raca, "sexo": sexo, "renda": renda, "peso": peso}))
    return pd.concat(partes, ignore_index=True)


@pytest.mark.parametrize("raca_t", ["Negra"])
def test_alvo_masculino_sem_efeito_de_genero(raca_t):
    d = decompor_raca_genero(_micro(), "Homem", raca_t, "renda")
    assert d["efeito_genero"] == pytest.approx(0.0, abs=1e-9)
    assert d["interacao"] == pytest.approx(0.0, abs=1e-9)
    assert d["gap_total"] == pytest.approx(d["efeito_raca"])
    assert d["gap_total"] == pytest.approx(5000 - 3100)


def test_alvo_feminino_igual_a_formula_antiga():
    """Com alvo feminino o termo de gênero já usava Mulher Branca: nada muda."""
    d = decompor_raca_genero(_micro(), "Mulher", "Negra", "renda")
    hb, mb, hn, mn = (MEDIAS[k] for k in [("Branca", "Homem"), ("Branca", "Mulher"),
                                         ("Negra", "Homem"), ("Negra", "Mulher")])
    assert d["gap_total"] == pytest.approx(hb - mn)
    assert d["efeito_raca"] == pytest.approx(hb - hn)
    assert d["efeito_genero"] == pytest.approx(hb - mb)
    assert d["interacao"] == pytest.approx((hb - mn) - (hb - hn) - (hb - mb))


@pytest.mark.parametrize("sexo_t,raca_t", [("Homem", "Negra"), ("Mulher", "Negra"), ("Mulher", "Branca")])
def test_soma_fecha(sexo_t, raca_t):
    d = decompor_raca_genero(_micro(seed=3), sexo_t, raca_t, "renda")
    assert d["gap_total"] == pytest.approx(d["efeito_raca"] + d["efeito_genero"] + d["interacao"])


def test_celula_pequena_devolve_none():
    micro = _micro()
    micro = micro[~((micro["raca_cor"] == "Negra") & (micro["sexo"] == "Mulher"))
                  | (micro.groupby(["raca_cor", "sexo"]).cumcount() < 10)]
    assert decompor_raca_genero(micro, "Mulher", "Negra", "renda") is None
