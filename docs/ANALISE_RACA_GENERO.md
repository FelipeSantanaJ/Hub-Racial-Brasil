# Análise Raça × Gênero — aprofundamento Branca/Negra/Indígena e Preta/Parda

Bloco dedicado a tratar os TRÊS grupos raciais (Branca, Negra, Indígena) em pé de
igualdade metodológica — não só Branca vs. Negra com Indígena como nota de rodapé — e a
abrir a diferença DENTRO da população negra (Preta vs. Parda), que até aqui só tinha o
hiato bruto de renda. Ver [PLANO.md](PLANO.md) pra decisões de escopo e
[LIMITACOES_E_METODOLOGIA.md](LIMITACOES_E_METODOLOGIA.md) pras limitações de amostra
encontradas. Entregável em tabela: os parquets em `data/processed/` e esta análise
textual dos achados (sem gráficos/PPTX próprios).

> **Auditado na Onda 2 (13/10/2026):** as médias por célula raça × sexo deste texto conferem com o estudo
> [C1](studies/C1/ficha.md) (ex.: homem branco R$ 5.238, mulher negra R$ 2.483 em 2026T2). A "interação" da seção 2 é
> uma ordem sequencial (cada fator medido a partir do homem branco) e vale −DiD em R$; a repartição que não depende
> da ordem (Shapley), em log e com IC, está no [C3](studies/C3/ficha.md); a interação formal com EP design-based está
> no [C2](studies/C2/ficha.md). A seção 3 (ritmo de convergência) foi refeita no [B1](studies/B1/ficha.md).
>
> **Atualizado na Onda 1 (13/10/2026):** números de renda na população de referência (ocupados 18+ com renda
> habitual do trabalho principal > 0). Segregação ocupacional/setorial e transições do painel não usam renda e
> não mudaram.

## 1. Levando o toolkit pesado também pra Branca-Indígena e Preta-Parda

### Oaxaca-Blinder

- **Branca vs. Indígena** (`decomposicao_oaxaca_blinder_indigena.parquet`): controlando
  por faixa etária + escolaridade + ocupação, **43,3%** do hiato (em log-renda) é
  explicado por essas três características observáveis, **56,7%** é resíduo
  não-explicado — coeficiente residual (log-pontos) equivalente a um hiato residual de
  ~31% (`exp(0,269)-1`), com p < 0,001 (EP do WLS com cluster por UPA; não passa pela linearização do B1). Comparando com Branca-Negra
  (residual ~23–29%, ordem de grandeza parecida): **o mecanismo é
  parecido em magnitude**, não um caso completamente diferente — ocupação sozinha já
  explica 32,5% do hiato Branca-Indígena, próximo do que explica pra Branca-Negra.
- **Preta vs. Parda** (`decomposicao_oaxaca_blinder_pretaparda.parquet`): decomposto
  pela primeira vez (antes só existia o hiato bruto de média). Achado importante: o
  hiato bruto atual (~−6,0%, Preta ganha menos que Parda) é **pequeno o bastante pra
  fazer os "% do hiato explicado" saírem instáveis/sem sentido interpretativo direto**
  (variam de −21% a +142% dependendo do conjunto de controles — divisão por um
  denominador perto de zero, não um bug, ver LIMITACOES). Em vez de "% explicado",
  o coeficiente residual (log-pontos, direto, sem dividir por nada) é a leitura
  confiável aqui: controlando por idade+escolaridade+ocupação, o hiato médio Preta-Parda
  **deixa de ser estatisticamente significativo** (coef=0,003, p=0,533) — ou seja, o
  hiato de MÉDIA some quase inteiro depois de controlar por características
  observáveis. Mas a história muda ao longo da distribuição: no P10 (base da
  distribuição), o coeficiente residual é positivo e significativo (+0,078; Preta > Parda
  controlando por X); no P90 (topo), é negativo e significativo (−0,032; Preta < Parda
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
cobria Homem Branco vs. Mulher Negra) pras nove combinações: Mulher Branca,
Homem Negro, Mulher Negra, Homem Indígena, Mulher Indígena, Homem Preto, Mulher Preta,
Homem Pardo, Mulher Pardo — todas vs. Homem Branco, trimestre a trimestre, Brasil.
Fórmula, com HB = renda média do Homem Branco e Y(sexo, raça) = renda média da célula:

- `gap_total = HB − Y(alvo)`;
- `efeito_raça = HB − Y(Homem, raça do alvo)`;
- `efeito_gênero = HB − Y(sexo do alvo, Branca)`;
- `interação = gap_total − efeito_raça − efeito_gênero`.

Logo **`gap_total = efeito_raça + efeito_gênero + interação`**. A versão anterior deste texto
trazia "− interação", com o sinal errado (E10). A coluna "Gap" em % é relativa à renda do
**Homem Branco** (gap_total ÷ HB; HB = R$ 5.238 em 2026 T2, população de referência). Isso difere do hiato % do resto do
Hub, que é relativo ao grupo de menor renda. Achados do trimestre mais recente (2026 T2), a
partir de `decomposicao_raca_genero.parquet` regenerado em 13/10/2026 com a correção do E6. Até
essa data, a tabela publicada trazia, por erro, efeito gênero de R$ 1.258 e interação de
−R$ 1.258 nas linhas masculinas; os valores abaixo já estavam certos neste documento.

