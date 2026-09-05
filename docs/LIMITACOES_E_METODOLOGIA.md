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

## Variável corrigida: VD4011A → VD4011 (grupamento ocupacional)

`VD4011A` nunca existiu com esse nome exato em nenhum trimestre da série — o nome correto no
layout do IBGE é `VD4011` (sem "A"), 11 categorias (diretores/gerentes, profissionais de
nível superior, técnicos, apoio administrativo, serviços/comércio, agropecuária,
construção/ofícios, operadores de máquinas, ocupações elementares, forças armadas/policiais,
maldefinidas). Corrigido no extrator e a série histórica completa foi **reextraída** (58
trimestres) para trazer essa coluna — usada na decomposição do hiato racial por ocupação
(ver `docs/PLANO.md`, seção "Decomposição do hiato").

## Aprofundamento estatístico (2026-09-04): Oaxaca-Blinder, RIF, segregação, quebra estrutural

- **Decomposição de Oaxaca-Blinder** (`pnadc_core.decomposicao_oaxaca_blinder`): os pesos
  amostrais (V1028) entram como pesos analíticos da regressão WLS (statsmodels), não como
  pesos de desenho amostral complexo (réplicas/bootstrap de desenho, que a PNAD Contínua
  pública não distribui). Os erros-padrão tendem a ser um pouco otimistas (mais estreitos
  que o "correto" sob desenho complexo) — a direção e a ordem de grandeza do coeficiente não
  mudam, mas o p-valor exato deve ser lido como aproximado, não exato ao terceiro dígito.
- **RIF por quantil** (`pnadc_core.rif_quantil`, Firpo-Fortin-Lemieux 2009): a densidade no
  ponto do quantil é estimada por kernel gaussiano ponderado sobre a distribuição CONJUNTA
  (Branca+Negra), não separadamente por grupo — é assim que a definição de RIF garante que a
  média da RIF recupera o quantil da distribuição de referência correta.
- **Teste de quebra estrutural** (`agregacoes_pnadc.gerar_quebra_estrutural`): é um teste de
  Chow simplificado — uma quebra conhecida a priori (a data do evento), testada isoladamente
  na série inteira (58 pontos trimestrais). NÃO é uma busca por múltiplas quebras
  desconhecidas (ex.: Bai-Perron) e não controla por outros eventos concorrentes no mesmo
  período (ex.: a pandemia caiu perto da reforma da previdência) — tratar como evidência de
  correlação temporal, não de causalidade.
- **Índice de segregação de Duncan**: só calculado para Branca vs. Negra na série trimestral
  — Indígena fica de fora (amostra pequena demais pra uma distribuição de 11 categorias
  ocupacionais trimestre a trimestre).

## Novas variáveis (2026-09-04): informalidade, horas, alfabetização, desalento

Decodificação (ver `data/raw/pnadc_extraido/_tmp/dicionario/` pro dicionário completo do
IBGE):

- **VD4009** (posição na ocupação, detalhada) → `tem_carteira_assinada`: `TRUE` p/
  empregado privado/doméstico/público COM carteira e militar/servidor estatutário (sempre
  "protegido"); `FALSE` p/ empregado privado/doméstico/público SEM carteira; `NULL`
  (não aplicável) p/ empregador, conta-própria e trabalhador familiar auxiliar — o conceito
  de "carteira assinada" não existe pra essas posições. `pct_com_carteira` em
  `informalidade.parquet` é calculado só sobre quem tem o conceito aplicável (empregados).
- **VD4012** (contribuição previdenciária) → `contribui_previdencia`: cobre TODOS os
  ocupados, inclusive conta-própria/empregador — é o indicador mais amplo de proteção
  social, complementar a `tem_carteira_assinada`.
- **V3001** (alfabetização) e **V3014** (frequência escolar atual): perguntas feitas pra
  toda a população 14+, não têm a ambiguidade de "sem instrução" (não são código de
  não-resposta).
- **VD4003** (força de trabalho potencial) e **VD4005** (desalento): só têm valor definido
  para quem está FORA da força de trabalho (VD4001='2') — dentro da força de trabalho o
  conceito não se aplica e a coluna vem NULL, por desenho.
- **Horas trabalhadas → renda por hora**: `renda_por_hora_real_media` é uma aproximação
  (renda habitual mensal ÷ (horas semanais habituais × 4,345 semanas/mês)), calculada pessoa
  a pessoa e depois ponderada — não é uma medida oficial do IBGE, é derivada aqui.

