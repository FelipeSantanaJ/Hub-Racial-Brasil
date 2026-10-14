"""Onda 2 — Bloco B: o hiato está aumentando ou diminuindo? (`docs/PLANO_DE_ANALISE.md`, Bloco B; fichas em
`docs/studies/B1`…`B6`). Tendência com EP robusto a autocorrelação (`src/inference/tendencia.py`: EWC, com
Newey-West e GLS AR(1) ao lado).

- **B1** — tendência 2012–2026 do hiato (P1: Branca × Negra, Branca × Indígena, Preta × Parda, em % e em
  log-pontos; Bloco T: P4 e renda domiciliar per capita) e degraus em 2015T1, 2020T1, 2022T1.
- **B2** — mudança do hiato entre 2012 e 2025T3–2026T2: reclassificação (Kitagawa dentro de Negra; % Preta em
  coortes fixas) e Juhn-Murphy-Pierce (versão de médias), com bootstrap Rao-Wu.
- **B3** — hiato por quantil (P10…P90) em cada trimestre e tendência por quantil; diferença entre janelas com
  bootstrap; ao lado, quantis da renda domiciliar per capita (T1).
- **B4** — mesma idade, coortes diferentes; modelo idade-período-coorte com normalização de Deaton-Paxson.
- **B5** — ciclo × tendência: hiato ~ tendência + taxa de desocupação + pandemia + trimestre.
- **B6** — projeção condicional do ano de paridade sob premissas explícitas de ritmo.

Uso:
    python -m src.processing.bloco_b [--so b1 b2 b3 b4 b5 b6]
"""
from __future__ import annotations

import argparse

import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from src.inference import multiplicidade, tendencia, variancia
from src.inference.saida import salvar_tabela
from src.processing.agregacoes_pnadc import DEFLATOR_PATH, OUTPUT_DIR, PARQUET_GLOB
from src.processing.bloco_a import multiplicadores_rao_wu
from src.processing.sensibilidade_populacao import Z95
from src.utils import pnadc_core
from src.utils import populacao as pop

DEGRAUS = {"2015T1": (2015, 1), "2020T1": (2020, 1), "2022T1": (2022, 1)}
JANELAS = {"2012": [(2012, t) for t in (1, 2, 3, 4)],
           "2025T3-2026T2": [(2025, 3), (2025, 4), (2026, 1), (2026, 2)]}
RACA_SQL = """CASE m.V2010 WHEN '1' THEN 'Branca' WHEN '2' THEN 'Negra' WHEN '4' THEN 'Negra'
                           WHEN '5' THEN 'Indígena' WHEN '3' THEN 'Amarela' END"""


def micro_b(con, ano: int, tri: int, todos_18: bool = False) -> pd.DataFrame:
    """P1 do trimestre (ou todas as pessoas 18+, com `em_p1`), com cor/raça detalhada."""
    filtro = f"m.V2009 >= {pop.IDADE_MINIMA_REFERENCIA}" if todos_18 else pop.REFERENCIA.sql("m")
    return con.execute(f"""
        SELECT {ano} AS ano, {tri} AS trimestre, {RACA_SQL} AS raca,
               CASE m.V2010 WHEN '2' THEN 'Preta' WHEN '4' THEN 'Parda' END AS negra_det,
               CASE m.V2007 WHEN '1' THEN 'Homem' WHEN '2' THEN 'Mulher' END AS sexo, m.V2009 AS idade,
               m.VD3004 AS instrucao, SUBSTR(CAST(m.UF AS VARCHAR), 1, 1) AS regiao,
               m.V1028 AS peso, m.UPA AS upa, m.Estrato AS estrato,
               COALESCE({pop.REFERENCIA.sql('m')}, FALSE) AS em_p1,
               CASE WHEN {pop.REFERENCIA.sql('m')} THEN m.VD4016 * d.deflator_habitual END AS renda
        FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1) m
        LEFT JOIN read_parquet('{DEFLATOR_PATH}') d ON m.ano = d.ano AND m.trimestre = d.trimestre AND m.UF = d.UF
        WHERE m.ano = {ano} AND m.trimestre = {tri} AND {filtro} AND m.V2010 IN ('1','2','3','4','5')
    """).df()


def janela(con, tris, todos_18: bool = False) -> pd.DataFrame:
    return pd.concat([micro_b(con, a, t, todos_18) for a, t in tris], ignore_index=True)


def trimestres(con) -> list[tuple[int, int]]:
    return [(int(a), int(t)) for a, t in con.execute(
        f"SELECT DISTINCT ano, trimestre FROM read_parquet('{PARQUET_GLOB}', hive_partitioning=1) ORDER BY 1, 2").fetchall()]


