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
  amostrais (V1028) entram como pesos analíticos da regressão WLS (statsmodels). Até
  2026-09-13, o erro-padrão do teste de significância (`residuo_restrito_erro_padrao`) vinha
  de `cov_type` i.i.d. padrão, sem capturar o conglomerado por UPA do desenho amostral
  complexo da PNAD Contínua — corrigido para `cov_type='cluster'` sobre a UPA nos três
  modelos WLS (ver seção "Hardening" abaixo para o antes/depois). Ainda não é o desenho
  completo (réplicas de estratificação por Estrato, que a PNAD Contínua pública não
  distribui) — o que sobra de otimismo no erro-padrão é bem menor do que o corrigido aqui.
- **Hiato histórico por Welch** (`pnadc_core.tabela_hiatos_significancia`, usada em
  `gerar_hiato_racial` e toda a família de hiatos): mesma limitação do Oaxaca-Blinder acima
  (só peso analítico, sem UPA), mas sem um `cov_type='cluster'` pronto pra usar — o teste de
  Welch aqui é calculado à mão, não via regressão. Checagem de robustez feita em 2026-09-13
  via `pnadc_core.erro_padrao_cluster_bootstrap` (bootstrap por cluster, 200 réplicas)
  rodada sobre os 58 trimestres de `hiato_racial.parquet`
  (`src/processing/checagem_robustez_hiato.py` →
  `data/processed/checagem_robustez_hiato_racial.parquet`): o erro-padrão bootstrap ficou
  **54×-90× maior** (média 67×) que o erro-padrão em produção — bem mais dramático que a
  inflação de 2-3× vista no Oaxaca-Blinder. Causa identificada (não é bug): renda tem cauda
  MUITO pesada (ex.: 2012 T1, Branca — mediana R\$2.089, máximo R\$328.247) e o bootstrap por
  cluster reamostra a UPA inteira como bloco; quando uma UPA isolada concentra 1-2 pessoas com
  renda extrema (achado real e conferido no microdado bruto — não um artefato do pipeline),
  ela entra/sai do bootstrap de forma binária a cada réplica, inflando a variância muito mais
  do que a fórmula fechada (que nunca trata UPA como bloco) ou do que um erro-padrão
  clusterizado de regressão (que pesa a CONTRIBUIÇÃO de cada observação ao score do modelo,
  não o valor bruto — bem menos sensível a um único outlier). **Apesar disso, os 58
  trimestres continuam significativos** mesmo sob esse erro-padrão muito mais conservador —
  o hiato (~R\$1.750-2.040) segue de longe maior que o erro-padrão bootstrap (~R\$55-90).
  Não substitui `tabela_hiatos_significancia` em produção, só confirma que a conclusão de
  significância resiste a um método de erro-padrão bem mais rigoroso.
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
  Q1-Q4. O objetivo original era "decomposição histórica dos 4 quartis", e o topo 10% entregue
  antes cobria só um exemplo disso, não o pedido completo — corrigido ao perceber a lacuna na
  revisão. Mesma ressalva de heaping do P90 vale aqui: cada quartil
  deveria capturar ~25% da população do grupo, mas pode desviar um pouco (checado no
  trimestre mais recente: entre 22% e 31% conforme quartil/raça) — mesma coluna de
  diagnóstico (`pct_populacao_capturada`), sem correção de desempate.

## Gini/Theil por raça, setor econômico e sobre-qualificação (2026-09-05)

- **Gini por raça**: `pnadc_core.gini_ponderado_por_grupo`, já existente (portada do
  notebook original), calcula o Gini DENTRO de cada raça — não confundir com o hiato ENTRE
  raças. Um Gini mais baixo dentro de um grupo não indica "situação melhor" — pode
  simplesmente refletir uma distribuição mais comprimida perto da base (é o caso de Negra
  vs. Branca aqui: Negra tem Gini mais baixo, mas renda média bem menor).
- **Theil T, decomposição entre/dentro**: `pnadc_core.decomposicao_theil_entre_dentro`
  (nova) usa a fórmula clássica de decomposição exata (T_total = T_entre + T_dentro, com
  T_entre ponderado pela participação populacional de cada grupo). Validada com 3 casos
  sintéticos antes de usar em dados reais: grupos com distribuições idênticas →
  T_entre ≈ 0; grupos com médias diferentes mas variância interna zero → T_entre = 100% do
  total; um único grupo → decomposição bate exatamente com o `theil_t` calculado direto.
  Achado (2026 T2): ~7% da desigualdade total vem de diferença ENTRE raças, ~93% é DENTRO —
  isso é um resultado esperado na literatura de decomposição de desigualdade (recortes
  demográficos amplos como raça/gênero tipicamente explicam uma fatia pequena da
  desigualdade total, mesmo quando o hiato entre os grupos é grande e significativo) — não
  é evidência de que a diferença racial "não importa".
