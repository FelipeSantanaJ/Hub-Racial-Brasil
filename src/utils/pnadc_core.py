"""Funcoes compartilhadas do projeto PNAD Continua.

Cobre recorte racial/genero, geografia, estatistica ponderada (media, erro
padrao, IC, coeficiente de variacao), significancia (teste t Welch), deflator
de renda e coeficiente de Gini ponderado. Portado do notebook Colab
pnadc_core.ipynb (projeto original no Drive).
"""



import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from scipy.stats import gaussian_kde

COLUNA_PESO = 'V1028'
# V2010/V2007/UF/Capital/RM_RIDE são lidos do layout fixo do IBGE como TEXTO (largura
# fixa "$N.", não numérico) — as chaves destes dicionários são strings de propósito,
# batendo com o dtype real das colunas no parquet extraído por src/ingestion/extrator_pnadc.py.
CODIGOS_RACA = {'1': 'Branca', '2': 'Preta', '3': 'Amarela', '4': 'Parda', '5': 'Indígena', '9': 'Ignorado'}
CODIGOS_SEXO = {'1': 'Homem', '2': 'Mulher'}
ORDEM_RECORTE1 = ['Branca', 'Preta', 'Parda', 'Negra', 'Indígena']
ORDEM_RECORTE3 = ['Preta', 'Parda', 'Negra']
ORDEM_RECORTE2_HOMENS = ['Homens Brancos', 'Homens Pretos', 'Homens Pardos', 'Homens Negros', 'Homens Indígenas']
ORDEM_RECORTE2_MULHERES = ['Mulheres Brancas', 'Mulheres Pretas', 'Mulheres Pardas', 'Mulheres Negras', 'Mulheres Indígenas']
ROTULO_GRUPO_RECORTE2 = {('Homem', 'Branca'): 'Homens Brancos', ('Homem', 'Preta'): 'Homens Pretos', ('Homem', 'Parda'): 'Homens Pardos', ('Homem', 'Negra'): 'Homens Negros', ('Homem', 'Indígena'): 'Homens Indígenas', ('Mulher', 'Branca'): 'Mulheres Brancas', ('Mulher', 'Preta'): 'Mulheres Pretas', ('Mulher', 'Parda'): 'Mulheres Pardas', ('Mulher', 'Negra'): 'Mulheres Negras', ('Mulher', 'Indígena'): 'Mulheres Indígenas'}
REGIAO_POR_UF = {'11': 'Norte', '12': 'Norte', '13': 'Norte', '14': 'Norte', '15': 'Norte', '16': 'Norte', '17': 'Norte', '21': 'Nordeste', '22': 'Nordeste', '23': 'Nordeste', '24': 'Nordeste', '25': 'Nordeste', '26': 'Nordeste', '27': 'Nordeste', '28': 'Nordeste', '29': 'Nordeste', '31': 'Sudeste', '32': 'Sudeste', '33': 'Sudeste', '35': 'Sudeste', '41': 'Sul', '42': 'Sul', '43': 'Sul', '50': 'Centro-Oeste', '51': 'Centro-Oeste', '52': 'Centro-Oeste', '53': 'Centro-Oeste'}
NIVEIS_GEOGRAFICOS = ['brasil', 'regiao', 'uf', 'capital_interior']
URL_DEFLATOR_TRIMESTRAL = None
CORES_RACA = {'Branca': '#4E79A7', 'Preta': '#E15759', 'Parda': '#F28E2B', 'Negra': '#B07AA1', 'Indígena': '#59A14F', 'Amarela': '#EDC948'}
CORES_GENERO = {'Homem': '#4E79A7', 'Mulher': '#B07AA1'}


