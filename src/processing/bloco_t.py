"""Onda 1 — Bloco T: panorama da população inteira (`docs/PLANO_DE_ANALISE.md`, Bloco T; ficha
`docs/studies/T/ficha.md`). O S1 mostrou que o hiato muda muito quando entram todos os adultos
(P4) ou a renda domiciliar (P5); por isso T deixou de ser opcional.

Fonte: PNAD Contínua anual (Visita 1; Visita 5 em 2020–2021), `data/raw/pnadc_anual_v2`. Unidade:
pessoa (todas as idades), com a renda do domicílio onde mora. Pensionistas, empregados domésticos
e seus parentes (`V2005` 17–19) ficam fora, como no IBGE (não têm `VD5008`).

- **T1** — renda domiciliar per capita habitual (`VD5008`: habitual de trabalhos + efetivo de
  outras fontes, ÷ moradores) por cor/raça da pessoa e por cor/raça × sexo da pessoa responsável
  pelo domicílio: média, mediana, P10, P90, hiato % (Branca ÷ grupo − 1) com IC design-based, Gini.
- **T2** — pobreza: FGT(0) (proporção), FGT(1) (hiato de pobreza) e FGT(2) (severidade) com três
  linhas por pessoa e por mês: ¼ salário mínimo (critério de renda do BPC), ½ salário mínimo
  (critério de baixa renda do CadÚnico) e 50% da mediana nacional do ano (linha relativa).
  Linhas internacionais em PPC ficam pendentes (exigem fator de conversão externo).
- **T3** — de onde vem a renda: % das pessoas em domicílios que recebem cada fonte, e participação
  de cada fonte no total da renda domiciliar das pessoas de cada grupo.

Valores **nominais do ano** (o extrato anual não traz os deflatores CO1/CO2); comparações no tempo
usam razões, taxas e linhas definidas em salários mínimos do próprio ano.

Uso:
    python -m src.processing.bloco_t
"""
from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd

from src.inference import variancia
from src.inference.saida import salvar_tabela
from src.processing.agregacoes_pnadc import OUTPUT_DIR, SALARIO_MINIMO_NOMINAL
from src.processing.sensibilidade_populacao import ANUAL_GLOB, Z95
from src.utils import pnadc_core

RACAS = ["Branca", "Negra", "Indígena", "Amarela"]
FONTES = {  # coluna individual → rótulo
    "V5001A2": "BPC-LOAS", "V5002A2": "Bolsa Família", "V5003A2": "Outros programas sociais",
    "V5004A2": "Aposentadoria e pensão", "V5005A2": "Seguro-desemprego/defeso",
    "V5006A2": "Pensão alimentícia, doação", "V5007A2": "Aluguel e arrendamento",
    "V5008A2": "Outros (poupança, aplicações, bolsa de estudos)",
}
# V5001A2…V5008A2 existem desde a mudança do questionário em 2015 (ano parcial): T3 começa em 2016
ANO_INICIO_FONTES = 2016
RACA_SQL = """CASE m.V2010 WHEN '1' THEN 'Branca' WHEN '2' THEN 'Negra' WHEN '4' THEN 'Negra'
                           WHEN '5' THEN 'Indígena' WHEN '3' THEN 'Amarela' END"""


def carregar_ano(con, glob: str, ano: int) -> pd.DataFrame:
    """Pessoas do ano com renda domiciliar per capita, chave de domicílio e cor/sexo do responsável."""
    fontes = ", ".join(f"COALESCE(m.{c}, 0) AS {c}" for c in FONTES)
    return con.execute(f"""
        WITH p AS (
          SELECT {RACA_SQL} AS raca, CASE m.V2007 WHEN '1' THEN 'Homem' WHEN '2' THEN 'Mulher' END AS sexo,
                 m.V2005 AS condicao, m.UPA AS upa, m.Estrato AS estrato, m.V1032 AS peso,
                 CAST(m.UPA AS VARCHAR) || '-' || CAST(m.V1008 AS VARCHAR) || '-' || CAST(m.V1014 AS VARCHAR) AS dom,
                 m.VD5008 AS renda_pc, m.VD5007 AS renda_dom, COALESCE(m.VD4019, 0) AS trabalho, {fontes}
          FROM read_parquet('{glob}', hive_partitioning = 1, union_by_name = true) m
          WHERE m.ano = {ano} AND m.V2005 NOT IN ('17', '18', '19') AND m.VD5008 IS NOT NULL)
        SELECT p.*, r.raca AS raca_resp, r.sexo AS sexo_resp
        FROM p LEFT JOIN (SELECT dom, raca, sexo FROM p WHERE condicao = '01') r USING (dom)
    """).df()