- **`setor_atividade` (VD4010)**: 12 categorias, vem ZERO-PADDED (`'01'`..`'12'`) no layout
  do IBGE — checado direto no parquet bruto (`value_counts()`) ANTES de escrever o `CASE`,
  já que os dois bugs anteriores (VD4009, também zero-padded) ensinaram a desconfiar por
  padrão. Estava extraído desde o início (junto com VD4011) mas nunca tinha sido decodificado.
- **`setor_trabalho`** (derivado de VD4009): `'Público'` = empregado público c/ ou s/
  carteira + militar/servidor estatutário (códigos `'05'`,`'06'`,`'07'`); `'Privado'` =
  empregado privado ou doméstico c/ ou s/ carteira (`'01'`-`'04'`); `NULL` p/ empregador,
  conta-própria e familiar auxiliar (não é uma posição assalariada "pública" nem "privada").
- **Sobre-qualificação**: proxy = ter Superior completo E estar em "Ocupações elementares"
  (grupamento_ocupacional categoria 09, VD4011 — corresponde ao ISCO major group 9, o proxy
  padrão de mismatch credencial-ocupação na literatura). É um proxy conservador — não
  captura sobre-qualificação em ocupações intermediárias (ex.: alguém com mestrado
  trabalhando em apoio administrativo também seria "sobrequalificado" em um sentido mais
  amplo, mas não entra nesse indicador). Indígena tem amostra pequena aqui (poucas pessoas
  com Superior completo nesse grupo) — a série fica ruidosa mesmo com média móvel de 4
  trimestres, ler com cautela.

## Matriz de combinações raça × A × B e "só ocupação" isolada (2026-09-05)

- **`renda_multidimensional_faixa.parquet`** e **`renda_multidimensional_geracao.parquet`**:
  raça × sexo × [faixa_etaria ou geracao] × nivel_instrucao × grupamento_ocupacional, Brasil
  apenas, últimos 8 trimestres agrupados (mesma razão de sempre: ocupação tem 11 categorias,
  célula por trimestre isolado ficaria pequena demais). Toda combinação raça×A×B usada nos
  heatmaps novos é derivada dessas duas tabelas, colapsando (média ponderada, via
  `_combinar_negra`/`_media_ponderada_por_grupo`) as dimensões que sobram.
- **Combinação deliberadamente NÃO feita: raça × faixa etária × geração.** As duas variáveis
  descrevem a MESMA coisa (idade) de formas diferentes — faixa etária é a idade atual da
  pessoa, geração é o ano de nascimento aproximado. Cruzá-las geraria células
  minúsculas/instáveis sem adicionar informação além do que "raça × faixa etária" e "raça ×
  geração" (cada uma já existente separadamente) já mostram.
- **"Só ocupação" como controle isolado** (`decomposicao_hiato_ocupacional.parquet` e
  `decomposicao_oaxaca_blinder.parquet`, controles=`grupamento_ocupacional` sem mais nada):
  diferente da cadeia progressiva (que mostra o efeito MARGINAL de ocupação depois de
  idade+escolaridade já estarem no modelo), esta linha isola o efeito de ocupação sozinha.
  Resultado: hiato bruto 67,0% → 33,4% controlando só por ocupação (padronização direta);
  40,4% de "% explicada" via Oaxaca-Blinder (p<0,001) — em ambos os métodos, ocupação sozinha
  explica quase tanto quanto idade+escolaridade JUNTAS.

## Nota técnica: tipos de variável no layout do IBGE

Várias variáveis que parecem numéricas na verdade são **texto** no layout de largura fixa do
IBGE (formato `$N.`), incluindo `V2010` (raça), `V2007` (sexo), `UF`, `Capital`, `RM_RIDE`.
Isso já causou um bug real (ver `docs/PLANO.md`, Etapa 3) — qualquer código novo que compare
essas colunas com valores literais precisa usar strings (`'1'`, `'35'`), não inteiros.
`V2009` (idade) e as variáveis de renda (`VD4016/17/19/20`) são numéricas de verdade.

