"""Onda 1 — Bloco A: a diferença existe? De quanto é? (`docs/PLANO_DE_ANALISE.md`, Bloco A; ficha
`docs/studies/A/ficha.md`). População de referência (ocupados 18+ com renda do trabalho principal
> 0), renda habitual real do trabalho principal; PNAD Contínua trimestral, extrato v2.

- **A2** — o hiato em quatro métricas lado a lado, com IC design-based (linearização Estrato/UPA):
  diferença em R$, razão Branca/grupo, log-pontos ln(razão) e "o grupo ganha X% da renda Branca".
  Hiato % = 100 × (razão − 1), relativo ao grupo de menor renda (convenção do Hub).
- **A3** — onde na distribuição: quantis P10…P99 por raça, hiato por quantil e razões P90/P50 e
  P50/P10, com IC por bootstrap Rao-Wu Estrato/UPA (200 réplicas), nos 2º trimestres.
- **A4** — quanto da desigualdade total é entre raças: Theil T e Theil L (MLD) entre/dentro e Gini,
  com Branca, Negra, Indígena e Amarela.
- **A5** — probabilidade de estar em cada décimo nacional: participação de cada raça por décimo,
  índice de representação (participação no décimo ÷ participação na população) e razão de chances
  de estar no topo 10% e na base 10% (Negra e Indígena vs. Branca). Peso empatado nos limiares
  repartido (`pnadc_core.fracao_na_fatia`).
- **A6** — dominância estocástica de 1ª ordem: F_grupo(c) − F_Branca(c) em 99 pontos da distribuição
  conjunta, com IC; dominância = diferença positiva em todos os pontos.
- **A7** — A2 também para a renda por hora do trabalho principal (`VD4016` ÷ (`V4039` × 4,345)).
  A versão domiciliar per capita é o T1 (`bloco_t.py`).

Uso:
    python -m src.processing.bloco_a
"""
from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd

from src.inference import variancia
from src.inference.saida import salvar_tabela
from src.processing.agregacoes_pnadc import DEFLATOR_PATH, OUTPUT_DIR, PARQUET_GLOB
from src.processing.sensibilidade_populacao import Z95
from src.utils import pnadc_core
from src.utils import populacao as pop

