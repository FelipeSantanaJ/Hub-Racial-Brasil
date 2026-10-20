"""Onda 4 — Blocos E (educação) e H (origem social e patrimônio), parte que sai da PNAD Contínua
(`docs/PLANO_DE_ANALISE.md`; fichas `docs/studies/{E1,E4,H1,H2,H3}`). SAEB, Censo Escolar, Censo da Educação Superior
e POF ficam para depois (fontes externas, sem download autorizado).

- **E1** — frequência, etapa adequada, atraso, fora da escola e conclusão por idade simples (5–29) e raça.
- **E4** — rede privada × pública por etapa e raça; bruto, condicional ao lugar e, para corresidentes, à escolaridade
  dos pais; composição racial da graduação por rede.
- **H1** — transmissão educacional pais → filhos (corresidentes) e o viés de corresidência medido.
- **H2** — hiato de renda do D1 com e sem origem (escolaridade e renda dos pais), elasticidade *proxy* e matriz de
  quintis.
- **H3** — casa própria e rendas de aluguel/aplicações por raça, dentro do mesmo décimo de renda domiciliar.

Ligação filho–pais: filho(a) do responsável e do cônjuge, só do responsável ou enteado(a) (`V2005` 04/05/06); pais =
responsável (01) e cônjuge (02/03) do mesmo domicílio e trimestre (UPA + V1008 + V1014).

Uso:
    python -m src.processing.bloco_eh [--so e1 e4 h1 h2 h3]
"""
from __future__ import annotations

import argparse

import duckdb
import numpy as np
import pandas as pd
from scipy import stats

from src.inference import multiplicidade, variancia
from src.inference.saida import salvar_tabela
from src.processing.agregacoes_pnadc import DEFLATOR_PATH, OUTPUT_DIR, PARQUET_GLOB
from src.processing.bloco_d import BLOCOS, ROTULO, Sistema, _dummies, ep_de, gelbach, montar_x
from src.processing.sensibilidade_populacao import ANUAL_GLOB, Z95
from src.utils import populacao as pop

RACAS = ["Branca", "Negra", "Indígena"]
JANELAS = {"2012": [(2012, t) for t in (1, 2, 3, 4)],
           "2025T3-2026T2": [(2025, 3), (2025, 4), (2026, 1), (2026, 2)]}
JANELAS_E4 = {"2016": [(2016, t) for t in (1, 2, 3, 4)], "2025T3-2026T2": JANELAS["2025T3-2026T2"]}
RACA_SQL = """CASE m.V2010 WHEN '1' THEN 'Branca' WHEN '2' THEN 'Negra' WHEN '4' THEN 'Negra' WHEN '5' THEN 'Indígena' END"""
# etapa que a pessoa frequenta, harmonizada: V3003 (até 4T2015) e V3003A (desde 2016); conferida pela idade média
ETAPA_SQL = """CASE WHEN m.V3002 <> '1' OR m.V3002 IS NULL THEN 'não frequenta'
     WHEN m.V3003A IS NOT NULL THEN CASE m.V3003A WHEN '01' THEN 'creche' WHEN '02' THEN 'pré-escola'
          WHEN '04' THEN 'fundamental' WHEN '06' THEN 'médio' WHEN '08' THEN 'superior'
          WHEN '09' THEN 'pós' WHEN '10' THEN 'pós' WHEN '11' THEN 'pós' ELSE 'EJA/alfabetização' END
     ELSE CASE m.V3003 WHEN '01' THEN 'pré-escola' WHEN '03' THEN 'fundamental' WHEN '05' THEN 'médio'
          WHEN '07' THEN 'superior' WHEN '08' THEN 'pós' WHEN '09' THEN 'pós' ELSE 'EJA/alfabetização' END END"""
ORIGEM = {"1": "G1 até fundamental incompleto", "2": "G1 até fundamental incompleto",
          "3": "G2 fundamental completo a médio incompleto", "4": "G2 fundamental completo a médio incompleto",
          "5": "G3 médio completo a superior incompleto", "6": "G3 médio completo a superior incompleto",
          "7": "G4 superior completo"}
GRUPOS_ORIGEM = sorted(set(ORIGEM.values()))
SE = "linearizacao_taylor_estrato_upa"
SE_WLS = "wls_influencia_linearizacao_estrato_upa"
DECLARACAO_H = "associação entre origem observada e destino; não efeito causal da origem; amostra restrita a quem mora com os pais"


