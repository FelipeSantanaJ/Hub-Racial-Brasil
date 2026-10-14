"""Onda 2 — Bloco C: raça × gênero (`docs/PLANO_DE_ANALISE.md`, Bloco C; fichas em `docs/studies/C1`…`C5`).
Sempre com a versão do Bloco T ao lado: P4 (todos os adultos, fora de P1 com renda zero) e, quando cabe, a renda
domiciliar per capita (PNAD anual, raça × sexo da pessoa).

- **C1** — as células raça × sexo: médias, razão para o homem branco (HB), log-pontos, % da renda de HB; quantis com
  bootstrap; Theil entre células.
- **C2** — interação: DiD em log das médias e coeficiente β3 de ln y ~ raça × sexo (com e sem controles), com EP
  design-based (função de influência do WLS linearizada por Estrato/UPA); tendência da interação (EWC).
- **C3** — Shapley de dois fatores (raça, gênero) da distância HB − mulher negra, com a interação à parte e as duas
  ordens sequenciais; reconciliação com `decomposicao_raca_genero`.
- **C4** — penalidade da maternidade por raça (filho(a) de 0–5 no domicílio; chave UPA + V1008 + V1014).
- **C6** — estado conjugal e chefia: associação com Pr(P1), ln renda e horas por raça × sexo; hiato racial
  condicional com e sem esses controles.
- **C5** — trabalho doméstico remunerado (`VD4009` 03/04): participação, carteira, renda e Kitagawa do hiato
  entre mulheres.

Uso:
    python -m src.processing.bloco_c [--so c123 c4 c5 anual quantis]
"""
from __future__ import annotations

import argparse

import duckdb
import numpy as np
import pandas as pd
from scipy import stats

from src.inference import multiplicidade, precisao, tendencia, variancia
from src.inference.saida import salvar_tabela
from src.processing.agregacoes_pnadc import DEFLATOR_PATH, OUTPUT_DIR, PARQUET_GLOB
from src.processing.bloco_a import _quantis, multiplicadores_rao_wu, theil_l_entre_dentro
from src.processing.sensibilidade_populacao import ANUAL_GLOB, Z95
from src.utils import pnadc_core
from src.utils import populacao as pop

RACAS_C = ["Branca", "Negra", "Indígena"]
SEXOS = ["Homem", "Mulher"]
CELULAS = [(r, s) for r in RACAS_C for s in SEXOS]
SIGLA = {("Branca", "Homem"): "HB", ("Branca", "Mulher"): "MB", ("Negra", "Homem"): "HN", ("Negra", "Mulher"): "MN",
         ("Indígena", "Homem"): "HI", ("Indígena", "Mulher"): "MI"}
JANELAS = {"2012": [(2012, t) for t in (1, 2, 3, 4)],
           "2025T3-2026T2": [(2025, 3), (2025, 4), (2026, 1), (2026, 2)]}
RACA_SQL = """CASE m.V2010 WHEN '1' THEN 'Branca' WHEN '2' THEN 'Negra' WHEN '4' THEN 'Negra'
                           WHEN '5' THEN 'Indígena' WHEN '3' THEN 'Amarela' END"""


# ----------------------------------------------------------------------------------------- #
# dados
# ----------------------------------------------------------------------------------------- #
def micro_c(con, ano: int, tri: int) -> pd.DataFrame:
    """Pessoas de 18+ do trimestre. `filho_0a5`: a pessoa é responsável (01) e há criança de 0–5 filha
    do responsável (04/05), ou é cônjuge (02/03) e há criança de 0–5 filha do casal ou enteada (04/06),
    no mesmo domicílio (UPA + V1008 + V1014)."""
    return con.execute(f"""
        WITH t AS (
          SELECT m.*,
                 MAX(CASE WHEN m.V2009 <= 5 AND m.V2005 IN ('04','05') THEN 1 ELSE 0 END)
                     OVER (PARTITION BY m.UPA, m.V1008, m.V1014) AS f_resp,
                 MAX(CASE WHEN m.V2009 <= 5 AND m.V2005 IN ('04','06') THEN 1 ELSE 0 END)
                     OVER (PARTITION BY m.UPA, m.V1008, m.V1014) AS f_conj,
                 MAX(CASE WHEN m.V2009 <= 5 THEN 1 ELSE 0 END) OVER (PARTITION BY m.UPA, m.V1008, m.V1014) AS c05,
                 MAX(CASE WHEN m.V2005 IN ('02','03') THEN 1 ELSE 0 END)
                     OVER (PARTITION BY m.UPA, m.V1008, m.V1014) AS conj_dom
          FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1) m
          WHERE m.ano = {ano} AND m.trimestre = {tri})
        SELECT {ano} AS ano, {tri} AS trimestre, {RACA_SQL} AS raca,
               CASE m.V2007 WHEN '1' THEN 'Homem' WHEN '2' THEN 'Mulher' END AS sexo, m.V2009 AS idade,
               m.VD3004 AS instrucao, SUBSTR(CAST(m.UF AS VARCHAR), 1, 1) AS regiao, m.V2005 AS condicao_dom,
               m.VD4009 AS posicao, m.V1028 AS peso, m.UPA AS upa, m.Estrato AS estrato,
               COALESCE({pop.REFERENCIA.sql('m')}, FALSE) AS em_p1,
               CASE WHEN {pop.REFERENCIA.sql('m')} THEN m.VD4016 * d.deflator_habitual END AS renda,
               m.VD4002 = '1' AS ocupado,
               (m.V2005 = '01' AND m.f_resp = 1) OR (m.V2005 IN ('02','03') AND m.f_conj = 1) AS filho_0a5,
               m.c05 = 1 AS crianca_0a5_dom, m.V2005 IN ('01','02','03') AS resp_ou_conj,
               m.V2005 = '01' AS chefe,
               (m.V2005 = '01' AND m.conj_dom = 1) OR m.V2005 IN ('02','03') AS em_casal, m.V4039 AS horas
        FROM t m
        LEFT JOIN read_parquet('{DEFLATOR_PATH}') d ON m.ano = d.ano AND m.trimestre = d.trimestre AND m.UF = d.UF
        WHERE m.V2009 >= {pop.IDADE_MINIMA_REFERENCIA} AND m.V2010 IN ('1','2','3','4','5') AND m.V2007 IN ('1','2')
    """).df()