## Moradia e deslocamento — não disponíveis nesta base (2026-09-04)

Características de domicílio (água, esgoto, tipo de domicílio etc.) só existem no bloco
"Visita 1" da PNAD Contínua — uma sub-amostra menor (1/5 dos domicílios, só na primeira
entrevista do painel rotativo), que exigiria uma extração SEPARADA da que já temos (o
arquivo trimestral regular não traz essas colunas). Mobilidade/deslocamento para o trabalho
não é coletado na PNAD Contínua regular. Ambos ficam para o Censo Demográfico (Fase 2), que
tem os dois blocos.

## Geração (coorte de nascimento sintética), "topo 10%" e os 4 quartis (2026-09-05)

- **Geração**: `ano_nascimento_aprox = ano da pesquisa - V2009` (idade) — aproximado, não
  considera mês de nascimento x mês de entrevista, pode errar por 1 ano perto de cada
  fronteira. Fronteiras usadas (convenção internacional/brasileira comum): Geração
  Silenciosa (antes de 1946), Baby Boomer (1946-1964), Geração X (1965-1980), Millennial
  (1981-1996), Geração Z (1997-2012), Geração Alpha (2013+, nunca aparece de fato no recorte
  14+ anos desta base — o mais jovem possível seria alguém que completasse 14 anos em 2027,
  fora da nossa janela de dados). É uma **coorte sintética** (Deaton, 1985): cada trimestre
  ainda traz pessoas diferentes dentro da mesma geração, só o grupo de nascimento se mantém
  fixo — não é o mesmo que acompanhar os mesmos indivíduos ano a ano (a PNAD Contínua tem um
  painel rotativo real de até 5 entrevistas/15 meses, mas isso não alcança décadas).
- **"Topo 10%" por raça**: `pnadc_core.quantil_ponderado` calcula o P90 ponderado dentro de
  Branca e dentro de Negra SEPARADAMENTE (não um corte único pro Brasil). Renda autodeclarada
  tem heaping forte (checado direto no parquet bruto — ex.: no trimestre mais recente, 3,1%
  de Branca declara EXATAMENTE R$10.000 e 3,4% de Negra declara EXATAMENTE R$5.000) — quando
  o P90 cai bem em cima de um valor populoso desses, o filtro `>= limiar` inclui todo mundo
  empatado ali, capturando mais que 10% de fato (checado manualmente: ~11,5% de Branca,
  ~12,8% de Negra no trimestre mais recente). A coluna `pct_populacao_capturada` em
  `perfil_topo10_racial.parquet` registra o valor real capturado a cada trimestre — não
  tentamos uma correção de desempate mais sofisticada (fracionar a inclusão de quem está
  exatamente no limiar) por estar fora do escopo desta rodada.
- **4 quartis por raça** (`perfil_quartis_racial.parquet`): generaliza o "topo 10%" acima —
  em vez de só o P90, calcula P25/P50/P75 dentro de cada raça e classifica cada pessoa em
  Q1-Q4. Pedido originalmente como "decomposição histórica dos 4 quartis", o topo 10% tinha
  sido entregue como resposta parcial (só um exemplo dado pelo usuário, não o pedido
  completo) — corrigido depois que o usuário perguntou se a quebra por quartil dentro de
  cada raça tinha sido entendida. Mesma ressalva de heaping do P90 vale aqui: cada quartil
  deveria capturar ~25% da população do grupo, mas pode desviar um pouco (checado no
  trimestre mais recente: entre 22% e 31% conforme quartil/raça) — mesma coluna de
  diagnóstico (`pct_populacao_capturada`), sem correção de desempate.

## Nota técnica: tipos de variável no layout do IBGE

Várias variáveis que parecem numéricas na verdade são **texto** no layout de largura fixa do
IBGE (formato `$N.`), incluindo `V2010` (raça), `V2007` (sexo), `UF`, `Capital`, `RM_RIDE`.
Isso já causou um bug real (ver `docs/PLANO.md`, Etapa 3) — qualquer código novo que compare
essas colunas com valores literais precisa usar strings (`'1'`, `'35'`), não inteiros.
`V2009` (idade) e as variáveis de renda (`VD4016/17/19/20`) são numéricas de verdade.