## Seção "Renda média" do PPT: hiato multidimensional com Welch (2026-09-05)

- **Snapshot de 1 trimestre, não série histórica.** As 22 combinações de hiato que cruzam
  dimensões (gênero, faixa etária/geração, escolaridade — ver
  `agregacoes_pnadc.gerar_hiatos_multidimensionais`) usam só o trimestre mais recente, não
  os 58 trimestres inteiros como `hiato_racial.parquet`/`hiato_preta_parda.parquet` (esses
  dois, a combinação "Raça" sozinha, seguem sendo série histórica completa). Rodar Welch por
  célula em 58 trimestres pras combinações de 3 dimensões (até 70 células cada) seria caro e
  a maioria das células já fica fina o bastante com 1 trimestre só — não valia o custo extra
  pra um gráfico que já é, por natureza, um corte fino.
- **Preta vs. Parda: referência é Parda.** `gerar_hiato_preta_parda` e a família
  multidimensional usam Parda como grupo de referência (é o maior dos dois grupos) e reportam
  o hiato de Preta em relação a ela — sinal negativo significa Preta ganha MENOS que Parda.
  Achado novo: esse sinal **mudou ao longo da série histórica** — Preta chegou a ganhar mais
  que Parda em vários trimestres até ~2015, mas hoje ganha consistentemente menos (-6% no
  trimestre mais recente, ver `hiato_preta_parda_percentual.png`).
- **Categorias residuais excluídas do cálculo da escala de cor.** Os heatmaps de hiato
  restringem os dados às categorias que aparecem nos eixos (`METADADOS_DIM_HIATO[...]["ordem"]`)
  ANTES de calcular o limite da escala divergente — sem isso, uma célula de amostra mínima
  fora do que é mostrado (ex.: Geração Silenciosa/Alpha, quase sem observações) ainda entrava
  no `.abs().max()` e esticava a escala, lavando o contraste do resto do mapa.
- **Universo de dados nem sempre idêntico entre "Todas as raças" e "Apenas negros" do mesmo
  cruzamento.** Pra Raça×Faixa Etária×Escolaridade e Raça×Geração×Escolaridade, a versão
  "Todas as raças" reaproveita `renda_multidimensional_faixa/geracao.parquet` (últimos 8
  trimestres, só ocupados — porque também cruza com ocupação em outros gráficos da mesma
  tabela), enquanto a versão "Apenas negros" usa as tabelas novas de universo amplo
  (`renda_completa.parquet`/`renda_completa_geracao.parquet`, sem restrição de ocupação,
  trimestre mais recente). Os valores dos dois escopos não são estritamente comparáveis
  célula a célula por causa dessa diferença de universo — cada um é internamente consistente,
  mas não foram construídos com a mesma base exata.

## Limiares de topo 10% / base 10% / quartis — escopos (reconstrução do deck, 2026-09-06)

O deck reconstruído tem, além do topo10%/quartis com limiar **dentro de cada raça** (já
documentado acima, `gerar_perfil_topo10_racial`/`gerar_perfil_quartis_racial`), um bloco
novo (`gerar_extremos_racial`/`gerar_quartis_multi_racial` → `extremos_*`/`quartis_multi_racial`)
com o limiar calculado em **três escopos diferentes** — é cálculo novo, não recorte do que
já existia:

- **`brasil`**: um único P90/P10 (ou P25/P50/P75) sobre TODOS os ocupados com renda real
  > 0, sem separar por grupo. Responde "quem chega ao topo / fica na base do Brasil
  inteiro?" — e aí sim a composição racial é informativa (Negra é ~56% dos ocupados mas
  ~33% do topo 10% e ~73% da base 10% no trimestre mais recente). É o oposto do limiar
  dentro-da-raça, que por construção põe 10% de cada raça no seu próprio topo.
- **`genero`**: P90/P10 calculado separadamente dentro de Homens e dentro de Mulheres —
  tira o efeito do hiato de gênero do limiar antes de olhar a composição racial do decil.
- **`raca_genero`**: P90/P10 dentro de cada uma das 4 células raça×gênero — usado só para
  renda em R$ e composição demográfica do decil (a "distribuição racial" nesse escopo
  seria trivial, 100% da própria raça).

