"""Onda 5 — Bloco G: políticas e causalidade (`docs/PLANO_DE_ANALISE.md`, Bloco G; fichas `docs/studies/G1`…`G6`).

- **G6** — efeito mínimo detectável (EMD) de cada desenho, calculado ANTES de estimar: o estimador de cada desenho é
  linear no desfecho (θ̂ = a'y), então Var(θ̂) = Σ_i a_i' Σ_i a_i com Σ_i AR(1) por unidade; σ_i e ρ vêm dos resíduos
  de um modelo só com efeitos fixos (G1: só 2009–2012, antes da lei; G4: sem o regressor de exposição). EMD =
  (z₀,₉₇₅ + z₀,₈₀)·DP, o pior caso numa grade de ρ; conferido por simulação.
- **G1** — Lei 12.711: event study instituição × ano (Censo da Educação Superior 2009–2023), federais sem reserva
  étnica antes de 2013 × estaduais/municipais sem reserva antes de 2013; EP agrupado por instituição (CR1) e bootstrap
  por instituição; versão escalonada (Callaway–Sant'Anna) como sensibilidade.
- **G4** — salário mínimo × hiato por exposição regional (`C`): painel UF × trimestre da PNADC, efeitos fixos de UF e
  trimestre, *wild cluster bootstrap* (Webb) por UF.

Só roda o que tiver poder (regra das fichas G1, G4 e G6).

Uso:
    python -m src.processing.bloco_g [--so g6 g1 g4]
"""
from __future__ import annotations

import argparse

import duckdb
import numpy as np
import pandas as pd
from scipy import stats

from src.inference import multiplicidade
from src.inference.saida import salvar_tabela
from src.ingestion.censo_superior_painel import SAIDA as PAINEL_SUPERIOR
from src.processing.agregacoes_pnadc import DEFLATOR_PATH, OUTPUT_DIR, PARQUET_GLOB, SALARIO_MINIMO_NOMINAL
from src.utils import populacao as pop

Z_EMD = stats.norm.ppf(0.975) + stats.norm.ppf(0.80)  # ≈ 2,80
Z95_ = 1.959963984540054
GRADE_RHO = (0.0, 0.5, 0.8)
SEMENTE = 20261020

# ---- G1 ------------------------------------------------------------------------------------------------- #
ANOS = list(range(2009, 2024))
BASE = 2012
PRE_LEI = [2009, 2010, 2011, 2012]
LIMIAR_RESERVA = 0.05
MIN_ING = 30
JANELAS_G1 = {"2013–2015": [2013, 2014, 2015], "2016–2019": [2016, 2017, 2018, 2019], "2020–2023": [2020, 2021, 2022, 2023]}
JANELA_PRINCIPAL = "2016–2019"
DESFECHOS_G1 = {"Y1": "% negra entre declarados", "Y1b": "% negra, não declarados como negros (conservador)",
                "Y1c": "% negra, não declarados como não negros (limite)", "Y2": "% de escola pública",
                "Y3": "% sem cor/raça declarada"}
N_BOOT = 999
EMD_G1_ROTINA, EMD_G1_LIMITE = 2.0, 10.0  # p.p. (fichas G1 e G6)

# ---- G4 ------------------------------------------------------------------------------------------------- #
SM_2023T1 = 1302  # R$ 1.302 em jan–abr/2023; R$ 1.320 a partir de maio (2023T2 em diante) — ficha G4
MIN_N_UF = 100
EMD_G4_LIMITE = 1.0
N_WILD = 9999


