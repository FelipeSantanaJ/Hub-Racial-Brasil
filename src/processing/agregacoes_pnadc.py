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

from src.utils import pnadc_core

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
        CASE m.VD4011
            WHEN '01' THEN 'Diretores e gerentes'
            WHEN '02' THEN 'Profissionais das ciências e intelectuais'
            WHEN '03' THEN 'Técnicos e profissionais de nível médio'
            WHEN '04' THEN 'Trabalhadores de apoio administrativo'
            WHEN '05' THEN 'Trabalhadores dos serviços, vendedores do comércio'
            WHEN '06' THEN 'Trabalhadores agropecuários, florestais, da caça e pesca'
            WHEN '07' THEN 'Trabalhadores da construção, artes mecânicas e ofícios'
            WHEN '08' THEN 'Operadores de instalações e máquinas e montadores'
            WHEN '09' THEN 'Ocupações elementares'
            WHEN '10' THEN 'Forças armadas, policiais e bombeiros militares'
            WHEN '11' THEN 'Ocupações maldefinidas'
        END AS grupamento_ocupacional,
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


def gerar_decomposicao_hiato_ocupacional(con: duckdb.DuckDBPyConnection, n_trimestres: int = 8) -> None:
    """Decompõe o hiato de renda Branca vs. Negra: quanto sobra depois de controlar por
    faixa etária, depois + escolaridade, depois + ocupação (VD4011/grupamento_ocupacional)?

    Método: padronização direta. Pra cada conjunto de variáveis de controle, calcula a
    média ponderada de Branca e de Negra DENTRO de cada célula (ex.: faixa etária x
    escolaridade x ocupação), descarta células com amostra insuficiente de qualquer um dos
    dois grupos, e agrega de volta usando a distribuição de Negra nas células como peso —
    ou seja, "se Branca tivesse a mesma distribuição de idade/escolaridade/ocupação que
    Negra tem hoje, qual seria a média de Branca?". A diferença entre essa média ajustada e
    a média real de Negra é o hiato que control ainda não explica.

    Só entram pessoas OCUPADAS com ocupação identificada (grupamento_ocupacional não nulo)
    — é o universo em que a pergunta "mesma ocupação, ainda assim ganha menos?" faz sentido.
    Pool de `n_trimestres` mais recentes (não só o último) porque abrir por ocupação deixa
    as células menores.
    """
    micro = con.execute(f"""
        SELECT raca_cor, faixa_etaria, nivel_instrucao, grupamento_ocupacional,
               renda_habitual_real, peso
        FROM base
        WHERE raca_cor IN ('Branca', 'Preta', 'Parda')
          AND grupamento_ocupacional IS NOT NULL
          AND renda_habitual_real IS NOT NULL
          AND (ano, trimestre) IN (
              SELECT ano, trimestre FROM (SELECT DISTINCT ano, trimestre FROM base ORDER BY ano DESC, trimestre DESC LIMIT {n_trimestres})
          )
    """).df()
    micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})

    def media_pond(df, col="renda_habitual_real"):
        return (df[col] * df["peso"]).sum() / df["peso"].sum()

    def gap_padronizado(controles: list[str], n_minimo: int = 30) -> dict:
        if not controles:
            b = micro[micro["raca_cor"] == "Branca"]
            n = micro[micro["raca_cor"] == "Negra"]
            return {
                "controles": "nenhum (hiato bruto)",
                "media_branca_ajustada": media_pond(b),
                "media_negra": media_pond(n),
                "n_branca": len(b), "n_negra": len(n),
                "pct_amostra_negra_incluida": 100.0,
            }

        # Acumula Branca e Negra célula a célula, na mesma passada — só entram células
        # (combinações de `controles`) com amostra mínima dos DOIS grupos.
        soma_pond_branca = soma_peso_negra = soma_pond_negra = 0.0
        n_branca_total = n_negra_total = n_negra_incluida = 0
        for _, grupo in micro.groupby(controles, observed=True):
            gb = grupo[grupo["raca_cor"] == "Branca"]
            gn = grupo[grupo["raca_cor"] == "Negra"]
            n_branca_total += len(gb)
            n_negra_total += len(gn)
            if len(gb) < n_minimo or len(gn) < n_minimo:
                continue
            peso_negra_cel = gn["peso"].sum()
            soma_pond_branca += media_pond(gb) * peso_negra_cel
            soma_pond_negra += (gn["renda_habitual_real"] * gn["peso"]).sum()
            soma_peso_negra += peso_negra_cel
            n_negra_incluida += len(gn)

        return {
            "controles": " + ".join(controles),
            "media_branca_ajustada": soma_pond_branca / soma_peso_negra if soma_peso_negra else None,
            "media_negra": soma_pond_negra / soma_peso_negra if soma_peso_negra else None,
            "n_branca": n_branca_total, "n_negra": n_negra_total,
            "pct_amostra_negra_incluida": 100 * n_negra_incluida / n_negra_total if n_negra_total else 0,
        }

    resultados = []
    for controles in [[], ["faixa_etaria"], ["faixa_etaria", "nivel_instrucao"],
                       ["faixa_etaria", "nivel_instrucao", "grupamento_ocupacional"]]:
        r = gap_padronizado(controles)
        if r["media_branca_ajustada"] is not None and r["media_negra"] is not None:
            r["hiato_absoluto"] = r["media_branca_ajustada"] - r["media_negra"]
            r["hiato_percentual"] = 100 * r["hiato_absoluto"] / r["media_negra"]
        resultados.append(r)

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "decomposicao_hiato_ocupacional.parquet"
    df.to_parquet(destino, index=False)
    print(f"decomposicao_hiato_ocupacional.parquet: {len(df)} linhas (controles progressivos)", flush=True)
    print(df[["controles", "hiato_absoluto", "hiato_percentual", "pct_amostra_negra_incluida"]].to_string(index=False), flush=True)