# ----------------------------------------------------------------------------------------- #
# B1 — tendência
# ----------------------------------------------------------------------------------------- #
def series_b1() -> pd.DataFrame:
    """Séries publicadas que entram no B1, num formato longo (serie, ano, trimestre, valor)."""
    P = OUTPUT_DIR
    s = []
    for arq, rot in (("hiato_racial", "P1 · Branca × Negra"), ("hiato_branca_indigena", "P1 · Branca × Indígena"),
                     ("hiato_preta_parda", "P1 · Preta × Parda")):
        d = pd.read_parquet(P / f"{arq}.parquet")
        s.append(d.assign(serie=rot, metrica="hiato_pct", valor=d["hiato_percentual"])[["serie", "metrica", "ano", "trimestre", "valor"]])
    a2 = pd.read_parquet(P / "a2_metricas_hiato.parquet")
    for (conc, comp), d in a2.groupby(["conceito", "comparacao"]):
        rot = f"P1 · {comp}" + (" · por hora" if conc == "por_hora" else "")
        s.append(d.assign(serie=rot, metrica="log_pontos", valor=d["log_pontos"])[["serie", "metrica", "ano", "trimestre", "valor"]])
        if conc == "por_hora":
            s.append(d.assign(serie=rot, metrica="hiato_pct", valor=d["hiato_percentual"])[["serie", "metrica", "ano", "trimestre", "valor"]])
    pp = pd.read_parquet(P / "a2_metricas_hiato_preta_parda.parquet")
    s.append(pp.assign(serie="P1 · Preta × Parda", metrica="log_pontos", valor=pp["log_pontos"])[["serie", "metrica", "ano", "trimestre", "valor"]])
    sens = pd.read_parquet(P / "sensibilidade_hiato_populacao.parquet")
    for comp, d in sens[sens["populacao"] == "P4"].groupby("comparacao"):
        s.append(d.assign(serie=f"P4 · {comp}", metrica="hiato_pct", valor=d["hiato_percentual"])[["serie", "metrica", "ano", "trimestre", "valor"]])
        s.append(d.assign(serie=f"P4 · {comp}", metrica="log_pontos", valor=np.log(1 + d["hiato_percentual"] / 100))[["serie", "metrica", "ano", "trimestre", "valor"]])
    t1 = pd.read_parquet(P / "t1_renda_domiciliar_per_capita.parquet")
    t1 = t1[(t1["recorte"] == "raca_pessoa") & t1["grupo"].isin(["Negra", "Indígena"])]
    for g, d in t1.groupby("grupo"):
        s.append(d.assign(serie=f"T1 · Branca × {g} (domiciliar per capita)", metrica="hiato_pct", trimestre=1,
                          valor=d["hiato_percentual"])[["serie", "metrica", "ano", "trimestre", "valor"]])
        s.append(d.assign(serie=f"T1 · Branca × {g} (domiciliar per capita)", metrica="log_pontos", trimestre=1,
                          valor=np.log(1 + d["hiato_percentual"] / 100))[["serie", "metrica", "ano", "trimestre", "valor"]])
    return pd.concat(s, ignore_index=True).sort_values(["serie", "metrica", "ano", "trimestre"])


def gerar_b1() -> tuple[pd.DataFrame, pd.DataFrame]:
    s = series_b1()
    tend, deg = [], []
    for (serie, met), x in s.groupby(["serie", "metrica"]):
        anual = serie.startswith("T1")
        t = tendencia.tempo_anos(x["ano"], x["trimestre"])
        r = tendencia.tendencia_hac(t, x["valor"])
        ult = x.iloc[-1]
        recente = x[x["ano"] >= 2022]
        r22 = tendencia.tendencia_hac(tendencia.tempo_anos(recente["ano"], recente["trimestre"]), recente["valor"]) \
            if len(recente) >= 8 else {}
        tend.append({"serie": serie, "metrica": met, "frequencia": "anual" if anual else "trimestral",
                     "inicio": f"{int(x['ano'].iloc[0])}" + ("" if anual else f"T{int(x['trimestre'].iloc[0])}"),
                     "fim": f"{int(ult['ano'])}" + ("" if anual else f"T{int(ult['trimestre'])}"),
                     "valor_inicial": float(x["valor"].iloc[0]), "valor_final": float(ult["valor"]), **r,
                     **{f"desde_2022_{k}": v for k, v in r22.items() if k in ("inclinacao_por_ano", "ic_inferior",
                                                                              "ic_superior", "tendencia_confiavel", "n_periodos")}})
        if not anual:
            d = tendencia.degraus_ewc(x["ano"], x["trimestre"], x["valor"], DEGRAUS)
            d.insert(0, "metrica", met)
            d.insert(0, "serie", serie)
            deg.append(d)
    tend = pd.DataFrame(tend)
    deg = pd.concat(deg, ignore_index=True)
    deg = multiplicidade.adicionar_fdr(deg.assign(p_valor=np.where(deg["termo"].str.startswith("degrau"), deg["p_valor_ewc"], np.nan)),
                                       ["serie", "metrica"])
    salvar_tabela(tend, OUTPUT_DIR / "b1_tendencia_hiato.parquet", se_metodo=tendencia.METODO,
                  nota="Inclinação por ano; hiato_pct em p.p./ano, log_pontos em log-pontos/ano; desde_2022_* = só 2022–2026")
    salvar_tabela(deg, OUTPUT_DIR / "b1_degraus_hiato.parquet", se_metodo=tendencia.METODO,
                  familia_fdr=["serie", "metrica"], degraus=list(DEGRAUS))
    return tend, deg


