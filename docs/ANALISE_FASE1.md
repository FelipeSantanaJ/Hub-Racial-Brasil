# Análise Etapa 1 — PNAD Contínua (2012-2026)

Galeria completa dos gráficos exploratórios da Etapa 1 — todas as interseções entre raça,
gênero, faixa etária e escolaridade, para renda habitual real (deflator oficial do IBGE, ver
[PLANO.md](PLANO.md)), Brasil, salvo indicação contrária.

> **Atualizado na Onda 1 (13/10/2026).** Todo número de renda deste documento é da **população de
> referência**: ocupados de 18+ anos com renda habitual do **trabalho principal** (`VD4016`) > 0, em R$ do
> 2º trimestre de 2026. Até esta data o Hub usava ocupados de 14+ com renda de todos os trabalhos (`VD4019`);
> a troca reduziu o hiato Branca × Negra em 1,4 p.p. em média (`docs/CHANGELOG_METODOLOGICO.md`). Quanto o
> hiato muda com outras populações (todos os adultos, renda domiciliar) está em
> [`studies/S1/ficha.md`](studies/S1/ficha.md). Indicadores que não são de renda (escolaridade, ocupação,
> desalento, alfabetização) seguem com pessoas de 14+. Gerados por
`src/processing/graficos_fase1.py` a partir dos datasets em `data/processed/*.parquet`.
Também disponível como apresentação: [Datahub_Racial_Brasil_Fase1.pptx](Datahub_Racial_Brasil_Fase1.pptx).

87 gráficos nesta galeria (de 687 imagens em `docs/img`: 503 da árvore `arv_*` e 184 das demais análises; contagem da Onda 1, 13/10/2026). O deck em PPTX (`Datahub_Racial_Brasil_Fase1.pptx`) é
organizado como uma **árvore cruzada** de renda por raça (Branca / Negra / Indígena), sem
repetição de imagem — ver [README](../README.md) e [PLANO.md](PLANO.md) (bloco "Deck em
árvore"). Os gráficos da árvore (`docs/img/arv_*.png`, gerados por
`src/processing/graficos_arvore.py`) e do bloco topo 10% / base 10% / quartis com limiares
Brasil / gênero / raça×gênero (`docs/img/ext_*.png`, por `graficos_extremos.py`) **não**
estão listados aqui — esta galeria é a leitura narrada das análises exploratórias, inclusive
da família Preta vs. Parda separadas (que não entra no deck em árvore). Índice:

- [Raça](#raça)
- [Hiato Branca vs. Negra — série histórica](#hiato-branca-vs-negra--série-histórica)
- [É ocupação, ou é cor da pele?](#é-ocupação-ou-é-cor-da-pele)
- [Raça cruzada com tudo: as combinações que faltavam](#raça-cruzada-com-tudo-as-combinações-que-faltavam)
- [Aprofundamentos: região, segregação e quebras estruturais](#aprofundamentos-região-segregação-e-quebras-estruturais)
- [Aprofundamentos: novas variáveis da PNAD](#aprofundamentos-novas-variáveis-da-pnad)
- [Geração: seguindo a mesma coorte, não a mesma faixa etária](#geração-seguindo-a-mesma-coorte-não-a-mesma-faixa-etária)
- [Quem está no topo 10%? Negra vs. Branca](#quem-está-no-topo-10-negra-vs-branca)
- [Decomposição dos 4 quartis de renda — Negra vs. Branca](#decomposição-dos-4-quartis-de-renda--negra-vs-branca)
- [Desigualdade interna, setor público/privado e sobre-qualificação](#desigualdade-interna-setor-públicoprivado-e-sobre-qualificação)
- [A função quantil da renda, em R$, e sua inversa](#a-função-quantil-da-renda-em-r-e-sua-inversa)
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

O hiato relativo caiu de 74,2% (2012 T1; 74,9% na média de 2012) para 65,7% (2026 T2) — **todos os 58 trimestres da série são
estatisticamente significativos a 95%** (dado o tamanho da amostra, o intervalo de confiança
é muito estreito e praticamente invisível no gráfico).

![Hiato absoluto](img/hiato_racial_absoluto.png)

Em R$, uma história diferente aparece: o hiato **disparou durante a pandemia** (pico de
R$ 1.964 em 2020 T3) antes de despencar para o menor valor da série (R$ 1.461 em 2021 T4) e
se recuperar até os R$ 1.856 de 2026 T2. O hiato percentual e o absoluto contam ângulos
complementares — vale olhar os dois.

## É ocupação, ou é cor da pele?

![Decomposição do hiato](img/decomposicao_hiato_ocupacional.png)

Pergunta: controlando por idade, escolaridade e ocupação, o hiato de renda negros vs.
brancos ainda existe, ou desaparece? Decompondo progressivamente (últimos 8 trimestres,
pessoas ocupadas, padronização direta — ver [PLANO.md](PLANO.md) para o método completo):

| Controle | Hiato |
|---|---|
| Nenhum (hiato bruto) | 66,4% |
| + faixa etária | 63,6% |
| + faixa etária + escolaridade | 30,7% |
| + faixa etária + escolaridade + ocupação | **24,7%** |

Idade sozinha quase não explica nada. Escolaridade explica mais da metade do hiato. Ocupação
explica uma fatia adicional — mas **mesmo comparando pessoas da mesma idade, mesma
escolaridade e mesma categoria ocupacional, sobra um hiato de ~25%** que essas três variáveis
não explicam. Não é prova direta de discriminação (outros fatores não medidos aqui — horas
trabalhadas, formalidade, região, senioridade dentro da ocupação — também podem contribuir),
mas mostra que "estar na mesma ocupação" está longe de eliminar o hiato racial de renda.

**E quanto ocupação SOZINHA explica, sem controlar idade/escolaridade primeiro?** A barra
"Só ocupação (isolado)" no mesmo gráfico responde: o hiato cai de 66% pra **34%** — ou seja,
ocupação por si só (uma única variável) já explica quase tanto quanto idade+escolaridade
JUNTAS (que levam a 31%). Ocupação é, isoladamente, um dos fatores mais explicativos do hiato
que temos nesta base.

**Mesma pergunta, com teste de significância formal** — regressão (Oaxaca-Blinder):

![Decomposição de Oaxaca-Blinder](img/oaxaca_blinder_decomposicao.png)

Com os mesmos controles, o resíduo (parte "não-explicada" — mesma idade, escolaridade e
ocupação, retorno diferente) converge pra **+23%**, muito perto dos 25% da padronização
direta acima — dois métodos diferentes concordando é uma checagem de robustez importante —
e agora **com teste de significância** (p < 0,001, não é ruído amostral).

![Hiato residual por quantil](img/oaxaca_blinder_quantis.png)

O resíduo não é uniforme ao longo da distribuição de renda: menor na mediana (~15%), mas
maior tanto na base (P10, ~35% — "piso pegajoso") quanto no topo (P90, ~34% — "teto de
vidro", coerente com o hiato que se abre no Superior completo).

A mesma barra "só ocupação" aqui: explica **40% do hiato** de log-renda, com significância
formal (p < 0,001) — um pouco menos que os 52% que idade+escolaridade+ocupação juntas
explicam neste método, mas ainda assim substancial pra uma única variável.

![Renda por raça e ocupação](img/renda_por_raca_ocupacao.png)

E olhando direto, sem decomposição nenhuma: dentro de **cada uma** das 11 categorias
ocupacionais, Branca ganha mais que Negra — o hiato não desaparece nem na categoria mais bem
paga (Diretores/gerentes: R\$10.865 Branca vs. R\$7.252 Negra) nem na pior paga (Ocupações
elementares: R\$1.837 vs. R\$1.541; média dos últimos 8 trimestres).

## Raça cruzada com tudo: as combinações que faltavam

Fecha a matriz de combinações de raça × gênero × faixa etária × geração × escolaridade ×
ocupação — em especial as que envolvem ocupação e as que cruzam geração/faixa etária com
escolaridade/ocupação. Cada gráfico é um heatmap com um painel por raça
(Branca/Negra/Indígena), célula em branco = amostra insuficiente naquele cruzamento (mais
comum com Indígena, sample menor).

**Combinação deliberadamente pulada**: raça × faixa etária × geração. As duas são visões
diferentes da mesma coisa (idade) — faixa etária é a idade ATUAL da pessoa, geração é o ano
de nascimento. Cruzá-las criaria células minúsculas e instáveis sem agregar informação nova
além do que os gráficos "raça × faixa etária" e "raça × geração" (seções anteriores) já
mostram separadamente.

![Raça, gênero e geração](img/raca_genero_geracao.png)
![Raça, gênero e ocupação](img/raca_genero_ocupacao.png)
![Raça, faixa etária e escolaridade](img/raca_faixa_etaria_escolaridade.png)
![Raça, faixa etária e ocupação](img/raca_faixa_etaria_ocupacao.png)
![Raça, geração e escolaridade](img/raca_geracao_escolaridade.png)
![Raça, geração e ocupação](img/raca_geracao_ocupacao.png)
![Raça, escolaridade e ocupação](img/raca_escolaridade_ocupacao.png)

Padrão consistente em todos os sete: dentro de praticamente qualquer par de células
comparáveis (mesma faixa etária/geração/escolaridade E mesma ocupação), Branca aparece com
renda mais alta que Negra na grande maioria dos cruzamentos — o hiato resiste a controles
bem finos, não só aos controles agregados já vistos nas seções de decomposição.

## Aprofundamentos: região, segregação e quebras estruturais

![Hiato por região](img/hiato_racial_por_regiao.png)

O hiato racial varia MUITO entre regiões. O Sudeste tem o maior nos 58 trimestres (de 59,7% a
83,3% ao longo de 2012T1–2026T2); o Sul tem a faixa mais baixa (de 39,2% a 52,4%) e é o menor em
45 dos 58 trimestres. Faixas = mínimo e máximo de `hiato_regional.parquet`. A desigualdade regional do Brasil também aparece especificamente no
hiato racial, não é uniforme pelo país.

![Segregação ocupacional](img/segregacao_ocupacional.png)

Índice de dissimilaridade de Duncan: ~17% de um dos grupos (Branca ou Negra) precisaria
trocar de categoria ocupacional pra igualar a distribuição do outro — mede segregação
ocupacional em si, à parte do efeito dela na renda (já coberto pela decomposição acima).

![Quebra estrutural](img/hiato_quebra_estrutural.png)

Teste tipo Chow (simplificado) nos 3 eventos já mapeados como possíveis pontos de inflexão,
com EP robusto a autocorrelação (EWC; Onda 2, [B1](studies/B1/ficha.md)) e correção para os 3 eventos:
reforma trabalhista (2017) e recessão (2015) mostram mudança significativa de patamar e/ou
inclinação; a reforma da previdência (2019) **não** (com o EP antigo, i.i.d., as três apareciam) — não é
prova de causalidade (a série tem só 58 pontos e outros eventos concorrentes, como a
pandemia perto da reforma da previdência, não são controlados), mas é evidência de
correlação temporal que vale documentar.

## Aprofundamentos: novas variáveis da PNAD

Quatro variáveis da PNAD que complementam renda e ocupação — ver decodificação
completa em [LIMITACOES_E_METODOLOGIA.md](LIMITACOES_E_METODOLOGIA.md).

![Informalidade](img/informalidade_carteira_assinada.png)

% com carteira assinada (só CLT) entre empregados privados, domésticos e públicos, 2026 T2
(`informalidade.parquet`, Brasil, 14+): Branca 71,7%, Negra 63,0%, Indígena 48,4%. Militares e
estatutários ficam em categoria própria: 13,2% / 9,8% / 9,5% dos empregados. O hiato de proteção
social/formalização acompanha o hiato de renda.

> **Mudança de definição (Onda 1, 13/10/2026):** até esta data "com carteira" incluía militares e
> estatutários (Branca 75,4%, Negra 66,5%, Indígena 53,1% em 2026 T2). Um texto ainda anterior dizia
> 72/63/52%, que não correspondia a nenhuma das duas definições (E8 da auditoria Rodada 2).

![Renda por hora](img/renda_por_hora.png)

Testando se o hiato de renda vem de jornada menor: **não vem** — a jornada semanal habitual
no trabalho principal é parecida entre os três grupos (40,0h Branca vs. 39,0h Negra vs. 38,4h
Indígena, 2026 T2), e o hiato na renda POR HORA (63%) é quase idêntico ao hiato na renda mensal
(66%). O hiato é
de remuneração por hora mesmo, não de quantas horas se trabalha.

![Alfabetização 60+](img/alfabetizacao_60mais.png)

Analfabetismo residual ainda é uma realidade nas cohorts mais velhas: 93% Branca vs. 80%
Negra vs. 72% Indígena alfabetizados entre 60+ anos (2026 T2).

![Desalento](img/desalento.png)

Entre quem está fora da força de trabalho (denominador: pessoas de 14+ anos fora da força,
`desalento_subutilizacao.parquet`, Brasil, 2026 T2), estão desalentadas 4,5% das pessoas
Negras e 4,1% das Indígenas, contra 2,0% das Brancas. Desalento vai além da taxa de
desocupação simples e também tem recorte racial. (Até 13/10/2026 este parágrafo dizia
7,4/5,9/3,4%, números que nenhuma definição testada reproduz: E7 da auditoria Rodada 2.)

## Geração: seguindo a mesma coorte, não a mesma faixa etária

A PNAD Contínua é um corte transversal **repetido**, não um painel longitudinal — "pessoas
de 14-17 anos" em 2012 e em 2026 são pessoas **diferentes** chegando nessa idade, não as
mesmas envelhecendo. Um gráfico "por faixa etária" ao longo do tempo mistura coortes de
nascimento diferentes a cada trimestre. Geração resolve isso agrupando por ano de nascimento
aproximado (ano da pesquisa − idade) — cada linha abaixo é (aproximadamente) o MESMO grupo de
pessoas nascidas numa janela, observado envelhecendo dentro da janela 2012-2026 (método de
coorte sintética, Deaton 1985).

![Hiato por geração](img/hiato_racial_por_geracao.png)

O hiato varia MUITO entre gerações — em 2026 T2, de 33% na Geração Z a 85% no Baby Boomer. O do
Baby Boomer oscila bastante (média anual entre 78% e 99%), sem tendência clara; parte dessa
instabilidade deve vir de seleção: quem continua trabalhando até os 60–80 anos não é uma amostra
aleatória (hipótese, não testada aqui). Até 13/10/2026 este parágrafo dizia que o hiato do Baby
Boomer "cresce"; com a população de referência a série não sustenta isso.

![Renda por geração e raça](img/renda_por_geracao_raca.png)

Snapshot do trimestre mais recente, cada geração na idade em que está hoje (não controla por
idade) — o hiato racial aparece em todas as quatro gerações com amostra suficiente.

## Quem está no topo 10%? Negra vs. Branca

Não é "top 10% do Brasil" (que seria quase todo Branca, dado o hiato) — é o topo 10% **DENTRO**
de cada raça, com o limiar (P90) calculado separadamente para Branca e para Negra. Responde:
quem chega ao topo dentro do próprio grupo racial, e como isso mudou ao longo do tempo?
(Indígena fica de fora — amostra insuficiente pra um P90 confiável por trimestre.)

![Topo 10% — gênero](img/topo10_genero.png)

% de mulheres no topo 10% de cada raça: Branca sempre um pouco à frente da Negra, com distância
pequena e estável (média anual: 30,3% vs. 27,5% em 2012; 34,9% vs. 32,5% em 2026).

![Topo 10% — escolaridade](img/topo10_escolaridade.png)

O achado mais forte desta seção: o topo 10% dos negros ficou muito mais escolarizado — de
37% com Superior completo em 2012 T1 para 61% em 2026 T2 — mas ainda fica atrás do topo dos
brancos (84%). A escolaridade de quem chega ao topo está convergindo, ainda que o nível continue
bem diferente.

![Topo 10% — composição completa de escolaridade](img/topo10_escolaridade_composicao.png)

A distribuição completa pelos 7 níveis (não só Superior completo): o topo 10% dos negros tem
mais que o dobro de Médio completo (22,5%) do que o dos brancos (8,7%; 2026 T2) — quem não chega ao
Superior completo dentro do topo dos negros, na maioria das vezes, já concluiu o Médio, não
fica pra trás no Fundamental.

![Topo 10% — faixa etária](img/topo10_faixa_etaria.png)

Composição por faixa etária do topo 10%, média dos últimos 8 trimestres — o topo dos negros é
um pouco mais concentrado em 25-39 anos e um pouco menos em 60+ do que o topo dos brancos.

![Topo 10% — geração](img/topo10_geracao.png)

Composição por geração do topo 10% — o topo dos negros pende um pouco mais para
Millennial/Geração Z; o topo dos brancos, para Baby Boomer/Geração X. Coerente com o gráfico
de escolaridade acima: gerações mais novas de negros parecem estar chegando ao topo com
credenciais mais parecidas às dos brancos do que gerações mais velhas.

## Decomposição dos 4 quartis de renda — Negra vs. Branca

O topo 10% acima é um recorte estreito (P90). Aqui vai a versão completa: **os 4 quartis**
da distribuição de renda (Q1 = 25% que menos ganham, ..., Q4 = 25% que mais ganham),
calculados DENTRO de cada raça — permite comparar a composição demográfica de QUALQUER fatia
da distribuição entre Negra e Branca, não só o topo.

![Quartis — gênero](img/quartis_genero.png)

% de mulheres em cada quartil: maioria entre as mais pobres (Q1) nas duas raças, minoria
entre as mais ricas (Q4) — e a distância ENTRE as raças também cresce no Q4 (38% Branca vs.
33% Negra, 2026 T2), não só a diferença entre quartis dentro de cada raça.

![Quartis — escolaridade](img/quartis_escolaridade.png)

O achado mais forte desta seção: % com Superior completo cresce em todos os quartis nas duas
raças, mas o hiato racial se ABRE dramaticamente no topo — no Q4, 73% de Branca tem Superior
completo contra 43% de Negra (uma diferença de 30 p.p., 2026 T2); no Q1, a diferença é de só ~6 p.p.
Confirma, com o painel completo, o padrão já visto no gráfico de topo 10%: quanto mais alto
na distribuição de renda, maior o hiato educacional entre as raças.

![Quartis — composição completa de escolaridade](img/quartis_escolaridade_composicao.png)

Distribuição completa pelos 7 níveis, um painel por quartil — mesmo padrão do topo 10% (Médio
completo mais presente entre os negros, Superior completo mais presente entre os brancos)
visível em todas as fatias da distribuição, não só no topo.

![Quartis — faixa etária](img/quartis_faixa_etaria.png)

Composição por faixa etária, um painel por quartil — perfil etário bem parecido entre Negra e
Branca dentro de cada quartil (diferente da escolaridade, que diverge fortemente no topo).

![Quartis — geração](img/quartis_geracao.png)

Composição por geração, um painel por quartil — mesmo padrão qualitativo do topo 10%, agora
visível em todas as fatias da distribuição.

## Desigualdade interna, setor público/privado e sobre-qualificação

Cinco análises sobre a estrutura interna da desigualdade — ver [PLANO.md](PLANO.md) pro
escopo completo do bloco.

![Gini por raça](img/gini_por_raca.png)

Coeficiente de Gini calculado DENTRO de cada raça — pergunta diferente do hiato ENTRE elas.
Achado que exige leitura cuidadosa: Branca tem Gini mais alto (mais desigualdade interna) que
Negra em todos os 58 trimestres (2026 T2: 0,489 vs. 0,423; Indígena 0,440; Amarela, incluída desde a
Onda 1, 0,495). Isso não significa que a população negra está "melhor" — só que sua distribuição de
renda é mais comprimida perto da base (menos gente muito rica para abrir a distribuição).

![Decomposição de Theil](img/theil_decomposicao.png)

Só ~7% (6,96% em 2026 T2, com Amarela no total desde a Onda 1) da desigualdade TOTAL de renda no Brasil vem de diferença ENTRE raças — os outros 93%
são desigualdade DENTRO de cada raça. Isso não diminui o hiato racial (que continua grande e
significativo, ver seções anteriores) — mostra que a desigualdade brasileira tem várias
fontes, e raça é uma delas identificável, não a maior fatia isolada.

![Hiato setor público vs. privado](img/hiato_setor_publico_privado.png)

Confirma uma hipótese conhecida da literatura: o hiato racial é sistematicamente menor no
setor Público (de 41,7% a 58,5% ao longo de 2012T1–2026T2, mediana 48,1%) do que no Privado
(de 54,5% a 66,7%, mediana 60,2%). É menor em todos os 58 trimestres. Faixas = mínimo e máximo de
`hiato_setor_publico_privado.parquet`. Mecanismos sugeridos (hipótese, não testada aqui): o
salário de concurso segue tabela padronizada, e no setor privado há mais espaço para negociação
individual e discricionariedade.

![Segregação setorial](img/segregacao_setorial.png)

Segregação por SETOR econômico (~10%) é menor que por OCUPAÇÃO/cargo (~17%, ver seção
anterior) — Branca e Negra se distribuem de forma mais parecida entre setores da economia do
que entre cargos específicos dentro desses setores.

![Sobre-qualificação](img/sobrequalificacao.png)

Entre quem tem Superior completo, a taxa de "sobre-qualificação" (acabar numa ocupação
elementar, o proxy padrão de mismatch credencial-ocupação na literatura) é quase o DOBRO para
Negra em relação a Branca ao longo de quase toda a série — mesmo diploma, resultado
profissional diferente. Indígena tem amostra pequena aqui (poucas pessoas com Superior
completo) e a série fica bem ruidosa mesmo suavizada — ler com cautela.

## A função quantil da renda, em R$, e sua inversa

Os gráficos de quartil (seção acima) mostram QUEM está em cada fatia da distribuição —
composição por gênero/idade/geração/escolaridade. Aqui vai o complemento: os valores
em R$ de fato, nas duas direções.

![Função quantil por raça](img/funcao_quantil_racial.png)

Responde diretamente: "os 10% mais pobres entre os negros ganham quanto, comparado aos 10%
mais pobres entre os brancos? E os 20%? E assim por diante?" No P10, Branca ganha R$1.500 e
Negra R$766 — quase o dobro (2026 T2). Na mediana (P50), R$3.000 vs. R$2.000. No P90, R$10.000 vs.
R$5.000 — o hiato em R$ cresce conforme sobe a distribuição.

![Hiato bruto por percentil](img/hiato_por_percentil.png)

O hiato bruto (sem nenhum controle, diferente da versão residual da seção "É ocupação, ou é
cor da pele?") não é uniforme ao longo da distribuição: maior na base (96% no P10) e no topo
(100% no P90), menor no meio (8% no P20; 23–50% entre P30 e P70). Os valores declarados se
concentram em números redondos (R$ 1.500, R$ 2.000…), então hiatos de percentis vizinhos pulam.

![Percentil de um valor de renda, por raça](img/percentil_de_valor_racial.png)

A pergunta INVERSA: quem ganha uma quantia fixa está em que posição da distribuição de CADA
raça? R$3.000 é uma renda "do meio" pra Branca (P58, pouco acima da mediana) — mas a mesma
quantia já coloca uma pessoa negra no P77, perto do topo dos 25% que mais ganham dentro do
próprio grupo. A mesma quantia em R$ representa posições relativas bem diferentes conforme a
raça.

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

![18-24 anos](img/renda_por_raca_faixa_18_24.png)
![25-39 anos](img/renda_por_raca_faixa_25_39.png)
![40-59 anos](img/renda_por_raca_faixa_40_59.png)
![60+ anos](img/renda_por_raca_faixa_60mais.png)

</details>

## Preta × Parda × Faixa etária

![Preta vs. Parda por faixa etária](img/renda_preta_parda_faixa_etaria.png)

<details>
<summary><strong>Um gráfico por faixa etária</strong></summary>

![18-24 anos](img/renda_preta_parda_faixa_18_24.png)
![25-39 anos](img/renda_preta_parda_faixa_25_39.png)
![40-59 anos](img/renda_preta_parda_faixa_40_59.png)
![60+ anos](img/renda_preta_parda_faixa_60mais.png)

</details>

## Raça × Escolaridade

![Renda por raça e nível de instrução](img/renda_por_raca_escolaridade.png)

**O achado mais importante da Etapa 1**: o hiato racial de renda não desaparece quando se
compara pessoas com o mesmo nível de instrução — ele só some ou até se inverte nos níveis
mais baixos, mas **se abre dramaticamente no Superior completo** (Branca R\$7.866 vs. Negra
R\$5.483 vs. Indígena R\$5.493, Brasil, 2026 T2).

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

O hiato no Superior completo é maior entre homens (Branca R\$9.697 vs. Negra R\$6.617, ~47%)
do que entre mulheres (Branca R\$6.308 vs. Negra R\$4.576, ~38%; 2026 T2).

## Raça × Gênero × Faixa etária

![Renda por faixa etária, raça e gênero](img/renda_por_faixa_etaria_raca_genero.png)

Mesmo efeito de abertura em 40-59 anos, visível nos dois gêneros — mais acentuado entre homens.

## Escolaridade × Raça × Gênero

![Superior completo por raça e gênero](img/escolaridade_por_raca_genero.png)

Hiato de conclusão do ensino superior maior que 2× entre Branca (24-29%) e Negra (10-14%).
Mulheres têm taxa de conclusão maior que homens em todos os três grupos raciais.

<details>
<summary><strong>Um gráfico por nível de instrução</strong> (os outros 6 níveis — só o Superior
completo estava publicado antes)</summary>

![Sem instrução](img/escolaridade_por_raca_genero_sem_instrucao.png)
![Fundamental incompleto](img/escolaridade_por_raca_genero_fundamental_incompl.png)
![Fundamental completo](img/escolaridade_por_raca_genero_fundamental_compl.png)
![Médio incompleto](img/escolaridade_por_raca_genero_medio_incompl.png)
![Médio completo](img/escolaridade_por_raca_genero_medio_compl.png)
![Superior incompleto](img/escolaridade_por_raca_genero_superior_incompl.png)

</details>

## Raça × Gênero × Faixa etária × Escolaridade

![Heatmap completo](img/renda_completa_heatmap.png)

As quatro dimensões de uma vez: um painel por raça × gênero (6 no total), faixa etária nas
colunas, nível de instrução nas linhas, cor = renda real. O padrão "Branca mais escura que
as outras duas em quase toda célula" segura mesmo nesse nível de detalhe.

## Limitações a ter em mente lendo estes gráficos

- Indígena tem amostra pequena — séries temporais de raça isolada usam média móvel centrada de 4
  trimestres (usa trimestres futuros; nas pontas, menos pontos); os cortes-instantâneo (escolaridade, faixa etária, heatmap completo) não
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
- **Bug estatístico encontrado e corrigido na validação**: a primeira versão da função
  `erro_padrao_media_ponderada` em `pnadc_core.py` calculava um
  erro padrão inflado por um fator de ~√n em relação ao valor correto — bug puramente de
  código, não de dados; documentado em detalhe no `docs/PLANO.md`.
- **Bug de decodificação encontrado e corrigido na validação**: `VD4009` (posição na
  ocupação/carteira assinada) tem 10 categorias e vem zero-padded (`'01'`..`'10'`) no layout
  do IBGE — o código inicial usava `'1'`,`'2'` sem padding, o que fazia `pct_com_carteira`
  sair inteiramente NULO sem erro nenhum. Encontrado só ao conferir a distribuição bruta dos
  valores antes de confiar no número.
- **Frequência escolar (V3014) descartada** *(correção de 13/10/2026, E11: `V3014` é "concluiu o
  curso que frequentou", não frequência escolar; a frequência é `V3002`, extraída na v2. O motivo
  abaixo não vale)*: a cobertura de V3014 na população
  14-17 anos é de só ~6-8% em vários trimestres testados (2018 a 2026) — bem menor que o
  ~95% de V3001 (alfabetização) ou os ~20% que uma rotação padrão de painel explicaria.
  Não foi possível confirmar se essa subamostra é aleatória
  (estimativa válida, só com IC mais largo) ou enviesada — preferimos não publicar um número
  sobre evasão escolar sem entender a regra de coleta exata do IBGE pra essa variável.
- **Geração é uma coorte SINTÉTICA, não um painel real**: "ano de nascimento" é aproximado
  (ano da pesquisa − idade, sem considerar mês de nascimento x mês de entrevista) e cada
  trimestre ainda traz PESSOAS DIFERENTES dentro da mesma geração — só o grupo de nascimento
  se mantém fixo, não os indivíduos. É o método padrão pra estudar coortes em pesquisas
  transversais repetidas (Deaton, 1985), mas não é o mesmo que acompanhar as mesmas pessoas
  ano a ano.
- **"Topo 10%" e quartis com valores redondos**: renda autodeclarada tem forte concentração
  em valores redondos (R$1.000, R$2.000, R$5.000, R$10.000 etc.; em 2026 T2, 48% da renda de
  pessoas brancas e 33% da de pessoas negras é múltipla de R$ 1.000 — `heaping_renda.parquet`).
  Até 13/10/2026 o corte `>= limiar` punha todo mundo empatado no limiar de um lado e o "topo"
  capturava 11–13%; desde a Onda 1 o peso dos empatados é repartido e cada fatia tem
  exatamente 10% ou 25% (`pct_populacao_capturada` fica como checagem).
