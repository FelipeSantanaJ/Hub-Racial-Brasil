"""Testes da proveniência padronizada (Fase 2, item 4)."""
import json
from pathlib import Path

import pandas as pd

from src.inference import saida
from src.utils.catalogo_tabelas import NAO_DOCUMENTADA, entrada

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"


def test_catalogo_cobre_todas_as_tabelas():
    sem = [p.name for p in PROCESSED.glob("*.parquet") if entrada(p.name)[0] == NAO_DOCUMENTADA]
    assert not sem, f"tabelas sem população no catálogo: {sem}"


def test_todo_parquet_tem_meta_no_esquema():
    for p in PROCESSED.glob("*.parquet"):
        meta = json.loads(Path(f"{p}._meta.json").read_text(encoding="utf-8"))
        assert meta["esquema"] == saida.ESQUEMA_META, p.name
        for campo in ("codigo", "insumos", "se_metodo", "populacao", "periodo", "n_linhas"):
            assert campo in meta, (p.name, campo)


def test_salvar_tabela_grava_meta(tmp_path):
    df = pd.DataFrame({"ano": [2025, 2026], "trimestre": [4, 1], "x": [1.0, 2.0]})
    destino = tmp_path / "hiato_racial.parquet"
    saida.salvar_tabela(df, destino, se_metodo="teste", insumos="derivado")
    meta = json.loads(Path(f"{destino}._meta.json").read_text(encoding="utf-8"))
    assert meta["periodo"] == {"inicio": "2025T4", "fim": "2026T1"}
    assert meta["n_linhas"] == 2 and meta["se_metodo"] == "teste"
    assert meta["populacao"].startswith("Ocupados")  # vem do catálogo pelo nome do arquivo


def test_hash_insumos_muda_com_o_arquivo(tmp_path, monkeypatch):
    arq = tmp_path / "insumo.csv"
    arq.write_text("a")
    monkeypatch.setattr(saida, "REPO_ROOT", tmp_path)
    monkeypatch.setitem(saida.INSUMOS, "teste", ("teste", ["insumo.csv"]))
    saida.hash_insumos.cache_clear()
    h1 = saida.hash_insumos("teste")["hash"]
    arq.write_text("b")
    saida.hash_insumos.cache_clear()
    assert saida.hash_insumos("teste")["hash"] != h1
    saida.hash_insumos.cache_clear()
