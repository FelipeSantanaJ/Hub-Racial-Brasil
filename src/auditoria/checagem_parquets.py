"""Checagens automáticas de integridade dos parquets de data/processed (Rodada 2, item 5).

Só lê. Para cada tabela: unicidade das chaves, NaN nas colunas de estimativa, faixas
plausíveis (taxas, proporções, p-valores, IC, Gini, Theil, renda, peso) e células publicadas
com amostra pequena. Depois, consistências cruzadas entre tabelas (Brasil = soma das regiões
= soma das UFs; população estimada × projeção; Theil entre + dentro = total).

Uso:
    python -m src.auditoria.checagem_parquets            # grava docs/auditoria/checagem_parquets.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED = REPO_ROOT / "data" / "processed"
SAIDA = REPO_ROOT / "docs" / "auditoria" / "checagem_parquets.json"

INFERENCIA = re.compile(r"p_valor|ic_inferior|ic_superior|significativo|erro_padrao|^ep_|^se$|gl_welch|_bh$|_fdr$|_nominal$")
# colunas que identificam a linha (dimensões): texto, inteiros de calendário e contagens de recorte
DIMENSOES_INT = {"ano", "trimestre", "relative_quarter", "ano_nascimento", "ano_lei", "limiar_nascimento", "quartil",
                 "percentil", "valor_referencia", "ano_evento", "trimestre_evento", "trimestre_inicio", "trimestre_fim", "salario_minimo"}
N_MINIMO = 30


def _chaves(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns
            if (df[c].dtype == object or str(df[c].dtype) in ("string", "str", "category", "bool")
                or c in DIMENSOES_INT) and not INFERENCIA.search(c)]


def _faixas(nome: str, df: pd.DataFrame) -> list[str]:
    problemas = []

    def fora(col, lo=None, hi=None, rotulo=""):
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        tol = 1e-9 * max(1.0, abs(hi or 0), abs(lo or 0))
        ruim = s[((s < lo - tol) if lo is not None else False) | ((s > hi + tol) if hi is not None else False)]
        if len(ruim):
            problemas.append(f"{col}: {len(ruim)} valor(es) fora de [{lo}, {hi}] {rotulo}(ex.: {ruim.iloc[0]:.4g})")

    for c in df.columns:
        if not pd.api.types.is_numeric_dtype(df[c]) or pd.api.types.is_bool_dtype(df[c]):
            continue
        if re.search(r"p_valor", c):
            fora(c, 0, 1)
        elif re.match(r"^(pct_|taxa)", c) and not re.search(r"explicada|nao_explicada", c):
            fora(c, 0, 100)
        elif c in ("gini",):
            fora(c, 0, 1)
        elif c.startswith("theil"):
            fora(c, 0, None)
        elif re.search(r"(^renda|renda_media|renda_no_percentil|limiar)", c) and "hiato" not in c:
            fora(c, 0, None, "(renda negativa) ")
        elif re.search(r"^(populacao|pop_|n_|n$)", c):
            fora(c, 0, None)
        elif c.startswith("indice_duncan"):
            fora(c, 0, 1)
        elif c.startswith("deflator"):
            fora(c, 0.5, 5)
    if {"ic_inferior", "ic_superior"} <= set(df.columns):
        inv = (df["ic_inferior"] > df["ic_superior"]).sum()
        if inv:
            problemas.append(f"ic_inferior > ic_superior em {int(inv)} linha(s)")
    if {"pct_explicada", "pct_nao_explicada"} <= set(df.columns):
        soma = (df["pct_explicada"] + df["pct_nao_explicada"] - 100).abs().max()
        if soma > 1e-6:
            problemas.append(f"pct_explicada + pct_nao_explicada ≠ 100 (desvio máx. {soma:.3g})")
    if {"pct_entre_grupos", "pct_dentro_grupos"} <= set(df.columns):
        soma = (df["pct_entre_grupos"] + df["pct_dentro_grupos"] - 100).abs().max()
        if soma > 1e-6:
            problemas.append(f"pct_entre + pct_dentro ≠ 100 (desvio máx. {soma:.3g})")
    return problemas


def checar_tabela(caminho: Path) -> dict:
    df = pd.read_parquet(caminho)
    chaves = _chaves(df)
    dup = int(df.duplicated(subset=chaves).sum()) if chaves else None
    pontos = [c for c in df.columns if pd.api.types.is_float_dtype(df[c]) and not INFERENCIA.search(c)]
    nan = {c: round(float(df[c].isna().mean()) * 100, 2) for c in pontos if df[c].isna().any()}
    n_cols = [c for c in df.columns if c in ("n_amostra", "n", "n_outro", "n_branca", "n_negra", "n_extremo", "n_topo10",
                                             "n_quartil", "n_favorecido", "n_desfavorecido", "n_publico", "n_privado")]
    pequenas = {c: int((pd.to_numeric(df[c], errors="coerce") < N_MINIMO).sum()) for c in n_cols
                if (pd.to_numeric(df[c], errors="coerce") < N_MINIMO).any()}
    return {"arquivo": caminho.name, "linhas": len(df), "chaves": chaves, "linhas_chave_duplicada": dup,
            "pct_nan_colunas_ponto": nan, "faixas": _faixas(caminho.name, df), "celulas_n_menor_30": pequenas}


def consistencias() -> list[dict]:
    out = []
    r = pd.read_parquet(PROCESSED / "renda.parquet")
    dims = ["ano", "trimestre", "raca_cor", "sexo", "faixa_etaria"]
    br = r[r["nivel_geografico"] == "brasil"].set_index(dims)["populacao_estimada"]
    for nivel in ("regiao", "uf"):
        soma = r[r["nivel_geografico"] == nivel].groupby(dims, dropna=False)["populacao_estimada"].sum()
        rel = ((soma.reindex(br.index) - br).abs() / br).max()
        out.append({"checagem": f"renda.populacao_estimada: Brasil = soma por {nivel}", "desvio_rel_max": float(rel),
                    "ok": bool(rel < 1e-9)})
    tot = r[r["nivel_geografico"] == "brasil"].groupby(["ano", "trimestre"])["populacao_estimada"].sum() / 1e6
    out.append({"checagem": "renda: população 14+ estimada (milhões) por trimestre",
                "min": float(tot.min()), "max": float(tot.max()),
                "maior_salto_trimestral_pct": float((tot.pct_change().abs() * 100).max()),
                "trimestre_maior_salto": str(tot.pct_change().abs().idxmax())})
    t = pd.read_parquet(PROCESSED / "theil_racial.parquet")
    d = (t["theil_entre_grupos"] + t["theil_dentro_grupos"] - t["theil_total"]).abs().max()
    out.append({"checagem": "theil: entre + dentro = total", "desvio_abs_max": float(d), "ok": bool(d < 1e-9)})
    h = pd.read_parquet(PROCESSED / "hiato_racial.parquet")
    d = (h["renda_media_branca"] - h["renda_media_negra"] - h["hiato_absoluto"]).abs().max()
    d2 = (100 * h["hiato_absoluto"] / h["renda_media_negra"] - h["hiato_percentual"]).abs().max()
    out.append({"checagem": "hiato_racial: absoluto = Branca − Negra e % = abs/Negra", "desvio_abs": float(d),
                "desvio_pct": float(d2), "ok": bool(d < 1e-6 and d2 < 1e-6)})
    # mesma série nacional em duas tabelas
    arv = pd.read_parquet(PROCESSED / "hiato_arvore.parquet")
    a = arv[(arv["combo"] == "") & (arv["comparacao"] == "Negra")].set_index(["ano", "trimestre"])["hiato_percentual"]
    d = (a - h.set_index(["ano", "trimestre"])["hiato_percentual"]).abs().max()
    out.append({"checagem": "hiato_arvore (combo vazio, Negra) = hiato_racial", "desvio_pp_max": float(d), "ok": bool(d < 1e-6)})
    return out


def main() -> None:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    tabelas = [checar_tabela(p) for p in sorted(PROCESSED.glob("*.parquet"))]
    res = {"tabelas": tabelas, "consistencias": consistencias()}
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    dup = [(t["arquivo"], t["linhas_chave_duplicada"]) for t in tabelas if t["linhas_chave_duplicada"]]
    fx = [(t["arquivo"], t["faixas"]) for t in tabelas if t["faixas"]]
    pq = [(t["arquivo"], t["celulas_n_menor_30"]) for t in tabelas if t["celulas_n_menor_30"]]
    nan = [(t["arquivo"], t["pct_nan_colunas_ponto"]) for t in tabelas if t["pct_nan_colunas_ponto"]]
    print("CHAVES DUPLICADAS:", dup)
    print("FAIXAS:", json.dumps(fx, ensure_ascii=False, indent=1))
    print("N<30:", pq)
    print("NaN:", nan)
    print("CONSISTÊNCIAS:", json.dumps(res["consistencias"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
