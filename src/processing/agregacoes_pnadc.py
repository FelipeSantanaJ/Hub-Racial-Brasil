"""Gera os datasets agregados da Fase 1 a partir da base extraída da PNAD Contínua.

Cruza Raça/Cor x Gênero x Faixa etária x Geografia (Brasil/Região/UF/São Paulo
capital-interior/RM São Paulo) para três temas: renda, escolaridade e
ocupação/desocupação. Lê o parquet particionado em data/raw/ (fora do git) e grava
datasets pequenos e já tratados em data/processed/ (versionados).

Decisões importantes (ver docs/PLANO.md para o histórico completo):
- `raca_cor` mantém as 6 categorias BRUTAS do IBGE (Branca/Preta/Parda/Amarela/
  Indígena/Ignorado) — não pré-agrega Preta+Parda em "Negra". Isso evita o bug que a
  função `aplicar_recorte1` de src/utils/pnadc_core.py tem (categoria não listada vira
  NaN silenciosamente) e mantém Amarela sempre explicitada. Quem consumir os dados e
  quiser o recorte "Negra" agregado soma Preta+Parda sob demanda.
- V2009 (idade) filtrado para >= 14 anos: as variáveis de mercado de trabalho
  (VD4001/VD4002) só existem para essa população, e as faixas etárias do escopo
  também começam em 14.
- Renda usa VD4019 (habitual) e VD4020 (efetivo), ambos "qualquer trabalho" (soma de
  todos os trabalhos da pessoa) — mais completo que só o trabalho principal
  (VD4016/VD4017). Saem tanto em valores NOMINAIS (R$ correntes do próprio
  trimestre) quanto REAIS (deflacionados pelo deflator oficial do IBGE — ver
  `src/ingestion/baixar_deflator.py` — a preços do trimestre de referência mais
  recente, hoje 2026 T2). Use as colunas `_real` para qualquer comparação entre
  trimestres diferentes; as `_nominal` só valem para comparar dentro do mesmo
  trimestre.

Uso:
    python -m src.processing.agregacoes_pnadc
"""
from pathlib import Path

import duckdb
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
PARQUET_GLOB = str(REPO_ROOT / "data" / "raw" / "pnadc_extraido" / "parquet" / "ano=*" / "trimestre=*" / "*.parquet")
DEFLATOR_PATH = str(REPO_ROOT / "data" / "processed" / "deflator_ibge.parquet")
OUTPUT_DIR = REPO_ROOT / "data" / "processed"

# (nivel_geografico, expressão SQL da coluna "geografia", filtro extra, group-by extra)
NIVEIS_GEOGRAFICOS = [
    ("brasil", "'Brasil'", "TRUE", None),
    ("regiao", "regiao", "TRUE", "regiao"),
    ("uf", "UF", "TRUE", "UF"),
    ("sp_capital_interior", "localizacao", "UF = '35'", "localizacao"),
    ("rm_sp", "CASE WHEN Capital IS NOT NULL THEN 'RM São Paulo - Capital' "
              "ELSE 'RM São Paulo - Não-capital (proxy ABC Paulista)' END",
     "RM_RIDE = '35'", "CASE WHEN Capital IS NOT NULL THEN 'RM São Paulo - Capital' "
                        "ELSE 'RM São Paulo - Não-capital (proxy ABC Paulista)' END"),
]