# ----------------------------------------------------------------------------------------- #
# dados
# ----------------------------------------------------------------------------------------- #
def micro_eh(con, tris: list[tuple[int, int]], idade_min: int = 5, idade_max: int = 29) -> pd.DataFrame:
    """Pessoas (Branca, Negra, Indígena) de `idade_min` a `idade_max` com as informações dos pais do domicílio."""
    filtro = " OR ".join(f"(m.ano = {a} AND m.trimestre = {t})" for a, t in tris)
    dom = "PARTITION BY m.ano, m.trimestre, m.UPA, m.V1008, m.V1014"
    pais = "m.V2005 IN ('01','02','03')"
    return con.execute(f"""
        WITH t AS (
          SELECT m.*, d.deflator_habitual AS defl,
                 MAX(CASE WHEN {pais} THEN m.VD3004 END) OVER ({dom}) AS educ_pais,
                 SUM(CASE WHEN {pais} THEN COALESCE(m.VD4019, 0) * d.deflator_habitual ELSE 0 END) OVER ({dom}) AS renda_pais,
                 MAX(CASE WHEN {pais} AND m.VD4009 IN ('05','06','07','08') THEN 1 ELSE 0 END) OVER ({dom}) AS pais_emp_pub
          FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1) m
          LEFT JOIN read_parquet('{DEFLATOR_PATH}') d ON m.ano = d.ano AND m.trimestre = d.trimestre AND m.UF = d.UF
          WHERE ({filtro}))
        SELECT m.ano, m.trimestre, {RACA_SQL} AS raca, m.V2007 AS sexo, m.V2009 AS idade, m.V2005 AS condicao,
               m.VD3004 AS instrucao, {ETAPA_SQL} AS etapa, m.V3002A AS rede,
               CAST(m.UF AS VARCHAR) AS uf, m.V1022 AS urbano, m.V1023 AS area, m.V4039 AS horas,
               m.VD4009 AS posicao, m.VD4012 AS previdencia, m.VD4011 AS ocupacao, m.VD4010 AS atividade,
               m.V1028 AS peso, m.UPA AS upa, m.Estrato AS estrato,
               COALESCE({pop.REFERENCIA.sql('m')}, FALSE) AS em_p1,
               CASE WHEN {pop.REFERENCIA.sql('m')} THEN m.VD4016 * m.defl END AS renda,
               m.V2005 IN ('04','05','06') AND m.educ_pais IS NOT NULL AS corresidente,
               CASE WHEN m.V2005 IN ('04','05','06') THEN m.educ_pais END AS educ_pais,
               CASE WHEN m.V2005 IN ('04','05','06') THEN m.renda_pais END AS renda_pais,
               m.V2005 IN ('04','05','06') AND m.pais_emp_pub = 1 AS pais_emp_pub
        FROM t m
        WHERE m.V2009 BETWEEN {idade_min} AND {idade_max} AND m.V2010 IN ('1','2','4','5') AND m.V2007 IN ('1','2')
    """).df()


# ----------------------------------------------------------------------------------------- #
# ferramentas
# ----------------------------------------------------------------------------------------- #
def prop(ind: np.ndarray, w: np.ndarray, dom: np.ndarray) -> tuple[float, np.ndarray]:
    z, mu = variancia.influencia_media(np.where(dom, ind, 0.0), w, dom)
    return float(mu), z


def _ic(df: pd.DataFrame, col: str = "estimativa") -> pd.DataFrame:
    df["ic_inferior"] = df[col] - Z95 * df["ep"]
    df["ic_superior"] = df[col] + Z95 * df["ep"]
    return df


def _p(df: pd.DataFrame, col: str = "estimativa") -> pd.DataFrame:
    df["p_valor"] = 2 * stats.norm.sf(np.abs(df[col] / df["ep"]))
    return df


def _publicavel(df: pd.DataFrame) -> pd.DataFrame:
    with np.errstate(divide="ignore", invalid="ignore"):
        cv = df["ep"] / df["estimativa"].abs()
    df["publicavel"] = (df["n"].fillna(1e9) >= 30) & ((cv <= 0.30) | df["estimativa"].abs().lt(1e-12) | df["n"].isna())
    return df


def x_com(m: pd.DataFrame, blocos: list[str], racas: list[str], extra: dict[str, np.ndarray] | None = None):
    """montar_x + blocos extras (matriz por nome); colinearidade checada em montar_x só para os blocos padrão."""
    X, idx = montar_x(m, blocos, racas)
    if extra:
        cols = [X]
        k = X.shape[1]
        for nome, mat in extra.items():
            mat = np.atleast_2d(mat.T).T if mat.ndim == 1 else mat
            usa = np.abs(mat).sum(axis=0) > 0
            mat = mat[:, usa]
            cols.append(mat)
            idx[nome] = np.arange(k, k + mat.shape[1])
            k += mat.shape[1]
        X = np.column_stack(cols)
    return X, idx


def dummies_origem(educ_pais: pd.Series) -> np.ndarray:
    g = educ_pais.astype(str).map(ORIGEM)
    mat, _ = _dummies(g)
    return mat


# ----------------------------------------------------------------------------------------- #
# E1
# ----------------------------------------------------------------------------------------- #
ETAPA_ADEQUADA = {range(6, 15): ("fundamental", "médio", "superior"), range(15, 18): ("médio", "superior", "pós"),
                  range(18, 25): ("superior", "pós")}


def indicadores_e1(m: pd.DataFrame) -> dict[str, np.ndarray]:
    idade, etapa = m["idade"].to_numpy(), m["etapa"].to_numpy(object)
    instr = pd.to_numeric(m["instrucao"], errors="coerce").to_numpy()
    freq = etapa != "não frequenta"
    adequada = np.zeros(len(m), bool)
    for faixa, ok in ETAPA_ADEQUADA.items():
        sel = np.isin(idade, list(faixa))
        adequada |= sel & np.isin(etapa, ok)
    tem_faixa = (idade >= 6) & (idade <= 24)
    atraso = tem_faixa & freq & ~adequada
    fora_sem_medio = (~freq) & (instr < 5) & (idade >= 15)
    return {"frequenta": 100.0 * freq, "etapa_adequada": np.where(tem_faixa, 100.0 * adequada, np.nan),
            "atraso": np.where(tem_faixa, 100.0 * atraso, np.nan),
            "fora_da_escola_sem_medio": np.where(idade >= 15, 100.0 * fora_sem_medio, np.nan),
            "fundamental_completo": 100.0 * (instr >= 3), "medio_completo": 100.0 * (instr >= 5),
            "superior_completo": 100.0 * (instr == 7)}