def media_ponderada(valores, pesos):
    """Média ponderada, ignorando pares (valor, peso) com NaN em qualquer um dos dois."""
    valores = np.asarray(valores, dtype=float)
    pesos = np.asarray(pesos, dtype=float)
    # remove NaNs onde valores ou pesos não são válidos
    valid = ~np.isnan(valores) & ~np.isnan(pesos) & (pesos > 0)
    if not valid.any():
        return np.nan  # ou 0, dependendo da semântica desejada para grupo vazio
    return np.average(valores[valid], weights=pesos[valid])


def erro_padrao_media_ponderada(valores, pesos):
    """Erro padrão de média ponderada, ignorando NaNs e pesos zero ou negativos."""
    valores = np.asarray(valores, dtype=float)
    pesos = np.asarray(pesos, dtype=float)
    valid = ~np.isnan(valores) & ~np.isnan(pesos) & (pesos > 0)
    if not valid.any() or len(valores[valid]) == 1: # precisa de pelo menos 2 pontos para calcular EP
        return np.nan
    valores = valores[valid]
    pesos = pesos[valid]

    # Cochran (1977), Sampling Techniques, p. 30
    # Variância (da MÉDIA) = (n / (n-1)) * (sum(w_i * (x_i - mean)^2) / (sum(w_i)^2))
    # O termo (n / (n-1)) é para amostras finitas.
    # BUG histórico corrigido em 2026-09-04: a versão anterior usava um denominador
    # diferente do documentado aqui (sum(w)^2 - sum(w^2)) e ainda multiplicava o
    # resultado por len(valores) no final — isso inflava o erro padrão em ~sqrt(n)x
    # (para n ~ centenas de milhares, um fator de centenas de vezes), gerando
    # intervalos de confiança absurdamente largos mesmo com amostras enormes. Ver
    # docs/PLANO.md para como isso foi encontrado (banda de IC do gráfico de hiato
    # racial cobrindo de 40% a mais de 100%, incompatível com p-valores já
    # extremamente pequenos calculados com a mesma fórmula).
    n = len(valores)
    media = np.average(valores, weights=pesos)
    variancia_media = (n / (n - 1)) * np.sum(pesos * (valores - media)**2) / (np.sum(pesos)**2)
    erro_padrao = np.sqrt(variancia_media)
    return erro_padrao


def coeficiente_variacao_ponderado(valores, pesos):
    """Coeficiente de variação ponderado."""
    valores = np.asarray(valores, dtype=float)
    pesos = np.asarray(pesos, dtype=float)
    valid = ~np.isnan(valores) & ~np.isnan(pesos) & (pesos > 0)
    if not valid.any() or len(valores[valid]) == 1:
        return np.nan
    valores = valores[valid]
    pesos = pesos[valid]

    media = np.average(valores, weights=pesos)
    # Variância = sum(w_i * (x_i - mean)^2) / sum(w_i)
    # Desvio padrão = sqrt(Variância)
    desvio_padrao = np.sqrt(np.sum(pesos * (valores - media)**2) / np.sum(pesos))

    if media == 0:
        return np.nan # ou um valor que indique divisão por zero, dependendo do contexto
    return desvio_padrao / media


def intervalo_confianca_media_ponderada(df, coluna_valor, peso=COLUNA_PESO, nivel_confianca=0.95):
    """Calcula o intervalo de confiança para a média ponderada.
    Retorna uma tupla (inferior, superior).
    """
    media = media_ponderada(df[coluna_valor], df[peso])
    ep = erro_padrao_media_ponderada(df[coluna_valor], df[peso])

    if np.isnan(media) or np.isnan(ep):
        return np.nan, np.nan

    # Usar t-distribuição para pequenas amostras, Z para grandes
    # Para n > 30, t-distribuição se aproxima da normal
    n = len(df.dropna(subset=[coluna_valor, peso]))
    if n < 30:
        # Para graus de liberdade, n-1. Se n=1, df=0, t_critical não é definido.
        # Já tratamos n=1 no erro_padrao.
        t_critical = stats.t.ppf((1 + nivel_confianca) / 2, df=n-1)
    else:
        t_critical = stats.norm.ppf((1 + nivel_confianca) / 2)

    margem_erro = t_critical * ep
    return media - margem_erro, media + margem_erro