def trimestres(con) -> list[tuple[int, int]]:
    return [(int(a), int(t)) for a, t in con.execute(
        f"SELECT DISTINCT ano, trimestre FROM read_parquet('{PARQUET_GLOB}', hive_partitioning=1) ORDER BY 1, 2").fetchall()]


# ----------------------------------------------------------------------------------------- #
# ferramentas
# ----------------------------------------------------------------------------------------- #
def medias_z(y: np.ndarray, w: np.ndarray, dominios: dict) -> dict:
    """{nome: (média, z linearizado)} para cada domínio (sobre o mesmo universo)."""
    out = {}
    for k, d in dominios.items():
        z, mu = variancia.influencia_media(np.where(d, y, 0.0), w, d)
        out[k] = (mu, z)
    return out

def combinacoes(mz: dict, combos: dict[str, dict], upa, est, log: bool = True) -> pd.DataFrame:
    """Estimativa e EP de Σ coef·ln(média) (ou Σ coef·média) para cada combinação, numa única
    linearização (covariância entre células incluída)."""
    nomes, ests, zs = [], [], []
    for nome, coefs in combos.items():
        if any(not np.isfinite(mz[c][0]) or (log and mz[c][0] <= 0) for c in coefs):
            continue
        if log:
            e = sum(a * np.log(mz[c][0]) for c, a in coefs.items())
            z = sum(a * mz[c][1] / mz[c][0] for c, a in coefs.items())
        else:
            e = sum(a * mz[c][0] for c, a in coefs.items())
            z = sum(a * mz[c][1] for c, a in coefs.items())
        nomes.append(nome)
        ests.append(float(e))
        zs.append(z)
    if not nomes:
        return pd.DataFrame(columns=["metrica", "estimativa", "ep"])
    cov, _ = variancia.variancia_linearizada(np.column_stack(zs), upa, est)
    ep = np.sqrt(np.maximum(np.diag(np.atleast_2d(cov)), 0.0))
    return pd.DataFrame({"metrica": nomes, "estimativa": ests, "ep": ep})


