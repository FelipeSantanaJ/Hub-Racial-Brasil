"""Onda 3 — Bloco D: por que a diferença existe? (decomposição `C`; `docs/PLANO_DE_ANALISE.md`, Bloco D;
fichas em `docs/studies/D1`…).

- **D1** — hiato de ln renda (P1) Branca × Negra e Branca × Indígena:
  especificações aninhadas E0–E8 (idade → sexo → instrução → território → horas → vínculo → ocupação → atividade);
  Gelbach (contribuição de cada bloco, sem depender da ordem, com EP que inclui a incerteza de β); Shapley sobre os
  8 blocos; OB de dois termos (Reimers); RIF-OB em quantis (bootstrap Rao-Wu); sensibilidade a omitidas (Oster,
  Cinelli-Hazlett); e o lado do Bloco T: Gelbach da diferença de Pr(estar em P1) entre adultos 18+.

Rótulo obrigatório: o que sobra é a **parte do hiato não associada às covariáveis incluídas** (R5) — nunca
"discriminação".

Todas as regressões de uma amostra saem de uma única matriz X'WX (`Sistema`): as aninhadas, Gelbach e Shapley são
sub-blocos dela. A influência de c'β_S é ψ_i = x_iS·(G_SS⁻¹c)·w_i·e_iS, linearizada por Estrato/UPA.

Uso:
    python -m src.processing.bloco_d [--so d1 serie rif ext]
"""
from __future__ import annotations

import argparse
from itertools import combinations
from math import factorial

import duckdb
import numpy as np
import pandas as pd

from src.inference import variancia
from src.inference.saida import salvar_tabela
from src.processing.agregacoes_pnadc import DEFLATOR_PATH, OUTPUT_DIR, PARQUET_GLOB
from src.processing.bloco_a import multiplicadores_rao_wu
from src.processing.sensibilidade_populacao import Z95
from src.utils import pnadc_core
from src.utils import populacao as pop

RACAS_D = ["Negra", "Indígena"]  # comparadas com Branca
JANELAS = {"2012": [(2012, t) for t in (1, 2, 3, 4)],
           "2025T3-2026T2": [(2025, 3), (2025, 4), (2026, 1), (2026, 2)]}
BLOCOS = ["idade", "sexo", "instrucao", "territorio", "horas", "vinculo", "ocupacao", "atividade"]
ROTULO = {"idade": "Idade (faixas de 5 anos)", "sexo": "Sexo", "instrucao": "Instrução (VD3004)",
          "territorio": "Território (UF, urbano, tipo de área)", "horas": "Horas habituais (ln)",
          "vinculo": "Vínculo (posição, previdência)", "ocupacao": "Ocupação (grupamento VD4011)",
          "atividade": "Atividade (grupamento VD4010)"}
BLOCOS_EXT = ["idade", "sexo", "instrucao", "territorio"]  # existem para quem não trabalha
QUANTIS_RIF = [0.10, 0.25, 0.50, 0.75, 0.90]
BANDAS_RIF = [0.5, 1.0, 2.0]
N_BOOT_RIF = 100
NAO_ASSOCIADA = "parte não associada às covariáveis incluídas"
RACA_SQL = """CASE m.V2010 WHEN '1' THEN 'Branca' WHEN '2' THEN 'Negra' WHEN '4' THEN 'Negra'
                           WHEN '5' THEN 'Indígena' END"""


# ----------------------------------------------------------------------------------------- #
# dados
# ----------------------------------------------------------------------------------------- #
def micro_d(con, tris: list[tuple[int, int]]) -> pd.DataFrame:
    """Pessoas de 18+ (Branca, Negra, Indígena; sexo informado) dos trimestres pedidos."""
    filtro = " OR ".join(f"(m.ano = {a} AND m.trimestre = {t})" for a, t in tris)
    return con.execute(f"""
        SELECT m.ano, m.trimestre, {RACA_SQL} AS raca, m.V2007 AS sexo, m.V2009 AS idade, m.VD3004 AS instrucao,
               CAST(m.UF AS VARCHAR) AS uf, m.V1022 AS urbano, m.V1023 AS area, m.V4039 AS horas,
               m.VD4009 AS posicao, m.VD4012 AS previdencia, m.VD4011 AS ocupacao, m.VD4010 AS atividade, m.V4010 AS cbo,
               m.V1028 AS peso, m.UPA AS upa, m.Estrato AS estrato,
               COALESCE({pop.REFERENCIA.sql('m')}, FALSE) AS em_p1,
               CASE WHEN {pop.REFERENCIA.sql('m')} THEN m.VD4016 * d.deflator_habitual END AS renda
        FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1) m
        LEFT JOIN read_parquet('{DEFLATOR_PATH}') d ON m.ano = d.ano AND m.trimestre = d.trimestre AND m.UF = d.UF
        WHERE ({filtro}) AND m.V2009 >= {pop.IDADE_MINIMA_REFERENCIA} AND m.V2010 IN ('1','2','4','5')
          AND m.V2007 IN ('1','2')
    """).df()