def e1(m: pd.DataFrame, periodo: str, guardar: bool = False) -> tuple[list[dict], dict]:
    w, upa, est = m["peso"].to_numpy(float), m["upa"].to_numpy(), m["estrato"].to_numpy()
    raca, idade = m["raca"].to_numpy(object), m["idade"].to_numpy()
    ind = indicadores_e1(m)
    faixas = [(a, a, str(a)) for a in range(5, 30)] + [(25, 29, "25–29"), (15, 17, "15–17"), (18, 24, "18–24"),
                                                      (6, 14, "6–14")]
    linhas, guard = [], {}
    for nome, v in ind.items():
        ok = np.isfinite(v)
        for lo, hi, rot in faixas:
            d0 = ok & (idade >= lo) & (idade <= hi)
            if not d0.any():
                continue
            res = {}
            for r in RACAS:
                d = d0 & (raca == r)
                if d.sum() == 0:
                    continue
                mu, z = prop(np.nan_to_num(v), w, d)
                res[r] = (mu, z)
                linhas.append({"periodo": periodo, "indicador": nome, "idade": rot, "raca": r, "estimativa": mu,
                               "ep": ep_de(z, upa, est), "n": int(d.sum())})
            for r in ("Negra", "Indígena"):
                if r in res and "Branca" in res:
                    dz = res["Branca"][1] - res[r][1]
                    linhas.append({"periodo": periodo, "indicador": nome, "idade": rot, "raca": f"Branca − {r}",
                                   "estimativa": res["Branca"][0] - res[r][0], "ep": ep_de(dz, upa, est)})
                    if guardar:
                        guard[(nome, rot, r)] = (res["Branca"][0] - res[r][0], dz)
    guard["upa"], guard["est"] = upa, est
    return linhas, guard


def mudanca(g0: dict, g1: dict, chaves: list) -> list[dict]:
    upa = np.concatenate([g0["upa"], g1["upa"]])
    est = np.concatenate([g0["est"], g1["est"]])
    out = []
    for ch in chaves:
        if ch in g0 and ch in g1:
            out.append({"chave": " · ".join(map(str, ch)), "valor_inicial": g0[ch][0], "valor_final": g1[ch][0],
                        "estimativa": g1[ch][0] - g0[ch][0], "ep": ep_de(np.concatenate([-g0[ch][1], g1[ch][1]]), upa, est)})
    return out


# ----------------------------------------------------------------------------------------- #
# E4
# ----------------------------------------------------------------------------------------- #
def e4(m: pd.DataFrame, periodo: str) -> list[dict]:
    w, upa, est = m["peso"].to_numpy(float), m["upa"].to_numpy(), m["estrato"].to_numpy()
    raca, etapa = m["raca"].to_numpy(object), m["etapa"].to_numpy(object)
    privada = 100.0 * (m["rede"].astype(str) == "1").to_numpy()
    tem_rede = m["rede"].notna().to_numpy()
    cor = m["corresidente"].fillna(False).to_numpy(bool)
    linhas = []
    for et in ("pré-escola", "fundamental", "médio", "superior"):
        d0 = tem_rede & (etapa == et)
        for r in RACAS:
            mu, z = prop(privada, w, d0 & (raca == r))
            linhas.append({"periodo": periodo, "etapa": et, "raca": r, "medida": "% na rede privada", "estimativa": mu,
                           "ep": ep_de(z, upa, est), "n": int((d0 & (raca == r)).sum())})
        # bruto e condicional (MQO linear), em toda a etapa e nos corresidentes
        guard = {}
        for amostra, dom, extra in (("todos", d0, False), ("corresidentes", d0 & cor, False),
                                    ("corresidentes", d0 & cor, "educ"), ("corresidentes", d0 & cor, "educ+renda")):
            sub = m[dom]
            if len(sub) < 200:
                continue
            racas = [r for r in ("Negra", "Indígena") if (sub["raca"] == r).sum() >= 30]
            for esp, blocos in (("bruto", []), ("condicional (território)", ["territorio"])):
                if extra and esp == "bruto":
                    continue
                if extra == "educ":
                    ext = {"origem": dummies_origem(sub["educ_pais"])}
                elif extra == "educ+renda":  # sensibilidade acrescentada depois da 1ª rodada (declarada na ficha)
                    rp = sub["renda_pais"].fillna(0).to_numpy(float)
                    ext = {"origem": np.column_stack([dummies_origem(sub["educ_pais"]), np.log1p(rp), (rp <= 0).astype(float)])}
                else:
                    ext = None
                X, idx = x_com(sub, blocos, racas, ext)
                s = Sistema(X, privada[dom], w[dom])
                cols = np.arange(X.shape[1])
                b = s.beta(cols)
                rot = esp + {"educ": " + escolaridade dos pais", "educ+renda": " + escolaridade e renda dos pais"}.get(extra, "")
                for j, r in enumerate(racas, start=1):
                    c = np.zeros(len(cols))
                    c[j] = 1.0
                    psi = np.zeros(len(m))
                    psi[dom] = s.influencia(cols, c, b)
                    linhas.append({"periodo": periodo, "etapa": et, "raca": f"Branca − {r}", "medida": f"{rot} ({amostra})",
                                   "estimativa": -float(b[j]), "ep": ep_de(psi, upa, est), "n": int((sub["raca"] == r).sum())})
                    guard[(f"{rot} ({amostra})", r)] = (-float(b[j]), -psi)
        for r in ("Negra",):
            base_ = guard.get(("bruto (corresidentes)", r))
            for rot in ("condicional (território) + escolaridade dos pais (corresidentes)",
                        "condicional (território) + escolaridade e renda dos pais (corresidentes)"):
                c_ = guard.get((rot, r))
                if base_ and c_:
                    razao = c_[0] / base_[0]
                    psi = c_[1] / base_[0] - c_[0] * base_[1] / base_[0] ** 2
                    linhas.append({"periodo": periodo, "etapa": et, "raca": f"Branca − {r}",
                                   "medida": "razão: " + rot.replace(" (corresidentes)", "") + " ÷ bruto (corresidentes)",
                                   "estimativa": razao, "ep": ep_de(psi, upa, est)})
    # composição racial da graduação por rede
    sup = tem_rede & (etapa == "superior")
    neg = 100.0 * (raca == "Negra")
    res = {}
    for rede, cod in (("pública", "2"), ("privada", "1")):
        d = sup & (m["rede"].astype(str) == cod).to_numpy() & np.isin(raca, RACAS)
        res[rede] = prop(neg, w, d)
        linhas.append({"periodo": periodo, "etapa": "superior", "raca": "Negra", "medida": f"% negra na graduação {rede}",
                       "estimativa": res[rede][0], "ep": ep_de(res[rede][1], upa, est), "n": int(d.sum())})
    linhas.append({"periodo": periodo, "etapa": "superior", "raca": "Negra", "medida": "% negra: pública − privada",
                   "estimativa": res["pública"][0] - res["privada"][0], "ep": ep_de(res["pública"][1] - res["privada"][1], upa, est)})
    return linhas


