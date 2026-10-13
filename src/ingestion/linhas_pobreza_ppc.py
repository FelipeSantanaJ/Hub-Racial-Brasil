"""Linhas internacionais de pobreza do Banco Mundial (PPC de 2021) em R$ nominais do ano (T2).

Linhas (nota do Banco Mundial de 05/06/2025, PPC de 2021): US$ 3,00, US$ 4,20 e US$ 8,30 por
pessoa por dia. Conversão para R$ nominais do ano, por pessoa por MÊS:

    linha_R$(ano) = US$/dia × PPC_2021 × IPC(ano) / IPC(2021) × 365/12

- PPC_2021: `PA.NUS.PRVT.PP` (fator de conversão de PPC do consumo final das famílias e ISFLSF,
  R$ por dólar internacional), ano 2021;
- IPC: `FP.CPI.TOTL` (índice de preços ao consumidor, 2010 = 100), média do ano;
- 365/12 = 30,4167 dias por mês.

Fonte: API v2 do Banco Mundial (World Development Indicators), Brasil, 2010–2025, arquivos JSON
em `data/raw/externos/` (baixados em 13/10/2026; `lastupdated` da API: 2026-10-08). Se faltam,
são baixados de novo. Ano sem IPC fica SEM linha (status "NÃO VERIFICADO"), nunca extrapolado.

Uso:
    python -m src.ingestion.linhas_pobreza_ppc
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import requests

from src.inference.saida import salvar_tabela

REPO_ROOT = Path(__file__).resolve().parents[2]
EXTERNOS = REPO_ROOT / "data" / "raw" / "externos"
DESTINO = REPO_ROOT / "data" / "processed" / "linhas_pobreza_ppc.parquet"
URL = "https://api.worldbank.org/v2/country/BRA/indicator/{ind}?format=json&date=2010:2025&per_page=100"
IND_PPC, IND_IPC = "PA.NUS.PRVT.PP", "FP.CPI.TOTL"
DATA_ACESSO = "2026-10-13"
ANO_BASE_PPC = 2021
LINHAS_USD_DIA = (3.00, 4.20, 8.30)
DIAS_POR_MES = 365 / 12
ANOS = range(2012, 2026)  # anos da PNAD Contínua anual usados no T2


def nome_linha(usd_dia: float) -> str:
    return f"US$ {usd_dia:.2f}/dia (PPC 2021)".replace(".", ",")


def linha_reais_mes(usd_dia: float, ppc_base: float, ipc_ano: float, ipc_base: float) -> float:
    """R$ nominais do ano por pessoa por mês."""
    return usd_dia * ppc_base * (ipc_ano / ipc_base) * DIAS_POR_MES


def ler_serie(indicador: str) -> dict[int, float]:
    """{ano: valor} do JSON da API do Banco Mundial (valores nulos ficam fora)."""
    arq = EXTERNOS / f"wb_{indicador}_BRA.json"
    if not arq.exists() or arq.stat().st_size == 0:
        EXTERNOS.mkdir(parents=True, exist_ok=True)
        r = requests.get(URL.format(ind=indicador), timeout=60)
        r.raise_for_status()
        arq.write_bytes(r.content)
    _, dados = json.loads(arq.read_text(encoding="utf-8"))
    serie = {}
    for d in dados:
        if d["indicator"]["id"] != indicador or d["countryiso3code"] != "BRA":
            raise ValueError(f"{arq.name}: registro inesperado ({d['indicator']['id']}, {d['countryiso3code']})")
        if d["value"] is not None:
            serie[int(d["date"])] = float(d["value"])
    return serie


def montar(ppc: dict[int, float], ipc: dict[int, float], anos=ANOS) -> pd.DataFrame:
    ppc_base, ipc_base = ppc[ANO_BASE_PPC], ipc[ANO_BASE_PPC]
    linhas = []
    for ano in anos:
        for usd in LINHAS_USD_DIA:
            ok = ano in ipc
            linhas.append({"ano": ano, "linha": nome_linha(usd), "usd_ppc_dia": usd,
                           "ppc_2021_reais_por_dolar": ppc_base, "ipc_ano": ipc.get(ano), "ipc_2021": ipc_base,
                           "fator_ipc": ipc[ano] / ipc_base if ok else None,
                           "valor_reais_mes": linha_reais_mes(usd, ppc_base, ipc[ano], ipc_base) if ok else None,
                           "status": "ok" if ok else "NÃO VERIFICADO (sem IPC do ano)"})
    return pd.DataFrame(linhas)


def main() -> None:
    df = montar(ler_serie(IND_PPC), ler_serie(IND_IPC))
    salvar_tabela(df, DESTINO, formula="US$/dia × PPC_2021 (PA.NUS.PRVT.PP) × IPC(ano)/IPC(2021) (FP.CPI.TOTL) × 365/12",
                  fonte="Banco Mundial, WDI (API v2); linhas da nota de 05/06/2025 (PPC de 2021)",
                  data_acesso=DATA_ACESSO)
    print(df.pivot(index="ano", columns="linha", values="valor_reais_mes").round(2).to_string())


if __name__ == "__main__":
    main()