# ========================================================================================================= #
# álgebra comum
# ========================================================================================================= #
def wls_cluster(X: np.ndarray, y: np.ndarray, w: np.ndarray, cl: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """MQO ponderado com variância agrupada CR1 (fator G/(G−1)). `cl` = códigos 0..G−1."""
    sw = np.sqrt(w)
    xtwx = (X * w[:, None]).T @ X
    bread = np.linalg.pinv(xtwx)
    b = bread @ ((X * w[:, None]).T @ y)
    u = y - X @ b
    g = int(cl.max()) + 1
    s = np.zeros((g, X.shape[1]))
    np.add.at(s, cl, X * (w * u)[:, None])
    v = bread @ (s.T @ s) @ bread * g / (g - 1)
    del sw
    return b, v


def var_ar1(a: np.ndarray, unidade: np.ndarray, tempo: np.ndarray, sigma2: np.ndarray, rho: float) -> float:
    """Var(a'y) com y_it AR(1) estacionário por unidade (variância sigma2[unidade]), independente entre unidades."""
    total = 0.0
    for u in np.unique(unidade):
        m = unidade == u
        t = tempo[m].astype(float)
        r = rho ** np.abs(t[:, None] - t[None, :])
        total += sigma2[u] * a[m] @ r @ a[m]
    return float(total)


def simular_ar1(a: np.ndarray, unidade: np.ndarray, tempo: np.ndarray, sigma2: np.ndarray, rho: float,
                n_sim: int = 2000, semente: int = SEMENTE) -> float:
    """DP de a'y em `n_sim` simulações AR(1) estacionárias (conferência da fórmula)."""
    rng = np.random.default_rng(semente)
    tmin, tmax = int(tempo.min()), int(tempo.max())
    nt = tmax - tmin + 1
    nu = int(unidade.max()) + 1
    e = np.empty((n_sim, nu, nt))
    e[:, :, 0] = rng.standard_normal((n_sim, nu))
    for k in range(1, nt):
        e[:, :, k] = rho * e[:, :, k - 1] + np.sqrt(1 - rho ** 2) * rng.standard_normal((n_sim, nu))
    y = e[:, unidade, tempo - tmin] * np.sqrt(sigma2[unidade])[None, :]
    return float((y @ a).std(ddof=1))


def residuos_ef(y: np.ndarray, w: np.ndarray, unidade: np.ndarray, tempo: np.ndarray) -> np.ndarray:
    """Resíduos de y ~ efeito fixo de unidade + efeito fixo de tempo (MQO ponderado)."""
    d = _dummies_ef(unidade, tempo)
    b = np.linalg.pinv((d * w[:, None]).T @ d) @ ((d * w[:, None]).T @ y)
    return y - d @ b


def _dummies_ef(unidade: np.ndarray, tempo: np.ndarray) -> np.ndarray:
    nu = int(unidade.max()) + 1
    tt, ti = np.unique(tempo, return_inverse=True)
    du = np.zeros((len(unidade), nu))
    du[np.arange(len(unidade)), unidade] = 1
    dt = np.zeros((len(unidade), len(tt) - 1))
    m = ti > 0
    dt[np.where(m)[0], ti[m] - 1] = 1
    return np.hstack([du, dt])


def sigma_rho(r: np.ndarray, unidade: np.ndarray, tempo: np.ndarray, w_unid: np.ndarray, encolher: float = 0.5
              ) -> tuple[np.ndarray, float]:
    """σ²_i (encolhida `encolher` para a média ponderada) e ρ AR(1) agrupado dos resíduos."""
    nu = int(unidade.max()) + 1
    n = np.bincount(unidade, minlength=nu)
    s2 = np.bincount(unidade, weights=r ** 2, minlength=nu) / np.maximum(n - 1, 1)
    media = np.average(s2, weights=w_unid)
    sigma2 = (1 - encolher) * s2 + encolher * media
    df = pd.DataFrame({"u": unidade, "t": tempo, "r": r}).sort_values(["u", "t"])
    df["r_lag"] = df.groupby("u")["r"].shift()
    df["t_lag"] = df.groupby("u")["t"].shift()
    ok = df["t"] - df["t_lag"] == 1
    rho = float(np.corrcoef(df.loc[ok, "r"], df.loc[ok, "r_lag"])[0, 1])
    return sigma2, rho


# ========================================================================================================= #
# G1 — dados
# ========================================================================================================= #
def painel_g1(limiar: float = LIMIAR_RESERVA, balanceado: bool = True) -> pd.DataFrame:
    """Instituição × ano: desfechos Y1–Y3, grupo (tratada/controle/prévias), coorte de reserva étnica e peso."""
    d = pd.read_parquet(PAINEL_SUPERIOR)
    d = d[(d["TP_NIVEL_ACADEMICO"] == 1) & (d["TP_MODALIDADE_ENSINO"] == 1)
          & d["TP_CATEGORIA_ADMINISTRATIVA"].isin([1, 2, 3])]
    soma = [c for c in d.columns if c.startswith("QT_")]
    g = d.groupby(["CO_IES", "NU_ANO_CENSO"])[soma].sum().reset_index().rename(columns={"NU_ANO_CENSO": "ano"})
    cat = (d.groupby("CO_IES")["TP_CATEGORIA_ADMINISTRATIVA"].agg(lambda s: int(s.mode().iloc[0]))
           .rename("categoria"))
    g = g.merge(cat, left_on="CO_IES", right_index=True)
    g["ano"] = g["ano"].astype(int)
    g["s_etnica"] = g["QT_ING_RVETNICO"] / g["QT_ING"].where(g["QT_ING"] > 0)
    adota = g[g["s_etnica"] >= limiar].groupby("CO_IES")["ano"].min()
    g["coorte"] = g["CO_IES"].map(adota).fillna(0).astype(int)
    previa = (g["coorte"] > 0) & (g["coorte"] <= BASE)
    g["grupo"] = np.select([(g["categoria"] == 1) & ~previa, (g["categoria"] > 1) & ~previa, g["categoria"] == 1],
                           ["tratada", "controle", "federal com reserva prévia"], "estadual/municipal com reserva prévia")
    if balanceado:
        ok = g[g["QT_ING"] >= MIN_ING].groupby("CO_IES")["ano"].nunique()
        g = g[g["CO_IES"].isin(ok[ok == len(ANOS)].index)]
    decl = g[["QT_ING_BRANCA", "QT_ING_PRETA", "QT_ING_PARDA", "QT_ING_AMARELA", "QT_ING_INDIGENA"]].sum(axis=1)
    tot = decl + g["QT_ING_CORND"]
    neg = g["QT_ING_PRETA"] + g["QT_ING_PARDA"]
    g["n_declarados"] = decl
    g["Y1"] = np.where(decl >= MIN_ING, 100 * neg / decl.where(decl > 0), np.nan)
    g["Y1b"] = np.where(tot >= MIN_ING, 100 * (neg + g["QT_ING_CORND"]) / tot.where(tot > 0), np.nan)
    g["Y1c"] = np.where(tot >= MIN_ING, 100 * neg / tot.where(tot > 0), np.nan)
    proc = g["QT_ING_PROCESCPUBLICA"] + g["QT_ING_PROCESCPRIVADA"]
    g["Y2"] = np.where(proc >= MIN_ING, 100 * g["QT_ING_PROCESCPUBLICA"] / proc.where(proc > 0), np.nan)
    g["Y3"] = np.where(tot >= MIN_ING, 100 * g["QT_ING_CORND"] / tot.where(tot > 0), np.nan)
    peso = g[g["ano"] == BASE].set_index("CO_IES")["QT_ING"]
    g["peso"] = g["CO_IES"].map(peso).astype(float)
    return g.reset_index(drop=True)


# ========================================================================================================= #
# G1 — event study
# ========================================================================================================= #
def _desenho_es(df: pd.DataFrame) -> tuple[np.ndarray, list[int], np.ndarray]:
    """X = [EF de unidade | EF de ano (sem a base) | tratada × ano (sem a base)]; devolve X, anos dos δ e unidade."""
    unid = pd.factorize(df["_u"])[0]
    anos = sorted(df["ano"].unique())
    anos_d = [a for a in anos if a != BASE]
    n = len(df)
    du = np.zeros((n, unid.max() + 1))
    du[np.arange(n), unid] = 1
    ano = df["ano"].to_numpy()
    dt = np.column_stack([(ano == a).astype(float) for a in anos_d])
    trat = df["tratada"].to_numpy(float)
    de = dt * trat[:, None]
    return np.hstack([du, dt, de]), anos_d, unid


def event_study(df: pd.DataFrame, y: str, pesos: bool = True) -> dict:
    """δ_k por ano (base 2012) com V CR1 por instituição. `df` com colunas _u, ano, tratada, peso, y."""
    x = df.dropna(subset=[y])
    X, anos_d, unid = _desenho_es(x)
    w = x["peso"].to_numpy(float) if pesos else np.ones(len(x))
    b, v = wls_cluster(X, x[y].to_numpy(float), w, unid)
    k = len(anos_d)
    return {"anos": anos_d, "delta": b[-k:], "V": v[-k:, -k:], "n": len(x), "n_unid": int(unid.max()) + 1}


def contraste(res: dict, anos: list[int]) -> tuple[float, float]:
    c = np.array([1.0 / len(anos) if a in anos else 0.0 for a in res["anos"]])
    return float(c @ res["delta"]), float(np.sqrt(c @ res["V"] @ c))


def wald_pre(res: dict, anos: list[int]) -> float:
    idx = [res["anos"].index(a) for a in anos if a in res["anos"]]
    d = res["delta"][idx]
    v = res["V"][np.ix_(idx, idx)]
    return float(stats.chi2.sf(d @ np.linalg.pinv(v) @ d, len(idx)))


def bootstrap_es(df: pd.DataFrame, y: str, janelas: dict, pesos: bool = True, n_boot: int = N_BOOT,
                 semente: int = SEMENTE) -> dict[str, np.ndarray]:
    """Bootstrap por instituição, estratificado por tratada/controle: distribuição de cada contraste."""
    rng = np.random.default_rng(semente)
    blocos = {u: g for u, g in df.groupby("CO_IES")}
    estratos = [df.loc[df["tratada"] == t, "CO_IES"].unique() for t in (1, 0)]
    saida = {j: np.empty(n_boot) for j in janelas}
    for r in range(n_boot):
        partes = []
        for est in estratos:
            for i, u in enumerate(rng.choice(est, size=len(est), replace=True)):
                partes.append(blocos[u].assign(_u=f"{u}#{len(partes)}"))
        res = event_study(pd.concat(partes, ignore_index=True), y, pesos)
        for j, anos in janelas.items():
            saida[j][r] = contraste(res, anos)[0]
    return saida


def amostra_principal(g: pd.DataFrame) -> pd.DataFrame:
    x = g[g["grupo"].isin(["tratada", "controle"])].copy()
    x["tratada"] = (x["grupo"] == "tratada").astype(int)
    x["_u"] = x["CO_IES"]
    return x


# ========================================================================================================= #
# G1 — Callaway–Sant'Anna (sensibilidade escalonada)
# ========================================================================================================= #
def cs_att(df: pd.DataFrame, y: str, controle: str = "nunca", pesos: bool = True) -> pd.DataFrame:
    """ATT(g,t) com base universal g−1 e controles 'nunca' (coorte 0) ou 'ainda_nao' (coorte > max(t, g−1)).
    Unidades com coorte = primeiro ano (sem período anterior) saem."""
    p = df.pivot(index="CO_IES", columns="ano", values=y)
    coorte = df.groupby("CO_IES")["coorte"].first().reindex(p.index).to_numpy()
    w = (df.groupby("CO_IES")["peso"].first().reindex(p.index).to_numpy(float) if pesos else np.ones(len(p)))
    anos = list(p.columns)
    yv = p.to_numpy(float)
    linhas = []
    for gc in sorted(c for c in np.unique(coorte) if c > anos[0]):
        tr = coorte == gc
        b = anos.index(gc - 1)
        for t in anos:
            if t == gc - 1:
                continue
            k = anos.index(t)
            ctl = (coorte == 0) if controle == "nunca" else ((coorte == 0) | (coorte > max(t, gc - 1)))
            ctl &= ~tr
            dy = yv[:, k] - yv[:, b]
            mt, mc = tr & ~np.isnan(dy), ctl & ~np.isnan(dy)
            if mt.sum() == 0 or mc.sum() == 0:
                continue
            att = np.average(dy[mt], weights=w[mt]) - np.average(dy[mc], weights=w[mc])
            linhas.append({"coorte": gc, "ano": t, "e": t - gc, "att": att, "peso_coorte": w[mt].sum()})
    return pd.DataFrame(linhas)


def cs_agregado(att: pd.DataFrame) -> dict[str, float]:
    """Média ponderada pelo tamanho da coorte: por tempo de evento e no pós (t ≥ g, até 2019)."""
    out = {}
    for e, x in att.groupby("e"):
        out[f"e={e}"] = float(np.average(x["att"], weights=x["peso_coorte"]))
    pos = att[(att["e"] >= 0) & (att["ano"] <= 2019)]
    out["pós (t ≥ g, até 2019)"] = float(np.average(pos["att"], weights=pos["peso_coorte"])) if len(pos) else np.nan
    return out


def cs_bootstrap(df: pd.DataFrame, y: str, controle: str, n_boot: int = N_BOOT, semente: int = SEMENTE
                 ) -> tuple[dict, dict]:
    est = cs_agregado(cs_att(df, y, controle))
    rng = np.random.default_rng(semente)
    ies = df["CO_IES"].unique()
    blocos = {u: g for u, g in df.groupby("CO_IES")}
    dist = {k: [] for k in est}
    for _ in range(n_boot):
        partes = [blocos[u].assign(CO_IES=f"{u}#{i}") for i, u in enumerate(rng.choice(ies, len(ies), replace=True))]
        ag = cs_agregado(cs_att(pd.concat(partes, ignore_index=True), y, controle))
        for k in est:
            dist[k].append(ag.get(k, np.nan))
    return est, {k: np.array(v) for k, v in dist.items()}


# ========================================================================================================= #
# G6 — EMD do G1
# ========================================================================================================= #
def emd_g1(g: pd.DataFrame, y: str = "Y1") -> list[dict]:
    """EMD do contraste 2016–2019 com σ_i e ρ só de 2009–2012; desenho = painel completo (sem faltantes)."""
    x = amostra_principal(g).sort_values(["CO_IES", "ano"]).reset_index(drop=True)
    X, anos_d, unid = _desenho_es(x)
    w = x["peso"].to_numpy(float)
    c = np.zeros(X.shape[1])
    for a in JANELAS_G1[JANELA_PRINCIPAL]:
        c[X.shape[1] - len(anos_d) + anos_d.index(a)] = 1 / len(JANELAS_G1[JANELA_PRINCIPAL])
    a_vec = (X * w[:, None]) @ (np.linalg.pinv((X * w[:, None]).T @ X) @ c)
    pre = x[x["ano"].isin(PRE_LEI)].dropna(subset=[y])
    up = pd.factorize(pre["CO_IES"])[0]
    r = residuos_ef(pre[y].to_numpy(float), pre["peso"].to_numpy(float), up, pre["ano"].to_numpy())
    w_u = pre.groupby(up)["peso"].first().to_numpy(float)
    s2_pre, rho_hat = sigma_rho(r, up, pre["ano"].to_numpy(), w_u)
    mapa = dict(zip(pd.factorize(pre["CO_IES"])[1], s2_pre))
    media = float(np.average(s2_pre, weights=w_u))
    sigma2 = np.array([mapa.get(u, media) for u in pd.factorize(x["CO_IES"])[1]])
    linhas = []
    for rho in sorted({*GRADE_RHO, round(max(rho_hat, 0.0), 3)}):
        dp = np.sqrt(var_ar1(a_vec, unid, x["ano"].to_numpy(), sigma2, rho))
        dp_sim = simular_ar1(a_vec, unid, x["ano"].to_numpy(), sigma2, rho)
        linhas.append({"desenho": "G1", "desfecho": y, "parametro": f"média δ {JANELA_PRINCIPAL} (p.p.)", "rho": rho,
                       "rho_estimado": rho_hat, "dp": dp, "dp_simulado": dp_sim, "emd": Z_EMD * dp,
                       "n_unidades": int(unid.max()) + 1, "n_tratadas": int(x.groupby("CO_IES")["tratada"].first().sum())})
    return linhas


# ========================================================================================================= #
# G4 — painel UF × trimestre
# ========================================================================================================= #
def sm_nominal(ano: int, tri: int) -> float:
    return SM_2023T1 if (ano, tri) == (2023, 1) else SALARIO_MINIMO_NOMINAL[ano]


def painel_g4() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(painel UF × trimestre com hiato e ln SM real; exposição por UF em 2012)."""
    con = duckdb.connect()
    sm_case = "CASE " + " ".join(f"WHEN m.ano = {a} THEN {v}" for a, v in SALARIO_MINIMO_NOMINAL.items()) + " END"
    sm_sql = f"(CASE WHEN m.ano = 2023 AND m.trimestre = 1 THEN {SM_2023T1} ELSE {sm_case} END)"
    base = f"""
        SELECT m.ano, m.trimestre, CAST(m.UF AS INTEGER) AS uf,
               CASE WHEN m.V2010 = '1' THEN 'Branca' ELSE 'Negra' END AS raca, m.V1028 AS peso,
               m.VD4016 AS renda_nom, {sm_sql} AS sm, d.deflator_habitual AS defl
        FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1) m
        LEFT JOIN read_parquet('{DEFLATOR_PATH}') d ON m.ano = d.ano AND m.trimestre = d.trimestre AND m.UF = d.UF
        WHERE {pop.REFERENCIA.sql('m')} AND m.V2010 IN ('1', '2', '4')"""
    agg = con.execute(f"""
        SELECT ano, trimestre, uf, raca, SUM(peso) AS pop, COUNT(*) AS n,
               SUM(peso * LN(renda_nom * defl)) / SUM(peso) AS mlog, AVG(LN(sm * defl)) AS ln_sm_real
        FROM ({base}) GROUP BY ALL""").df()
    expo = con.execute(f"""
        SELECT uf, raca, SUM(peso * (renda_nom <= 1.05 * sm)::INT) / SUM(peso) AS s105,
               SUM(peso * (renda_nom <= 1.5 * sm)::INT) / SUM(peso) AS s150,
               SUM(CASE WHEN trimestre = 1 THEN peso * (renda_nom <= 1.05 * sm)::INT END)
                 / SUM(CASE WHEN trimestre = 1 THEN peso END) AS s105_t1,
               SUM(peso) / 4 AS pop2012
        FROM ({base}) WHERE ano = 2012 GROUP BY ALL""").df()
    p = agg.pivot_table(index=["ano", "trimestre", "uf"], columns="raca", values=["mlog", "n", "pop"]).reset_index()
    p.columns = ["_".join(c).strip("_") for c in p.columns]
    lsm = agg.groupby(["ano", "trimestre", "uf"])["ln_sm_real"].mean().reset_index()
    p = p.merge(lsm, on=["ano", "trimestre", "uf"])
    p["hiato"] = p["mlog_Branca"] - p["mlog_Negra"]
    p["t"] = (p["ano"] - 2012) * 4 + p["trimestre"] - 1
    e = expo.pivot(index="uf", columns="raca", values=["s105", "s150", "s105_t1"])
    ex = pd.DataFrame({"E105": e[("s105", "Negra")] - e[("s105", "Branca")],
                       "E150": e[("s150", "Negra")] - e[("s150", "Branca")],
                       "E105_t1": e[("s105_t1", "Negra")] - e[("s105_t1", "Branca")],
                       "s105_negra": e[("s105", "Negra")], "s105_branca": e[("s105", "Branca")]})
    ex["pop2012"] = expo.groupby("uf")["pop2012"].sum()
    p = p.merge(ex, left_on="uf", right_index=True)
    p["amostra_ok"] = (p["n_Branca"] >= MIN_N_UF) & (p["n_Negra"] >= MIN_N_UF)
    return p, ex.reset_index()


def _residualizar(z: np.ndarray, d: np.ndarray, w: np.ndarray) -> np.ndarray:
    dw = d * w[:, None]
    return z - d @ (np.linalg.pinv(dw.T @ d) @ (dw.T @ z))


def g4_estimar(p: pd.DataFrame, expo: str = "E105", pesos: bool = True, n_wild: int = N_WILD,
               semente: int = SEMENTE) -> dict:
    """β com EF de UF e trimestre; CR1 por UF; wild cluster bootstrap (Webb, nulo imposto) para p e IC (inversão)."""
    x = p[p["amostra_ok"]].reset_index(drop=True)
    uf = pd.factorize(x["uf"])[0]
    d = _dummies_ef(uf, x["t"].to_numpy())
    w = x["pop2012"].to_numpy(float) if pesos else np.ones(len(x))
    reg = (x[expo] * x["ln_sm_real"]).to_numpy(float)
    xt = _residualizar(reg, d, w)
    yt = _residualizar(x["hiato"].to_numpy(float), d, w)
    den = float(xt @ (w * xt))
    beta = float(xt @ (w * yt)) / den
    ng = int(uf.max()) + 1
    ind = np.zeros((ng, len(x)))
    ind[uf, np.arange(len(x))] = 1.0

    def se_cr1(resid: np.ndarray) -> np.ndarray:  # resid: n × B
        s = ind @ ((w * xt)[:, None] * resid)
        return np.sqrt((s ** 2).sum(axis=0) * ng / (ng - 1)) / den

    se = float(se_cr1((yt - beta * xt)[:, None])[0])
    rng = np.random.default_rng(semente)
    webb = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5), np.sqrt(0.5), 1, np.sqrt(1.5)])
    v = webb[rng.integers(0, 6, size=(ng, n_wild))]

    def p_wild(b0: float) -> float:
        er = yt - b0 * xt  # resíduo restrito (EF já removidos)
        acc = 0
        for i in range(0, n_wild, 2000):
            vv = v[:, i:i + 2000]
            ys = _residualizar(er[:, None] * vv[uf], d, w) + b0 * xt[:, None]
            bs = (xt * w) @ ys / den
            ts = (bs - b0) / se_cr1(ys - xt[:, None] * bs[None, :])
            acc += int((np.abs(ts) >= abs((beta - b0) / se)).sum())
        return acc / n_wild

    p0 = p_wild(0.0)
    grade = np.linspace(beta - 10 * se, beta + 10 * se, 161)
    aceita = [b0 for b0 in grade if p_wild(b0) >= 0.05]
    aberto = bool(aceita) and (aceita[0] == grade[0] or aceita[-1] == grade[-1])
    return {"beta": beta, "ep_cr1": se, "p_wild": p0, "ic_inferior": min(aceita) if aceita else np.nan,
            "ic_superior": max(aceita) if aceita else np.nan, "ic_encosta_na_grade": aberto, "n": len(x), "n_uf": ng,
            "p_wild_beta_menos1": p_wild(-1.0)}


def emd_g4(p: pd.DataFrame, expo: str = "E105") -> list[dict]:
    x = p[p["amostra_ok"]].reset_index(drop=True)
    uf = pd.factorize(x["uf"])[0]
    t = x["t"].to_numpy()
    d = _dummies_ef(uf, t)
    w = x["pop2012"].to_numpy(float)
    xt = _residualizar((x[expo] * x["ln_sm_real"]).to_numpy(float), d, w)
    a_vec = w * xt / float(xt @ (w * xt))
    r = residuos_ef(x["hiato"].to_numpy(float), w, uf, t)
    w_u = x.groupby(uf)["pop2012"].first().to_numpy(float)
    sigma2, rho_hat = sigma_rho(r, uf, t, w_u, encolher=0.0)
    linhas = []
    for rho in sorted({*GRADE_RHO, round(max(rho_hat, 0.0), 3)}):
        dp = np.sqrt(var_ar1(a_vec, uf, t, sigma2, rho))
        linhas.append({"desenho": "G4", "desfecho": "hiato (lp)", "parametro": "β (−1 = repasse total)", "rho": rho,
                       "rho_estimado": rho_hat, "dp": dp, "dp_simulado": simular_ar1(a_vec, uf, t, sigma2, rho),
                       "emd": Z_EMD * dp, "n_unidades": int(uf.max()) + 1, "n_tratadas": np.nan,
                       "dp_exposicao": float(np.sqrt(np.cov(x.groupby("uf")[expo].first())))})
    return linhas


# ========================================================================================================= #
# execução
# ========================================================================================================= #
def _ic(est: float, ep: float) -> tuple[float, float]:
    return est - 1.959964 * ep, est + 1.959964 * ep


def gerar_g6() -> pd.DataFrame:
    g = painel_g1()
    linhas = []
    for y in ("Y1", "Y1b", "Y2"):
        linhas += emd_g1(g, y)
    p, _ = painel_g4()
    linhas += emd_g4(p)
    df = pd.DataFrame(linhas)
    pior = df.groupby(["desenho", "desfecho"])["emd"].transform("max")
    df["emd_pior_caso"] = pior
    df["decisao"] = ""
    m1 = (df["desenho"] == "G1") & (df["desfecho"] == "Y1")
    df.loc[m1, "decisao"] = np.select([pior[m1] <= EMD_G1_ROTINA, pior[m1] <= EMD_G1_LIMITE],
                                      ["roda", "roda; só detecta efeitos ≥ EMD"], "não roda")
    m4 = df["desenho"] == "G4"
    df.loc[m4, "decisao"] = np.where(pior[m4] <= EMD_G4_LIMITE, "roda", "não roda")
    salvar_tabela(df, OUTPUT_DIR / "g6_emd.parquet", se_metodo="simulacao_ar1",
                  nota="EMD = 2,80 × DP do estimador sob efeito nulo; G1: σ e ρ só de 2009–2012; pior caso da grade de ρ")
    return df


def gerar_g1() -> None:
    g = painel_g1()
    x = amostra_principal(g)
    linhas = []
    especs = {"principal": (x, True)}
    especs["sem pesos"] = (x, False)
    gn = painel_g1(balanceado=False)
    xn = amostra_principal(gn).dropna(subset=["peso"])
    especs["painel não balanceado"] = (xn, True)
    for lim in (0.01, 0.10):
        especs[f"limiar {int(lim * 100)}% para 'sem reserva'"] = (amostra_principal(painel_g1(limiar=lim)), True)
    nunca = x[~((x["grupo"] == "controle") & (x["coorte"] > 0))]
    especs["controle: nunca adotou até 2023"] = (nunca, True)
    for nome, (dados, pesos) in especs.items():
        ys = DESFECHOS_G1 if nome == "principal" else {"Y1": DESFECHOS_G1["Y1"], "Y1b": DESFECHOS_G1["Y1b"]}
        for y, rot in ys.items():
            res = event_study(dados, y, pesos)
            boot = bootstrap_es(dados, y, JANELAS_G1, pesos)
            p_pre = wald_pre(res, [2009, 2010, 2011])
            for jan, anos in {**{str(a): [a] for a in res["anos"]}, **JANELAS_G1}.items():
                est, ep = contraste(res, anos)
                lo, hi = _ic(est, ep)
                linha = {"especificacao": nome, "desfecho": y, "rotulo": rot, "periodo": jan, "estimativa": est,
                         "ep_cr1": ep, "ic_inferior": lo, "ic_superior": hi, "n": res["n"], "n_instituicoes": res["n_unid"],
                         "p_pre_tendencia_2009_2011": p_pre}
                if jan in JANELAS_G1:
                    b = boot[jan]
                    linha |= {"ep_boot": float(np.nanstd(b, ddof=1)), "ic_boot_inferior": float(np.nanpercentile(b, 2.5)),
                              "ic_boot_superior": float(np.nanpercentile(b, 97.5))}
                    ep_max = max(ep, linha["ep_boot"])
                    linha["ep"] = ep_max
                    linha["ic_inferior"], linha["ic_superior"] = _ic(est, ep_max)
                    linha["p_valor"] = float(2 * stats.norm.sf(abs(est / ep_max)))
                linhas.append(linha)
            print(f"G1 {nome} {y}: ok", flush=True)
    # sensibilidade escalonada (Callaway–Sant'Anna), todas as instituições públicas balanceadas
    for controle in ("nunca", "ainda_nao"):
        est, dist = cs_bootstrap(g, "Y1", controle)
        for k, v in est.items():
            ep = float(np.nanstd(dist[k], ddof=1))
            lo, hi = _ic(v, ep)
            linhas.append({"especificacao": f"Callaway–Sant'Anna, controle {controle.replace('_', ' ')}",
                           "desfecho": "Y1", "rotulo": DESFECHOS_G1["Y1"], "periodo": k, "estimativa": v, "ep": ep,
                           "ic_inferior": lo, "ic_superior": hi, "n_instituicoes": g["CO_IES"].nunique()})
    df = pd.DataFrame(linhas)
    fam = (df["especificacao"] == "principal") & df["periodo"].isin(JANELAS_G1) & df["desfecho"].isin(["Y1", "Y1b", "Y2", "Y3"])
    df["familia_fdr"] = np.where(fam, "principal", None)
    df["p_valor_sem_fdr"] = df["p_valor"].where(~fam)
    df.loc[~fam, "p_valor"] = np.nan
    df = multiplicidade.adicionar_fdr(df, ["familia_fdr"])
    salvar_tabela(df, OUTPUT_DIR / "g1_cotas_federais.parquet", se_metodo="cr1_instituicao_e_bootstrap_instituicao",
                  familia_fdr=["familia_fdr"],
                  nota="δ em p.p. relativos a 2012; ep = maior entre CR1 e bootstrap (999) nas janelas")
    ser = (g.melt(id_vars=["CO_IES", "ano", "grupo", "peso"], value_vars=list(DESFECHOS_G1),
                              var_name="desfecho", value_name="valor").dropna(subset=["valor"])
           .groupby(["grupo", "desfecho", "ano"])
           .apply(lambda s: pd.Series({"media": np.average(s["valor"], weights=s["peso"]),
                                       "n_instituicoes": s["CO_IES"].nunique()}), include_groups=False)
           .reset_index())
    salvar_tabela(ser, OUTPUT_DIR / "g1_series_grupos.parquet", se_metodo="sem_inferencia",
                  nota="Médias ponderadas pelos ingressantes de 2012, por grupo e ano")


def gerar_g4() -> None:
    p, ex = painel_g4()
    linhas = []
    especs = {"principal": dict(), "exposição até 1,5 SM": dict(expo="E150"), "sem pesos": dict(pesos=False),
              "2012–2019": dict(filtro=p["ano"] <= 2019), "sem 2020–2021": dict(filtro=~p["ano"].isin([2020, 2021])),
              "exposição de 2012T1": dict(expo="E105_t1")}
    for nome, o in especs.items():
        dados = p[o["filtro"]] if "filtro" in o else p
        r = g4_estimar(dados, o.get("expo", "E105"), o.get("pesos", True))
        linhas.append({"tipo": "beta", "especificacao": nome, "estimativa": r["beta"], "ep": r["ep_cr1"],
                       "ic_inferior": r["ic_inferior"], "ic_superior": r["ic_superior"], "p_valor": r["p_wild"],
                       "p_valor_beta_igual_menos1": r["p_wild_beta_menos1"], "ic_encosta_na_grade": r["ic_encosta_na_grade"],
                       "n": r["n"], "n_uf": r["n_uf"]})
        print(f"G4 {nome}: β = {r['beta']:.3f}", flush=True)
    df = pd.DataFrame(linhas)
    df = multiplicidade.adicionar_fdr(df, None)
    ex = ex.assign(tipo="exposicao_uf")
    df = pd.concat([df, ex], ignore_index=True)
    salvar_tabela(df, OUTPUT_DIR / "g4_salario_minimo.parquet", se_metodo="wild_cluster_bootstrap_webb_uf",
                  familia_fdr=None, nota="β: −1 = repasse integral do mínimo a quem ganha até 1,05 SM; IC por inversão do "
                                          "wild bootstrap; ep = CR1 por UF (só registro)")


# ========================================================================================================= #
# G1 — sensibilidade de Rambachan–Roth (magnitudes relativas), análise POSTERIOR ao pré-registro
# ========================================================================================================= #
GRADE_MBAR = (0.0, 0.1, 0.2, 0.25, 0.5, 1.0, 2.0)


def rr_magnitudes_relativas(delta_pre: dict[int, float], theta: float, ep: float, horizontes: list[int],
                            mbar: float) -> dict:
    """Versão conservadora e simplificada de Rambachan & Roth (2023, *Review of Economic Studies*), restrição de
    magnitudes relativas: a violação de tendências paralelas entre anos consecutivos depois da base é no máximo
    M̄ × a maior variação entre anos consecutivos antes da base (Δmax, tratada como conhecida). O viés do efeito no
    horizonte h fica limitado por M̄·Δmax·h; para a média de vários horizontes, por M̄·Δmax·média(h). IC robusto =
    [θ − viés − 1,96·ep, θ + viés + 1,96·ep] (mais largo que o FLCI do artigo; não incorpora a incerteza de Δmax)."""
    anos = sorted(delta_pre)
    serie = [delta_pre[a] for a in anos] + [0.0]
    dmax = float(max(abs(b - a) for a, b in zip(serie[:-1], serie[1:])))
    vies = mbar * dmax * float(np.mean(horizontes))
    return {"M_barra": mbar, "delta_max_pre": dmax, "vies_maximo": vies,
            "ic_inferior": theta - vies - Z95_ * ep, "ic_superior": theta + vies + Z95_ * ep}


def gerar_g1_rr() -> pd.DataFrame:
    g1 = pd.read_parquet(OUTPUT_DIR / "g1_cotas_federais.parquet")
    x = g1[g1["especificacao"] == "principal"]
    linhas = []
    for y in ("Y1", "Y1b"):
        s = x[x["desfecho"] == y]
        pre = {int(a): float(s.loc[s["periodo"] == str(a), "estimativa"].iloc[0]) for a in (2009, 2010, 2011)}
        for jan, anos in JANELAS_G1.items():
            j = s[s["periodo"] == jan].iloc[0]
            hor = [a - BASE for a in anos]
            for mb in GRADE_MBAR:
                linhas.append({"desfecho": y, "periodo": jan, "estimativa": float(j["estimativa"]), "ep": float(j["ep"]),
                               **rr_magnitudes_relativas(pre, float(j["estimativa"]), float(j["ep"]), hor, mb)})
            lo0 = float(j["estimativa"]) - Z95_ * float(j["ep"])
            hi0 = float(j["estimativa"]) + Z95_ * float(j["ep"])
            dmax = linhas[-1]["delta_max_pre"]
            quebra = (max(lo0, -hi0) / (dmax * float(np.mean(hor)))) if (lo0 > 0 or hi0 < 0) else 0.0
            linhas.append({"desfecho": y, "periodo": jan, "estimativa": float(j["estimativa"]), "ep": float(j["ep"]),
                           "M_barra": np.nan, "delta_max_pre": dmax, "M_barra_de_ruptura": quebra})
    df = pd.DataFrame(linhas)
    salvar_tabela(df, OUTPUT_DIR / "g1_sensibilidade_rr.parquet", se_metodo="rambachan_roth_magnitudes_relativas_conservador",
                  nota="Análise posterior ao pré-registro; IC conservador (Δmax tratado como conhecido); M̄ de ruptura = "
                       "menor M̄ com IC contendo zero")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--so", nargs="*", default=None, help="g6 g1 g4 g1rr")
    fazer = set(parser.parse_args().so or ["g6", "g1", "g4"])
    if fazer == {"g1rr"}:
        print(gerar_g1_rr().round(2).to_string())
        return
    if "g6" in fazer:
        emd = gerar_g6()
    else:
        emd = pd.read_parquet(OUTPUT_DIR / "g6_emd.parquet")
    print(emd[["desenho", "desfecho", "rho", "dp", "dp_simulado", "emd", "decisao"]].to_string(), flush=True)
    dec = emd[emd["decisao"] != ""].groupby("desenho")["decisao"].first()
    if "g1" in fazer:
        if dec.get("G1", "não roda").startswith("roda"):
            gerar_g1()
        else:
            print("G1 não roda (sem poder; ficha G6).")
    if "g4" in fazer:
        if dec.get("G4", "não roda").startswith("roda"):
            gerar_g4()
        else:
            print("G4 não roda (sem poder; ficha G6).")


if __name__ == "__main__":
    main()
