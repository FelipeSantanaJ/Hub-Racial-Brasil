"""Inventário dos parquets de data/processed — linha de base para os relatórios
antes × depois da Etapa 2 da auditoria (ver docs/auditoria/rodada1.md).

Para cada parquet registra: nome, número de linhas, colunas (nome e tipo), hash
SHA-256 dos bytes do arquivo, hash do CONTEÚDO (independente da versão do pyarrow
que gravou o arquivo: `pandas.util.hash_pandas_object` linha a linha, na ordem em
que as linhas estão gravadas), data de modificação e se o arquivo é versionado no git.

Não altera nada em data/processed: só lê.

Uso:
    python -m src.auditoria.inventario_parquets                       # grava docs/auditoria/baseline.json
    python -m src.auditoria.inventario_parquets --saida outro.json
"""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
SAIDA_PADRAO = REPO_ROOT / "docs" / "auditoria" / "baseline.json"


def _sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def _hash_conteudo(df: pd.DataFrame) -> str:
    """Hash do conteúdo tabular: nomes das colunas + hash de cada linha (índice ignorado).
    Colunas com tipos não hasheáveis (listas, dicts) são convertidas para texto antes."""
    df = df.reset_index(drop=True)
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].map(lambda v: v if isinstance(v, (str, type(None), float, int, bool)) else repr(v))
    h = hashlib.sha256()
    h.update("|".join(map(str, df.columns)).encode("utf-8"))
    h.update(pd.util.hash_pandas_object(df, index=False).to_numpy().tobytes())
    return h.hexdigest()


def _arquivos_versionados() -> set[str]:
    try:
        saida = subprocess.run(
            ["git", "ls-files", "data/processed"], cwd=REPO_ROOT,
            capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return set()
    return {Path(linha).name for linha in saida.splitlines() if linha.strip()}


def _commit_atual() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def inventariar(diretorio: Path = PROCESSED_DIR) -> dict:
    versionados = _arquivos_versionados()
    itens = []
    for caminho in sorted(diretorio.rglob("*.parquet")):
        if "_legado" in caminho.parts:
            continue
        df = pd.read_parquet(caminho)
        itens.append({
            "arquivo": caminho.relative_to(REPO_ROOT).as_posix(),
            "linhas": int(len(df)),
            "colunas": [{"nome": str(c), "tipo": str(t)} for c, t in df.dtypes.items()],
            "sha256_arquivo": _sha256_arquivo(caminho),
            "hash_conteudo": _hash_conteudo(df),
            "modificado_em": datetime.fromtimestamp(caminho.stat().st_mtime, tz=timezone.utc).isoformat(),
            "versionado_git": caminho.name in versionados,
        })
    return {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "commit": _commit_atual(),
        "pandas": pd.__version__,
        "n_parquets": len(itens),
        "parquets": itens,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    args = parser.parse_args()
    inventario = inventariar()
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(inventario, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{inventario['n_parquets']} parquets inventariados -> {args.saida}")


if __name__ == "__main__":
    main()
