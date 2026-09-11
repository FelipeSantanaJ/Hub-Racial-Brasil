"""Fase E — tabela de crescimento da renda por raça, 2012 T1 → trimestre mais recente.

Uma linha por folha "Valores" da árvore (itens 1-10 = 181 linhas): renda média real
Branca e Negra no primeiro trimestre disponível e no último, % de crescimento de cada
raça no período, e o hiato em R$ no início vs. no fim — pra ver quem cresceu mais e se a
diferença em R$ caiu ou não (o hiato relativo pode cair mesmo com a diferença em R$
subindo, então as duas colunas ficam lado a lado).

Saída: `docs/tabela_crescimento_renda.xlsx` (uma aba por item + aba "Tudo") e
`docs/tabela_crescimento_renda.csv` (tudo junto). Não é slide — arquivo à parte
(decisão do usuário, ver docs/PLANO.md).

Uso:
    python -m src.processing.tabela_crescimento
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.processing import graficos_fase1 as g

REPO_ROOT = g.REPO_ROOT
PROCESSED = REPO_ROOT / "data" / "processed"
XLSX = REPO_ROOT / "docs" / "tabela_crescimento_renda.xlsx"
CSV = REPO_ROOT / "docs" / "tabela_crescimento_renda.csv"


def _wmean(sub: pd.DataFrame) -> float:
    if sub.empty:
        return np.nan
    w = sub["populacao_estimada"]
    tot = w.sum()
    return float((sub["renda_habitual_real_media"] * w).sum() / tot) if tot else np.nan


def _corte(df, ano, tri, filtro, sexo):
    d = df[df["nivel_geografico"] == "brasil"] if "nivel_geografico" in df.columns else df
    d = d[(d["ano"] == ano) & (d["trimestre"] == tri)]
    for c, v in (filtro or {}).items():
        d = d[d[c] == v]
    if sexo:
        d = d[d["sexo"] == sexo]
    return d


def _cresc(v0, v1):
    return 100 * (v1 / v0 - 1) if v0 and pd.notna(v0) and pd.notna(v1) else np.nan


def _linha(nome_item, recorte, df, filtro, sexo, ini, fim):
    a0, t0 = ini
    a1, t1 = fim
    d0, d1 = _corte(df, a0, t0, filtro, sexo), _corte(df, a1, t1, filtro, sexo)
    b0 = _wmean(d0[d0["raca_cor"] == "Branca"]); n0 = _wmean(d0[d0["raca_cor"].isin(["Preta", "Parda"])])
    b1 = _wmean(d1[d1["raca_cor"] == "Branca"]); n1 = _wmean(d1[d1["raca_cor"].isin(["Preta", "Parda"])])
    i0 = _wmean(d0[d0["raca_cor"] == "Indígena"]); i1 = _wmean(d1[d1["raca_cor"] == "Indígena"])
    cresc_b, cresc_n, cresc_i = _cresc(b0, b1), _cresc(n0, n1), _cresc(i0, i1)
    hiato_rs0 = b0 - n0 if pd.notna(b0) and pd.notna(n0) else np.nan
    hiato_rs1 = b1 - n1 if pd.notna(b1) and pd.notna(n1) else np.nan
    hiato_i_rs0 = b0 - i0 if pd.notna(b0) and pd.notna(i0) else np.nan
    hiato_i_rs1 = b1 - i1 if pd.notna(b1) and pd.notna(i1) else np.nan
    cresc_map = {"Branca": cresc_b, "Negra": cresc_n, "Indígena": cresc_i}
    validos = {k: v for k, v in cresc_map.items() if pd.notna(v)}
    cresceu_mais = max(validos, key=validos.get) if validos else "—"
    if pd.notna(hiato_rs0) and pd.notna(hiato_rs1):
        dif_rs = "caiu" if hiato_rs1 < hiato_rs0 else ("subiu" if hiato_rs1 > hiato_rs0 else "igual")
    else:
        dif_rs = "—"
    return {
        "item": nome_item, "recorte": recorte,
        f"Branca {a0}T{t0}": b0, f"Branca {a1}T{t1}": b1, "cresc.% Branca": cresc_b,
        f"Negra {a0}T{t0}": n0, f"Negra {a1}T{t1}": n1, "cresc.% Negra": cresc_n,
        f"Indígena {a0}T{t0}": i0, f"Indígena {a1}T{t1}": i1, "cresc.% Indígena": cresc_i,
        "cresceu mais": cresceu_mais,
        f"hiato B-N R$ {a0}T{t0}": hiato_rs0, f"hiato B-N R$ {a1}T{t1}": hiato_rs1, "hiato B-N R$": dif_rs,
        f"hiato B-I R$ {a0}T{t0}": hiato_i_rs0, f"hiato B-I R$ {a1}T{t1}": hiato_i_rs1,
        f"hiato B-N % {a0}T{t0}": (100 * hiato_rs0 / n0 if n0 and pd.notna(hiato_rs0) else np.nan),
        f"hiato B-N % {a1}T{t1}": (100 * hiato_rs1 / n1 if n1 and pd.notna(hiato_rs1) else np.nan),
        f"hiato B-I % {a0}T{t0}": (100 * hiato_i_rs0 / i0 if i0 and pd.notna(hiato_i_rs0) else np.nan),
        f"hiato B-I % {a1}T{t1}": (100 * hiato_i_rs1 / i1 if i1 and pd.notna(hiato_i_rs1) else np.nan),
    }


def _leaves(dados):
    renda, rpe, rg = dados["renda"], dados["renda_por_escolaridade"], dados["renda_por_geracao"]
    rc, rcg = dados["renda_completa"], dados["renda_completa_geracao"]
    faixas = g.FAIXAS_ETARIAS_ORDEM
    gers = g.GERACOES_ORDEM_GRAFICO
    nivs = g.NIVEIS_INSTRUCAO_ORDEM
    rg_rot = g.ROTULOS_GERACAO_CURTO
    nv_rot = g.NIVEIS_INSTRUCAO_ROTULO_CURTO
    L = []
    L.append(("1. Raça", "Brasil", renda, None, None))
    L.append(("2. Raça × Gênero", "Combinado", renda, None, None))
    for s, r in [("Mulher", "Mulheres"), ("Homem", "Homens")]:
        L.append(("2. Raça × Gênero", r, renda, None, s))
    L.append(("3. Raça × Faixa Etária", "Combinado", renda, None, None))
    for fx in faixas:
        L.append(("3. Raça × Faixa Etária", f"{fx} anos", renda, {"faixa_etaria": fx}, None))
    L.append(("4. Raça × Geração", "Combinado", rg, None, None))
    for ge in gers:
        L.append(("4. Raça × Geração", rg_rot[ge], rg, {"geracao": ge}, None))
    L.append(("5. Raça × Escolaridade", "Combinado", rpe, None, None))
    for ni in nivs:
        L.append(("5. Raça × Escolaridade", nv_rot[ni], rpe, {"nivel_instrucao": ni}, None))
    for s, r in [("Mulher", "Mulheres"), ("Homem", "Homens")]:
        for fx in faixas:
            L.append(("6. Raça × Gênero × Faixa Etária", f"{r} · {fx} anos", renda, {"faixa_etaria": fx}, s))
        for ge in gers:
            L.append(("7. Raça × Gênero × Geração", f"{r} · {rg_rot[ge]}", rg, {"geracao": ge}, s))
        for ni in nivs:
            L.append(("8. Raça × Gênero × Escolaridade", f"{r} · {nv_rot[ni]}", rpe, {"nivel_instrucao": ni}, s))
        for fx in faixas:
            for ni in nivs:
                L.append(("9. Raça × Gênero × Faixa Etária × Escolaridade",
                          f"{r} · {fx} · {nv_rot[ni]}", rc, {"faixa_etaria": fx, "nivel_instrucao": ni}, s))
        for ge in gers:
            for ni in nivs:
                L.append(("10. Raça × Gênero × Geração × Escolaridade",
                          f"{r} · {rg_rot[ge]} · {nv_rot[ni]}", rcg, {"geracao": ge, "nivel_instrucao": ni}, s))
    return L


def main():
    dados = {n: pd.read_parquet(PROCESSED / f"{n}.parquet") for n in
             ["renda", "renda_por_escolaridade", "renda_por_geracao", "renda_completa", "renda_completa_geracao"]}
    ini = (2012, 1)
    fim = g._trimestre_mais_recente(dados["renda"])
    linhas = [_linha(item, rec, df, filt, sexo, ini, fim) for item, rec, df, filt, sexo in _leaves(dados)]
    tudo = pd.DataFrame(linhas)
    num = tudo.select_dtypes("number").columns
    tudo[num] = tudo[num].round(1)

    tudo.to_csv(CSV, index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(XLSX, engine="openpyxl") as xl:
        tudo.to_excel(xl, sheet_name="Tudo", index=False)
        for item, bloco in tudo.groupby("item", sort=False):
            aba = item.split(".")[0].strip()[:31]
            bloco.drop(columns=["item"]).to_excel(xl, sheet_name=f"Item {aba}", index=False)

    print(f"{len(tudo)} linhas | {ini[0]}T{ini[1]} -> {fim[0]}T{fim[1]}")
    print(f"  {CSV.relative_to(REPO_ROOT)}")
    print(f"  {XLSX.relative_to(REPO_ROOT)}")
    print("\nResumo — quem cresceu mais (contagem de linhas):")
    print(tudo["cresceu mais"].value_counts().to_string())
    print("\nHiato Branca-Negra em R$ (2012 -> hoje):")
    print(tudo["hiato B-N R$"].value_counts().to_string())


if __name__ == "__main__":
    main()
