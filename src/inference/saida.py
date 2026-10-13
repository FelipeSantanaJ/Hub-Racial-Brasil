"""Gravação de tabelas com inferência + metadados de proveniência (B2/B3 da auditoria).

Toda tabela com EP/IC/p-valor gravada por `salvar_com_inferencia` ganha:
- colunas de multiplicidade (`significativo_nominal`, `p_valor_bh`, `significativo_fdr`)
  quando tem `p_valor` — ver `src.inference.multiplicidade`;
- um arquivo `<nome>.parquet._meta.json` ao lado, com `se_metodo`, `commit` do código,
  a definição de família do FDR e a data de geração.

`significativo` (coluna antiga) é mantida como ALIAS de `significativo_nominal` até os
gráficos serem regenerados (docs/auditoria/graficos_a_regenerar.md); não usar em código novo.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.inference.multiplicidade import ALFA_PADRAO, adicionar_fdr
from src.inference.variancia import SE_METODO

REPO_ROOT = Path(__file__).resolve().parents[2]


def commit_atual() -> str | None:
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
        sujo = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no", "src"],
                              cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout.strip()
        return sha + ("-modificado" if sujo else "")
    except (OSError, subprocess.CalledProcessError):
        return None


def escrever_meta(destino: Path, **extra) -> None:
    meta = {
        "arquivo": destino.name,
        "se_metodo": SE_METODO,
        "commit": commit_atual(),
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        **extra,
    }
    Path(f"{destino}._meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def salvar_com_inferencia(df: pd.DataFrame, destino: Path, familia: list[str] | None,
                          coluna_p: str = "p_valor", se_metodo: str = SE_METODO, **meta_extra) -> pd.DataFrame:
    """Acrescenta FDR por família (se houver `coluna_p`), grava o parquet e o `_meta.json`."""
    if coluna_p in df.columns and len(df):
        prefixo = "" if coluna_p == "p_valor" else coluna_p.replace("p_valor", "").strip("_") + "_"
        df = adicionar_fdr(df, familia, coluna_p=coluna_p, prefixo=prefixo)
        if coluna_p == "p_valor" and "significativo" in df.columns:
            df["significativo"] = df["significativo_nominal"]
    df.to_parquet(destino, index=False)
    escrever_meta(Path(destino), se_metodo=se_metodo,
                  familia_fdr=familia if coluna_p in df.columns else None,
                  alfa=ALFA_PADRAO, **meta_extra)
    return df
