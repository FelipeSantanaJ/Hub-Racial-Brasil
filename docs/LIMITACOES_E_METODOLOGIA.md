# Limitações e Notas Metodológicas

Documento de referência sobre como os dados deste datahub foram construídos e o que eles
não conseguem responder. Atualizar sempre que uma nova limitação for descoberta (ver
`docs/PLANO.md` para o histórico completo de como cada uma foi encontrada).

## Fonte

PNAD Contínua Trimestral (IBGE), microdados baixados diretamente do FTP público do IBGE
(`src/ingestion/extrator_pnadc.py`), cobrindo 2012 T1 até o trimestre mais recente
disponível. Cerca de 30 milhões de registros pessoa-trimestre no total.

## Recorte racial

A variável `V2010` (Cor ou raça) tem 6 categorias no questionário do IBGE: Branca, Preta,
Amarela, Parda, Indígena, Ignorado. `data/processed/*.parquet` mantém essas 6 categorias
**separadas** (não pré-soma Preta+Parda em "Negra") — isso evita perder informação e evita
um bug real que existia no código herdado (ver `docs/PLANO.md`, Etapa 3). Quando a análise
usa o recorte "Negra" (Preta+Parda), isso é somado sob demanda a partir dos dados brutos.

**Amarela e Ignorado nunca são descartados silenciosamente**, mesmo quando o foco central da
análise é Branca/Negra/Indígena — mas ambos têm amostra pequena (Amarela ~0,4% da amostra,
Ignorado ~0,01%), então qualquer leitura sobre eles precisa de mais cautela estatística.

## Amostra pequena para população Indígena

Autodeclaração indígena é ~0,6% da amostra da PNAD Contínua (ex.: ~2.900 registros em 521 mil
no trimestre mais recente, antes de qualquer segmentação por UF, gênero ou faixa etária).
Cruzamentos mais finos (ex.: mulheres indígenas de 60+ anos numa UF específica) podem ter
poucas dezenas de observações — a estimativa ainda é calculada, mas o intervalo de confiança
é largo. Quando isso importar para uma conclusão, checar `n_amostra` antes de destacar o
número. O Censo Demográfico (Fase 2) tem quesito e cobertura dedicados à população indígena
(incl. terras indígenas) e deve ser tratado como fonte mais robusta para esse recorte
especificamente.

## Geografia: São Paulo sim, ABC Paulista não

- **Brasil, Grandes Regiões, UFs**: sempre disponíveis.
- **Município de São Paulo**: identificável via `UF='35'` + `Capital` não-nula. `Capital`
  **não é** um flag binário — traz o código da UF quando o registro é do município da
  capital daquela UF, e fica em branco caso contrário (mesma lógica vale para `RM_RIDE`).
- **Municípios do ABC Paulista individualmente**: **não são identificáveis** na PNAD
  Contínua pública, por confidencialidade — o IBGE só libera o código de Região
  Metropolitana/RIDE (`RM_RIDE`), sem código de município dentro dela. O mais granular
  possível é "RM São Paulo, não-capital" (`RM_RIDE='35'` e `Capital` nula), que mistura
  Santo André/São Bernardo/São Caetano/Diadema/Mauá/Ribeirão Pires/Rio Grande da Serra com
  outras cidades da Grande São Paulo (ex.: Guarulhos, Osasco). Um recorte por município
  específico do ABC só é possível a partir do Censo Demográfico (Fase 2), que tem código de
  município.

## Renda: nominal vs. real, e o que cada uma serve

`data/processed/renda.parquet` traz `renda_{habitual,efetiva}_{nominal,real}_media`.

- **Nominal**: R$ correntes do próprio trimestre. Só é válido comparar raças/grupos **dentro
  do mesmo trimestre** — nunca comparar nominal entre trimestres diferentes (um R$1.000 de
  2012 e um R$1.000 de 2026 não valem o mesmo).
- **Real**: deflacionado pelo deflator oficial do IBGE (`src/ingestion/baixar_deflator.py`,
  ver `docs/PLANO.md` para os detalhes de onde ele vem e como foi validado), a preços do
  trimestre de referência mais recente (hoje, 2026 T2). **Use sempre esta coluna** para
  qualquer comparação que atravesse mais de um trimestre.
- Renda vem de `VD4019` (habitual) e `VD4020` (efetivo), somando **todos os trabalhos** da
  pessoa — não só o principal.

## Rupturas e mudanças conhecidas que afetam comparabilidade histórica

- **Pandemia de COVID-19 (2020-2021)**: a coleta presencial foi substituída por telefone
  durante boa parte desse período, o que reduziu a taxa de resposta e o tamanho da amostra —
  visível diretamente nos nossos próprios dados: a contagem de registros por trimestre caiu
  de ~550 mil (2019) para um mínimo de ~320 mil (2021 T1), só voltando à faixa histórica em
  2022-2023 (ver `_resumo_extracao.csv` herdado, citado em `docs/PLANO.md`). Qualquer análise
  que cruze esse período precisa citar essa quebra explicitamente, não só mostrar a linha do
  tempo sem comentário.
- **Recalibração de pesos pós-Censo 2022 — checado, sem salto visível**: a hipótese era de
  que o IBGE tivesse revisado as projeções populacionais pós-Censo 2022 de forma
  descontínua, gerando um "degrau" na população total estimada (`SUM(V1028)`) em algum
  trimestre. Checamos isso diretamente (2026-09-04): a população estimada cresce de forma
  suave e contínua em toda a série (2012 T1: 196,7 milhões → 2026 T2: 213,5 milhões), com a
  taxa de crescimento trimestral desacelerando gradualmente (~0,21% em 2012 para ~0,09% em
  2026) — sem nenhum salto abrupto visível, inclusive no período pós-2022. Ou o IBGE já
  suaviza essas revisões retroativamente em vez de aplicar um degrau, ou o efeito aparece em
  outra dimensão (ex.: composição por idade/UF, não no nível agregado nacional) — não
  confirmamos qual das duas. Mantido como ponto de atenção para quando a análise for
  desagregada por sub-população, mas não é uma quebra visível no nível mais agregado.
- **Reforma trabalhista (2017) e da previdência (2019)**: candidatas a pontos de inflexão em
  indicadores de mercado de trabalho (informalidade, taxa de ocupação) — vale checar se
  aparecem como quebras visíveis nas séries de `ocupacao.parquet` ao montar as visualizações
  da Fase 1.
- **Recessão de 2015-2016**: candidata a período de piora aguda em renda/ocupação,
  possivelmente com efeito desigual entre raças — checar na Etapa 6.

## Variável ausente: VD4011A

`VD4011A` (grupamento ocupacional do trabalho principal) nunca existiu com esse nome exato
em nenhum trimestre da série — o nome correto no layout atual do IBGE é `VD4011` (sem "A").
Não afeta nenhum cruzamento obrigatório do MVP (renda, escolaridade, condição de ocupação
usam outras variáveis). Corrigido no extrator para trimestres futuros; os 58 trimestres já
extraídos ficam sem essa coluna específica.

## Nota técnica: tipos de variável no layout do IBGE

Várias variáveis que parecem numéricas na verdade são **texto** no layout de largura fixa do
IBGE (formato `$N.`), incluindo `V2010` (raça), `V2007` (sexo), `UF`, `Capital`, `RM_RIDE`.
Isso já causou um bug real (ver `docs/PLANO.md`, Etapa 3) — qualquer código novo que compare
essas colunas com valores literais precisa usar strings (`'1'`, `'35'`), não inteiros.
`V2009` (idade) e as variáveis de renda (`VD4016/17/19/20`) são numéricas de verdade.