# ----------------------------------------------------------------------------------------- #
# T1
# ----------------------------------------------------------------------------------------- #
def _hiato(m: pd.DataFrame, y: np.ndarray, grupo_col: str, ref: str, alvo: str) -> dict:
    w = m["peso"].to_numpy(float)
    g = m[grupo_col].to_numpy(object)
    za, ma = variancia.influencia_media(y, w, g == ref)
    zb, mb = variancia.influencia_media(y, w, g == alvo)
    ep_r = variancia.razao_delta_design(za, zb, ma, mb, m["upa"].to_numpy(), m["estrato"].to_numpy())
    h = 100 * (ma / mb - 1)
    return {"hiato_percentual": h, "ic_inferior": h - Z95 * 100 * ep_r, "ic_superior": h + Z95 * 100 * ep_r}


def t1(m: pd.DataFrame, ano: int, visita: int) -> pd.DataFrame:
    y = m["renda_pc"].to_numpy(float)
    linhas = []
    m = m.assign(resp=m["raca_resp"].fillna("?") + " · " + m["sexo_resp"].fillna("?"))
    for recorte, col, grupos, ref in [("raca_pessoa", "raca", RACAS, "Branca"),
                                      ("raca_sexo_responsavel", "resp",
                                       [f"{r} · {s}" for r in ("Branca", "Negra", "Indígena") for s in ("Homem", "Mulher")],
                                       "Branca · Homem")]:
        for gr in grupos:
            sel = (m[col] == gr).to_numpy()
            if sel.sum() < 30:
                continue
            yy, ww = y[sel], m["peso"].to_numpy(float)[sel]
            linha = {"ano": ano, "visita": visita, "recorte": recorte, "grupo": gr, "n": int(sel.sum()),
                     "populacao": float(ww.sum()), "media": float(np.average(yy, weights=ww)),
                     "mediana": pnadc_core.quantil_ponderado(yy, ww, 0.5),
                     "p10": pnadc_core.quantil_ponderado(yy, ww, 0.1), "p90": pnadc_core.quantil_ponderado(yy, ww, 0.9),
                     "gini": pnadc_core.calcular_gini_ponderado(yy, ww), "pct_renda_zero": float(100 * ww[yy <= 0].sum() / ww.sum())}
            if gr != ref:
                linha.update(_hiato(m, y, col, ref, gr))
            linhas.append(linha)
    tot = {"ano": ano, "visita": visita, "recorte": "total", "grupo": "Total", "n": len(m),
           "populacao": float(m["peso"].sum()), "media": float(np.average(y, weights=m["peso"])),
           "mediana": pnadc_core.quantil_ponderado(y, m["peso"], 0.5),
           "p10": pnadc_core.quantil_ponderado(y, m["peso"], 0.1), "p90": pnadc_core.quantil_ponderado(y, m["peso"], 0.9),
           "gini": pnadc_core.calcular_gini_ponderado(y, m["peso"].to_numpy(float)),
           "pct_renda_zero": float(100 * m.loc[y <= 0, "peso"].sum() / m["peso"].sum())}
    pos = m[(y > 0) & m["raca"].isin(RACAS)]
    resumo, _ = pnadc_core.decomposicao_theil_entre_dentro(pos, "renda_pc", "raca", "peso")
    tot["theil_t_pct_entre_racas"] = resumo.get("pct_entre_grupos")
    linhas.append(tot)
    return pd.DataFrame(linhas)


# ----------------------------------------------------------------------------------------- #
# T2
# ----------------------------------------------------------------------------------------- #
def linhas_pobreza(ano: int, mediana: float) -> dict[str, float]:
    sm = SALARIO_MINIMO_NOMINAL[ano]
    return {"1/4 salário mínimo (BPC)": sm / 4, "1/2 salário mínimo (CadÚnico)": sm / 2,
            "50% da mediana": 0.5 * mediana}