def aplicar_recorte1(df):
    """Aplica o recorte racial 1: Branca, Preta, Parda, Negra, Indígena.
    'Negra' é a soma de Preta e Parda para análise.
    V2010: 1=Branca, 2=Preta, 3=Amarela, 4=Parda, 5=Indígena, 9=Ignorado
    """
    df['raca_cor'] = df['V2010'].map(CODIGOS_RACA)
    df.loc[df['raca_cor'].isin(['Preta', 'Parda']), 'raca_cor'] = 'Negra'
    df['raca_cor'] = pd.Categorical(df['raca_cor'], categories=ORDEM_RECORTE1, ordered=True)
    return df


def aplicar_recorte2(df):
    """Aplica o recorte de gênero-raça, com Homens Brancos, Mulheres Negras etc.
    V2007: 1=Homem, 2=Mulher
    V2010: 1=Branca, 2=Preta, 3=Amarela, 4=Parda, 5=Indígena, 9=Ignorado
    """
    df['sexo'] = df['V2007'].map(CODIGOS_SEXO)
    df['raca_cor'] = df['V2010'].map(CODIGOS_RACA)
    # Categoriza 'Negra' para fins de agregação antes de criar o grupo final
    df.loc[df['raca_cor'].isin(['Preta', 'Parda']), 'raca_cor_agregada'] = 'Negra'
    df.loc[df['raca_cor'] == 'Branca', 'raca_cor_agregada'] = 'Branca'
    df.loc[df['raca_cor'] == 'Indígena', 'raca_cor_agregada'] = 'Indígena'

    # Cria a coluna de grupo de recorte
    df['grupo'] = df.apply(lambda row: ROTULO_GRUPO_RECORTE2.get((row['sexo'], row['raca_cor_agregada'])), axis=1)

    # Define a ordem para a categoria 'grupo'
    ordem_completa = ORDEM_RECORTE2_HOMENS + ORDEM_RECORTE2_MULHERES
    df['grupo'] = pd.Categorical(df['grupo'], categories=ordem_completa, ordered=True)

    return df.drop(columns=['raca_cor_agregada'])


def aplicar_recorte3(df):
    """Aplica o recorte racial 3: Preta, Parda, Negra. 'Negra' é a soma de Preta e Parda.
    V2010: 1=Branca, 2=Preta, 3=Amarela, 4=Parda, 5=Indígena, 9=Ignorado
    """
    df['raca_cor'] = df['V2010'].map(CODIGOS_RACA)
    df.loc[df['raca_cor'].isin(['Preta', 'Parda']), 'raca_cor'] = 'Negra'
    df = df[df['raca_cor'].isin(ORDEM_RECORTE3)].copy() # Filtra apenas as raças desejadas
    df['raca_cor'] = pd.Categorical(df['raca_cor'], categories=ORDEM_RECORTE3, ordered=True)
    return df


def preparar_niveis_geograficos(df):
    """Adiciona colunas para Região e Capital/Interior com base em UF e Capital.

    `Capital` NÃO é um flag binário: traz o código da UF quando o registro é do
    município da capital daquela UF, e fica em branco (NaN/None) caso contrário.
    Mesma lógica vale para `RM_RIDE` (Região Metropolitana/RIDE).
    """
    df['regiao'] = df['UF'].map(REGIAO_POR_UF)
    df['localizacao'] = np.where(df['Capital'].notna(), 'Capital', 'Interior')
    return df