Universo: ocupados com `renda_habitual_real > 0` (mesmo escopo da decomposição do hiato e
do topo10% dentro-da-raça). Amostra mínima antes de calcular um quantil: 200 (escopo com 3
limiares), 100-150 nas células raça×gênero. Vale a **mesma ressalva de heaping** já
documentada para o topo10% dentro-da-raça — renda autodeclarada concentra em valores
redondos, então o filtro `>= limiar` captura um pouco mais que 10%/25% exatos; as tabelas
gravam `pct_populacao_capturada` como diagnóstico.

`gerar_quartis_multi_racial` generaliza `gerar_perfil_quartis_racial` para os recortes
`raca` (limiar dentro da raça; dimensões sexo/escolaridade/faixa/geração) e `raca_sexo`
(limiar dentro de raça×gênero; escolaridade/faixa/geração) — cobre os 7 cruzamentos de
quartil pedidos na reconstrução do deck.

## Múltiplas comparações: sem correção formal, por quê isso não muda as conclusões

A série histórica tem 58 trimestres e dezenas de cruzamentos testados (hiato por região,
por geração, por setor público/privado, por categoria de escolaridade/faixa etária/
ocupação, entre outros) — nenhum desses testes usa correção pra múltiplas comparações
(Bonferroni, FDR/Benjamini-Hochberg). Isso é uma limitação conhecida, não uma omissão:

- **Tamanho de efeito, não só significância**: o achado central do projeto é um hiato de
  renda Branca-Negra de ~60-70 p.p. (dependendo do trimestre/corte), com p-valores tipicamente
  < 1e-5 mesmo nos cortes mais finos. Correção de Bonferroni sobre ~60 testes simultâneos
  (a ordem de grandeza de cruzamentos publicados neste repositório) dividiria o limiar de
  significância de 0,05 para ~0,0008 — não chega perto de anular um efeito dessa magnitude.
  Ruído de múltiplas comparações produz falsos positivos marginais (p perto de 0,05), não
  hiatos de dezenas de pontos percentuais com p ordens de grandeza menor que qualquer limiar
  corrigido razoável.
- **Onde a ressalva pesa mais**: cortes com amostra pequena (Indígena em geral, células
  finas de geração×escolaridade×ocupação) têm p-valores mais próximos da fronteira — é
  exatamente onde já existem ressalvas de amostra documentadas nas seções acima
  ("Amostra pequena para população Indígena" etc.). A ausência de correção formal nesses
  casos específicos é uma limitação real, e a leitura desses números já vem qualificada por
  esse motivo.
- **Não corrigido, mas não escondido**: registrado aqui como limitação conhecida em vez de
  omitida — quem for reusar os dados pra um teste específico isolado (não os ~60 já
  publicados) deve aplicar sua própria correção se for testar múltiplas hipóteses novas.

## Aprofundamento raça×gênero (2026-09-13): Branca-Indígena e Preta-Parda em pé de igualdade

Ver [ANALISE_RACA_GENERO.md](ANALISE_RACA_GENERO.md) pros achados completos. Limitações de
amostra novas encontradas ao levar o toolkit pesado (Oaxaca-Blinder, segregação de Duncan,
hiato regional, topo10/quartis) pros pares Branca-Indígena e Preta-Parda:

- **Segregação setorial (VD4010) Branca-Indígena: não publicada.** Mesmo agrupando os 58
  trimestres inteiros, a menor categoria de `setor_atividade` (12 categorias) fica com
  n=11 — abaixo do `n_minimo`=30 já usado no projeto. Diferente da segregação
  ocupacional (11 categorias, pooling de 8 trimestres já fecha com folga, menor categoria
  n=66), aqui nem o pooling máximo resolve — deixado como lacuna documentada, não forçado.
- **Indígena: pooled snapshot em vez de série trimestral, em três lugares novos.**
  Segregação ocupacional Branca-Indígena (`segregacao_ocupacional_indigena.parquet`) e
  topo10%/quartis dentro de Indígena (`perfil_topo10_racial_indigena.parquet`,
  `perfil_quartis_racial_indigena.parquet`) só publicam UMA janela (últimos 8 trimestres,
  mesmo padrão já usado em `gerar_decomposicao_oaxaca_blinder_indigena` e
  `renda_multidimensional_faixa/geracao`), não uma série histórica — checado antes de
  escrever cada função que a amostra trimestre a trimestre não fecha (11 categorias
  ocupacionais ou 3 limiares de quartil precisam de mais gente por corte do que ~750-1.100
  pessoas indígenas/trimestre entregam isoladamente).