def t2(m: pd.DataFrame, ano: int, visita: int) -> pd.DataFrame:
    y = m["renda_pc"].to_numpy(float)
    w = m["peso"].to_numpy(float)
    upa, est = m["upa"].to_numpy(), m["estrato"].to_numpy()
    med = pnadc_core.quantil_ponderado(y, w, 0.5)
    linhas = []
    grupos = [("raca_pessoa", r, (m["raca"] == r).to_numpy()) for r in RACAS + ["Total"]]
    grupos[-1] = ("raca_pessoa", "Total", np.ones(len(m), bool))
    grupos += [("raca_sexo_pessoa", f"{r} · {s}", ((m["raca"] == r) & (m["sexo"] == s)).to_numpy())
               for r in ("Branca", "Negra", "Indígena") for s in ("Homem", "Mulher")]
    for nome, z in linhas_pobreza(ano, med).items():
        pobre = (y < z).astype(float)
        gap = np.where(y < z, (z - y) / z, 0.0)
        sev = gap ** 2
        for recorte, gr, sel in grupos:
            if sel.sum() < 30:
                continue
            linha = {"ano": ano, "visita": visita, "linha": nome, "valor_linha": z, "recorte": recorte, "grupo": gr,
                     "n": int(sel.sum())}
            for rot, v in (("fgt0", pobre), ("fgt1", gap), ("fgt2", sev)):
                est_v = float(np.average(v[sel], weights=w[sel]))
                ep = variancia.erro_padrao_media_design(np.where(sel, v, 0.0), w, upa, est, dominio=sel)
                linha[f"{rot}_pct"] = 100 * est_v
                linha[f"{rot}_ic_inferior"] = 100 * (est_v - Z95 * ep)
                linha[f"{rot}_ic_superior"] = 100 * (est_v + Z95 * ep)
            linhas.append(linha)
    return pd.DataFrame(linhas)


# ----------------------------------------------------------------------------------------- #
# T3
# ----------------------------------------------------------------------------------------- #
def t3(m: pd.DataFrame, ano: int, visita: int) -> pd.DataFrame:
    cols = ["trabalho", *FONTES]
    dom = m.groupby("dom")[cols].sum()
    d = m[["dom", "raca", "peso", "renda_dom"]].join(dom, on="dom")
    d["total"] = d[cols].sum(axis=1)
    linhas = []
    for r in RACAS + ["Total"]:
        g = d if r == "Total" else d[d["raca"] == r]
        if len(g) < 30:
            continue
        w = g["peso"].to_numpy(float)
        tot = float((g["total"] * w).sum())
        for c in cols:
            rot = "Trabalho (habitual, todos os trabalhos)" if c == "trabalho" else FONTES[c]
            linhas.append({"ano": ano, "visita": visita, "raca": r, "fonte": rot,
                           "pct_pessoas_em_domicilio_que_recebe": 100 * float(w[(g[c] > 0).to_numpy()].sum() / w.sum()),
                           "pct_da_renda_domiciliar": 100 * float((g[c] * w).sum() / tot) if tot else np.nan})
    # checagem: total reconstruído × VD5007 (renda habitual domiciliar do IBGE)
    ok = d["renda_dom"] > 0
    dif = (d.loc[ok, "total"] / d.loc[ok, "renda_dom"] - 1).abs()
    out = pd.DataFrame(linhas)
    out["checagem_mediana_dif_rel_vs_VD5007"] = float(dif.median())
    return out


def main() -> None:
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    t1s, t2s, t3s = [], [], []
    for visita, glob in ANUAL_GLOB.items():
        anos = [r[0] for r in con.execute(f"SELECT DISTINCT ano FROM read_parquet('{glob}', hive_partitioning=1) ORDER BY 1").fetchall()]
        for ano in anos:
            m = carregar_ano(con, glob, int(ano))
            t1s.append(t1(m, int(ano), visita))
            t2s.append(t2(m, int(ano), visita))
            if int(ano) >= ANO_INICIO_FONTES:  # fontes separadas só existem completas desde 2016
                t3s.append(t3(m, int(ano), visita))
            print(f"T {ano} (visita {visita}): {len(m):,} pessoas".replace(",", "."), flush=True)
    meta = dict(insumos="anual_v2", se_metodo=variancia.SE_METODO,
                nota_renda="Valores NOMINAIS do ano; VD5008 = renda habitual domiciliar per capita")
    salvar_tabela(pd.concat(t1s, ignore_index=True), OUTPUT_DIR / "t1_renda_domiciliar_per_capita.parquet", **meta)
    salvar_tabela(pd.concat(t2s, ignore_index=True), OUTPUT_DIR / "t2_pobreza.parquet", **meta)
    salvar_tabela(pd.concat(t3s, ignore_index=True), OUTPUT_DIR / "t3_fontes_de_renda.parquet",
                  insumos="anual_v2", nota_renda=meta["nota_renda"])


if __name__ == "__main__":
    main()