def wls_design(y, X, w, upa, est, dominio=None, apenas: list[int] | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """WLS com EP design-based: ψ_i = (X'WX)⁻¹ x_i w_i e_i (zero fora do domínio), linearizado por
    Estrato/UPA. Devolve (β, EP, ψ n×k) — ψ permite combinar coeficientes de regressões em domínios
    diferentes da mesma amostra."""
    y, X, w = np.asarray(y, float), np.asarray(X, float), np.asarray(w, float)
    d = np.ones(len(y), bool) if dominio is None else np.asarray(dominio, bool)
    d = d & np.isfinite(y) & np.isfinite(X).all(axis=1)
    # colunas sem nenhum valor no domínio (ex.: dummy de idade fora da faixa) saem; β = NaN nelas
    usa = np.abs(X[d]).sum(axis=0) > 0
    Xd, yd, wd = X[d][:, usa], y[d], w[d]
    A = (Xd * wd[:, None]).T @ Xd
    b_ = np.linalg.solve(A, (Xd * wd[:, None]).T @ yd)
    e = yd - Xd @ b_
    beta = np.full(X.shape[1], np.nan)
    beta[usa] = b_
    # ψ só das colunas pedidas (`apenas`): poupa memória com muitas dummies e milhões de linhas
    cols = np.flatnonzero(usa) if apenas is None else np.array([c for c in apenas if usa[c]], int)
    pos = np.searchsorted(np.flatnonzero(usa), cols)
    Ainv = np.linalg.inv(A)[pos]                      # linhas de (X'WX)⁻¹ das colunas pedidas
    psi = np.zeros((len(y), X.shape[1]))
    psi[np.ix_(d, cols)] = (Xd * (wd * e)[:, None]) @ Ainv.T
    ep = np.full(X.shape[1], np.nan)
    if len(cols):
        cov, _ = variancia.variancia_linearizada(psi[:, cols], upa, est)
        ep[cols] = np.sqrt(np.maximum(np.diag(np.atleast_2d(cov)), 0.0))
    return beta, ep, psi


def delta_generico(funcoes: dict, theta: np.ndarray, Z: np.ndarray, upa, est) -> pd.DataFrame:
    """Método delta numérico: para cada f(θ) (θ = vetor de médias/proporções de domínio com z em Z,
    n × k), z_f = Z·∇f; EP por linearização Estrato/UPA. Diferenças centrais."""
    nomes, ests, zf = [], [], []
    for nome, f in funcoes.items():
        g = np.zeros(len(theta))
        for j in range(len(theta)):
            h = 1e-6 * max(abs(theta[j]), 1.0)
            tp, tm = theta.copy(), theta.copy()
            tp[j] += h
            tm[j] -= h
            g[j] = (f(tp) - f(tm)) / (2 * h)
        nomes.append(nome)
        ests.append(float(f(theta)))
        zf.append(Z @ g)
    cov, _ = variancia.variancia_linearizada(np.column_stack(zf), upa, est)
    return pd.DataFrame({"metrica": nomes, "estimativa": ests, "ep": np.sqrt(np.maximum(np.diag(np.atleast_2d(cov)), 0.0))})


def _ic(df: pd.DataFrame) -> pd.DataFrame:
    df["ic_inferior"] = df["estimativa"] - Z95 * df["ep"]
    df["ic_superior"] = df["estimativa"] + Z95 * df["ep"]
    return df


# ----------------------------------------------------------------------------------------- #
# C1, C2, C3 — células, interação, Shapley (um passo por período)
# ----------------------------------------------------------------------------------------- #
def combos_c123(alvo: str) -> dict:
    """Combinações lineares das médias das células para o grupo racial `alvo` (Negra/Indígena)."""
    h, m = ("HN", "MN") if alvo == "Negra" else ("HI", "MI")
    s = f"·{alvo}"
    return {
        f"C2 interação DiD{s}": {"HB": 1, h: -1, "MB": -1, m: 1},
        f"C2 hiato racial entre homens{s}": {"HB": 1, h: -1},
        f"C2 hiato racial entre mulheres{s}": {"MB": 1, m: -1},
        f"C2 hiato de gênero entre brancos{s}": {"HB": 1, "MB": -1},
        f"C2 hiato de gênero no grupo{s}": {h: 1, m: -1},
        f"C3 total HB − mulher{s}": {"HB": 1, m: -1},
        f"C3 Shapley raça{s}": {"HB": .5, h: -.5, "MB": .5, m: -.5},
        f"C3 Shapley gênero{s}": {"HB": .5, "MB": -.5, h: .5, m: -.5},
        f"C3 Shapley raça − gênero{s}": {"MB": 1, h: -1},  # φ_raça − φ_gênero = L_MB − L_HN
        f"C3 sequencial raça primeiro: raça{s}": {"HB": 1, h: -1},
        f"C3 sequencial raça primeiro: gênero{s}": {h: 1, m: -1},
        f"C3 sequencial gênero primeiro: gênero{s}": {"HB": 1, "MB": -1},
        f"C3 sequencial gênero primeiro: raça{s}": {"MB": 1, m: -1},
    }


def celulas_c123(y: np.ndarray, w: np.ndarray, raca, sexo, dom_base, upa, est, chaves: dict) -> list[dict]:
    doms = {SIGLA[(r, s)]: dom_base & (raca == r) & (sexo == s) for r, s in CELULAS}
    mz = medias_z(y, w, doms)
    linhas = []
    for (r, s), sig in SIGLA.items():
        n = int(doms[sig].sum())
        linhas.append({**chaves, "bloco": "C1", "metrica": f"média {sig}", "celula": sig, "escala": "R$",
                       "estimativa": mz[sig][0], "n": n})
    # C1: razão para HB em log, % da renda de HB e diferença em R$
    c1_log = {f"C1 log HB/{k}": {"HB": 1, k: -1} for k in SIGLA.values() if k != "HB"}
    c1_rs = {f"C1 R$ HB − {k}": {"HB": 1, k: -1} for k in SIGLA.values() if k != "HB"}
    partes = [combinacoes(mz, c1_log, upa, est).assign(escala="log-pontos"),
              combinacoes(mz, c1_rs, upa, est, log=False).assign(escala="R$")]
    for alvo in ("Negra", "Indígena"):
        cb = combos_c123(alvo)
        partes.append(combinacoes(mz, cb, upa, est).assign(escala="log-pontos"))
        partes.append(combinacoes(mz, cb, upa, est, log=False).assign(escala="R$"))
    # EP das médias (para a regra de supressão)
    for sig in SIGLA.values():
        z = mz[sig][1]
        v, _ = variancia.variancia_linearizada(z, upa, est)
        linhas[[ln["celula"] for ln in linhas].index(sig)]["ep"] = float(np.sqrt(max(v, 0.0)))
    df = pd.concat(partes, ignore_index=True)
    df["bloco"] = df["metrica"].str[:2]
    out = pd.DataFrame(linhas)
    out = pd.concat([out, df.assign(**chaves)], ignore_index=True)
    return out.to_dict("records")


def beta3_c2(m: pd.DataFrame, controles: bool) -> list[dict]:
    """ln renda ~ Negra + Indígena + Mulher + Negra×Mulher + Indígena×Mulher [+ idade, instrução, região],
    em P1 (Amarela fora)."""
    p1 = m["em_p1"].to_numpy(bool) & m["renda"].notna().to_numpy() & m["raca"].isin(RACAS_C).to_numpy()
    raca, mulher = m["raca"].to_numpy(object), (m["sexo"] == "Mulher").to_numpy(float)
    neg, ind = (raca == "Negra").astype(float), (raca == "Indígena").astype(float)
    cols = [np.ones(len(m)), neg, ind, mulher, neg * mulher, ind * mulher]
    nomes = ["const", "Negra", "Indígena", "Mulher", "Negra×Mulher", "Indígena×Mulher"]
    if controles:
        faixa = pd.cut(m["idade"], [17, 24, 29, 39, 49, 59, 200]).astype(str)
        D = pd.get_dummies(pd.DataFrame({"f": faixa, "i": m["instrucao"].astype(str), "r": m["regiao"].astype(str)}),
                           drop_first=True, dtype=float)
        cols += [D[c].to_numpy() for c in D.columns]
        nomes += list(D.columns)
    X = np.column_stack(cols)
    y = np.log(np.where(p1, m["renda"].to_numpy(float), np.nan))
    beta, ep, _ = wls_design(y, X, m["peso"].to_numpy(float), m["upa"].to_numpy(), m["estrato"].to_numpy(), p1)
    return [{"termo": n, "estimativa": float(b), "ep": float(e)} for n, b, e in zip(nomes, beta, ep) if n in nomes[1:6]]


def gerar_c123(con) -> pd.DataFrame:
    linhas, betas, theil = [], [], []
    for a, t in trimestres(con):
        m = micro_c(con, a, t)
        w, upa, est = m["peso"].to_numpy(float), m["upa"].to_numpy(), m["estrato"].to_numpy()
        raca, sexo = m["raca"].to_numpy(object), m["sexo"].to_numpy(object)
        y = m["renda"].to_numpy(float)
        p1 = m["em_p1"].to_numpy(bool) & np.isfinite(y)
        linhas += celulas_c123(np.nan_to_num(y), w, raca, sexo, p1, upa, est, {"ano": a, "trimestre": t, "conceito": "P1"})
        linhas += celulas_c123(np.nan_to_num(y), w, raca, sexo, np.ones(len(m), bool), upa, est,
                               {"ano": a, "trimestre": t, "conceito": "P4 (todos os adultos, fora de P1 = 0)"})
        for ctrl in (False, True):
            for b in beta3_c2(m, ctrl):
                betas.append({"ano": a, "trimestre": t, "especificacao": "com controles" if ctrl else "sem controles", **b})
        # Theil entre células raça × sexo (P1, inclui Amarela)
        mp = m[p1].assign(cel=lambda d: d["raca"] + " · " + d["sexo"])
        tt, _ = pnadc_core.decomposicao_theil_entre_dentro(mp, "renda", "cel", "peso")
        tl = theil_l_entre_dentro(mp["renda"], mp["peso"], mp["cel"])
        tr, _ = pnadc_core.decomposicao_theil_entre_dentro(mp, "renda", "raca", "peso")
        ts, _ = pnadc_core.decomposicao_theil_entre_dentro(mp, "renda", "sexo", "peso")
        theil.append({"ano": a, "trimestre": t, "theil_t_total": tt.get("theil_total"),
                      "theil_t_pct_entre_celulas": tt.get("pct_entre_grupos"),
                      "theil_t_pct_entre_racas": tr.get("pct_entre_grupos"), "theil_t_pct_entre_sexos": ts.get("pct_entre_grupos"),
                      "theil_l_pct_entre_celulas": tl["theil_l_pct_entre"]})
        print(f"C1–C3 {a}T{t}", flush=True)
    df = _ic(pd.DataFrame(linhas))
    nivel = df["metrica"].str.startswith("média")
    with np.errstate(invalid="ignore", divide="ignore"):
        df["cv"] = np.where(nivel, df["ep"] / df["estimativa"].abs(), np.nan)
    df["publicavel"] = np.where(nivel, precisao.publicavel(df["n"], df["cv"]), True)
    b = _ic(pd.DataFrame(betas))
    b["p_valor"] = 2 * stats.norm.sf(np.abs(b["estimativa"] / b["ep"]))
    b = multiplicidade.adicionar_fdr(b.assign(p_valor=np.where(b["termo"].str.contains("×"), b["p_valor"], np.nan)),
                                     ["ano", "trimestre", "especificacao"])
    salvar_tabela(df, OUTPUT_DIR / "c123_racaxsexo_celulas.parquet", se_metodo=variancia.SE_METODO,
                  nota="C1 (células e razão para HB), C2 (DiD) e C3 (Shapley e ordens sequenciais); log-pontos = ln das médias")
    salvar_tabela(b, OUTPUT_DIR / "c2_interacao_regressao.parquet", se_metodo="wls_influencia_linearizacao_estrato_upa",
                  familia_fdr=["ano", "trimestre", "especificacao"])
    salvar_tabela(pd.DataFrame(theil), OUTPUT_DIR / "c1_theil_celulas.parquet",
                  nota="Theil T e L (MLD) com 8 células raça × sexo (inclui Amarela); P1")
    return df


def gerar_c2_tendencia() -> pd.DataFrame:
    df = pd.read_parquet(OUTPUT_DIR / "c123_racaxsexo_celulas.parquet")
    linhas = []
    for (conc, met, esc), x in df[df["metrica"].str.startswith("C2 interação")].groupby(["conceito", "metrica", "escala"]):
        x = x.sort_values(["ano", "trimestre"])
        r = tendencia.tendencia_hac(tendencia.tempo_anos(x["ano"], x["trimestre"]), x["estimativa"])
        linhas.append({"conceito": conc, "metrica": met, "escala": esc, "valor_2012T1": x["estimativa"].iloc[0],
                       "valor_final": x["estimativa"].iloc[-1], **r})
    t = pd.DataFrame(linhas)
    salvar_tabela(t, OUTPUT_DIR / "c2_interacao_tendencia.parquet", se_metodo=tendencia.METODO)
    return t


# ----------------------------------------------------------------------------------------- #
# Renda domiciliar per capita (anual) por raça × sexo da pessoa — versão do Bloco T de C1–C3
# ----------------------------------------------------------------------------------------- #
def gerar_c123_anual(con) -> pd.DataFrame:
    linhas = []
    for visita, glob in ANUAL_GLOB.items():
        anos = [r[0] for r in con.execute(f"SELECT DISTINCT ano FROM read_parquet('{glob}', hive_partitioning=1) ORDER BY 1").fetchall()]
        for ano in anos:
            m = con.execute(f"""
                SELECT {RACA_SQL} AS raca, CASE m.V2007 WHEN '1' THEN 'Homem' WHEN '2' THEN 'Mulher' END AS sexo,
                       m.V1032 AS peso, m.UPA AS upa, m.Estrato AS estrato, m.VD5008 AS renda_pc
                FROM read_parquet('{glob}', hive_partitioning = 1, union_by_name = true) m
                WHERE m.ano = {ano} AND m.V2009 >= 18 AND m.V2005 NOT IN ('17','18','19') AND m.VD5008 IS NOT NULL
                  AND m.V2010 IN ('1','2','3','4','5')""").df()
            linhas += celulas_c123(m["renda_pc"].to_numpy(float), m["peso"].to_numpy(float), m["raca"].to_numpy(object),
                                   m["sexo"].to_numpy(object), np.ones(len(m), bool), m["upa"].to_numpy(), m["estrato"].to_numpy(),
                                   {"ano": int(ano), "visita": visita, "conceito": "T · renda domiciliar per capita (18+)"})
            print(f"C anual {ano}", flush=True)
    df = _ic(pd.DataFrame(linhas))
    salvar_tabela(df, OUTPUT_DIR / "c123_racaxsexo_domiciliar_anual.parquet", se_metodo=variancia.SE_METODO,
                  insumos="anual_v2", nota_renda="VD5008 nominal do ano; pessoas 18+ por raça × sexo da pessoa")
    return df


# ----------------------------------------------------------------------------------------- #
# C1 — quantis por célula (bootstrap)
# ----------------------------------------------------------------------------------------- #
def gerar_c1_quantis(con, n_boot: int = 200) -> pd.DataFrame:
    linhas = []
    for a, t in ((2012, 2), (2026, 2)):
        m = micro_c(con, a, t)
        m = m[m["em_p1"] & m["renda"].notna() & m["raca"].isin(RACAS_C)].reset_index(drop=True)
        cod, mult = multiplicadores_rao_wu(m["upa"].to_numpy(), m["estrato"].to_numpy(), n_boot, seed=11)
        y, w = m["renda"].to_numpy(float), m["peso"].to_numpy(float)
        qs = [0.10, 0.50, 0.90]
        est, rep = {}, {}
        for (r, s), sig in SIGLA.items():
            sel = np.flatnonzero((m["raca"] == r).to_numpy() & (m["sexo"] == s).to_numpy())
            o = sel[np.argsort(y[sel], kind="stable")]
            est[sig] = _quantis(y[o], w[o], qs)
            rep[sig] = _quantis(y[o], w[o][:, None] * mult[cod[o]], qs)
        for sig in SIGLA.values():
            for i, q in enumerate(qs):
                r_ = np.log(rep["HB"][i] / rep[sig][i])
                linhas.append({"ano": a, "trimestre": t, "celula": sig, "quantil": f"P{int(q * 100)}", "valor": est[sig][i],
                               "log_HB_sobre_celula": float(np.log(est["HB"][i] / est[sig][i])),
                               "ic_inferior": float(np.percentile(r_, 2.5)), "ic_superior": float(np.percentile(r_, 97.5))})
    df = pd.DataFrame(linhas)
    salvar_tabela(df, OUTPUT_DIR / "c1_quantis_celulas.parquet", se_metodo=f"bootstrap_rao_wu_estrato_upa_{n_boot}",
                  nota="Valores redondos (heaping) produzem IC de largura zero: não é precisão")
    return df


# ----------------------------------------------------------------------------------------- #
# C4 — penalidade da maternidade
# ----------------------------------------------------------------------------------------- #
def _x_c4(d: pd.DataFrame, flag: str) -> tuple[np.ndarray, list[str]]:
    D = pd.get_dummies(pd.DataFrame({"idade": d["idade"].astype(int).astype(str), "i": d["instrucao"].astype(str),
                                     "r": d["regiao"].astype(str)}), drop_first=True, dtype=float)
    X = np.column_stack([np.ones(len(d)), d[flag].fillna(False).to_numpy(float), D.to_numpy()])
    return X, ["const", flag, *D.columns]


def penalidades(m: pd.DataFrame, flag: str, universo: np.ndarray, rotulo: str) -> list[dict]:
    """Coeficiente de `flag` em três desfechos, por raça (Branca, Negra) e sexo; diferença Negra − Branca
    com covariância (mesma amostra, domínios disjuntos)."""
    w, upa, est = m["peso"].to_numpy(float), m["upa"].to_numpy(), m["estrato"].to_numpy()
    y = m["renda"].to_numpy(float)
    p1 = m["em_p1"].to_numpy(bool) & np.isfinite(y)
    desfechos = {"pr_p1_pp": 100 * p1.astype(float), "ln_renda_p1": np.where(p1, np.log(np.where(p1, y, 1.0)), np.nan),
                 "renda_por_pessoa_rs": np.where(p1, y, 0.0)}
    X, _ = _x_c4(m, flag)
    linhas = []
    for sexo in SEXOS:
        for nome, yy in desfechos.items():
            dom_base = universo & (m["sexo"] == sexo).to_numpy() & (p1 if nome == "ln_renda_p1" else True)
            res = {}
            for r in ("Branca", "Negra", "Indígena"):
                dom = dom_base & (m["raca"] == r).to_numpy()
                if dom.sum() < 200 or m.loc[dom, flag].sum() < 30:
                    continue
                beta, ep, psi = wls_design(yy, X, w, upa, est, dom, apenas=[1])
                sem = dom & ~m[flag].fillna(False).to_numpy(bool)
                zb, base = variancia.influencia_media(np.where(sem, yy, 0.0), w, sem)
                res[r] = (beta[1], ep[1], psi[:, 1])
                linha = {"definicao": rotulo, "sexo": sexo, "desfecho": nome, "raca": r, "penalidade": float(beta[1]),
                         "ep": float(ep[1]), "media_sem_filho": float(base), "n": int(dom.sum()),
                         "n_com_filho": int(m.loc[dom, flag].sum())}
                if nome != "ln_renda_p1":
                    # penalidade relativa à média de quem não tem filho pequeno (delta: ψ_β/base − β·z_base/base²)
                    zr = psi[:, 1] / base - beta[1] * zb / base**2
                    v, _ = variancia.variancia_linearizada(zr, upa, est)
                    linha["penalidade_pct_da_media"] = float(100 * beta[1] / base)
                    linha["ep_pct"] = float(100 * np.sqrt(max(v, 0.0)))
                linhas.append(linha)
            if "Negra" in res and "Branca" in res:
                v, _ = variancia.variancia_linearizada(res["Negra"][2] - res["Branca"][2], upa, est)
                d, e = res["Negra"][0] - res["Branca"][0], float(np.sqrt(max(v, 0.0)))
                linhas.append({"definicao": rotulo, "sexo": sexo, "desfecho": nome, "raca": "Negra − Branca",
                               "penalidade": float(d), "ep": e, "emd_80pct": 2.8 * e})
    return linhas


def gerar_c4(con) -> pd.DataFrame:
    linhas = []
    for nome, tris in JANELAS.items():
        m = pd.concat([micro_c(con, a, t) for a, t in tris], ignore_index=True)
        # universo da linearização = pessoas de 25–44 da janela (UPAs sem ninguém nessa idade não entram)
        m = m[(m["idade"] >= 25) & (m["idade"] <= 44) & m["raca"].isin(RACAS_C)].reset_index(drop=True)
        idade = m["idade"].to_numpy()
        for lo, hi, faixa in ((25, 44, "25–44"), (25, 34, "25–34"), (35, 44, "35–44")):
            u = (idade >= lo) & (idade <= hi)
            for ln in penalidades(m, "filho_0a5", u & m["resp_ou_conj"].to_numpy(bool),
                                  "principal: mãe/pai de criança 0–5 (responsável ou cônjuge)"):
                linhas.append({"janela": nome, "faixa_etaria": faixa, **ln})
            if faixa == "25–44":
                for ln in penalidades(m, "crianca_0a5_dom", u, "sensibilidade: há criança 0–5 no domicílio (todas as pessoas)"):
                    linhas.append({"janela": nome, "faixa_etaria": faixa, **ln})
        print(f"C4 {nome}", flush=True)
    df = _ic(pd.DataFrame(linhas).rename(columns={"penalidade": "estimativa"}))

    df["p_valor"] = 2 * stats.norm.sf(np.abs(df["estimativa"] / df["ep"]))
    df = multiplicidade.adicionar_fdr(df, ["janela", "faixa_etaria", "definicao", "sexo"])
    salvar_tabela(df, OUTPUT_DIR / "c4_penalidade_maternidade.parquet", se_metodo="wls_influencia_linearizacao_estrato_upa",
                  familia_fdr=["janela", "faixa_etaria", "definicao", "sexo"],
                  nota="Coeficiente de ter filho(a) 0–5 controlando idade (anos simples), instrução e região; "
                       "pr_p1_pp em p.p., ln_renda_p1 em log-pontos, renda_por_pessoa_rs em R$ (fora de P1 = 0)")
    return df


# ----------------------------------------------------------------------------------------- #
# C5 — trabalho doméstico remunerado
# ----------------------------------------------------------------------------------------- #
def c5_trimestre(m: pd.DataFrame, a: int, t: int) -> list[dict]:
    w, upa, est = m["peso"].to_numpy(float), m["upa"].to_numpy(), m["estrato"].to_numpy()
    mulher = (m["sexo"] == "Mulher").to_numpy()
    y = m["renda"].to_numpy(float)
    p1 = m["em_p1"].to_numpy(bool) & np.isfinite(y)
    dom = m["posicao"].isin(["03", "04"]).to_numpy() & m["ocupado"].fillna(False).to_numpy(bool)
    cart = (m["posicao"] == "03").to_numpy()
    raca = m["raca"].to_numpy(object)
    theta, Z, nomes, linhas, ns = [], [], [], [], []

    def add(nome, yy, d):
        z, mu = variancia.influencia_media(np.where(d, yy, 0.0), w, d)
        theta.append(mu)
        Z.append(z)
        nomes.append(nome)
        ns.append(int(d.sum()))
    for r in ("Branca", "Negra", "Indígena"):
        g = mulher & (raca == r)
        add(f"pct_domesticas_entre_ocupadas_p1|{r}", 100 * dom.astype(float), g & p1)
        add(f"pct_domesticas_entre_todas_18mais|{r}", 100 * dom.astype(float), g)
        add(f"pct_carteira_entre_domesticas|{r}", 100 * cart.astype(float), g & p1 & dom)
        add(f"renda_media_domesticas|{r}", np.nan_to_num(y), g & p1 & dom)
        add(f"renda_media_outras|{r}", np.nan_to_num(y), g & p1 & ~dom)
        add(f"renda_media_todas_p1|{r}", np.nan_to_num(y), g & p1)
    theta = np.array(theta)
    Z = np.column_stack(Z)
    ix = {n: i for i, n in enumerate(nomes)}
    for n, v, nn in zip(nomes, theta, ns):
        k, r = n.split("|")
        linhas.append({"ano": a, "trimestre": t, "indicador": k, "raca": r, "estimativa": float(v), "n": nn})
    # EP dos níveis
    cov, _ = variancia.variancia_linearizada(Z, upa, est)
    for i, ln in enumerate(linhas):
        ln["ep"] = float(np.sqrt(max(cov[i, i], 0.0)))
    # Kitagawa (Branca − Negra, mulheres em P1) e razão Negra/Branca de % domésticas
    def comp(th, B="Branca", N="Negra"):
        sB, sN = th[ix[f"pct_domesticas_entre_ocupadas_p1|{B}"]] / 100, th[ix[f"pct_domesticas_entre_ocupadas_p1|{N}"]] / 100
        mBd, mBo = th[ix[f"renda_media_domesticas|{B}"]], th[ix[f"renda_media_outras|{B}"]]
        mNd, mNo = th[ix[f"renda_media_domesticas|{N}"]], th[ix[f"renda_media_outras|{N}"]]
        composicao = (sB - sN) * (mBd + mNd) / 2 + ((1 - sB) - (1 - sN)) * (mBo + mNo) / 2
        dentro = (mBd - mNd) * (sB + sN) / 2 + (mBo - mNo) * ((1 - sB) + (1 - sN)) / 2
        return composicao, dentro, sB, sN, mBd, mBo, mNd, mNo
    f = {
        "kitagawa_diferenca_total_rs": lambda th: sum(comp(th)[:2]),
        "kitagawa_composicao_rs": lambda th: comp(th)[0],
        "kitagawa_dentro_rs": lambda th: comp(th)[1],
        "kitagawa_pct_composicao": lambda th: 100 * comp(th)[0] / sum(comp(th)[:2]),
        "contrafactual_renda_negra_com_pct_domesticas_branca": lambda th: (
            comp(th)[2] * comp(th)[6] + (1 - comp(th)[2]) * comp(th)[7]),
        "razao_pct_domesticas_negra_sobre_branca": lambda th: th[ix["pct_domesticas_entre_ocupadas_p1|Negra"]]
        / th[ix["pct_domesticas_entre_ocupadas_p1|Branca"]],
        "hiato_pct_dentro_domesticas": lambda th: 100 * (th[ix["renda_media_domesticas|Branca"]]
                                                         / th[ix["renda_media_domesticas|Negra"]] - 1),
    }
    dk = delta_generico(f, theta, Z, upa, est)
    for _, r in dk.iterrows():
        linhas.append({"ano": a, "trimestre": t, "indicador": r["metrica"], "raca": "Branca − Negra (mulheres)",
                       "estimativa": r["estimativa"], "ep": r["ep"]})
    return linhas


def gerar_c5(con) -> pd.DataFrame:
    linhas = []
    for a, t in trimestres(con):
        linhas += c5_trimestre(micro_c(con, a, t), a, t)
        print(f"C5 {a}T{t}", flush=True)
    df = _ic(pd.DataFrame(linhas))
    nivel = df["n"].notna()
    with np.errstate(invalid="ignore", divide="ignore"):
        df["cv"] = np.where(nivel, df["ep"] / df["estimativa"].abs(), np.nan)
    df["publicavel"] = np.where(nivel, precisao.publicavel(df["n"], df["cv"]), True)
    salvar_tabela(df, OUTPUT_DIR / "c5_trabalho_domestico.parquet", se_metodo=variancia.SE_METODO,
                  regra_supressao=precisao.REGRA_SUPRESSAO,
                  nota="Mulheres 18+; doméstico = VD4009 03/04; Kitagawa com duas posições (doméstica × outras)")
    tend = []
    for (ind, r), x in df[df["indicador"].isin(["pct_domesticas_entre_ocupadas_p1", "pct_domesticas_entre_todas_18mais",
                                                "kitagawa_composicao_rs", "kitagawa_pct_composicao"])].groupby(["indicador", "raca"]):
        x = x.sort_values(["ano", "trimestre"])
        tend.append({"indicador": ind, "raca": r, "valor_inicial": x["estimativa"].iloc[0], "valor_final": x["estimativa"].iloc[-1],
                     **tendencia.tendencia_hac(tendencia.tempo_anos(x["ano"], x["trimestre"]), x["estimativa"])})
    salvar_tabela(pd.DataFrame(tend), OUTPUT_DIR / "c5_tendencia.parquet", se_metodo=tendencia.METODO)
    return df


# ----------------------------------------------------------------------------------------- #
# C6 — estado conjugal e chefia
# ----------------------------------------------------------------------------------------- #
def _dummies_basicas(d: pd.DataFrame) -> np.ndarray:
    D = pd.get_dummies(pd.DataFrame({"idade": d["idade"].astype(int).astype(str), "i": d["instrucao"].astype(str),
                                     "r": d["regiao"].astype(str)}), drop_first=True, dtype=float)
    return D.to_numpy()


def associacoes_c6(m: pd.DataFrame) -> list[dict]:
    """Coeficientes de chefe e em_casal (com filho 0–5 e controles básicos) em Pr(P1), ln renda e horas, por raça × sexo,
    e a diferença Negra − Branca (mesma amostra, ψ combinados)."""
    w, upa, est = m["peso"].to_numpy(float), m["upa"].to_numpy(), m["estrato"].to_numpy()
    y = m["renda"].to_numpy(float)
    p1 = m["em_p1"].to_numpy(bool) & np.isfinite(y)
    flags = np.column_stack([m[c].fillna(False).to_numpy(float) for c in ("chefe", "em_casal", "filho_0a5")])
    X = np.column_stack([np.ones(len(m)), flags, _dummies_basicas(m)])
    desfechos = {"pr_p1_pp": (100 * p1.astype(float), None),
                 "ln_renda_p1": (np.log(np.where(p1, y, 1.0)), p1),
                 "horas_p1": (m["horas"].to_numpy(float), p1)}
    linhas = []
    for sexo in SEXOS:
        for nome, (yy, restr) in desfechos.items():
            res = {}
            for r in ("Branca", "Negra"):
                dom = (m["sexo"] == sexo).to_numpy() & (m["raca"] == r).to_numpy()
                if restr is not None:
                    dom &= restr
                beta, ep, psi = wls_design(yy, X, w, upa, est, dom, apenas=[1, 2])
                res[r] = (beta, psi)
                for j, cond in ((1, "chefe"), (2, "em_casal")):
                    linhas.append({"sexo": sexo, "desfecho": nome, "condicao": cond, "raca": r,
                                   "estimativa": float(beta[j]), "ep": float(ep[j]), "n": int(dom.sum()),
                                   "n_condicao": int((dom & (flags[:, j - 1] > 0)).sum())})
            for j, cond in ((1, "chefe"), (2, "em_casal")):
                v, _ = variancia.variancia_linearizada(res["Negra"][1][:, j] - res["Branca"][1][:, j], upa, est)
                e = float(np.sqrt(max(v, 0.0)))
                linhas.append({"sexo": sexo, "desfecho": nome, "condicao": cond, "raca": "Negra − Branca",
                               "estimativa": float(res["Negra"][0][j] - res["Branca"][0][j]), "ep": e, "emd_80pct": 2.8 * e})
    return linhas


def hiato_condicional_c6(m: pd.DataFrame) -> list[dict]:
    """Coeficiente de Negra em ln renda (P1) por sexo: controles básicos × + chefia, casal e filho 0–5."""
    w, upa, est = m["peso"].to_numpy(float), m["upa"].to_numpy(), m["estrato"].to_numpy()
    y = m["renda"].to_numpy(float)
    p1 = m["em_p1"].to_numpy(bool) & np.isfinite(y)
    neg = (m["raca"] == "Negra").to_numpy(float)
    basicas = _dummies_basicas(m)
    flags = np.column_stack([m[c].fillna(False).to_numpy(float) for c in ("chefe", "em_casal", "filho_0a5")])
    ly = np.log(np.where(p1, y, 1.0))
    linhas = []
    for sexo in SEXOS:
        dom = p1 & (m["sexo"] == sexo).to_numpy()
        b0, e0, s0 = wls_design(ly, np.column_stack([np.ones(len(m)), neg, basicas]), w, upa, est, dom, apenas=[1])
        b1, e1, s1 = wls_design(ly, np.column_stack([np.ones(len(m)), neg, flags, basicas]), w, upa, est, dom, apenas=[1])
        v, _ = variancia.variancia_linearizada(s1[:, 1] - s0[:, 1], upa, est)
        for esp, b, e in (("controles básicos", b0[1], e0[1]), ("+ chefia, casal, filho 0–5", b1[1], e1[1]),
                          ("mudança", b1[1] - b0[1], float(np.sqrt(max(v, 0.0))))):
            linhas.append({"sexo": sexo, "especificacao": esp, "coef_negra_ln_renda": float(b), "ep": float(e),
                           "pct_do_basico": float(100 * (b1[1] - b0[1]) / b0[1]) if esp == "mudança" else np.nan})
    return linhas


def gerar_c6(con) -> tuple[pd.DataFrame, pd.DataFrame]:
    a_, h_ = [], []
    for nome, tris in JANELAS.items():
        m = pd.concat([micro_c(con, a, t) for a, t in tris], ignore_index=True)
        m = m[(m["idade"] >= 25) & (m["idade"] <= 59) & m["raca"].isin(["Branca", "Negra"])].reset_index(drop=True)
        a_ += [{"janela": nome, **x} for x in associacoes_c6(m)]
        h_ += [{"janela": nome, **x} for x in hiato_condicional_c6(m)]
        print(f"C6 {nome}", flush=True)
    a = _ic(pd.DataFrame(a_))
    a["p_valor"] = 2 * stats.norm.sf(np.abs(a["estimativa"] / a["ep"]))
    a = multiplicidade.adicionar_fdr(a, ["janela", "sexo"])
    h = _ic(pd.DataFrame(h_).rename(columns={"coef_negra_ln_renda": "estimativa"}))
    meta = dict(se_metodo="wls_influencia_linearizacao_estrato_upa",
                nota="Pessoas 25–59 (Branca, Negra); controles: idade (anos simples), instrução, região; "
                     "associação, não efeito (endogeneidade)")
    salvar_tabela(a, OUTPUT_DIR / "c6_conjugal_chefia.parquet", familia_fdr=["janela", "sexo"], **meta)
    salvar_tabela(h, OUTPUT_DIR / "c6_hiato_condicional.parquet", **meta)
    return a, h


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--so", nargs="*", default=None, help="c123 anual quantis c4 c5 c6")
    fazer = set(parser.parse_args().so or ["c123", "anual", "quantis", "c4", "c5", "c6"])
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    if "c123" in fazer:
        gerar_c123(con)
        gerar_c2_tendencia()
    if "anual" in fazer:
        gerar_c123_anual(con)
    if "quantis" in fazer:
        gerar_c1_quantis(con)
    if "c4" in fazer:
        gerar_c4(con)
    if "c6" in fazer:
        gerar_c6(con)
    if "c5" in fazer:
        gerar_c5(con)


if __name__ == "__main__":
    main()
