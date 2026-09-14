"""Primeira tentativa de identificação CAUSAL (não mais só descritiva/correlacional),
usando as Leis de Cotas como fonte de variação exógena.

Enquadramento (ver docs/ANALISE_CAUSAL_COTAS.md pro texto completo): a PNAD Contínua não
tem nota de vestibular nem instituição de ensino — não dá pra fazer o RDD que a literatura
padrão usa (Mello 2022; Francis-Tan & Tannuri-Pianto). O desenho possível aqui é
diff-in-diff por COORTE DE EXPOSIÇÃO (nível agregado coorte/trimestre, não indivíduo
tratado/não-tratado) — mais fraco que RDD em identificação fina, mas com cobertura
nacional e histórica que RDD (restrito a universidades/anos específicos) não tem.

Dois desenhos:
- **A**: Lei de Cotas Universitárias (12.711/2012) — DiD por coorte de nascimento,
  outcome = % Superior completo medido em idade FIXA (25-29 anos, pra não confundir
  efeito da lei com "coorte mais nova ainda não teve tempo de terminar a faculdade").
- **B**: Lei de Cotas no Serviço Público Federal (12.990/2014) — event-study DiD,
  unidade = pessoa x setor_trabalho (Público/Privado) x trimestre relativo à lei,
  Privado como grupo de controle (setor não afetado pela lei).

Método de inferência: a CURVA do event-study (coeficiente por trimestre relativo) é
calculada em forma fechada (diferença de médias ponderadas + erro padrão de
`pnadc_core.erro_padrao_media_ponderada`, mesmo método usado em toda a família de
`hiato_*` do projeto) — uma regressão totalmente saturada (uma dummy por trimestre
relativo x setor) rodada em cima de dados já agregados por célula tem grau de liberdade
residual ZERO e devolve erro padrão indefinido; rodando em forma fechada sobre o
microdado (que tem milhares de pessoas por célula) isso não acontece. Já o RESUMO da
tendência pré-lei e do DiD global (um único coeficiente, não um por trimestre) É uma
regressão de verdade, rodada sobre o microdado no formato de sempre, com erro padrão
clusterizado por UPA (mesmo padrão de `pnadc_core.decomposicao_oaxaca_blinder`).

Os dois desenhos têm teste de tendências paralelas pré-lei e placebo em data falsa — se
qualquer um deles falhar, isso é reportado como "identificação não se sustenta aqui",
não escondido.

Uso:
    python -m src.processing.analise_causal_cotas
"""
from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from src.processing.agregacoes_pnadc import CRIAR_BASE, OUTPUT_DIR
from src.utils import pnadc_core

# --------------------------------------------------------------------------------------
# Desenho A — Lei de Cotas Universitárias (12.711/2012)
# --------------------------------------------------------------------------------------

ANO_LEI_UNIVERSITARIA = 2012
IDADE_ENTRADA_UNIVERSIDADE = 18
IDADE_MEDICAO = (25, 29)  # idade em que a maioria de quem vai terminar Superior já terminou
N_MINIMO_COORTE = 30
PLACEBOS_UNIVERSITARIA = [2008, 2016]  # anos de lei FALSOS, testados na mesma escala


def _limiar_nascimento(ano_lei: int) -> int:
    """Converte um ano de LEI (calendário) no limiar de ANO DE NASCIMENTO equivalente —
    quem nasceu nesse ano ou depois tinha `IDADE_ENTRADA_UNIVERSIDADE` anos ou menos
    quando a lei passou a valer, logo é a primeira coorte com acesso à cota desde a
    entrada na universidade. Ponto de bug real encontrado ao rodar pela primeira vez:
    as funções abaixo compararam `ano_nascimento` direto contra o ANO DA LEI (2012) sem
    essa conversão — como as coortes do painel (1983-2001) são todas anteriores a 2012,
    a dummy `pos` saía constante em zero pra todo mundo, gerando matriz de design
    deficiente em posto (regressão soltando aviso de rank-deficient e coeficiente saindo
    zerado) sem lançar nenhum erro. Só percebido inspecionando a saída, não pelo
    warning sozinho — lição igual à de várias outras rodadas deste projeto: sempre olhar
    o NÚMERO produzido, não só se a função "rodou sem erro"."""
    return ano_lei - IDADE_ENTRADA_UNIVERSIDADE


