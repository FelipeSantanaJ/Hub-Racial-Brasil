"""Onda 1 (pendências) — Bloco S: S0.3, S1.3, S1.4 e S1.5 (`docs/PLANO_DE_ANALISE.md`, Bloco S; fichas em
`docs/studies/S0.3`, `S1.3`, `S1.4`, `S1.5`). Complementa `sensibilidade_populacao.py` (S0.1, S0.2, S1.1, S1.2).

- **S0.3** — perfis de quem fica fora de P1 (escolaridade, idade, criança de 0–5 no domicílio, chefia,
  frequência escolar, região), por raça e raça × sexo e condição, com IC design-based.
- **S1.3** — limites do hiato (média e mediana) sob suposições explícitas sobre a renda potencial de quem está
  fora de P1 (sem suposição com suporte limitado, seleção positiva, piso, aparamento à la Lee), com IC de
  Imbens–Manski por bootstrap Rao-Wu. Sem Heckman (não há restrição de exclusão crível; ver a ficha).
- **S1.4** — renda do trabalho por adulto = Pr(P1) × horas × renda por hora; o hiato em log-pontos é a soma
  exata das três diferenças, com covariância por linearização.
- **S1.5** — séries do S0.1, S0.2 (por ano) e do Δ do S1, com médias por episódio e EP de Newey-West.

Uso:
    python -m src.processing.bloco_s --so s03 s13 s14 s15
"""
from __future__ import annotations

import argparse

import duckdb
import numpy as np
import pandas as pd

from src.inference import precisao, variancia
from src.inference.saida import salvar_tabela
from src.processing.agregacoes_pnadc import DEFLATOR_PATH, OUTPUT_DIR, PARQUET_GLOB
from src.processing.sensibilidade_populacao import RACA_SQL, SEXO_SQL, Z95
from src.utils import populacao as pop

JANELAS = {"2012": [(2012, t) for t in (1, 2, 3, 4)],
           "2025T3-2026T2": [(2025, 3), (2025, 4), (2026, 1), (2026, 2)]}
CONDICOES = {"a_populacao_referencia": "P1 (ocupado com renda)", "b_ocupado_sem_renda_principal": "Ocupado sem renda",
             "c_desocupado": "Desocupado", "d1_fora_desalentado": "Fora da força, desalentado",
             "d2_fora_da_forca_outros": "Fora da força, outros"}
INDICADORES_S03 = {
    "pct_ate_fundamental_incompleto": "Sem instrução ou fundamental incompleto (%)",
    "pct_superior_completo": "Superior completo (%)",
    "idade_media": "Idade média (anos)",
    "pct_crianca_0a5_no_domicilio": "Há criança de 0–5 anos no domicílio (%)",
    "pct_responsavel_domicilio": "Responsável pelo domicílio (%)",
    "pct_frequenta_escola": "Frequenta escola ou faculdade (%)",
    "pct_nordeste": "Mora no Nordeste (%)",
}


# ----------------------------------------------------------------------------------------- #
# dados
# ----------------------------------------------------------------------------------------- #
def micro_s(con, ano: int, tri: int) -> pd.DataFrame:
    """Pessoas de 18+ do trimestre com o que os estudos S precisam; criança de 0–5 contada no domicílio
    inteiro (todas as idades) pela chave UPA + V1008 + V1014."""
    return con.execute(f"""
        WITH t AS (
          SELECT m.*, COUNT(*) FILTER (WHERE m.V2009 <= 5) OVER (PARTITION BY m.UPA, m.V1008, m.V1014) AS n_0a5
          FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1) m
          WHERE m.ano = {ano} AND m.trimestre = {tri})
        SELECT {ano} AS ano, {tri} AS trimestre, {RACA_SQL} AS raca, {SEXO_SQL} AS sexo, m.V2009 AS idade,
               m.VD3004 AS instrucao, SUBSTR(CAST(m.UF AS VARCHAR), 1, 1) AS regiao, m.V2005 AS condicao_dom,
               m.V3002 AS frequenta, m.V1028 AS peso, m.UPA AS upa, m.Estrato AS estrato,
               m.VD4001 AS forca, m.VD4002 AS ocupacao, m.VD4005 AS desalento, m.V4039 AS horas,
               m.VD4016 * d.deflator_habitual AS renda_principal, {pop.REFERENCIA.sql('m')} AS em_p1, m.n_0a5
        FROM t m
        LEFT JOIN read_parquet('{DEFLATOR_PATH}') d ON m.ano = d.ano AND m.trimestre = d.trimestre AND m.UF = d.UF
        WHERE m.V2009 >= {pop.IDADE_MINIMA_REFERENCIA}
    """).df()


