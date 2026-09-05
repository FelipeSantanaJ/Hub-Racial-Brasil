# Plano de Projeto — Datahub de Análise Racial no Brasil

Documento vivo. Atualizar conforme o projeto avança (datas, marcos concluídos, riscos novos).

- **Início**: 2026-09-04
- **Ritmo assumido**: 3-5h/semana (projeto pessoal, horas vagas).
- **Status atual**: 🏁 **Fase 1 (MVP) concluída em 2026-09-04**, mesmo dia do início do repo
  — graças à base herdada de um projeto anterior no Colab (ver "Base herdada" abaixo).
  Próximo passo: Fase 2 (Censo Demográfico), ainda não detalhada.

---

## Base herdada de um projeto anterior (Colab/Drive)

Antes deste repo, o projeto rodava em notebooks Colab com storage no Google Drive
(`MyDrive/pnadc_microdados/`). Essa base **não é descartada** — é o ponto de partida da
Fase 1:

- **`parquet/ano=2012.../ano=2026/trimestre=1..4/*.parquet`**: extração pessoa-a-pessoa da
  PNAD Contínua, já com as colunas de interesse selecionadas (geografia incl. `RM_RIDE`,
  raça/cor `V2010`, sexo, idade, escolaridade `VD3004/VD3005`, mercado de trabalho
  `VD4001-VD4035`, peso amostral `V1028`). Cobre 2012 T1 até 2026 T1 (56 trimestres).
  **Faltam**: 2026 T2 (publicado pelo IBGE em 14/ago/2026, ainda não extraído) e os
  trimestres seguintes conforme forem saindo.
- **`pnadc_core.py`**: funções compartilhadas (estatística ponderada, IC, teste de
  significância Welch, deflator, Gini ponderado, recortes raciais/gênero, paleta de cores).
  Já **portado** para `src/utils/pnadc_core.py` neste repo.
- **`extracao_pnadc_historico.ipynb`**: o notebook que gerou a base acima (download direto
  do FTP do IBGE, parsing do layout SAS de largura fixa, conversão em Parquet particionado).
  Já **portado e adaptado** para `src/ingestion/extrator_pnadc.py` (paths locais, sem
  Colab/Drive, idempotente por trimestre via marcador `_SUCCESS`).
- Outros notebooks do Drive (`atualizacao_variaveis_pnadc.ipynb`, `analise_*.ipynb`,
  `ETL das fontes.ipynb`) eram exploratórios/redundantes — o `ETL das fontes.ipynb` em
  particular contém várias tentativas abandonadas via API SIDRA (algumas com dados
  simulados de fallback) e não foi aproveitado; a abordagem de microdados + DuckDB é
  superior para os cruzamentos que este projeto precisa (idade/RM/significância
  estatística, que a API agregada do SIDRA não permite).

### Passo imediato — recuperar a base (fora do Claude, ver metodologia abaixo)

1. Baixar manualmente a pasta `parquet` inteira do Drive (~500 MB, botão direito → Fazer
   download → .zip) e extrair em `data/raw/pnadc_extraido/parquet/` neste repo, mantendo a
   estrutura `ano=AAAA/trimestre=T/*.parquet`.
2. Rodar `python -m src.ingestion.extrator_pnadc --ano-inicial 2026 --ano-final 2026` para
   buscar o 2026 T2 (e trimestres seguintes, conforme o IBGE for publicando) — o script pula
   automaticamente o que já tem marcador `_SUCCESS`, então é seguro rodar por cima da base
   herdada.
3. (Opcional) sincronizar os trimestres novos de volta pro Drive, se você quiser manter o
   Drive como backup — isso pode ser feito por mim (Claude) quando chegar a hora, já que são
   poucos arquivos pequenos (~9 MB/trimestre); não faz sentido fazer isso para os 56
   trimestres já existentes (ver metodologia de tokens abaixo).

---

## Como trabalhar este projeto com o Claude Code (sessões e tokens)

Você pediu pra eu levar em conta que não vai usar a totalidade dos seus tokens só nisso, já
que também usa o Claude para outros processos (o projeto **MIA\Scripts**, de trabalho, é hoje
de longe o que mais concentra uso — não tenho acesso a um medidor exato de custo/cota da sua
conta, então isso é uma leitura pelo tamanho do histórico de sessões salvo localmente, não um
número oficial). Diante disso, a estrutura de trabalho recomendada:

1. **Este projeto já vive num diretório próprio** (`C:\Users\jfdsdsantana\Projects\datahub-racial-brasil`,
   fora do MIA\Scripts) — o histórico de conversas fica isolado do seu trabalho principal por
   padrão, sem competir por contexto com ele.
2. **Uma etapa da tabela abaixo = uma sessão** (ou um bloquinho de etapas relacionadas). Abra
   a sessão apontando pro `CLAUDE.md` + este `PLANO.md` — não precisa colar histórico de
   sessões anteriores.
3. **Feche cada sessão atualizando a tabela de status** deste arquivo (uma frase: o que
   mudou, o que falta) antes de encerrar. Assim a próxima sessão não depende do transcript
   anterior, só do arquivo — pode abrir uma sessão nova ou dar `/clear` sem perder contexto
   relevante.
4. **Processamento pesado roda como script Python via terminal**, não como algo que o Claude
   lê linha a linha — peça resumos/contagens (`df.describe()`, `SELECT COUNT(*) ...`), nunca
   dataframes inteiros no chat.
5. **Transferência de dados binários grandes fica fora do Claude.** O zip de ~500 MB do Drive
   (passo 1 acima) é baixo manual pelo navegador — passar arquivo binário grande por chamada
   de ferramenta custaria uma fortuna em tokens (uma chamada de ~3 MB já estourou o limite de
   uma resposta de ferramenta nesta própria sessão de planejamento). Atualizações incrementais
   pequenas (1 trimestre novo, ~9 MB) são a exceção onde vale a pena eu mediar via Drive.
6. **Pode abrir/fechar sessões livremente entre etapas** — não precisa manter uma sessão
   maratona aberta o projeto inteiro. Isso é bom tanto para tokens quanto porque o ritmo real
   (3-5h/semana) já é o fator limitante, não o contexto.

---

## Visão geral das fases

| Fase | Escopo | Status | Estimativa |
|---|---|---|---|
| 1 | MVP — PNAD Contínua (renda, escolaridade, ocupação) | ✅ concluída | 2026-09-04 (1 dia; estimativa original: ~6 semanas) |
| 2 | Censo Demográfico (moradia, recorte municipal — resolve limitação do ABC Paulista) | ⏳ não iniciada | a partir de 2026-10-16 |
| 3 | Saúde (DataSUS/SIM/SINASC/PNS) | ⏳ não iniciada | a definir após Fase 2 |
| 3.x | Módulos adicionais (ver tabela "Outras fontes" abaixo) — ordem flexível | ⏳ pool de candidatos | intercalar conforme interesse |
| 4 | Dashboard público (Observable Framework) | ⏳ não iniciada | após consolidar Fases 1-3 |
| 5 | Conteúdo Instagram/TikTok | ⏳ prioridade baixa | sem data fixa |

A Fase 1 encolheu de ~33h/12 semanas (estimativa original, do zero) para ~21h/6 semanas
graças ao reaproveitamento da base já extraída no Colab.

---

## Fase 1 — MVP: PNAD Contínua (2026-09-04 → 2026-10-15)

