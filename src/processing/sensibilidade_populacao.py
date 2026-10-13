"""Onda 1 — Bloco S (S0–S1) e Bloco F (F1, F4): quanto a escolha da população e da renda de
referência muda o hiato racial, quem fica fora da população de referência e como a renda
declarada se distribui (heaping). `docs/PLANO_DE_ANALISE.md`, Blocos F e S; fichas em
`docs/studies/S1`, `docs/studies/S0` e `docs/studies/F`.

Populações do S1 (todas de 18+ anos; renda real a preços do trimestre de referência):

    P1  ocupados com VD4016 > 0                         renda do trabalho principal (REFERÊNCIA)
    P2  ocupados (sem rendimento entram com 0)          renda do trabalho principal
    P3  ocupados com VD4019 > 0                         renda de todos os trabalhos
    P4  todas as pessoas (não ocupados entram com 0)    renda do trabalho principal
    P5  todas as pessoas                                renda domiciliar per capita (VD5008; anual)

Hiato % = 100 × (média Branca / média do grupo − 1), relativo ao grupo de menor renda, como no
resto do Hub. Incerteza design-based (linearização Estrato/UPA, `src/inference/variancia.py`):
as médias de cada população são domínios de um mesmo universo (todas as pessoas 18+ do período),
e a diferença entre o hiato de Pk e o de P1 leva a covariância entre os dois (as amostras se
sobrepõem). Critério de "diferença grande" (fixado no plano antes de rodar): |Δ| > 10% do hiato
de P1 **e** |Δ| > 1,96 × EP(Δ).

Uso:
    python -m src.processing.sensibilidade_populacao
"""
from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.inference import variancia
from src.inference.saida import salvar_tabela
from src.processing.agregacoes_pnadc import DEFLATOR_PATH, OUTPUT_DIR, PARQUET_GLOB, REPO_ROOT
from src.utils import populacao as pop

ANUAL_GLOB = {1: str(REPO_ROOT / "data" / "raw" / "pnadc_anual_v2" / "visita1" / "parquet" / "ano=*" / "*.parquet"),
              5: str(REPO_ROOT / "data" / "raw" / "pnadc_anual_v2" / "visita5" / "parquet" / "ano=*" / "*.parquet")}
LIMIAR_RELATIVO = 0.10
Z95 = 1.959963984540054

POPULACOES = {
    "P1": "Ocupados 18+ com renda do trabalho principal > 0 (referência)",
    "P2": "Ocupados 18+ (sem rendimento = 0); renda do trabalho principal",
    "P3": "Ocupados 18+ com renda de todos os trabalhos > 0; renda de todos os trabalhos",
    "P4": "Todas as pessoas 18+ (não ocupados = 0); renda do trabalho principal",
    "P5": "Todas as pessoas 18+; renda domiciliar per capita (VD5008)",
}
COMPARACOES = [  # (rótulo, grupo de referência (maior renda), grupo comparado, filtro de sexo)
    ("Branca × Negra", "Branca", "Negra", None),
    ("Branca × Negra, homens", "Branca", "Negra", "Homem"),
    ("Branca × Negra, mulheres", "Branca", "Negra", "Mulher"),
    ("Branca × Indígena", "Branca", "Indígena", None),
]
RACA_SQL = """CASE m.V2010 WHEN '1' THEN 'Branca' WHEN '2' THEN 'Negra' WHEN '4' THEN 'Negra'
                           WHEN '5' THEN 'Indígena' WHEN '3' THEN 'Amarela' END"""
SEXO_SQL = "CASE m.V2007 WHEN '1' THEN 'Homem' WHEN '2' THEN 'Mulher' END"