| Combinação | Gap vs. Homem Branco (% da renda do HB) | efeito raça | efeito gênero | interação |
|---|---:|---:|---:|---:|
| Mulher Preta | 55,3% | R$2.306 | R$1.225 | -R$636 |
| Mulher Negra | 52,6% | R$2.168 | R$1.225 | -R$638 |
| Mulher Parda | 51,9% | R$2.132 | R$1.225 | -R$638 |
| Mulher Indígena | 48,5% | R$2.464 | R$1.225 | -R$1.148 |
| Homem Indígena | 47,0% | R$2.464 | R$0 | R$0 |
| Homem Preto | 44,0% | R$2.306 | R$0 | R$0 |
| Homem Negro | 41,4% | R$2.168 | R$0 | R$0 |
| Homem Pardo | 40,7% | R$2.132 | R$0 | R$0 |
| Mulher Branca | 23,4% | R$0 | R$1.225 | R$0 |

Três achados não-óbvios:

1. **Homem Indígena tem o MAIOR "efeito raça puro" isolado** (R$2.464, maior até que o
   de Homem Preto) — o penalty de raça sozinho (mantendo gênero=Homem fixo) é mais
   forte pra Indígena que pra qualquer recorte de Negra. Ainda assim, o gap TOTAL de
   Mulher Indígena (48,5%) fica ABAIXO do de Mulher Preta/Negra/Parda (52-55%) — porque
   o termo de interação de Mulher Indígena é o mais negativo de todos (-R$1.148).
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

> **Atualizado na Onda 2 (13/10/2026, estudo [B1](studies/B1/ficha.md)):** EP refeito com EWC (Newey-West e GLS AR(1)
> ao lado); "tendência confiável" = os três IC excluem zero. Branca-Negra: −0,78 p.p./ano (IC −1,25 a −0,32),
> confiável — mas com degraus no modelo a tendência some e a queda é um degrau de −5 p.p. em 2022. Branca-Indígena:
> +0,52 (IC −0,16 a 1,21), **não** confiável. Preta-Parda: −0,31 (−0,51 a −0,12), confiável. "Anos para zerar"
> saiu da tabela: a projeção condicional é o [B6](studies/B6/ficha.md). A tabela abaixo é o registro histórico.

`ritmo_convergencia_hiatos.parquet` ajustava uma tendência linear simples no hiato
percentual de cada par ao longo dos 58 trimestres (OLS com EP i.i.d. sobre a série; sem correção
para autocorrelação, R6 da auditoria):

| Par | Hiato atual | Inclinação (p.p./ano) | R² | Tendência confiável? | Anos p/ zerar (extrapolação ingênua) |
|---|---:|---:|---:|---|---:|
| Branca-Negra | 65,7% | -0,78 | 0,58 | Sim | ~84 anos |
| Branca-Indígena | 70,9% | +0,53 (bruta, p=0,11) / +0,67 (suavizada) | 0,05 (bruta) / 0,20 (suavizada) | Só na série suavizada | — (não converge) |
| Preta-Parda | -6,0% | -0,31 | 0,47 | Sim | — (não converge, está piorando) |

- **Branca-Negra**: converge lentamente. "~84 anos pra zerar no ritmo atual" é só um
  exercício ilustrativo de extrapolação ingênua (assume a mesma inclinação linear
  projetada indefinidamente) — nunca uma projeção de verdade.
- **Branca-Indígena é a série mais ruidosa das três** (menor amostra por trimestre):
  o ajuste na série BRUTA tem R²=0,05 e inclinação não significativa (p=0,11); numa
  versão suavizada (média móvel de 4 trimestres para trás; os gráficos de Indígena
  usam média móvel centrada) o R² sobe pra 0,20 — a direção (hiato subindo) aparece só na série
  suavizada, e a suavização cria autocorrelação que o EP i.i.d. ignora: **não afirmar que o hiato
  Branca-Indígena está aumentando** até o teste com HAC (Onda 2). Como o hiato está subindo (divergindo), não faz sentido nenhum "anos
  pra zerar" — reportado como tal (branco/NaN), não forçado.
- **Preta-Parda tem um resultado sutil que exige atenção ao SINAL**: o hiato atual já é
  NEGATIVO (Preta ganha menos que Parda, -6,0%) e a inclinação também é negativa
  (-0,31 p.p./ano) — os dois têm o MESMO sinal, então o hiato está ficando **mais
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
   à primeira vista. Não é necessariamente "situação melhor". **Hipótese (não testada
   aqui):** maior rotatividade em trabalhos mais precários/informais, que têm ciclos de
   entrada e saída mais curtos. Testá-la exigiria, por exemplo, olhar a duração e a
   qualidade do emprego de destino (formal/informal, renda), o que esta tabela não faz.
   Mesmo cuidado de leitura já aplicado ao Gini por raça: um número "melhor" isoladamente
   pode refletir um mercado de trabalho pior em outra dimensão.
2. **Em compensação, a transição informal→formal é sistematicamente menor pra todo
   grupo não-branco**, e MENOR AINDA pra Indígena (10,4-10,7%, a mais baixa das
   cinco) — condizente com o hiato de renda e com a literatura de acesso desigual a
   emprego formal. As duas métricas juntas são **compatíveis** com a hipótese de que
   trabalhadores negros/indígenas circulam mais rápido por empregos (geralmente
   informais), mas têm mais dificuldade de ATERRISSAR num emprego formal; não a
   demonstram.

Mesmo Indígena, que era a preocupação central de amostra nesse item, chegou a
n=1.451-1.653 desocupados pareados e n=3.913-4.150 informais pareados por sexo (pooled
período inteiro) — de sobra pro `n_minimo`=30. Branca/Negra/Preta/Parda têm amostra
grande o bastante que TERIA dado pra fazer série trimestral (não só pooled) — não
planejado como extensão para 2027 em [PLANO.md](PLANO.md).