**Objetivo**: dataset(s) agregado(s) de renda, escolaridade e mercado de trabalho, cruzados
por **Raça/Cor × Gênero × Faixa etária**, para Brasil / Regiões / UFs / Município de São
Paulo / Região Metropolitana de São Paulo, cobrindo 2012 T1 até o trimestre mais recente
disponível no FTP do IBGE.

**Recorte racial**: três grupos centrais em pé de igualdade — **Branca**, **Negra**
(Preta + Parda) e **Indígena** — com Amarela sempre explicitada nas tabelas (nunca
descartada silenciosamente). `pnadc_core.py` já trata Indígena como categoria de primeira
classe em `aplicar_recorte1`/`aplicar_recorte2` (ver risco sobre tamanho amostral abaixo).

**Critério de "pronto"**: parquet(s) versionado(s) em `data/processed/` com todos os
cruzamentos obrigatórios, mais pelo menos um gráfico comparativo (Branca vs. Negra vs.
Indígena, ao longo do tempo) publicado no README.

| # | Etapa | Estimativa | Semana | Marco |
|---|---|---|---|---|
| 0 | Recuperar a base herdada do Drive (download manual do zip) + portar `pnadc_core.py` e o extrator para este repo | 3h | Sem 1 (04-10/set) | ✅ concluído 2026-09-04 |
| 1 | Validar a base herdada (contagens batem com `_resumo_extracao.csv` original; schema confere com `VARIAVEIS_DESEJADAS`) | 2h | Sem 2 (11-17/set) | ✅ concluído 2026-09-04 — ver resultado abaixo |
| 2 | Rodar o extrator para os trimestres faltantes (2026 T2 em diante) | 2h | Sem 2-3 (11-24/set) | ✅ concluído 2026-09-04 — 2026 T2 processado (521.730 linhas); T3/T4 ainda indisponíveis no IBGE |
| 3 | Ajustar/confirmar o recorte racial de 3 grupos (Branca/Negra/Indígena) em todas as agregações; documentar caveat de amostra pequena para Indígena | 2h | Sem 3 (18-24/set) | ✅ concluído 2026-09-04 — bug crítico encontrado e corrigido, ver abaixo |
| 4 | Agregações finais: renda, escolaridade, ocupação/desocupação × raça × gênero × faixa etária × geografia (Brasil/Região/UF/SP capital/RM SP) | 6h | Sem 4 (25/set-01/out) | ✅ concluído 2026-09-04 — `data/processed/{renda,escolaridade,ocupacao}.parquet`, ver abaixo |
| 5 | Documentar limitações conhecidas (rupturas metodológicas, RM × município, amostra indígena) em `docs/` | 2h | Sem 5 (02-08/out) | ✅ concluído 2026-09-04 — `docs/LIMITACOES_E_METODOLOGIA.md` |
| 6 | Primeiras visualizações exploratórias + gráfico comparativo no README | 4h | Sem 6 (09-15/out) | ✅ concluído 2026-09-04 — 🏁 **fecha a Fase 1** (~6 semanas antes do previsto) |

Total estimado: ~21h ativas (vs. ~33h da estimativa original do zero). Concluída em ~1 dia
de trabalho intenso em vez de 6 semanas — a maior parte da estimativa original assumia
retomar o projeto do zero, sem a base herdada do Colab nem a disponibilidade concentrada
desta sessão.

### Etapa 5 e 6 (2026-09-04)

- **Etapa 5**: consolidado em [`docs/LIMITACOES_E_METODOLOGIA.md`](LIMITACOES_E_METODOLOGIA.md)
  — fonte, recorte racial, amostra indígena, geografia (SP capital vs. ABC), renda
  nominal/real, rupturas conhecidas (checamos a hipótese de recalibração pós-Censo 2022
  contra os dados — sem salto visível no nível populacional agregado, documentado como tal
  em vez de deixar como suposição não verificada), variável `VD4011A` ausente, e a nota
  técnica sobre tipos texto vs. numérico no layout do IBGE.
- **Etapa 6**: `src/processing/graficos_fase1.py` gera `docs/img/renda_por_raca.png`
  (renda habitual real, Branca vs. Negra vs. Indígena, Brasil, 2012-2026), publicado no
  README. Paleta e specs seguem a skill de dataviz do projeto (paleta categórica validada
  via `validate_palette.js`, PASS com um WARN de contraste mitigado por rótulos diretos).
  Indígena usa média móvel de 4 trimestres (amostra pequena torna a série trimestral bruta
  ruidosa demais para mostrar tendência).
- **Etapa 6 — expandida a pedido (2026-09-04, mesmo dia)**: mais 7 gráficos além do
  mínimo da Fase 1 ("pelo menos um"), todos em `docs/ANALISE_FASE1.md` (galeria completa
  com a leitura de cada um) e o principal também no README: Preta e Parda separadas (sem
  pré-somar em "Negra"), renda × gênero (com paleta de 4 cores validada à parte para o
  corte detalhado — azul/laranja/violeta/aqua), escolaridade × gênero, renda × faixa
  etária × gênero, e **renda × nível de instrução** (geral + só homens + só mulheres) —
  esse último exigiu uma agregação nova (`gerar_renda_por_escolaridade` em
  `agregacoes_pnadc.py` → `data/processed/renda_por_escolaridade.parquet`, 143.157
  linhas), já que nem `renda.parquet` nem `escolaridade.parquet` tinham as duas dimensões
  juntas. Achado central: o hiato racial de renda **sobrevive ao controle por
  escolaridade** e se abre mais no Superior completo (Branca R\$8.104 vs. Negra R\$5.701,
  Brasil, 2026 T2) — maior entre homens (~46% de diferença) que entre mulheres (~36%).
  No caminho, corrigido mais um bug real: `_agregar_por_geografia` tinha `faixa_etaria`
  fixo no `GROUP BY` mesmo quando o `SELECT` não a listava, o que geraria linhas
  "duplicadas" ocultas na nova agregação — virou parâmetro opcional
  (`incluir_faixa_etaria`).

### Etapa 6 — segunda rodada de expansão, "todas as interseções" (2026-09-04)

Pedido explícito: cobrir sistematicamente raça × gênero × faixa etária × escolaridade, não
só uma curadoria — "um gráfico combinado + um por categoria" para cada dimensão cruzada com
raça, e o mesmo tratamento repetido só para Preta vs. Parda (sem Branca/Indígena). Foram pra
43 gráficos no total (ver `docs/ANALISE_FASE1.md`). Principais adições:

- **Rótulos simplificados**: "Negra (Preta+Parda)" → só "Negra" em todos os gráficos (a
  definição já está documentada uma vez em vez de repetida em cada legenda).
- **Preta × Parda em todos os níveis**: gênero (combinado + um por gênero), faixa etária
  (combinado + 5 individuais), escolaridade (combinado + 7 individuais) — 18 gráficos só
  dessa família, reaproveitando os mesmos helpers genéricos (`_serie_por_raca`,
  `_grafico_serie_temporal`) usados pro recorte de 3 raças.
- **Um gráfico por categoria**: 5 por faixa etária + 7 por nível de instrução (série
  temporal 2012-2026 filtrada a uma faixa/nível fixo), tanto pra Branca/Negra/Indígena
  quanto pra Preta/Parda.