# ----------------------------------------------------------------------------------------- #
# núcleo: hiatos de várias populações sobre um mesmo universo, com covariância entre eles
# ----------------------------------------------------------------------------------------- #
def hiatos_populacoes(micro: pd.DataFrame, populacoes: dict[str, tuple[np.ndarray, np.ndarray]],
                      grupo_a: np.ndarray, grupo_b: np.ndarray, referencia: str = "P1") -> pd.DataFrame:
    """Hiato % do grupo A sobre o grupo B em cada população, com EP design-based, e a diferença
    para a população de `referencia` com o EP da diferença (covariância incluída).

    micro: colunas `peso`, `upa`, `estrato` (universo = todas as linhas).
    populacoes: {nome: (máscara do domínio, y)} — y só precisa valer dentro do domínio.
    grupo_a / grupo_b: máscaras booleanas (ex.: Branca / Negra; já combinadas com sexo)."""
    w = micro["peso"].to_numpy(float)
    nomes, zs, linhas = [], [], []
    for nome, (dom, y) in populacoes.items():
        y = np.where(dom, np.asarray(y, float), 0.0)
        za, ma = variancia.influencia_media(y, w, dom & grupo_a)
        zb, mb = variancia.influencia_media(y, w, dom & grupo_b)
        if not (np.isfinite(ma) and np.isfinite(mb)) or mb <= 0:
            continue
        r = ma / mb
        zs.append((za - r * zb) / mb)  # z linearizado da razão A/B
        nomes.append(nome)
        linhas.append({"populacao": nome, "media_a": ma, "media_b": mb, "hiato_absoluto": ma - mb,
                       "hiato_percentual": 100 * (r - 1), "n_a": int((dom & grupo_a).sum()),
                       "n_b": int((dom & grupo_b).sum())})
    if not linhas:
        return pd.DataFrame()
    cov, _ = variancia.variancia_linearizada(np.column_stack(zs), micro["upa"].to_numpy(), micro["estrato"].to_numpy())
    cov = np.atleast_2d(cov) * 100**2
    df = pd.DataFrame(linhas)
    df["ep_hiato_percentual"] = np.sqrt(np.maximum(np.diag(cov), 0))
    if referencia in nomes:
        i = nomes.index(referencia)
        h_ref = df.loc[i, "hiato_percentual"]
        var_dif = np.diag(cov) + cov[i, i] - 2 * cov[:, i]
        df["dif_vs_ref_pp"] = df["hiato_percentual"] - h_ref
        df["ep_dif_vs_ref"] = np.sqrt(np.maximum(var_dif, 0))
        df["dif_relativa_vs_ref"] = df["dif_vs_ref_pp"] / h_ref
        df["diferenca_grande"] = ((df["dif_relativa_vs_ref"].abs() > LIMIAR_RELATIVO)
                                  & (df["dif_vs_ref_pp"].abs() > Z95 * df["ep_dif_vs_ref"]))
        df.loc[i, ["dif_vs_ref_pp", "ep_dif_vs_ref", "dif_relativa_vs_ref"]] = 0.0
        df.loc[i, "diferenca_grande"] = False
    df["ic_inferior"] = df["hiato_percentual"] - Z95 * df["ep_hiato_percentual"]
    df["ic_superior"] = df["hiato_percentual"] + Z95 * df["ep_hiato_percentual"]
    return df


# ----------------------------------------------------------------------------------------- #
# dados
# ----------------------------------------------------------------------------------------- #
def _micro_trimestre(con, ano: int, tri: int, glob: str = PARQUET_GLOB, deflator: str = DEFLATOR_PATH) -> pd.DataFrame:
    """Pessoas de 18+ do trimestre, direto do extrato (sem a CRIAR_BASE)."""
    return con.execute(f"""
        SELECT {RACA_SQL} AS raca, {SEXO_SQL} AS sexo, m.V2009 AS idade, m.VD3004 AS instrucao,
               SUBSTR(CAST(m.UF AS VARCHAR), 1, 1) AS regiao, m.V1028 AS peso, m.UPA AS upa, m.Estrato AS estrato,
               m.VD4001 AS forca, m.VD4002 AS ocupacao, m.VD4005 AS desalento,
               m.VD4016 * d.deflator_habitual AS renda_principal, m.VD4019 * d.deflator_habitual AS renda_todos,
               m.VD4016 AS renda_principal_nominal, {pop.REFERENCIA.sql('m')} AS em_p1
        FROM read_parquet('{glob}', hive_partitioning = 1) m
        LEFT JOIN read_parquet('{deflator}') d ON m.ano = d.ano AND m.trimestre = d.trimestre AND m.UF = d.UF
        WHERE m.ano = {ano} AND m.trimestre = {tri} AND m.V2009 >= {pop.IDADE_MINIMA_REFERENCIA}
    """).df()


def _populacoes_trimestrais(m: pd.DataFrame) -> dict:
    ocup = (m["ocupacao"] == pop.CODIGO_OCUPADO).to_numpy()
    rp = m["renda_principal"].to_numpy(float)
    rt = m["renda_todos"].to_numpy(float)
    p1 = m["em_p1"].fillna(False).to_numpy(bool) & np.isfinite(rp)
    return {
        "P1": (p1, rp),
        "P2": (ocup, np.where(np.isfinite(rp) & ocup, rp, 0.0)),
        "P3": (ocup & np.isfinite(rt) & (np.nan_to_num(rt) > 0), rt),
        "P4": (np.ones(len(m), bool), np.where(np.isfinite(rp) & ocup, rp, 0.0)),
    }


