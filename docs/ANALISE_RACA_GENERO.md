# Análise Raça × Gênero — aprofundamento Branca/Negra/Indígena e Preta/Parda

Rodada dedicada a tratar os TRÊS grupos raciais (Branca, Negra, Indígena) em pé de
igualdade metodológica — não só Branca vs. Negra com Indígena como nota de rodapé — e a
abrir a diferença DENTRO da população negra (Preta vs. Parda), que até aqui só tinha o
hiato bruto de renda. Ver [PLANO.md](PLANO.md) pra decisões de escopo e
[LIMITACOES_E_METODOLOGIA.md](LIMITACOES_E_METODOLOGIA.md) pras limitações de amostra
encontradas. Sem gráficos/PPTX novos nesta rodada — só os parquets em
`data/processed/` e esta análise textual dos achados (ver "critério de pronto" no
pedido original).

## 1. Levando o toolkit pesado também pra Branca-Indígena e Preta-Parda

### Oaxaca-Blinder

- **Branca vs. Indígena** (`decomposicao_oaxaca_blinder_indigena.parquet`): controlando
  por faixa etária + escolaridade + ocupação, **44,5%** do hiato (em log-renda) é
  explicado por essas três características observáveis, **55,5%** é resíduo
  não-explicado — coeficiente residual (log-pontos) equivalente a um hiato residual de
  ~30% (`exp(0,263)-1`), altamente significativo (p<1e-36). Comparando com Branca-Negra
  (residual ~24-30% em rodadas anteriores, ordem de grandeza parecida): **o mecanismo é
  parecido em magnitude**, não um caso completamente diferente — ocupação sozinha já
  explica 33,4% do hiato Branca-Indígena, próximo do que explica pra Branca-Negra.
- **Preta vs. Parda** (`decomposicao_oaxaca_blinder_pretaparda.parquet`): decomposto
  pela primeira vez (antes só existia o hiato bruto de média). Achado importante: o
  hiato bruto atual (~-5,8%, Preta ganha menos que Parda) é **pequeno o bastante pra
  fazer os "% do hiato explicado" saírem instáveis/sem sentido interpretativo direto**
  (variam de -191% a +345% dependendo do conjunto de controles — divisão por um
  denominador perto de zero, não um bug, ver LIMITACOES). Em vez de "% explicado",
  o coeficiente residual (log-pontos, direto, sem dividir por nada) é a leitura
  confiável aqui: controlando por idade+escolaridade+ocupação, o hiato médio Preta-Parda
  **deixa de ser estatisticamente significativo** (coef=0,003, p=0,449) — ou seja, o
  hiato de MÉDIA some quase inteiro depois de controlar por características
  observáveis. Mas a história muda ao longo da distribuição: no P10 (base da
  distribuição), o coeficiente residual é positivo e significativo (Preta > Parda
  controlando por X); no P90 (topo), é negativo e significativo (Preta < Parda
  controlando por X) — um "teto de vidro" especificamente para Preta DENTRO da própria
  população negra, mesmo depois de controlar por idade/escolaridade/ocupação, que não
  aparece na média.

### Segregação ocupacional e setorial (índice de Duncan)

- **Ocupacional, Branca vs. Indígena** (`segregacao_ocupacional_indigena.parquet`):
  **16,8%** (pooled 2024T3-2026T2, único valor publicável — ver LIMITACOES pra por que
  não é série trimestral). Bem abaixo do índice Branca-Negra (~17% na série mais
  recente) — praticamente a mesma magnitude de segregação ocupacional, apesar do hiato
  de renda Branca-Indígena ser um pouco maior que Branca-Negra.
- **Ocupacional, Preta vs. Parda** (`segregacao_ocupacional_pretaparda.parquet`):
  **3,1%** no trimestre mais recente — ordem de grandeza MUITO menor que
  Branca-Negra/Branca-Indígena (~17%). Preta e Parda têm perfis ocupacionais bem
  parecidos entre si; a segregação ocupacional é majoritariamente um fenômeno
  Branca-vs-Negra, não um fenômeno interno à população negra.
- **Setorial, Preta vs. Parda** (`segregacao_setorial_pretaparda.parquet`): **4,7%** no
  trimestre mais recente — mesmo padrão (baixa segregação interna).
- **Setorial, Branca vs. Indígena**: **não publicado** — nem agregando os 58 trimestres
  inteiros a menor categoria de `setor_atividade` (12 categorias) fica acima do
  `n_minimo`=30 (ficou em 11). Documentado como limitação, não forçado.

### Hiato regional

- **Branca vs. Indígena, por Região** (`hiato_regional_indigena.parquet`, série
  trimestral completa, 290 linhas): viável em quase toda célula (288/290 região×
  trimestre com n≥30, checado antes de construir).
- **Preta vs. Parda, por UF** (`hiato_regional_pretaparda.parquet`, série trimestral
  completa, 1.566 linhas): viável em nível de UF (mais fino que Região) — Parda é
  ~50% da amostra, Preta tem no mínimo ~277 pessoas por UF já num único trimestre.