def construir_painel_cohortes(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Painel coorte de nascimento x raça: % com Superior completo, SEMPRE medido na
    mesma janela de idade (25-29 anos) — cada coorte contribui só com as observações em
    que tinha essa idade no momento da entrevista (trimestres diferentes, mesma idade).
    Sem isso, coortes mais jovens apareceriam com % Superior completo mecanicamente mais
    baixo só por ainda não terem tido tempo de terminar a faculdade, contaminando
    qualquer comparação antes/depois da lei com um artefato de idade, não um efeito
    real."""
    micro = con.execute(f"""
        SELECT (ano - idade) AS ano_nascimento, raca_cor, nivel_instrucao, peso
        FROM base
        WHERE idade BETWEEN {IDADE_MEDICAO[0]} AND {IDADE_MEDICAO[1]}
          AND raca_cor IN ('Branca', 'Preta', 'Parda', 'Indígena')
          AND nivel_instrucao IS NOT NULL
    """).df()
    micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})
    micro["superior"] = (micro["nivel_instrucao"] == "Superior completo").astype(float)

    linhas = []
    for (ano_nasc, raca), grupo in micro.groupby(["ano_nascimento", "raca_cor"]):
        linhas.append({
            "ano_nascimento": int(ano_nasc), "raca_cor": raca,
            "pct_superior": pnadc_core.media_ponderada(grupo["superior"], grupo["peso"]) * 100,
            "n_amostra": len(grupo),
        })
    return pd.DataFrame(linhas)


def _rodar_did_cohortes(
    painel: pd.DataFrame, raca_tratado: str, ano_lei: int, n_minimo: int = N_MINIMO_COORTE,
) -> dict:
    """DiD por coorte pra UM par (Branca vs. `raca_tratado`) e UM `ano_lei` — usado tanto
    pro corte real (2012) quanto pros placebos (2008/2016). Duas especificações: nível
    (dummy pós-limiar) e rampa (anos desde o limiar, capado em 4 — a Lei 12.711 deu até
    2016 pras universidades atingirem 100% da cota, efeito não é um degrau puro).
    Pondera pelo `n_amostra` de cada célula coorte x raça (WLS) — células maiores pesam
    mais, mesmo espírito do peso amostral do resto do projeto, só que já no nível
    agregado coorte (o dado de entrada aqui é uma tabela de médias por coorte, não
    microdado — por isso não há erro-padrão clusterizado por UPA aqui, ao contrário do
    resumo do Desenho B)."""
    limiar = _limiar_nascimento(ano_lei)
    d = painel[painel["raca_cor"].isin(["Branca", raca_tratado])].copy()
    d = d[d["n_amostra"] >= n_minimo]
    d["tratado"] = (d["raca_cor"] == raca_tratado).astype(int)
    d["ano_centrado"] = d["ano_nascimento"] - limiar
    d["pos"] = (d["ano_nascimento"] >= limiar).astype(int)
    d["anos_desde_lei"] = d["ano_centrado"].clip(lower=0, upper=4)

    modelo_nivel = smf.wls(
        "pct_superior ~ tratado * ano_centrado + tratado * pos",
        data=d, weights=d["n_amostra"],
    ).fit()
    modelo_rampa = smf.wls(
        "pct_superior ~ tratado * ano_centrado + tratado * anos_desde_lei",
        data=d, weights=d["n_amostra"],
    ).fit()

    return {
        "raca_tratado": raca_tratado, "ano_lei": ano_lei, "limiar_nascimento": limiar,
        "n_coortes_pre": int(d.loc[d["pos"] == 0, "ano_nascimento"].nunique()),
        "n_coortes_pos": int(d.loc[d["pos"] == 1, "ano_nascimento"].nunique()),
        "did_nivel_coef": modelo_nivel.params.get("tratado:pos", np.nan),
        "did_nivel_p_valor": modelo_nivel.pvalues.get("tratado:pos", np.nan),
        "did_rampa_coef": modelo_rampa.params.get("tratado:anos_desde_lei", np.nan),
        "did_rampa_p_valor": modelo_rampa.pvalues.get("tratado:anos_desde_lei", np.nan),
    }


def _testar_tendencias_paralelas(painel: pd.DataFrame, raca_tratado: str, ano_lei: int, n_minimo: int = N_MINIMO_COORTE) -> dict:
    """Restringe às coortes ANTERIORES ao limiar de nascimento e testa se a tendência
    (coorte a coorte) de `raca_tratado` já divergia da de Branca antes da lei existir —
    pré-requisito do desenho DiD. Coeficiente de interesse: `tratado:ano_centrado`
    (tendência RACA-específica pré-corte) tem que ficar perto de zero/não significativo
    pra sustentar a suposição de tendências paralelas."""
    limiar = _limiar_nascimento(ano_lei)
    d = painel[painel["raca_cor"].isin(["Branca", raca_tratado])].copy()
    d = d[d["n_amostra"] >= n_minimo]
    d = d[d["ano_nascimento"] < limiar]
    d["tratado"] = (d["raca_cor"] == raca_tratado).astype(int)
    d["ano_centrado"] = d["ano_nascimento"] - limiar
    if d["ano_centrado"].nunique() < 3:
        return {"raca_tratado": raca_tratado, "ano_lei": ano_lei, "limiar_nascimento": limiar,
                "n_coortes_pre": d["ano_centrado"].nunique(),
                "tendencia_pre_coef": np.nan, "tendencia_pre_p_valor": np.nan, "tendencias_paralelas_sustentadas": None}
    modelo = smf.wls("pct_superior ~ tratado * ano_centrado", data=d, weights=d["n_amostra"]).fit()
    coef = modelo.params.get("tratado:ano_centrado", np.nan)
    p = modelo.pvalues.get("tratado:ano_centrado", np.nan)
    return {
        "raca_tratado": raca_tratado, "ano_lei": ano_lei, "limiar_nascimento": limiar,
        "n_coortes_pre": int(d["ano_centrado"].nunique()),
        "tendencia_pre_coef": coef, "tendencia_pre_p_valor": p,
        "tendencias_paralelas_sustentadas": bool(p >= 0.05) if pd.notna(p) else None,
    }


def rodar_desenho_a(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Roda o Desenho A completo: painel de coortes, DiD (nível + rampa) no corte real
    (2012), teste de tendências paralelas pré-2012, e os dois placebos (2008, 2016) —
    pros dois pares (Branca vs. Negra, Branca vs. Indígena). Resultado em formato longo,
    uma linha por (par racial, tipo de teste)."""
    painel = construir_painel_cohortes(con)
    painel.to_parquet(OUTPUT_DIR / "painel_cohortes_superior_completo.parquet", index=False)

    resultados = []
    for raca_tratado in ["Negra", "Indígena"]:
        tendencia = _testar_tendencias_paralelas(painel, raca_tratado, ANO_LEI_UNIVERSITARIA)
        resultados.append({**tendencia, "tipo": "tendencia_pre_2012"})

        did_real = _rodar_did_cohortes(painel, raca_tratado, ANO_LEI_UNIVERSITARIA)
        resultados.append({**did_real, "tipo": "did_real_2012"})

        for ano_placebo in PLACEBOS_UNIVERSITARIA:
            did_placebo = _rodar_did_cohortes(painel, raca_tratado, ano_placebo)
            resultados.append({**did_placebo, "tipo": f"placebo_{ano_placebo}"})

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "did_cotas_universitarias.parquet"
    df.to_parquet(destino, index=False)
    print(f"did_cotas_universitarias.parquet: {len(df)} linhas", flush=True)
    print(df[["raca_tratado", "tipo", "did_nivel_coef", "did_nivel_p_valor",
              "tendencia_pre_coef", "tendencia_pre_p_valor"]].to_string(index=False), flush=True)
    return painel


def rodar_mecanismo_renda_cohortes(con: duckdb.DuckDBPyConnection) -> None:
    """Extensão de MECANISMO (não é um resultado causal novo e independente — é uma
    leitura correlacional DENTRO do desenho de coorte de exposição acima): será que o
    hiato de renda, controlando por escolaridade/idade/ocupação (mesmo método de
    `agregacoes_pnadc.gerar_decomposicao_oaxaca_blinder`), difere entre quem está nas
    coortes de PRÉ-exposição (nascidos antes do limiar de 1994, nunca teve acesso à
    cota) e quem está nas coortes de PÓS-exposição (nascidos 1994+, teve acesso)? Usa as
    MESMAS coortes do painel acima (1983-2001) pra manter as duas janelas comparáveis,
    olhando pra renda de quem está ocupado ao longo de toda a série (não restrito à
    janela de 25-29 anos aqui — a pergunta é sobre o mercado de trabalho dessas coortes
    de forma geral, não sobre conclusão de curso)."""
    limiar = _limiar_nascimento(ANO_LEI_UNIVERSITARIA)
    micro = con.execute(f"""
        SELECT raca_cor, faixa_etaria, nivel_instrucao, grupamento_ocupacional,
               renda_habitual_real, peso, upa, (ano - idade) AS ano_nascimento
        FROM base
        WHERE raca_cor IN ('Branca', 'Preta', 'Parda')
          AND grupamento_ocupacional IS NOT NULL
          AND renda_habitual_real IS NOT NULL AND renda_habitual_real > 0
          AND (ano - idade) BETWEEN 1983 AND 2001
    """).df()
    micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})
    micro["log_renda"] = np.log(micro["renda_habitual_real"])
    micro["cohort_era"] = np.where(
        micro["ano_nascimento"] < limiar, f"pré-exposição (< {limiar})", f"pós-exposição ({limiar}+)"
    )

    controles = ["faixa_etaria", "nivel_instrucao", "grupamento_ocupacional"]
    resultados = []
    for era, grupo in micro.groupby("cohort_era"):
        r = pnadc_core.decomposicao_oaxaca_blinder(
            grupo, "log_renda", controles, "peso", "raca_cor", "Branca", "Negra", cluster="upa"
        )
        r["cohort_era"] = era
        r["n_total"] = len(grupo)
        resultados.append(r)

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "mecanismo_renda_cohortes_cotas.parquet"
    df.to_parquet(destino, index=False)
    print(f"mecanismo_renda_cohortes_cotas.parquet: {len(df)} linhas", flush=True)
    print(df[["cohort_era", "n_total", "pct_explicada", "pct_nao_explicada",
              "residuo_restrito_coef", "residuo_restrito_p_valor"]].to_string(index=False), flush=True)