# ----------------------------------------------------------------------------------------- #
# H1
# ----------------------------------------------------------------------------------------- #
def desfechos_h1(m: pd.DataFrame) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """{nome: (indicador 0/100, máscara de idade)}."""
    idade = m["idade"].to_numpy()
    instr = pd.to_numeric(m["instrucao"], errors="coerce").to_numpy()
    return {"médio completo (19–24)": (100.0 * (instr >= 5), (idade >= 19) & (idade <= 24)),
            "frequenta ou concluiu superior (18–24)": (100.0 * ((instr >= 6) | (m["etapa"] == "superior").to_numpy()),
                                                       (idade >= 18) & (idade <= 24)),
            "superior completo (25–29)": (100.0 * (instr == 7), (idade >= 25) & (idade <= 29))}


def h1(m: pd.DataFrame, periodo: str) -> tuple[list[dict], list[dict], dict]:
    w, upa, est = m["peso"].to_numpy(float), m["upa"].to_numpy(), m["estrato"].to_numpy()
    raca, idade = m["raca"].to_numpy(object), m["idade"].to_numpy()
    cor = m["corresidente"].fillna(False).to_numpy(bool)
    orig = m["educ_pais"].astype(str).map(ORIGEM).to_numpy(object)
    trans, corres, guard = [], [], {}
    # (a) % que mora com pai/mãe por idade e raça
    for a in list(range(18, 30)) + ["18–24", "25–29"]:
        d0 = (idade == a) if isinstance(a, int) else ((idade >= int(a[:2])) & (idade <= int(a[-2:])))
        res = {}
        for r in RACAS:
            mu, z = prop(100.0 * cor, w, d0 & (raca == r))
            res[r] = (mu, z)
            corres.append({"periodo": periodo, "medida": "% que mora com pai/mãe", "idade": str(a), "raca": r,
                           "estimativa": mu, "ep": ep_de(z, upa, est), "n": int((d0 & (raca == r)).sum())})
        corres.append({"periodo": periodo, "medida": "% que mora com pai/mãe", "idade": str(a), "raca": "Branca − Negra",
                       "estimativa": res["Branca"][0] - res["Negra"][0], "ep": ep_de(res["Branca"][1] - res["Negra"][1], upa, est)})
    for nome, (y, faixa) in desfechos_h1(m).items():
        if not all((faixa & cor & (raca == r)).any() for r in ("Branca", "Negra")):
            continue
        # (b) desfecho entre corresidentes × não corresidentes; (c) diferença racial na população × na subamostra
        dif = {}
        for amostra, mask in (("todos", faixa), ("corresidentes", faixa & cor), ("não corresidentes", faixa & ~cor)):
            res = {}
            for r in RACAS:
                if not (mask & (raca == r)).any():
                    continue
                mu, z = prop(y, w, mask & (raca == r))
                res[r] = (mu, z)
                corres.append({"periodo": periodo, "medida": f"{nome}", "idade": amostra, "raca": r, "estimativa": mu,
                               "ep": ep_de(z, upa, est), "n": int((mask & (raca == r)).sum())})
            if "Branca" not in res or "Negra" not in res:
                continue
            dif[amostra] = (res["Branca"][0] - res["Negra"][0], res["Branca"][1] - res["Negra"][1])
            corres.append({"periodo": periodo, "medida": nome, "idade": amostra, "raca": "Branca − Negra",
                           "estimativa": dif[amostra][0], "ep": ep_de(dif[amostra][1], upa, est)})
        if "corresidentes" in dif and "todos" in dif:
            v = dif["corresidentes"][0] - dif["todos"][0]
            corres.append({"periodo": periodo, "medida": nome, "idade": "viés: corresidentes − todos",
                           "raca": "Branca − Negra", "estimativa": v,
                           "ep": ep_de(dif["corresidentes"][1] - dif["todos"][1], upa, est)})
        # H1.1/H1.3: por origem, entre corresidentes
        base = faixa & cor
        p, s_neg = {}, {}
        for g in GRUPOS_ORIGEM:
            for r in RACAS:
                d = base & (orig == g) & (raca == r)
                if d.sum() == 0:
                    continue
                p[(g, r)] = prop(y, w, d)
                trans.append({"periodo": periodo, "desfecho": nome, "origem": g, "raca": r, "medida": "% com o desfecho",
                              "estimativa": p[(g, r)][0], "ep": ep_de(p[(g, r)][1], upa, est), "n": int(d.sum())})
            for r in ("Negra", "Indígena"):
                if (g, r) in p and (g, "Branca") in p:
                    trans.append({"periodo": periodo, "desfecho": nome, "origem": g, "raca": f"Branca − {r}",
                                  "medida": "diferença dentro da origem (p.p.)",
                                  "estimativa": p[(g, "Branca")][0] - p[(g, r)][0],
                                  "ep": ep_de(p[(g, "Branca")][1] - p[(g, r)][1], upa, est)})
            s_neg[g] = prop(100.0 * (orig == g), w, base & (raca == "Negra"))
        comuns = [g for g in GRUPOS_ORIGEM if (g, "Branca") in p and (g, "Negra") in p]
        # bruto (corresidentes) e padronizado pela distribuição de origem dos negros
        pb, pn = prop(y, w, base & (raca == "Branca")), prop(y, w, base & (raca == "Negra"))
        bruto, zb = pb[0] - pn[0], pb[1] - pn[1]
        pad = sum(s_neg[g][0] / 100 * (p[(g, "Branca")][0] - p[(g, "Negra")][0]) for g in comuns)
        zp = sum(s_neg[g][0] / 100 * (p[(g, "Branca")][1] - p[(g, "Negra")][1])
                 + (p[(g, "Branca")][0] - p[(g, "Negra")][0]) * s_neg[g][1] / 100 for g in comuns)
        razao, zr = pad / bruto, zp / bruto - pad * zb / bruto ** 2
        for med, v_, z_ in (("diferença bruta (corresidentes)", bruto, zb),
                            ("diferença padronizada pela origem dos negros", pad, zp),
                            ("razão padronizada ÷ bruta", razao, zr)):
            trans.append({"periodo": periodo, "desfecho": nome, "origem": "todas", "raca": "Branca − Negra", "medida": med,
                          "estimativa": v_, "ep": ep_de(z_, upa, est)})
        # gradiente de origem (G4 − G1), por raça e Branca+Negra
        for r, mask_r in (("Branca", raca == "Branca"), ("Negra", raca == "Negra"),
                          ("Branca + Negra", np.isin(raca, ["Branca", "Negra"]))):
            a4 = prop(y, w, base & (orig == "G4 superior completo") & mask_r)
            a1 = prop(y, w, base & (orig == "G1 até fundamental incompleto") & mask_r)
            g_, zg = a4[0] - a1[0], a4[1] - a1[1]
            trans.append({"periodo": periodo, "desfecho": nome, "origem": "G4 − G1", "raca": r,
                          "medida": "gradiente de origem (p.p.)", "estimativa": g_, "ep": ep_de(zg, upa, est)})
            guard[(nome, r)] = (g_, zg)
    # H1.2 mobilidade (25–29 corresidentes): grupo do filho × grupo dos pais
    faixa = (idade >= 25) & (idade <= 29) & cor
    gf = m["instrucao"].astype(str).map(ORIGEM).to_numpy(object)
    valido = pd.notna(gf) & pd.notna(orig)
    sobe = valido & np.array([valido[i] and gf[i] > orig[i] for i in range(len(gf))])
    desce = valido & np.array([valido[i] and gf[i] < orig[i] for i in range(len(gf))])
    faixa = faixa & valido
    for nome, ind in (("mobilidade ascendente", 100.0 * sobe), ("mobilidade descendente", 100.0 * desce)):
        res = {}
        for r in RACAS:
            res[r] = prop(ind, w, faixa & (raca == r))
            trans.append({"periodo": periodo, "desfecho": nome + " (25–29)", "origem": "todas", "raca": r,
                          "medida": "% (filho vs. pais)", "estimativa": res[r][0], "ep": ep_de(res[r][1], upa, est),
                          "n": int((faixa & (raca == r)).sum())})
        trans.append({"periodo": periodo, "desfecho": nome + " (25–29)", "origem": "todas", "raca": "Branca − Negra",
                      "medida": "% (filho vs. pais)", "estimativa": res["Branca"][0] - res["Negra"][0],
                      "ep": ep_de(res["Branca"][1] - res["Negra"][1], upa, est)})
        for g in GRUPOS_ORIGEM[:3]:
            rr = {r: prop(ind, w, faixa & (orig == g) & (raca == r)) for r in ("Branca", "Negra")}
            trans.append({"periodo": periodo, "desfecho": nome + " (25–29)", "origem": g, "raca": "Branca − Negra",
                          "medida": "diferença dentro da origem (p.p.)", "estimativa": rr["Branca"][0] - rr["Negra"][0],
                          "ep": ep_de(rr["Branca"][1] - rr["Negra"][1], upa, est)})
    guard["upa"], guard["est"] = upa, est
    return trans, corres, guard