- **Heatmap de 4 dimensões** (`renda_completa_heatmap.png`): raça × gênero × faixa etária ×
  nível de instrução tudo de uma vez — exigiu nova agregação Brasil-only
  (`gerar_renda_completa` → `data/processed/renda_completa.parquet`, 20.377 linhas; só
  Brasil porque abrir mais 4 dimensões por 5 níveis geográficos deixaria a maioria das
  células com amostra residual).
- **Gráficos de hiato Branca vs. Negra com significância estatística de verdade**
  (`hiato_racial_percentual.png`, `hiato_racial_absoluto.png`) — nova agregação
  `gerar_hiato_racial` que roda `pnadc_core.tabela_hiatos_significancia` (teste de Welch)
  trimestre a trimestre sobre os MICRODADOS (não sobre médias já agregadas, que não dão pra
  calcular erro padrão corretamente) → `data/processed/hiato_racial.parquet` (58 linhas).
  Resultado: os 58 trimestres são estatisticamente significativos a 95%.
- **Bug estatístico real encontrado e corrigido**: implementando o teste de significância
  com rigor, a banda de intervalo de confiança saiu absurda (40% a mais de 100%, para uma
  amostra de centenas de milhares de pessoas). Causa: `erro_padrao_media_ponderada` em
  `pnadc_core.py` tinha uma fórmula que não batia com o próprio comentário que a documentava
  (citando Cochran 1977) — usava um denominador diferente do descrito E multiplicava o
  resultado por `len(valores)` no final, inflando o erro padrão por um fator de ~√n (pra
  n ~ centenas de milhares, um fator de centenas de vezes). Corrigido pra bater exatamente
  com a fórmula documentada; validado com um teste unitário contra a fórmula clássica
  s/√n do caso não-ponderado. O bug tornava os IC muito mais largos que o real (nunca
  overclaiming significância — se algo, o oposto), mas ainda assim precisava de correção
  antes de virar gráfico público.
- **Bug de layout descoberto durante a depuração acima**: dois gráficos (`hiato_racial_*`)
  vieram com o eixo X inexplicavelmente espremido num canto — depurado a fundo (isolando
  cada parte do código) até achar que o subtítulo longo demais fazia o `fig.tight_layout()`
  encolher o retângulo do eixo pra ~22% da largura da figura pra tentar acomodar o texto.
  Corrigido encurtando os subtítulos; lição: `tight_layout()` pode silenciosamente destruir
  o layout de um gráfico com texto longo, sem lançar nenhum erro — vale conferir visualmente
  todo gráfico novo, não só rodar sem exceção.
- **Apresentação em PowerPoint**: `src/processing/apresentacao_fase1.py` →
  `docs/Datahub_Racial_Brasil_Fase1.pptx` (56 slides: 1 título + 12 divisores de seção + 43
  gráficos), gerada automaticamente a partir da mesma lista de imagens.
- **Reextração completa da série histórica em andamento** (58 trimestres, ~30min) pra trazer
  `VD4011` (grupamento ocupacional/tipo de ocupação) — variável que faltava desde a Etapa 1
  (era pedida como `VD4011A`, nome que nunca existiu; corrigido pra `VD4011` mas só passou a
  valer pra trimestres extraídos depois da correção). Motivação: pergunta de pesquisa sobre
  se o hiato racial de renda, controlando por idade e escolaridade, se explica por
  segregação ocupacional (negros em ocupações que pagam menos) ou persiste mesmo dentro da
  mesma ocupação — ver seção "Decomposição do hiato" abaixo.

## Decomposição do hiato: ocupação explica, ou é só cor da pele? ✅ (2026-09-04)

Pergunta feita pelo usuário: controlando por idade e escolaridade, o hiato de renda entre
negros e brancos existe porque estão em ocupações diferentes (que pagam menos), ou persiste
mesmo dentro da mesma ocupação?

- **`VD4010`** (setor/ramo de atividade econômica) já estava disponível.
- **`VD4011`** (grupamento ocupacional, 11 categorias — diretores/gerentes, profissionais
  de nível superior, técnicos, apoio administrativo, serviços/comércio, agropecuária,
  construção/ofícios, operadores de máquinas, ocupações elementares, forças
  armadas/policiais, maldefinidas) exigiu a reextração completa da série (58 trimestres)
  concluída nesta sessão — mesmas contagens de linhas de antes, agora com a coluna nova.
- **Método**: padronização direta (`gerar_decomposicao_hiato_ocupacional` em
  `agregacoes_pnadc.py`) — não é uma regressão Oaxaca-Blinder completa, mas responde a
  mesma pergunta de forma direta e auditável: dentro de cada célula (faixa etária ×
  escolaridade × ocupação, só entram células com ≥30 pessoas de cada raça), calcula a média
  de Branca e "padroniza" usando a distribuição de Negra nessas células como peso — ou seja,
  "se Branca tivesse a mesma distribuição de idade/escolaridade/ocupação que Negra tem hoje,
  qual seria a média de Branca?". Usa os últimos 8 trimestres agrupados (2 anos) porque abrir
  por ocupação (11 categorias) deixa as células menores — só pessoas ocupadas com ocupação
  identificada entram (universo onde a pergunta faz sentido).
- **Resultado** (`data/processed/decomposicao_hiato_ocupacional.parquet`,
  `docs/img/decomposicao_hiato_ocupacional.png`):

  | Controle | Hiato | Amostra de Negra incluída |
  |---|---|---|
  | Nenhum (hiato bruto) | 67,0% (R\$1.884) | 100% |
  | + faixa etária | 63,9% (R\$1.797) | 100% |
  | + faixa etária + escolaridade | 30,3% (R\$851) | 99,99% |
  | + faixa etária + escolaridade + ocupação | **24,3% (R\$684)** | 99,91% |

  **Leitura**: idade sozinha explica quase nada do hiato (as distribuições etárias de
  Branca e Negra não são tão diferentes). Escolaridade explica MUITO — mais da metade do
  hiato desaparece só com esse controle. Ocupação explica uma fatia adicional menor. Mas
  **mesmo comparando pessoas de mesma idade, mesma escolaridade E mesma categoria
  ocupacional, sobra um hiato de ~24%** — não explicado por nenhuma dessas três variáveis.
  Isso não é prova direta de discriminação (podem existir outros fatores não medidos aqui —
  horas trabalhadas, formalidade, região, porte da empresa, senioridade dentro da mesma
  ocupação), mas é evidência de que "estar na mesma ocupação" está longe de eliminar o
  hiato racial de renda.
- **Limitação a documentar**: esse resultado NÃO passou pelo teste de significância formal
  (Welch) célula a célula — é uma comparação de médias padronizadas, não um teste
  estatístico completo. Ainda assim, a queda de 67%→24% e a alta retenção de amostra (>99%
  em todos os cortes) tornam o padrão qualitativo (idade pouco explica, escolaridade explica
  muito, resta hiato mesmo controlando ocupação) bastante robusto. Aplicar
  `tabela_hiatos_significancia` ao recorte final (mesma idade/escolaridade/ocupação) é um
  refinamento natural para uma futura rodada.

## Aprofundamento estatístico e novas variáveis ✅ (2026-09-04, terceira rodada)

A pedido do usuário: (1) aplicar teste de significância formal ao resíduo da decomposição
do hiato por ocupação (pendência deixada em aberto na seção anterior); (2) pensar em outras
análises/cruzamentos/metodologias; (3) pensar em outras variáveis da PNAD ainda não usadas.
Antes de implementar, apresentei um menu de opções (AskUserQuestion) e o usuário escolheu
TUDO: regressão Oaxaca-Blinder (não a alternativa mais simples de só adaptar o teste de
Welch), as 4 variáveis novas sugeridas (+ moradia/deslocamento, que não existem na PNAD
Contínua trimestral — ver nota abaixo), e os 4 métodos extra sugeridos.