def _dummies(codigos: pd.Series) -> tuple[np.ndarray, list[str]]:
    """Dummies sem a categoria mais frequente (referência); faltante vira categoria própria."""
    c = codigos.astype(object).where(codigos.notna(), "NA").astype(str)
    ref = c.value_counts().index[0]
    cats = sorted(set(c) - {ref})
    return np.column_stack([(c == k).to_numpy(float) for k in cats]) if cats else np.empty((len(c), 0)), cats


def colunas_blocos(m: pd.DataFrame, blocos: list[str]) -> dict[str, tuple[np.ndarray, list[str]]]:
    out = {}
    for b in blocos:
        if b == "idade":
            out[b] = _dummies(pd.cut(m["idade"], [17, 24, 29, 34, 39, 44, 49, 54, 59, 64, 200]).astype(str))
        elif b == "sexo":
            out[b] = ((m["sexo"] == "2").to_numpy(float)[:, None], ["Mulher"])
        elif b == "instrucao":
            out[b] = _dummies(m["instrucao"])
        elif b == "territorio":
            partes = [_dummies(m["uf"]), _dummies(m["urbano"]), _dummies(m["area"])]
            out[b] = (np.column_stack([p[0] for p in partes]), sum((p[1] for p in partes), []))
        elif b == "horas":
            out[b] = (np.log(m["horas"].to_numpy(float))[:, None], ["ln_horas"])
        elif b == "vinculo":
            partes = [_dummies(m["posicao"]), _dummies(m["previdencia"])]
            out[b] = (np.column_stack([p[0] for p in partes]), sum((p[1] for p in partes), []))
        elif b == "ocupacao":
            out[b] = _dummies(m["ocupacao"])
        elif b == "atividade":
            out[b] = _dummies(m["atividade"])
    return out


def montar_x(m: pd.DataFrame, blocos: list[str], racas: list[str] = RACAS_D,
             remover: bool = True) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """X = [const, dummies de raça, blocos…] e o índice das colunas de cada parte ('base' = const + raças).
    Com `remover`, sai toda coluna que é combinação linear das anteriores (na ordem dos blocos) — ex.: "serviços
    domésticos" da atividade (`VD4010`) repete "doméstico" da posição (`VD4009` 03/04) e fica no vínculo; os nomes
    removidos ficam em idx['_removidas']."""
    partes = colunas_blocos(m, blocos)
    raca = m["raca"].to_numpy(object)
    cols = [np.ones(len(m))] + [(raca == r).astype(float) for r in racas]
    nomes = ["const", *racas]
    idx = {"base": np.arange(1 + len(racas))}
    k = len(cols)
    for b in blocos:
        mat, rot = partes[b]
        cols += [mat[:, j] for j in range(mat.shape[1])]
        nomes += [f"{b}:{r}" for r in rot]
        idx[b] = np.arange(k, k + mat.shape[1])
        k += mat.shape[1]
    X = np.column_stack(cols)
    del cols
    if not remover:
        return X, idx
    w = m["peso"].to_numpy(float) if "peso" in m else np.ones(len(m))
    keep = colunas_independentes(X, w)
    if len(keep) == X.shape[1]:
        return X, {**idx, "_removidas": np.array([], dtype=object)}
    nova = np.full(X.shape[1], -1)
    nova[keep] = np.arange(len(keep))
    idx2 = {k_: nova[v][nova[v] >= 0] for k_, v in idx.items()}
    idx2["_removidas"] = np.array([nomes[j] for j in range(X.shape[1]) if nova[j] < 0], dtype=object)
    return X[:, keep], idx2


def colunas_independentes(X: np.ndarray, w: np.ndarray, tol: float = 1e-8, bloco: int = 200_000) -> np.ndarray:
    """Colunas de X mantidas, na ordem: a coluna j sai se a variância residual (ponderada) de x_j projetada nas
    colunas já mantidas for < tol × Σ w x_j² (colinear com as anteriores) ou se for toda zero."""
    p = X.shape[1]
    G = np.zeros((p, p))
    for i in range(0, X.shape[0], bloco):
        Xi = X[i:i + bloco]
        G += (Xi * w[i:i + bloco, None]).T @ Xi
    keep: list[int] = []
    for j in range(p):
        if G[j, j] <= 0:
            continue
        if keep:
            K = np.array(keep)
            r = G[j, j] - G[j, K] @ np.linalg.lstsq(G[np.ix_(K, K)], G[K, j], rcond=None)[0]
            if r < tol * G[j, j]:
                continue
        keep.append(j)
    return np.array(keep)