def condicao(m: pd.DataFrame) -> np.ndarray:
    """Mesma classificação do S0.1 (`sensibilidade_populacao._composicao`)."""
    ocup = m["ocupacao"] == pop.CODIGO_OCUPADO
    p1 = m["em_p1"].fillna(False).astype(bool) & m["renda_principal"].notna()
    conds = [p1, ocup, m["ocupacao"] == "2", m["desalento"] == "1"]
    return np.select([c.fillna(False).to_numpy(bool) for c in conds], list(CONDICOES)[:4], default=list(CONDICOES)[4])


def janela(con, tris) -> pd.DataFrame:
    return pd.concat([micro_s(con, a, t) for a, t in tris], ignore_index=True)


# ----------------------------------------------------------------------------------------- #
# médias de muitos domínios de uma vez (linearização em lote)
# ----------------------------------------------------------------------------------------- #
def medias_dominios(y: np.ndarray, w: np.ndarray, upa, estrato, dominios: dict[str, np.ndarray],
                    lote: int = 24) -> pd.DataFrame:
    """Média ponderada de `y` em cada domínio, com EP por linearização (domínio sobre o universo
    inteiro passado). Várias colunas de z por chamada, para fatorar UPA/estrato menos vezes."""
    nomes, zs, linhas = list(dominios), [], []
    for nome in nomes:
        d = dominios[nome] & np.isfinite(y)
        z, media = variancia.influencia_media(np.where(d, y, 0.0), w, d)
        zs.append(z)
        linhas.append({"dominio": nome, "estimativa": media, "n": int(d.sum())})
    eps = []
    for i in range(0, len(zs), lote):
        cov, _ = variancia.variancia_linearizada(np.column_stack(zs[i:i + lote]), upa, estrato)
        eps += list(np.sqrt(np.maximum(np.diag(np.atleast_2d(cov)), 0.0)))
    out = pd.DataFrame(linhas)
    out["ep"] = eps
    return out


# ----------------------------------------------------------------------------------------- #
# S0.3 — perfis de quem está fora de P1
# ----------------------------------------------------------------------------------------- #
def indicadores_s03(m: pd.DataFrame) -> dict[str, np.ndarray]:
    instr = m["instrucao"].astype(str)
    inst_ok = m["instrucao"].notna().to_numpy()
    um = lambda c: np.where(inst_ok, c.to_numpy(float), np.nan)  # noqa: E731
    return {
        "pct_ate_fundamental_incompleto": 100 * um(instr.isin(["1", "2"])),
        "pct_superior_completo": 100 * um(instr == "7"),
        "idade_media": m["idade"].to_numpy(float),
        "pct_crianca_0a5_no_domicilio": 100 * (m["n_0a5"].to_numpy(float) > 0),
        "pct_responsavel_domicilio": 100 * (m["condicao_dom"] == "01").to_numpy(float),
        "pct_frequenta_escola": 100 * (m["frequenta"] == "1").to_numpy(float),
        "pct_nordeste": 100 * (m["regiao"] == "2").to_numpy(float),
    }