**Moradia/deslocamento — não disponível nesta base**: características de domicílio só
existem no bloco "Visita 1" da PNAD Contínua (sub-amostra menor, 1/5 dos domicílios,
extração separada da que já temos) e mobilidade/deslocamento para o trabalho não é
coletado na PNAD Contínua regular. Continua no escopo do Censo (Fase 2), não entrou nesta
rodada.

### Novas funções em `pnadc_core.py`

- **`decomposicao_oaxaca_blinder`**: decomposição twofold clássica (Blinder 1973, Oaxaca
  1973) do hiato médio de log-renda entre dois grupos, controlando por covariáveis
  categóricas — regressão WLS separada por grupo, coeficientes de referência = média dos
  dois grupos (convenção Reimers 1983, evita a arbitrariedade de usar só um grupo como
  "estrutura não-discriminatória"). Separa o hiato em **parcela explicada** (diferença de
  composição — idade/escolaridade/ocupação) e **parcela não-explicada** (mesma composição,
  retorno diferente — proxy de discriminação, não prova direta). Ajusta TAMBÉM um modelo
  único restrito (mesmos coeficientes de controle nos dois grupos, só o intercepto de grupo
  muda) — o coeficiente de raça desse modelo já sai com erro-padrão e p-valor prontos, sem
  precisar de bootstrap: é o teste de significância formal que faltava.
- **`rif_quantil`**: Recentered Influence Function (Firpo-Fortin-Lemieux 2009) de um
  quantil — permite rodar a MESMA decomposição de Oaxaca-Blinder em qualquer ponto da
  distribuição de renda (não só na média), respondendo "o hiato residual é maior no topo
  ou na base da distribuição?".
- Validadas com dado sintético (grupo com composição de escolaridade diferente E retorno
  diferente à escolaridade, gerado com parâmetros conhecidos) antes de rodar nos dados
  reais — `decomposicao_oaxaca_blinder` recuperou o hiato bruto exatamente e a proporção
  explicada/não-explicada bateu com a conta manual; `rif_quantil` passou no teste de
  consistência interna (média da RIF ≈ o próprio quantil).
- Limitação documentada: os pesos amostrais entram como pesos analíticos do WLS
  (statsmodels), não como pesos de desenho amostral complexo (réplicas/bootstrap de
  desenho) — os erros-padrão tendem a ser um pouco otimistas, mas a direção/magnitude do
  coeficiente não muda.

### Resultado: decomposição de Oaxaca-Blinder (com teste de significância)

Mesmo universo da decomposição por padronização direta (últimos 8 trimestres, ocupados
com ocupação identificada, Branca vs. Negra):

| Controles | Explicada | Não-explicada | Coef. residual (log) | p-valor |
|---|---|---|---|---|
| + faixa etária | 1,6% | 98,4% | 0,422 | < 0,001 |
| + faixa etária + escolaridade | 44,8% | 55,2% | 0,235 | < 0,001 |
| + faixa etária + escolaridade + ocupação | 52,6% | 47,4% | 0,202 | < 0,001 |

O coeficiente residual final (0,202 em log-pontos) converte pra um hiato de **~22,4%**
(e^0,202 − 1) — **muito próximo dos 24,3% da padronização direta** feita na rodada
anterior. Dois métodos diferentes (padronização direta vs. regressão) convergindo pro mesmo
número é uma checagem de robustez útil: o achado "sobra ~1/4 do hiato mesmo controlando
idade/escolaridade/ocupação" não é artefato de um método específico, e agora tem teste de
significância formal (p < 0,001) confirmando que o resíduo não é zero.

**RIF por quantil** (mesmos controles completos, Branca vs. Negra):

| Ponto da distribuição | Não-explicada | Hiato residual (convertido) |
|---|---|---|
| P10 (base) | 58,2% | ~30,6% |
| P50 (mediana) | 45,5% | ~14,9% |
| P90 (topo) | 41,1% | ~36,1% |

Achado novo: o hiato residual tem formato em **U** — menor na mediana (~15%), mas maior
tanto na base (P10, ~31% — indício de "piso pegajoso": mesmo no topo da pirâmide de baixa
renda, negros ganham menos que brancos comparáveis) quanto no topo (P90, ~36% — "teto de
vidro", consistente com o achado já visto de que o hiato se abre dramaticamente no Superior
completo). O grosso do hiato NÃO está concentrado num único ponto da distribuição.

### Resultado: hiato por Região

`gerar_hiato_regional` aplica o mesmo teste de Welch trimestre a trimestre, quebrado pelas
5 Grandes Regiões (`data/processed/hiato_regional.parquet`, 290 linhas = 58 trimestres × 5
regiões). Ver `docs/img/hiato_racial_por_regiao.png` pra leitura visual.

### Resultado: índice de segregação ocupacional (Duncan)

`gerar_indice_segregacao_ocupacional` calcula o índice de dissimilaridade de Duncan (1955)
entre a distribuição de Branca e Negra nas 11 categorias de `grupamento_ocupacional`,
trimestre a trimestre. No trimestre mais recente: **17,0%** — ou seja, 17% de um dos grupos
precisaria trocar de categoria ocupacional pra igualar a distribuição do outro. Isso mede
segregação ocupacional EM SI (quem trabalha em quê), diferente da decomposição do hiato
(que mede o EFEITO da ocupação na renda) — os dois se complementam.

### Resultado: quebra estrutural nos 3 eventos já mapeados

`gerar_quebra_estrutural` testa (OLS com dummy pós-evento + interação com tendência,
equivalente a um teste de Chow simplificado — uma quebra conhecida a priori, não busca por
múltiplas quebras como Bai-Perron) se a trajetória do hiato % muda de patamar/inclinação:

| Evento | Mudança de patamar | Mudança de inclinação | Significativo? |
|---|---|---|---|
| Reforma trabalhista (2017 T3) | +9,45 p.p. (p<0,001) | −0,43 p.p./trim. (p<0,001) | Sim |
| Reforma da previdência (2019 T4) | +8,87 p.p. (p=0,004) | −0,37 p.p./trim. (p<0,001) | Sim |
| Recessão (2015 T1) | +5,58 p.p. (p=0,004) | −0,08 p.p./trim. (p=0,74, NS) | Sim (só no patamar) |

Interpretação cuidadosa: o teste aponta mudança estatisticamente detectável na trajetória
ao redor dos 3 eventos, mas é uma correlação temporal simples (regressão numa série
agregada de 58 pontos), não inferência causal — outros fatores concorrentes no mesmo
período (ex.: a própria pandemia, perto da reforma da previdência) não são controlados
aqui. Ver `docs/img/hiato_quebra_estrutural.png`.

### Novas variáveis da PNAD (já extraídas, sem necessidade de reextração)

Quatro novos `data/processed/*.parquet`, todos por raça × gênero × faixa etária (Brasil +
geografias, exceto alfabetização que é Brasil apenas):