- **Boa notícia, checada empiricamente antes de decidir onde agrupar**: nem toda análise
  envolvendo Indígena precisou de pooling. Hiato regional Branca-Indígena por Região
  (`hiato_regional_indigena.parquet`) e a decomposição raça×gênero
  (`decomposicao_raca_genero.parquet`) rodam trimestre a trimestre sem nenhum
  agrupamento — a amostra de Indígena só fica pequena demais quando o corte abre uma
  dimensão categórica FINA (11-12 categorias de ocupação/setor, ou 3 limiares de
  quantil), não em recortes de 2 a 5 categorias (região, sexo).
- **Oaxaca-Blinder Preta-Parda: "% do hiato explicado" sai instável, não é bug.** O hiato
  bruto médio Preta-Parda é pequeno (~-5,8% no trimestre mais recente) — dividir
  parcela-explicada/não-explicada por um `hiato_total` perto de zero produz percentuais
  que variam de -191% a +345% conforme o conjunto de controles
  (`decomposicao_oaxaca_blinder_pretaparda.parquet`). O coeficiente residual em
  log-pontos (não dividido por nada) é a leitura confiável nesse caso — e ele revela um
  padrão real: não-significativo na média (p=0,449), mas significativo e com SINAIS
  OPOSTOS nos extremos da distribuição (positivo no P10, negativo no P90) — ver
  ANALISE_RACA_GENERO.md. Ao reportar Oaxaca-Blinder pra qualquer par com hiato bruto
  pequeno, preferir o coeficiente em log-pontos à porcentagem-do-hiato.
- **Painel rotativo real (`gerar_transicoes_painel`)**: liga a MESMA pessoa entre
  trimestres calendário consecutivos via (UPA, V1008, V2003) — mas essa chave só é
  válida quando `V1016` (número da entrevista) avança exatamente +1 entre os dois
  trimestres. Checado empiricamente antes de implementar (traçando um domicílio real ao
  longo de vários anos): UPA/V1008 são REAPROVEITADOS por um domicílio novo assim que o
  ciclo de 5 entrevistas anterior termina, então essa condição sozinha já evita a maior
  parte dos falsos pareamentos entre pessoas diferentes que passaram pelo mesmo número de
  ordem em ciclos diferentes. Ainda assim, adicionamos duas checagens de robustez
  (sexo idêntico e idade variando no máximo 1 ano entre os dois trimestres) pra descartar
  o caso mais raro de troca de residente DENTRO do mesmo ciclo de 5 entrevistas (ex.:
  alguém muda de domicílio e outra pessoa assume o mesmo número de ordem). Taxa de match
  geral ~68% das pessoas-trimestre da base — compatível com o desenho (cada ciclo dura só
  5 visitas, quem está na 5ª visita não tem continuação). Publicado só POOLED no período
  inteiro (2012-2026), Brasil apenas — mesmo Indígena, que era a preocupação central de
  amostra, chega a n~1.450-1.650 (desemprego→emprego) e n~3.900-4.150 (informal→formal)
  pareados por sexo, mas isso só fecha agregando os 57 pares de trimestres inteiros; uma
  série trimestral ou um corte por UF deixaria a maioria das células abaixo do mínimo.
- **Bug real encontrado e corrigido durante a construção de `gerar_ritmo_convergencia`**:
  a primeira versão do cálculo de "anos pra zerar" só checava se a inclinação da
  tendência era negativa, sem considerar o sinal do NÍVEL atual do hiato. Isso é
  suficiente quando o hiato é positivo (caso Branca-Negra/Branca-Indígena), mas quebra
  quando o hiato já é negativo (caso Preta-Parda, onde Preta já ganha menos que Parda):
  nível negativo + inclinação negativa significa o hiato está ficando MAIS negativo
  (divergindo), não convergindo — a versão com bug teria devolvido "-16,7 anos pra
  zerar", um número sem sentido. Corrigido para exigir que nível e inclinação tenham
  SINAIS OPOSTOS antes de calcular qualquer projeção (a condição real de "aproximando de
  zero"). Mesma classe de bug (comparar/combinar duas quantidades com sinal sem checar
  consistência de sinal primeiro) vale a pena ter em mente em qualquer métrica futura que
  combine nível + tendência.

## Primeira identificação causal (2026-09-13): Leis de Cotas como variação exógena

Ver [ANALISE_CAUSAL_COTAS.md](ANALISE_CAUSAL_COTAS.md) pro desenho completo e os
resultados. Diferente de todo o resto do projeto (descritivo/correlacional, mesmo quando
estatisticamente rigoroso), esta é a primeira tentativa de identificação CAUSAL — as
limitações abaixo são específicas dela.