def perfis_s03(m: pd.DataFrame, rotulo_janela: str) -> pd.DataFrame:
    cond = condicao(m)
    raca, sexo = m["raca"].to_numpy(object), m["sexo"].to_numpy(object)
    w, upa, est = m["peso"].to_numpy(float), m["upa"].to_numpy(), m["estrato"].to_numpy()
    grupos = {(r, "Total"): raca == r for r in ("Branca", "Negra", "Indígena")}
    grupos |= {(r, s): (raca == r) & (sexo == s) for r in ("Branca", "Negra", "Indígena") for s in ("Homem", "Mulher")}
    fora = cond != "a_populacao_referencia"
    conds = {c: cond == c for c in CONDICOES} | {"z_fora_de_p1": fora}
    linhas = []
    for ind, y in indicadores_s03(m).items():
        doms = {(g, s, c): gm & cm for (g, s), gm in grupos.items() for c, cm in conds.items()}
        res = medias_dominios(y, w, upa, est, {k: v for k, v in doms.items()})
        for (g, s, c), (_, r) in zip(doms, res.iterrows()):
            linhas.append({"janela": rotulo_janela, "indicador": ind, "condicao": c, "raca": g, "sexo": s,
                           "estimativa": r["estimativa"], "ep": r["ep"], "n": r["n"]})
        # diferenças Negra − Branca e Indígena − Branca na mesma condição e sexo
        for s in ("Total", "Homem", "Mulher"):
            for c, cm in conds.items():
                for alvo in ("Negra", "Indígena"):
                    d = variancia.diferenca_medias_design(np.where(np.isfinite(y), y, 0.0), w, upa, est,
                                                          grupos[(alvo, s)] & cm & np.isfinite(y),
                                                          grupos[("Branca", s)] & cm & np.isfinite(y))
                    linhas.append({"janela": rotulo_janela, "indicador": ind, "condicao": c,
                                   "raca": f"{alvo} − Branca", "sexo": s, "estimativa": d["diferenca"],
                                   "ep": d["ep_diferenca"], "n": min(d["n_a"], d["n_b"])})
    df = pd.DataFrame(linhas)
    df["ic_inferior"] = df["estimativa"] - Z95 * df["ep"]
    df["ic_superior"] = df["estimativa"] + Z95 * df["ep"]
    nivel = ~df["raca"].str.contains("−")
    with np.errstate(invalid="ignore", divide="ignore"):
        cv = np.where(nivel, df["ep"] / df["estimativa"].abs(), np.nan)
    df["cv"] = cv
    df["publicavel"] = np.where(nivel, precisao.publicavel(df["n"], cv), df["n"] >= precisao.N_MINIMO)
    df["descricao_indicador"] = df["indicador"].map(INDICADORES_S03)
    df["descricao_condicao"] = df["condicao"].map(CONDICOES | {"z_fora_de_p1": "Fora de P1 (todas as condições)"})
    return df


def gerar_s03(con) -> pd.DataFrame:
    partes = []
    for nome, tris in JANELAS.items():
        partes.append(perfis_s03(janela(con, tris), nome))
        print(f"S0.3 {nome}", flush=True)
    df = pd.concat(partes, ignore_index=True)
    salvar_tabela(df, OUTPUT_DIR / "s03_perfil_fora_populacao_referencia.parquet", se_metodo=variancia.SE_METODO,
                  regra_supressao=precisao.REGRA_SUPRESSAO,
                  nota="Diferenças (raca com '−'): publicavel = n ≥ 30 nos dois grupos (CV não se aplica a diferenças)")
    return df


# ----------------------------------------------------------------------------------------- #
# S1.3 — limites do hiato sob suposições explícitas
# ----------------------------------------------------------------------------------------- #
COMPARACOES_S1 = [("Branca × Negra", "Negra", None), ("Branca × Negra, homens", "Negra", "Homem"),
                  ("Branca × Negra, mulheres", "Negra", "Mulher"), ("Branca × Indígena", "Indígena", None)]