- **`informalidade.parquet`**: % com carteira assinada (VD4009, entre empregados) e % que
  contribui para previdência (VD4012, entre todos os ocupados). **Bug real encontrado e
  corrigido**: `VD4009` tem 10 categorias e vem ZERO-PADDED (`'01'`..`'10'`) no layout do
  IBGE — o código inicial usava `'1'`,`'2'` sem padding, o que fazia `pct_com_carteira` sair
  inteiramente NULO sem nenhum erro (`CASE` sem match = NULL, silencioso). Só percebido ao
  conferir a distribuição bruta dos valores (`value_counts()`) em vez de confiar que "rodou
  sem erro" = "está certo" — mais uma vez, o padrão de bug deste projeto (ver Etapa 3 e o bug
  do erro padrão): decodificação de código categórico do layout do IBGE que não é o que se
  assume à primeira vista.
- **`horas_trabalhadas.parquet`**: horas semanais habituais (VD4031) e uma renda-por-hora
  aproximada — testa se o hiato de renda reflete jornada diferente ou remuneração por hora
  menor. Resultado (2026 T2): jornada é parecida entre os grupos (38,8h Branca vs. 37,7h
  Negra vs. 36,7h Indígena), mas o hiato na renda POR HORA (~65%) é quase idêntico ao hiato
  mensal (67%) — não é sobre jornada, é remuneração por hora mesmo.
- **`alfabetizacao.parquet`**: % alfabetizado (V3001), mais relevante em 60+ anos —
  complementa `nivel_instrucao` (que só mostra o nível JÁ concluído). **Frequência escolar
  (V3014) foi DESCARTADA desta rodada**: checando a cobertura bruta antes de publicar
  qualquer número (mesmo hábito de validação), a % de população 14-17 anos com V3014
  não-nulo é de só ~6-8% em vários trimestres (2018 a 2026) — bem menor que o ~95% de V3001
  ou os ~20% que uma rotação padrão de painel (1 de 5 grupos por trimestre) explicaria. Não
  conseguimos confirmar dentro do orçamento desta rodada se essa subamostra pequena é
  aleatória (estimativa ainda válida, só com IC mais largo) ou enviesada por algum critério
  de coleta que não identificamos — preferimos não publicar em vez de arriscar um número
  errado sobre evasão escolar.
- **`desalento_subutilizacao.parquet`**: % em força de trabalho potencial (VD4003) e % de
  desalento (VD4005, desistiu de procurar emprego) entre quem está fora da força de
  trabalho — vai além da taxa de desocupação simples já existente em `ocupacao.parquet`.

Ver `docs/ANALISE_FASE1.md` pra leitura de cada gráfico com os números do trimestre mais
recente, e `docs/LIMITACOES_E_METODOLOGIA.md` pra decodificação completa das variáveis.

---

## Geração e perfil do topo 10% ✅ (2026-09-05)

Duas perguntas do usuário sobre limitações metodológicas dos gráficos por faixa etária e
sobre decompor quem está no topo da distribuição de renda:

1. **"Faixa etária" não acompanha as mesmas pessoas** — a PNAD Contínua é um corte
   transversal repetido, não um painel de décadas: "pessoas de 14-17 anos" em 2012 e em 2026
   são pessoas DIFERENTES chegando nessa idade. Resolvido com **geração** — coorte de
   nascimento sintética (`ano_nascimento_aprox = ano - V2009`, método de Deaton 1985),
   adicionada como coluna em `CRIAR_BASE`: Baby Boomer (1946-1964), Geração X (1965-1980),
   Millennial (1981-1996), Geração Z (1997-2012) têm amostra ao longo de toda a janela
   2012-2026 (Geração Silenciosa e Alpha ficam de fora, amostra residual/inexistente).
   - `gerar_hiato_por_geracao`: hiato Branca-Negra (Welch) DENTRO de cada geração, ao longo
     do tempo — mantém a coorte fixa em vez de misturar coortes diferentes.
   - Achado: o hiato varia MUITO por geração (30% na Geração Z, ~90-100% no Baby Boomer) e o
     do Baby Boomer especificamente CRESCE conforme a coorte envelhece dentro da janela —
     provável efeito de seleção (quem continua trabalhando até os 60-80 anos não é uma
     amostra aleatória, e essa seleção pode ser diferente por raça).
   - `gerar_renda_por_geracao`: snapshot de renda por geração x raça na idade atual de cada
     geração.

2. **Decomposição histórica do topo 10%** — "onde estão os 10% que mais ganham entre os
   negros em comparação com os brancos" (quebrado por gênero, faixa etária, geração,
   escolaridade). Implementado como `gerar_perfil_topo10_racial`: calcula o limiar (P90) de
   renda DENTRO de cada raça separadamente (Branca e Negra — não um corte único pro Brasil,
   que seria quase todo Branca dado o hiato; Indígena fica de fora, amostra insuficiente pra
   um P90 confiável por trimestre) e compõe o perfil demográfico de quem está acima desse
   limiar, trimestre a trimestre desde 2012.
   - Achado mais forte: o topo 10% dos negros ficou muito mais escolarizado ao longo da
     série — de 38% com Superior completo em 2012 para ~58% hoje — mas ainda fica atrás do
     topo dos brancos (~83%). A composição geracional do topo também diverge um pouco: o
     topo dos negros pende mais para Millennial/Geração Z, o dos brancos para Baby
     Boomer/Geração X — coerente com a convergência de escolaridade sendo mais forte nas
     gerações mais novas.
   - **Limitação encontrada e documentada, não "corrigida"**: renda autodeclarada tem forte
     concentração em valores redondos (heaping — R$1.000, R$2.000, R$5.000, R$10.000 etc.,
     checado direto no parquet bruto). Quando o P90 calculado cai bem em cima de um desses
     valores populosos, o filtro `>= limiar` inclui todo mundo empatado ali, capturando um
     pouco mais que 10% de fato (checado manualmente no trimestre mais recente: ~11,5% de
     Branca, ~12,8% de Negra). Em vez de tentar uma correção de desempate mais sofisticada
     (fora de escopo pra esta rodada), a função grava `pct_populacao_capturada` como
     diagnóstico transparente — quem for usar o dado sabe exatamente o quão perto de "10%
     exato" cada linha está.

Ambas as novas funções (`gerar_hiato_por_geracao`, `gerar_renda_por_geracao`,
`gerar_perfil_topo10_racial`) seguem os mesmos padrões já estabelecidos (Welch via
microdados quando aplicável, universo de ocupados com renda > 0, amostra mínima de 100
antes de calcular um quantil). 6 gráficos novos, seção nova na apresentação.

### Correção: faltava a decomposição dos 4 quartis (2026-09-05)

O usuário pediu originalmente "decomposição histórica dos 4 quartis das populações",
usando o topo 10% só como EXEMPLO de uma coisa que queria ver. A entrega acima cobriu só o
exemplo (P90/topo 10%), não o pedido completo (P25/P50/P75, os 4 quartis) — usuário
perguntou de volta se eu tinha entendido que ele queria a quebra dentro de cada raça pra
toda a distribuição, não só o topo. Corrigido: `gerar_perfil_quartis_racial` generaliza
`gerar_perfil_topo10_racial` pros 4 quartis (Q1-Q4, limiares P25/P50/P75 calculados DENTRO
de cada raça, mesmas 4 dimensões de composição, mesma ressalva de heaping documentada
acima). O topo 10% continua publicado à parte — é um recorte mais estreito (P90) e
complementar, não foi substituído.

- Gráficos novos: 4 painéis "pequenos múltiplos" (um por quartil, Q1 a Q4 lado a lado),
  2 em série temporal (gênero, escolaridade) e 2 em snapshot/barras (faixa etária, geração)
  — generaliza os 4 gráficos de topo 10% já existentes.