def carregar_deflator(url=URL_DEFLATOR_TRIMESTRAL):
    """Carrega o deflator de preços trimestral (IPCA-CO2/CO2e) do IPEA. Ajusta os dados
    para ter um trimestre de referência único (último trimestre completo disponível)
    e prepara para merge.
    """
    if url is None:
        raise ValueError(
            "URL_DEFLATOR_TRIMESTRAL não preenchido. Defina-o no notebook base (pnadc_core.ipynb) "
            "e regere o pnadc_core.py, ou passe um caminho local válido para o df_deflator."
        )
    df_deflator = pd.read_csv(url, sep=';', skiprows=1, decimal=',')
    df_deflator = df_deflator.iloc[:-1] # ultima linha é nota de rodape
    df_deflator['Data'] = pd.to_datetime(df_deflator['Data'], format='%d/%m/%Y')
    df_deflator['ano'] = df_deflator['Data'].dt.year
    df_deflator['trimestre'] = df_deflator['Data'].dt.quarter

    # Ajustar para o último trimestre completo para que o deflator seja 1
    ultimo_ano = df_deflator['ano'].max()
    ultimo_trimestre = df_deflator[df_deflator['ano'] == ultimo_ano]['trimestre'].max()
    deflator_referencia = df_deflator[(df_deflator['ano'] == ultimo_ano) &
                                      (df_deflator['trimestre'] == ultimo_trimestre)]['CO2'].iloc[0]

    df_deflator['deflator_ajustado'] = df_deflator['CO2'] / deflator_referencia
    return df_deflator[['ano', 'trimestre', 'deflator_ajustado']]


def aplicar_deflator(df, df_deflator):
    """Aplica o deflator ao DataFrame de renda, criando colunas '_real'."""
    df = pd.merge(df, df_deflator, on=['ano', 'trimestre'], how='left')
    df['VD4019_real'] = df['VD4019'] / df['deflator_ajustado']
    df['VD4020_real'] = df['VD4020'] / df['deflator_ajustado']
    return df


def tabela_hiatos_significancia(df, coluna_valor, col_grupo, grupo_referencia, peso=COLUNA_PESO, nivel_confianca=0.95):
    """Calcula hiatos de média, seus intervalos de confiança e p-valor (teste t).
    Retorna um DataFrame com os resultados.
    """
    grupos = sorted(df[col_grupo].unique())

    if grupo_referencia not in grupos:
        raise ValueError(f"Grupo de referência '{grupo_referencia}' não encontrado na coluna '{col_grupo}'.")

    df_ref = df[df[col_grupo] == grupo_referencia].copy()
    media_ref = media_ponderada(df_ref[coluna_valor], df_ref[peso])
    ep_ref = erro_padrao_media_ponderada(df_ref[coluna_valor], df_ref[peso])

    resultados = []
    for grupo in grupos:
        if grupo == grupo_referencia:
            hiato_media = 0.0
            p_valor = 1.0
            ic_inferior = 0.0
            ic_superior = 0.0
            significativo = False
        else:
            df_grupo = df[df[col_grupo] == grupo].copy()
            media_grupo = media_ponderada(df_grupo[coluna_valor], df_grupo[peso])
            ep_grupo = erro_padrao_media_ponderada(df_grupo[coluna_valor], df_grupo[peso])

            hiato_media = media_grupo - media_ref

            # Erro padrão da diferença de médias (assumindo amostras independentes)
            ep_diferenca = np.sqrt(ep_grupo**2 + ep_ref**2)

            # Teste t para diferença de médias
            if ep_diferenca > 0:
                t_stat = hiato_media / ep_diferenca
                # Graus de liberdade aproximados (Welch-Satterthwaite)
                n1 = len(df_grupo.dropna(subset=[coluna_valor, peso]))
                n2 = len(df_ref.dropna(subset=[coluna_valor, peso]))
                if n1 > 1 and n2 > 1:
                    df_welch = (ep_grupo**2/n1 + ep_ref**2/n2)**2 / \
                               ((ep_grupo**2/n1)**2 / (n1-1) + (ep_ref**2/n2)**2 / (n2-1))
                    p_valor = 2 * (1 - stats.t.cdf(abs(t_stat), df=df_welch))
                else:
                    p_valor = np.nan # Não há dados suficientes para teste t
            else:
                t_stat = np.nan
                p_valor = np.nan

            # Intervalo de confiança da diferença
            if not np.isnan(ep_diferenca) and ep_diferenca > 0:
                if n1 > 1 and n2 > 1:
                    # Usar t-distribuição para o IC
                    t_critical = stats.t.ppf((1 + nivel_confianca) / 2, df=df_welch)
                else:
                    t_critical = stats.norm.ppf((1 + nivel_confianca) / 2) # Fallback para Z se df_welch não for calculado
                margem_erro = t_critical * ep_diferenca
                ic_inferior = hiato_media - margem_erro
                ic_superior = hiato_media + margem_erro
            else:
                ic_inferior = np.nan
                ic_superior = np.nan

            significativo = p_valor < (1 - nivel_confianca) if not np.isnan(p_valor) else False

        resultados.append({
            col_grupo: grupo,
            'media': media_ponderada(df[df[col_grupo] == grupo][coluna_valor], df[df[col_grupo] == grupo][peso]),
            'hiato_media': hiato_media,
            'p_valor': p_valor,
            'ic_inferior': ic_inferior,
            'ic_superior': ic_superior,
            'significativo': significativo
        })

    return pd.DataFrame(resultados).set_index(col_grupo)


