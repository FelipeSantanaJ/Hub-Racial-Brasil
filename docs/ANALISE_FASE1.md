# Análise Fase 1 — PNAD Contínua (2012-2026)

Galeria completa dos gráficos exploratórios da Fase 1 — todas as interseções entre raça,
gênero, faixa etária e escolaridade, para renda habitual real (deflator oficial do IBGE, ver
[PLANO.md](PLANO.md)), Brasil, salvo indicação contrária. Gerados por
`src/processing/graficos_fase1.py` a partir dos datasets em `data/processed/*.parquet`.
Também disponível como apresentação: [Datahub_Racial_Brasil_Fase1.pptx](Datahub_Racial_Brasil_Fase1.pptx).

53 gráficos ao todo. Índice:

- [Raça](#raça)
- [Hiato Branca vs. Negra — série histórica](#hiato-branca-vs-negra--série-histórica)
- [É ocupação, ou é cor da pele?](#é-ocupação-ou-é-cor-da-pele)
- [Aprofundamentos: região, segregação e quebras estruturais](#aprofundamentos-região-segregação-e-quebras-estruturais)
- [Aprofundamentos: novas variáveis da PNAD](#aprofundamentos-novas-variáveis-da-pnad)
- [Raça × Gênero](#raça--gênero)
- [Preta × Parda × Gênero](#preta--parda--gênero)
- [Raça × Faixa etária](#raça--faixa-etária)
- [Preta × Parda × Faixa etária](#preta--parda--faixa-etária)
- [Raça × Escolaridade](#raça--escolaridade)
- [Preta × Parda × Escolaridade](#preta--parda--escolaridade)
- [Raça × Gênero × Escolaridade](#raça--gênero--escolaridade)
- [Raça × Gênero × Faixa etária](#raça--gênero--faixa-etária)
- [Escolaridade × Raça × Gênero](#escolaridade--raça--gênero)
- [Raça × Gênero × Faixa etária × Escolaridade](#raça--gênero--faixa-etária--escolaridade)
- [Limitações a ter em mente](#limitações-a-ter-em-mente-lendo-estes-gráficos)

## Raça

![Renda por raça](img/renda_por_raca.png)

Hiato grande e persistente entre Branca e Negra/Indígena ao longo de toda a série.

![Preta vs. Parda](img/renda_preta_parda.png)

Preta e Parda **não são a mesma coisa** — mas andam muito próximas ao longo de toda a série,
com Parda ultrapassando levemente Preta nos últimos anos.

## Hiato Branca vs. Negra — série histórica

Com teste de significância estatística (Welch, IC 95%) calculado trimestre a trimestre a
partir dos microdados — ver `src/processing/agregacoes_pnadc.py::gerar_hiato_racial`.

![Hiato percentual](img/hiato_racial_percentual.png)

O hiato relativo caiu de ~76% (2012) para ~66% (2026) — **todos os 58 trimestres da série são
estatisticamente significativos a 95%** (dado o tamanho da amostra, o intervalo de confiança
é muito estreito e praticamente invisível no gráfico).

![Hiato absoluto](img/hiato_racial_absoluto.png)

Em R$, uma história diferente aparece: o hiato **disparou durante a pandemia** (pico de
~R$2.035 em 2020 T3) antes de despencar para o menor valor da série (~R$1.510 em 2021 T4) e
se recuperar até os ~R$1.912 atuais. O hiato percentual e o absoluto contam ângulos
complementares — vale olhar os dois.

## É ocupação, ou é cor da pele?

![Decomposição do hiato](img/decomposicao_hiato_ocupacional.png)

Pergunta: controlando por idade, escolaridade e ocupação, o hiato de renda negros vs.
brancos ainda existe, ou desaparece? Decompondo progressivamente (últimos 8 trimestres,
pessoas ocupadas, padronização direta — ver [PLANO.md](PLANO.md) para o método completo):

| Controle | Hiato |
|---|---|
| Nenhum (hiato bruto) | 67,0% |
| + faixa etária | 63,9% |
| + faixa etária + escolaridade | 30,3% |
| + faixa etária + escolaridade + ocupação | **24,3%** |

Idade sozinha quase não explica nada. Escolaridade explica mais da metade do hiato. Ocupação
explica uma fatia adicional — mas **mesmo comparando pessoas da mesma idade, mesma
escolaridade e mesma categoria ocupacional, sobra um hiato de ~24%** que essas três variáveis
não explicam. Não é prova direta de discriminação (outros fatores não medidos aqui — horas
trabalhadas, formalidade, região, senioridade dentro da ocupação — também podem contribuir),
mas mostra que "estar na mesma ocupação" está longe de eliminar o hiato racial de renda.

**Mesma pergunta, com teste de significância formal** — regressão (Oaxaca-Blinder):

![Decomposição de Oaxaca-Blinder](img/oaxaca_blinder_decomposicao.png)

Com os mesmos controles, o resíduo (parte "não-explicada" — mesma idade, escolaridade e
ocupação, retorno diferente) converge pra **+22%**, muito perto dos 24% da padronização
direta acima — dois métodos diferentes concordando é uma checagem de robustez importante —
e agora **com teste de significância** (p < 0,001, não é ruído amostral).

![Hiato residual por quantil](img/oaxaca_blinder_quantis.png)

O resíduo não é uniforme ao longo da distribuição de renda: menor na mediana (~15%), mas
maior tanto na base (P10, ~31% — "piso pegajoso") quanto no topo (P90, ~36% — "teto de
vidro", coerente com o hiato que se abre no Superior completo).

## Aprofundamentos: região, segregação e quebras estruturais

![Hiato por região](img/hiato_racial_por_regiao.png)

O hiato racial varia MUITO entre regiões — Sudeste tem o maior (65-85% ao longo da série),
Sul o menor (45-55%). A desigualdade regional do Brasil também aparece especificamente no
hiato racial, não é uniforme pelo país.

![Segregação ocupacional](img/segregacao_ocupacional.png)

Índice de dissimilaridade de Duncan: ~17% de um dos grupos (Branca ou Negra) precisaria
trocar de categoria ocupacional pra igualar a distribuição do outro — mede segregação
ocupacional em si, à parte do efeito dela na renda (já coberto pela decomposição acima).

![Quebra estrutural](img/hiato_quebra_estrutural.png)

Teste tipo Chow (simplificado) nos 3 eventos já mapeados como possíveis pontos de inflexão:
os 3 mostram mudança estatisticamente significativa de patamar e/ou inclinação — não é
prova de causalidade (a série tem só 58 pontos e outros eventos concorrentes, como a
pandemia perto da reforma da previdência, não são controlados), mas é evidência de
correlação temporal que vale documentar.

## Aprofundamentos: novas variáveis da PNAD

Quatro variáveis da PNAD ainda não exploradas nas rodadas anteriores — ver decodificação
completa em [LIMITACOES_E_METODOLOGIA.md](LIMITACOES_E_METODOLOGIA.md).

![Informalidade](img/informalidade_carteira_assinada.png)

% com carteira assinada (entre empregados): Branca 72%, Negra 63%, Indígena 52% (2026 T2) —
o hiato de proteção social/formalização acompanha o hiato de renda.

![Renda por hora](img/renda_por_hora.png)

Testando se o hiato de renda vem de jornada menor: **não vem** — a jornada semanal é
parecida entre os três grupos (38,8h Branca vs. 37,7h Negra vs. 36,7h Indígena, 2026 T2), e
o hiato na renda POR HORA (~65%) é quase idêntico ao hiato na renda mensal (67%). O hiato é
de remuneração por hora mesmo, não de quantas horas se trabalha.

![Alfabetização 60+](img/alfabetizacao_60mais.png)

Analfabetismo residual ainda é uma realidade nas cohorts mais velhas: 93% Branca vs. 80%
Negra vs. 72% Indígena alfabetizados entre 60+ anos (2026 T2).

![Desalento](img/desalento.png)

Entre quem está fora da força de trabalho, Negra (7,4%) e Indígena (5,9%) desistem de
procurar emprego a taxas bem maiores que Branca (3,4%, 2026 T2) — desalento vai além da taxa
de desocupação simples e também tem recorte racial.

## Raça × Gênero

![Renda por raça e gênero](img/renda_por_raca_genero.png)

O hiato de gênero **soma** ao de raça, não substitui.

<details>
<summary><strong>Um gráfico por gênero</strong></summary>

![Renda por raça — Homens](img/renda_por_raca_homens.png)
![Renda por raça — Mulheres](img/renda_por_raca_mulheres.png)

</details>

## Preta × Parda × Gênero

![Preta vs. Parda por gênero](img/renda_preta_parda_genero.png)

<details>
<summary><strong>Um gráfico por gênero</strong></summary>

![Preta vs. Parda — Homens](img/renda_preta_parda_homens.png)
![Preta vs. Parda — Mulheres](img/renda_preta_parda_mulheres.png)

</details>

## Raça × Faixa etária

![Renda por raça e faixa etária](img/renda_por_raca_faixa_etaria.png)

O hiato racial se abre justamente na faixa de maior potencial de renda (40-59 anos).

<details>
<summary><strong>Um gráfico por faixa etária</strong> (série temporal, 2012-2026)</summary>

![14-17 anos](img/renda_por_raca_faixa_14_17.png)
![18-24 anos](img/renda_por_raca_faixa_18_24.png)
![25-39 anos](img/renda_por_raca_faixa_25_39.png)
![40-59 anos](img/renda_por_raca_faixa_40_59.png)
![60+ anos](img/renda_por_raca_faixa_60mais.png)

</details>

## Preta × Parda × Faixa etária

![Preta vs. Parda por faixa etária](img/renda_preta_parda_faixa_etaria.png)

<details>
<summary><strong>Um gráfico por faixa etária</strong></summary>

![14-17 anos](img/renda_preta_parda_faixa_14_17.png)
![18-24 anos](img/renda_preta_parda_faixa_18_24.png)
![25-39 anos](img/renda_preta_parda_faixa_25_39.png)
![40-59 anos](img/renda_preta_parda_faixa_40_59.png)
![60+ anos](img/renda_preta_parda_faixa_60mais.png)

</details>

## Raça × Escolaridade

![Renda por raça e nível de instrução](img/renda_por_raca_escolaridade.png)

**O achado mais importante da Fase 1**: o hiato racial de renda não desaparece quando se
compara pessoas com o mesmo nível de instrução — ele só some ou até se inverte nos níveis
mais baixos, mas **se abre dramaticamente no Superior completo** (Branca R\$8.104 vs. Negra
R\$5.701 vs. Indígena R\$5.725, Brasil, 2026 T2).

<details>
<summary><strong>Um gráfico por nível de instrução</strong> (série temporal, 2012-2026)</summary>

![Sem instrução](img/renda_por_raca_escolaridade_sem_instrucao.png)
![Fundamental incompleto](img/renda_por_raca_escolaridade_fundamental_incompl.png)
![Fundamental completo](img/renda_por_raca_escolaridade_fundamental_compl.png)
![Médio incompleto](img/renda_por_raca_escolaridade_medio_incompl.png)
![Médio completo](img/renda_por_raca_escolaridade_medio_compl.png)
![Superior incompleto](img/renda_por_raca_escolaridade_superior_incompl.png)
![Superior completo](img/renda_por_raca_escolaridade_superior_compl.png)

</details>

## Preta × Parda × Escolaridade

![Preta vs. Parda por nível de instrução](img/renda_preta_parda_escolaridade.png)

<details>
<summary><strong>Um gráfico por nível de instrução</strong></summary>

![Sem instrução](img/renda_preta_parda_escolaridade_sem_instrucao.png)
![Fundamental incompleto](img/renda_preta_parda_escolaridade_fundamental_incompl.png)
![Fundamental completo](img/renda_preta_parda_escolaridade_fundamental_compl.png)
![Médio incompleto](img/renda_preta_parda_escolaridade_medio_incompl.png)
![Médio completo](img/renda_preta_parda_escolaridade_medio_compl.png)
![Superior incompleto](img/renda_preta_parda_escolaridade_superior_incompl.png)
![Superior completo](img/renda_preta_parda_escolaridade_superior_compl.png)

</details>

## Raça × Gênero × Escolaridade

![Renda por raça e nível de instrução — Homens](img/renda_por_raca_escolaridade_homens.png)

![Renda por raça e nível de instrução — Mulheres](img/renda_por_raca_escolaridade_mulheres.png)

O hiato no Superior completo é maior entre homens (Branca R\$10.150 vs. Negra R\$6.955, ~46%)
do que entre mulheres (Branca R\$6.572 vs. Negra R\$4.826, ~36%).

## Raça × Gênero × Faixa etária

![Renda por faixa etária, raça e gênero](img/renda_por_faixa_etaria_raca_genero.png)

Mesmo efeito de abertura em 40-59 anos, visível nos dois gêneros — mais acentuado entre homens.

## Escolaridade × Raça × Gênero

![Superior completo por raça e gênero](img/escolaridade_por_raca_genero.png)

Hiato de conclusão do ensino superior maior que 2× entre Branca (24-29%) e Negra (10-14%).
Mulheres têm taxa de conclusão maior que homens em todos os três grupos raciais.

## Raça × Gênero × Faixa etária × Escolaridade

![Heatmap completo](img/renda_completa_heatmap.png)

As quatro dimensões de uma vez: um painel por raça × gênero (6 no total), faixa etária nas
colunas, nível de instrução nas linhas, cor = renda real. O padrão "Branca mais escura que
as outras duas em quase toda célula" segura mesmo nesse nível de detalhe.

## Limitações a ter em mente lendo estes gráficos

- Indígena tem amostra pequena — séries temporais de raça isolada usam média móvel de 4
  trimestres; os cortes-instantâneo (escolaridade, faixa etária, heatmap completo) não
  suavizam, então alguns valores podem ser ruidosos nas células mais cruzadas.
- "Negra" nos gráficos = Preta + Parda somadas (ponderado); os gráficos "Preta × Parda"
  mostram as duas populações separadas para quem quiser o detalhe.
- O heatmap completo e os gráficos "por nível de instrução"/"por faixa etária" (recorte
  raça × gênero × escolaridade ou × faixa) combinam Preta+Parda em "Negra" para caber no
  espaço — quem quiser Preta e Parda separadas nesses cruzamentos mais finos precisa gerar a
  partir de `data/processed/renda_completa.parquet` (Brasil apenas).
- "Sem instrução" (nível de instrução) é uma categoria substantiva real do questionário do
  IBGE ("sem instrução e menos de 1 ano de estudo") — **não** é código de não-resposta; quem
  não respondeu/não se aplica já é excluído antes de qualquer gráfico (ver
  [LIMITACOES_E_METODOLOGIA.md](LIMITACOES_E_METODOLOGIA.md)).
- Estes são gráficos **exploratórios** — o hiato Branca-Negra nacional e por região, e a
  decomposição de Oaxaca-Blinder (incl. por quantil), passaram por teste de significância
  formal (Welch e/ou o coeficiente de regressão, respectivamente); as demais comparações
  (por faixa etária, escolaridade, informalidade, alfabetização, desalento etc.) ainda não —
  são comparações de médias ponderadas, não testes estatísticos completos.
- **Bug estatístico real encontrado e corrigido (rodada 2)**: a função
  `erro_padrao_media_ponderada` em `pnadc_core.py` (herdada do projeto anterior) calculava um
  erro padrão inflado por um fator de ~√n em relação ao valor correto — bug puramente de
  código, não de dados; documentado em detalhe no `docs/PLANO.md`.
- **Bug de decodificação real encontrado e corrigido (rodada 3)**: `VD4009` (posição na
  ocupação/carteira assinada) tem 10 categorias e vem zero-padded (`'01'`..`'10'`) no layout
  do IBGE — o código inicial usava `'1'`,`'2'` sem padding, o que fazia `pct_com_carteira`
  sair inteiramente NULO sem erro nenhum. Encontrado só ao conferir a distribuição bruta dos
  valores antes de confiar no número.
- **Frequência escolar (V3014) descartada desta rodada**: a cobertura de V3014 na população
  14-17 anos é de só ~6-8% em vários trimestres testados (2018 a 2026) — bem menor que o
  ~95% de V3001 (alfabetização) ou os ~20% que uma rotação padrão de painel explicaria.
  Não conseguimos confirmar dentro do orçamento desta rodada se essa subamostra é aleatória
  (estimativa válida, só com IC mais largo) ou enviesada — preferimos não publicar um número
  sobre evasão escolar sem entender a regra de coleta exata do IBGE pra essa variável.