def _comparacoes(m: pd.DataFrame, pops: dict, chaves: dict) -> list[pd.DataFrame]:
    saida = []
    raca, sexo = m["raca"].to_numpy(object), m["sexo"].to_numpy(object)
    for rotulo, ga, gb, sx in COMPARACOES:
        filtro = np.ones(len(m), bool) if sx is None else (sexo == sx)
        df = hiatos_populacoes(m, pops, (raca == ga) & filtro, (raca == gb) & filtro)
        if df.empty:
            continue
        for k, v in chaves.items():
            df.insert(0, k, v)
        df.insert(len(chaves), "comparacao", rotulo)
        saida.append(df)
    return saida


def gerar_sensibilidade_trimestral(con) -> pd.DataFrame:
    trimestres = con.execute(f"SELECT DISTINCT ano, trimestre FROM read_parquet('{PARQUET_GLOB}', hive_partitioning=1) "
                             "ORDER BY 1, 2").fetchall()
    partes, comp, entrada = [], [], []
    for ano, tri in trimestres:
        m = _micro_trimestre(con, int(ano), int(tri))
        pops = _populacoes_trimestrais(m)
        partes += _comparacoes(m, pops, {"ano": int(ano), "trimestre": int(tri)})
        comp.append(_composicao(m, int(ano), int(tri)))
        print(f"{ano}T{tri}", flush=True)
    df = pd.concat(partes, ignore_index=True)
    df["descricao_populacao"] = df["populacao"].map(POPULACOES)
    salvar_tabela(df, OUTPUT_DIR / "sensibilidade_hiato_populacao.parquet", se_metodo=variancia.SE_METODO,
                  criterio_diferenca_grande={"relativo": LIMIAR_RELATIVO, "z": Z95})
    c = pd.concat(comp, ignore_index=True)
    salvar_tabela(c, OUTPUT_DIR / "composicao_populacao_referencia.parquet")
    return df


# ----------------------------------------------------------------------------------------- #
# S0.1 e F1: quem está em P1 e como a composição racial declarada mudou
# ----------------------------------------------------------------------------------------- #
def _composicao(m: pd.DataFrame, ano: int, tri: int) -> pd.DataFrame:
    ocup = m["ocupacao"] == pop.CODIGO_OCUPADO
    p1 = m["em_p1"].fillna(False).astype(bool) & m["renda_principal"].notna()
    conds = [p1, ocup, m["ocupacao"] == "2", m["desalento"] == "1"]
    cond = np.select([c.fillna(False).to_numpy(bool) for c in conds],
                     ["a_populacao_referencia", "b_ocupado_sem_renda_principal", "c_desocupado", "d1_fora_desalentado"],
                     default="d2_fora_da_forca_outros")
    d = m.assign(condicao=cond)
    linhas = []
    for (r, s), g in list(d.groupby(["raca", "sexo"])) + [((r, "Total"), g) for r, g in d.groupby("raca")]:
        tot = g["peso"].sum()
        for c_, gc in g.groupby("condicao"):
            linhas.append({"ano": ano, "trimestre": tri, "raca": r, "sexo": s, "condicao": c_,
                           "pct": 100 * gc["peso"].sum() / tot, "n": len(gc), "populacao_18mais": tot})
    return pd.DataFrame(linhas)


def gerar_composicao_racial_declarada(con) -> pd.DataFrame:
    """F1: participação de cada cor/raça declarada (5 categorias + Ignorado) nas pessoas 14+,
    18+ e na população de referência, por trimestre."""
    df = con.execute(f"""
        WITH b AS (
          SELECT m.ano, m.trimestre, CASE m.V2010 WHEN '1' THEN 'Branca' WHEN '2' THEN 'Preta' WHEN '3' THEN 'Amarela'
                 WHEN '4' THEN 'Parda' WHEN '5' THEN 'Indígena' ELSE 'Ignorado' END AS raca_cor,
                 m.V1028 AS peso, m.V2009 >= 18 AS adulto, COALESCE({pop.REFERENCIA.sql('m')}, FALSE) AS p1
          FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1) m WHERE m.V2009 >= 14)
        SELECT ano, trimestre, raca_cor, universo,
               100 * peso / SUM(peso) OVER (PARTITION BY ano, trimestre, universo) AS pct, n
        FROM (SELECT ano, trimestre, raca_cor, '14+' AS universo, SUM(peso) peso, COUNT(*) n FROM b GROUP BY ALL
              UNION ALL SELECT ano, trimestre, raca_cor, '18+', SUM(peso), COUNT(*) FROM b WHERE adulto GROUP BY ALL
              UNION ALL SELECT ano, trimestre, raca_cor, 'P1', SUM(peso), COUNT(*) FROM b WHERE p1 GROUP BY ALL)
        ORDER BY 1, 2, 4, 3""").df()
    salvar_tabela(df, OUTPUT_DIR / "composicao_racial_declarada.parquet")
    return df


