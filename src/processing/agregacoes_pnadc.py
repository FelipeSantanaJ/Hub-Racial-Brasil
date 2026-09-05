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
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

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
        -- Geração: ano de nascimento APROXIMADO (ano da pesquisa - idade, sem levar em
        -- conta mês de nascimento x mês de entrevista — pode errar por 1 ano perto de
        -- cada fronteira). A PNAD Contínua é um corte transversal repetido, não um
        -- painel longitudinal de décadas — "pessoas de 14-17 anos" em trimestres
        -- diferentes são pessoas DIFERENTES chegando nessa idade, não as mesmas
        -- envelhecendo. Geração agrupa por ano de NASCIMENTO (coorte sintética/pseudo-
        -- painel, método de Deaton 1985) — isso sim segue aproximadamente o mesmo grupo
        -- de pessoas ao longo do tempo, envelhecendo dentro da janela 2012-2026.
        CASE
            WHEN (m.ano - m.V2009) < 1946 THEN 'Geração Silenciosa (antes de 1946)'
            WHEN (m.ano - m.V2009) BETWEEN 1946 AND 1964 THEN 'Baby Boomer (1946-1964)'
            WHEN (m.ano - m.V2009) BETWEEN 1965 AND 1980 THEN 'Geração X (1965-1980)'
            WHEN (m.ano - m.V2009) BETWEEN 1981 AND 1996 THEN 'Millennial (1981-1996)'
            WHEN (m.ano - m.V2009) BETWEEN 1997 AND 2012 THEN 'Geração Z (1997-2012)'
            ELSE 'Geração Alpha (2013+)'
        END AS geracao,
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
        -- posição na ocupação com carteira assinada: só definida p/ empregados
        -- (privado/doméstico/público) e militar/estatutário (sempre "protegido"); NULL
        -- p/ empregador, conta-própria e familiar auxiliar (o conceito não se aplica).
        -- VD4009 tem 10 categorias e vem ZERO-PADDED ('01'..'10' — mesmo padrão de
        -- VD4011) — checado direto no parquet bruto (values_counts) depois de um bug
        -- em que '1'/'2' sem padding não batia com nada e dava NULL silencioso.
        CASE m.VD4009
            WHEN '01' THEN TRUE WHEN '03' THEN TRUE WHEN '05' THEN TRUE WHEN '07' THEN TRUE
            WHEN '02' THEN FALSE WHEN '04' THEN FALSE WHEN '06' THEN FALSE
        END AS tem_carteira_assinada,
        -- setor de trabalho: Público = empregado público (c/ ou s/ carteira) + militar/
        -- estatutário; Privado = empregado privado/doméstico (c/ ou s/ carteira); NULL
        -- p/ empregador, conta-própria e familiar auxiliar (não é "público" nem
        -- "privado" no sentido de posição assalariada).
        CASE m.VD4009
            WHEN '05' THEN 'Público' WHEN '06' THEN 'Público' WHEN '07' THEN 'Público'
            WHEN '01' THEN 'Privado' WHEN '02' THEN 'Privado'
            WHEN '03' THEN 'Privado' WHEN '04' THEN 'Privado'
        END AS setor_trabalho,
        CASE m.VD4012 WHEN '1' THEN TRUE WHEN '2' THEN FALSE END AS contribui_previdencia,
        -- VD4010 tem 12 categorias e vem ZERO-PADDED ('01'..'12') — checado direto no
        -- parquet bruto antes de usar, mesmo padrão de bug já visto em VD4009/VD4011.
        CASE m.VD4010
            WHEN '01' THEN 'Agropecuária, produção florestal, pesca e aquicultura'
            WHEN '02' THEN 'Indústria geral'
            WHEN '03' THEN 'Construção'
            WHEN '04' THEN 'Comércio, reparação de veículos'
            WHEN '05' THEN 'Transporte, armazenagem e correio'
            WHEN '06' THEN 'Alojamento e alimentação'
            WHEN '07' THEN 'Informação, comunicação, financeiro, imobiliário e profissional'
            WHEN '08' THEN 'Administração pública, defesa e seguridade social'
            WHEN '09' THEN 'Educação, saúde humana e serviços sociais'
            WHEN '10' THEN 'Outros serviços'
            WHEN '11' THEN 'Serviços domésticos'
            WHEN '12' THEN 'Atividades mal definidas'
        END AS setor_atividade,
        CASE m.V3001 WHEN '1' THEN TRUE WHEN '2' THEN FALSE END AS alfabetizado,
        -- só definida p/ quem está FORA da força de trabalho (m.VD4001='2')
        CASE m.VD4003 WHEN '1' THEN TRUE WHEN '2' THEN FALSE END AS forca_trabalho_potencial,
        -- só existe o código '1' (demais = não aplicável, já NULL)
        CASE m.VD4005 WHEN '1' THEN TRUE END AS desalentado,
        m.VD4031 AS horas_habituais_todos_trabalhos,
        m.VD4035 AS horas_efetivas_todos_trabalhos,
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