### Topo 10% / quartis

- **Dentro de Preta e dentro de Parda separadamente**
  (`perfil_topo10_racial_pretaparda.parquet`, `perfil_quartis_racial_pretaparda.parquet`):
  série trimestral completa, mesmo padrão de amostra grande de sempre.
- **Dentro de Indígena** (`perfil_topo10_racial_indigena.parquet`,
  `perfil_quartis_racial_indigena.parquet`): só publicável como UMA janela pooled
  (últimos 8 trimestres, 2024T3-2026T2) — trimestre a trimestre a amostra de Indígena
  ocupado com renda fica abaixo do mínimo pros 3 limiares de quartil.

## 2. Decomposição raça × gênero (2 fatores) — nove combinações vs. Homem Branco

`decomposicao_raca_genero.parquet` generaliza `dupla_desvantagem.parquet` (que só
cobria Homem Branco vs. Mulher Negra) pras nove combinações pedidas: Mulher Branca,
Homem Negro, Mulher Negra, Homem Indígena, Mulher Indígena, Homem Preto, Mulher Preta,
Homem Pardo, Mulher Pardo — todas vs. Homem Branco, trimestre a trimestre, Brasil.
Fórmula: `gap_total = efeito_raça + efeito_gênero − interação` (ver docstring da função
pro detalhe). Achados do trimestre mais recente (2026 T2):

| Combinação | Gap vs. Homem Branco | efeito raça | efeito gênero | interação |
|---|---:|---:|---:|---:|
| Mulher Preta | 55,1% | R$2.379 | R$1.258 | -R$677 |
| Mulher Negra | 52,6% | R$2.239 | R$1.258 | -R$671 |
| Mulher Parda | 52,0% | R$2.202 | R$1.258 | -R$669 |
| Mulher Indígena | 48,9% | R$2.561 | R$1.258 | -R$1.193 |
| Homem Indígena | 47,7% | R$2.561 | R$0 | R$0 |
| Homem Preto | 44,3% | R$2.379 | R$0 | R$0 |
| Homem Negro | 41,7% | R$2.239 | R$0 | R$0 |
| Homem Pardo | 41,0% | R$2.202 | R$0 | R$0 |
| Mulher Branca | 23,4% | R$0 | R$1.258 | R$0 |

Três achados não-óbvios:

1. **Homem Indígena tem o MAIOR "efeito raça puro" isolado** (R$2.561, maior até que o
   de Homem Preto) — o penalty de raça sozinho (mantendo gênero=Homem fixo) é mais
   forte pra Indígena que pra qualquer recorte de Negra. Ainda assim, o gap TOTAL de
   Mulher Indígena (48,9%) fica ABAIXO do de Mulher Preta/Negra/Parda (52-55%) — porque
   o termo de interação de Mulher Indígena é o mais negativo de todos (-R$1.193).
2. **O termo de interação é negativo em toda combinação "Mulher + raça não-branca"**:
   o gap total observado é sempre MENOR que a soma simples de efeito-raça +
   efeito-gênero previsse. Isso NÃO significa que ser mulher negra/indígena "não
   acumula" desvantagem — é uma propriedade de uma decomposição de MÉDIAS, que pode
   sair sub-aditiva por composição (ex.: seleção de quem permanece no mercado de
   trabalho formal pode diferir por sexo dentro de cada raça) — mesmo cuidado de
   leitura já aplicado ao Gini/Theil por raça no projeto (ver LIMITACOES).
3. **Repetindo a decomposição com Preta/Parda separadas** (em vez de Negra combinada)
   muda pouco a ordem geral — Mulher Preta fica em primeiro lugar no gap total (à
   frente de Mulher Negra combinada), Homem Pardo é o de MENOR gap entre os quatro
   grupos não-brancos/não-indígenas.

Indígena não precisou de nenhum agrupamento de trimestres aqui — mesmo Indígena×sexo
em nível Brasil, trimestre a trimestre, tem n mínimo histórico de 136 (checado antes de
construir a função).

## 3. Ritmo de convergência do hiato — Branca-Negra, Branca-Indígena, Preta-Parda

`ritmo_convergencia_hiatos.parquet` ajusta uma tendência linear simples no hiato
percentual de cada par ao longo dos 58 trimestres:

| Par | Hiato atual | Inclinação (p.p./ano) | R² | Tendência confiável? | Anos p/ zerar (extrapolação ingênua) |
|---|---:|---:|---:|---|---:|
| Branca-Negra | 66,2% | -0,85 | 0,58 | Sim | ~78 anos |
| Branca-Indígena | 72,7% | +0,70 (bruta) / +0,85 (suavizada) | 0,07 (bruta) / 0,25 (suavizada) | Sim (só na série suavizada) | — (não converge, está piorando) |
| Preta-Parda | -5,8% | -0,35 | 0,50 | Sim | — (não converge, está piorando) |