# ----------------------------------------------------------------------------------------- #
# H2
# ----------------------------------------------------------------------------------------- #
def bloco_origem(sub: pd.DataFrame) -> np.ndarray:
    rp = sub["renda_pais"].fillna(0).to_numpy(float)
    return np.column_stack([dummies_origem(sub["educ_pais"]), np.log1p(rp), (rp <= 0).astype(float),
                            sub["pais_emp_pub"].fillna(False).to_numpy(float)])


def h2(m: pd.DataFrame, periodo: str) -> tuple[list[dict], list[dict]]:
    """m: pessoas 18–29 em P1 com horas > 0, Branca e Negra."""
    upa, est = m["upa"].to_numpy(), m["estrato"].to_numpy()
    w = m["peso"].to_numpy(float)
    y = np.log(m["renda"].to_numpy(float))
    cor = m["corresidente"].fillna(False).to_numpy(bool)
    linhas, mob = [], []

    def coef(dom, extra):
        sub = m[dom]
        X, idx = x_com(sub, BLOCOS, ["Negra"], {"origem": bloco_origem(sub)} if extra else None)
        s = Sistema(X, y[dom], w[dom])
        cols = np.arange(X.shape[1])
        b = s.beta(cols)
        c = np.zeros(len(cols))
        c[1] = 1.0
        psi = np.zeros(len(m))
        psi[dom] = s.influencia(cols, c, b)
        return -float(b[1]), -psi, s, idx, dom

    todos = np.ones(len(m), bool)
    res = {"E8, todos de 18–29": coef(todos, False), "E8, corresidentes": coef(cor, False),
           "E8 + origem, corresidentes": coef(cor, True)}
    bruto_c = None
    for esp, (v, psi, *_r) in res.items():
        linhas.append({"periodo": periodo, "especificacao": esp, "medida": "hiato condicional (lp)", "estimativa": v,
                       "ep": ep_de(psi, upa, est), "n": int(res[esp][4].sum())})
    a, pa = res["E8 + origem, corresidentes"][:2]
    b_, pb = res["E8, corresidentes"][:2]
    linhas.append({"periodo": periodo, "especificacao": "mudança ao incluir a origem", "medida": "lp", "estimativa": a - b_,
                   "ep": ep_de(pa - pb, upa, est)})
    linhas.append({"periodo": periodo, "especificacao": "mudança ao incluir a origem", "medida": "% do E8 dos corresidentes",
                   "estimativa": 100 * (a - b_) / b_, "ep": ep_de(100 * ((pa - pb) / b_ - (a - b_) * pb / b_ ** 2), upa, est)})
    # Gelbach com o bloco origem
    _, _, s, idx, dom = res["E8 + origem, corresidentes"]
    blocos = [b for b in BLOCOS if len(idx.get(b, [])) > 0] + ["origem"]
    seq_bruto = s.beta(idx["base"])
    bruto_c = -seq_bruto[1]
    for blk, (dlt, psi_s) in gelbach(s, idx, blocos, 1).items():
        psi = np.zeros(len(m))
        psi[dom] = -psi_s
        linhas.append({"periodo": periodo, "especificacao": "Gelbach (corresidentes, E8 + origem)",
                       "medida": ROTULO.get(blk, "Origem (escolaridade e renda do trabalho dos pais)"),
                       "estimativa": -dlt, "ep": ep_de(psi, upa, est), "pct_do_bruto": 100 * -dlt / bruto_c})
    linhas.append({"periodo": periodo, "especificacao": "Gelbach (corresidentes, E8 + origem)", "medida": "hiato bruto",
                   "estimativa": bruto_c, "ep": np.nan})
    # H2.3: elasticidade proxy (pais com renda > 0), com dummies de idade do filho
    rp = m["renda_pais"].fillna(0).to_numpy(float)
    el = {}
    for r in ("Branca", "Negra"):
        dom = cor & (rp > 0) & (m["raca"] == r).to_numpy()
        sub = m[dom]
        D, _ = _dummies(sub["idade"].astype(int).astype(str))
        X = np.column_stack([np.ones(len(sub)), np.log(rp[dom]), D])
        s = Sistema(X, y[dom], w[dom])
        cols = np.arange(X.shape[1])
        b = s.beta(cols)
        c = np.zeros(len(cols))
        c[1] = 1.0
        psi = np.zeros(len(m))
        psi[dom] = s.influencia(cols, c, b)
        el[r] = (float(b[1]), psi)
        linhas.append({"periodo": periodo, "especificacao": "elasticidade proxy (ln renda filho ~ ln renda dos pais)",
                       "medida": r, "estimativa": el[r][0], "ep": ep_de(psi, upa, est), "n": int(dom.sum())})
    linhas.append({"periodo": periodo, "especificacao": "elasticidade proxy (ln renda filho ~ ln renda dos pais)",
                   "medida": "Negra − Branca", "estimativa": el["Negra"][0] - el["Branca"][0],
                   "ep": ep_de(el["Negra"][1] - el["Branca"][1], upa, est)})
    # H2.4: quintis (pais com renda > 0, corresidentes)
    base = cor & (rp > 0)
    qp = np.quantile(rp[base], [0.2, 0.4, 0.6, 0.8], method="inverted_cdf", weights=w[base])
    qf = np.quantile(y[base], [0.2, 0.4, 0.6, 0.8], method="inverted_cdf", weights=w[base])
    qpais = np.searchsorted(qp, rp, side="left") + 1
    qfilho = np.searchsorted(qf, y, side="left") + 1
    for qpa in (1, 3, 5):
        for qfi in (1, 5):
            res_r = {}
            for r in ("Branca", "Negra"):
                d = base & (qpais == qpa) & (m["raca"] == r).to_numpy()
                res_r[r] = prop(100.0 * (qfilho == qfi), w, d)
                mob.append({"periodo": periodo, "quintil_pais": qpa, "quintil_filho": qfi, "raca": r,
                            "estimativa": res_r[r][0], "ep": ep_de(res_r[r][1], upa, est), "n": int(d.sum())})
            mob.append({"periodo": periodo, "quintil_pais": qpa, "quintil_filho": qfi, "raca": "Negra − Branca",
                        "estimativa": res_r["Negra"][0] - res_r["Branca"][0],
                        "ep": ep_de(res_r["Negra"][1] - res_r["Branca"][1], upa, est)})
    return linhas, mob