def rif_quantil(valores, pesos, quantil):
    """Recentered Influence Function (Firpo-Fortin-Lemieux, 2009) do quantil `quantil`
    (ex.: 0.1, 0.5, 0.9) de `valores`, ponderada por `pesos`.

    RIF(y; q) = q + (quantil - 1{y <= q}) / f_Y(q), onde f_Y(q) é a densidade estimada
    (kernel gaussiano ponderado) no ponto do quantil q. Regredir a RIF em covariáveis
    (WLS) e decompor via Oaxaca-Blinder (ver `decomposicao_oaxaca_blinder`) dá a
    decomposição do hiato NAQUELE PONTO da distribuição, não só na média — permite
    perguntar "o hiato racial é maior no topo ou na base da distribuição de renda?".

    Pré-condição: `valores`/`pesos` sem NaN (filtrar antes de chamar). Retorna
    (array de RIF na mesma ordem de `valores`, valor do quantil, densidade estimada).
    """
    valores = np.asarray(valores, dtype=float)
    pesos = np.asarray(pesos, dtype=float)
    ordem = np.argsort(valores)
    cum = np.cumsum(pesos[ordem]) / pesos.sum()
    pos = np.searchsorted(cum, quantil)
    q = valores[ordem][min(pos, len(valores) - 1)]
    densidade = float(gaussian_kde(valores, weights=pesos)(q)[0])
    rif = q + (quantil - (valores <= q).astype(float)) / densidade
    return rif, q, densidade