# --------------------------------------------------------------------------------------
# Heterogeneidade geográfica — Desenho A (Região, área urbana/rural)
# --------------------------------------------------------------------------------------

REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]


def construir_painel_cohortes_por_estrato(con: duckdb.DuckDBPyConnection, expressao_estrato: str) -> pd.DataFrame:
    """Como `construir_painel_cohortes`, mas mantendo um estrato geográfico extra
    (`expressao_estrato`, uma expressão SQL sobre `base` — ex.: `'regiao'` ou
    `"CASE WHEN regiao='Norte' THEN 'Norte' ELSE 'Resto do Brasil' END"`), pra rodar o
    DiD separado por estrato."""
    micro = con.execute(f"""
        SELECT (ano - idade) AS ano_nascimento, raca_cor, nivel_instrucao, peso,
               {expressao_estrato} AS estrato
        FROM base
        WHERE idade BETWEEN {IDADE_MEDICAO[0]} AND {IDADE_MEDICAO[1]}
          AND raca_cor IN ('Branca', 'Preta', 'Parda', 'Indígena')
          AND nivel_instrucao IS NOT NULL
    """).df()
    micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})
    micro["superior"] = (micro["nivel_instrucao"] == "Superior completo").astype(float)

    linhas = []
    for (ano_nasc, raca, estrato), grupo in micro.groupby(["ano_nascimento", "raca_cor", "estrato"]):
        linhas.append({
            "ano_nascimento": int(ano_nasc), "raca_cor": raca, "estrato": estrato,
            "pct_superior": pnadc_core.media_ponderada(grupo["superior"], grupo["peso"]) * 100,
            "n_amostra": len(grupo),
        })
    return pd.DataFrame(linhas)