# ----------------------------------------------------------------------------------------- #
# H3
# ----------------------------------------------------------------------------------------- #
def h3(con) -> list[dict]:
    linhas = []
    for visita, glob in ANUAL_GLOB.items():
        anos = [r[0] for r in con.execute(f"SELECT DISTINCT ano FROM read_parquet('{glob}', hive_partitioning=1) ORDER BY 1").fetchall()]
        for ano in anos:
            if int(ano) < 2016:
                continue
            cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{glob}', hive_partitioning=1, union_by_name=true) LIMIT 1").fetchall()]
            s01 = "m.S01017" if "S01017" in cols else "NULL"
            m = con.execute(f"""
                SELECT {RACA_SQL} AS raca, m.V2009 AS idade, CAST(m.UF AS VARCHAR) AS uf, m.V1022 AS urbano,
                       m.V1032 AS peso, m.UPA AS upa, m.Estrato AS estrato, m.VD5008 AS renda_pc, {s01} AS condicao_dom,
                       m.V5007A AS aluguel, m.V5008A AS aplicacoes
                FROM read_parquet('{glob}', hive_partitioning = 1, union_by_name = true) m
                WHERE m.ano = {ano} AND m.V2005 NOT IN ('17','18','19') AND m.VD5008 IS NOT NULL
                  AND m.V2010 IN ('1','2','4','5')""").df()
            linhas += h3_ano(m, int(ano), visita)
            print(f"H3 {ano}", flush=True)
    return linhas


