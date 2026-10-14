"""Gravação de tabelas de data/processed com proveniência padronizada (B2/B3 + Fase 2).

Todo parquet gravado por `salvar_tabela` (ou `salvar_com_inferencia`) ganha, ao lado, um
`<nome>.parquet._meta.json` no esquema `hub-racial-meta/1`:

    esquema, arquivo, n_linhas, gerado_em,
    codigo:    {commit, modulo}            versão do código que gerou a tabela
    insumos:   {chave, descricao, hash, n_arquivos}
                                            hash do MANIFESTO dos insumos (caminho relativo +
                                            tamanho de cada arquivo bruto; sha256 dos
                                            arquivos pequenos, como o deflator)
    se_metodo: método do erro-padrão, ou "sem_inferencia"
    populacao: quem entra no cálculo (src/utils/catalogo_tabelas.py)
    periodo:   {inicio, fim} (AAAATn), se a tabela tem ano/trimestre
    familia_fdr, alfa                       quando há p-valor (src/inference/multiplicidade.py)

`significativo` (coluna antiga) é mantida como ALIAS de `significativo_nominal` até os
gráficos serem regenerados (docs/auditoria/graficos_a_regenerar.md); não usar em código novo.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import subprocess
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import pandas as pd

from src.inference.multiplicidade import ALFA_PADRAO, adicionar_fdr
from src.inference.variancia import SE_METODO
from src.utils.catalogo_tabelas import entrada

REPO_ROOT = Path(__file__).resolve().parents[2]
ESQUEMA_META = "hub-racial-meta/1"
SEM_INFERENCIA = "sem_inferencia"

INSUMOS = {
    "trimestral_v1": ("PNAD Contínua trimestral, extrato v1 + deflator IBGE",
                      ["data/raw/pnadc_extraido/parquet", "data/processed/deflator_ibge.parquet"]),
    "trimestral_v2": ("PNAD Contínua trimestral, extrato v2 + deflator IBGE",
                      ["data/raw/pnadc_extraido_v2/parquet", "data/processed/deflator_ibge.parquet"]),
    "anual_visita1_v1": ("PNAD Contínua anual, Visita 1, extrato v1 (tema Habitação)",
                         ["data/raw/pnadc_anual_visita1/parquet"]),
    "anual_v2": ("PNAD Contínua anual, Visitas 1 e 5, extrato v2", ["data/raw/pnadc_anual_v2"]),
    "derivado": ("Outras tabelas de data/processed", []),
    "ibge_deflator": ("Planilha de deflatores do IBGE (FTP)", ["data/raw/pnadc_extraido/_tmp/deflatores"]),
    "wb_ppc_ipc": ("Banco Mundial (WDI, API v2): fator de PPC do consumo privado (PA.NUS.PRVT.PP) e IPC (FP.CPI.TOTL), Brasil",
                   ["data/raw/externos/wb_PA.NUS.PRVT.PP_BRA.json", "data/raw/externos/wb_FP.CPI.TOTL_BRA.json"]),
}
LIMITE_SHA_ARQUIVO = 5 * 1024 * 1024  # arquivos menores que isso entram com sha256 do conteúdo


def commit_atual() -> str | None:
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
        sujo = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no", "src"],
                              cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout.strip()
        return sha + ("-modificado" if sujo else "")
    except (OSError, subprocess.CalledProcessError):
        return None


@lru_cache(maxsize=None)
def hash_insumos(chave: str) -> dict:
    """Manifesto dos insumos de `chave` (ver INSUMOS): sha256 sobre (caminho relativo,
    tamanho) de cada arquivo, mais o sha256 do conteúdo dos arquivos pequenos. Detecta
    reextração, trimestre novo ou deflator trocado sem ler os ~600 MB de microdados."""
    descricao, caminhos = INSUMOS.get(chave, (chave, []))
    h = hashlib.sha256()
    n = 0
    for rel in caminhos:
        alvo = REPO_ROOT / rel
        arquivos = sorted(p for p in (alvo.rglob("*") if alvo.is_dir() else [alvo]) if p.is_file())
        for arq in arquivos:
            if arq.name == "_resumo_extracao.csv":
                continue
            tam = arq.stat().st_size
            h.update(f"{arq.relative_to(REPO_ROOT).as_posix()}|{tam}\n".encode())
            if tam < LIMITE_SHA_ARQUIVO and arq.suffix != ".parquet":
                h.update(hashlib.sha256(arq.read_bytes()).digest())
            n += 1
    return {"chave": chave, "descricao": descricao, "hash": h.hexdigest() if n else None, "n_arquivos": n}


def _periodo(df: pd.DataFrame | None) -> dict | None:
    if df is None or "ano" not in df.columns or df.empty:
        return None
    if "trimestre" in df.columns:
        chaves = sorted({(int(a), int(t)) for a, t in zip(df["ano"], df["trimestre"]) if pd.notna(a) and pd.notna(t)})
        return {"inicio": f"{chaves[0][0]}T{chaves[0][1]}", "fim": f"{chaves[-1][0]}T{chaves[-1][1]}"} if chaves else None
    anos = sorted(int(a) for a in df["ano"].dropna().unique())
    return {"inicio": str(anos[0]), "fim": str(anos[-1])} if anos else None


def _modulo_chamador() -> str | None:
    for quadro in inspect.stack()[2:]:
        mod = inspect.getmodule(quadro.frame)
        if mod and mod.__name__ not in (__name__,) and not mod.__name__.startswith("src.inference"):
            return mod.__name__
    return None


def montar_meta(destino: Path, df: pd.DataFrame | None = None, se_metodo: str | None = None,
                populacao: str | None = None, insumos: str | None = None, commit: str | None = None,
                **extra) -> dict:
    pop_catalogo, insumo_catalogo = entrada(Path(destino).name)
    return {
        "esquema": ESQUEMA_META,
        "arquivo": Path(destino).name,
        "n_linhas": None if df is None else int(len(df)),
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "codigo": {"commit": commit or commit_atual(), "modulo": extra.pop("modulo", None) or _modulo_chamador()},
        "insumos": hash_insumos(insumos or insumo_catalogo),
        "se_metodo": se_metodo or SEM_INFERENCIA,
        "populacao": populacao or pop_catalogo,
        "periodo": _periodo(df),
        **extra,
    }


def escrever_meta(destino: Path, df: pd.DataFrame | None = None, **kwargs) -> dict:
    meta = montar_meta(destino, df, **kwargs)
    Path(f"{destino}._meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def salvar_tabela(df: pd.DataFrame, destino: Path, **meta) -> pd.DataFrame:
    """Grava o parquet e o `_meta.json` (tabela sem inferência, ou com inferência que não
    passa pelo EP design-based — informar `se_metodo`)."""
    df.to_parquet(destino, index=False)
    escrever_meta(Path(destino), df, **meta)
    return df


def salvar_com_inferencia(df: pd.DataFrame, destino: Path, familia: list[str] | None,
                          coluna_p: str = "p_valor", se_metodo: str = SE_METODO, **meta_extra) -> pd.DataFrame:
    """Acrescenta FDR por família (se houver `coluna_p`), grava o parquet e o `_meta.json`."""
    tem_p = coluna_p in df.columns and len(df)
    if tem_p:
        prefixo = "" if coluna_p == "p_valor" else coluna_p.replace("p_valor", "").strip("_") + "_"
        df = adicionar_fdr(df, familia, coluna_p=coluna_p, prefixo=prefixo)
        if coluna_p == "p_valor" and "significativo" in df.columns:
            df["significativo"] = df["significativo_nominal"]
    return salvar_tabela(df, destino, se_metodo=se_metodo,
                         familia_fdr=familia if tem_p else None, alfa=ALFA_PADRAO, **meta_extra)