def quantil_ord(v_ord: np.ndarray, cum: np.ndarray, q: float) -> float:
    """Quantil q de valores já ordenados, com `cum` = participação acumulada (termina em 1).
    Mesma convenção de `pnadc_core.quantil_ponderado` (primeiro valor com F ≥ q)."""
    if q <= 0:
        return 0.0
    return float(v_ord[min(np.searchsorted(cum, min(q, 1.0) - 1e-12), len(v_ord) - 1)])


def media_aparada(v_ord: np.ndarray, w_ord: np.ndarray, fracao: float, lado: str) -> float:
    """Média ponderada depois de retirar `fracao` do peso pelo `lado` ("topo" ou "base"), com
    peso parcial na observação de fronteira (aparamento exato, também com heaping)."""
    if fracao <= 0:
        return float(np.average(v_ord, weights=w_ord))
    v, w = (v_ord, w_ord) if lado == "topo" else (v_ord[::-1], w_ord[::-1])
    manter = (1 - fracao) * w.sum()
    acum = np.cumsum(w)
    w_m = np.clip(manter - (acum - w), 0.0, w)  # quanto de cada observação cabe no que se mantém
    return float(np.sum(w_m * v) / np.sum(w_m))


def limites_grupo(p: float, v_ord: np.ndarray, w_ord: np.ndarray, y_max: float) -> dict[str, tuple[float, float]]:
    """Limites (L, U) da média e da mediana da renda potencial de todo o grupo, por suposição."""
    cum = np.cumsum(w_ord) / w_ord.sum()
    m = float(np.sum(v_ord * w_ord) / w_ord.sum())
    p10 = quantil_ord(v_ord, cum, 0.10)
    med = quantil_ord(v_ord, cum, 0.50)
    if p > 0.5:
        med_l, med_u = quantil_ord(v_ord, cum, 1 - 0.5 / p), quantil_ord(v_ord, cum, 0.5 / p)
    else:
        med_l, med_u = 0.0, y_max
    return {"media|S-a sem suposição (suporte [0, P99])": (p * m, p * m + (1 - p) * y_max),
            "media|S-b seleção positiva": (p * m, m),
            "media|S-c seleção positiva com piso no P10": (p * m + (1 - p) * p10, m),
            "mediana|S-a sem suposição (suporte [0, P99])": (med_l, med_u),
            "mediana|S-b seleção positiva": (med_l, med)}


def limites_hiato(lb: tuple[float, float], lg: tuple[float, float]) -> tuple[float, float]:
    """Hiato % Branca/grupo − 1 a partir dos limites de cada grupo."""
    lo = 100 * (lb[0] / lg[1] - 1) if lg[1] > 0 else -100.0
    hi = 100 * (lb[1] / lg[0] - 1) if lg[0] > 0 else np.inf
    return lo, hi


def limites_lee(p_b: float, p_g: float, vb, wb, vg, wg) -> tuple[float, float]:
    """S-d: apara o grupo de maior participação em (p_maior − p_menor)/p_maior."""
    mb, mg = np.average(vb, weights=wb), np.average(vg, weights=wg)
    if p_b >= p_g:
        q = (p_b - p_g) / p_b
        return 100 * (media_aparada(vb, wb, q, "topo") / mg - 1), 100 * (media_aparada(vb, wb, q, "base") / mg - 1)
    q = (p_g - p_b) / p_g
    return 100 * (mb / media_aparada(vg, wg, q, "base") - 1), 100 * (mb / media_aparada(vg, wg, q, "topo") - 1)


