"""Blocos E e H (Onda 4): indicadores e padronização com respostas conhecidas."""
import numpy as np
import pandas as pd
import pytest

from src.processing import bloco_eh as EH


def test_etapa_adequada_atraso_e_fora_da_escola():
    m = pd.DataFrame({"idade": [8, 8, 16, 16, 16, 20, 20],
                      "etapa": ["fundamental", "pré-escola", "médio", "fundamental", "não frequenta", "superior", "médio"],
                      "instrucao": ["1", "1", "3", "2", "3", "5", "4"]})
    ind = EH.indicadores_e1(m)
    assert ind["etapa_adequada"].tolist() == [100, 0, 100, 0, 0, 100, 0]
    assert ind["atraso"].tolist() == [0, 100, 0, 100, 0, 0, 100]
    assert np.isnan(ind["fora_da_escola_sem_medio"][0]) and ind["fora_da_escola_sem_medio"][4] == 100
    assert ind["fora_da_escola_sem_medio"][3] == 0  # frequenta
    assert ind["medio_completo"].tolist() == [0, 0, 0, 0, 0, 100, 0]


def _sim_h1(n=20000, seed=0):
    """Mesma probabilidade de superior dentro de cada origem para as duas raças; negros com origem mais baixa."""
    rng = np.random.default_rng(seed)
    raca = rng.choice(["Branca", "Negra"], n)
    probs_orig = {"Branca": [0.2, 0.2, 0.3, 0.3], "Negra": [0.5, 0.25, 0.2, 0.05]}
    cod_orig = {0: "2", 1: "3", 2: "5", 3: "7"}
    g = np.array([rng.choice(4, p=probs_orig[r]) for r in raca])
    p_sup = np.array([0.05, 0.15, 0.35, 0.7])[g]
    sup = rng.random(n) < p_sup
    return pd.DataFrame({"raca": raca, "idade": rng.integers(25, 30, n), "corresidente": True,
                         "educ_pais": [cod_orig[k] for k in g], "instrucao": np.where(sup, "7", "5"),
                         "etapa": "não frequenta", "peso": 1.0, "upa": np.arange(n), "estrato": 0})


def test_padronizacao_pela_origem_zera_diferenca_que_e_so_de_origem():
    m = _sim_h1()
    tr, co, _ = EH.h1(m, "teste")
    t = pd.DataFrame(tr)
    sel = (t.desfecho == "superior completo (25–29)") & (t.raca == "Branca − Negra")
    bruto = t[sel & (t.medida == "diferença bruta (corresidentes)")].estimativa.iloc[0]
    pad = t[sel & (t.medida == "diferença padronizada pela origem dos negros")]
    assert bruto > 15  # a diferença bruta existe (só por origem)
    assert abs(pad.estimativa.iloc[0]) < 2.5
    # dentro de cada origem não há diferença sistemática
    dentro = t[sel & (t.medida == "diferença dentro da origem (p.p.)")]
    assert (dentro.estimativa.abs() < 3.5 * dentro.ep).all()
    # mobilidade: filhos com superior de pais G1–G3 sobem; de pais G4 não
    mob = t[(t.desfecho == "mobilidade ascendente (25–29)") & (t.raca == "Branca")].estimativa.iloc[0]
    esperado = 100 * np.mean([(i == "7") and (o != "7") or (i == "5" and o in ("2", "3"))
                              for i, o in zip(m[m.raca == "Branca"].instrucao, m[m.raca == "Branca"].educ_pais)])
    assert mob == pytest.approx(esperado)