def decomposicao_oaxaca_blinder(micro, outcome, controles, peso, col_grupo, grupo_favorecido, grupo_desfavorecido):
    """Decomposição de Oaxaca-Blinder (twofold) do hiato médio de `outcome` entre
    `grupo_favorecido` e `grupo_desfavorecido`, controlando por `controles` (lista de
    colunas categóricas). `outcome` já deve estar na escala desejada — passar
    log(renda) pra hiato multiplicativo/log-pontos, ou a RIF de um quantil (ver
    `rif_quantil`) pra decompor naquele ponto da distribuição em vez da média.

    Coeficientes de referência = média dos dois grupos (convenção Reimers, 1983) — evita
    a arbitrariedade de usar só um dos dois grupos como "estrutura não-discriminatória"
    (a alternativa clássica de Blinder/Oaxaca original).

    - `parcela_explicada`: quanto do hiato vem de os dois grupos terem características
      (idade/escolaridade/ocupação) diferentes.
    - `parcela_nao_explicada`: quanto sobra mesmo com as MESMAS características — os
      grupos têm retornos (coeficientes) diferentes pra elas. Proxy de discriminação,
      não prova direta (outras variáveis não observadas aqui também caem aqui dentro).

    Teste de significância: ajusta também um modelo único (mesmos coeficientes pros
    controles nos dois grupos, só o intercepto de grupo muda) — o coeficiente de
    `col_grupo` nesse modelo restrito já sai com erro-padrão e p-valor prontos, sem
    precisar de bootstrap. É uma versão mais simples (assume retornos iguais aos
    controles) do resíduo "não-explicado" acima — reportar os dois é intencional: um dá
    o tamanho da decomposição completa, o outro dá o teste formal de significância.

    Limitação: os pesos amostrais (V1028) entram como pesos analíticos do WLS
    (statsmodels), não como pesos de desenho amostral complexo (replicação/bootstrap de
    desenho) — os erros-padrão tendem a ser um pouco otimistas (mais estreitos que o
    "correto" sob desenho complexo), mas a direção/magnitude do coeficiente não muda.
    """
    formula_controles = " + ".join(f"C({c})" for c in controles)
    micro = micro.dropna(subset=[outcome, peso, col_grupo] + controles)
    df_fav = micro[micro[col_grupo] == grupo_favorecido]
    df_desf = micro[micro[col_grupo] == grupo_desfavorecido]

    modelo_fav = smf.wls(f"{outcome} ~ {formula_controles}", data=df_fav, weights=df_fav[peso]).fit()
    modelo_desf = smf.wls(f"{outcome} ~ {formula_controles}", data=df_desf, weights=df_desf[peso]).fit()

    # Reindexa pro conjunto UNIÃO de colunas dummy (caso alguma categoria não apareça
    # num dos dois grupos) preenchendo com 0 — trata ausência de dados como "grupo não
    # observado nessa categoria", não como erro.
    exog_fav = pd.DataFrame(modelo_fav.model.exog, columns=modelo_fav.model.exog_names, index=df_fav.index)
    exog_desf = pd.DataFrame(modelo_desf.model.exog, columns=modelo_desf.model.exog_names, index=df_desf.index)
    colunas_comuns = exog_fav.columns.union(exog_desf.columns)

    xbar_fav = exog_fav.reindex(columns=colunas_comuns, fill_value=0.0).mul(df_fav[peso], axis=0).sum() / df_fav[peso].sum()
    xbar_desf = exog_desf.reindex(columns=colunas_comuns, fill_value=0.0).mul(df_desf[peso], axis=0).sum() / df_desf[peso].sum()
    beta_fav = modelo_fav.params.reindex(colunas_comuns, fill_value=0.0)
    beta_desf = modelo_desf.params.reindex(colunas_comuns, fill_value=0.0)
    beta_pooled = 0.5 * (beta_fav + beta_desf)

    explicada = float((xbar_fav - xbar_desf) @ beta_pooled)
    nao_explicada = float(xbar_fav @ (beta_fav - beta_pooled) + xbar_desf @ (beta_pooled - beta_desf))
    hiato_total = float(xbar_fav @ beta_fav - xbar_desf @ beta_desf)

    micro_pooled = micro[micro[col_grupo].isin([grupo_favorecido, grupo_desfavorecido])]
    modelo_restrito = smf.wls(
        f"{outcome} ~ C({col_grupo}, Treatment(reference='{grupo_desfavorecido}')) + {formula_controles}",
        data=micro_pooled, weights=micro_pooled[peso],
    ).fit()
    nome_coef = next(c for c in modelo_restrito.params.index if col_grupo in c)

    return {
        "hiato_total": hiato_total,
        "parcela_explicada": explicada,
        "parcela_nao_explicada": nao_explicada,
        "pct_explicada": 100 * explicada / hiato_total if hiato_total else np.nan,
        "pct_nao_explicada": 100 * nao_explicada / hiato_total if hiato_total else np.nan,
        "residuo_restrito_coef": float(modelo_restrito.params[nome_coef]),
        "residuo_restrito_erro_padrao": float(modelo_restrito.bse[nome_coef]),
        "residuo_restrito_p_valor": float(modelo_restrito.pvalues[nome_coef]),
        "residuo_restrito_significativo": bool(modelo_restrito.pvalues[nome_coef] < 0.05),
        "n_favorecido": int(len(df_fav)), "n_desfavorecido": int(len(df_desf)),
    }