- **Branca-Negra**: converge lentamente. "~78 anos pra zerar no ritmo atual" é só um
  exercício ilustrativo de extrapolação ingênua (assume a mesma inclinação linear
  projetada indefinidamente) — nunca uma projeção de verdade.
- **Branca-Indígena é a série mais ruidosa das três** (menor amostra por trimestre):
  o ajuste na série BRUTA tem R²=0,07 (baixo, não confiável isoladamente); numa
  versão suavizada (média móvel de 4 trimestres, mesmo padrão já usado nos gráficos
  de Indígena) o R² sobe pra 0,25 — confiável o bastante pra dizer a DIREÇÃO (hiato
  SUBINDO, não descendo), mas não confiável o bastante pra um número preciso de
  inclinação. Como o hiato está subindo (divergindo), não faz sentido nenhum "anos
  pra zerar" — reportado como tal (branco/NaN), não forçado.
- **Preta-Parda tem um resultado sutil que exige atenção ao SINAL**: o hiato atual já é
  NEGATIVO (Preta ganha menos que Parda, -5,8%) e a inclinação também é negativa
  (-0,35 p.p./ano) — os dois têm o MESMO sinal, então o hiato está ficando **mais
  negativo** (Preta se afastando ainda mais de Parda por baixo), não convergindo pra
  zero. Um bug real foi encontrado e corrigido durante a construção desta função: a
  primeira versão calculava "anos pra zerar" só checando se a inclinação era negativa,
  sem considerar o sinal do nível atual — nesse caso específico (nível negativo +
  inclinação negativa = divergindo) o cálculo ingênuo teria devolvido um número
  negativo sem sentido (-16,7 "anos"). Corrigido para exigir sinais OPOSTOS entre
  nível e inclinação (a condição real de "aproximando de zero").

## 4. Painel rotativo real — transições desemprego→emprego e informal→formal

`transicao_desemprego_emprego.parquet` e `transicao_informal_formal.parquet` ligam a
MESMA PESSOA entre trimestres calendário consecutivos via (UPA, V1008, V2003) + V1016
avançando exatamente +1 + sexo/idade consistentes (ver `pnadc_core`/`agregacoes_pnadc.
gerar_transicoes_painel` pro método completo — é o painel rotativo REAL da PNAD
Contínua, até 5 entrevistas por domicílio, diferente da coorte sintética usada em
`geracao`). Taxa de match geral ~68% das pessoas-trimestre da base (dentro do esperado
dado que cada ciclo de painel dura só 5 visitas). Pooled no período 2012-2026 inteiro,
Brasil apenas (nem trimestre a trimestre, nem por UF/Região — teria deixado células,
sobretudo de Indígena, abaixo do `n_minimo`; ver LIMITACOES).

| Raça | Sexo | Desemprego→emprego | Informal→formal |
|---|---|---:|---:|
| Branca | Homem | 33,2% | 15,3% |
| Branca | Mulher | 25,1% | 14,5% |
| Preta | Homem | 36,3% | 13,1% |
| Preta | Mulher | 24,5% | 11,6% |
| Parda | Homem | 36,1% | 12,1% |
| Parda | Mulher | 23,8% | 11,2% |
| Indígena | Homem | 37,6% | 10,4% |
| Indígena | Mulher | 24,9% | 10,7% |
| Negra | Homem | 36,1% | 12,3% |
| Negra | Mulher | 24,0% | 11,3% |

Dois achados que pedem leitura cuidadosa:

1. **Homens negros/pardos/pretos/indígenas SAEM do desemprego mais rápido que homens
   brancos** (36-38% vs. 33%) — o oposto do que a direção do hiato de renda sugeriria
   à primeira vista. Não é "situação melhor": condiz com maior rotatividade em
   trabalhos mais precários/informais (que têm ciclos de entrada/saída mais curtos),
   não com melhores oportunidades — mesmo cuidado de leitura já aplicado ao Gini por
   raça (um número "melhor" isoladamente pode refletir um mercado de trabalho pior em
   outra dimensão, não capturado pela métrica em si).
2. **Em compensação, a transição informal→formal é sistematicamente menor pra todo
   grupo não-branco**, e MENOR AINDA pra Indígena (10,4-10,7%, a mais baixa das
   cinco) — condizente com o hiato de renda e com a literatura de acesso desigual a
   emprego formal. As duas métricas juntas contam uma história consistente:
   trabalhadores negros/indígenas circulam mais rápido por empregos (geralmente
   informais), mas têm mais dificuldade de ATERRISSAR num emprego formal
   especificamente.

Mesmo Indígena, que era a preocupação central de amostra nesse item, chegou a
n=1.451-1.653 desocupados pareados e n=3.913-4.150 informais pareados por sexo (pooled
período inteiro) — de sobra pro `n_minimo`=30. Branca/Negra/Preta/Parda têm amostra
grande o bastante que TERIA dado pra fazer série trimestral (não só pooled) — não
construído nesta rodada pra não estourar o escopo além do pedido original, registrado
como candidato futuro em [PLANO.md](PLANO.md).