- Achado mais forte: o hiato educacional (% Superior completo) ENTRE Negra e Branca cresce
  conforme sobe o quartil — de ~6 p.p. no Q1 pra ~32 p.p. no Q4 — confirmando com o painel
  completo o padrão já visto isoladamente no topo 10%.

---

## Sugestões de análise validadas antes de executar (2026-09-05)

Usuário pediu explicitamente "sugere mais algum tipo de análise... me traga antes de
executar". Antes de implementar, mapeei o que já temos extraído mas nunca usado, e
apresentei um menu (AskUserQuestion) separado em "fáceis" (dado já pronto, função já
existente ou barata de fazer) e "custosas" (mais esforço/risco). Usuário escolheu as 4
fáceis inteiras + 1 das custosas (Theil), não escolheu: hiato Capital/Interior nem o painel
rotativo real de curto prazo (ficam registrados abaixo como candidatos futuros).

- **Gini por raça** (`gerar_gini_por_raca`): `pnadc_core.gini_ponderado_por_grupo` já
  existia, portada do notebook original, mas nunca tinha sido chamada em nenhuma rodada
  anterior. Achado que exige leitura cuidadosa: Branca tem Gini mais alto (mais
  desigualdade DENTRO do grupo) que Negra — não é "a população negra está melhor", é que a
  distribuição de renda dela é mais comprimida perto da base.
- **Índice de Theil, decomposição entre/dentro** (`gerar_theil_racial`): nova função
  `pnadc_core.decomposicao_theil_entre_dentro`, validada com 3 casos sintéticos antes de
  rodar nos dados reais (grupos idênticos → theil_entre≈0; médias diferentes com variância
  interna zero → theil_entre=100%; grupo único → bate exatamente com `theil_t` direto).
  Achado: só ~7% da desigualdade total de renda do Brasil vem de diferença ENTRE raças — 93%
  é DENTRO de cada raça. Não diminui o hiato racial, mostra que a desigualdade brasileira é
  multifatorial.
- **Setor de atividade econômica** (VD4010, `setor_atividade` em `CRIAR_BASE`): variável já
  extraída desde o início (junto com VD4011), nunca decodificada nem usada. **Bug de
  decodificação encontrado e corrigido ANTES de usar** (mesmo padrão de VD4009/VD4011): 12
  categorias, zero-padded (`'01'`..`'12'`) — checado direto no parquet bruto antes de
  escrever o `CASE`. `gerar_segregacao_setorial` aplica o mesmo índice de Duncan já usado
  pra ocupação, agora por setor — resultado: segregação setorial (~10%) é menor que
  ocupacional (~17%), as raças se distribuem mais parecido entre setores do que entre cargos
  dentro deles.
- **Hiato no setor Público vs. Privado** (`setor_trabalho`, derivado de VD4009;
  `gerar_hiato_setor_publico_privado`): confirma a hipótese da literatura — hiato menor no
  Público (~45-50%, tabela salarial padronizada) que no Privado (~58-68%).
- **Sobre-qualificação/"brain waste"** (`gerar_sobrequalificacao`): % de quem tem Superior
  completo e está em "Ocupações elementares" (ISCO grupo 9, proxy padrão de mismatch
  credencial-ocupação). Achado: taxa de Negra é quase o dobro da de Branca ao longo de quase
  toda a série — mesmo diploma, resultado profissional diferente.

**Candidatos registrados pra uma rodada futura, se fizer sentido** (não escolhidos desta
vez): painel rotativo REAL de curto prazo (usar UPA/V1008/V2003/painel — já extraídos — pra
medir taxa de transição desemprego→emprego por raça usando o vínculo real entre entrevistas,
não mais coorte sintética); hiato Capital vs. Interior (extensão barata do hiato regional).

5 gráficos novos nesta rodada (68 no total, era 63), apresentação com 88 slides (era 82), 25
datasets (era 20).

---

## 🏁 Fase 1 concluída (2026-09-04, expandida em 2026-09-05)

Todas as 7 etapas (0-6) fechadas no mesmo dia, incl. quatro rodadas de expansão a pedido (a
segunda com teste de significância formal via Oaxaca-Blinder, hiato regional, segregação
ocupacional, quebra estrutural e 4 variáveis novas; a terceira com geração, perfil do topo
10% e a decomposição completa dos 4 quartis; a quarta com Gini/Theil por raça, setor
econômico, setor público/privado e sobre-qualificação — ver seções acima). Entregáveis:
`src/ingestion/{extrator_pnadc,baixar_deflator}.py`,
`src/processing/{agregacoes_pnadc,graficos_fase1,apresentacao_fase1}.py`,
`src/utils/pnadc_core.py`, 25 datasets em `data/processed/*.parquet`,
`docs/{LIMITACOES_E_METODOLOGIA,ANALISE_FASE1}.md`, 68 gráficos em `docs/img/` (galeria
completa em `docs/ANALISE_FASE1.md`, destaques no README), apresentação
`docs/Datahub_Racial_Brasil_Fase1.pptx` (88 slides). Próximo passo: Fase 2 (Censo
Demográfico) — ainda não detalhada.

---

## Outras fontes de dados (além de PNAD/Censo/DataSUS já previstos)

Você pediu pra eu incluir outras ideias de fonte, não só as já citadas. Lista de módulos
candidatos — independentes entre si, para intercalar com as Fases 2-3 conforme o interesse,
sem ordem fixa:

| Módulo | Fonte | Formato de acesso | Esforço aprox. | Ângulo |
|---|---|---|---|---|
| Desigualdades raciais (IBGE) | Publicação "Desigualdades Sociais por Cor ou Raça no Brasil" (IBGE, biênio) | Tabelas já agregadas (xls/pdf) | Baixo (1-2h) | Validação cruzada rápida dos achados da PNAD; bom "quick win" antes do Censo |
| Mercado formal (RAIS/CAGED) | Portal PDET (Ministério do Trabalho), FTP público — **não** Base dos Dados/BigQuery | Microdados administrativos | Médio-alto (similar à PNAD) | Salário e admissão/desligamento por raça no emprego formal (complementa a visão domiciliar da PNAD); raça/cor só é confiável nos anos mais recentes |
| Violência (Atlas da Violência) | IPEA + Fórum Brasileiro de Segurança Pública | CSV agregado, já pronto | Baixo (2-3h) | Homicídios por raça/gênero — ângulo de alto impacto, pouco esforço |
| Encarceramento (INFOPEN/Depen) | Depen, dados abertos | CSV/planilhas agregadas | Baixo-médio | Superpopulação carcerária por raça |
| Educação (INEP) | Censo Escolar + microdados do ENEM | Microdados grandes | Alto (similar à PNAD) | Desempenho e acesso educacional por raça/cor |
| Representação política (TSE) | Portal de dados abertos do TSE | CSV de candidaturas | Baixo-médio | Candidaturas/eleitos por raça (autodeclaração obrigatória desde 2014) |
| Saúde percebida (PNS) | IBGE/DataSUS, edições 2013/2019/2024 | Microdados (survey, como a PNAD) | Médio | Complementa os registros administrativos do DataSUS (Fase 3) com dados autorreportados |

Nenhum desses substitui as Fases 2 (Censo) e 3 (DataSUS) já previstas no escopo original —
são adições ao roadmap, a priorizar conforme o interesse depois que a Fase 1 fechar.