def gerar_hiato_racial(con: duckdb.DuckDBPyConnection) -> None:
    """Hiato de renda Branca vs. Negra (Preta+Parda), trimestre a trimestre, COM teste
    de significância (Welch) — usa `pnadc_core.tabela_hiatos_significancia`, que precisa
    dos microdados (não das médias já agregadas) pra calcular erro padrão corretamente.
    Roda uma query por trimestre em vez de uma vez só pra manter a tabela intermediária
    pequena na memória do pandas (58 trimestres x algumas centenas de milhares de linhas
    cada seria pesado de concatenar tudo de uma vez)."""
    trimestres = con.execute("SELECT DISTINCT ano, trimestre FROM base ORDER BY ano, trimestre").df()

    resultados = []
    for _, row in trimestres.iterrows():
        ano, trimestre = int(row["ano"]), int(row["trimestre"])
        micro = con.execute(f"""
            SELECT raca_cor, renda_habitual_real, peso
            FROM base
            WHERE ano = {ano} AND trimestre = {trimestre}
              AND raca_cor IN ('Branca', 'Preta', 'Parda')
              AND renda_habitual_real IS NOT NULL
        """).df()
        if micro.empty:
            continue
        micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})

        tabela = pnadc_core.tabela_hiatos_significancia(
            micro, "renda_habitual_real", "raca_cor", grupo_referencia="Negra", peso="peso"
        )
        if "Branca" not in tabela.index:
            continue
        linha_branca = tabela.loc["Branca"]
        media_negra = tabela.loc["Negra", "media"]
        resultados.append({
            "ano": ano, "trimestre": trimestre,
            "renda_media_branca": linha_branca["media"],
            "renda_media_negra": media_negra,
            "hiato_absoluto": linha_branca["hiato_media"],
            "hiato_percentual": 100 * linha_branca["hiato_media"] / media_negra if media_negra else None,
            "ic_inferior": linha_branca["ic_inferior"],
            "ic_superior": linha_branca["ic_superior"],
            "p_valor": linha_branca["p_valor"],
            "significativo": linha_branca["significativo"],
        })

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "hiato_racial.parquet"
    df.to_parquet(destino, index=False)
    n_nao_significativo = (~df["significativo"]).sum()
    print(f"hiato_racial.parquet: {len(df):,} linhas".replace(",", "."), flush=True)
    if n_nao_significativo:
        print(
            f"  aviso: {n_nao_significativo} trimestre(s) com hiato Branca-Negra "
            "NÃO significativo a 95% (checar antes de destacar no gráfico)", flush=True,
        )


def gerar_renda_completa(con: duckdb.DuckDBPyConnection) -> None:
    """Cruza renda com raça x sexo x faixa_etaria x nivel_instrucao TODAS AO MESMO TEMPO
    — o cruzamento mais fino pedido. Só Brasil (as outras 4 dimensões já multiplicam
    bastante as combinações; abrir também por geografia deixaria a maioria das células
    com amostra residual)."""
    select_agregado = """
           ano, trimestre, raca_cor, sexo, faixa_etaria, nivel_instrucao,
           COUNT(*) AS n_amostra,
           SUM(peso) AS populacao_estimada,
           SUM(renda_habitual_real * peso)
               / NULLIF(SUM(peso) FILTER (WHERE renda_habitual_real IS NOT NULL), 0)
               AS renda_habitual_real_media"""
    query = f"""
        SELECT 'brasil' AS nivel_geografico, 'Brasil' AS geografia, {select_agregado}
        FROM base
        GROUP BY ano, trimestre, raca_cor, sexo, faixa_etaria, nivel_instrucao"""
    df = con.execute(query).df()
    df = df[df["nivel_instrucao"].notna()]
    destino = OUTPUT_DIR / "renda_completa.parquet"
    df.to_parquet(destino, index=False)
    print(f"renda_completa.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


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
    gerar_renda_completa(con)
    gerar_hiato_racial(con)
    gerar_decomposicao_hiato_ocupacional(con)
    gerar_ocupacao(con)


if __name__ == "__main__":
    main()