def calcular_gini_ponderado(valores, pesos):
    """Calcula o coeficiente de Gini ponderado para uma distribuição de valores."""
    df = pd.DataFrame({'valores': valores, 'pesos': pesos}).dropna()
    df = df[df['pesos'] > 0] # Ignora pesos zero ou negativos
    if df.empty or len(df) == 1:
        return np.nan

    df = df.sort_values(by='valores').reset_index(drop=True)
    n = len(df)
    # Soma acumulada dos pesos (para o eixo x da curva de Lorenz)
    pesos_acumulados = df['pesos'].cumsum()
    total_pesos = pesos_acumulados.iloc[-1]
    p = pesos_acumulados / total_pesos

    # Soma acumulada dos valores ponderados (para o eixo y da curva de Lorenz)
    valores_ponderados = df['valores'] * df['pesos']
    valores_ponderados_acumulados = valores_ponderados.cumsum()
    total_valores_ponderados = valores_ponderados_acumulados.iloc[-1]

    # Evitar divisão por zero se todos os valores ponderados forem zero
    if total_valores_ponderados == 0:
        return 0.0 # Todos têm 0 de renda, Gini é 0

    l = valores_ponderados_acumulados / total_valores_ponderados

    # Gini = 1 - 2 * área sob a curva de Lorenz
    # A área sob a curva de Lorenz pode ser calculada usando a soma de trapézios.
    # Para cada ponto (p_i, l_i), o trapézio é (p_i - p_{i-1}) * (l_i + l_{i-1}) / 2
    # A soma total é 0.5 * sum((p_i - p_{i-1}) * (l_i + l_{i-1}))
    # Para o cálculo, adicionamos (0,0) como o primeiro ponto
    p_prev = np.concatenate(([0.], p.values[:-1]))
    l_prev = np.concatenate(([0.], l.values[:-1]))

    # área sob a curva de Lorenz por soma de trapézios
    area_sob_lorenz = np.sum((p - p_prev) * (l + l_prev)) / 2
    return 1 - (2 * area_sob_lorenz)


def gini_ponderado(valores, pesos):
    """Calcula o coeficiente de Gini ponderado para uma distribuição de valores.
    Esta é uma função de wrapper para a calcular_gini_ponderado.
    """
    return calcular_gini_ponderado(valores, pesos)


def gini_ponderado_por_grupo(df, coluna_valor, by, peso=COLUNA_PESO):
    """Gini ponderado calculado separadamente para cada grupo de `by` (não o
    Gini nacional geral) — é isso que o item 4.1 do escopo pede."""
    linhas = []
    for chave, grupo in df.groupby(by, observed=True):
        g = gini_ponderado(grupo[coluna_valor], grupo[peso])
        linha = {"gini": g, "n": len(grupo)}
        if isinstance(chave, tuple):
            for col, val in zip(by, chave):
                linha[col] = val
        else:
            linha[by[0]] = chave
        linhas.append(linha)
    return pd.DataFrame(linhas)


def paleta_para_categorias(categorias, mapa_cores=CORES_RACA):
    """Retorna a lista de cores na mesma ordem de `categorias`, útil para
    passar direto a matplotlib/plotly (ex.: color=paleta_para_categorias(ORDEM_RECORTE1))."""
    return [mapa_cores.get(c, "#999999") for c in categorias]