### Ferramentas/fontes de referência para cruzar dados (anotado a pedido, 2026-09-04)

Não avaliadas em profundidade ainda — só registradas aqui como ponto de partida pra quando
formos expandir a análise (Fase 2+ ou aprofundamento da Fase 1):

- **IPUMS** (ipums.org, incl. IPUMS International) — microdados de censos e pesquisas
  domiciliares harmonizados entre países/anos. Útil se algum dia quisermos comparar o Brasil
  com outros países ou harmonizar variáveis entre Censo e PNAD de anos diferentes sem
  reinventar o mapeamento de categorias.
- **`lodown`** (pacote R, projeto asdfree.com de Anthony Damico) — toolkit padronizado pra
  baixar e analisar dados de pesquisas complexas (survey data) de vários países, incluindo
  pesquisas domiciliares brasileiras. Referência de metodologia (desenho amostral, pesos)
  mesmo se a gente continuar em Python/DuckDB.
- **`microdadosBrasil`** (pacote R) — leitura de microdados de pesquisas brasileiras (PNAD,
  Censo, POF etc.). Pode servir de checagem cruzada da nossa própria extração (comparar
  contagens/médias com o que esse pacote produz pros mesmos trimestres).
- **Data Zoom (PUC-Rio, Departamento de Economia)** — rotinas Stata/R pra processar
  microdados de pesquisas domiciliares brasileiras (PNAD, PNAD Contínua, POF, Censo). Muito
  citado em trabalhos aplicados de economia brasileira — bom lugar pra checar convenções
  metodológicas (ex.: deflação de renda, tratamento de painel rotativo) contra o que fizemos
  aqui.

Uso pretendido: validação cruzada de metodologia, não substituição do pipeline atual
(FTP do IBGE direto + DuckDB já funciona e está validado).

---

## Fase 2 — Censo Demográfico (não detalhada ainda)

Moradia, condições domiciliares e, principalmente, **recorte municipal** — o Censo tem
identificação de município (a PNAD Contínua pública não tem, ver risco abaixo), o que
resolve a limitação do ABC Paulista da Fase 1. Também tem quesito dedicado para população
indígena (incl. terras indígenas), mais robusto que a PNAD Contínua para esse recorte.
Detalhar etapas quando a Fase 1 fechar.

## Fase 3 — Saúde (DataSUS/SIM/SINASC/PNS) (não detalhada ainda)

Natalidade, mortalidade (incl. materna/infantil por raça/cor) e acesso a serviços de saúde.
Detalhar etapas quando a Fase 2 fechar.

## Fase 4 — Dashboard (Observable Framework) (não detalhada ainda)

Publicação pública das análises consolidadas. Desacoplado do pipeline de dados — pode trocar
de ferramenta sem impacto retroativo.

## Fase 5 — Conteúdo (Instagram/TikTok) (não detalhada ainda)

Prioridade baixa. Recorte de achados do dashboard em formato visual para redes sociais.

---

## Riscos e pontos de atenção

- **Município de São Paulo é identificável na PNAD Contínua (UF='35' + `Capital` não-nula),
  mas os municípios do ABC Paulista individualmente NÃO são** — a PNAD Contínua pública só
  identifica Região Metropolitana/RIDE (`RM_RIDE`) por confidencialidade, sem código de
  município. O mais granular que dá pra fazer na Fase 1 é "RM São Paulo, não-capital"
  (`RM_RIDE` não-nula E `Capital` nula — mistura ABC com outras cidades da Grande São Paulo).
  Um recorte por município do ABC específico só é possível a partir do Censo Demográfico
  (Fase 2). **Nota de validação (2026-09-04)**: `Capital` não é o flag binário 1/2 que o
  `pnadc_core.py` herdado do Colab documentava — na prática ela traz o código da UF quando o
  registro é do município da capital, e fica em branco caso contrário (mesma convenção vale
  para `RM_RIDE`). Corrigido em `preparar_niveis_geograficos()`; o resultado final
  (Capital/Interior por UF) é o mesmo, só a lógica interna que estava errada — testado contra
  2026 T2 e bate: 8.645 registros de SP capital vs. 31.410 do interior de SP.
- **Amostra de população Indígena na PNAD Contínua é pequena e de alta variância** —
  autodeclaração indígena é uma fração pequena da amostra domiciliar nacional; estimativas
  trimestrais isoladas por UF podem ter intervalo de confiança muito largo. Pode ser
  necessário agrupar vários trimestres para ter significância, e o Censo (Fase 2, que tem
  quesito e cobertura dedicados a terras indígenas) deve ser tratado como fonte mais robusta
  para esse recorte especificamente.
- **Mudanças metodológicas do IBGE**: a PNAD Contínua passou por recalibração de pesos
  amostrais após o Censo 2022 (projeções populacionais revisadas). Documentar em `docs/`
  assim que identificado onde a série quebra.
- **Mudança de layout do arquivo de microdados**: o IBGE atualiza o layout de posições fixas
  periodicamente. O extrator já baixa o dicionário/layout mais recente a cada execução (não
  fixa um único layout para toda a série) — mas se um nome de variável mudar de um ano para
  outro, o script vai reportar isso no aviso de "variáveis não encontradas" e precisa de
  ajuste manual. **Investigado na Etapa 1 (2026-09-04)**: `VD4011A` nunca existiu em nenhum
  trimestre da série, nem nos herdados do Colab — não é uma quebra nova de 2026, é um nome de
  variável errado desde o início do projeto anterior. O nome correto no layout atual é
  `VD4011` (sem "A") — "Grupamento ocupacional do trabalho principal". Não afeta nenhum
  cruzamento obrigatório do MVP (renda, escolaridade, condição de ocupação usam outras
  variáveis, todas presentes). Corrigido em `extrator_pnadc.py` para `VD4011` daqui pra
  frente; os 58 trimestres já extraídos ficam sem essa coluna específica — não justifica
  reprocessar tudo por uma variável não-obrigatória.

### Resultado da validação (Etapa 1, 2026-09-04)

- **Contagens**: as 58 partições ano/trimestre com dado real (2012 T1 → 2026 T2) batem
  exatamente com `_resumo_extracao.csv`, sem nenhuma divergência. Total: **29.926.646**
  registros pessoa-trimestre na série completa.
- **Schema**: 40 das 41 variáveis desejadas presentes em todos os trimestres testados (só
  falta `VD4011A`/`VD4011`, ver acima — não bloqueia o MVP).
- **Distribuição racial** (V2010, 2026 T2): Branca 39,2% · Parda 50,2% · Preta 9,6% ·
  Indígena 0,6% · Amarela 0,4% · Ignorado ~0% — condizente com o esperado; confirma na
  prática o risco já documentado de amostra pequena para Indígena (~2.900 registros em 521
  mil no trimestre, antes de qualquer segmentação por UF/gênero/idade).
- **Peso amostral** (`V1028`): zero registros nulos ou ≤0 no trimestre mais recente.

### Bug crítico encontrado e corrigido (Etapa 3, 2026-09-04)

