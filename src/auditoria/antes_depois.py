"""Relatório antes × depois de uma regeneração de data/processed (B2 da auditoria).

Compara cada parquet atual com a cópia em `data/processed/_legado/<rotulo>/`:
- estimativas pontuais idênticas? (todas as colunas que não são de inferência; diferença
  máxima absoluta e relativa);
- erro-padrão antigo × novo (mediana, mín e máx da razão novo/antigo, pela meia-largura do
  IC ou pela coluna `se`);
- flags de significância que mudaram (antigo `significativo` × novo
  `significativo_nominal` e × `significativo_fdr`).

As linhas são comparadas na ORDEM em que foram gravadas (a geração é determinística); as
colunas-chave não numéricas são conferidas para garantir que a ordem bate.

Uso:
    python -m src.auditoria.antes_depois --legado pre_b1_63563e3
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = REPO_ROOT / "data" / "processed"

PADROES_INFERENCIA = ("p_valor", "ic_inferior", "ic_superior", "significativo", "erro_padrao",
                      "ep_", "gl_welch", "n_amostra", "_bh", "_fdr", "_nominal", "z_", "razao_",
                      "se_metodo", "correlacao_medias", "n_upas", "n_estratos", "tendencias_paralelas")


def _texto(serie: pd.Series) -> pd.Series:
    """Chave como texto com nulos normalizados (no pandas 3, `astype(str)` mantém NaN)."""
    return serie.astype(object).where(serie.notna(), "<NA>").astype(str)


def _eh_inferencia(col: str) -> bool:
    return col == "se" or any(p in col for p in PADROES_INFERENCIA)


def _meia_largura(df: pd.DataFrame, prefixo: str = "") -> pd.Series | None:
    inf, sup = f"{prefixo}ic_inferior", f"{prefixo}ic_superior"
    if inf in df.columns and sup in df.columns:
        return (df[sup] - df[inf]) / 2
    if "se" in df.columns:
        return df["se"]
    return None


def _resumo_razao(r: pd.Series) -> dict | None:
    r = r.replace([np.inf, -np.inf], np.nan).dropna()
    r = r[r > 0]
    if r.empty:
        return None
    return {"mediana": float(r.median()), "min": float(r.min()), "max": float(r.max()), "n": int(len(r))}


def comparar(nome: str, antigo: pd.DataFrame, novo: pd.DataFrame) -> dict:
    res = {"arquivo": nome, "linhas_antes": len(antigo), "linhas_depois": len(novo),
           "colunas_novas": sorted(set(novo.columns) - set(antigo.columns)),
           "colunas_removidas": sorted(set(antigo.columns) - set(novo.columns))}
    if len(antigo) != len(novo):
        res["pontos_identicos"] = None
        res["nota"] = "número de linhas mudou: comparação por posição impossível"
        return res

    comuns = [c for c in antigo.columns if c in novo.columns]
    chaves = [c for c in comuns if not pd.api.types.is_float_dtype(antigo[c]) and not _eh_inferencia(c)]
    # O GROUP BY do DuckDB não garante ordem de linhas: alinha pelas chaves e, para
    # desempatar, pelas colunas pontuais (que têm de ser idênticas se nada mudou).
    pontuais = [c for c in comuns if pd.api.types.is_float_dtype(antigo[c]) and not _eh_inferencia(c)]
    ordem = chaves + pontuais
    if ordem:
        def _ordenar(df):
            aux = pd.DataFrame({c: (_texto(df[c]) if c in chaves else df[c].round(6)) for c in ordem})
            return df.loc[aux.sort_values(ordem, na_position="last", kind="stable").index]
        antigo, novo = _ordenar(antigo), _ordenar(novo)
    antigo, novo = antigo.reset_index(drop=True), novo.reset_index(drop=True)
    for c in chaves:
        a, b = _texto(antigo[c]), _texto(novo[c])
        if not (a == b).all():
            res["pontos_identicos"] = None
            res["nota"] = f"ordem/chave '{c}' diverge"
            return res

    dif_abs, dif_rel, cols_dif = 0.0, 0.0, []
    for c in comuns:
        if _eh_inferencia(c) or not pd.api.types.is_numeric_dtype(antigo[c]) or pd.api.types.is_bool_dtype(antigo[c]):
            continue
        a, b = antigo[c].astype(float), novo[c].astype(float)
        mesmo_nan = a.isna() == b.isna()
        d = (a - b).abs()
        rel = d / a.abs().where(a.abs() > 0)
        if not mesmo_nan.all() or (rel.fillna(d) > 1e-9).any():
            cols_dif.append(c)
        dif_abs = max(dif_abs, float(d.max(skipna=True) or 0.0))
        dif_rel = max(dif_rel, float(rel.max(skipna=True) or 0.0))
    res["pontos_identicos"] = not cols_dif
    res["colunas_ponto_diferentes"] = cols_dif
    res["dif_max_abs"], res["dif_max_rel"] = dif_abs, dif_rel

    ma, mn = _meia_largura(antigo), _meia_largura(novo)
    if ma is not None and mn is not None:
        res["razao_ep_novo_sobre_antigo"] = _resumo_razao(mn / ma)

    if "significativo" in antigo.columns:
        velho = antigo["significativo"].astype(bool)
        for alvo in ("significativo_nominal", "significativo_fdr"):
            if alvo in novo.columns:
                nv = novo[alvo].astype(bool)
                res[f"{alvo}_sim_para_nao"] = int((velho & ~nv).sum())
                res[f"{alvo}_nao_para_sim"] = int((~velho & nv).sum())
                res[f"{alvo}_total_sim"] = int(nv.sum())
        res["antigo_total_sim"] = int(velho.sum())
    for alvo in [c for c in novo.columns if c.endswith("significativo_fdr") and c != "significativo_fdr"]:
        nom = alvo.replace("_fdr", "_nominal")
        res[f"{alvo}_total_sim"] = int(novo[alvo].sum())
        res[f"{nom}_total_sim"] = int(novo[nom].sum())
    return res


def tabela_markdown(resultados: list[dict]) -> str:
    """Uma linha por parquet que tem inferência ou mudou; os sem inferência e idênticos
    são só contados no fim."""
    def fmt(x, nd=1):
        return "—" if x is None else f"{x:.{nd}f}".replace(".", ",")

    linhas = ["| Tabela | Linhas | Pontos idênticos (dif. máx. rel.) | EP novo/antigo: mediana (mín–máx) "
              "| Nominal: sim→não / não→sim | FDR: sim→não / não→sim | Colunas novas |",
              "|---|---|---|---|---|---|---|"]
    silenciosos = 0
    for r in resultados:
        tem_inf = "razao_ep_novo_sobre_antigo" in r or "significativo_nominal_sim_para_nao" in r or r.get("colunas_novas")
        if r.get("pontos_identicos") is True and not tem_inf:
            silenciosos += 1
            continue
        ep = r.get("razao_ep_novo_sobre_antigo")
        ep_txt = "—" if not ep else f"{fmt(ep['mediana'])} ({fmt(ep['min'])}–{fmt(ep['max'])})"
        pi = r.get("pontos_identicos")
        pi_txt = {True: "sim", False: "**NÃO**", None: f"n/a: {r.get('nota', '')}"}[pi]
        if pi is not None:
            pi_txt += f" ({r.get('dif_max_rel', 0):.1e})"
        nom = (f"{r['significativo_nominal_sim_para_nao']} / {r['significativo_nominal_nao_para_sim']}"
               if "significativo_nominal_sim_para_nao" in r else "—")
        fdr = (f"{r['significativo_fdr_sim_para_nao']} / {r['significativo_fdr_nao_para_sim']}"
               if "significativo_fdr_sim_para_nao" in r else "—")
        novas = ", ".join(f"`{c}`" for c in r.get("colunas_novas", [])) or "—"
        linhas.append(f"| `{r['arquivo']}` | {r.get('linhas_depois', '—')} | {pi_txt} | {ep_txt} | {nom} | {fdr} | {novas} |")
    linhas.append("")
    linhas.append(f"Outros {silenciosos} parquets sem colunas de inferência: estimativas idênticas e nenhuma coluna nova.")
    return "\n".join(linhas) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legado", required=True)
    parser.add_argument("--saida", type=Path, default=REPO_ROOT / "docs" / "auditoria" / "antes_depois.json")
    args = parser.parse_args()
    pasta_legado = PROCESSED_DIR / "_legado" / args.legado

    resultados = []
    for antigo_path in sorted(pasta_legado.glob("*.parquet")):
        novo_path = PROCESSED_DIR / antigo_path.name
        if not novo_path.exists():
            resultados.append({"arquivo": antigo_path.name, "nota": "removido"})
            continue
        resultados.append(comparar(antigo_path.name, pd.read_parquet(antigo_path), pd.read_parquet(novo_path)))
    args.saida.write_text(json.dumps(resultados, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    args.saida.with_name(args.saida.stem + ".tabela.md").write_text(tabela_markdown(resultados), encoding="utf-8")
    n_dif = [r["arquivo"] for r in resultados if r.get("pontos_identicos") is False]
    n_none = [r["arquivo"] for r in resultados if r.get("pontos_identicos") is None]
    print(f"{len(resultados)} parquets comparados; pontos diferentes: {n_dif}; não comparáveis: {n_none}")


if __name__ == "__main__":
    main()