def _rodar_bateria_desenho_a(painel_estrato: pd.DataFrame, raca_tratado: str, estrato_tipo: str) -> list[dict]:
    """Roda tendência pré-lei + DiD real + os 2 placebos pra CADA valor de estrato
    presente em `painel_estrato`, reaproveitando as mesmas `_testar_tendencias_paralelas`/
    `_rodar_did_cohortes` do desenho nacional (elas já operam sobre um painel
    ano_nascimento x raca_cor x pct_superior x n_amostra — um estrato de cada vez é só
    filtrar antes de chamar)."""
    resultados = []
    for estrato in sorted(painel_estrato["estrato"].dropna().unique()):
        sub = painel_estrato[painel_estrato["estrato"] == estrato].drop(columns="estrato")

        tendencia = _testar_tendencias_paralelas(sub, raca_tratado, ANO_LEI_UNIVERSITARIA)
        resultados.append({**tendencia, "estrato_tipo": estrato_tipo, "estrato": estrato, "tipo": "tendencia_pre_2012"})

        did_real = _rodar_did_cohortes(sub, raca_tratado, ANO_LEI_UNIVERSITARIA)
        resultados.append({**did_real, "estrato_tipo": estrato_tipo, "estrato": estrato, "tipo": "did_real_2012"})

        for ano_placebo in PLACEBOS_UNIVERSITARIA:
            did_placebo = _rodar_did_cohortes(sub, raca_tratado, ano_placebo)
            resultados.append({**did_placebo, "estrato_tipo": estrato_tipo, "estrato": estrato, "tipo": f"placebo_{ano_placebo}"})
    return resultados


def rodar_desenho_a_heterogeneidade(con: duckdb.DuckDBPyConnection) -> None:
    """Heterogeneidade geográfica do Desenho A — testa se o resultado nulo (ver
    `rodar_desenho_a`) é uniforme pelo país ou esconde alguma diferença regional.

    Amostra checada antes de escrever esta função: Negra fecha `n_minimo` em TODAS as
    5 regiões (célula mais fina, Sul, n=706) e nas duas áreas (Rural, a mais fina,
    n=2.047) — série completa nos dois recortes. Indígena não fecha em 4 das 5 regiões
    (células chegando a n=7) — só Norte (n mínimo 48, a região com a maior população
    indígena do país) fica de pé sozinha; testado como Norte vs. Resto do Brasil (2
    categorias, não 5), não a partição completa. Por área, Indígena Rural também não
    fecha (n mínimo 25, abaixo de 30) — só a área Urbana é publicada pra Indígena; Rural
    fica de fora, documentado como limitação, não forçado."""
    painel_regiao = construir_painel_cohortes_por_estrato(con, "regiao")
    painel_regiao.to_parquet(OUTPUT_DIR / "painel_cohortes_superior_completo_regiao.parquet", index=False)
    painel_norte_resto = construir_painel_cohortes_por_estrato(
        con, "CASE WHEN regiao='Norte' THEN 'Norte' ELSE 'Resto do Brasil' END"
    )
    painel_area = construir_painel_cohortes_por_estrato(con, "area")
    painel_area.to_parquet(OUTPUT_DIR / "painel_cohortes_superior_completo_area.parquet", index=False)

    resultados = []
    resultados += _rodar_bateria_desenho_a(painel_regiao, "Negra", "regiao")
    resultados += _rodar_bateria_desenho_a(painel_norte_resto, "Indígena", "regiao_norte_resto")
    resultados += _rodar_bateria_desenho_a(painel_area, "Negra", "area")
    resultados += _rodar_bateria_desenho_a(
        painel_area[painel_area["estrato"] == "Urbana"], "Indígena", "area"
    )

    df = pd.DataFrame(resultados)
    destino = OUTPUT_DIR / "did_cotas_universitarias_heterogeneidade.parquet"
    df.to_parquet(destino, index=False)
    print(f"did_cotas_universitarias_heterogeneidade.parquet: {len(df)} linhas", flush=True)
    print(df[["estrato_tipo", "estrato", "raca_tratado", "tipo", "did_nivel_coef", "did_nivel_p_valor",
              "tendencia_pre_coef", "tendencia_pre_p_valor"]].to_string(index=False), flush=True)


# --------------------------------------------------------------------------------------
# Desenho B — Lei de Cotas no Serviço Público Federal (12.990/2014)
# --------------------------------------------------------------------------------------

TRIMESTRE_LEI_SERVICO_PUBLICO = (2014, 3)  # lei sancionada jun/2014 (2014 T2); 1º trimestre
                                            # "pós" é T3 — 1 trimestre de defasagem administrativa