# ----------------------------------------------------------------------------------------- #
# álgebra: um X'WX, muitas regressões
# ----------------------------------------------------------------------------------------- #
class Sistema:
    """WLS de y em subconjuntos de colunas de X, a partir de G = X'WX e g = X'Wy (calculados uma vez)."""

    def __init__(self, X: np.ndarray, y: np.ndarray, w: np.ndarray, bloco: int = 200_000):
        self.X, self.y, self.w = X, np.asarray(y, float), np.asarray(w, float)
        p = X.shape[1]
        self.G, self.g = np.zeros((p, p)), np.zeros(p)
        for i in range(0, len(y), bloco):
            Xi, wi = X[i:i + bloco], self.w[i:i + bloco]
            Xw = Xi * wi[:, None]
            self.G += Xw.T @ Xi
            self.g += Xw.T @ self.y[i:i + bloco]

    @staticmethod
    def _resolver(A: np.ndarray, v: np.ndarray) -> np.ndarray:
        """A⁻¹v; em domínios pequenos (dummies colineares) usa a pseudo-inversa — os coeficientes de interesse
        (raça) continuam identificados quando a colinearidade está só entre controles."""
        try:
            return np.linalg.solve(A, v)
        except np.linalg.LinAlgError:
            return np.linalg.pinv(A, hermitian=True) @ v

    def beta(self, cols: np.ndarray) -> np.ndarray:
        """β completo (zeros fora de `cols`)."""
        b = np.zeros(self.X.shape[1])
        b[cols] = self._resolver(self.G[np.ix_(cols, cols)], self.g[cols])
        return b

    def residuo(self, b: np.ndarray) -> np.ndarray:
        return self.y - self.X @ b

    def influencia(self, cols: np.ndarray, c: np.ndarray, b: np.ndarray | None = None) -> np.ndarray:
        """ψ de c'β_S (c indexado como `cols`)."""
        b = self.beta(cols) if b is None else b
        a = np.zeros(self.X.shape[1])
        a[cols] = self._resolver(self.G[np.ix_(cols, cols)], c)
        return (self.X @ a) * self.w * self.residuo(b)

    def r2(self, b: np.ndarray) -> float:
        ybar = np.average(self.y, weights=self.w)
        return float(1 - np.sum(self.w * self.residuo(b) ** 2) / np.sum(self.w * (self.y - ybar) ** 2))


def ep_de(psi: np.ndarray, upa, est) -> float:
    v, _ = variancia.variancia_linearizada(psi, upa, est)
    return float(np.sqrt(max(float(v), 0.0)))


def aninhadas(s: Sistema, idx: dict, blocos: list[str], j_raca: int) -> list[tuple[str, float, np.ndarray]]:
    """[(especificação, coeficiente da raça, ψ)] para E0 (só raça) até E_k (todos os blocos)."""
    out, cols = [], idx["base"]
    pos = int(np.flatnonzero(cols == j_raca)[0])
    for k in range(len(blocos) + 1):
        if k:
            cols = np.concatenate([cols, idx[blocos[k - 1]]])
        b = s.beta(cols)
        c = np.zeros(len(cols))
        c[pos] = 1.0
        out.append((f"E{k}" + ("" if not k else f" + {blocos[k - 1]}"), float(b[j_raca]), s.influencia(cols, c, b)))
    return out


def gelbach(s: Sistema, idx: dict, blocos: list[str], j_raca: int) -> dict[str, tuple[float, np.ndarray]]:
    """Contribuição δ_k = e_r'G_BB⁻¹G_BK β_K de cada bloco à queda do coeficiente da raça de E0 (só base) para o
    modelo completo; Σ δ_k = β_base − β_completo. ψ_δk = influência da regressão auxiliar de h_k = X_K β_K em X_B
    (com h_k fixo) + c_k'ψ_βK (incerteza de β), com c_k = G_KB G_BB⁻¹ e_r."""
    B = idx["base"]
    F = np.concatenate([B, *[idx[b] for b in blocos]])
    bF = s.beta(F)
    eF = s.residuo(bF)
    r = int(np.flatnonzero(B == j_raca)[0])
    GBB_inv_er = np.linalg.solve(s.G[np.ix_(B, B)], np.eye(len(B))[r])
    GFF_inv = np.linalg.inv(s.G[np.ix_(F, F)])
    XB = s.X[:, B]
    out = {}
    for blk in blocos:
        K = idx[blk]
        h = s.X[:, K] @ bF[K]
        gama = np.linalg.solve(s.G[np.ix_(B, B)], s.G[np.ix_(B, K)] @ bF[K])
        delta = float(gama[r])
        ck = s.G[np.ix_(K, B)] @ GBB_inv_er
        posK = np.searchsorted(F, K) if np.all(np.diff(F) > 0) else np.array([int(np.flatnonzero(F == k)[0]) for k in K])
        a = np.zeros(s.X.shape[1])
        a[F] = GFF_inv[:, posK] @ ck
        psi = (XB @ GBB_inv_er) * s.w * (h - XB @ gama) + (s.X @ a) * s.w * eF
        out[blk] = (delta, psi)
    return out