def c_imbens_manski(delta: float, sigma: float, nivel: float = 0.95) -> float:
    """c tal que Φ(c + Δ/σ) − Φ(−c) = nível (Imbens & Manski 2004 — *a confirmar*)."""
    from scipy import optimize, stats
    if not np.isfinite(delta) or sigma <= 0:
        return float(stats.norm.ppf(nivel))
    f = lambda c: stats.norm.cdf(c + delta / sigma) - stats.norm.cdf(-c) - nivel  # noqa: E731
    return float(optimize.brentq(f, 0.0, 10.0))


def _limites_todas(p: dict, ords: dict, y_max: float, g: str) -> dict[str, tuple[float, float]]:
    lb = limites_grupo(p["Branca"], *ords["Branca"], y_max)
    lg = limites_grupo(p[g], *ords[g], y_max)
    out = {k: limites_hiato(lb[k], lg[k]) for k in lb}
    out["media|S-d aparamento à la Lee"] = limites_lee(p["Branca"], p[g], *ords["Branca"], *ords[g])
    return out


def limites_s13(m: pd.DataFrame, rotulo_janela: str, n_boot: int = 200, seed: int = 0) -> pd.DataFrame:
    from src.processing.bloco_a import multiplicadores_rao_wu
    w, raca, sexo = m["peso"].to_numpy(float), m["raca"].to_numpy(object), m["sexo"].to_numpy(object)
    y = m["renda_principal"].to_numpy(float)
    p1 = m["em_p1"].fillna(False).to_numpy(bool) & np.isfinite(y)
    y_max = pnadc_core_quantil(y[p1], w[p1], 0.99)
    upa_cod, mult = multiplicadores_rao_wu(m["upa"].to_numpy(), m["estrato"].to_numpy(), n_boot, seed)
    linhas = []
    for rotulo, g, sx in COMPARACOES_S1:
        filtro = np.ones(len(m), bool) if sx is None else (sexo == sx)
        doms = {r: (raca == r) & filtro for r in ("Branca", g)}
        idx = {r: np.flatnonzero(d & p1) for r, d in doms.items()}
        idx = {r: i[np.argsort(y[i], kind="stable")] for r, i in idx.items()}

        def calcula(wv):
            pv = {r: wv[idx[r]].sum() / wv[d].sum() for r, d in doms.items()}
            ords = {r: (y[idx[r]], wv[idx[r]]) for r in doms}
            return pv, _limites_todas(pv, ords, y_max, g)

        p_est, lim = calcula(w)
        reps = {k: [] for k in lim}
        for b in range(n_boot):
            _, lb = calcula(w * mult[upa_cod, b])
            for k, v in lb.items():
                reps[k].append(v)
        mb, mg = (np.average(y[idx[r]], weights=w[idx[r]]) for r in ("Branca", g))
        for k, (lo, hi) in lim.items():
            estat, sup = k.split("|")
            r_ = np.array(reps[k], float)
            s_lo = float(np.nanstd(r_[:, 0], ddof=1))
            s_hi = float(np.nanstd(r_[:, 1], ddof=1)) if np.isfinite(hi) else np.nan
            c = c_imbens_manski(hi - lo, max(s_lo, s_hi if np.isfinite(s_hi) else 0.0))
            linhas.append({"janela": rotulo_janela, "comparacao": rotulo, "estatistica": estat, "suposicao": sup,
                           "p_branca": 100 * p_est["Branca"], "p_grupo": 100 * p_est[g],
                           "hiato_p1": 100 * (mb / mg - 1) if estat == "media" else 100 * (
                               pnadc_core_quantil(y[idx["Branca"]], w[idx["Branca"]], 0.5)
                               / pnadc_core_quantil(y[idx[g]], w[idx[g]], 0.5) - 1),
                           "limite_inferior": lo, "limite_superior": hi, "ep_inferior": s_lo, "ep_superior": s_hi,
                           "c_imbens_manski": c, "ic_inferior": lo - c * s_lo,
                           "ic_superior": hi + c * s_hi if np.isfinite(hi) else np.inf,
                           "sinal_identificado": bool(lo - c * s_lo > 0),
                           "n_branca_p1": len(idx["Branca"]), "n_grupo_p1": len(idx[g]), "y_max_p99": y_max})
    return pd.DataFrame(linhas)