QUANTIS = [0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
N_BOOT = 200
RACAS = ["Branca", "Negra", "Indígena", "Amarela"]
COMPARADAS = ["Negra", "Indígena"]
RACA_SQL = """CASE m.V2010 WHEN '1' THEN 'Branca' WHEN '2' THEN 'Negra' WHEN '4' THEN 'Negra'
                           WHEN '5' THEN 'Indígena' WHEN '3' THEN 'Amarela' END"""


def micro_p1(con, ano: int, tri: int, separar_preta_parda: bool = False) -> pd.DataFrame:
    raca_sql = RACA_SQL.replace("WHEN '2' THEN 'Negra' WHEN '4' THEN 'Negra'",
                                "WHEN '2' THEN 'Preta' WHEN '4' THEN 'Parda'") if separar_preta_parda else RACA_SQL
    return con.execute(f"""
        SELECT {raca_sql} AS raca, m.V1028 AS peso, m.UPA AS upa, m.Estrato AS estrato,
               m.VD4016 * d.deflator_habitual AS renda, m.V4039 AS horas
        FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1) m
        LEFT JOIN read_parquet('{DEFLATOR_PATH}') d ON m.ano = d.ano AND m.trimestre = d.trimestre AND m.UF = d.UF
        WHERE m.ano = {ano} AND m.trimestre = {tri} AND {pop.REFERENCIA.sql('m')} AND m.V2010 IN ('1','2','3','4','5')
    """).df()


# ----------------------------------------------------------------------------------------- #
# A2 / A7
# ----------------------------------------------------------------------------------------- #
def metricas_hiato(y, w, upa, estrato, ref: np.ndarray, alvo: np.ndarray) -> dict:
    """Diferença, razão, log-pontos e % da renda de referência, com EP design-based."""
    za, ma = variancia.influencia_media(y, w, ref)
    zb, mb = variancia.influencia_media(y, w, alvo)
    cov, _ = variancia.variancia_linearizada(np.column_stack([za, zb]), upa, estrato)
    ep_dif = float(np.sqrt(max(cov[0, 0] + cov[1, 1] - 2 * cov[0, 1], 0.0)))
    r = ma / mb
    ep_r = variancia.razao_delta_design(za, zb, ma, mb, upa, estrato)
    out = {"media_branca": ma, "media_grupo": mb,
           "diferenca_rs": ma - mb, "ep_diferenca_rs": ep_dif,
           "razao": r, "ep_razao": ep_r,
           "log_pontos": float(np.log(r)), "ep_log_pontos": ep_r / r,
           "pct_da_renda_branca": 100 / r, "ep_pct_da_renda_branca": 100 * ep_r / r**2,
           "hiato_percentual": 100 * (r - 1), "ep_hiato_percentual": 100 * ep_r}
    for k in ("diferenca_rs", "razao", "log_pontos", "pct_da_renda_branca", "hiato_percentual"):
        e = out["ep_" + k]
        out[k + "_ic_inferior"], out[k + "_ic_superior"] = out[k] - Z95 * e, out[k] + Z95 * e
    return out


def a2_a7(m: pd.DataFrame, ano: int, tri: int) -> list[dict]:
    linhas = []
    upa, est, w = m["upa"].to_numpy(), m["estrato"].to_numpy(), m["peso"].to_numpy(float)
    raca = m["raca"].to_numpy(object)
    hora = m["renda"].to_numpy(float) / (m["horas"].to_numpy(float) * 4.345)
    tem_hora = np.isfinite(hora) & (m["horas"].fillna(0).to_numpy(float) > 0)
    for conceito, y, dom in (("mensal", m["renda"].to_numpy(float), np.ones(len(m), bool)),
                             ("por_hora", np.where(tem_hora, hora, 0.0), tem_hora)):
        for g in COMPARADAS:
            d = metricas_hiato(y, w, upa, est, dom & (raca == "Branca"), dom & (raca == g))
            linhas.append({"ano": ano, "trimestre": tri, "conceito": conceito, "comparacao": f"Branca × {g}", **d})
    return linhas


def a2_preta_parda(m: pd.DataFrame, ano: int, tri: int) -> dict:
    """A2 para Preta × Parda (dentro da população negra; R11): hiato % = Preta ÷ Parda − 1, como em
    `hiato_preta_parda`, com IC por método delta."""
    raca = m["raca"].to_numpy(object)
    d = metricas_hiato(m["renda"].to_numpy(float), m["peso"].to_numpy(float), m["upa"].to_numpy(),
                       m["estrato"].to_numpy(), raca == "Preta", raca == "Parda")
    d = {k.replace("media_branca", "media_preta").replace("media_grupo", "media_parda")
          .replace("pct_da_renda_branca", "pct_parda_da_renda_preta"): v for k, v in d.items()}
    return {"ano": ano, "trimestre": tri, "conceito": "mensal", "comparacao": "Preta × Parda", **d}


# ----------------------------------------------------------------------------------------- #
# A3 — quantis com bootstrap Rao-Wu
# ----------------------------------------------------------------------------------------- #
def multiplicadores_rao_wu(upa, estrato, n_boot: int = N_BOOT, seed: int = 0):
    """(código da UPA de cada observação, matriz n_upas × n_boot de multiplicadores de peso) do
    bootstrap de Rao-Wu: em cada estrato sorteia n_h − 1 UPAs com reposição e reescala por
    n_h/(n_h − 1) × multiplicidade; estratos de UPA única ficam fixos (mesma convenção de
    `variancia.erro_padrao_bootstrap_estrato_upa`)."""
    upa_cod, estrato_da_upa, n_estratos = variancia._codigos_upa_estrato(upa, estrato)
    n_upas = len(estrato_da_upa)
    n_h = np.bincount(estrato_da_upa, minlength=n_estratos)
    ordem = np.argsort(estrato_da_upa, kind="stable")
    inicio = np.concatenate([[0], np.cumsum(n_h)[:-1]])
    m_h = np.maximum(n_h - 1, 0)
    estr_sorteio = np.repeat(np.arange(n_estratos), m_h)
    fator = np.where(n_h > 1, n_h / np.maximum(n_h - 1, 1), 1.0)[estrato_da_upa]
    fixas = n_h[estrato_da_upa] == 1
    rng = np.random.default_rng(seed)
    mult = np.empty((n_upas, n_boot))
    for b in range(n_boot):
        pos = inicio[estr_sorteio] + np.floor(rng.random(len(estr_sorteio)) * n_h[estr_sorteio]).astype(int)
        cont = np.bincount(ordem[pos], minlength=n_upas).astype(float)
        mult[:, b] = np.where(fixas, 1.0, cont * fator)
    return upa_cod, mult


def _quantis(v_ord: np.ndarray, w_ord: np.ndarray, qs) -> np.ndarray:
    """Mesma convenção de `pnadc_core.quantil_ponderado` (primeiro valor com F ≥ q)."""
    cum = np.cumsum(w_ord, axis=0)
    cum = cum / cum[-1]
    if cum.ndim == 1:
        return v_ord[np.minimum(np.searchsorted(cum, qs), len(v_ord) - 1)]
    return np.stack([v_ord[np.minimum(np.searchsorted(cum[:, b], qs), len(v_ord) - 1)]
                     for b in range(cum.shape[1])], axis=1)


def a3(m: pd.DataFrame, ano: int, tri: int, n_boot: int = N_BOOT) -> list[dict]:
    upa_cod, mult = multiplicadores_rao_wu(m["upa"].to_numpy(), m["estrato"].to_numpy(), n_boot)
    y, w, raca = m["renda"].to_numpy(float), m["peso"].to_numpy(float), m["raca"].to_numpy(object)
    est, rep = {}, {}
    for g in ["Branca", *COMPARADAS]:
        sel = np.flatnonzero(raca == g)
        o = sel[np.argsort(y[sel], kind="stable")]
        est[g] = _quantis(y[o], w[o], QUANTIS)
        rep[g] = _quantis(y[o], w[o][:, None] * mult[upa_cod[o]], QUANTIS)  # q × n_boot
    linhas = []
    for g in ["Branca", *COMPARADAS]:
        for i, q in enumerate(QUANTIS):
            r = rep[g][i]
            linhas.append({"ano": ano, "trimestre": tri, "raca": g, "medida": f"P{int(q * 100)}", "valor": est[g][i],
                           "ep_bootstrap": float(np.std(r, ddof=1)),
                           "ic_inferior": float(np.percentile(r, 2.5)), "ic_superior": float(np.percentile(r, 97.5))})
        p = dict(zip(QUANTIS, range(len(QUANTIS))))
        for nome, (a, b) in {"P90/P50": (0.90, 0.50), "P50/P10": (0.50, 0.10), "P90/P10": (0.90, 0.10)}.items():
            r = rep[g][p[a]] / rep[g][p[b]]
            linhas.append({"ano": ano, "trimestre": tri, "raca": g, "medida": nome, "valor": est[g][p[a]] / est[g][p[b]],
                           "ep_bootstrap": float(np.std(r, ddof=1)),
                           "ic_inferior": float(np.percentile(r, 2.5)), "ic_superior": float(np.percentile(r, 97.5))})
    for g in COMPARADAS:
        for i, q in enumerate(QUANTIS):
            r = 100 * (rep["Branca"][i] / rep[g][i] - 1)
            linhas.append({"ano": ano, "trimestre": tri, "raca": f"hiato Branca × {g}", "medida": f"P{int(q * 100)}",
                           "valor": 100 * (est["Branca"][i] / est[g][i] - 1), "ep_bootstrap": float(np.std(r, ddof=1)),
                           "ic_inferior": float(np.percentile(r, 2.5)), "ic_superior": float(np.percentile(r, 97.5))})
    return linhas


# ----------------------------------------------------------------------------------------- #
# A4 — Theil T, Theil L (MLD), Gini
# ----------------------------------------------------------------------------------------- #
def theil_l_entre_dentro(y, w, grupos) -> dict:
    """MLD = Σ w ln(μ/y) / Σ w; entre = Σ_g s_g ln(μ/μ_g) (s_g = participação na população);
    dentro = Σ_g s_g MLD_g. Exige y > 0."""
    y, w, grupos = np.asarray(y, float), np.asarray(w, float), np.asarray(grupos, object)
    mu = np.average(y, weights=w)
    total = float(np.average(np.log(mu / y), weights=w))
    entre = dentro = 0.0
    for g in np.unique(grupos):
        s = grupos == g
        sg, mg = w[s].sum() / w.sum(), np.average(y[s], weights=w[s])
        entre += sg * np.log(mu / mg)
        dentro += sg * np.average(np.log(mg / y[s]), weights=w[s])
    return {"theil_l_total": total, "theil_l_entre": float(entre), "theil_l_dentro": float(dentro),
            "theil_l_pct_entre": 100 * float(entre) / total}


def a4(m: pd.DataFrame, ano: int, tri: int) -> dict:
    y, w, g = m["renda"].to_numpy(float), m["peso"].to_numpy(float), m["raca"].to_numpy(object)
    t, _ = pnadc_core.decomposicao_theil_entre_dentro(m, "renda", "raca", "peso")
    return {"ano": ano, "trimestre": tri, "gini_total": pnadc_core.calcular_gini_ponderado(y, w),
            "theil_t_total": t.get("theil_total"), "theil_t_pct_entre": t.get("pct_entre_grupos"),
            **theil_l_entre_dentro(y, w, g)}


# ----------------------------------------------------------------------------------------- #
# A5 — décimos nacionais
# ----------------------------------------------------------------------------------------- #
def a5(m: pd.DataFrame, ano: int, tri: int) -> list[dict]:
    y, w, raca = m["renda"].to_numpy(float), m["peso"].to_numpy(float), m["raca"].to_numpy(object)
    upa, est = m["upa"].to_numpy(), m["estrato"].to_numpy()
    pop_share = {g: w[raca == g].sum() / w.sum() for g in RACAS}
    linhas = []
    fracs = {d: pnadc_core.fracao_na_fatia(y, w, d / 10, (d + 1) / 10) for d in range(10)}
    for d, f in fracs.items():
        wd = w * f
        for g in RACAS:
            share = wd[raca == g].sum() / wd.sum()
            linhas.append({"ano": ano, "trimestre": tri, "decimo": f"D{d + 1:02d}", "raca": g, "pct_do_decimo": 100 * share,
                           "pct_da_populacao": 100 * pop_share[g], "indice_representacao": share / pop_share[g]})
    # razão de chances de estar no topo/base 10% (vs. Branca), EP do log-OR por delta sobre as
    # proporções de domínio (os limiares são tratados como fixos)
    for nome, f in (("topo10", fracs[9]), ("base10", fracs[0])):
        p, zs = {}, {}
        for g in ["Branca", *COMPARADAS]:
            zz, pg = variancia.influencia_media(f, w, raca == g)
            p[g], zs[g] = pg, zz
        for g in COMPARADAS:
            lor = np.log(p[g] / (1 - p[g])) - np.log(p["Branca"] / (1 - p["Branca"]))
            zl = zs[g] / (p[g] * (1 - p[g])) - zs["Branca"] / (p["Branca"] * (1 - p["Branca"]))
            var, _ = variancia.variancia_linearizada(zl, upa, est)
            ep = float(np.sqrt(max(var, 0.0)))
            linhas.append({"ano": ano, "trimestre": tri, "decimo": nome, "raca": g,
                           "prob_grupo_pct": 100 * p[g], "prob_branca_pct": 100 * p["Branca"],
                           "razao_de_chances": float(np.exp(lor)),
                           "rc_ic_inferior": float(np.exp(lor - Z95 * ep)), "rc_ic_superior": float(np.exp(lor + Z95 * ep))})
    return linhas


# ----------------------------------------------------------------------------------------- #
# A6 — dominância estocástica de 1ª ordem
# ----------------------------------------------------------------------------------------- #
def a6(m: pd.DataFrame, ano: int, tri: int) -> list[dict]:
    y, w, raca = m["renda"].to_numpy(float), m["peso"].to_numpy(float), m["raca"].to_numpy(object)
    upa, est = m["upa"].to_numpy(), m["estrato"].to_numpy()
    grade = np.unique([pnadc_core.quantil_ponderado(y, w, q / 100) for q in range(1, 100)])
    linhas = []
    for g in COMPARADAS:
        difs, zs = [], []
        for c in grade:
            ind = (y <= c).astype(float)
            r = variancia.diferenca_medias_design(ind, w, upa, est, raca == g, raca == "Branca")
            difs.append(r["diferenca"])
            zs.append(r["diferenca"] / r["ep_diferenca"] if r["ep_diferenca"] > 0 else np.nan)
        difs, zs = np.array(difs), np.array(zs)
        linhas.append({"ano": ano, "trimestre": tri, "comparacao": f"Branca domina {g}?", "n_pontos": len(grade),
                       "pontos_com_dif_positiva": int((difs > 0).sum()),
                       "pontos_positivos_significativos": int((zs > Z95).sum()),
                       "pontos_negativos_significativos": int((zs < -Z95).sum()),
                       "menor_diferenca_pp": 100 * float(difs.min()), "maior_diferenca_pp": 100 * float(difs.max()),
                       "menor_z": float(np.nanmin(zs)),
                       "dominancia_branca": bool((difs > 0).all() and (zs > Z95).all())})
    return linhas


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--so", nargs="*", default=None, help="a2 a2pp a3 a4 a5 a6 (padrão: todos)")
    fazer = set(parser.parse_args().so or ["a2", "a2pp", "a3", "a4", "a5", "a6"])
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    tris = [(int(a), int(t)) for a, t in con.execute(
        f"SELECT DISTINCT ano, trimestre FROM read_parquet('{PARQUET_GLOB}', hive_partitioning=1) ORDER BY 1, 2").fetchall()]
    r2, r2pp, r3, r4, r5, r6 = [], [], [], [], [], []
    for ano, tri in tris:
        if "a2pp" in fazer:
            r2pp.append(a2_preta_parda(micro_p1(con, ano, tri, separar_preta_parda=True), ano, tri))
        if not fazer - {"a2pp"}:
            continue
        m = micro_p1(con, ano, tri)
        if "a2" in fazer:
            r2 += a2_a7(m, ano, tri)
        if "a4" in fazer:
            r4.append(a4(m, ano, tri))
        if "a5" in fazer:
            r5 += a5(m, ano, tri)
        if tri == 2:  # A3 (bootstrap) e A6 nos 2º trimestres
            if "a3" in fazer:
                r3 += a3(m, ano, tri)
            if "a6" in fazer:
                r6 += a6(m, ano, tri)
        print(f"A {ano}T{tri}", flush=True)
    SE = variancia.SE_METODO
    saidas = [("a2", r2, "a2_metricas_hiato", SE), ("a2pp", r2pp, "a2_metricas_hiato_preta_parda", SE), ("a3", r3, "a3_hiato_quantis", "bootstrap_rao_wu_estrato_upa_200"),
              ("a4", r4, "a4_desigualdade_decomposicao", None), ("a5", r5, "a5_representacao_decimos", SE),
              ("a6", r6, "a6_dominancia", SE)]
    for chave, dados, nome, se in saidas:
        if chave in fazer:
            salvar_tabela(pd.DataFrame(dados), OUTPUT_DIR / f"{nome}.parquet", **({"se_metodo": se} if se else {}))


if __name__ == "__main__":
    main()