def shapley(s: Sistema, idx: dict, blocos: list[str], j_raca: int) -> dict[str, tuple[float, np.ndarray]]:
    """Shapley-Shorrocks da queda do coeficiente da raça: φ_k = Σ_{S∌k} ω(|S|)[c(S) − c(S∪k)], ω(s) = s!(n−s−1)!/n!."""
    n = len(blocos)
    B = idx["base"]
    pos = int(np.flatnonzero(B == j_raca)[0])
    omega = [factorial(t) * factorial(n - t - 1) / factorial(n) for t in range(n)]
    phi = {b: 0.0 for b in blocos}
    psi = {b: np.zeros(len(s.y)) for b in blocos}
    for t in range(n + 1):
        for T in combinations(range(n), t):
            cols = np.concatenate([B, *[idx[blocos[k]] for k in T]]) if T else B
            b = s.beta(cols)
            c = np.zeros(len(cols))
            c[pos] = 1.0
            ps = s.influencia(cols, c, b)
            for k in range(n):
                coef = omega[t] if k not in T else -omega[t - 1]
                phi[blocos[k]] += coef * b[j_raca]
                psi[blocos[k]] += coef * ps
    return {k: (phi[k], psi[k]) for k in blocos}


# ----------------------------------------------------------------------------------------- #
# OB de dois termos (Reimers) e RIF-OB
# ----------------------------------------------------------------------------------------- #
def _g_dominio(X: np.ndarray, w: np.ndarray, dom: np.ndarray) -> np.ndarray:
    Xd = X[dom]
    return (Xd * w[dom][:, None]).T @ Xd


