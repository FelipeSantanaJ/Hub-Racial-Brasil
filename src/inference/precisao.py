"""Precisão das tabelas de nível e regra de supressão (R8 da auditoria Rodada 2; decisão do
Ponto de parada 3, 13/10/2026).

**Regra:** uma estimativa de célula só é publicável se `n ≥ 30` **e** `CV ≤ 30%`, onde `n` é o
número de observações no DENOMINADOR do indicador (ex.: para a renda média, só quem tem renda;
para % com carteira, só os empregados) e CV = EP design-based ÷ estimativa. Estimativa zero ou
CV indefinido ⇒ não publicável. Os valores **não** são apagados: as tabelas ganham
`n_<ind>`, `cv_<ind>` e `publicavel_<ind>`, e gráficos e textos filtram por `publicavel`.

**CV a partir de totais por UPA.** Para não trazer o microdado para o pandas, as agregações via
SQL devolvem, por (célula, estrato, UPA), A = Σ w·y e B = Σ w sobre o domínio do indicador.
A combinação aqui reproduz `variancia.variancia_linearizada` com domínio = célula:

    média  ȳ = ΣA / ΣB,       z_hj = (A_hj − ȳ·B_hj) / ΣB      (média ou proporção)
    total  T = ΣB,            z_hj = B_hj                       (contagem ponderada)
    Var    = Σ_h n_h/(n_h−1) · Σ_j (z_hj − z̄_h)²

com n_h = nº de UPAs do estrato h no UNIVERSO (não só as que têm alguém da célula: as demais
entram com z = 0). Estrato com uma só UPA: contribui z_hj² (política "centrar_media_geral" de
`variancia.py`, cuja média geral é 0 para a média de domínio). Para o total a média geral não é
zero; o efeito é desprezível e está coberto pelo teste contra `variancia_linearizada` com
tolerância.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

N_MINIMO = 30
CV_MAXIMO = 0.30

REGRA_SUPRESSAO = {
    "n_minimo": N_MINIMO,
    "cv_maximo": CV_MAXIMO,
    "descricao": ("Estimativa publicável só se n ≥ 30 observações no denominador do indicador E "
                  "CV design-based (linearização Estrato/UPA) ≤ 30%. Estimativa zero ou CV indefinido "
                  "⇒ não publicável. Valores não são apagados: filtrar pela coluna publicavel_<ind>."),
    "decisao": "Ponto de parada 3, 13/10/2026 (R8 da auditoria Rodada 2)",
}


def publicavel(n, cv, n_minimo: int = N_MINIMO, cv_maximo: float = CV_MAXIMO):
    """Aplica a regra elemento a elemento; NaN em n ou cv ⇒ False."""
    n = np.asarray(n, dtype=float)
    cv = np.asarray(cv, dtype=float)
    with np.errstate(invalid="ignore"):
        return (n >= n_minimo) & (cv <= cv_maximo) & ~np.isnan(cv)


def cv_de_totais_upa(totais: pd.DataFrame, chaves: list[str], n_upas_estrato: pd.DataFrame,
                     tipo: str = "media", chaves_universo: list[str] | None = None) -> pd.DataFrame:
    """CV design-based por célula a partir de totais por (célula, estrato, UPA).

    totais:          colunas `chaves` + `estrato`, `upa`, `A` (Σ w·y; ignorada em "total"),
                     `B` (Σ w) e `n` (contagem) — só linhas com alguém do domínio.
    n_upas_estrato:  `chaves_universo` + `estrato` + `n_h` (UPAs do estrato no universo).
    chaves_universo: subconjunto de `chaves` que define o universo (ex.: ano, trimestre);
                     [] quando o universo é um só (trimestres agrupados).
    Devolve uma linha por célula: chaves, estimativa, ep, cv, n."""
    if tipo not in ("media", "total"):
        raise ValueError("tipo deve ser 'media' ou 'total'")
    cu = list(chaves_universo or [])
    if totais.empty:
        return pd.DataFrame(columns=[*chaves, "estimativa", "ep", "cv", "n"])
    t = totais.copy()
    t["_cel"] = t.groupby(chaves, dropna=False, sort=False).ngroup()
    cel = t.groupby("_cel", sort=True).agg(**{"B_tot": ("B", "sum"), "n": ("n", "sum")})
    cel = cel.join(t.groupby("_cel", sort=True)[chaves].first())
    if tipo == "media":
        cel["A_tot"] = t.groupby("_cel", sort=True)["A"].sum()
        with np.errstate(invalid="ignore", divide="ignore"):
            cel["estimativa"] = cel["A_tot"] / cel["B_tot"]
        ybar = cel["estimativa"].to_numpy()[t["_cel"].to_numpy()]
        wtot = cel["B_tot"].to_numpy()[t["_cel"].to_numpy()]
        with np.errstate(invalid="ignore", divide="ignore"):
            t["z"] = (t["A"].to_numpy() - ybar * t["B"].to_numpy()) / wtot
    else:
        cel["estimativa"] = cel["B_tot"]
        t["z"] = t["B"].astype(float)

    # Σz e Σz² por (célula, estrato), somando UPAs; as UPAs ausentes do estrato têm z = 0
    t["z2"] = t["z"] ** 2
    por_estrato = t.groupby(["_cel", "estrato"], sort=False).agg(S1=("z", "sum"), S2=("z2", "sum")).reset_index()
    por_estrato = por_estrato.join(cel[cu], on="_cel") if cu else por_estrato
    por_estrato = por_estrato.merge(n_upas_estrato[[*cu, "estrato", "n_h"]], on=[*cu, "estrato"], how="left")
    if por_estrato["n_h"].isna().any():
        raise ValueError("estrato sem contagem de UPAs no universo")
    nh = por_estrato["n_h"].to_numpy(dtype=float)
    s1, s2 = por_estrato["S1"].to_numpy(), por_estrato["S2"].to_numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        contrib = np.where(nh > 1, nh / (nh - 1) * (s2 - s1**2 / nh), s2)
    var = pd.Series(contrib).groupby(por_estrato["_cel"].to_numpy()).sum()
    cel["ep"] = np.sqrt(np.maximum(var.reindex(cel.index).to_numpy(), 0.0))
    cel.loc[cel["n"] < 2, "ep"] = np.nan  # como erro_padrao_media_design: sem variância com n < 2
    with np.errstate(invalid="ignore", divide="ignore"):
        cel["cv"] = np.where(cel["estimativa"] != 0, cel["ep"] / np.abs(cel["estimativa"]), np.nan)
    return cel[[*chaves, "estimativa", "ep", "cv", "n"]].reset_index(drop=True)