- **RDD não é possível com este dado.** A PNAD Contínua não tem nota de vestibular nem
  identifica instituição de ensino — o desenho de regressão descontínua que a literatura
  padrão usa pra medir o efeito causal das cotas raciais no Brasil (Mello 2022;
  Francis-Tan & Tannuri-Pianto) não pode ser replicado aqui. O desenho usado
  (diff-in-diff por coorte de exposição, nível agregado) troca identificação fina por
  cobertura nacional/histórica — ver a seção 3 de ANALISE_CAUSAL_COTAS.md.
- **Bug real encontrado na primeira rodada do Desenho A**: `ano_exposicao =
  ano_nascimento + 18` e `exposto = ano_exposicao >= ano_lei` implica um limiar sobre
  `ano_nascimento` de `ano_lei - 18` — a primeira versão do código comparou
  `ano_nascimento` direto contra o ANO DA LEI (2012) sem essa conversão. Como as coortes
  do painel (nascidos 1983-2001) são todas anteriores a 2012, a dummy "pós-lei" saía
  constante em zero pra todo mundo — a regressão soltou aviso de matriz de design
  deficiente em posto (rank-deficient) e o coeficiente saiu zerado, SEM lançar exceção
  nenhuma. Só percebido inspecionando o número produzido (0,0 exato, não um valor
  plausível), não pelo aviso do statsmodels sozinho — mesma lição repetida de outras
  rodadas deste projeto: sempre olhar o NÚMERO, "rodou sem erro" não é suficiente.
- **Event-study sobre dado agregado tem grau de liberdade residual ZERO.** A primeira
  versão do Desenho B rodou uma regressão totalmente saturada (uma dummy por trimestre
  relativo × setor) em cima de um painel já agregado a UMA linha por (trimestre, setor)
  — com exatamente 2 observações por célula da interação completa, o modelo satura
  (R²=1, todo grau de liberdade consumido) e o erro padrão sai indefinido (aviso de
  "divide by zero" do statsmodels). Corrigido reestruturando em dois níveis: a CURVA
  ponto a ponto calculada em forma fechada (diferença de médias ponderadas + soma de
  variâncias em quadratura, sobre o MICRODADO, que tem milhares de pessoas por célula) e
  o RESUMO (tendência pré-lei + DiD global, um coeficiente só) como regressão de verdade
  sobre o microdado, com erro-padrão clusterizado por UPA. Lição geral: rodar uma
  regressão com uma dummy por período só tem erro-padrão válido se cada célula
  período×grupo tiver replicação de verdade (várias pessoas), nunca sobre uma série já
  reduzida a uma média por célula.
- **Bug de escala encontrado no outcome de participação do Desenho B**: a primeira
  versão construiu o outcome de participação como uma dummy 0/1 (fração), mas os
  gráficos/textos já assumiam "pontos percentuais" — os números saíam 100x menores do
  que o rótulo dizia (ex.: eixo do gráfico mostrando "-0,0012" quando deveria mostrar
  "-0,12"). Pego numa inspeção visual do gráfico gerado (a escala do eixo não batia com
  o que o subtítulo prometia), não durante a checagem dos números da regressão — reforça
  o hábito já estabelecido no projeto de olhar o PNG renderizado, não só a tabela.
- **Limitação de esfera de governo no Desenho B, documentada sem tentar contornar**:
  `setor_trabalho` (derivado de VD4009) não distingue federal de estadual/municipal — só
  o federal foi atingido pela Lei 12.990/2014. O grupo "Público" do desenho mistura
  observações tratadas (federal) com nunca-tratadas (estadual/municipal), diluindo
  qualquer efeito estimado na direção de zero. `setor_atividade`/VD4010 tem uma categoria
  de administração pública, mas também não separa esfera de governo — não existe uma
  variável já extraída que resolva isso; registrado como limitação real, não contornado
  com uma aproximação que os dados não sustentam.
- **Sem correção de múltiplas comparações**, mesma limitação já documentada acima pro
  resto do projeto — especialmente relevante aqui porque o Desenho B produziu só UM
  resultado significativo (o hiato de renda dentro do setor público, p=0,041) entre
  vários testes (2 outcomes × várias raças/especificações) — um p isolado perto de 0,05
  entre vários testes pede mais cautela do que um p ordens de grandeza menor teria.