CRIAR_BASE = f"""
CREATE TEMP TABLE base AS
    SELECT
        m.ano, m.trimestre,
        m.UF,
        CASE m.UF
            WHEN '11' THEN 'Norte' WHEN '12' THEN 'Norte' WHEN '13' THEN 'Norte'
            WHEN '14' THEN 'Norte' WHEN '15' THEN 'Norte' WHEN '16' THEN 'Norte'
            WHEN '17' THEN 'Norte'
            WHEN '21' THEN 'Nordeste' WHEN '22' THEN 'Nordeste' WHEN '23' THEN 'Nordeste'
            WHEN '24' THEN 'Nordeste' WHEN '25' THEN 'Nordeste' WHEN '26' THEN 'Nordeste'
            WHEN '27' THEN 'Nordeste' WHEN '28' THEN 'Nordeste' WHEN '29' THEN 'Nordeste'
            WHEN '31' THEN 'Sudeste' WHEN '32' THEN 'Sudeste' WHEN '33' THEN 'Sudeste'
            WHEN '35' THEN 'Sudeste'
            WHEN '41' THEN 'Sul' WHEN '42' THEN 'Sul' WHEN '43' THEN 'Sul'
            WHEN '50' THEN 'Centro-Oeste' WHEN '51' THEN 'Centro-Oeste'
            WHEN '52' THEN 'Centro-Oeste' WHEN '53' THEN 'Centro-Oeste'
        END AS regiao,
        CASE WHEN m.Capital IS NOT NULL THEN 'Capital' ELSE 'Interior' END AS localizacao,
        m.Capital, m.RM_RIDE,
        CASE m.V2010
            WHEN '1' THEN 'Branca' WHEN '2' THEN 'Preta' WHEN '3' THEN 'Amarela'
            WHEN '4' THEN 'Parda' WHEN '5' THEN 'Indígena' WHEN '9' THEN 'Ignorado'
        END AS raca_cor,
        CASE m.V2007 WHEN '1' THEN 'Homem' WHEN '2' THEN 'Mulher' END AS sexo,
        CASE
            WHEN m.V2009 BETWEEN 14 AND 17 THEN '14-17'
            WHEN m.V2009 BETWEEN 18 AND 24 THEN '18-24'
            WHEN m.V2009 BETWEEN 25 AND 39 THEN '25-39'
            WHEN m.V2009 BETWEEN 40 AND 59 THEN '40-59'
            WHEN m.V2009 >= 60 THEN '60+'
        END AS faixa_etaria,
        CASE m.VD3004
            WHEN '1' THEN 'Sem instrução e menos de 1 ano de estudo'
            WHEN '2' THEN 'Fundamental incompleto ou equivalente'
            WHEN '3' THEN 'Fundamental completo ou equivalente'
            WHEN '4' THEN 'Médio incompleto ou equivalente'
            WHEN '5' THEN 'Médio completo ou equivalente'
            WHEN '6' THEN 'Superior incompleto ou equivalente'
            WHEN '7' THEN 'Superior completo'
        END AS nivel_instrucao,
        m.VD4001 AS forca_trabalho,      -- '1' = na força de trabalho, '2' = fora
        m.VD4002 AS condicao_ocupacao,   -- '1' = ocupada, '2' = desocupada
        m.VD4019 AS renda_habitual_nominal,
        m.VD4020 AS renda_efetiva_nominal,
        -- deflator do IBGE: MULTIPLICA o nominal para trazer a preços do trimestre
        -- de referência (ver src/ingestion/baixar_deflator.py) — não divide.
        m.VD4019 * d.deflator_habitual AS renda_habitual_real,
        m.VD4020 * d.deflator_efetivo AS renda_efetiva_real,
        m.V1028 AS peso
    FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1) AS m
    LEFT JOIN read_parquet('{DEFLATOR_PATH}') AS d
        ON m.ano = d.ano AND m.trimestre = d.trimestre AND m.UF = d.UF
    WHERE m.V2009 >= 14
"""


def _agregar_por_geografia(
    con: duckdb.DuckDBPyConnection, select_agregado: str, group_by_extra: str = "",
    incluir_faixa_etaria: bool = True,
) -> pd.DataFrame:
    """Roda uma query por nível geográfico (5 no total) e concatena os resultados.

    Rodar os 5 níveis como UNION ALL numa única query fazia o DuckDB (nesta
    versão/setup) travar por vários minutos, mesmo cada bloco isolado levando
    poucos segundos — 5 execuções separadas + concat em pandas é bem mais rápido
    e robusto na prática (ver docs/PLANO.md).

    `incluir_faixa_etaria=False` colapsa (pondera) essa dimensão em vez de
    agrupar por ela — precisa bater com o que `select_agregado` de fato lista,
    senão a query agrupa por uma coluna que não aparece no SELECT e devolve
    linhas "duplicadas" nas colunas visíveis (uma por faixa etária escondida).
    """
    partes = []
    for nivel, geografia_expr, filtro, group_extra in NIVEIS_GEOGRAFICOS:
        group_cols = "ano, trimestre, raca_cor, sexo"
        if incluir_faixa_etaria:
            group_cols += ", faixa_etaria"
        if group_extra:
            group_cols = f"{group_extra}, {group_cols}"
        if group_by_extra:
            group_cols = f"{group_cols}, {group_by_extra}"
        query = f"""
    SELECT '{nivel}' AS nivel_geografico, {geografia_expr} AS geografia,
           {select_agregado}
    FROM base
    WHERE {filtro}
    GROUP BY {group_cols}"""
        partes.append(con.execute(query).df())
    return pd.concat(partes, ignore_index=True)