# ----------------------------------------------------------------------------------------- #
# F4: heaping — quanto da renda declarada cai em valores redondos
# ----------------------------------------------------------------------------------------- #
def gerar_heaping(con) -> pd.DataFrame:
    df = con.execute(f"""
        SELECT m.ano, m.trimestre, {RACA_SQL} AS raca,
               100 * COALESCE(SUM(m.V1028) FILTER (WHERE m.VD4016 % 1000 = 0), 0) / SUM(m.V1028) AS pct_multiplo_1000,
               100 * COALESCE(SUM(m.V1028) FILTER (WHERE m.VD4016 % 500 = 0), 0) / SUM(m.V1028) AS pct_multiplo_500,
               100 * COALESCE(SUM(m.V1028) FILTER (WHERE m.VD4016 % 100 = 0), 0) / SUM(m.V1028) AS pct_multiplo_100,
               COUNT(*) AS n
        FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1) m
        WHERE {pop.REFERENCIA.sql('m')} AND m.V2010 IN ('1','2','4','5')
        GROUP BY ALL ORDER BY 1, 2, 3""").df()
    salvar_tabela(df, OUTPUT_DIR / "heaping_renda.parquet")
    return df


# ----------------------------------------------------------------------------------------- #
# S0.2: probabilidade de estar em P1, controlando idade, escolaridade, região e sexo
# ----------------------------------------------------------------------------------------- #
def efeitos_marginais_entrada(m: pd.DataFrame) -> pd.DataFrame:
    """Logit ponderado de Pr(P1 | 18+) com raça, sexo, faixa de idade, instrução e região;
    efeito marginal médio (EMM) de Negra e Indígena vs. Branca, contrafactual (cada pessoa como
    o grupo vs. como Branca, demais características mantidas).

    EP design-based: a variável linearizada do EMM combina o resíduo de g_i = p1_i − p0_i com a
    influência dos coeficientes (sanduíche do logit, ψ_i = H⁻¹ w_i x_i (y_i − p_i)) e vai para
    `variancia.variancia_linearizada` com Estrato/UPA — a mesma linearização do resto do Hub."""
    d = m[m["raca"].isin(["Branca", "Negra", "Indígena"]) & m["sexo"].notna()].copy()
    d["y"] = (d["em_p1"].fillna(False).astype(bool) & d["renda_principal"].notna()).astype(float)
    d["faixa"] = pd.cut(d["idade"], [17, 24, 29, 39, 49, 59, 200]).astype(str)
    X = pd.get_dummies(d[["raca", "sexo", "faixa", "instrucao", "regiao"]].astype(str), drop_first=False, dtype=float)
    referencias = ["raca_Branca", "sexo_Homem", X.filter(like="faixa_").columns[0],
                   X.filter(like="instrucao_").columns[0], X.filter(like="regiao_").columns[0]]
    X = X.drop(columns=[c for c in referencias if c in X])
    X = X.loc[:, X.std() > 0]  # ex.: sexo constante quando o modelo roda só para um sexo
    X = sm.add_constant(X)
    w = d["peso"].to_numpy(float)
    y = d["y"].to_numpy(float)
    beta = sm.GLM(y, X, family=sm.families.Binomial(), var_weights=w / w.mean()).fit().params.to_numpy()
    Xa = X.to_numpy(float)
    p = 1 / (1 + np.exp(-Xa @ beta))
    H = (Xa * (w * p * (1 - p))[:, None]).T @ Xa
    psi = np.linalg.solve(H, (Xa * (w * (y - p))[:, None]).T).T  # n × k
    W = w.sum()
    linhas = []
    for grupo in ("Negra", "Indígena"):
        col = f"raca_{grupo}"
        if col not in X:
            continue
        X1, X0 = X.copy(), X.copy()
        for c in ("raca_Negra", "raca_Indígena"):
            if c in X1:
                X1[c] = X0[c] = 0.0
        X1[col] = 1.0
        x1, x0 = X1.to_numpy(float), X0.to_numpy(float)
        p1, p0 = 1 / (1 + np.exp(-x1 @ beta)), 1 / (1 + np.exp(-x0 @ beta))
        g = p1 - p0
        ame = float(np.sum(w * g) / W)
        dg = (w[:, None] * (x1 * (p1 * (1 - p1))[:, None] - x0 * (p0 * (1 - p0))[:, None])).sum(axis=0) / W
        z = w * (g - ame) / W + psi @ dg
        var, _ = variancia.variancia_linearizada(z, d["upa"].to_numpy(), d["estrato"].to_numpy())
        ep = float(np.sqrt(max(var, 0.0)))
        sel_g, sel_b = (d["raca"] == grupo).to_numpy(), (d["raca"] == "Branca").to_numpy()
        bruta = np.average(y[sel_g], weights=w[sel_g]) - np.average(y[sel_b], weights=w[sel_b])
        linhas.append({"grupo": grupo, "diferenca_bruta_pp": 100 * bruta, "efeito_marginal_pp": 100 * ame,
                       "ep_pp": 100 * ep, "ic_inferior": 100 * (ame - Z95 * ep), "ic_superior": 100 * (ame + Z95 * ep),
                       "n": len(d), "n_grupo": int(sel_g.sum())})
    return pd.DataFrame(linhas)


