"""População e renda de referência do Hub (Bloco F do plano de análise; decisões de 12/10/2026).

**Uma única definição**, da qual saem o SQL usado na `CRIAR_BASE` e a máscara em pandas
usada nos testes e em análises fora do DuckDB:

- **Renda de referência:** rendimento mensal **habitual do trabalho principal** (`VD4016`),
  deflacionado pelo deflator habitual do IBGE. O Hub usava até aqui o habitual de **todos os
  trabalhos** (`VD4019`), que continua disponível como `renda_habitual_*` para as tabelas ainda
  não migradas e como sensibilidade (P3 do Bloco S).
- **População de referência (P1):** ocupados (`VD4002 = '1'`), **18 anos ou mais** (`V2009`),
  com `VD4016 > 0`. Ficam de fora: não ocupados, ocupados sem rendimento no trabalho principal
  (ex.: trabalhador familiar auxiliar) e renda zero. Quanto essa exclusão pesa é o Bloco S.
- **Sensibilidade de idade:** 14+ (o recorte histórico do Hub).

Gini e Theil usam a MESMA população (fecha E3/R1 da auditoria): as duas funções recebem a base
já filtrada por `filtro_sql()`.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

IDADE_MINIMA_REFERENCIA = 18
IDADE_MINIMA_SENSIBILIDADE = 14
VARIAVEL_RENDA_REFERENCIA = "VD4016"   # habitual, trabalho principal
VARIAVEL_RENDA_TODOS_TRABALHOS = "VD4019"
VARIAVEL_OCUPACAO = "VD4002"           # '1' = ocupada
VARIAVEL_IDADE = "V2009"
CODIGO_OCUPADO = "1"

DESCRICAO_RENDA_REFERENCIA = ("Rendimento mensal habitual do trabalho principal (VD4016), "
                              "deflacionado pelo deflator habitual do IBGE")
DESCRICAO_POPULACAO_REFERENCIA = (f"Ocupados ({VARIAVEL_OCUPACAO}=1) de {IDADE_MINIMA_REFERENCIA}+ anos com "
                                  f"rendimento habitual do trabalho principal ({VARIAVEL_RENDA_REFERENCIA}) > 0")

COLUNA_FLAG = "em_populacao_referencia"
COLUNA_FLAG_14 = "em_populacao_referencia_14mais"
COLUNA_RENDA_REAL = "renda_referencia_real"
COLUNA_RENDA_NOMINAL = "renda_referencia_nominal"


@dataclass(frozen=True)
class DefinicaoPopulacao:
    """Os três critérios da população de referência, como dados (fonte única do SQL e do pandas)."""
    idade_minima: int = IDADE_MINIMA_REFERENCIA
    variavel_ocupacao: str = VARIAVEL_OCUPACAO
    codigo_ocupado: str = CODIGO_OCUPADO
    variavel_idade: str = VARIAVEL_IDADE
    variavel_renda: str = VARIAVEL_RENDA_REFERENCIA

    def sql(self, alias: str = "m") -> str:
        a = f"{alias}." if alias else ""
        return (f"({a}{self.variavel_ocupacao} = '{self.codigo_ocupado}' "
                f"AND {a}{self.variavel_idade} >= {self.idade_minima} "
                f"AND {a}{self.variavel_renda} > 0)")

    def mascara(self, df: pd.DataFrame) -> pd.Series:
        renda = pd.to_numeric(df[self.variavel_renda], errors="coerce")
        idade = pd.to_numeric(df[self.variavel_idade], errors="coerce")
        return ((df[self.variavel_ocupacao] == self.codigo_ocupado)
                & (idade >= self.idade_minima) & (renda > 0)).fillna(False).astype(bool)


REFERENCIA = DefinicaoPopulacao()
REFERENCIA_14MAIS = DefinicaoPopulacao(idade_minima=IDADE_MINIMA_SENSIBILIDADE)


def na_populacao_referencia(df: pd.DataFrame, idade_minima: int = IDADE_MINIMA_REFERENCIA) -> pd.Series:
    """Máscara booleana da população de referência sobre colunas BRUTAS do IBGE
    (`VD4002`, `V2009`, `VD4016`)."""
    return DefinicaoPopulacao(idade_minima=idade_minima).mascara(df)


def sql_colunas_criar_base(alias: str = "m", alias_deflator: str = "d") -> str:
    """Colunas que a `CRIAR_BASE` acrescenta: renda de referência (nominal e real) e as
    flags de população (18+ e 14+). Terminam com vírgula, para entrar no meio do SELECT."""
    a, d = alias, alias_deflator
    return f"""
        -- População e renda de referência (src/utils/populacao.py; Bloco F, 12/10/2026)
        {a}.{VARIAVEL_RENDA_REFERENCIA} AS {COLUNA_RENDA_NOMINAL},
        {a}.{VARIAVEL_RENDA_REFERENCIA} * {d}.deflator_habitual AS {COLUNA_RENDA_REAL},
        COALESCE({REFERENCIA.sql(a)}, FALSE) AS {COLUNA_FLAG},
        COALESCE({REFERENCIA_14MAIS.sql(a)}, FALSE) AS {COLUNA_FLAG_14},"""


def sql_colunas_renda_tabelas(alias: str = "m", alias_deflator: str = "d") -> str:
    """Colunas de renda que TODAS as tabelas de renda da `agregacoes_pnadc` usam, desde a
    regeneração da Onda 1 (13/10/2026; decisão do Ponto de parada 2: o Hub não fica com duas
    populações): `renda_habitual_*` = `VD4016` (trabalho principal) e `renda_efetiva_*` =
    `VD4017`, **só para quem está na população de referência** (NULL fora dela). Assim todo
    gerador que filtra "renda IS NOT NULL" passa a usar P1 sem mudar código. O recorte
    histórico (todos os trabalhos, 14+) fica em `renda_todos_trabalhos_*`, para sensibilidade
    (P3 do Bloco S). Terminam com vírgula."""
    a, d = alias, alias_deflator
    p1 = REFERENCIA.sql(a)
    return f"""
        -- Renda das tabelas = renda de referência restrita à população de referência (Onda 1)
        CASE WHEN {p1} THEN {a}.VD4016 END AS renda_habitual_nominal,
        CASE WHEN {p1} THEN {a}.VD4017 END AS renda_efetiva_nominal,
        CASE WHEN {p1} THEN {a}.VD4016 * {d}.deflator_habitual END AS renda_habitual_real,
        CASE WHEN {p1} THEN {a}.VD4017 * {d}.deflator_efetivo END AS renda_efetiva_real,
        -- Recorte histórico (até a Onda 1): todos os trabalhos, 14+, só para sensibilidade
        {a}.{VARIAVEL_RENDA_TODOS_TRABALHOS} AS renda_todos_trabalhos_nominal,
        {a}.{VARIAVEL_RENDA_TODOS_TRABALHOS} * {d}.deflator_habitual AS renda_todos_trabalhos_real,
        {a}.VD4020 * {d}.deflator_efetivo AS renda_todos_trabalhos_efetiva_real,"""


def filtro_sql(idade_minima: int = IDADE_MINIMA_REFERENCIA) -> str:
    """Predicado SQL sobre a tabela `base` (já com as colunas de `sql_colunas_criar_base`)."""
    if idade_minima == IDADE_MINIMA_REFERENCIA:
        return f"{COLUNA_FLAG} AND {COLUNA_RENDA_REAL} IS NOT NULL"
    if idade_minima == IDADE_MINIMA_SENSIBILIDADE:
        return f"{COLUNA_FLAG_14} AND {COLUNA_RENDA_REAL} IS NOT NULL"
    raise ValueError(f"idade mínima sem flag na base: {idade_minima} (use 18 ou 14)")


def resumo_exclusoes(df: pd.DataFrame, peso: str = "V1028", idade_minima: int = IDADE_MINIMA_REFERENCIA) -> pd.Series:
    """Composição ponderada (%) das pessoas com `idade_minima`+ anos entre: na população de
    referência / ocupado sem renda do trabalho principal / desocupado / fora da força.
    Ponto de partida do S0.1."""
    idade = pd.to_numeric(df[VARIAVEL_IDADE], errors="coerce")
    d = df[idade >= idade_minima]
    w = d[peso].astype(float)
    ref = DefinicaoPopulacao(idade_minima=idade_minima).mascara(d)
    ocup = d[VARIAVEL_OCUPACAO] == CODIGO_OCUPADO
    desoc = d[VARIAVEL_OCUPACAO] == "2"
    grupos = {
        "populacao_referencia": ref,
        "ocupado_sem_renda_trabalho_principal": ocup & ~ref,
        "desocupado": desoc,
        "fora_da_forca_ou_nao_aplicavel": ~ocup & ~desoc,
    }
    total = w.sum()
    return pd.Series({k: float(100 * w[m.fillna(False).to_numpy()].sum() / total) for k, m in grupos.items()})
