"""Correção de multiplicidade por família (B3 da auditoria; R3/R7).

**Definição de família (12/10/2026):** uma família é o conjunto de comparações de UMA
tabela (um parquet) que compartilham o mesmo período e a mesma dimensão de abertura —
na prática, as colunas passadas em `familia` (ex.: `["ano", "trimestre"]` para as 5
regiões de um trimestre em `hiato_regional`; `["combo", "ano", "trimestre"]` na árvore).
Uma tabela com uma comparação por período (ex.: `hiato_racial`) tem famílias de tamanho 1
e o FDR coincide com o nominal — o problema de "58 trimestres ≠ 58 evidências
independentes" é outro (R6, tendência com HAC na Onda 2), não de multiplicidade.

Regra de uso (aprovada pelo Felipe em 13/10/2026):
- esta família por tabela é o PADRÃO (piso) das tabelas descritivas;
- todo estudo da Fase 4 declara a SUA família na ficha (`docs/studies/<id>/ficha.md`),
  ligada à pergunta (ex.: "as 27 UFs em 2026T2", "os 40 DiD do Desenho B"); a ficha manda;
- tendência no tempo não se testa com FDR sobre trimestres: usa regressão com EP robusto
  a autocorrelação (HAC; R6, Onda 2).

Método: Benjamini-Hochberg (controle da taxa de falsas descobertas, FDR), via
`statsmodels.stats.multitest.multipletests(method="fdr_bh")`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

ALFA_PADRAO = 0.05


def adicionar_fdr(df: pd.DataFrame, familia: list[str] | None, coluna_p: str = "p_valor",
                  alfa: float = ALFA_PADRAO, prefixo: str = "") -> pd.DataFrame:
    """Acrescenta `{prefixo}significativo_nominal` (p < alfa, sem correção),
    `{prefixo}p_valor_bh` (p ajustado por BH dentro da família) e
    `{prefixo}significativo_fdr`. `familia=None` = a tabela inteira é uma família.

    p-valores ausentes ficam fora da correção (não contam no tamanho da família) e saem
    como não significativos."""
    df = df.copy()
    p = df[coluna_p].astype(float)
    ajustado = pd.Series(np.nan, index=df.index)
    grupos = [(None, df.index)] if not familia else [(k, g.index) for k, g in df.groupby(familia, dropna=False)]
    for _, idx in grupos:
        sub = p.loc[idx].dropna()
        if len(sub):
            ajustado.loc[sub.index] = multipletests(sub.to_numpy(), alpha=alfa, method="fdr_bh")[1]
    df[f"{prefixo}significativo_nominal"] = (p < alfa).fillna(False).astype(bool)
    df[f"{prefixo}p_valor_bh"] = ajustado
    df[f"{prefixo}significativo_fdr"] = (ajustado < alfa).fillna(False).astype(bool)
    return df