def _beta_grupo(G: np.ndarray, v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """β da regressão de um grupo só nas colunas com alguma observação nele (dummy vazia → coeficiente ausente)."""
    usa = np.diag(G) > 0
    b = np.zeros(len(v))
    b[usa] = Sistema._resolver(G[np.ix_(usa, usa)], v[usa])
    return b, usa


def _ginv(G: np.ndarray, c: np.ndarray, usa: np.ndarray) -> np.ndarray:
    a = np.zeros(len(c))
    a[usa] = Sistema._resolver(G[np.ix_(usa, usa)], c[usa])
    return a


def _pesos_ref(uA: np.ndarray, uB: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Peso de β_A e β_B em β*: ½–½ (Reimers) onde os dois existem; o único identificado onde só um existe."""
    ambos = uA & uB
    return np.where(ambos, 0.5, np.where(uA, 1.0, 0.0)), np.where(ambos, 0.5, np.where(uB, 1.0, 0.0))


def reimers(X: np.ndarray, y: np.ndarray, w: np.ndarray, domA: np.ndarray, domB: np.ndarray,
            GA: np.ndarray | None = None, GB: np.ndarray | None = None) -> dict:
    """OB de dois termos, A − B, com β* = (β_A + β_B)/2. X sem as dummies de raça (com constante).
    Devolve estimativas e ψ (n) de bruto, explicada e não associada."""
    GA = _g_dominio(X, w, domA) if GA is None else GA
    GB = _g_dominio(X, w, domB) if GB is None else GB
    bA, uA = _beta_grupo(GA, (X[domA] * w[domA][:, None]).T @ y[domA])
    bB, uB = _beta_grupo(GB, (X[domB] * w[domB][:, None]).T @ y[domB])
    xA = np.average(X[domA], axis=0, weights=w[domA])
    xB = np.average(X[domB], axis=0, weights=w[domB])
    pA, pB = _pesos_ref(uA, uB)
    d, bs = xA - xB, pA * bA + pB * bB
    zyA, mA = variancia.influencia_media(np.where(domA, y, 0.0), w, domA)
    zyB, mB = variancia.influencia_media(np.where(domB, y, 0.0), w, domB)
    xb = X @ bs
    zxA, _ = variancia.influencia_media(np.where(domA, xb, 0.0), w, domA)
    zxB, _ = variancia.influencia_media(np.where(domB, xb, 0.0), w, domB)
    eA = np.where(domA, y - X @ bA, 0.0)
    eB = np.where(domB, y - X @ bB, 0.0)
    psi_bA_d = (X @ _ginv(GA, pA * d, uA)) * w * eA
    psi_bB_d = (X @ _ginv(GB, pB * d, uB)) * w * eB
    psi_expl = (zxA - zxB) + psi_bA_d + psi_bB_d
    psi_bruto = zyA - zyB
    expl = float(d @ bs)
    return {"bruto": (float(mA - mB), psi_bruto), "explicada": (expl, psi_expl),
            NAO_ASSOCIADA: (float(mA - mB - expl), psi_bruto - psi_expl)}


def _densidade(y: np.ndarray, w: np.ndarray, ponto: float, fator: float) -> float:
    """Densidade kernel gaussiana ponderada em `ponto`; banda de Silverman × fator."""
    sw = w.sum()
    mu = np.sum(w * y) / sw
    sd = np.sqrt(np.sum(w * (y - mu) ** 2) / sw)
    iqr = pnadc_core.quantil_ponderado(y, w, 0.75) - pnadc_core.quantil_ponderado(y, w, 0.25)
    h = fator * 0.9 * min(sd, iqr / 1.34 if iqr > 0 else sd) * len(y) ** (-0.2)
    u = (ponto - y) / h
    return float(np.sum(w * np.exp(-0.5 * u * u)) / (sw * h * np.sqrt(2 * np.pi)))


def rif(y: np.ndarray, w: np.ndarray, tau: float, fator: float = 1.0) -> np.ndarray:
    q = pnadc_core.quantil_ponderado(y, w, tau)
    return q + (tau - (y <= q).astype(float)) / _densidade(y, w, q, fator)


def rif_ob(X: np.ndarray, y: np.ndarray, w: np.ndarray, domA: np.ndarray, domB: np.ndarray, tau: float,
           fator: float, GA: np.ndarray, GB: np.ndarray) -> dict[str, float]:
    """RIF-OB (Reimers) no quantil τ: RIF de cada grupo na própria distribuição; bruto = q_A − q_B."""
    r = np.zeros(len(y))
    r[domA] = rif(y[domA], w[domA], tau, fator)
    r[domB] = rif(y[domB], w[domB], tau, fator)
    bA, uA = _beta_grupo(GA, (X[domA] * w[domA][:, None]).T @ r[domA])
    bB, uB = _beta_grupo(GB, (X[domB] * w[domB][:, None]).T @ r[domB])
    pA, pB = _pesos_ref(uA, uB)
    xA = np.average(X[domA], axis=0, weights=w[domA])
    xB = np.average(X[domB], axis=0, weights=w[domB])
    bruto = pnadc_core.quantil_ponderado(y[domA], w[domA], tau) - pnadc_core.quantil_ponderado(y[domB], w[domB], tau)
    expl = float((xA - xB) @ (pA * bA + pB * bB))
    return {"bruto": float(bruto), "explicada": expl, NAO_ASSOCIADA: float(bruto - expl)}


# ----------------------------------------------------------------------------------------- #
# sensibilidade a omitidas
# ----------------------------------------------------------------------------------------- #
def oster(beta_curto: float, r2_curto: float, beta_longo: float, r2_longo: float, r2max: float) -> dict:
    """Aproximação de Oster (2019, a confirmar): β* = β̃ − δ(β̊ − β̃)(Rmax − R̃)/(R̃ − R̊), δ = 1; e o δ que zera β."""
    mov = (beta_curto - beta_longo) * (r2max - r2_longo) / (r2_longo - r2_curto)
    return {"beta_ajustado_delta1": beta_longo - mov, "delta_para_zero": beta_longo / mov if mov else np.nan}


def valor_robustez(r2_parcial: float, q: float = 1.0) -> float:
    """RV de Cinelli-Hazlett (2020): força (R² parcial com tratamento e desfecho) de uma omitida que reduziria o
    efeito em 100·q%. f = q·√(R²/(1−R²)); RV = ½(√(f⁴ + 4f²) − f²)."""
    f2 = q * q * r2_parcial / (1 - r2_parcial)
    return 0.5 * (np.sqrt(f2 * f2 + 4 * f2) - f2)


def limite_ch(r2dxj: float, r2yxj: float, k: float, beta: float, razao_dp: float) -> dict:
    """Limite de Cinelli-Hazlett para uma omitida k vezes tão forte quanto o bloco j (fórmulas do sensemakr,
    a confirmar). razao_dp = √(SSR(y|D,X)/SSR(D|X)) (= EP·√gl em MQO)."""
    r2dz = k * r2dxj / (1 - r2dxj)
    if r2dz >= 1:
        return {"r2dz_x": r2dz, "r2yz_dx": np.nan, "vies": np.nan, "beta_ajustado": np.nan}
    r2zxj = k * r2dxj ** 2 / ((1 - k * r2dxj) * (1 - r2dxj))
    r2yz = min(1.0, ((np.sqrt(k) + np.sqrt(r2zxj)) / np.sqrt(1 - r2zxj)) ** 2 * r2yxj / (1 - r2yxj))
    vies = np.sqrt(r2yz * r2dz / (1 - r2dz)) * razao_dp
    return {"r2dz_x": r2dz, "r2yz_dx": r2yz, "vies": vies, "beta_ajustado": float(np.sign(beta) * (abs(beta) - vies))}


def sensibilidade(m: pd.DataFrame, X: np.ndarray, idx: dict, blocos: list[str]) -> list[dict]:
    """Oster e Cinelli-Hazlett para o coeficiente de Negra (amostra Branca + Negra, especificação completa)."""
    sel = m["raca"].isin(["Branca", "Negra"]).to_numpy()
    Xs = X[sel]
    y = np.log(m["renda"].to_numpy(float)[sel])
    w = m["peso"].to_numpy(float)[sel]
    j_neg = 1
    sem_ind = np.array([c for c in range(X.shape[1]) if c != 2])  # tira a coluna Indígena (vazia aqui)
    s = Sistema(Xs[:, sem_ind], y, w)
    F = np.arange(len(sem_ind))
    curto = np.array([0, 1])
    b_c, b_l = s.beta(curto), s.beta(F)
    r2c, r2l = s.r2(b_c), s.r2(b_l)
    linhas = []
    for mult in (1.3, 2.0):
        r2max = min(mult * r2l, 1.0)
        o = oster(b_c[j_neg], r2c, b_l[j_neg], r2l, r2max)
        linhas.append({"metodo": "Oster", "parametro": f"R²max = min({mult}·R̃, 1) = {r2max:.3f}",
                       "beta_curto": b_c[j_neg], "r2_curto": r2c, "beta_completo": b_l[j_neg], "r2_completo": r2l, **o})
    # Cinelli-Hazlett: R² parciais por FWL (somas de quadrados ponderadas)
    def ssr(sist, cols):
        return float(np.sum(sist.w * sist.residuo(sist.beta(cols)) ** 2))
    sem_d = F[F != j_neg]
    ssr_y_full, ssr_y_semd = ssr(s, F), ssr(s, sem_d)
    r2yd = (ssr_y_semd - ssr_y_full) / ssr_y_semd
    sd = Sistema(Xs[:, sem_ind], Xs[:, 1], w)  # tratamento D = Negra em X sem D
    ssr_d = ssr(sd, sem_d)
    razao = np.sqrt(ssr_y_full / ssr_d)
    linhas.append({"metodo": "Cinelli-Hazlett", "parametro": "RV (q = 1)", "beta_completo": b_l[j_neg],
                   "r2_parcial_y_d": r2yd, "rv_q1": valor_robustez(r2yd), "razao_dp": razao})
    mapa = {c: i for i, c in enumerate(sem_ind)}
    for blk in ("instrucao", "territorio"):
        J = np.array([mapa[c] for c in idx[blk]])
        sem_j = np.setdiff1d(sem_d, J)
        r2dxj = (ssr(sd, sem_j) - ssr_d) / ssr(sd, sem_j)
        sem_j_y = np.setdiff1d(F, J)
        r2yxj = (ssr(s, sem_j_y) - ssr_y_full) / ssr(s, sem_j_y)
        for k in (1, 2, 3):
            linhas.append({"metodo": "Cinelli-Hazlett", "parametro": f"omitida {k}× tão forte quanto {blk}",
                           "beta_completo": b_l[j_neg], "r2_parcial_d_bloco": r2dxj, "r2_parcial_y_bloco": r2yxj,
                           **limite_ch(r2dxj, r2yxj, k, b_l[j_neg], razao)})
    return linhas


# ----------------------------------------------------------------------------------------- #
# geradores
# ----------------------------------------------------------------------------------------- #
def _amostra_p1(m: pd.DataFrame) -> pd.DataFrame:
    ok = m["em_p1"] & m["renda"].notna() & (m["renda"] > 0) & m["horas"].notna() & (m["horas"] > 0)
    return m[ok].reset_index(drop=True)


def decompor(m: pd.DataFrame, chaves: dict, shap: bool = True) -> tuple[list[dict], list[dict], dict]:
    """Aninhadas + Gelbach (+ Shapley) numa amostra P1. Devolve linhas e ψ guardados para diferenças entre janelas."""
    X, idx = montar_x(m, BLOCOS)
    print(f"  {chaves}: colunas colineares removidas: {list(idx['_removidas'])}", flush=True)
    y = np.log(m["renda"].to_numpy(float))
    w = m["peso"].to_numpy(float)
    upa, est = m["upa"].to_numpy(), m["estrato"].to_numpy()
    s = Sistema(X, y, w)
    raca = m["raca"].to_numpy(object)
    an, gb, guard = [], [], {}
    for j, r in enumerate(RACAS_D, start=1):
        n_g = int((raca == r).sum())
        seq = aninhadas(s, idx, BLOCOS, j)
        bruto = -seq[0][1]  # coeficiente de raça (grupo − Branca) → hiato Branca − grupo
        for esp, coef, psi in seq:
            e = ep_de(psi, upa, est)
            an.append({**chaves, "raca": r, "especificacao": esp, "hiato_condicional_lp": -coef, "ep": e,
                       "pct_associada_do_bruto": 100 * (1 - coef / -bruto) if bruto else np.nan, "n_grupo": n_g,
                       "n_total": len(m)})
        guard[(r, "E8")] = (-seq[-1][1], -seq[-1][2])
        guard[(r, "bruto")] = (bruto, -seq[0][2])
        g = gelbach(s, idx, BLOCOS, j)
        metodos = [("Gelbach", g)] + ([("Shapley", shapley(s, idx, BLOCOS, j))] if shap else [])
        for metodo, res in metodos:
            for blk, (d, psi) in res.items():
                # δ < 0 = o bloco leva o coeficiente da raça para perto de zero: contribuição ao hiato = −δ > 0
                gb.append({**chaves, "raca": r, "metodo": metodo, "bloco": ROTULO[blk], "contribuicao_lp": -d,
                           "ep": ep_de(psi, upa, est), "pct_do_bruto": 100 * -d / bruto if bruto else np.nan})
                if metodo == "Gelbach":
                    guard[(r, f"gelbach {blk}")] = (-d, -psi)
            if metodo == "Gelbach":
                # H1: instrução − cada outro bloco
                for blk in BLOCOS:
                    if blk == "instrucao":
                        continue
                    psi = -(res["instrucao"][1] - res[blk][1])
                    gb.append({**chaves, "raca": r, "metodo": "Gelbach: diferença", "bloco": f"instrução − {blk}",
                               "contribuicao_lp": -(res["instrucao"][0] - res[blk][0]), "ep": ep_de(psi, upa, est)})
                vmm = sum(res[b][0] for b in ("vinculo", "ocupacao", "atividade")) - res["instrucao"][0]
                psi = -(sum(res[b][1] for b in ("vinculo", "ocupacao", "atividade")) - res["instrucao"][1])
                gb.append({**chaves, "raca": r, "metodo": "Gelbach: diferença", "bloco": "(vínculo + ocupação + atividade) − instrução",
                           "contribuicao_lp": -vmm, "ep": ep_de(psi, upa, est)})
    guard["upa"], guard["est"] = upa, est
    return an, gb, guard


def reimers_rif(m: pd.DataFrame, chaves: dict, n_boot: int = N_BOOT_RIF) -> tuple[list[dict], list[dict]]:
    X, _ = montar_x(m, BLOCOS, racas=[])
    y = np.log(m["renda"].to_numpy(float))
    w = m["peso"].to_numpy(float)
    upa, est = m["upa"].to_numpy(), m["estrato"].to_numpy()
    raca = m["raca"].to_numpy(object)
    domB = raca == "Branca"
    GB = _g_dominio(X, w, domB)
    ob, rf = [], []
    cod, mult = multiplicadores_rao_wu(upa, est, n_boot, seed=31)
    doms = {r: raca == r for r in RACAS_D}
    GAs = {r: _g_dominio(X, w, doms[r]) for r in RACAS_D}
    for r in RACAS_D:
        res = reimers(X, y, w, domB, doms[r], GB, GAs[r])
        for comp, (v, psi) in res.items():
            ob.append({**chaves, "raca": r, "componente": comp, "estimativa_lp": v, "ep": ep_de(psi, upa, est)})
        for fator in BANDAS_RIF:
            for tau in QUANTIS_RIF:
                for comp, v in rif_ob(X, y, w, domB, doms[r], tau, fator, GB, GAs[r]).items():
                    rf.append({**chaves, "raca": r, "quantil": f"P{int(round(tau * 100))}", "banda_fator": fator,
                               "componente": comp, "estimativa_lp": v})
    # bootstrap de Rao-Wu (banda × 1): G do grupo Branco uma vez por réplica
    reps = {(r, tau, c): [] for r in RACAS_D for tau in QUANTIS_RIF for c in ("bruto", "explicada", NAO_ASSOCIADA)}
    for b in range(n_boot):
        wb = w * mult[cod, b]
        GBb = _g_dominio(X, wb, domB)
        for r in RACAS_D:
            GAb = _g_dominio(X, wb, doms[r])
            for tau in QUANTIS_RIF:
                for c, v in rif_ob(X, y, wb, domB, doms[r], tau, 1.0, GBb, GAb).items():
                    reps[(r, tau, c)].append(v)
        if (b + 1) % 20 == 0:
            print(f"  RIF-OB bootstrap {b + 1}/{n_boot}", flush=True)
    for ln in rf:
        if ln["banda_fator"] != 1.0:
            continue
        arr = np.array(reps[(ln["raca"], int(ln["quantil"][1:]) / 100, ln["componente"])])
        ln["ep_bootstrap"] = float(arr.std(ddof=1))
        ln["ic_inferior"], ln["ic_superior"] = float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))
    return ob, rf


def extensiva(m: pd.DataFrame, chaves: dict) -> list[dict]:
    """Lado P4: Gelbach da diferença de Pr(P1) (p.p.) entre adultos 18+ com os blocos que existem fora do trabalho."""
    X, idx = montar_x(m, BLOCOS_EXT)
    y = 100 * m["em_p1"].to_numpy(float)
    w = m["peso"].to_numpy(float)
    upa, est = m["upa"].to_numpy(), m["estrato"].to_numpy()
    s = Sistema(X, y, w)
    linhas = []
    for j, r in enumerate(RACAS_D, start=1):
        seq = aninhadas(s, idx, BLOCOS_EXT, j)
        bruto = -seq[0][1]
        for esp, coef, psi in seq:
            linhas.append({**chaves, "raca": r, "metodo": "aninhada", "termo": esp, "estimativa_pp": -coef,
                           "ep": ep_de(psi, upa, est)})
        for blk, (d, psi) in gelbach(s, idx, BLOCOS_EXT, j).items():
            linhas.append({**chaves, "raca": r, "metodo": "Gelbach", "termo": ROTULO[blk], "estimativa_pp": -d,
                           "ep": ep_de(psi, upa, est), "pct_do_bruto": 100 * -d / bruto if bruto else np.nan})
    return linhas


def _ic(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df["ic_inferior"] = df[col] - Z95 * df["ep"]
    df["ic_superior"] = df[col] + Z95 * df["ep"]
    return df


def diferencas_janelas(g0: dict, g1: dict) -> list[dict]:
    """Mudança (recente − 2012) de E8, bruto e Gelbach por bloco, com a covariância das UPAs comuns (ψ empilhados)."""
    upa = np.concatenate([g0["upa"], g1["upa"]])
    est = np.concatenate([g0["est"], g1["est"]])
    linhas = []
    for chave in g1:
        if chave in ("upa", "est"):
            continue
        v0, p0 = g0[chave]
        v1, p1 = g1[chave]
        psi = np.concatenate([-p0, p1])
        linhas.append({"raca": chave[0], "termo": chave[1], "valor_2012": v0, "valor_recente": v1,
                       "mudanca_lp": v1 - v0, "ep": ep_de(psi, upa, est)})
    return linhas


def gerar_d1(con, fazer: set[str]) -> None:
    meta = dict(se_metodo="wls_influencia_linearizacao_estrato_upa",
                rotulo_residuo=NAO_ASSOCIADA + " (nunca 'discriminação'; regra R5)")
    an, gb, ob, rf, se, ext, guard = [], [], [], [], [], [], {}
    if fazer & {"d1", "rif", "ext"}:
        for nome, tris in JANELAS.items():
            todos = micro_d(con, tris)
            m = _amostra_p1(todos)
            ch = {"periodo": nome}
            print(f"D1 {nome}: {len(m):,} em P1 (de {int(todos['em_p1'].sum()):,})".replace(",", "."), flush=True)
            if "d1" in fazer:
                a, g, guard[nome] = decompor(m, ch)
                an += a
                gb += g
                X, idx = montar_x(m, BLOCOS)
                se += [{**ch, **ln} for ln in sensibilidade(m, X, idx, BLOCOS)]
                del X
            if "rif" in fazer:
                o, r_ = reimers_rif(m, ch)
                ob += o
                rf += r_
            if "ext" in fazer:
                ext += extensiva(todos, ch)
            del m, todos
    if "serie" in fazer:
        for a in range(2012, 2027):
            m = _amostra_p1(micro_d(con, [(a, 2)]))
            x, g, _ = decompor(m, {"periodo": f"{a}T2"}, shap=False)
            an += x
            gb += g
            print(f"D1 série {a}T2", flush=True)
    if an:
        salvar_tabela(_ic(pd.DataFrame(an), "hiato_condicional_lp"), OUTPUT_DIR / "d1_aninhada.parquet", **meta,
                      nota="Hiato Branca − grupo em ln renda (log-pontos) por especificação aninhada E0–E8")
        salvar_tabela(_ic(pd.DataFrame(gb), "contribuicao_lp"), OUTPUT_DIR / "d1_contribuicao_blocos.parquet", **meta,
                      nota="Gelbach (com incerteza de β) e Shapley; contribuição > 0 = bloco associado a parte do hiato")
    if "d1" in fazer and len(guard) == 2:
        salvar_tabela(_ic(pd.DataFrame(diferencas_janelas(guard["2012"], guard["2025T3-2026T2"])), "mudanca_lp"),
                      OUTPUT_DIR / "d1_mudanca_janelas.parquet", **meta,
                      nota="Recente − 2012; EP com a covariância das UPAs comuns às duas janelas")
    if se:
        salvar_tabela(pd.DataFrame(se), OUTPUT_DIR / "d1_sensibilidade_omitidas.parquet", se_metodo="sem_inferencia",
                      nota="Oster (aproximação, δ = 1) e Cinelli-Hazlett (RV e limites por bloco); Branca + Negra, E8")
    if ob:
        salvar_tabela(_ic(pd.DataFrame(ob), "estimativa_lp"), OUTPUT_DIR / "d1_ob_reimers.parquet", **meta)
        salvar_tabela(pd.DataFrame(rf), OUTPUT_DIR / "d1_rif_ob.parquet",
                      se_metodo=f"bootstrap_rao_wu_estrato_upa_{N_BOOT_RIF} (banda × 1)",
                      nota="RIF-OB (Reimers), ln renda; bandas de Silverman × 0,5/1/2; IC só na banda × 1")
    if ext:
        salvar_tabela(_ic(pd.DataFrame(ext), "estimativa_pp"), OUTPUT_DIR / "d1_extensiva_p1.parquet", **meta,
                      nota="Diferença de Pr(P1) Branca − grupo (p.p.), adultos 18+; Gelbach com idade, sexo, instrução, território")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--so", nargs="*", default=None, help="d1 serie rif ext")
    fazer = set(parser.parse_args().so or ["d1", "serie", "rif", "ext"])
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    gerar_d1(con, fazer)


if __name__ == "__main__":
    main()