def h3_ano(m: pd.DataFrame, ano: int, visita: int) -> list[dict]:
    w, upa, est = m["peso"].to_numpy(float), m["upa"].to_numpy(), m["estrato"].to_numpy()
    raca = m["raca"].to_numpy(object)
    y = m["renda_pc"].to_numpy(float)
    cortes = np.quantile(y, np.arange(1, 10) / 10, method="inverted_cdf", weights=w)
    decimo = np.searchsorted(cortes, y, side="left").astype(str)
    adulto = m["idade"].to_numpy() >= 18
    cd = m["condicao_dom"].astype(str).to_numpy()
    tem_cd = m["condicao_dom"].notna().to_numpy()
    ind = {}
    if tem_cd.any():
        ind.update({"casa própria quitada": (100.0 * (cd == "1"), tem_cd),
                    "casa própria (quitada ou pagando)": (100.0 * np.isin(cd, ["1", "2"]), tem_cd),
                    "alugada": (100.0 * (cd == "3"), tem_cd), "cedida": (100.0 * np.isin(cd, ["4", "5", "6"]), tem_cd)})
    alu = (m["aluguel"].astype(str) == "1").to_numpy()
    apl = (m["aplicacoes"].astype(str) == "1").to_numpy()
    ind.update({"recebe aluguel (18+)": (100.0 * alu, adulto), "recebe aplicações/outros (18+)": (100.0 * apl, adulto),
                "recebe aluguel ou aplicações (18+)": (100.0 * (alu | apl), adulto)})
    linhas = []
    for nome, (v, uni) in ind.items():
        for r in RACAS:
            mu, z = prop(v, w, uni & (raca == r))
            linhas.append({"ano": ano, "visita": visita, "indicador": nome, "raca": r, "medida": "%", "estimativa": mu,
                           "ep": ep_de(z, upa, est), "n": int((uni & (raca == r)).sum())})
        sub = m[uni].assign(decimo=decimo[uni])
        racas = [r for r in ("Negra", "Indígena") if (sub["raca"] == r).sum() >= 30]
        for esp, extra in (("diferença bruta (p.p.)", None), ("diferença no mesmo décimo de renda, UF e situação (p.p.)", True)):
            if extra:
                mats = {"decimo": _dummies(sub["decimo"])[0], "uf": _dummies(sub["uf"])[0], "urbano": _dummies(sub["urbano"])[0]}
                X, idx = x_com(sub, [], racas, mats)
            else:
                X, idx = x_com(sub, [], racas)
            s = Sistema(X, v[uni], w[uni])
            cols = np.arange(X.shape[1])
            b = s.beta(cols)
            for j, r in enumerate(racas, start=1):
                c = np.zeros(len(cols))
                c[j] = 1.0
                psi = np.zeros(len(m))
                psi[uni] = s.influencia(cols, c, b)
                linhas.append({"ano": ano, "visita": visita, "indicador": nome, "raca": f"{r} − Branca", "medida": esp,
                               "estimativa": float(b[j]), "ep": ep_de(psi, upa, est)})
    return linhas