def pnadc_core_quantil(y, w, q) -> float:
    from src.utils import pnadc_core
    return float(pnadc_core.quantil_ponderado(np.asarray(y, float), np.asarray(w, float), q))


def gerar_s13(con, n_boot: int = 200) -> pd.DataFrame:
    partes = []
    for nome, tris in JANELAS.items():
        partes.append(limites_s13(janela(con, tris), nome, n_boot))
        print(f"S1.3 {nome}", flush=True)
    df = pd.concat(partes, ignore_index=True)
    salvar_tabela(df, OUTPUT_DIR / "s13_limites_hiato.parquet", se_metodo=f"bootstrap_rao_wu_estrato_upa_{n_boot}",
                  ic="Imbens-Manski sobre os limites (a confirmar: Imbens & Manski 2004)",
                  nota="Renda real VD4016 (deflator habitual); 4 visitas empilhadas por janela; y_max = P99 nacional de P1")
    return df


# ----------------------------------------------------------------------------------------- #
# S1.4 — margem extensiva × intensiva × renda por hora
# ----------------------------------------------------------------------------------------- #
TERMOS_S14 = ["ln_pr_p1", "ln_horas", "ln_renda_hora", "ln_renda_por_adulto"]


def _zs_log_grupo(w, dom, p1, h, y):
    """z linearizados de ln Pr(P1), ln horas médias, ln renda por hora e ln renda por adulto no grupo."""
    T = np.sum(w * dom)
    P = np.sum(w * dom * p1)
    H = np.sum(w * dom * p1 * h)
    Y = np.sum(w * dom * p1 * y)
    zT, zP, zH, zY = w * dom / T, w * dom * p1 / P, w * dom * p1 * h / H, w * dom * p1 * y / Y
    valores = {"ln_pr_p1": np.log(P / T), "ln_horas": np.log(H / P), "ln_renda_hora": np.log(Y / H),
               "ln_renda_por_adulto": np.log(Y / T)}
    zs = {"ln_pr_p1": zP - zT, "ln_horas": zH - zP, "ln_renda_hora": zY - zH, "ln_renda_por_adulto": zY - zT}
    niveis = {"pr_p1_pct": 100 * P / T, "horas_semanais": H / P, "renda_hora": Y / H / 4.345, "renda_por_adulto": Y / T}
    return valores, zs, niveis


def margens_s14(m: pd.DataFrame, ano: int, tri: int) -> list[dict]:
    w = m["peso"].to_numpy(float)
    y = np.nan_to_num(m["renda_principal"].to_numpy(float))
    h = np.nan_to_num(m["horas"].to_numpy(float))
    p1 = (m["em_p1"].fillna(False).to_numpy(bool) & (y > 0) & (h > 0)).astype(float)
    raca, sexo = m["raca"].to_numpy(object), m["sexo"].to_numpy(object)
    upa, est = m["upa"].to_numpy(), m["estrato"].to_numpy()
    linhas = []
    for rotulo, g, sx in COMPARACOES_S1:
        filtro = np.ones(len(m), bool) if sx is None else (sexo == sx)
        if not ((raca == g) & filtro & (p1 > 0)).any() or not ((raca == "Branca") & filtro & (p1 > 0)).any():
            continue
        vb, zb, nb = _zs_log_grupo(w, ((raca == "Branca") & filtro).astype(float), p1, h, y)
        vg, zg, ng = _zs_log_grupo(w, ((raca == g) & filtro).astype(float), p1, h, y)
        Z = np.column_stack([zb[k] - zg[k] for k in TERMOS_S14])
        cov, _ = variancia.variancia_linearizada(Z, upa, est)
        ep = np.sqrt(np.maximum(np.diag(cov), 0.0))
        total = vb["ln_renda_por_adulto"] - vg["ln_renda_por_adulto"]
        linha = {"ano": ano, "trimestre": tri, "comparacao": rotulo,
                 "n_branca_p1": int(((raca == "Branca") & filtro & (p1 > 0)).sum()),
                 "n_grupo_p1": int(((raca == g) & filtro & (p1 > 0)).sum())}
        for i, k in enumerate(TERMOS_S14):
            d = vb[k] - vg[k]
            linha[k] = d
            linha[f"{k}_ic_inferior"], linha[f"{k}_ic_superior"] = d - Z95 * ep[i], d + Z95 * ep[i]
            if k != "ln_renda_por_adulto":
                linha[f"{k}_pct_do_total"] = 100 * d / total
        for k in nb:
            linha[f"{k}_branca"], linha[f"{k}_grupo"] = nb[k], ng[k]
        linha["hiato_renda_por_adulto_pct"] = 100 * (np.exp(total) - 1)
        linha["mesmo_sinal"] = bool(len({np.sign(linha[k]) for k in TERMOS_S14[:3]}) == 1)
        linhas.append(linha)
    return linhas