Testando `aplicar_recorte1`/`aplicar_recorte2`/`preparar_niveis_geograficos` contra dados
reais (não só `py_compile`), todos os recortes vinham 100% `NaN`. Causa: `V2010`, `V2007`,
`UF`, `Capital` e `RM_RIDE` são colunas de **texto** no layout oficial do IBGE (formato
`$N.`, não numérico) — o `extrator_pnadc.py` já lê corretamente como string, mas os
dicionários de mapeamento do `pnadc_core.py` herdado do Colab usavam chaves **inteiras**
(`{1: 'Branca', ...}`), que nunca batiam com os valores string (`'1'`, `'2'`...). Corrigido:
`CODIGOS_RACA`, `CODIGOS_SEXO` e `REGIAO_POR_UF` agora usam chaves string. De quebra, achei e
corrigi também um typo de concordância (`'Mulheres Pardos'` → `'Mulheres Pardas'` em
`ROTULO_GRUPO_RECORTE2`, que também gerava `NaN` silencioso) e a lógica de `Capital`/`RM_RIDE`
(ver nota nos riscos, acima). Retestado após a correção: os três recortes agora reproduzem
exatamente a distribuição bruta de `V2010` (nenhuma linha perdida além do esperado
Amarela+Ignorado, que ficam fora do recorte central por design).

**Lição**: código herdado de um projeto anterior (mesmo que só compile e "pareça" certo)
precisa ser testado contra os dados reais antes de virar a base de qualquer agregação — os
três bugs acima eram completamente silenciosos (sem erro, sem warning, só `NaN`).

### Etapa 4 — Agregações finais (2026-09-04)

Script: `src/processing/agregacoes_pnadc.py`. Cruza Raça/Cor (6 categorias brutas do IBGE,
`raca_cor` — Preta+Parda não são pré-somadas em "Negra" no dataset base, ver docstring do
script) × Gênero × Faixa etária × 5 níveis geográficos (Brasil/Região/UF/SP capital-interior/
RM SP capital-vs-não-capital) × ano/trimestre. Saída: `data/processed/renda.parquet`
(105.969 linhas), `escolaridade.parquet` (544.540 linhas), `ocupacao.parquet` (105.969
linhas) — ~13 MB total, versionados no git.

**Bug de performance encontrado e corrigido**: a primeira versão do script montava os 5
níveis geográficos como um único `UNION ALL` gigante por tema. Isolado, cada bloco levava
3-8s — mas a query unificada travava (testado por 15+ min sem terminar, em 3 tentativas
diferentes, incluindo com a barra de progresso do DuckDB desligada). Causa não totalmente
diagnosticada (possível pathologia do otimizador do DuckDB com múltiplos `UNION ALL` +
`FILTER` na versão instalada), mas contornada: cada nível geográfico agora roda como uma
query separada (`con.execute(...).df()`), concatenadas em pandas com `pd.concat`. Resultado:
pipeline completo (base + 3 temas × 5 níveis = 15 queries) roda em bem menos de 3 minutos.

**Checagem substantiva dos resultados** (Brasil, 2026 T2, nominal): renda habitual média
Branca R\$4.506 vs. Preta R\$2.600 / Parda R\$2.708 (~67% de diferença) · taxa de
desocupação Branca 4,2% vs. Preta 6,9% / Parda 6,1% · superior completo Branca 26,4% vs.
Preta 11,9% / Parda 12,2%. Todos os hiatos batem em direção e magnitude com estatísticas
públicas conhecidas do IBGE — não é prova de correção total do pipeline, mas é um forte
sinal de que os números fazem sentido, não só que o código rodou sem erro.

### Deflator oficial do IBGE (2026-09-04)

Você pediu pra buscar um deflator oficial, priorizando o próprio IBGE antes de outras
fontes. Achado: o IBGE publica, na MESMA pasta de documentação dos microdados (não em
outro lugar), um deflator pronto para a PNAD Contínua — `Documentacao/Deflatores.zip`,
atualizado junto com cada nova divulgação trimestral (a versão baixada em 2026-09-04 já
veio com o T2/2026, calibrado nesse mesmo dia). Não foi preciso recorrer ao IPEA.

- **Script**: `src/ingestion/baixar_deflator.py` → `data/processed/deflator_ibge.parquet`
  (1.566 linhas = 27 UFs × 4 trimestres/ano × ~14,5 anos).
- **Granularidade**: por UF e trimestre, com deflator separado para renda "Habitual" e
  "Efetiva" (bate exatamente com `VD4019`/`VD4020`). A planilha do IBGE também tem 8
  janelas móveis de mês por ano (p.ex. `02-03-04`) usadas pela PNAD Contínua Mensal — só
  as 4 que coincidem com os trimestres fixos (`01-02-03`, `04-05-06`, `07-08-09`,
  `10-11-12`) foram mantidas, o resto é descartado por não se aplicar aqui.
- **Direção da conversão — ponto crítico**: o deflator do IBGE é o fator que se
  **multiplica** pelo valor nominal (não divide) para trazê-lo a preços do trimestre de
  referência mais recente (hoje, 2026 T2, onde o deflator é exatamente 1.0). Isso é o
  oposto da função `aplicar_deflator` herdada em `pnadc_core.py`, que fazia `/` e era
  desenhada pra outra fonte (IPEA) — não foi reaproveitada; `agregacoes_pnadc.py` já
  aplica a multiplicação direto no `LEFT JOIN` com o deflator, dentro da tabela `base`.
- **Validado**: no trimestre de referência (2026 T2), nominal e real batem exatamente
  (checado linha a linha); em 2012 T1, real ≈ 2,2× nominal (consistente com ~14 anos de
  inflação acumulada). Comparação histórica de exemplo, em R$ reais (preços de 2026 T2):
  renda habitual Branca foi de R\$3.768 (2012 T1) para R\$4.506 (2026 T2); Negra
  (Preta+Parda) foi de R\$2.077 para R\$2.687 — ambas cresceram em termos reais, e o
  hiato racial (razão Branca/Negra) estreitou de 1,81× para 1,68× no período. Achado
  plausível e alinhado com a literatura sobre desigualdade racial no Brasil nesse
  intervalo — não é a análise final da Fase 1, só uma checagem de sanidade do pipeline.
- `data/processed/renda.parquet` agora tem `renda_{habitual,efetiva}_{nominal,real}_media`
  — use as colunas `_real` para qualquer comparação entre trimestres diferentes.

- **Instabilidade do FTP do IBGE**: `extrator_pnadc.py` já tem retry com backoff e é
  idempotente por trimestre (marcador `_SUCCESS`), então pode ser interrompido e retomado sem
  perder o que já foi processado.
- **Tamanho dos dados**: a base herdada já soma ~500 MB (56 trimestres); cada trimestre novo
  soma mais ~9 MB. Fica em `data/raw/` (fora do git e do controle de versão).
- **Categorização de raça/cor**: Amarela sempre explicitada nas tabelas, nunca descartada
  silenciosamente — mesmo quando o recorte central da análise é Branca/Negra/Indígena.
- ~~**Renda nominal, sem deflator ainda**~~ — ✅ **resolvido em 2026-09-04**, ver seção
  "Deflator oficial do IBGE" abaixo. `data/processed/renda.parquet` agora traz colunas
  `_nominal` (R$ correntes do trimestre) e `_real` (deflacionadas, a preços do trimestre de
  referência mais recente).
- **Quebras estruturais conhecidas a anotar quando aparecerem nos dados**: recessão
  2015-2016, pandemia de COVID-19 (2020-2021, incl. mudança temporária de coleta por
  telefone — visível na queda de registros por trimestre no `_resumo_extracao.csv` herdado),
  reforma trabalhista (2017) e da previdência (2019).