# ----------------------------------------------------------------------------------------- #
# B6 — projeção condicional
# ----------------------------------------------------------------------------------------- #
def ano_paridade(nivel: float, ano_final: float, ritmo: float, lo: float, hi: float) -> dict:
    """Ano em que um hiato positivo chega a zero se cair `ritmo` por ano (ritmo < 0). Intervalo
    pelos extremos do IC do ritmo; se o IC alcança 0, o limite tardio é "sem data finita" (inf)."""
    def ano(r):
        return ano_final + nivel / (-r) if r < 0 else np.inf
    return {"ano_central": ano(ritmo), "ano_mais_cedo": ano(lo), "ano_mais_tarde": ano(hi),
            "data_finita": bool(hi < 0)}


def gerar_b6(tend: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    alvo = tend[(tend["metrica"] == "hiato_pct") & tend["serie"].isin(
        ["P1 · Branca × Negra", "P4 · Branca × Negra", "P4 · Branca × Negra, mulheres",
         "T1 · Branca × Negra (domiciliar per capita)"])]
    for _, r in alvo.iterrows():
        fim = float(r["fim"][:4]) + (int(r["fim"][5]) - 1) / 4 if "T" in r["fim"] else float(r["fim"])
        nivel = r["valor_final"]
        for prem, (rit, lo, hi) in {
            "P-a ritmo linear de todo o período": (r["inclinacao_por_ano"], r["ic_inferior"], r["ic_superior"]),
            "P-b ritmo linear desde 2022": (r.get("desde_2022_inclinacao_por_ano"), r.get("desde_2022_ic_inferior"),
                                            r.get("desde_2022_ic_superior")),
        }.items():
            if rit is None or not np.isfinite(rit):
                continue
            linhas.append({"serie": r["serie"], "premissa": prem, "hiato_atual_pct": nivel, "ritmo_pp_ano": rit,
                           "ritmo_ic_inferior": lo, "ritmo_ic_superior": hi, **ano_paridade(nivel, fim, rit, lo, hi)})
        lg = tend[(tend["serie"] == r["serie"]) & (tend["metrica"] == "log_pontos")]
        if len(lg):
            g = lg.iloc[0]
            # queda proporcional constante do hiato em log-pontos: meia-vida = ln 2 / |ritmo relativo|
            rel = g["inclinacao_por_ano"] / g["valor_final"]
            rel_lo, rel_hi = g["ic_inferior"] / g["valor_final"], g["ic_superior"] / g["valor_final"]
            meia = (lambda x: np.log(2) / -x if x < 0 else np.inf)
            linhas.append({"serie": r["serie"], "premissa": "P-c queda proporcional constante (meia-vida do hiato)",
                           "hiato_atual_pct": nivel, "ritmo_pp_ano": 100 * rel, "ritmo_ic_inferior": 100 * rel_lo,
                           "ritmo_ic_superior": 100 * rel_hi, "ano_central": fim + meia(rel),
                           "ano_mais_cedo": fim + meia(rel_lo), "ano_mais_tarde": fim + meia(rel_hi),
                           "data_finita": bool(rel_hi < 0), "nota": "ano em que o hiato cai à METADE (nunca chega a zero)"})
    df = pd.DataFrame(linhas)
    df["unidade_ritmo"] = np.where(df["premissa"].str.startswith("P-c"), "% do hiato (log-pontos) por ano", "p.p. de hiato por ano")
    salvar_tabela(df, OUTPUT_DIR / "b6_projecao_condicional.parquet", se_metodo=tendencia.METODO,
                  aviso="Projeção CONDICIONAL: 'se o ritmo for X'. Não é previsão; só a incerteza do ritmo passado.")
    return df


# ----------------------------------------------------------------------------------------- #
# B5 — ciclo × tendência
# ----------------------------------------------------------------------------------------- #
def taxa_desocupacao(con) -> pd.DataFrame:
    return con.execute(f"""
        SELECT ano, trimestre, 100 * SUM(V1028) FILTER (WHERE VD4002 = '2') / SUM(V1028) AS desocupacao
        FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1)
        WHERE VD4001 = '1' AND V2009 >= 14 GROUP BY 1, 2 ORDER BY 1, 2""").df()


def ciclo_ewc(d: pd.DataFrame, y: str) -> dict:
    t = tendencia.tempo_anos(d["ano"], d["trimestre"])
    pand = ((d["ano"] >= 2020) & (d["ano"] <= 2021)).astype(float).to_numpy()
    saz = pd.get_dummies(d["trimestre"].astype(int), prefix="tri", drop_first=True, dtype=float).to_numpy()
    X = np.column_stack([np.ones(len(d)), t - t.mean(), d["desocupacao"].to_numpy(float), pand, saz])
    yy = d[y].to_numpy(float)
    fit = sm.OLS(yy, X).fit()
    V, nu = tendencia.cov_ewc(X, fit.resid)
    q = float(stats.t.ppf(0.975, nu))
    nw = sm.OLS(yy, X).fit(cov_type="HAC", cov_kwds={"maxlags": tendencia.defasagem_hac(len(yy)), "use_correction": True})
    gls = sm.GLSAR(yy, X, rho=1).iterative_fit(maxiter=20)
    c, ep = float(fit.params[2]), float(np.sqrt(V[2, 2]))
    # R² parciais: quanto a desocupação acrescenta à tendência (e vice-versa)
    r2_tend = sm.OLS(yy, X[:, [0, 1, 3, *range(4, X.shape[1])]]).fit().rsquared
    r2_cicl = sm.OLS(yy, X[:, [0, 2, 3, *range(4, X.shape[1])]]).fit().rsquared
    ic_nw = (c - Z95 * nw.bse[2], c + Z95 * nw.bse[2])
    ic_g = (gls.params[2] - stats.t.ppf(0.975, len(yy) - X.shape[1]) * gls.bse[2],
            gls.params[2] + stats.t.ppf(0.975, len(yy) - X.shape[1]) * gls.bse[2])
    exc = lambda lo, hi: lo > 0 or hi < 0  # noqa: E731
    return {"coef_desocupacao": c, "ep_ewc": ep, "ic_inferior": c - q * ep, "ic_superior": c + q * ep,
            "p_valor": float(2 * stats.t.sf(abs(c / ep), nu)), "gl_ewc": nu,
            "ep_newey_west": float(nw.bse[2]), "coef_gls_ar1": float(gls.params[2]), "ep_gls_ar1": float(gls.bse[2]),
            "inclinacao_por_ano": float(fit.params[1]), "coef_pandemia": float(fit.params[3]),
            "r2_completo": float(fit.rsquared), "r2_sem_desocupacao": float(r2_tend), "r2_sem_tendencia": float(r2_cicl),
            "emd_80pct": float((q + stats.t.ppf(0.80, nu)) * ep),
            "associacao_confiavel": bool(exc(c - q * ep, c + q * ep) and exc(*ic_nw) and exc(*ic_g))}


def gerar_b5(con) -> pd.DataFrame:
    deso = taxa_desocupacao(con)
    sens = pd.read_parquet(OUTPUT_DIR / "sensibilidade_hiato_populacao.parquet")
    linhas = []
    for (popn, comp), x in sens[sens["populacao"].isin(["P1", "P4"])].groupby(["populacao", "comparacao"]):
        if "Indígena" in comp:
            continue
        d = x.merge(deso, on=["ano", "trimestre"]).sort_values(["ano", "trimestre"])
        linhas.append({"populacao": popn, "comparacao": comp, **ciclo_ewc(d, "hiato_percentual")})
    df = multiplicidade.adicionar_fdr(pd.DataFrame(linhas), None)
    salvar_tabela(df, OUTPUT_DIR / "b5_ciclo_tendencia.parquet", se_metodo=tendencia.METODO, familia_fdr="as 6 séries (BH)",
                  nota="hiato % ~ tendência + desocupação (14+, IBGE) + dummy 2020–21 + trimestre; coef em p.p. de hiato por p.p. de desocupação")
    salvar_tabela(deso, OUTPUT_DIR / "b5_taxa_desocupacao.parquet", nota="Desocupados ÷ força de trabalho, 14+, ponderado (V1028)")
    return df


# ----------------------------------------------------------------------------------------- #
# B3 — quantis
# ----------------------------------------------------------------------------------------- #
QUANTIS_B3 = [0.10, 0.25, 0.50, 0.75, 0.90]


def hiatos_quantis(y, w, raca, qs=QUANTIS_B3, a="Branca", b="Negra") -> np.ndarray:
    qa = np.array([pnadc_core.quantil_ponderado(y[raca == a], w[raca == a], q) for q in qs])
    qb = np.array([pnadc_core.quantil_ponderado(y[raca == b], w[raca == b], q) for q in qs])
    return np.log(qa / qb)


def _quantis_rep(y, w_rep, sel, qs):
    """Quantis de y[sel] para cada coluna de pesos replicados (mesma convenção de `quantil_ponderado`)."""
    idx = np.flatnonzero(sel)
    o = idx[np.argsort(y[idx], kind="stable")]
    cum = np.cumsum(w_rep[o], axis=0)
    cum = cum / cum[-1]
    return np.stack([y[o][np.minimum(np.searchsorted(cum[:, b], qs), len(o) - 1)] for b in range(cum.shape[1])], axis=1)


def gerar_b3(con, n_boot: int = 100) -> tuple[pd.DataFrame, pd.DataFrame]:
    linhas = []
    for a, t in trimestres(con):
        m = micro_b(con, a, t)
        y, w, raca = m["renda"].to_numpy(float), m["peso"].to_numpy(float), m["raca"].to_numpy(object)
        for q, lp in zip(QUANTIS_B3, hiatos_quantis(y, w, raca)):
            linhas.append({"ano": a, "trimestre": t, "quantil": f"P{int(q * 100)}", "log_pontos": lp,
                           "hiato_pct": 100 * (np.exp(lp) - 1)})
        print(f"B3 {a}T{t}", flush=True)
    serie = pd.DataFrame(linhas)
    tend = []
    for q, x in serie.groupby("quantil"):
        r = tendencia.tendencia_hac(tendencia.tempo_anos(x["ano"], x["trimestre"]), x["log_pontos"])
        tend.append({"conceito": "P1 · renda do trabalho", "quantil": q, **r})
    t1 = pd.read_parquet(OUTPUT_DIR / "t1_renda_domiciliar_per_capita.parquet")
    t1 = t1[t1["recorte"] == "raca_pessoa"].pivot_table(index="ano", columns="grupo", values=["p10", "mediana", "p90"])
    for col, q in (("p10", "P10"), ("mediana", "P50"), ("p90", "P90")):
        lp = np.log(t1[col]["Branca"] / t1[col]["Negra"]).replace([np.inf, -np.inf], np.nan)
        r = tendencia.tendencia_hac(t1.index.to_numpy(float), lp.to_numpy())
        tend.append({"conceito": "T1 · renda domiciliar per capita (anual)", "quantil": q, **r,
                     "valor_2012": float(lp.iloc[0]), "valor_final": float(lp.iloc[-1])})
    tend = pd.DataFrame(tend)
    # diferença entre janelas, bootstrap Rao-Wu (janelas independentes)
    reps, est = {}, {}
    for nome, tris in JANELAS.items():
        m = janela(con, tris)
        y, w, raca = m["renda"].to_numpy(float), m["peso"].to_numpy(float), m["raca"].to_numpy(object)
        est[nome] = hiatos_quantis(y, w, raca)
        cod, mult = multiplicadores_rao_wu(m["upa"].to_numpy(), m["estrato"].to_numpy(), n_boot, seed=3)
        wr = w[:, None] * mult[cod]
        qa = _quantis_rep(y, wr, raca == "Branca", QUANTIS_B3)
        qb = _quantis_rep(y, wr, raca == "Negra", QUANTIS_B3)
        reps[nome] = np.log(qa / qb)
    j0, j1 = list(JANELAS)
    dif = reps[j1] - reps[j0]
    jan = pd.DataFrame({"quantil": [f"P{int(q * 100)}" for q in QUANTIS_B3],
                        f"log_pontos_{j0}": est[j0], f"log_pontos_{j1}": est[j1], "diferenca": est[j1] - est[j0],
                        "ic_inferior": np.percentile(dif, 2.5, axis=1), "ic_superior": np.percentile(dif, 97.5, axis=1),
                        "ep_bootstrap": dif.std(axis=1, ddof=1)})
    jan["p_valor"] = 2 * stats.norm.sf(np.abs(jan["diferenca"] / jan["ep_bootstrap"]))
    jan = multiplicidade.adicionar_fdr(jan, None)
    salvar_tabela(serie, OUTPUT_DIR / "b3_hiato_quantis_serie.parquet", nota="Hiato em quantis incondicionais; P1; trimestral")
    salvar_tabela(tend, OUTPUT_DIR / "b3_tendencia_quantis.parquet", se_metodo=tendencia.METODO)
    salvar_tabela(jan, OUTPUT_DIR / "b3_quantis_janelas.parquet", se_metodo=f"bootstrap_rao_wu_estrato_upa_{n_boot}",
                  familia_fdr="os 5 quantis (BH)")
    return serie, tend


# ----------------------------------------------------------------------------------------- #
# B2 — composição × renda no tempo
# ----------------------------------------------------------------------------------------- #
def kitagawa_reclassificacao(m: pd.DataFrame, y: np.ndarray, w: np.ndarray) -> dict:
    """Médias e participações de Preta e Parda dentro de Negra (para Kitagawa entre janelas)."""
    neg = (m["raca"] == "Negra").to_numpy()
    out = {"m_Branca": np.average(y[m["raca"].to_numpy() == "Branca"], weights=w[m["raca"].to_numpy() == "Branca"])}
    for k in ("Preta", "Parda"):
        s = neg & (m["negra_det"] == k).to_numpy()
        out[f"s_{k}"] = w[s].sum() / w[neg].sum()
        out[f"m_{k}"] = np.average(y[s], weights=w[s])
    return out


def decompor_kitagawa(k0: dict, k1: dict) -> dict:
    """Δ ln m_Negra = composição (Δs com médias iniciais) + dentro (resto); e o hiato em log."""
    m0 = k0["s_Preta"] * k0["m_Preta"] + k0["s_Parda"] * k0["m_Parda"]
    m1 = k1["s_Preta"] * k1["m_Preta"] + k1["s_Parda"] * k1["m_Parda"]
    m_cf = k1["s_Preta"] * k0["m_Preta"] + k1["s_Parda"] * k0["m_Parda"]  # composição nova, médias antigas
    h0, h1 = np.log(k0["m_Branca"] / m0), np.log(k1["m_Branca"] / m1)
    return {"hiato_log_inicial": h0, "hiato_log_final": h1, "variacao_hiato_log": h1 - h0,
            "variacao_ln_media_negra": np.log(m1 / m0), "composicao_preta_parda": np.log(m_cf / m0),
            "dentro_dos_subgrupos": np.log(m1 / m_cf), "variacao_ln_media_branca": np.log(k1["m_Branca"] / k0["m_Branca"]),
            "pct_preta_inicial": 100 * k0["s_Preta"], "pct_preta_final": 100 * k1["s_Preta"]}


def _matriz_x(m: pd.DataFrame) -> pd.DataFrame:
    faixa = pd.cut(m["idade"], [17, 24, 29, 39, 49, 59, 200]).astype(str)
    X = pd.get_dummies(pd.DataFrame({"faixa": faixa, "instrucao": m["instrucao"].astype(str),
                                     "regiao": m["regiao"].astype(str), "sexo": m["sexo"].astype(str)}),
                       drop_first=True, dtype=float)
    return sm.add_constant(X, has_constant="add")


def jmp_componentes(m: pd.DataFrame, w: np.ndarray, colunas: list[str]) -> dict:
    """D = ΔX·β_B + Δθ·σ_B (versão de médias de Juhn-Murphy-Pierce): β_B e σ_B da regressão dos
    brancos; θ_g = média do resíduo do grupo (com β_B) ÷ σ_B."""
    X = _matriz_x(m).reindex(columns=colunas, fill_value=0.0).to_numpy(float)
    y = np.log(m["renda"].to_numpy(float))
    b = (m["raca"] == "Branca").to_numpy()
    n = (m["raca"] == "Negra").to_numpy()
    sw = np.sqrt(w[b])
    beta = np.linalg.lstsq(X[b] * sw[:, None], y[b] * sw, rcond=None)[0]
    res = y - X @ beta
    sigma = np.sqrt(np.average(res[b] ** 2, weights=w[b]))
    dX = np.average(X[b], axis=0, weights=w[b]) - np.average(X[n], axis=0, weights=w[n])
    theta_dif = (np.average(res[b], weights=w[b]) - np.average(res[n], weights=w[n])) / sigma
    return {"dX": dX, "beta": beta, "sigma": sigma, "dtheta": theta_dif,
            "D": float(np.average(y[b], weights=w[b]) - np.average(y[n], weights=w[n]))}


def jmp_mudanca(j0: dict, j1: dict) -> dict:
    return {"variacao_total": j1["D"] - j0["D"],
            "caracteristicas": float((j1["dX"] - j0["dX"]) @ j1["beta"]),
            "retornos": float(j0["dX"] @ (j1["beta"] - j0["beta"])),
            "posicao_nao_associada": float((j1["dtheta"] - j0["dtheta"]) * j1["sigma"]),
            "dispersao_residual": float(j0["dtheta"] * (j1["sigma"] - j0["sigma"])),
            "D_inicial": j0["D"], "D_final": j1["D"]}


def gerar_b2(con, n_boot: int = 100) -> tuple[pd.DataFrame, pd.DataFrame]:
    ms = {n: janela(con, t, todos_18=True) for n, t in JANELAS.items()}
    p1 = {n: m[m["em_p1"] & m["renda"].notna() & m["raca"].isin(["Branca", "Negra"])].reset_index(drop=True)
          for n, m in ms.items()}
    colunas = list(_matriz_x(pd.concat(p1.values())).columns)
    j0n, j1n = list(JANELAS)
    boot = {n: multiplicadores_rao_wu(p["upa"].to_numpy(), p["estrato"].to_numpy(), n_boot, seed=7) for n, p in p1.items()}
    # P4: todas as pessoas 18+ (fora de P1 = 0)
    p4 = {n: m[m["raca"].isin(["Branca", "Negra"])].reset_index(drop=True) for n, m in ms.items()}
    boot4 = {n: multiplicadores_rao_wu(p["upa"].to_numpy(), p["estrato"].to_numpy(), n_boot, seed=8) for n, p in p4.items()}

    def calc(wp1: dict, wp4: dict) -> dict:
        out = {}
        k = {n: kitagawa_reclassificacao(p1[n], p1[n]["renda"].to_numpy(float), wp1[n]) for n in JANELAS}
        out.update({f"P1|{a}": v for a, v in decompor_kitagawa(k[j0n], k[j1n]).items()})
        k4 = {n: kitagawa_reclassificacao(p4[n], np.nan_to_num(p4[n]["renda"].to_numpy(float)), wp4[n]) for n in JANELAS}
        out.update({f"P4|{a}": v for a, v in decompor_kitagawa(k4[j0n], k4[j1n]).items()})
        j = {n: jmp_componentes(p1[n], wp1[n], colunas) for n in JANELAS}
        out.update({f"JMP|{a}": v for a, v in jmp_mudanca(j[j0n], j[j1n]).items()})
        return out

    base = calc({n: p["peso"].to_numpy(float) for n, p in p1.items()}, {n: p["peso"].to_numpy(float) for n, p in p4.items()})
    reps = []
    for b in range(n_boot):
        wp1 = {n: p1[n]["peso"].to_numpy(float) * boot[n][1][boot[n][0], b] for n in JANELAS}
        wp4 = {n: p4[n]["peso"].to_numpy(float) * boot4[n][1][boot4[n][0], b] for n in JANELAS}
        reps.append(calc(wp1, wp4))
        if b % 20 == 0:
            print(f"B2 bootstrap {b}", flush=True)
    rep = pd.DataFrame(reps)
    linhas = []
    for chave, v in base.items():
        bloco, comp = chave.split("|")
        r = rep[chave].to_numpy(float)
        linhas.append({"bloco": bloco, "componente": comp, "estimativa": float(v), "ep_bootstrap": float(np.std(r, ddof=1)),
                       "ic_inferior": float(np.percentile(r, 2.5)), "ic_superior": float(np.percentile(r, 97.5))})
    dec = pd.DataFrame(linhas)
    salvar_tabela(dec, OUTPUT_DIR / "b2_decomposicao_tempo.parquet", se_metodo=f"bootstrap_rao_wu_estrato_upa_{n_boot}",
                  janelas={k: [f"{a}T{t}" for a, t in v] for k, v in JANELAS.items()},
                  nota="Log-pontos. P1/P4: Kitagawa da reclassificação Preta/Parda dentro de Negra; JMP: versão de médias")
    coorte = gerar_b2_coortes(con)
    return dec, coorte


def gerar_b2_coortes(con) -> pd.DataFrame:
    """% Preta entre as pessoas de 18+ por coorte de nascimento (5 anos), em cada ano: se sobe dentro
    da mesma coorte, a mudança não vem de nascimentos (reclassificação, ou mortalidade/migração
    diferenciais)."""
    df = con.execute(f"""
        WITH b AS (SELECT m.ano, m.V1028 AS w, m.ano - m.V2009 AS nasc, m.V2010 AS cor
                   FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1) m
                   WHERE m.trimestre = 2 AND m.V2009 >= 18 AND m.V2010 IN ('1','2','3','4','5'))
        SELECT ano, CAST(FLOOR(nasc / 5) * 5 AS INTEGER) AS coorte_inicio, COUNT(*) AS n,
               100 * SUM(w) FILTER (WHERE cor = '2') / SUM(w) AS pct_preta,
               100 * SUM(w) FILTER (WHERE cor = '4') / SUM(w) AS pct_parda,
               100 * SUM(w) FILTER (WHERE cor = '1') / SUM(w) AS pct_branca
        FROM b WHERE nasc BETWEEN 1950 AND 1994 GROUP BY 1, 2 ORDER BY 2, 1""").df()
    salvar_tabela(df, OUTPUT_DIR / "b2_composicao_racial_coortes.parquet",
                  nota="2º trimestres; pessoas 18+; coortes de nascimento de 5 anos (1950–1994)")
    return df


# ----------------------------------------------------------------------------------------- #
# B4 — coortes (APC)
# ----------------------------------------------------------------------------------------- #
def log_hiato_delta(y, w, upa, est, dom_a, dom_b) -> tuple[float, float]:
    za, ma = variancia.influencia_media(y, w, dom_a)
    zb, mb = variancia.influencia_media(y, w, dom_b)
    v, _ = variancia.variancia_linearizada(za / ma - zb / mb, upa, est)
    return float(np.log(ma / mb)), float(np.sqrt(max(v, 0.0)))


def deaton_paxson(periodos: np.ndarray) -> np.ndarray:
    """Dummies de período transformadas (Deaton 1997 — *a confirmar*): para t = 3…T,
    d*_t = d_t − [(t − 1)·d_2 − (t − 2)·d_1]; efeitos de período somam zero e são ortogonais a
    uma tendência linear."""
    ps = np.sort(np.unique(periodos))
    idx = np.searchsorted(ps, periodos)
    D = np.zeros((len(periodos), len(ps)))
    D[np.arange(len(periodos)), idx] = 1.0
    cols = []
    for t in range(2, len(ps)):  # t indexado em 0 ⇒ (t+1)-ésimo período
        tt = t + 1
        cols.append(D[:, t] - ((tt - 1) * D[:, 1] - (tt - 2) * D[:, 0]))
    return np.column_stack(cols) if cols else np.zeros((len(periodos), 0))


def apc(celulas: pd.DataFrame, com_periodo: bool = True) -> pd.DataFrame:
    """WLS das células (peso 1/var) em idade (grupos de 5) + coorte (grupos de 5) [+ período DP]."""
    c = celulas.dropna(subset=["log_hiato", "ep"]).copy()
    c = c[c["ep"] > 0]
    idade = pd.get_dummies(c["idade_grupo"].astype(str), prefix="idade", drop_first=True, dtype=float)
    coorte = pd.get_dummies(c["coorte_grupo"].astype(str), prefix="coorte", drop_first=True, dtype=float)
    partes = [np.ones((len(c), 1)), idade.to_numpy(), coorte.to_numpy()]
    nomes = ["const", *idade.columns, *coorte.columns]
    if com_periodo:
        P = deaton_paxson(c["ano"].to_numpy())
        partes.append(P)
        nomes += [f"periodo_dp_{i + 3}" for i in range(P.shape[1])]
    X = np.column_stack(partes)
    fit = sm.WLS(c["log_hiato"].to_numpy(), X, weights=1 / c["ep"].to_numpy() ** 2).fit()
    # EP de modelo com variâncias conhecidas: (X'WX)^-1 (sem reescalar pelo resíduo)
    W = 1 / c["ep"].to_numpy() ** 2
    cov = np.linalg.inv((X * W[:, None]).T @ X)
    ep = np.sqrt(np.diag(cov))
    return pd.DataFrame({"termo": nomes, "estimativa": fit.params, "ep": ep,
                         "ic_inferior": fit.params - Z95 * ep, "ic_superior": fit.params + Z95 * ep,
                         "p_valor": 2 * stats.norm.sf(np.abs(fit.params / ep)),
                         "modelo": "APC (Deaton-Paxson)" if com_periodo else "AC (sem período)",
                         "qui2_por_gl": float(np.sum(W * fit.resid ** 2) / max(len(c) - X.shape[1], 1))})


def gerar_b4(con) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # (1) mesma idade, coortes diferentes
    comp = []
    for nome, tris in JANELAS.items():
        m = janela(con, tris)
        m = m[m["raca"].isin(["Branca", "Negra"])]
        y, w = m["renda"].to_numpy(float), m["peso"].to_numpy(float)
        upa, est, raca, idade = m["upa"].to_numpy(), m["estrato"].to_numpy(), m["raca"].to_numpy(object), m["idade"].to_numpy()
        for lo, hi in ((25, 34), (35, 44), (45, 54)):
            faixa = (idade >= lo) & (idade <= hi)
            lh, ep = log_hiato_delta(y, w, upa, est, faixa & (raca == "Branca"), faixa & (raca == "Negra"))
            ano_ref = 2012 if nome == "2012" else 2025.5
            comp.append({"janela": nome, "idade": f"{lo}–{hi}", "nascidos": f"{int(ano_ref - hi)}–{int(ano_ref - lo)}",
                         "log_hiato": lh, "ep": ep, "hiato_pct": 100 * (np.exp(lh) - 1)})
    comp = pd.DataFrame(comp)
    dif = []
    for idade_, x in comp.groupby("idade"):
        a, b = x.set_index("janela").loc["2012"], x.set_index("janela").loc["2025T3-2026T2"]
        d, ep = b["log_hiato"] - a["log_hiato"], np.hypot(a["ep"], b["ep"])
        dif.append({"janela": "diferença 2025–26 − 2012", "idade": idade_, "nascidos": f"{b['nascidos']} vs. {a['nascidos']}",
                    "log_hiato": d, "ep": ep, "ic_inferior": d - Z95 * ep, "ic_superior": d + Z95 * ep})
    comp["ic_inferior"] = comp["log_hiato"] - Z95 * comp["ep"]
    comp["ic_superior"] = comp["log_hiato"] + Z95 * comp["ep"]
    comp = pd.concat([comp, pd.DataFrame(dif)], ignore_index=True)
    # (2) células ano × idade simples (25–59), 4 trimestres por ano (2026: 2)
    cel = []
    for ano in sorted({a for a, _ in trimestres(con)}):
        if ano > 2025:
            continue  # 2026 incompleto: fica fora do APC (períodos anuais completos)
        m = janela(con, [(ano, t) for t in (1, 2, 3, 4)])
        m = m[m["raca"].isin(["Branca", "Negra"]) & (m["idade"] >= 25) & (m["idade"] <= 59)]
        y, w = m["renda"].to_numpy(float), m["peso"].to_numpy(float)
        upa, est, raca, idade = m["upa"].to_numpy(), m["estrato"].to_numpy(), m["raca"].to_numpy(object), m["idade"].to_numpy()
        zs, info = [], []
        for i in range(25, 60):
            da, db = (idade == i) & (raca == "Branca"), (idade == i) & (raca == "Negra")
            za, ma = variancia.influencia_media(y, w, da)
            zb, mb = variancia.influencia_media(y, w, db)
            zs.append(za / ma - zb / mb)
            info.append((i, np.log(ma / mb), int(da.sum()), int(db.sum())))
        eps = []
        for k in range(0, len(zs), 12):
            cov, _ = variancia.variancia_linearizada(np.column_stack(zs[k:k + 12]), upa, est)
            eps += list(np.sqrt(np.maximum(np.diag(np.atleast_2d(cov)), 0)))
        for (i, lh, na, nb), ep in zip(info, eps):
            cel.append({"ano": ano, "idade": i, "nascimento": ano - i, "log_hiato": lh, "ep": ep, "n_branca": na, "n_negra": nb})
        print(f"B4 {ano}", flush=True)
    cel = pd.DataFrame(cel)
    cel["idade_grupo"] = (cel["idade"] // 5) * 5
    cel["coorte_grupo"] = (cel["nascimento"] // 5) * 5
    modelos = pd.concat([apc(cel, True), apc(cel, False)], ignore_index=True)
    modelos = multiplicidade.adicionar_fdr(modelos.assign(p_valor=np.where(modelos["termo"].str.startswith("coorte"),
                                                                           modelos["p_valor"], np.nan)), ["modelo"])
    salvar_tabela(comp, OUTPUT_DIR / "b4_mesma_idade_coortes.parquet", se_metodo=variancia.SE_METODO,
                  nota="Log-pontos (ln média Branca − ln média Negra), P1")
    salvar_tabela(cel, OUTPUT_DIR / "b4_celulas_idade_ano.parquet", se_metodo=variancia.SE_METODO)
    salvar_tabela(modelos, OUTPUT_DIR / "b4_apc.parquet", se_metodo="wls_variancias_conhecidas",
                  restricao="Deaton-Paxson: efeitos de período somam zero e são ortogonais à tendência linear (APC); "
                            "sensibilidade AC: sem período",
                  familia_fdr="efeitos de coorte de cada modelo (BH)")
    return comp, cel, modelos


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--so", nargs="*", default=None, help="b1 b2 b3 b4 b5 b6")
    fazer = set(parser.parse_args().so or ["b1", "b2", "b3", "b4", "b5", "b6"])
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    if "b1" in fazer or "b6" in fazer:
        tend, _ = gerar_b1()
        if "b6" in fazer:
            gerar_b6(tend)
    if "b5" in fazer:
        gerar_b5(con)
    if "b3" in fazer:
        gerar_b3(con)
    if "b2" in fazer:
        gerar_b2(con)
    if "b4" in fazer:
        gerar_b4(con)


if __name__ == "__main__":
    main()