# ----------------------------------------------------------------------------------------- #
def gerar(con, fazer: set[str]) -> None:
    meta = dict(se_metodo=SE)
    if "e1" in fazer:
        linhas, gs = [], {}
        for nome, tris in JANELAS.items():
            m = micro_eh(con, tris)
            x, gs[nome] = e1(m, nome, guardar=True)
            linhas += x
            print(f"E1 {nome}: {len(m):,}".replace(",", "."), flush=True)
            del m
        chaves = [(i, a, r) for i in ("medio_completo", "superior_completo", "frequenta", "etapa_adequada")
                  for a in ("19", "25–29", "15–17", "18–24", "6–14") for r in ("Negra", "Indígena")]
        mud = pd.DataFrame(mudanca(gs["2012"], gs["2025T3-2026T2"], chaves)).assign(periodo="mudança (recente − 2012)")
        for a in range(2012, 2027):
            m = micro_eh(con, [(a, 2)], 19, 29)
            x, _ = e1(m, f"{a}T2")
            linhas += [ln for ln in x if ln["indicador"] in ("medio_completo", "superior_completo")
                       and ln["idade"] in ("19", "25–29")]
            print(f"E1 série {a}T2", flush=True)
        df = _publicavel(_ic(pd.DataFrame(linhas)))
        df = _p(df)
        df.loc[~df["raca"].str.contains("−"), "p_valor"] = np.nan
        df = multiplicidade.adicionar_fdr(df, ["periodo", "indicador", "raca"])
        df = pd.concat([df, _ic(mud)], ignore_index=True)
        salvar_tabela(df, OUTPUT_DIR / "e1_escolarizacao_idade.parquet", familia_fdr=["periodo", "indicador", "raca"], **meta,
                      nota="p.p.; etapa adequada: 6–14 fundamental+, 15–17 médio+, 18–24 superior+; V3003/V3003A harmonizados")
    if "e4" in fazer:
        linhas = []
        for nome, tris in JANELAS_E4.items():
            linhas += e4(micro_eh(con, tris, 4, 40), nome)
            print(f"E4 {nome}", flush=True)
        df = multiplicidade.adicionar_fdr(_p(_ic(pd.DataFrame(linhas))), ["periodo", "medida"])
        salvar_tabela(df, OUTPUT_DIR / "e4_rede_escola.parquet", se_metodo=SE_WLS, familia_fdr=["periodo", "medida"],
                      nota="Rede privada = V3002A 1; condicional por MQO linear; escolaridade dos pais só para corresidentes")
    if "h1" in fazer or "h2" in fazer:
        tr, co, h2l, mob, gh = [], [], [], [], {}
        for nome, tris in JANELAS.items():
            m = micro_eh(con, tris, 18, 29)
            if "h1" in fazer:
                a, b, gh[nome] = h1(m, nome)
                tr += a
                co += b
                print(f"H1 {nome}", flush=True)
            if "h2" in fazer:
                mp = m[m["em_p1"] & m["renda"].notna() & (m["renda"] > 0) & m["horas"].notna() & (m["horas"] > 0)
                       & m["raca"].isin(["Branca", "Negra"])].reset_index(drop=True)
                a, b = h2(mp, nome)
                h2l += a
                mob += b
                print(f"H2 {nome}: {len(mp):,} em P1, {int(mp['corresidente'].sum()):,} corresidentes".replace(",", "."), flush=True)
            del m
        meta_h = dict(declaracao=DECLARACAO_H)
        if tr:
            if len(gh) == 2:
                ch = [(d, r) for d in desfechos_h1(pd.DataFrame({"idade": [], "instrucao": [], "etapa": []}))
                      for r in ("Branca", "Negra", "Branca + Negra")]
                mud = pd.DataFrame(mudanca(gh["2012"], gh["2025T3-2026T2"], ch)).assign(
                    periodo="mudança (recente − 2012)", medida="gradiente de origem (p.p.)")
                tr_df = pd.concat([_ic(pd.DataFrame(tr)), _ic(mud)], ignore_index=True)
            else:
                tr_df = _ic(pd.DataFrame(tr))
            salvar_tabela(tr_df, OUTPUT_DIR / "h1_transmissao_educacional.parquet", **meta, **meta_h,
                          nota="p.p.; origem = maior VD3004 de responsável/cônjuge em 4 grupos")
            salvar_tabela(_publicavel(_ic(pd.DataFrame(co))), OUTPUT_DIR / "h1_corresidencia.parquet", **meta, **meta_h,
                          nota="Viés de corresidência: desfechos de quem mora e de quem não mora com pai/mãe")
        if h2l:
            salvar_tabela(_ic(pd.DataFrame(h2l)), OUTPUT_DIR / "h2_origem_renda.parquet", se_metodo=SE_WLS, **meta_h,
                          nota="ln renda real do trabalho principal; E8 = controles do D1; origem = escolaridade (4 grupos), "
                               "ln(1 + renda do trabalho dos pais), pais sem renda, pai/mãe empregador ou setor público")
            salvar_tabela(_ic(pd.DataFrame(mob)), OUTPUT_DIR / "h2_mobilidade_quintis.parquet", **meta, **meta_h,
                          nota="Quintis da renda do trabalho dos pais (renda > 0) e da renda do filho, na subamostra corresidente")
    if "h3" in fazer:
        df = _p(_ic(pd.DataFrame(h3(con))))
        df.loc[df["medida"] == "%", "p_valor"] = np.nan
        df = multiplicidade.adicionar_fdr(df, ["ano", "raca", "medida"])
        salvar_tabela(df, OUTPUT_DIR / "h3_patrimonio_proxy.parquet", se_metodo=SE_WLS, insumos="anual_v2",
                      familia_fdr=["ano", "raca", "medida"],
                      nota="Condição do domicílio por pessoa (Visita 1); rendas de capital de adultos 18+; décimos de VD5008 "
                           "por limiar (peso empatado vai para o décimo de baixo)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--so", nargs="*", default=None, help="e1 e4 h1 h2 h3")
    fazer = set(parser.parse_args().so or ["e1", "e4", "h1", "h2", "h3"])
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    gerar(con, fazer)


if __name__ == "__main__":
    main()