def gerar_selecao_entrada(con, janelas: dict[str, list[tuple[int, int]]]) -> pd.DataFrame:
    partes = []
    for nome, tris in janelas.items():
        m = pd.concat([_micro_trimestre(con, a, t) for a, t in tris], ignore_index=True)
        for sexo in (None, "Homem", "Mulher"):
            sub = m if sexo is None else m[m["sexo"] == sexo]
            r = efeitos_marginais_entrada(sub)
            r.insert(0, "sexo", sexo or "Total")
            r.insert(0, "janela", nome)
            partes.append(r)
    df = pd.concat(partes, ignore_index=True)
    salvar_tabela(df, OUTPUT_DIR / "selecao_entrada_populacao_referencia.parquet",
                  se_metodo="logit_sanduiche_linearizacao_estrato_upa")
    return df


# ----------------------------------------------------------------------------------------- #
# P5 (anual): renda domiciliar per capita, comparada com P1 no MESMO extrato anual
# ----------------------------------------------------------------------------------------- #
def gerar_sensibilidade_anual(con) -> pd.DataFrame:
    partes = []
    for visita, glob in ANUAL_GLOB.items():
        anos = [r[0] for r in con.execute(f"SELECT DISTINCT ano FROM read_parquet('{glob}', hive_partitioning=1) ORDER BY 1").fetchall()]
        for ano in anos:
            m = con.execute(f"""
                SELECT {RACA_SQL} AS raca, {SEXO_SQL} AS sexo, m.V1032 AS peso, m.UPA AS upa, m.Estrato AS estrato,
                       m.VD4002 AS ocupacao, m.VD4016 AS renda_principal, m.VD5008 AS renda_dom_pc,
                       {pop.REFERENCIA.sql('m')} AS em_p1
                FROM read_parquet('{glob}', hive_partitioning = 1) m
                WHERE m.ano = {ano} AND m.V2009 >= 18""").df()
            rp = m["renda_principal"].to_numpy(float)
            pops = {"P1": (m["em_p1"].fillna(False).to_numpy(bool), rp),
                    "P5": (np.isfinite(m["renda_dom_pc"].to_numpy(float)), m["renda_dom_pc"].to_numpy(float))}
            partes += _comparacoes(m, pops, {"ano": int(ano), "visita": visita})
            print(f"anual {ano} (visita {visita})", flush=True)
    df = pd.concat(partes, ignore_index=True)
    df["descricao_populacao"] = df["populacao"].map(POPULACOES)
    salvar_tabela(df, OUTPUT_DIR / "sensibilidade_hiato_p5_anual.parquet", se_metodo=variancia.SE_METODO,
                  insumos="anual_v2", nota_renda="Valores NOMINAIS do ano (o hiato % não depende do deflator dentro do ano)",
                  criterio_diferenca_grande={"relativo": LIMIAR_RELATIVO, "z": Z95})
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--so", nargs="*", default=None, help="trimestral, anual, composicao, heaping, selecao")
    args = parser.parse_args()
    fazer = set(args.so or ["trimestral", "anual", "composicao", "heaping", "selecao"])
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    if "trimestral" in fazer:
        gerar_sensibilidade_trimestral(con)
    if "anual" in fazer:
        gerar_sensibilidade_anual(con)
    if "composicao" in fazer:
        gerar_composicao_racial_declarada(con)
    if "heaping" in fazer:
        gerar_heaping(con)
    if "selecao" in fazer:
        gerar_selecao_entrada(con, {"2012": [(2012, t) for t in (1, 2, 3, 4)],
                                    "2025T3-2026T2": [(2025, 3), (2025, 4), (2026, 1), (2026, 2)]})


if __name__ == "__main__":
    main()