def gerar_s14(con) -> pd.DataFrame:
    tris = [(int(a), int(t)) for a, t in con.execute(
        f"SELECT DISTINCT ano, trimestre FROM read_parquet('{PARQUET_GLOB}', hive_partitioning=1) ORDER BY 1, 2").fetchall()]
    linhas = []
    for a, t in tris:
        linhas += margens_s14(micro_s(con, a, t), a, t)
        print(f"S1.4 {a}T{t}", flush=True)
    df = pd.DataFrame(linhas)
    salvar_tabela(df, OUTPUT_DIR / "s14_margens_intensiva_extensiva.parquet", se_metodo=variancia.SE_METODO,
                  nota="Identidade: ln_renda_por_adulto = ln_pr_p1 + ln_horas + ln_renda_hora (diferença Branca − grupo)")
    return df


# ----------------------------------------------------------------------------------------- #
# S1.5 — a seleção mudou no tempo?
# ----------------------------------------------------------------------------------------- #
def gerar_s15(con) -> tuple[pd.DataFrame, pd.DataFrame]:
    from scipy import stats

    from src.inference import multiplicidade, tendencia
    from src.processing.sensibilidade_populacao import _micro_trimestre, efeitos_marginais_entrada
    series = []
    # (a) diferença de participação em P1 (S0.1)
    comp = pd.read_parquet(OUTPUT_DIR / "composicao_populacao_referencia.parquet")
    p1 = comp[comp["condicao"] == "a_populacao_referencia"].pivot_table(
        index=["ano", "trimestre", "sexo"], columns="raca", values="pct").reset_index()
    for g in ("Negra", "Indígena"):
        for s in ("Total", "Homem", "Mulher"):
            if g == "Indígena" and s != "Total":
                continue
            x = p1[p1["sexo"] == s]
            series.append(pd.DataFrame({"serie": "a_dif_participacao_p1_pp", "comparacao": f"Branca × {g}", "sexo": s,
                                        "ano": x["ano"], "trimestre": x["trimestre"], "valor": x["Branca"] - x[g]}))
    # (b) Δ do S1: hiato P4 − hiato P1 e P2 − P1
    sens = pd.read_parquet(OUTPUT_DIR / "sensibilidade_hiato_populacao.parquet")
    for popn in ("P4", "P2"):
        x = sens[sens["populacao"] == popn]
        for comp_, cx in x.groupby("comparacao"):
            sexo = "Homem" if "homens" in comp_ else "Mulher" if "mulheres" in comp_ else "Total"
            series.append(pd.DataFrame({"serie": f"b_delta_hiato_{popn}_menos_P1_pp",
                                        "comparacao": comp_.split(",")[0], "sexo": sexo, "ano": cx["ano"],
                                        "trimestre": cx["trimestre"], "valor": cx["dif_vs_ref_pp"]}))
    # (c) EMM ajustado por ano
    anos = [int(a) for (a,) in con.execute(
        f"SELECT DISTINCT ano FROM read_parquet('{PARQUET_GLOB}', hive_partitioning=1) ORDER BY 1").fetchall()]
    emm = []
    for a in anos:
        tris = [int(t) for (t,) in con.execute(f"SELECT DISTINCT trimestre FROM read_parquet('{PARQUET_GLOB}', "
                                               f"hive_partitioning=1) WHERE ano = {a} ORDER BY 1").fetchall()]
        mm = pd.concat([_micro_trimestre(con, a, t) for t in tris], ignore_index=True)
        for s in (None, "Homem", "Mulher"):
            r = efeitos_marginais_entrada(mm if s is None else mm[mm["sexo"] == s])
            r.insert(0, "sexo", s or "Total")
            r.insert(0, "n_trimestres", len(tris))
            r.insert(0, "ano", a)
            emm.append(r)
        print(f"S1.5 EMM {a}", flush=True)
    emm = pd.concat(emm, ignore_index=True)
    for _, x in emm.groupby(["grupo", "sexo"]):
        g, s = x["grupo"].iloc[0], x["sexo"].iloc[0]
        series.append(pd.DataFrame({"serie": "c_emm_pr_p1_grupo_menos_branca_pp", "comparacao": f"Branca × {g}",
                                    "sexo": s, "ano": x["ano"], "trimestre": 1, "valor": x["efeito_marginal_pp"],
                                    "ic_inferior": x["ic_inferior"], "ic_superior": x["ic_superior"]}))
    serie = pd.concat(series, ignore_index=True)
    # episódios com HAC
    eps = []
    for (sr, cmp_, sx), x in serie.groupby(["serie", "comparacao", "sexo"]):
        x = x.sort_values(["ano", "trimestre"])
        anual = sr.startswith("c_")
        e = tendencia.medias_episodios_hac(x["ano"], x["trimestre"], x["valor"])
        e.insert(0, "sexo", sx)
        e.insert(0, "comparacao", cmp_)
        e.insert(0, "serie", sr)
        e.insert(3, "frequencia", "anual" if anual else "trimestral")
        # EMD com 80% de poder e 5% bilateral, na mesma t de Student do IC
        e["emd_80pct"] = (stats.t.ppf(0.975, e["gl_ewc"]) + stats.t.ppf(0.80, e["gl_ewc"])) * e["ep_dif"]
        eps.append(e)
    eps = pd.concat(eps, ignore_index=True)
    eps = multiplicidade.adicionar_fdr(eps, ["serie", "comparacao", "sexo"], coluna_p="p_valor_dif")
    salvar_tabela(serie, OUTPUT_DIR / "s15_selecao_no_tempo.parquet",
                  nota="Séries: (a) S0.1, (b) S1.1, (c) S0.2 por ano (4 trimestres; 2026 = 2)")
    salvar_tabela(eps, OUTPUT_DIR / "s15_selecao_episodios.parquet", se_metodo=tendencia.METODO,
                  familia_fdr=["serie", "comparacao", "sexo"], episodios={k: [f"{a}T{t}" for a, t in v]
                                                                         for k, v in tendencia.EPISODIOS_PADRAO.items()})
    return serie, eps


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--so", nargs="*", default=None, help="s03 s13 s14 s15")
    fazer = set(parser.parse_args().so or ["s03", "s13", "s14", "s15"])
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    if "s03" in fazer:
        gerar_s03(con)
    if "s13" in fazer:
        gerar_s13(con)
    if "s14" in fazer:
        gerar_s14(con)
    if "s15" in fazer:
        gerar_s15(con)


if __name__ == "__main__":
    main()
