# Análise Fase 1 — PNAD Contínua (2012-2026)

Galeria completa dos gráficos exploratórios da Fase 1 — todas as interseções entre raça,
gênero, faixa etária e escolaridade, para renda habitual real (deflator oficial do IBGE, ver
[PLANO.md](PLANO.md)), Brasil, salvo indicação contrária. Gerados por
`src/processing/graficos_fase1.py` a partir de
`data/processed/{renda,escolaridade,renda_por_escolaridade,renda_completa,hiato_racial,decomposicao_hiato_ocupacional}.parquet`.
Também disponível como apresentação: [Datahub_Racial_Brasil_Fase1.pptx](Datahub_Racial_Brasil_Fase1.pptx).

44 gráficos ao todo. Índice:

- [Raça](#raça)
- [Hiato Branca vs. Negra — série histórica](#hiato-branca-vs-negra--série-histórica)
- [É ocupação, ou é cor da pele?](#é-ocupação-ou-é-cor-da-pele)
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
- Estes são gráficos **exploratórios** — só o hiato Branca-Negra (seção "Hiato" acima) passou
  por teste de significância formal; as demais comparações (por faixa etária, escolaridade,
  a decomposição por ocupação, etc.) ainda não — são comparações de médias ponderadas, não
  testes estatísticos completos.
- **Bug estatístico real encontrado e corrigido nesta rodada**: a função
  `erro_padrao_media_ponderada` em `pnadc_core.py` (herdada do projeto anterior) calculava um
  erro padrão inflado por um fator de ~√n em relação ao valor correto — bug puramente de
  código, não de dados; documentado em detalhe no `docs/PLANO.md`.
