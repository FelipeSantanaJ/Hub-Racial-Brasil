"""Padroniza (retroativamente) os `_meta.json` de data/processed no esquema `hub-racial-meta/1`.

Uso único depois da Fase 2: as tabelas atuais foram TODAS regeneradas pelo commit da Fase 1
(`--commit`), mas só as que têm inferência ganharam `_meta.json` naquela rodada. Este script
grava o meta padronizado para todas, preservando os campos já existentes (`se_metodo`,
`familia_fdr`, `alfa`, `nota`, `n_boot`...), e marca `meta_retroativo: true`. Na próxima
regeneração o pipeline grava o meta sozinho (`src/inference/saida.py`).

Uso:
    python -m src.auditoria.proveniencia --commit da7b04b
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.inference.saida import ESQUEMA_META, escrever_meta

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
CAMPOS_GERADOS = {"esquema", "arquivo", "n_linhas", "gerado_em", "codigo", "insumos", "periodo", "populacao", "commit",
                  "meta_retroativo", "meta_preenchido_em"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True, help="commit que gerou as tabelas atuais")
    args = parser.parse_args()

    n_nao_doc = []
    for caminho in sorted(PROCESSED_DIR.glob("*.parquet")):
        meta_path = Path(f"{caminho}._meta.json")
        antigo = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        if antigo.get("esquema") == ESQUEMA_META and not antigo.get("meta_retroativo"):
            continue  # já gravado pelo pipeline novo
        extra = {k: v for k, v in antigo.items() if k not in CAMPOS_GERADOS}
        df = pd.read_parquet(caminho)
        gerado_em = antigo.get("gerado_em") or datetime.fromtimestamp(
            caminho.stat().st_mtime, tz=timezone.utc).isoformat()
        commit = (antigo.get("codigo") or {}).get("commit") or antigo.get("commit") or args.commit
        meta = escrever_meta(caminho, df, commit=commit, modulo="(retroativo)", gerado_em=gerado_em,
                             meta_retroativo=True, meta_preenchido_em=datetime.now(timezone.utc).isoformat(),
                             **extra)
        if meta["populacao"].startswith("NÃO DOCUMENTADA"):
            n_nao_doc.append(caminho.name)
    print(f"metas padronizados em {PROCESSED_DIR}; população não documentada: {n_nao_doc or 'nenhuma'}")


if __name__ == "__main__":
    main()