def gerar_renda(con: duckdb.DuckDBPyConnection) -> None:
    select_agregado = """
           ano, trimestre, raca_cor, sexo, faixa_etaria,
           COUNT(*) AS n_amostra,
           SUM(peso) AS populacao_estimada,
           SUM(renda_habitual_nominal * peso)
               / NULLIF(SUM(peso) FILTER (WHERE renda_habitual_nominal IS NOT NULL), 0)
               AS renda_habitual_nominal_media,
           SUM(renda_efetiva_nominal * peso)
               / NULLIF(SUM(peso) FILTER (WHERE renda_efetiva_nominal IS NOT NULL), 0)
               AS renda_efetiva_nominal_media,
           SUM(renda_habitual_real * peso)
               / NULLIF(SUM(peso) FILTER (WHERE renda_habitual_real IS NOT NULL), 0)
               AS renda_habitual_real_media,
           SUM(renda_efetiva_real * peso)
               / NULLIF(SUM(peso) FILTER (WHERE renda_efetiva_real IS NOT NULL), 0)
               AS renda_efetiva_real_media"""
    df = _agregar_por_geografia(con, select_agregado)
    destino = OUTPUT_DIR / "renda.parquet"
    df.to_parquet(destino, index=False)
    print(f"renda.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def gerar_renda_por_escolaridade(con: duckdb.DuckDBPyConnection) -> None:
    """Cruza renda com nível de instrução — não existe em renda.parquet (que só tem
    faixa_etaria) nem em escolaridade.parquet (que não tem valores de renda)."""
    select_agregado = """
           ano, trimestre, raca_cor, sexo, nivel_instrucao,
           COUNT(*) AS n_amostra,
           SUM(peso) AS populacao_estimada,
           SUM(renda_habitual_real * peso)
               / NULLIF(SUM(peso) FILTER (WHERE renda_habitual_real IS NOT NULL), 0)
               AS renda_habitual_real_media,
           SUM(renda_efetiva_real * peso)
               / NULLIF(SUM(peso) FILTER (WHERE renda_efetiva_real IS NOT NULL), 0)
               AS renda_efetiva_real_media"""
    df = _agregar_por_geografia(
        con, select_agregado, group_by_extra="nivel_instrucao", incluir_faixa_etaria=False
    )
    df = df[df["nivel_instrucao"].notna()]
    destino = OUTPUT_DIR / "renda_por_escolaridade.parquet"
    df.to_parquet(destino, index=False)
    print(f"renda_por_escolaridade.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def gerar_escolaridade(con: duckdb.DuckDBPyConnection) -> None:
    select_agregado = """
           ano, trimestre, raca_cor, sexo, faixa_etaria, nivel_instrucao,
           COUNT(*) AS n_amostra,
           SUM(peso) AS populacao_estimada"""
    df = _agregar_por_geografia(con, select_agregado, group_by_extra="nivel_instrucao")
    df = df[df["nivel_instrucao"].notna()]
    destino = OUTPUT_DIR / "escolaridade.parquet"
    df.to_parquet(destino, index=False)
    print(f"escolaridade.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def gerar_ocupacao(con: duckdb.DuckDBPyConnection) -> None:
    select_agregado = """
           ano, trimestre, raca_cor, sexo, faixa_etaria,
           COUNT(*) AS n_amostra,
           SUM(peso) FILTER (WHERE forca_trabalho = '1') AS pop_forca_trabalho,
           SUM(peso) FILTER (WHERE condicao_ocupacao = '1') AS pop_ocupados,
           SUM(peso) FILTER (WHERE condicao_ocupacao = '2') AS pop_desocupados,
           100.0 * SUM(peso) FILTER (WHERE condicao_ocupacao = '2')
               / NULLIF(SUM(peso) FILTER (WHERE forca_trabalho = '1'), 0)
               AS taxa_desocupacao_pct"""
    df = _agregar_por_geografia(con, select_agregado)
    destino = OUTPUT_DIR / "ocupacao.parquet"
    df.to_parquet(destino, index=False)
    print(f"ocupacao.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    print("Materializando base (leitura única dos 58 trimestres)...", flush=True)
    con.execute(CRIAR_BASE)
    n_base = con.execute("SELECT COUNT(*) FROM base").fetchone()[0]
    print(f"base: {n_base:,} linhas (pessoas de 14+ anos)".replace(",", "."), flush=True)
    gerar_renda(con)
    gerar_escolaridade(con)
    gerar_renda_por_escolaridade(con)
    gerar_ocupacao(con)


if __name__ == "__main__":
    main()
