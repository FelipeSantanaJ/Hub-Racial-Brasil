"""Linhas internacionais de pobreza em PPC (T2) e comparação antes × depois com linhas novas."""
import pandas as pd
import pytest

from src.auditoria.antes_depois import comparar
from src.ingestion import linhas_pobreza_ppc as L
from src.processing import bloco_t as T


def test_conversao_com_valores_de_mentira_bate_com_a_conta_a_mao():
    # US$ 2/dia × R$ 5 por dólar PPC × (110 / 100) × 365/12 = 11 × 30,41666… = 334,58333…
    assert L.linha_reais_mes(2.0, 5.0, 110.0, 100.0) == pytest.approx(334.5833333333)


def test_ano_sem_ipc_fica_sem_linha_e_nao_verificado():
    ppc = {2021: 2.0}
    ipc = {2021: 100.0, 2024: 120.0}
    t = L.montar(ppc, ipc, anos=[2021, 2024, 2025])
    assert len(t) == 3 * len(L.LINHAS_USD_DIA)
    r21 = t[(t.ano == 2021) & (t.usd_ppc_dia == 3.0)].iloc[0]
    assert r21.valor_reais_mes == pytest.approx(3.0 * 2.0 * 365 / 12)
    r24 = t[(t.ano == 2024) & (t.usd_ppc_dia == 3.0)].iloc[0]
    assert r24.valor_reais_mes == pytest.approx(3.0 * 2.0 * 1.2 * 365 / 12)
    r25 = t[t.ano == 2025]
    assert r25.valor_reais_mes.isna().all() and r25.status.str.startswith("NÃO VERIFICADO").all()


def test_t2_usa_as_linhas_ppc_do_insumo_processado():
    ins = pd.read_parquet(T.LINHAS_PPC_PATH)
    linhas = T.linhas_pobreza(2025, 1000.0)
    for _, r in ins[(ins.ano == 2025) & (ins.status == "ok")].iterrows():
        assert linhas[r.linha] == pytest.approx(r.valor_reais_mes)
    # as linhas antigas continuam as mesmas
    assert linhas["1/4 salário mínimo (BPC)"] == pytest.approx(1518 / 4)
    assert len(linhas) == 6


def test_antes_depois_compara_so_as_linhas_que_ja_existiam():
    antigo = pd.DataFrame({"ano": [2024, 2025], "linha": ["a", "a"], "fgt0_pct": [10.0, 9.0]})
    novo = pd.DataFrame({"ano": [2024, 2024, 2025, 2025], "linha": ["a", "b", "a", "b"],
                         "fgt0_pct": [10.0, 3.0, 9.0, 2.0]})
    r = comparar("t", antigo, novo)
    assert r["pontos_identicos"] is True and r["linhas_novas_fora_da_comparacao"] == 2
    novo.loc[0, "fgt0_pct"] = 10.5
    assert comparar("t", antigo, novo)["pontos_identicos"] is False