def gerar_renda_por_geracao(con: duckdb.DuckDBPyConnection) -> None:
    """Cruza renda com geração (coorte de nascimento sintética — ver comentário em
    CRIAR_BASE). Resolve o viés de "não são as mesmas pessoas" da faixa etária: aqui
    cada geração é (aproximadamente) o MESMO grupo de pessoas nascidas numa janela,
    acompanhado envelhecendo dentro da janela de observação 2012-2026."""
    select_agregado = """
           ano, trimestre, raca_cor, sexo, geracao,
           COUNT(*) AS n_amostra,
           SUM(peso) AS populacao_estimada,
           SUM(renda_habitual_real * peso)
               / NULLIF(SUM(peso) FILTER (WHERE renda_habitual_real IS NOT NULL), 0)
               AS renda_habitual_real_media"""
    df = _agregar_por_geografia(
        con, select_agregado, group_by_extra="geracao", incluir_faixa_etaria=False
    )
    destino = OUTPUT_DIR / "renda_por_geracao.parquet"
    df.to_parquet(destino, index=False)
    print(f"renda_por_geracao.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def gerar_hiato_por_geracao(con: duckdb.DuckDBPyConnection) -> None:
    """Hiato Branca vs. Negra, trimestre a trimestre, DENTRO de cada geração — mesmo
    método de `gerar_hiato_racial` (Welch via microdados), mas mantendo a coorte de
    nascimento fixa em vez de misturar coortes diferentes que passam pela mesma faixa
    etária em anos diferentes. Só gerações com amostra suficiente em quase todos os 58
    trimestres entram (Baby Boomer, Geração X, Millennial, Geração Z — todas têm alguma
    parte da coorte com 14+ anos ao longo de toda a janela 2012-2026); Geração
    Silenciosa e Alpha ficam de fora por amostra residual/inexistente."""
    geracoes_com_amostra = [
        "Baby Boomer (1946-1964)", "Geração X (1965-1980)",
        "Millennial (1981-1996)", "Geração Z (1997-2012)",
    ]
    combinacoes = con.execute(f"""
        SELECT DISTINCT ano, trimestre, geracao FROM base
        WHERE geracao IN ({', '.join(f"'{g}'" for g in geracoes_com_amostra)})
        ORDER BY ano, trimestre, geracao
    """).df()

    resultados = []
    for _, row in combinacoes.iterrows():
        ano, trimestre, geracao = int(row["ano"]), int(row["trimestre"]), row["geracao"]
        micro = con.execute(f"""
            SELECT raca_cor, renda_habitual_real, peso
            FROM base
            WHERE ano = {ano} AND trimestre = {trimestre} AND geracao = '{geracao}'
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
            "ano": ano, "trimestre": trimestre, "geracao": geracao,
            "renda_media_branca": linha_branca["media"], "renda_media_negra": media_negra,
            "hiato_absoluto": linha_branca["hiato_media"],
            "hiato_percentual": 100 * linha_branca["hiato_media"] / media_negra if media_negra else None,
            "p_valor": linha_branca["p_valor"], "significativo": linha_branca["significativo"],
        })

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "hiato_por_geracao.parquet"
    df.to_parquet(destino, index=False)
    print(f"hiato_por_geracao.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


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
    # a lista progressiva (nenhum -> +idade -> +escolaridade -> +ocupação) conta uma
    # história de acumulação; "só ocupação" no final é uma comparação ISOLADA à parte
    # (sem idade/escolaridade já controladas) — responde direto "quanto ocupação
    # SOZINHA explica do hiato?", sem misturar com o que idade/escolaridade já
    # explicavam antes dela entrar na conta.
    for controles in [[], ["faixa_etaria"], ["faixa_etaria", "nivel_instrucao"],
                       ["faixa_etaria", "nivel_instrucao", "grupamento_ocupacional"],
                       ["grupamento_ocupacional"]]:
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


def gerar_decomposicao_oaxaca_blinder(con: duckdb.DuckDBPyConnection, n_trimestres: int = 8) -> None:
    """Versão com teste de significância formal da decomposição do hiato Branca-Negra:
    Oaxaca-Blinder (ver `pnadc_core.decomposicao_oaxaca_blinder`) em log(renda), com os
    mesmos controles progressivos de `gerar_decomposicao_hiato_ocupacional` (que usa
    padronização direta em R$ — mantida por ser mais fácil de explicar em R$/%; esta é
    o complemento estatisticamente testado, com a divisão explícita em parcela
    "explicada" por composição vs. "não-explicada" por diferença de retorno às mesmas
    características).

    Também decompõe a RIF (Recentered Influence Function, Firpo-Fortin-Lemieux 2009) de
    P10/P50/P90 da renda, com o conjunto completo de controles — responde se o hiato
    residual é maior no topo ou na base da distribuição ("teto de vidro" vs. "piso
    pegajoso"). Mesmo universo de `gerar_decomposicao_hiato_ocupacional`: ocupados com
    ocupação identificada, últimos `n_trimestres` agrupados.
    """
    micro = con.execute(f"""
        SELECT raca_cor, faixa_etaria, nivel_instrucao, grupamento_ocupacional,
               renda_habitual_real, peso
        FROM base
        WHERE raca_cor IN ('Branca', 'Preta', 'Parda')
          AND grupamento_ocupacional IS NOT NULL
          AND renda_habitual_real IS NOT NULL AND renda_habitual_real > 0
          AND (ano, trimestre) IN (
              SELECT ano, trimestre FROM (SELECT DISTINCT ano, trimestre FROM base ORDER BY ano DESC, trimestre DESC LIMIT {n_trimestres})
          )
    """).df()
    micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})
    micro["log_renda"] = np.log(micro["renda_habitual_real"])

    resultados = []
    # "grupamento_ocupacional" sozinho, no final, é uma comparação ISOLADA (sem idade/
    # escolaridade já controladas) — responde "quanto ocupação SOZINHA explica do
    # hiato, com teste de significância?", à parte da cadeia progressiva acima.
    for controles in [["faixa_etaria"], ["faixa_etaria", "nivel_instrucao"],
                       ["faixa_etaria", "nivel_instrucao", "grupamento_ocupacional"],
                       ["grupamento_ocupacional"]]:
        r = pnadc_core.decomposicao_oaxaca_blinder(
            micro, "log_renda", controles, "peso", "raca_cor", "Branca", "Negra"
        )
        r["controles"] = " + ".join(controles)
        r["ponto"] = "média"
        resultados.append(r)

    controles_completos = ["faixa_etaria", "nivel_instrucao", "grupamento_ocupacional"]
    for quantil, rotulo in [(0.1, "p10"), (0.5, "p50"), (0.9, "p90")]:
        rif, _, _ = pnadc_core.rif_quantil(micro["log_renda"].values, micro["peso"].values, quantil)
        micro_rif = micro.copy()
        micro_rif["rif"] = rif
        r = pnadc_core.decomposicao_oaxaca_blinder(
            micro_rif, "rif", controles_completos, "peso", "raca_cor", "Branca", "Negra"
        )
        r["controles"] = " + ".join(controles_completos)
        r["ponto"] = rotulo
        resultados.append(r)

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "decomposicao_oaxaca_blinder.parquet"
    df.to_parquet(destino, index=False)
    print(f"decomposicao_oaxaca_blinder.parquet: {len(df)} linhas", flush=True)
    print(df[["ponto", "controles", "pct_explicada", "pct_nao_explicada",
              "residuo_restrito_coef", "residuo_restrito_p_valor",
              "residuo_restrito_significativo"]].to_string(index=False), flush=True)


def gerar_perfil_topo10_racial(con: duckdb.DuckDBPyConnection) -> None:
    """Perfil demográfico de quem está no topo 10% de renda DENTRO de cada raça (Branca
    e Negra — Indígena fica de fora, amostra insuficiente pra um quantil confiável por
    trimestre), trimestre a trimestre.

    Importante: não é "top 10% do Brasil" (que seria quase todo Branca, dado o hiato) —
    é "top 10% ENTRE os brancos" vs. "top 10% ENTRE os negros", cada um com o limiar
    (P90) calculado dentro do próprio grupo. Composição por sexo, faixa etária, geração
    e nível de instrução — responde "quem chega ao topo dentro do próprio grupo racial,
    e como essa composição mudou ao longo do tempo?".

    Universo: pessoas ocupadas com renda habitual real > 0 (mesmo escopo da decomposição
    do hiato). Formato longo: uma linha por (trimestre, raça, dimensão, categoria).

    Nota sobre "topo 10%": renda autodeclarada tem "heaping" — concentração forte em
    valores redondos (R$1.000, R$2.000, R$5.000, R$10.000 etc., checado direto no
    parquet bruto). Quando o limiar do P90 cai bem em cima de um desses valores muito
    populosos, o filtro `>= limiar` inclui TODO mundo empatado naquele valor, capturando
    um pouco mais que 10% de fato (no 2026 T2, por exemplo, ~11,5% de Branca e ~12,8% de
    Negra — checado manualmente). Por isso a função grava `pct_populacao_capturada`
    (peso do grupo "topo" / peso total do grupo racial naquele trimestre) — use essa
    coluna pra saber o quão perto de "exatamente 10%" cada linha está de fato.
    """
    dimensoes = ["sexo", "faixa_etaria", "geracao", "nivel_instrucao"]
    trimestres = con.execute("SELECT DISTINCT ano, trimestre FROM base ORDER BY ano, trimestre").df()

    resultados = []
    for _, row in trimestres.iterrows():
        ano, trimestre = int(row["ano"]), int(row["trimestre"])
        micro = con.execute(f"""
            SELECT raca_cor, sexo, faixa_etaria, geracao, nivel_instrucao,
                   renda_habitual_real, peso
            FROM base
            WHERE ano = {ano} AND trimestre = {trimestre}
              AND raca_cor IN ('Branca', 'Preta', 'Parda')
              AND renda_habitual_real IS NOT NULL AND renda_habitual_real > 0
        """).df()
        if micro.empty:
            continue
        micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})

        for raca in ("Branca", "Negra"):
            grupo = micro[micro["raca_cor"] == raca]
            if len(grupo) < 100:  # amostra mínima pra um P90 confiável
                continue
            peso_grupo = grupo["peso"].sum()
            limiar = pnadc_core.quantil_ponderado(grupo["renda_habitual_real"], grupo["peso"], 0.9)
            topo = grupo[grupo["renda_habitual_real"] >= limiar]
            peso_topo = topo["peso"].sum()
            if peso_topo == 0:
                continue
            pct_capturado = 100 * peso_topo / peso_grupo
            for dimensao in dimensoes:
                for categoria, sub in topo.groupby(dimensao, observed=True):
                    resultados.append({
                        "ano": ano, "trimestre": trimestre, "raca_cor": raca,
                        "limiar_p90": limiar, "n_topo10": len(topo),
                        "pct_populacao_capturada": pct_capturado,
                        "dimensao": dimensao, "categoria": categoria,
                        "pct_do_topo10": 100 * sub["peso"].sum() / peso_topo,
                    })

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "perfil_topo10_racial.parquet"
    df.to_parquet(destino, index=False)
    print(f"perfil_topo10_racial.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


PERCENTIS_DECIS = [10, 20, 30, 40, 50, 60, 70, 80, 90]
VALORES_REFERENCIA_RENDA = [1000, 1500, 2000, 3000, 5000, 7500, 10000, 15000, 20000]


def gerar_funcao_quantil_racial(con: duckdb.DuckDBPyConnection) -> None:
    """Função quantil da renda (percentil -> R$) e sua INVERSA (R$ -> percentil),
    calculadas DENTRO de cada raça (Branca e Negra — Indígena fica de fora, mesma razão
    de sempre: amostra insuficiente pra deciles confiáveis por trimestre), trimestre a
    trimestre. Complementa `gerar_perfil_quartis_racial` (que olha QUEM está em cada
    fatia — composição demográfica) respondendo em R$ de fato:

    - "Percentil -> R$": os 10% mais pobres entre os negros ganham quanto, comparado
      aos 10% mais pobres entre os brancos? E os 20% mais pobres? E assim por diante,
      até os 90% mais ricos — a função quantil inteira das duas raças, lado a lado.
    - "R$ -> percentil" (inversa): quem ganha R$3.000 está em que posição da
      distribuição de CADA raça? A mesma quantia pode ser mediana pra uma raça e estar
      entre os mais ricos da outra, dado o hiato.

    Universo: ocupados com renda habitual real > 0 (mesmo escopo de sempre — igual à
    decomposição do hiato e ao topo 10%). Gera dois parquets, cada um em formato longo.
    """
    trimestres = con.execute("SELECT DISTINCT ano, trimestre FROM base ORDER BY ano, trimestre").df()

    resultado_percentil_para_valor = []
    resultado_valor_para_percentil = []
    for _, row in trimestres.iterrows():
        ano, trimestre = int(row["ano"]), int(row["trimestre"])
        micro = con.execute(f"""
            SELECT raca_cor, renda_habitual_real, peso
            FROM base
            WHERE ano = {ano} AND trimestre = {trimestre}
              AND raca_cor IN ('Branca', 'Preta', 'Parda')
              AND renda_habitual_real IS NOT NULL AND renda_habitual_real > 0
        """).df()
        if micro.empty:
            continue
        micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})

        for raca in ("Branca", "Negra"):
            grupo = micro[micro["raca_cor"] == raca]
            if len(grupo) < 100:
                continue
            valores = grupo["renda_habitual_real"].to_numpy()
            pesos = grupo["peso"].to_numpy()
            for p in PERCENTIS_DECIS:
                valor = pnadc_core.quantil_ponderado(valores, pesos, p / 100)
                resultado_percentil_para_valor.append({
                    "ano": ano, "trimestre": trimestre, "raca_cor": raca,
                    "percentil": p, "renda_no_percentil": valor,
                })
            for valor_ref in VALORES_REFERENCIA_RENDA:
                percentil_correspondente = pnadc_core.percentil_ponderado_de_valor(valores, pesos, valor_ref)
                resultado_valor_para_percentil.append({
                    "ano": ano, "trimestre": trimestre, "raca_cor": raca,
                    "valor_referencia": valor_ref, "percentil_correspondente": percentil_correspondente,
                })

    df1 = pd.DataFrame(resultado_percentil_para_valor)
    destino1 = OUTPUT_DIR / "funcao_quantil_racial.parquet"
    df1.to_parquet(destino1, index=False)
    print(f"funcao_quantil_racial.parquet: {len(df1):,} linhas".replace(",", "."), flush=True)

    df2 = pd.DataFrame(resultado_valor_para_percentil)
    destino2 = OUTPUT_DIR / "percentil_de_valor_racial.parquet"
    df2.to_parquet(destino2, index=False)
    print(f"percentil_de_valor_racial.parquet: {len(df2):,} linhas".replace(",", "."), flush=True)


def gerar_perfil_quartis_racial(con: duckdb.DuckDBPyConnection) -> None:
    """Perfil demográfico de cada QUARTIL de renda (Q1 = 25% que menos ganham, ..., Q4 =
    25% que mais ganham) DENTRO de cada raça (Branca e Negra — Indígena fica de fora,
    mesma razão do topo 10%: amostra insuficiente pra 3 quantis confiáveis por
    trimestre), trimestre a trimestre.

    Generaliza `gerar_perfil_topo10_racial` (que só olha o topo 10%, um recorte mais
    estreito — P90, não P75) pros 4 quartis de uma vez — permite comparar a composição
    demográfica de CADA fatia da distribuição de renda entre Negra e Branca, não só quem
    está no topo. Limiares (P25/P50/P75) calculados DENTRO de cada raça separadamente —
    "Q1 de Branca" e "Q1 de Negra" não têm o mesmo intervalo de R$, cada um é "os 25% que
    menos ganham dentro do próprio grupo".

    Universo/dimensões/formato: iguais a `gerar_perfil_topo10_racial`. Mesma ressalva de
    heaping documentada lá — `pct_populacao_capturada` aqui é o peso de cada quartil
    sobre o total do grupo (deveria ficar perto de 25%, pode desviar um pouco pela mesma
    razão: renda autodeclarada concentrada em valores redondos).
    """
    dimensoes = ["sexo", "faixa_etaria", "geracao", "nivel_instrucao"]
    trimestres = con.execute("SELECT DISTINCT ano, trimestre FROM base ORDER BY ano, trimestre").df()

    resultados = []
    for _, row in trimestres.iterrows():
        ano, trimestre = int(row["ano"]), int(row["trimestre"])
        micro = con.execute(f"""
            SELECT raca_cor, sexo, faixa_etaria, geracao, nivel_instrucao,
                   renda_habitual_real, peso
            FROM base
            WHERE ano = {ano} AND trimestre = {trimestre}
              AND raca_cor IN ('Branca', 'Preta', 'Parda')
              AND renda_habitual_real IS NOT NULL AND renda_habitual_real > 0
        """).df()
        if micro.empty:
            continue
        micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})

        for raca in ("Branca", "Negra"):
            grupo = micro[micro["raca_cor"] == raca].copy()
            if len(grupo) < 200:  # amostra mínima maior — 3 limiares em vez de 1
                continue
            peso_grupo = grupo["peso"].sum()
            p25 = pnadc_core.quantil_ponderado(grupo["renda_habitual_real"], grupo["peso"], 0.25)
            p50 = pnadc_core.quantil_ponderado(grupo["renda_habitual_real"], grupo["peso"], 0.50)
            p75 = pnadc_core.quantil_ponderado(grupo["renda_habitual_real"], grupo["peso"], 0.75)
            grupo["quartil"] = np.select(
                [grupo["renda_habitual_real"] < p25,
                 grupo["renda_habitual_real"] < p50,
                 grupo["renda_habitual_real"] < p75],
                ["Q1 (25% que menos ganham)", "Q2", "Q3"],
                default="Q4 (25% que mais ganham)",
            )
            for quartil, fatia in grupo.groupby("quartil", observed=True):
                peso_fatia = fatia["peso"].sum()
                if peso_fatia == 0:
                    continue
                pct_capturado = 100 * peso_fatia / peso_grupo
                for dimensao in dimensoes:
                    for categoria, sub in fatia.groupby(dimensao, observed=True):
                        resultados.append({
                            "ano": ano, "trimestre": trimestre, "raca_cor": raca,
                            "quartil": quartil, "n_quartil": len(fatia),
                            "pct_populacao_capturada": pct_capturado,
                            "dimensao": dimensao, "categoria": categoria,
                            "pct_do_quartil": 100 * sub["peso"].sum() / peso_fatia,
                        })

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "perfil_quartis_racial.parquet"
    df.to_parquet(destino, index=False)
    print(f"perfil_quartis_racial.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def gerar_hiato_regional(con: duckdb.DuckDBPyConnection) -> None:
    """Hiato Branca vs. Negra por Região, trimestre a trimestre, com teste de
    significância (Welch) — mesmo método de `gerar_hiato_racial`, quebrado por região
    pra ver se a desigualdade regional do Brasil (Norte/Nordeste vs. Sul/Sudeste)
    também aparece no hiato especificamente racial, ou se é uniforme pelo país."""
    combinacoes = con.execute(
        "SELECT DISTINCT ano, trimestre, regiao FROM base WHERE regiao IS NOT NULL "
        "ORDER BY ano, trimestre, regiao"
    ).df()

    resultados = []
    for _, row in combinacoes.iterrows():
        ano, trimestre, regiao = int(row["ano"]), int(row["trimestre"]), row["regiao"]
        micro = con.execute(f"""
            SELECT raca_cor, renda_habitual_real, peso
            FROM base
            WHERE ano = {ano} AND trimestre = {trimestre} AND regiao = '{regiao}'
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
            "ano": ano, "trimestre": trimestre, "regiao": regiao,
            "renda_media_branca": linha_branca["media"], "renda_media_negra": media_negra,
            "hiato_absoluto": linha_branca["hiato_media"],
            "hiato_percentual": 100 * linha_branca["hiato_media"] / media_negra if media_negra else None,
            "p_valor": linha_branca["p_valor"], "significativo": linha_branca["significativo"],
        })

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "hiato_regional.parquet"
    df.to_parquet(destino, index=False)
    print(f"hiato_regional.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def gerar_hiato_setor_publico_privado(con: duckdb.DuckDBPyConnection) -> None:
    """Hiato Branca vs. Negra DENTRO do setor Público e DENTRO do setor Privado,
    separadamente, trimestre a trimestre — mesmo método de `gerar_hiato_racial`. Testa
    uma hipótese conhecida na literatura de economia do trabalho brasileira: como
    salário de concurso público segue tabela padronizada (não negociação individual), o
    hiato racial deveria ser menor lá do que no setor privado. Só entram empregados com
    posição classificável como Público/Privado (`setor_trabalho`) — empregador,
    conta-própria e familiar auxiliar ficam de fora (não se aplica)."""
    combinacoes = con.execute(
        "SELECT DISTINCT ano, trimestre, setor_trabalho FROM base WHERE setor_trabalho IS NOT NULL "
        "ORDER BY ano, trimestre, setor_trabalho"
    ).df()

    resultados = []
    for _, row in combinacoes.iterrows():
        ano, trimestre, setor = int(row["ano"]), int(row["trimestre"]), row["setor_trabalho"]
        micro = con.execute(f"""
            SELECT raca_cor, renda_habitual_real, peso
            FROM base
            WHERE ano = {ano} AND trimestre = {trimestre} AND setor_trabalho = '{setor}'
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
            "ano": ano, "trimestre": trimestre, "setor_trabalho": setor,
            "renda_media_branca": linha_branca["media"], "renda_media_negra": media_negra,
            "hiato_absoluto": linha_branca["hiato_media"],
            "hiato_percentual": 100 * linha_branca["hiato_media"] / media_negra if media_negra else None,
            "p_valor": linha_branca["p_valor"], "significativo": linha_branca["significativo"],
        })

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "hiato_setor_publico_privado.parquet"
    df.to_parquet(destino, index=False)
    print(f"hiato_setor_publico_privado.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def gerar_indice_segregacao_ocupacional(con: duckdb.DuckDBPyConnection) -> None:
    """Índice de dissimilaridade de Duncan (1955) entre a distribuição ocupacional
    (grupamento_ocupacional/VD4011) de Branca e de Negra, trimestre a trimestre.

    D = 0,5 * soma_i |p_i_branca - p_i_negra|, p_i = fração ponderada do grupo ocupada
    na categoria i. Interpretação: % de um dos grupos que precisaria trocar de
    categoria ocupacional pra igualar a distribuição do outro — mede segregação
    ocupacional em si, independente do efeito disso na renda (já coberto pela
    decomposição do hiato). Indígena fica de fora da série trimestral — amostra
    pequena demais pra uma distribuição de 11 categorias trimestre a trimestre.
    """
    df = con.execute("""
        SELECT ano, trimestre, raca_cor, grupamento_ocupacional, SUM(peso) AS peso
        FROM base
        WHERE raca_cor IN ('Branca', 'Preta', 'Parda') AND grupamento_ocupacional IS NOT NULL
        GROUP BY ano, trimestre, raca_cor, grupamento_ocupacional
    """).df()
    df["raca_cor"] = df["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})
    df = df.groupby(["ano", "trimestre", "raca_cor", "grupamento_ocupacional"], as_index=False)["peso"].sum()

    resultados = []
    for (ano, trimestre), grupo in df.groupby(["ano", "trimestre"]):
        pivot = grupo.pivot_table(index="grupamento_ocupacional", columns="raca_cor", values="peso", fill_value=0.0)
        if "Branca" not in pivot.columns or "Negra" not in pivot.columns:
            continue
        p_branca = pivot["Branca"] / pivot["Branca"].sum()
        p_negra = pivot["Negra"] / pivot["Negra"].sum()
        duncan = 0.5 * (p_branca - p_negra).abs().sum()
        resultados.append({"ano": int(ano), "trimestre": int(trimestre), "indice_duncan_branca_negra": duncan})

    resultado_df = pd.DataFrame(resultados).sort_values(["ano", "trimestre"])
    destino = OUTPUT_DIR / "segregacao_ocupacional.parquet"
    resultado_df.to_parquet(destino, index=False)
    print(f"segregacao_ocupacional.parquet: {len(resultado_df)} linhas", flush=True)
    print(f"  Índice de Duncan Branca-Negra (trimestre mais recente): "
          f"{resultado_df['indice_duncan_branca_negra'].iloc[-1] * 100:.1f}%", flush=True)


def gerar_segregacao_setorial(con: duckdb.DuckDBPyConnection) -> None:
    """Índice de dissimilaridade de Duncan (1955) entre a distribuição por SETOR de
    atividade econômica (setor_atividade/VD4010) de Branca e de Negra, trimestre a
    trimestre — paralelo direto de `gerar_indice_segregacao_ocupacional`, só que por
    setor econômico (agropecuária/indústria/comércio/serviços/administração pública)
    em vez de por cargo/grupamento ocupacional. Mesma fórmula, mesma interpretação, e
    Indígena fica de fora pela mesma razão (amostra pequena demais pra uma distribuição
    de 12 categorias trimestre a trimestre)."""
    df = con.execute("""
        SELECT ano, trimestre, raca_cor, setor_atividade, SUM(peso) AS peso
        FROM base
        WHERE raca_cor IN ('Branca', 'Preta', 'Parda') AND setor_atividade IS NOT NULL
        GROUP BY ano, trimestre, raca_cor, setor_atividade
    """).df()
    df["raca_cor"] = df["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})
    df = df.groupby(["ano", "trimestre", "raca_cor", "setor_atividade"], as_index=False)["peso"].sum()

    resultados = []
    for (ano, trimestre), grupo in df.groupby(["ano", "trimestre"]):
        pivot = grupo.pivot_table(index="setor_atividade", columns="raca_cor", values="peso", fill_value=0.0)
        if "Branca" not in pivot.columns or "Negra" not in pivot.columns:
            continue
        p_branca = pivot["Branca"] / pivot["Branca"].sum()
        p_negra = pivot["Negra"] / pivot["Negra"].sum()
        duncan = 0.5 * (p_branca - p_negra).abs().sum()
        resultados.append({"ano": int(ano), "trimestre": int(trimestre), "indice_duncan_branca_negra": duncan})

    resultado_df = pd.DataFrame(resultados).sort_values(["ano", "trimestre"])
    destino = OUTPUT_DIR / "segregacao_setorial.parquet"
    resultado_df.to_parquet(destino, index=False)
    print(f"segregacao_setorial.parquet: {len(resultado_df)} linhas", flush=True)
    print(f"  Índice de Duncan setorial Branca-Negra (trimestre mais recente): "
          f"{resultado_df['indice_duncan_branca_negra'].iloc[-1] * 100:.1f}%", flush=True)


EVENTOS_ESTRUTURAIS = {
    "reforma_trabalhista_2017": (2017, 3),
    "reforma_previdencia_2019": (2019, 4),
    "recessao_2015": (2015, 1),
}


def gerar_quebra_estrutural() -> None:
    """Testa formalmente se a trajetória do hiato racial (%) muda de patamar/inclinação
    ao redor de 3 eventos candidatos já apontados como possíveis pontos de inflexão em
    docs/LIMITACOES_E_METODOLOGIA.md: reforma trabalhista (2017 T3), reforma da
    previdência (2019 T4) e a recessão de 2015-2016 (2015 T1).

    Método: OLS de hiato_percentual em índice de trimestre + dummy pós-evento +
    interação (índice x dummy) na série completa de `hiato_racial.parquet`. Testa se a
    dummy (mudança de patamar) OU a interação (mudança de inclinação) é
    estatisticamente significativa — equivalente a um teste de Chow simplificado (uma
    quebra conhecida a priori, não busca por múltiplas quebras como Bai-Perron). Roda
    DEPOIS de `gerar_hiato_racial` (lê o parquet que ela gera).
    """
    hiato = pd.read_parquet(OUTPUT_DIR / "hiato_racial.parquet").sort_values(["ano", "trimestre"]).reset_index(drop=True)
    hiato["indice_trimestre"] = range(len(hiato))

    resultados = []
    for nome_evento, (ano_evento, trimestre_evento) in EVENTOS_ESTRUTURAIS.items():
        hiato["pos_evento"] = (
            (hiato["ano"] > ano_evento) | ((hiato["ano"] == ano_evento) & (hiato["trimestre"] >= trimestre_evento))
        ).astype(int)
        if hiato["pos_evento"].sum() < 4 or (1 - hiato["pos_evento"]).sum() < 4:
            continue  # evento perto demais da borda da série pra ter poder estatístico
        modelo = smf.ols("hiato_percentual ~ indice_trimestre * pos_evento", data=hiato).fit()
        resultados.append({
            "evento": nome_evento, "ano_evento": ano_evento, "trimestre_evento": trimestre_evento,
            "coef_mudanca_patamar": modelo.params["pos_evento"],
            "p_valor_mudanca_patamar": modelo.pvalues["pos_evento"],
            "coef_mudanca_inclinacao": modelo.params["indice_trimestre:pos_evento"],
            "p_valor_mudanca_inclinacao": modelo.pvalues["indice_trimestre:pos_evento"],
            "significativo_a_5pct": bool(
                (modelo.pvalues["pos_evento"] < 0.05) or (modelo.pvalues["indice_trimestre:pos_evento"] < 0.05)
            ),
        })

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "quebra_estrutural.parquet"
    df.to_parquet(destino, index=False)
    print(f"quebra_estrutural.parquet: {len(df)} linhas", flush=True)
    print(df.to_string(index=False), flush=True)


def gerar_informalidade(con: duckdb.DuckDBPyConnection) -> None:
    """% com carteira assinada (entre empregados) e % contribuinte de previdência
    (entre TODOS os ocupados, cobre também conta-própria/empregador) por raça x gênero
    x faixa etária — ver decodificação de VD4009/VD4012 em
    docs/LIMITACOES_E_METODOLOGIA.md."""
    select_agregado = """
           ano, trimestre, raca_cor, sexo, faixa_etaria,
           COUNT(*) AS n_amostra,
           SUM(peso) AS populacao_estimada,
           SUM(peso) FILTER (WHERE tem_carteira_assinada IS NOT NULL) AS pop_empregados,
           100.0 * SUM(peso) FILTER (WHERE tem_carteira_assinada)
               / NULLIF(SUM(peso) FILTER (WHERE tem_carteira_assinada IS NOT NULL), 0)
               AS pct_com_carteira,
           100.0 * SUM(peso) FILTER (WHERE contribui_previdencia)
               / NULLIF(SUM(peso) FILTER (WHERE contribui_previdencia IS NOT NULL), 0)
               AS pct_contribui_previdencia"""
    df = _agregar_por_geografia(con, select_agregado)
    destino = OUTPUT_DIR / "informalidade.parquet"
    df.to_parquet(destino, index=False)
    print(f"informalidade.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def gerar_horas_trabalhadas(con: duckdb.DuckDBPyConnection) -> None:
    """Horas habitualmente trabalhadas (todos os trabalhos, VD4031) e uma renda-por-
    hora aproximada (renda habitual mensal / (horas semanais x 4,345 semanas/mês)) por
    raça x gênero x faixa etária — testa se o hiato de renda diminui quando controlado
    por jornada (relevante sobretudo pro hiato de GÊNERO, historicamente ligado a
    jornada menor por trabalho de cuidado não-remunerado)."""
    select_agregado = """
           ano, trimestre, raca_cor, sexo, faixa_etaria,
           COUNT(*) AS n_amostra,
           SUM(peso) AS populacao_estimada,
           SUM(horas_habituais_todos_trabalhos * peso)
               / NULLIF(SUM(peso) FILTER (WHERE horas_habituais_todos_trabalhos IS NOT NULL), 0)
               AS horas_semanais_media,
           SUM((renda_habitual_real / NULLIF(horas_habituais_todos_trabalhos * 4.345, 0)) * peso)
               / NULLIF(SUM(peso) FILTER (WHERE renda_habitual_real IS NOT NULL
                                            AND horas_habituais_todos_trabalhos > 0), 0)
               AS renda_por_hora_real_media"""
    df = _agregar_por_geografia(con, select_agregado)
    destino = OUTPUT_DIR / "horas_trabalhadas.parquet"
    df.to_parquet(destino, index=False)
    print(f"horas_trabalhadas.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def gerar_alfabetizacao(con: duckdb.DuckDBPyConnection) -> None:
    """% alfabetizado (V3001) por raça x gênero x faixa etária, Brasil apenas (célula
    fina demais pra abrir também por geografia com qualidade). Capta analfabetismo
    residual em cohorts mais velhas — complementa nivel_instrucao (que só mostra o
    nível já CONCLUÍDO).

    NÃO inclui frequência escolar (V3014): checado direto no parquet bruto e a
    cobertura de V3014 pra população 14-17 anos é de só ~6-8% em VÁRIOS trimestres
    (2018 a 2026), não os ~95% de V3001 nem os ~20% que uma rotação padrão de painel
    (1 de 5 grupos por trimestre) explicaria — não conseguimos confirmar se é uma
    subamostra aleatória (estimativa válida, só com IC mais largo) ou um recorte
    enviesado (ex.: só quem não trabalha) dentro do orçamento desta rodada. Descartado
    até investigar a regra de coleta exata do IBGE pra essa variável especificamente —
    ver docs/LIMITACOES_E_METODOLOGIA.md."""
    query = """
        SELECT 'brasil' AS nivel_geografico, 'Brasil' AS geografia,
               ano, trimestre, raca_cor, sexo, faixa_etaria,
               COUNT(*) AS n_amostra,
               SUM(peso) AS populacao_estimada,
               100.0 * SUM(peso) FILTER (WHERE alfabetizado)
                   / NULLIF(SUM(peso) FILTER (WHERE alfabetizado IS NOT NULL), 0)
                   AS pct_alfabetizado
        FROM base
        GROUP BY ano, trimestre, raca_cor, sexo, faixa_etaria
    """
    df = con.execute(query).df()
    destino = OUTPUT_DIR / "alfabetizacao.parquet"
    df.to_parquet(destino, index=False)
    print(f"alfabetizacao.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def gerar_desalento_subutilizacao(con: duckdb.DuckDBPyConnection) -> None:
    """Vai além da taxa de desocupação simples (já em ocupacao.parquet): entre quem
    está FORA da força de trabalho, qual % está na 'força de trabalho potencial'
    (queria e poderia trabalhar, mas não é contada como desocupada) e qual % está
    desalentada (desistiu de procurar) — a literatura aponta que isso afeta
    desproporcionalmente a população negra. Por raça x gênero x faixa etária."""
    select_agregado = """
           ano, trimestre, raca_cor, sexo, faixa_etaria,
           SUM(peso) AS populacao_estimada,
           SUM(peso) FILTER (WHERE forca_trabalho = '2') AS pop_fora_forca_trabalho,
           100.0 * SUM(peso) FILTER (WHERE forca_trabalho_potencial)
               / NULLIF(SUM(peso) FILTER (WHERE forca_trabalho_potencial IS NOT NULL), 0)
               AS pct_forca_trabalho_potencial,
           100.0 * SUM(peso) FILTER (WHERE desalentado)
               / NULLIF(SUM(peso) FILTER (WHERE forca_trabalho = '2'), 0)
               AS pct_desalento"""
    df = _agregar_por_geografia(con, select_agregado)
    destino = OUTPUT_DIR / "desalento_subutilizacao.parquet"
    df.to_parquet(destino, index=False)
    print(f"desalento_subutilizacao.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def gerar_sobrequalificacao(con: duckdb.DuckDBPyConnection) -> None:
    """% de pessoas com Superior completo que estão em 'Ocupações elementares'
    (grupamento_ocupacional/VD4011, categoria 09 — o grupo ISCO major 9, proxy padrão
    de sobre-qualificação/mismatch credencial-ocupação na literatura de economia do
    trabalho) — mesmo diploma, resultado profissional diferente por raça? Por raça x
    gênero, Brasil + geografias."""
    select_agregado = """
           ano, trimestre, raca_cor, sexo,
           COUNT(*) AS n_amostra,
           SUM(peso) AS populacao_estimada,
           SUM(peso) FILTER (WHERE nivel_instrucao = 'Superior completo' AND grupamento_ocupacional IS NOT NULL)
               AS pop_superior_completo_ocupado,
           100.0 * SUM(peso) FILTER (WHERE nivel_instrucao = 'Superior completo'
                                        AND grupamento_ocupacional = 'Ocupações elementares')
               / NULLIF(SUM(peso) FILTER (WHERE nivel_instrucao = 'Superior completo'
                                             AND grupamento_ocupacional IS NOT NULL), 0)
               AS pct_sobrequalificado"""
    df = _agregar_por_geografia(con, select_agregado, incluir_faixa_etaria=False)
    destino = OUTPUT_DIR / "sobrequalificacao.parquet"
    df.to_parquet(destino, index=False)
    print(f"sobrequalificacao.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


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


def gerar_hiato_preta_parda(con: duckdb.DuckDBPyConnection) -> None:
    """Espelha `gerar_hiato_racial`, mas DENTRO da população negra: Preta vs. Parda,
    sem combinar as duas (a regra do projeto é nunca pré-combinar Preta+Parda na base —
    só combina na hora de montar 'Negra' pra comparar com Branca/Indígena). Referência é
    Parda (o maior dos dois grupos); o hiato reportado é o quanto Preta ganha a mais/menos
    que Parda."""
    trimestres = con.execute("SELECT DISTINCT ano, trimestre FROM base ORDER BY ano, trimestre").df()

    resultados = []
    for _, row in trimestres.iterrows():
        ano, trimestre = int(row["ano"]), int(row["trimestre"])
        micro = con.execute(f"""
            SELECT raca_cor, renda_habitual_real, peso
            FROM base
            WHERE ano = {ano} AND trimestre = {trimestre}
              AND raca_cor IN ('Preta', 'Parda')
              AND renda_habitual_real IS NOT NULL
        """).df()
        if micro.empty:
            continue

        tabela = pnadc_core.tabela_hiatos_significancia(
            micro, "renda_habitual_real", "raca_cor", grupo_referencia="Parda", peso="peso"
        )
        if "Preta" not in tabela.index:
            continue
        linha_preta = tabela.loc["Preta"]
        media_parda = tabela.loc["Parda", "media"]
        resultados.append({
            "ano": ano, "trimestre": trimestre,
            "renda_media_preta": linha_preta["media"],
            "renda_media_parda": media_parda,
            "hiato_absoluto": linha_preta["hiato_media"],
            "hiato_percentual": 100 * linha_preta["hiato_media"] / media_parda if media_parda else None,
            "ic_inferior": linha_preta["ic_inferior"],
            "ic_superior": linha_preta["ic_superior"],
            "p_valor": linha_preta["p_valor"],
            "significativo": linha_preta["significativo"],
        })

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "hiato_preta_parda.parquet"
    df.to_parquet(destino, index=False)
    n_nao_significativo = (~df["significativo"]).sum()
    print(f"hiato_preta_parda.parquet: {len(df):,} linhas".replace(",", "."), flush=True)
    if n_nao_significativo:
        print(
            f"  aviso: {n_nao_significativo} trimestre(s) com hiato Preta-Parda "
            "NÃO significativo a 95% (checar antes de destacar no gráfico)", flush=True,
        )


# As 11 combinações de dimensões (além de raça sozinha, já coberta por
# gerar_hiato_racial/gerar_hiato_preta_parda acima) pedidas pra seção "Renda média" do
# PPT — cada uma vira um parquet de hiato com teste de Welch, pro cruzamento raça x
# essas dimensões. Roda num só trimestre (o mais recente) em vez da série histórica
# inteira: gerar Welch por célula pra TODAS as combinações em TODOS os 58 trimestres
# seria caro e a maioria das células já fica fina o bastante com 1 trimestre só quando
# cruza 3 dimensões (sexo x faixa/geração x escolaridade).
DIMENSOES_HIATO_MULTIDIMENSIONAL: list[tuple[str, ...]] = [
    ("sexo",),
    ("faixa_etaria",),
    ("geracao",),
    ("nivel_instrucao",),
    ("sexo", "faixa_etaria"),
    ("sexo", "geracao"),
    ("sexo", "nivel_instrucao"),
    ("faixa_etaria", "nivel_instrucao"),
    ("geracao", "nivel_instrucao"),
    ("sexo", "faixa_etaria", "nivel_instrucao"),
    ("sexo", "geracao", "nivel_instrucao"),
]


def _nome_hiato_multidimensional(dims: tuple[str, ...], sufixo: str) -> str:
    apelidos = {
        "sexo": "genero", "faixa_etaria": "faixa_etaria", "geracao": "geracao",
        "nivel_instrucao": "escolaridade",
    }
    return "hiato_" + "_".join(apelidos[d] for d in dims) + f"_{sufixo}.parquet"


def _gerar_hiato_multidimensional_para_escopo(
    con: duckdb.DuckDBPyConnection, racas_incluidas: list[str], combinar_negra: bool,
    grupo_referencia: str, grupo_nao_referencia: str, sufixo: str,
) -> None:
    """Um único pull de microdados (trimestre mais recente) pro escopo (racas_incluidas
    + se combina Preta/Parda em Negra ou não), reaproveitado pra calcular o hiato de
    TODAS as 11 combinações de dimensões de uma vez (evita 11 queries repetidas no
    DuckDB pra cada escopo)."""
    (ultimo_ano, ultimo_trimestre) = con.execute(
        "SELECT ano, trimestre FROM base ORDER BY ano DESC, trimestre DESC LIMIT 1"
    ).fetchone()
    racas_sql = "', '".join(racas_incluidas)
    micro = con.execute(f"""
        SELECT raca_cor, sexo, faixa_etaria, geracao, nivel_instrucao, renda_habitual_real, peso
        FROM base
        WHERE ano = {ultimo_ano} AND trimestre = {ultimo_trimestre}
          AND raca_cor IN ('{racas_sql}')
          AND renda_habitual_real IS NOT NULL
    """).df()
    if combinar_negra:
        micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})

    for dims in DIMENSOES_HIATO_MULTIDIMENSIONAL:
        resultados = []
        for chave, grupo_df in micro.groupby(list(dims), dropna=True):
            chave = chave if isinstance(chave, tuple) else (chave,)
            racas_presentes = set(grupo_df["raca_cor"].unique())
            if grupo_referencia not in racas_presentes or grupo_nao_referencia not in racas_presentes:
                continue
            tabela = pnadc_core.tabela_hiatos_significancia(
                grupo_df, "renda_habitual_real", "raca_cor",
                grupo_referencia=grupo_referencia, peso="peso",
            )
            if grupo_nao_referencia not in tabela.index or grupo_referencia not in tabela.index:
                continue
            linha = tabela.loc[grupo_nao_referencia]
            media_ref = tabela.loc[grupo_referencia, "media"]
            linha_resultado = dict(zip(dims, chave))
            linha_resultado.update({
                "ano": ultimo_ano, "trimestre": ultimo_trimestre,
                "n_amostra": len(grupo_df),
                f"renda_media_{grupo_nao_referencia.lower()}": linha["media"],
                f"renda_media_{grupo_referencia.lower()}": media_ref,
                "hiato_absoluto": linha["hiato_media"],
                "hiato_percentual": 100 * linha["hiato_media"] / media_ref if media_ref else None,
                "p_valor": linha["p_valor"],
                "significativo": linha["significativo"],
            })
            resultados.append(linha_resultado)

        df = pd.DataFrame(resultados)
        nome_arquivo = _nome_hiato_multidimensional(dims, sufixo)
        df.to_parquet(OUTPUT_DIR / nome_arquivo, index=False)
        n_nao_significativo = int((~df["significativo"]).sum()) if not df.empty else 0
        aviso = f" ({n_nao_significativo} célula(s) não-significativa(s))" if n_nao_significativo else ""
        print(f"{nome_arquivo}: {len(df):,} linhas".replace(",", ".") + aviso, flush=True)


def gerar_hiatos_multidimensionais(con: duckdb.DuckDBPyConnection) -> None:
    """Gera as 22 combinações de hiato (11 combinações de dimensões x 2 escopos:
    Branca-vs-Negra e Preta-vs-Parda) pedidas pra seção "Renda média" do PPT, todas com
    teste de Welch — ver `DIMENSOES_HIATO_MULTIDIMENSIONAL` e
    `_gerar_hiato_multidimensional_para_escopo`."""
    _gerar_hiato_multidimensional_para_escopo(
        con, racas_incluidas=["Branca", "Preta", "Parda"], combinar_negra=True,
        grupo_referencia="Negra", grupo_nao_referencia="Branca", sufixo="todas",
    )
    _gerar_hiato_multidimensional_para_escopo(
        con, racas_incluidas=["Preta", "Parda"], combinar_negra=False,
        grupo_referencia="Parda", grupo_nao_referencia="Preta", sufixo="pretaparda",
    )


def gerar_gini_por_raca(con: duckdb.DuckDBPyConnection) -> None:
    """Coeficiente de Gini ponderado da renda habitual real, calculado DENTRO de cada
    raça — usa `pnadc_core.gini_ponderado_por_grupo`, função já portada do notebook
    original mas nunca chamada até agora. Pergunta diferente do hiato ENTRE raças: aqui
    é sobre desigualdade DENTRO de cada grupo — a distribuição de renda entre os
    próprios negros está ficando mais ou menos desigual ao longo do tempo, e o mesmo
    pra brancos? Indígena entra com a mesma ressalva de amostra pequena de sempre."""
    trimestres = con.execute("SELECT DISTINCT ano, trimestre FROM base ORDER BY ano, trimestre").df()

    resultados = []
    for _, row in trimestres.iterrows():
        ano, trimestre = int(row["ano"]), int(row["trimestre"])
        micro = con.execute(f"""
            SELECT raca_cor, renda_habitual_real, peso
            FROM base
            WHERE ano = {ano} AND trimestre = {trimestre}
              AND raca_cor IN ('Branca', 'Preta', 'Parda', 'Indígena')
              AND renda_habitual_real IS NOT NULL AND renda_habitual_real > 0
        """).df()
        if micro.empty:
            continue
        micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})
        gini = pnadc_core.gini_ponderado_por_grupo(micro, "renda_habitual_real", by=["raca_cor"], peso="peso")
        gini["ano"] = ano
        gini["trimestre"] = trimestre
        resultados.append(gini)

    df = pd.concat(resultados, ignore_index=True)
    destino = OUTPUT_DIR / "gini_por_raca.parquet"
    df.to_parquet(destino, index=False)
    print(f"gini_por_raca.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def gerar_theil_racial(con: duckdb.DuckDBPyConnection, n_trimestres: int | None = None) -> None:
    """Decompõe a desigualdade TOTAL de renda (índice de Theil T) em quanto vem de
    diferença ENTRE raças (Branca/Negra/Indígena) vs. quanto vem de desigualdade DENTRO
    de cada raça — usa `pnadc_core.decomposicao_theil_entre_dentro` (nova, validada com
    dado sintético antes de rodar aqui). Complementa o Gini por raça acima: aquele mede
    desigualdade dentro de cada grupo isoladamente; este mede que FATIA da desigualdade
    total do Brasil o próprio recorte racial explica — e como essa fatia muda ao longo
    do tempo. `n_trimestres=None` roda todos os 58; passar um número menor pra teste
    rápido."""
    trimestres = con.execute("SELECT DISTINCT ano, trimestre FROM base ORDER BY ano, trimestre").df()
    if n_trimestres:
        trimestres = trimestres.tail(n_trimestres)

    resultados = []
    for _, row in trimestres.iterrows():
        ano, trimestre = int(row["ano"]), int(row["trimestre"])
        micro = con.execute(f"""
            SELECT raca_cor, renda_habitual_real, peso
            FROM base
            WHERE ano = {ano} AND trimestre = {trimestre}
              AND raca_cor IN ('Branca', 'Preta', 'Parda', 'Indígena')
              AND renda_habitual_real IS NOT NULL AND renda_habitual_real > 0
        """).df()
        if micro.empty:
            continue
        micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})
        resumo, _ = pnadc_core.decomposicao_theil_entre_dentro(micro, "renda_habitual_real", "raca_cor", "peso")
        resumo["ano"] = ano
        resumo["trimestre"] = trimestre
        resultados.append(resumo)

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "theil_racial.parquet"
    df.to_parquet(destino, index=False)
    print(f"theil_racial.parquet: {len(df):,} linhas".replace(",", "."), flush=True)
    print(f"  Trimestre mais recente: {df['pct_entre_grupos'].iloc[-1]:.1f}% da desigualdade "
          f"total vem de diferenças ENTRE raças, {df['pct_dentro_grupos'].iloc[-1]:.1f}% de "
          "dentro de cada raça", flush=True)


def gerar_renda_multidimensional_faixa(con: duckdb.DuckDBPyConnection, n_trimestres: int = 8) -> None:
    """Cruza renda com raça x sexo x faixa_etaria x nivel_instrucao x
    grupamento_ocupacional — estende `gerar_renda_completa` adicionando ocupação, pra
    fechar as combinações raça×faixa_etaria×ocupação e raça×faixa_etaria×escolaridade
    que ainda não tinham gráfico próprio (só apareciam embutidas no heatmap de 4
    dimensões, sem ocupação). Só ocupados com ocupação identificada (universo em que
    "ocupação" faz sentido), últimos `n_trimestres` agrupados — abrir mais uma dimensão
    de 11 categorias deixaria as células por trimestre pequenas demais (mesmo padrão de
    `gerar_decomposicao_hiato_ocupacional`/`gerar_decomposicao_oaxaca_blinder`). Brasil
    apenas — já são 5 dimensões, abrir também por geografia deixaria a maioria das
    células com amostra residual."""
    select_agregado = f"""
           raca_cor, sexo, faixa_etaria, nivel_instrucao, grupamento_ocupacional,
           COUNT(*) AS n_amostra,
           SUM(peso) AS populacao_estimada,
           SUM(renda_habitual_real * peso)
               / NULLIF(SUM(peso) FILTER (WHERE renda_habitual_real IS NOT NULL), 0)
               AS renda_habitual_real_media"""
    query = f"""
        SELECT {select_agregado}
        FROM base
        WHERE grupamento_ocupacional IS NOT NULL
          AND (ano, trimestre) IN (
              SELECT ano, trimestre FROM (SELECT DISTINCT ano, trimestre FROM base ORDER BY ano DESC, trimestre DESC LIMIT {n_trimestres})
          )
        GROUP BY raca_cor, sexo, faixa_etaria, nivel_instrucao, grupamento_ocupacional"""
    df = con.execute(query).df()
    df = df[df["nivel_instrucao"].notna()]
    destino = OUTPUT_DIR / "renda_multidimensional_faixa.parquet"
    df.to_parquet(destino, index=False)
    print(f"renda_multidimensional_faixa.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


def gerar_renda_multidimensional_geracao(con: duckdb.DuckDBPyConnection, n_trimestres: int = 8) -> None:
    """Igual a `gerar_renda_multidimensional_faixa`, mas com geração no lugar de faixa
    etária — fecha raça×geração×ocupação e raça×geração×escolaridade, além de
    raça×gênero×geração e raça×gênero×ocupação (todas derivadas colapsando as
    dimensões que sobram desta mesma tabela, ver `graficos_fase1.py`)."""
    select_agregado = f"""
           raca_cor, sexo, geracao, nivel_instrucao, grupamento_ocupacional,
           COUNT(*) AS n_amostra,
           SUM(peso) AS populacao_estimada,
           SUM(renda_habitual_real * peso)
               / NULLIF(SUM(peso) FILTER (WHERE renda_habitual_real IS NOT NULL), 0)
               AS renda_habitual_real_media"""
    query = f"""
        SELECT {select_agregado}
        FROM base
        WHERE grupamento_ocupacional IS NOT NULL
          AND (ano, trimestre) IN (
              SELECT ano, trimestre FROM (SELECT DISTINCT ano, trimestre FROM base ORDER BY ano DESC, trimestre DESC LIMIT {n_trimestres})
          )
        GROUP BY raca_cor, sexo, geracao, nivel_instrucao, grupamento_ocupacional"""
    df = con.execute(query).df()
    df = df[df["nivel_instrucao"].notna()]
    destino = OUTPUT_DIR / "renda_multidimensional_geracao.parquet"
    df.to_parquet(destino, index=False)
    print(f"renda_multidimensional_geracao.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


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


def gerar_renda_completa_geracao(con: duckdb.DuckDBPyConnection) -> None:
    """Espelha `gerar_renda_completa`, trocando faixa_etaria por geracao — cruzamento
    raça x sexo x geração x nível de instrução, universo amplo (sem restrição de
    ocupação), Brasil, série histórica completa. Preenche a lacuna que
    `renda_multidimensional_geracao.parquet` deixa (aquele é só últimos 8 trimestres e
    só ocupados, porque também cruza com ocupação — aqui não precisamos de ocupação)."""
    select_agregado = """
           ano, trimestre, raca_cor, sexo, geracao, nivel_instrucao,
           COUNT(*) AS n_amostra,
           SUM(peso) AS populacao_estimada,
           SUM(renda_habitual_real * peso)
               / NULLIF(SUM(peso) FILTER (WHERE renda_habitual_real IS NOT NULL), 0)
               AS renda_habitual_real_media"""
    query = f"""
        SELECT 'brasil' AS nivel_geografico, 'Brasil' AS geografia, {select_agregado}
        FROM base
        GROUP BY ano, trimestre, raca_cor, sexo, geracao, nivel_instrucao"""
    df = con.execute(query).df()
    df = df[df["nivel_instrucao"].notna()]
    destino = OUTPUT_DIR / "renda_completa_geracao.parquet"
    df.to_parquet(destino, index=False)
    print(f"renda_completa_geracao.parquet: {len(df):,} linhas".replace(",", "."), flush=True)


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
    gerar_renda_por_geracao(con)
    gerar_renda_completa(con)
    gerar_renda_completa_geracao(con)
    gerar_renda_multidimensional_faixa(con)
    gerar_renda_multidimensional_geracao(con)
    gerar_hiato_racial(con)
    gerar_hiato_preta_parda(con)
    gerar_hiatos_multidimensionais(con)
    gerar_hiato_por_geracao(con)
    gerar_gini_por_raca(con)
    gerar_theil_racial(con)
    gerar_quebra_estrutural()
    gerar_hiato_regional(con)
    gerar_hiato_setor_publico_privado(con)
    gerar_decomposicao_hiato_ocupacional(con)
    gerar_decomposicao_oaxaca_blinder(con)
    gerar_perfil_topo10_racial(con)
    gerar_perfil_quartis_racial(con)
    gerar_funcao_quantil_racial(con)
    gerar_indice_segregacao_ocupacional(con)
    gerar_segregacao_setorial(con)
    gerar_ocupacao(con)
    gerar_informalidade(con)
    gerar_horas_trabalhadas(con)
    gerar_alfabetizacao(con)
    gerar_desalento_subutilizacao(con)
    gerar_sobrequalificacao(con)


if __name__ == "__main__":
    main()
