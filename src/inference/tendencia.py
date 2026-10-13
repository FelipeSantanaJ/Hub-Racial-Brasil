"""Tendência e episódios em séries trimestrais com erro-padrão robusto a autocorrelação (HAC).

Corrige o R6 da auditoria: 58 trimestres da PNAD Contínua não são 58 evidências independentes —
o mesmo domicílio fica 5 trimestres na amostra (rotação) e o hiato tem inércia. A regressão de
tendência por OLS com EP i.i.d. (`ritmo_convergencia_hiatos`, `quebra_estrutural`) subestima a
incerteza.

**Estimador principal: EWC** (*equal-weighted cosine*; Lazarus, Lewis, Stock & Watson 2018 —
*a confirmar*): a variância de longo prazo de z_t = x_t·û_t é a média dos quadrados das projeções
de z em ν cossenos, Λ_j = √(2/T) Σ_t cos(πj(t − ½)/T) z_t, com ν = ⌊0,4·T^(2/3)⌋ (= 5 para T = 58)
e valores críticos t de Student com ν graus de liberdade. Escolhido por simulação (13/10/2026,
`tests/test_bloco_s.py`): com T = 58 e erro AR(1), a cobertura nominal de 95% fica em ≈ 92% (ρ = 0),
90% (ρ = 0,3), 89% (ρ = 0,7) e 79% (ρ = 0,9). Newey-West com defasagem 4 cobre 78% com ρ = 0,7.

**Sensibilidades reportadas junto:** Newey-West (Bartlett, L = max(⌊4(T/100)^(2/9)⌋, 4)) e GLS com
erro AR(1) (Prais-Winsten iterado, `statsmodels.GLSAR`). Uma tendência só é chamada de "confiável"
quando o IC 95% exclui zero nos três (`tendencia_confiavel`). Nenhum método é confiável com
persistência muito alta (ρ ≥ 0,9) em 58 pontos: o ρ dos resíduos sai na tabela.

O EP design-based de cada trimestre não entra como peso: a regressão descreve a série publicada; a
correção de autocorrelação absorve também a que vem da sobreposição de amostras.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

DEFASAGEM_MINIMA = 4
EPISODIOS_PADRAO = {  # (início, fim) em trimestres (ano, tri), inclusive
    "2012–2014 (antes da recessão)": ((2012, 1), (2014, 4)),
    "2015–2016 (recessão)": ((2015, 1), (2016, 4)),
    "2017–2019 (recuperação lenta)": ((2017, 1), (2019, 4)),
    "2020–2021 (pandemia; coleta por telefone)": ((2020, 1), (2021, 4)),
    "2022–2026 (pós-pandemia)": ((2022, 1), (2026, 4)),
}
METODO = "ewc_lazarus_lewis_stock_watson; sensibilidades newey_west e gls_ar1"


def defasagem_hac(n: int) -> int:
    return max(int(np.floor(4 * (n / 100) ** (2 / 9))), DEFASAGEM_MINIMA)


def graus_ewc(n: int) -> int:
    return max(int(np.floor(0.4 * n ** (2 / 3))), 2)


def cov_ewc(X: np.ndarray, u: np.ndarray, nu: int | None = None) -> tuple[np.ndarray, int]:
    """Matriz de covariância EWC dos coeficientes de OLS (X sem pesos, u = resíduos)."""
    X, u = np.asarray(X, float), np.asarray(u, float)
    T = len(u)
    nu = graus_ewc(T) if nu is None else nu
    Z = X * u[:, None]
    tt = np.arange(1, T + 1)
    L = np.array([np.sqrt(2 / T) * (np.cos(np.pi * j * (tt - 0.5) / T) @ Z) for j in range(1, nu + 1)])
    omega = L.T @ L / nu
    XXi = np.linalg.inv(X.T @ X)
    return XXi @ (T * omega) @ XXi, nu


def tempo_anos(ano, trimestre) -> np.ndarray:
    """Tempo contínuo em anos (2012T1 = 2012,0; 2012T2 = 2012,25…)."""
    return np.asarray(ano, float) + (np.asarray(trimestre, float) - 1) / 4


def tendencia_hac(t, y, z: float = 1.959963984540054) -> dict:
    """y = a + b·t por OLS; t em anos ⇒ b em unidades de y por ano. IC principal por EWC (t com ν
    g.l.); sensibilidades Newey-West e GLS AR(1); EP i.i.d. para mostrar quanto a correção muda."""
    t, y = np.asarray(t, float), np.asarray(y, float)
    ok = np.isfinite(t) & np.isfinite(y)
    t, y = t[ok], y[ok]
    n = len(y)
    X = sm.add_constant(t - t.mean())
    fit = sm.OLS(y, X).fit()
    b = float(fit.params[1])
    V, nu = cov_ewc(X, fit.resid)
    ep = float(np.sqrt(max(V[1, 1], 0.0)))
    q = float(stats.t.ppf(0.975, nu))
    L = defasagem_hac(n)
    nw = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": L, "use_correction": True})
    gls = sm.GLSAR(y, X, rho=1).iterative_fit(maxiter=20)
    ep_nw, ep_gls = float(nw.bse[1]), float(gls.bse[1])
    rho = float(np.corrcoef(fit.resid[1:], fit.resid[:-1])[0, 1]) if n > 3 else np.nan
    ic = (b - q * ep, b + q * ep)
    ic_nw = (b - z * ep_nw, b + z * ep_nw)
    b_gls = float(gls.params[1])
    ic_gls = (b_gls - stats.t.ppf(0.975, n - 3) * ep_gls, b_gls + stats.t.ppf(0.975, n - 3) * ep_gls)
    exclui = lambda lo, hi: bool(lo > 0 or hi < 0)  # noqa: E731
    return {"n_periodos": n, "inclinacao_por_ano": b, "ep_ewc": ep, "gl_ewc": nu, "ic_inferior": ic[0],
            "ic_superior": ic[1], "p_valor_ewc": float(2 * stats.t.sf(abs(b / ep), nu)) if ep > 0 else np.nan,
            "ep_newey_west": ep_nw, "defasagem_newey_west": L, "ic_nw_inferior": ic_nw[0], "ic_nw_superior": ic_nw[1],
            "inclinacao_gls_ar1": b_gls, "ep_gls_ar1": ep_gls, "rho_gls_ar1": float(gls.model.rho[0]),
            "ic_gls_inferior": ic_gls[0], "ic_gls_superior": ic_gls[1],
            "ep_iid": float(fit.bse[1]), "razao_ep_ewc_iid": ep / float(fit.bse[1]) if fit.bse[1] > 0 else np.nan,
            "rho_residuos": rho, "r2": float(fit.rsquared), "nivel_medio": float(fit.params[0]),
            "tendencia_confiavel": exclui(*ic) and exclui(*ic_nw) and exclui(*ic_gls)
                                   and np.sign(b) == np.sign(b_gls)}


def episodio_de(ano, trimestre, episodios: dict = EPISODIOS_PADRAO) -> np.ndarray:
    chave = np.asarray(ano, int) * 10 + np.asarray(trimestre, int)
    rot = np.full(len(chave), None, dtype=object)
    for nome, ((a0, t0), (a1, t1)) in episodios.items():
        rot[(chave >= a0 * 10 + t0) & (chave <= a1 * 10 + t1)] = nome
    return rot


def medias_episodios_hac(ano, trimestre, y, episodios: dict = EPISODIOS_PADRAO, referencia: str | None = None,
                         nu: int | None = None) -> pd.DataFrame:
    """Nível médio da série em cada episódio (regressão em dummies de episódio, sem constante) e
    diferença para o episódio de `referencia` (padrão: o primeiro), com covariância EWC e t de
    Student com ν g.l. (`nu`; padrão ⌊0,4·T^(2/3)⌋)."""
    y = np.asarray(y, float)
    ep_rot = episodio_de(ano, trimestre, episodios)
    ok = np.isfinite(y) & pd.notna(ep_rot)
    y, ep_rot = y[ok], ep_rot[ok]
    nomes = [e for e in episodios if (ep_rot == e).any()]
    X = np.column_stack([(ep_rot == e).astype(float) for e in nomes])
    fit = sm.OLS(y, X).fit()
    V, nu = cov_ewc(X, fit.resid, nu)
    q = float(stats.t.ppf(0.975, nu))
    ref = referencia or nomes[0]
    i0 = nomes.index(ref)
    linhas = []
    for i, e in enumerate(nomes):
        dif = float(fit.params[i] - fit.params[i0])
        ep_d = float(np.sqrt(max(V[i, i] + V[i0, i0] - 2 * V[i, i0], 0.0)))
        p = float(2 * stats.t.sf(abs(dif / ep_d), nu)) if ep_d > 0 else np.nan
        linhas.append({"episodio": e, "n_periodos": int((ep_rot == e).sum()), "media": float(fit.params[i]),
                       "ep": float(np.sqrt(max(V[i, i], 0.0))), "dif_vs_referencia": dif, "ep_dif": ep_d,
                       "dif_ic_inferior": dif - q * ep_d, "dif_ic_superior": dif + q * ep_d,
                       "p_valor_dif": p if i != i0 else np.nan, "referencia": ref, "gl_ewc": nu})
    return pd.DataFrame(linhas)