JANELA_EVENTO = (-10, 12)  # relative_quarter mín/máx mantidos na regressão/gráfico
RACAS_SERVICO_PUBLICO = ["Negra", "Indígena", "Preta", "Parda"]
N_MINIMO_CELULA_EVENTO = 30


def _indice_trimestre(trimestres_ordenados: pd.DataFrame) -> dict:
    """(ano,trimestre) -> índice sequencial 0..57, na ordem calendário — usado pra
    calcular `relative_quarter` em torno do evento sem cair no bug clássico de tratar
    `trimestre` como se fosse um número contínuo (T4 de um ano pra T1 do ano seguinte não
    é '+1' aritmético em `trimestre`, é preciso o índice sequencial de verdade)."""
    return {(int(r.ano), int(r.trimestre)): i for i, r in enumerate(trimestres_ordenados.itertuples())}


def _construir_microdados_evento_setor(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Microdado (pessoa a pessoa, não agregado) de ocupados com setor_trabalho
    classificável, recortado pra `JANELA_EVENTO` em torno da Lei 12.990/2014. Usado por
    AMBOS os outcomes do Desenho B (participação e renda) — mesma base, muda só a
    variável de saída construída a partir dela."""
    trimestres_todos = con.execute("SELECT DISTINCT ano, trimestre FROM base ORDER BY ano, trimestre").df()
    idx_map = _indice_trimestre(trimestres_todos)
    idx_evento = idx_map[TRIMESTRE_LEI_SERVICO_PUBLICO]

    micro = con.execute("""
        SELECT ano, trimestre, raca_cor, setor_trabalho, renda_habitual_real, peso, upa,
               regiao, area, UF
        FROM base
        WHERE setor_trabalho IS NOT NULL AND raca_cor IN ('Branca','Preta','Parda','Indígena')
    """).df()
    micro["indice_trimestre"] = list(zip(micro["ano"].astype(int), micro["trimestre"].astype(int)))
    micro["indice_trimestre"] = micro["indice_trimestre"].map(idx_map)
    micro["relative_quarter"] = micro["indice_trimestre"] - idx_evento
    micro = micro[(micro["relative_quarter"] >= JANELA_EVENTO[0]) & (micro["relative_quarter"] <= JANELA_EVENTO[1])]
    micro["setor_publico"] = (micro["setor_trabalho"] == "Público").astype(int)
    return micro


def _media_se(valores, pesos) -> tuple[float, float, int]:
    return (
        pnadc_core.media_ponderada(valores, pesos),
        pnadc_core.erro_padrao_media_ponderada(valores, pesos),
        int(len(valores)),
    )


def _curva_event_study(
    micro: pd.DataFrame, construir_outcome_setor,
) -> pd.DataFrame:
    """Motor comum das duas curvas de event-study (participação e hiato de renda) —
    calculado em FORMA FECHADA (diferença de médias ponderadas + soma de variâncias),
    não como coeficiente de uma regressão saturada (ver docstring do módulo pro porquê).
    `construir_outcome_setor(micro, setor_publico)` deve devolver (média, erro_padrão,
    n) pra CADA trimestre relativo dentro do subconjunto de `micro` já filtrado por
    aquele setor — chamado uma vez por (trimestre relativo, setor).

    Coeficiente em `relative_quarter=k`:
        DiD_k = (m_pub_k - m_pub_ref) - (m_priv_k - m_priv_ref)
    erro padrão combinado assumindo as 4 médias independentes (amostras disjuntas):
        se_k = sqrt(se_pub_k² + se_pub_ref² + se_priv_k² + se_priv_ref²)
    `ref` = trimestre -1 (último antes da lei)."""
    linhas = []
    for setor_publico in (0, 1):
        sub = micro[micro["setor_publico"] == setor_publico]
        for k in sorted(sub["relative_quarter"].unique()):
            m, se, n = construir_outcome_setor(sub[sub["relative_quarter"] == k])
            linhas.append({"relative_quarter": k, "setor_publico": setor_publico, "media": m, "se": se, "n": n})
    tabela = pd.DataFrame(linhas)

    ref_pub = tabela[(tabela["relative_quarter"] == -1) & (tabela["setor_publico"] == 1)].iloc[0]
    ref_priv = tabela[(tabela["relative_quarter"] == -1) & (tabela["setor_publico"] == 0)].iloc[0]

    curva = []
    for k in sorted(tabela["relative_quarter"].unique()):
        if k == -1:
            curva.append({"relative_quarter": k, "coef": 0.0, "se": 0.0, "ic_inferior": 0.0, "ic_superior": 0.0,
                          "n_publico": int(ref_pub["n"]), "n_privado": int(ref_priv["n"])})
            continue
        linha_pub = tabela[(tabela["relative_quarter"] == k) & (tabela["setor_publico"] == 1)]
        linha_priv = tabela[(tabela["relative_quarter"] == k) & (tabela["setor_publico"] == 0)]
        if linha_pub.empty or linha_priv.empty:
            continue
        linha_pub, linha_priv = linha_pub.iloc[0], linha_priv.iloc[0]
        if min(linha_pub["n"], linha_priv["n"], ref_pub["n"], ref_priv["n"]) < N_MINIMO_CELULA_EVENTO:
            continue
        coef = (linha_pub["media"] - ref_pub["media"]) - (linha_priv["media"] - ref_priv["media"])
        se = np.sqrt(linha_pub["se"]**2 + ref_pub["se"]**2 + linha_priv["se"]**2 + ref_priv["se"]**2)
        curva.append({
            "relative_quarter": k, "coef": coef, "se": se,
            "ic_inferior": coef - 1.96 * se, "ic_superior": coef + 1.96 * se,
            "n_publico": int(linha_pub["n"]), "n_privado": int(linha_priv["n"]),
        })
    return pd.DataFrame(curva).sort_values("relative_quarter").reset_index(drop=True)


def _resumo_regressao_evento(micro: pd.DataFrame, outcome_col: str) -> dict:
    """Resumo com inferência de verdade (não a curva ponto a ponto): (1) tendência
    pré-lei (só trimestres < 0, `outcome ~ relative_quarter * setor_publico` — coloca a
    tendência RACA/OUTCOME-específica dentro do público contra o privado antes da lei
    existir); (2) DiD global (`outcome ~ pos_evento * setor_publico`, pos_evento binário
    >= 0). As duas rodadas sobre o MICRODADO (milhares de pessoas por célula, nunca sobre
    médias já agregadas) com erro padrão clusterizado por UPA — mesmo padrão de
    `pnadc_core.decomposicao_oaxaca_blinder`."""
    pre = micro[micro["relative_quarter"] < 0]
    if pre["relative_quarter"].nunique() >= 3:
        m_pre = smf.wls(
            f"{outcome_col} ~ relative_quarter * setor_publico", data=pre, weights=pre["peso"],
        ).fit(cov_type="cluster", cov_kwds={"groups": pre["upa"]})
        coef_pre = m_pre.params.get("relative_quarter:setor_publico", np.nan)
        p_pre = m_pre.pvalues.get("relative_quarter:setor_publico", np.nan)
    else:
        coef_pre, p_pre = np.nan, np.nan

    d = micro.copy()
    d["pos_evento"] = (d["relative_quarter"] >= 0).astype(int)
    m_did = smf.wls(
        f"{outcome_col} ~ pos_evento * setor_publico", data=d, weights=d["peso"],
    ).fit(cov_type="cluster", cov_kwds={"groups": d["upa"]})
    coef_did = m_did.params.get("pos_evento:setor_publico", np.nan)
    p_did = m_did.pvalues.get("pos_evento:setor_publico", np.nan)

    return {
        "tendencia_pre_coef": coef_pre, "tendencia_pre_p_valor": p_pre,
        "tendencias_paralelas_sustentadas": bool(p_pre >= 0.05) if pd.notna(p_pre) else None,
        "did_coef": coef_did, "did_p_valor": p_did,
        "n_trimestres_pre": int(pre["relative_quarter"].nunique()),
        "n_trimestres_pos": int(d.loc[d["pos_evento"] == 1, "relative_quarter"].nunique()),
    }


def rodar_desenho_b_participacao(
    micro_evento: pd.DataFrame, racas: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Event-study DiD na PARTICIPAÇÃO de cada raça entre ocupados do setor público,
    usando o setor PRIVADO como grupo de controle (não afetado pela Lei 12.990/2014) —
    testa se a participação de Negra/Preta/Parda/Indígena no setor público muda de
    trajetória especificamente ali, além de qualquer tendência que já estivesse
    acontecendo nos dois setores. Outcome, no nível pessoa: `1[raca_cor == raça-alvo]`,
    então "participação" é a média ponderada dessa dummy dentro de cada
    (trimestre relativo, setor) — uma proporção, calculada em forma fechada.

    `racas` (default `RACAS_SERVICO_PUBLICO`, as 4) permite restringir a lista — usado
    pela heterogeneidade geográfica, que só roda Indígena nos estratos que fecham
    amostra (ver `rodar_desenho_b_heterogeneidade`)."""
    curvas, resumos = [], []
    for raca in (racas or RACAS_SERVICO_PUBLICO):
        micro = micro_evento.copy()
        # x100: outcome em PONTOS PERCENTUAIS (não fração 0-1) — mesma escala usada nos
        # gráficos/subtítulos ("pontos percentuais"), pra `did_coef`/`tendencia_pre_coef`
        # já saírem interpretáveis direto, sem precisar converter na hora de escrever o texto.
        indicador = (micro["raca_cor"] == raca) if raca != "Negra" else micro["raca_cor"].isin(["Preta", "Parda"])
        micro["outcome"] = indicador.astype(float) * 100

        def _outcome_setor(sub):
            return _media_se(sub["outcome"], sub["peso"])

        curva = _curva_event_study(micro, _outcome_setor)
        curva["raca_cor"] = raca
        curva["outcome"] = "participacao"
        curvas.append(curva)

        resumo = _resumo_regressao_evento(micro, "outcome")
        resumo.update({"raca_cor": raca, "outcome": "participacao"})
        resumos.append(resumo)

    curvas_df = pd.concat(curvas, ignore_index=True)
    resumos_df = pd.DataFrame(resumos)
    print(f"event_study_participacao_servico_publico: {len(curvas_df)} linhas de curva", flush=True)
    print(resumos_df.to_string(index=False), flush=True)
    return curvas_df, resumos_df


def rodar_desenho_b_renda(micro_evento: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Event-study DiD no HIATO de renda Branca-Negra DENTRO de cada setor — a pergunta
    é "o hiato racial no setor público mudou de TRAJETÓRIA depois da lei, além do que já
    vinha acontecendo no privado?", não mais só a foto atual que
    `hiato_setor_publico_privado.parquet` já dava. Reconstruído do microdado (não lido
    daquele parquet) porque a curva do event-study precisa de erro padrão célula a
    célula, que o parquet agregado não guarda."""
    micro = micro_evento[
        micro_evento["raca_cor"].isin(["Branca", "Preta", "Parda"])
        & micro_evento["renda_habitual_real"].notna() & (micro_evento["renda_habitual_real"] > 0)
    ].copy()
    micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})

    def _hiato_setor(sub):
        b = sub[sub["raca_cor"] == "Branca"]
        n = sub[sub["raca_cor"] == "Negra"]
        mb, seb, _ = _media_se(b["renda_habitual_real"], b["peso"])
        mn, sen, nn = _media_se(n["renda_habitual_real"], n["peso"])
        if not mn:
            return np.nan, np.nan, 0
        hiato_pct = 100 * (mb - mn) / mn
        # método delta pro erro padrão de h = 100*(mb-mn)/mn = 100*(mb/mn - 1),
        # assumindo mb e mn independentes (amostras disjuntas, Branca x Negra):
        # dh/dmb = 100/mn, dh/dmn = -100*mb/mn^2
        se_pct = 100 * np.sqrt((seb / mn) ** 2 + (mb * sen / mn**2) ** 2)
        return hiato_pct, se_pct, min(len(b), nn)

    curva = _curva_event_study(micro, _hiato_setor)
    curva["raca_cor"] = "Negra"
    curva["outcome"] = "hiato_renda_pct"

    resumo = _resumo_regressao_hiato_evento(micro)
    resumo.update({"raca_cor": "Negra", "outcome": "hiato_renda_pct"})
    print("event-study hiato de renda (setor público vs. privado), curva:", flush=True)
    print(curva.to_string(index=False), flush=True)
    return curva, pd.DataFrame([resumo])


def _resumo_regressao_hiato_evento(micro: pd.DataFrame) -> dict:
    """Resumo com inferência de verdade pro HIATO de renda especificamente (diferente
    de `_resumo_regressao_evento`, que só tem duas vias — aqui precisa de uma TERCEIRA
    via, `negra`, porque a pergunta não é "renda mudou no público" e sim "o HIATO racial
    dentro do público mudou" — o coeficiente de interesse é a interação TRIPLA
    `pos_evento:setor_publico:negra` em log(renda). Cluster por UPA, mesmo padrão do
    resto do projeto."""
    d = micro.copy()
    d["log_renda"] = np.log(d["renda_habitual_real"])
    d["negra"] = (d["raca_cor"] == "Negra").astype(int)
    d["pos_evento"] = (d["relative_quarter"] >= 0).astype(int)

    pre = d[d["relative_quarter"] < 0]
    m_pre = smf.wls(
        "log_renda ~ relative_quarter * setor_publico * negra", data=pre, weights=pre["peso"],
    ).fit(cov_type="cluster", cov_kwds={"groups": pre["upa"]})
    nome_pre = "relative_quarter:setor_publico:negra"
    coef_pre = m_pre.params.get(nome_pre, np.nan)
    p_pre = m_pre.pvalues.get(nome_pre, np.nan)

    m_did = smf.wls(
        "log_renda ~ pos_evento * setor_publico * negra", data=d, weights=d["peso"],
    ).fit(cov_type="cluster", cov_kwds={"groups": d["upa"]})
    nome_did = "pos_evento:setor_publico:negra"
    coef_did = m_did.params.get(nome_did, np.nan)
    p_did = m_did.pvalues.get(nome_did, np.nan)

    return {
        "tendencia_pre_coef": coef_pre, "tendencia_pre_p_valor": p_pre,
        "tendencias_paralelas_sustentadas": bool(p_pre >= 0.05) if pd.notna(p_pre) else None,
        "did_coef": coef_did, "did_p_valor": p_did,
        "n_trimestres_pre": int(pre["relative_quarter"].nunique()),
        "n_trimestres_pos": int(d.loc[d["pos_evento"] == 1, "relative_quarter"].nunique()),
        "nota": "coeficiente é a interação tripla tempo x setor x raça em log(renda) — log-pontos, não % direto",
    }


def _rodar_par_desenho_b(micro_estrato: pd.DataFrame, racas: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Roda participação (pras `racas` pedidas) + hiato de renda Branca-Negra (só se
    'Negra' estiver em `racas` — hiato é sempre Branca vs. Negra, não generaliza pras
    outras raças) num subconjunto JÁ FILTRADO por estrato geográfico de
    `micro_evento`. Motor comum de `rodar_desenho_b_heterogeneidade`."""
    curvas_p, resumo_p = rodar_desenho_b_participacao(micro_estrato, racas=racas)
    partes_curva, partes_resumo = [curvas_p], [resumo_p]
    if "Negra" in racas:
        curva_r, resumo_r = rodar_desenho_b_renda(micro_estrato)
        partes_curva.append(curva_r)
        partes_resumo.append(resumo_r)
    return pd.concat(partes_curva, ignore_index=True), pd.concat(partes_resumo, ignore_index=True)


def rodar_desenho_b_heterogeneidade(micro_evento: pd.DataFrame) -> None:
    """Heterogeneidade geográfica do Desenho B — Região, área urbana/rural, e Distrito
    Federal vs. resto do Brasil (aproximação parcial da limitação de esfera de governo:
    ver docs/LIMITACOES_E_METODOLOGIA.md — o funcionalismo federal é desproporcionalmente
    concentrado no DF, então um efeito mais forte ali é evidência indireta, não uma
    medida direta, de que o efeito federal isolado é maior que o estimado hoje).

    Amostra checada antes de escrever esta função: Negra (e Preta/Parda) fecham
    `n_minimo` em TODAS as 5 regiões, nas duas áreas e no DF isoladamente (célula mais
    fina, DF x Negra x Público, n mínimo 277 por trimestre). Indígena só fecha em
    Norte (n mínimo 32 por trimestre; as outras 4 regiões chegam a n=1) e em área
    Urbana (n mínimo 48; Rural chega a n=8) — testado como Norte vs. Resto do Brasil
    (não as 5 regiões) e só Urbana (Rural fica de fora). Indígena no DF não roda de
    jeito nenhum (n mínimo 1 por trimestre) — nem tentado."""
    resultados_curva, resultados_resumo = [], []

    def _registrar(curva, resumo, estrato_tipo, estrato):
        curva = curva.assign(estrato_tipo=estrato_tipo, estrato=estrato)
        resumo = resumo.assign(estrato_tipo=estrato_tipo, estrato=estrato)
        resultados_curva.append(curva)
        resultados_resumo.append(resumo)

    for regiao in REGIOES:
        sub = micro_evento[micro_evento["regiao"] == regiao]
        curva, resumo = _rodar_par_desenho_b(sub, ["Negra", "Preta", "Parda"])
        _registrar(curva, resumo, "regiao", regiao)

    estrato_norte = np.where(micro_evento["regiao"] == "Norte", "Norte", "Resto do Brasil")
    for valor in ["Norte", "Resto do Brasil"]:
        sub = micro_evento[estrato_norte == valor]
        curva, resumo = _rodar_par_desenho_b(sub, ["Indígena"])
        _registrar(curva, resumo, "regiao_norte_resto", valor)

    for area in ["Urbana", "Rural"]:
        sub = micro_evento[micro_evento["area"] == area]
        curva, resumo = _rodar_par_desenho_b(sub, ["Negra", "Preta", "Parda"])
        _registrar(curva, resumo, "area", area)

    curva, resumo = _rodar_par_desenho_b(micro_evento[micro_evento["area"] == "Urbana"], ["Indígena"])
    _registrar(curva, resumo, "area", "Urbana (Indígena)")

    estrato_df = np.where(micro_evento["UF"] == "53", "Distrito Federal", "Resto do Brasil")
    for valor in ["Distrito Federal", "Resto do Brasil"]:
        sub = micro_evento[estrato_df == valor]
        curva, resumo = _rodar_par_desenho_b(sub, ["Negra"])
        _registrar(curva, resumo, "df_vs_resto", valor)

    curvas = pd.concat(resultados_curva, ignore_index=True)
    resumo = pd.concat(resultados_resumo, ignore_index=True)
    curvas.to_parquet(OUTPUT_DIR / "did_cotas_servico_publico_heterogeneidade_curvas.parquet", index=False)
    resumo.to_parquet(OUTPUT_DIR / "did_cotas_servico_publico_heterogeneidade.parquet", index=False)
    print(f"did_cotas_servico_publico_heterogeneidade.parquet: {len(resumo)} linhas", flush=True)
    print(resumo[["estrato_tipo", "estrato", "raca_cor", "outcome", "tendencia_pre_p_valor",
                  "tendencias_paralelas_sustentadas", "did_coef", "did_p_valor"]].to_string(index=False), flush=True)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    con.execute(CRIAR_BASE)

    print("=== Desenho A: Lei de Cotas Universitárias (12.711/2012) ===", flush=True)
    rodar_desenho_a(con)
    rodar_mecanismo_renda_cohortes(con)
    print("\n--- Heterogeneidade geográfica, Desenho A ---", flush=True)
    rodar_desenho_a_heterogeneidade(con)

    print("\n=== Desenho B: Lei de Cotas no Serviço Público Federal (12.990/2014) ===", flush=True)
    micro_evento = _construir_microdados_evento_setor(con)
    curvas_participacao, resumo_participacao = rodar_desenho_b_participacao(micro_evento)
    curva_renda, resumo_renda = rodar_desenho_b_renda(micro_evento)

    curvas = pd.concat([curvas_participacao, curva_renda], ignore_index=True)
    resumo = pd.concat([resumo_participacao, resumo_renda], ignore_index=True)
    curvas.to_parquet(OUTPUT_DIR / "did_cotas_servico_publico_curvas.parquet", index=False)
    resumo.to_parquet(OUTPUT_DIR / "did_cotas_servico_publico.parquet", index=False)
    print(f"\ndid_cotas_servico_publico.parquet: {len(resumo)} linhas", flush=True)

    print("\n--- Heterogeneidade geográfica, Desenho B ---", flush=True)
    rodar_desenho_b_heterogeneidade(micro_evento)


if __name__ == "__main__":
    main()
