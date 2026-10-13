# Análise Causal — Leis de Cotas como Fonte de Variação Exógena

Primeira tentativa de identificação CAUSAL neste projeto — todo o resto do datahub (hiatos,
decomposições, Gini/Theil, segregação) é descritivo/correlacional, mesmo quando o método é
estatisticamente rigoroso. Este documento é um desenho PRELIMINAR: onde a identificação é
forte, digo; onde é fraca, digo também, no mesmo nível de destaque. Nenhum número aqui deve
ser lido como "prova de efeito causal" — ver a seção final, "o que isso NÃO prova".

> **Estado (13/10/2026): Bloqueado até o B4b** (reespecificação do Desenho B no plano de análise).
> As seções 2 e 3 foram reescritas como **exploratórias** depois da auditoria Rodada 2 (E9). O
> Desenho B tem **40 testes de DiD**: 5 nacionais e 35 de heterogeneidade. **Nenhum sobrevive ao
> FDR de Benjamini-Hochberg**; os menores p ajustados são 0,072 (nacional) e 0,191
> (heterogeneidade). Toda menção a p abaixo traz o p ajustado (`did_p_valor_bh`) na mesma frase.

## 0. Enquadramento

A PNAD Contínua não tem nota de vestibular nem identifica a instituição de ensino da pessoa
— o desenho de regressão descontínua (RDD) que a literatura padrão usa pra medir o efeito
causal das cotas raciais no Brasil (Mello 2022; Francis-Tan & Tannuri-Pianto) comparando
quem passou e quem não passou pela nota de corte da cota **não é possível com este dado**.

O desenho possível aqui é diferente: **diff-in-diff por COORTE DE EXPOSIÇÃO**, no nível
agregado (coorte de nascimento, ou setor×trimestre), não indivíduo tratado/não-tratado.
Isso troca identificação fina (o RDD compara pessoas quase idênticas de cada lado exato de
uma nota de corte) por cobertura nacional e histórica (RDD fica restrito às universidades e
anos com dado de vestibular disponível; aqui é o país inteiro, 2012-2026). É uma troca
honesta, não uma tentativa de imitar o RDD com dado pior — ver a seção 3.

Dois desenhos, duas leis:

- **Desenho A** — Lei de Cotas Universitárias (12.711/2012): coorte de nascimento como
  fonte de variação — quem nasceu antes ou depois de 1994 (18 anos antes da lei) teve
  acesso à cota, ou não, contando desde a entrada na universidade.
- **Desenho B** — Lei de Cotas no Serviço Público Federal (12.990/2014): event-study
  diff-in-diff, setor público vs. privado (controle), em torno de jun/2014.

## 1. Desenho A — Lei de Cotas Universitárias (12.711/2012)

### Método

`ano_exposicao = ano_nascimento_aprox + 18` (idade típica de entrada na universidade);
`exposto = 1` se `ano_exposicao >= 2012`, ou seja, quem nasceu em 1994 ou depois. É uma
aproximação de *intent-to-treat*: nem todo mundo entra na universidade aos 18 (erro de
medida que dilui qualquer efeito real, não infla), e a lei teve **rampa** de implementação
(universidades tinham até 2016 pra atingir 100% da cota) — por isso rodo duas
especificações: nível (dummy pós-1994) e rampa (anos desde o limiar, capado em 4).

Outcome: % com Superior completo, medido **sempre aos 25-29 anos** — idade fixa, pra não
confundir efeito da lei com "coorte mais nova ainda não teve tempo de terminar a
faculdade" (sem isso, qualquer comparação entre coortes seria uma comparação de
MATURAÇÃO, não de acesso à cota). Coortes disponíveis nessa janela de idade: nascidos
entre 1983 e 2001 (19 pontos de coorte, ~9-11 de cada lado do limiar de 1994).

### Resultado: nenhum efeito de nível detectado, tendências paralelas sustentadas

| Raça tratada | Tendência pré-1994 (coef, p) | DiD nível 2012 (coef, p) | DiD rampa (coef, p) |
|---|---|---|---|
| Negra | -0,08 pp/ano, p=0,42 | -0,04 pp, p=0,97 | ver parquet |
| Indígena | -0,14 pp/ano, p=0,86 | +1,81 pp, p=0,80 | ver parquet |

**Tendências paralelas: sustentadas nos dois pares** (coeficiente de tendência
raça-específica pré-1994 não significativo, p=0,42 e p=0,86) — pré-requisito do desenho
não é violado, o que é um sinal de validade metodológica, mesmo sem um efeito
significativo pra reportar.

**DiD nível: nenhum efeito estatisticamente significativo** em nenhum dos dois pares
(p=0,97 e p=0,80) — a rampa (capando em 4 anos) também não muda essa leitura
(`did_cotas_universitarias.parquet`).

### Placebo: nenhum "efeito" espúrio em datas falsas

Rodei a mesma especificação fingindo que a lei foi em 2008 e em 2016 (nenhuma mudança de
política real nessas datas). Nenhum dos quatro placebos (2 datas × 2 pares) deu
significativo — reforça que a ausência de efeito no corte real não é um artefato de uma
tendência espúria genérica que apareceria em qualquer data (se aparecesse nos placebos
também, seria motivo pra desconfiar até do resultado nulo).

![Lei de Cotas Universitárias — Branca vs. Negra](img/causal_cohortes_universitaria_negra.png)
![Lei de Cotas Universitárias — Branca vs. Indígena](img/causal_cohortes_universitaria_indigena.png)

Visualmente, as duas curvas (Branca e Negra) sobem de forma suave e contínua atravessando o
limiar de 1994 sem nenhum "degrau" visível — consistente com o DiD nulo. Isso é uma leitura
honesta possível: com um desenho de coorte agregado (só ~19 pontos de coorte, sem
identificar quem de fato usou a cota), um efeito real mas moderado pode não ter poder
estatístico suficiente pra aparecer — "não detectamos efeito" não é o mesmo que "não há
efeito", e a seção 3 volta nisso.

### Extensão de mecanismo (correlacional, não um resultado causal novo)

Pergunta: dentro do universo de coortes 1983-2001 já ocupadas hoje, o hiato de renda
Branca-Negra, controlando por idade/escolaridade/ocupação (Oaxaca-Blinder, mesmo método
de `gerar_decomposicao_oaxaca_blinder`), é diferente entre quem nasceu antes ou depois de
1994?

| Coorte | n | % explicada | Resíduo (log-pontos, p) | Resíduo aprox. em % |
|---|---:|---:|---|---:|
| Pré-exposição (< 1994) | 3.238.942 | 51,3% | 0,200 (p≈0) | ~22,1% |
| Pós-exposição (1994+) | 1.384.950 | 40,5% | 0,171 (p≈0) | ~18,6% |

O resíduo (o que sobra do hiato mesmo controlando por escolaridade/ocupação/idade) é um
pouco MENOR na coorte pós-exposição (~18,6% vs. ~22,1%), mas a % do hiato bruto EXPLICADA
por essas características cai (40,5% vs. 51,3%). (Valores da Onda 1, 13/10/2026: ocupados 18+ com
renda do trabalho principal; antes, 14+ com todos os trabalhos.) **Leitura correlacional, três motivos
pra não superinterpretar**: (1) as coortes pós-1994 ainda estão em início/meio de carreira
(mesmo controlando por faixa etária, a composição etária dentro de cada faixa pode diferir);
(2) não sei quem de fato passou pela cota — é a mesma aproximação de exposição do Desenho A,
sem o teste formal de DiD aplicado aqui; (3) é uma correlação dentro do universo de quem já
está ocupado, sujeita a qualquer viés de seleção do próprio mercado de trabalho.

## 2. Desenho B — Lei de Cotas no Serviço Público Federal (12.990/2014)

### Método

Event-study: pessoa × setor_trabalho (Público/Privado) × trimestre relativo à lei (0 = 1º
trimestre pós-lei, 2014 T3 — a lei foi sancionada em jun/2014, 2014 T2; um trimestre de
defasagem administrativa pra concursos já em andamento não serem afetados
imediatamente). Privado é o grupo de CONTROLE (setor não atingido pela lei). Janela: -10 a
+12 trimestres (todo o período pré disponível; pós capado em 3 anos pra manter o gráfico
legível).

Dois outcomes: (a) participação de Negra/Preta/Parda/Indígena entre ocupados do setor
público (outcome pessoa a pessoa: `1 se raça==alvo`, em pontos percentuais); (b) hiato de
renda Branca-Negra especificamente DENTRO de cada setor.

Inferência: a CURVA (coeficiente por trimestre relativo) é calculada em forma fechada —
diferença de médias ponderadas com erro padrão somado em quadratura — porque uma regressão
totalmente saturada (uma dummy por trimestre × setor) rodada sobre dado já agregado por
célula tem grau de liberdade residual ZERO (bug real encontrado rodando pela primeira vez,
ver `docs/LIMITACOES_E_METODOLOGIA.md`). O RESUMO (um coeficiente só, tendência pré-lei e
DiD global) é uma regressão de verdade sobre o microdado, com erro-padrão clusterizado por
UPA — mesmo padrão de `pnadc_core.decomposicao_oaxaca_blinder`.

### Participação: nenhum efeito significativo, e a identificação FALHA pra Indígena

| Raça | Tendência pré-lei (pp/trim., p) | Tendências paralelas? | DiD (pp, p; p ajustado BH) |
|---|---|---|---|
| Negra | +0,124, p=0,08 | Sustentadas (limítrofe) | +0,075, p=0,82; p_BH=0,82 |
| Indígena | +0,009, p=0,046 | **NÃO sustentadas** | +0,039, p=0,07; p_BH=0,16 |
| Preta | +0,043, p=0,22 | Sustentadas | -0,060, p=0,72; p_BH=0,82 |
| Parda | +0,081, p=0,23 | Sustentadas | +0,135, p=0,66; p_BH=0,82 |

**Para Indígena, a identificação NÃO se sustenta** — a tendência pré-lei já era
significativamente diferente entre público e privado (p=0,046) antes da lei sequer existir.
Reportado como está: qualquer leitura do coeficiente de DiD pra Indígena nesse outcome não
é confiável, mesmo ele próprio não sendo significativo (p=0,07). Pra Negra, a tendência
pré-lei fica BEM perto do limiar de significância (p=0,08) — não reprovo o desenho pelo
critério formal (p ≥ 0,05), mas é uma tendência pré-existente forte o bastante pra tratar o
resultado nulo de Negra com o mesmo grau de cautela. Preta e Parda sustentam tendências
paralelas com folga, e também não têm DiD significativo. **Conclusão honesta: este desenho
não detecta mudança na COMPOSIÇÃO racial do setor público atribuível à lei**, dentro da
janela de ~3 anos observada.

![Participação de Negra no setor público](img/causal_eventstudy_participacao_negra.png)
![Participação de Indígena no setor público](img/causal_eventstudy_participacao_indigena.png)

### Hiato de renda: sinal exploratório, que não sobrevive à correção de multiplicidade

A tendência pré-lei não diverge (coef=-0,001 log-pontos por trimestre, p=0,65). O DiD global
(interação tripla tempo × setor × raça, em log-renda) dá **+0,024 log-pontos (~2,4%), com p
nominal de 0,014 e p ajustado (BH) de 0,072**. (Na população de referência, Onda 1; antes da troca
de população, com 14+ e todos os trabalhos, era +0,020, p = 0,041, p_BH = 0,164.) Depois do ajuste pelos 5 testes nacionais, não é
significativo; entre os 40 testes do Desenho B, nenhum é.

Direção do ponto estimado: o hiato de renda Branca-Negra DENTRO do setor público encolheu mais do
que no setor privado depois da lei. A curva ponto a ponto vai de um padrão ruidoso
positivo/misto antes da lei para um padrão em geral negativo depois. É uma descrição do ponto
estimado, não um efeito estabelecido.

![Hiato de renda Branca-Negra, setor público vs. privado](img/causal_eventstudy_hiato_renda.png)

**Leitura: exploratória.** O resultado é um candidato a hipótese para o B4b, não um achado. Quatro
ressalvas:

1. **Multiplicidade.** São 40 testes de DiD no Desenho B (5 nacionais + 35 de heterogeneidade),
   e não ~6, como dizia a versão anterior deste texto. Nenhum sobrevive ao FDR. Um p nominal de
   0,014 escolhido entre 40 testes tende, além disso, a superestimar o tamanho do efeito
   ("maldição do vencedor", *a confirmar: Gelman & Carlin, 2014*).
2. **Esfera de governo.** `setor_trabalho` não distingue federal de estadual/municipal, e só o
   federal foi atingido pela Lei 12.990/2014. A categoria "Público" mistura tratados e nunca
   tratados. Isso torna o coeficiente difícil de interpretar como efeito da lei, e não permite
   concluir que o efeito "real" isolado ao federal seria maior. Nenhuma variável já extraída
   separa a esfera (`setor_atividade`/VD4010 tem administração pública, mas também sem esfera).
3. **Curva pré-lei ruidosa.** Mesmo com a tendência LINEAR não significativa, a curva oscila
   entre -2,2 e +5,8 pp antes da lei. "Tendência linear não significativa" não é o mesmo que
   "série plana".
4. **Erro-padrão da curva.** A soma entre células ainda ignora covariâncias (limitação
   documentada no `CHANGELOG_METODOLOGICO.md`; reespecificação no B4b).

## 3. Heterogeneidade geográfica

O resultado nacional dos dois desenhos é majoritariamente nulo. Esta seção testa se esse
nulo é uniforme pelo país, quebrando por Região, área urbana/rural, e (só pro Desenho B)
Distrito Federal vs. resto do Brasil. Amostra checada antes de rodar: Negra fecha
`n_minimo` em toda região/área/DF nos dois desenhos; Indígena só fecha em Norte (vs. Resto
do Brasil, não as 5 regiões) e em área Urbana (Rural fica de fora, célula mais fina com
n=25, abaixo do mínimo de 30) — ver `docs/LIMITACOES_E_METODOLOGIA.md`.

### Desenho A por região/área

`did_cotas_universitarias_heterogeneidade.parquet`. A maioria dos recortes repete o nulo
nacional (nenhum DiD significativo em nenhuma região/área/raça), mas dois deles **falham
o teste de tendências paralelas** — a identificação não se sustenta nesses dois pontos
específicos, mesmo o nacional estando ok:

- **Negra, Região Norte**: tendência pré-2012 coef=-0,39 pp/ano, **p=0,025**.
- **Negra, área Rural**: tendência pré-2012 coef=-0,36 pp/ano, **p=0,000004** — falha bem
  mais forte que a do Norte.

Indígena (Norte vs. Resto do Brasil, e área Urbana) tem tendências paralelas sustentadas
nos três recortes, mas os DiDs são extremamente ruidosos (coeficientes de -5,7 a +5,3 pp,
todos não significativos) — esperado dado o tamanho de amostra, não uma novidade.

### Desenho B por região/área/DF

`did_cotas_servico_publico_heterogeneidade.parquet` +
`..._heterogeneidade_curvas.parquet`. Dois achados que pedem destaque:

- **Falhas de tendências paralelas na participação**: Negra no Nordeste (p=0,012), Parda
  no Nordeste (p=0,009) e Parda no Sul (p=0,004) — identificação não se sustenta nesses
  três pontos. (Com a população antiga o hiato de renda no Norte também falhava, p=0,049; na
  população de referência, p=0,096.) Todo o resto sustenta tendências paralelas.
- **Centro-Oeste: maiores pontos estimados, nada significativo após o ajuste.** No hiato de
  renda, o ponto estimado é **+6,0% (log-pontos), com p nominal 0,018 e p ajustado (BH) 0,191**;
  as tendências paralelas se sustentam (p=0,37). Na participação, dois DiDs do Centro-Oeste
  também passam do limiar nominal: **Negra, +1,71 pp, p nominal 0,021, p ajustado 0,191**; e
  **Parda, +1,83 pp, p nominal 0,011, p ajustado 0,191** (tendências pré-lei com p=0,13 e
  p=0,21). Na população de referência, 6 dos 35 testes de heterogeneidade têm p nominal < 0,05:
  os três do Centro-Oeste e mais três de hiato de renda — Sul (−5,3%, p=0,035, p_BH=0,234; sinal
  contrário), área urbana (+2,3%, p=0,022, p_BH=0,191) e Brasil sem o DF (+2,0%, p=0,040,
  p_BH=0,234). Isso pede investigação no B4b, mas não é evidência de efeito, porque nenhum
  sobrevive ao FDR. A versão anterior deste texto chamava o hiato do Centro-Oeste de "efeito
  mais forte e mais bem-identificado de toda a análise" e omitia os dois resultados de
  participação.
- **A hipótese do Distrito Federal NÃO se confirmou**. A ideia era usar o DF como
  aproximação parcial de "federal puro" (funcionalismo federal concentrado lá), esperando
  um efeito mais forte que a média nacional — o resultado saiu **praticamente zero**
  (hiato de renda: coef=-0,013, p=0,76; participação: p=0,26). Como o DF está DENTRO do
  Centro-Oeste, isso é um resultado contraintuitivo: o ponto estimado alto do Centro-Oeste (não
  significativo após o ajuste: p_BH=0,191) parece vir dos OUTROS três estados da região (Goiás,
  Mato Grosso, Mato Grosso do Sul), não do DF especificamente. Duas leituras possíveis, nenhuma confirmável
  com este dado: (a) o efeito da lei não está de fato concentrado onde o funcionalismo é
  mais federal, o que enfraqueceria a leitura "federal" do resultado nacional; ou (b) o
  mercado de trabalho do DF é atípico o bastante (salários e composição muito diferentes da
  média) pra não seguir o padrão regional mesmo se o mecanismo for real. **Não resolve a
  limitação de esfera de governo; se algo, complica a história simples** de que haveria um
  efeito "federal, só diluído".

## 4. Comparação com a literatura

O RDD usado por Mello (2022) e Francis-Tan & Tannuri-Pianto — comparando candidatos
aprovados por pouco pela cota com candidatos reprovados por pouco, dentro de uma
universidade e um ano específicos — é o desenho mais forte já publicado sobre cotas
raciais no Brasil, porque compara pessoas quase idênticas de cada lado de uma régua clara.
Este exercício não tenta competir com isso: é complementar. Ganha em representatividade
nacional e histórica (RDD fica restrito às universidades/anos com nota de corte disponível
publicamente; aqui é o país inteiro, todo o período 2012-2026). Perde em identificação
fina — o desenho por coorte agregada não sabe quem de fato passou pela cota, só quem
NASCEU numa janela que teve acesso a ela, e isso dilui qualquer efeito real na direção de
zero. Um resultado nulo aqui é compatível tanto com "não há efeito" quanto com "há efeito,
mas o desenho não tem poder pra detectá-lo" — a literatura de RDD é a referência pra
distinguir entre essas duas leituras, não este documento.

## O que isso NÃO prova

- **Não prova que a Lei de Cotas Universitárias não teve efeito educacional.** O desenho
  por coorte agregada tem baixo poder estatístico (19 pontos de coorte) e não identifica
  quem de fato usou a cota — um efeito real pode existir e não aparecer aqui.
- **Não prova que a Lei de Cotas no Serviço Público não mudou a composição racial do
  funcionalismo.** A janela observada (~3 anos pós-lei) pode ser curta demais pra uma
  mudança de composição que depende de rotatividade lenta (concursos, aposentadorias);
  o resultado nulo é sobre ESTA janela, não uma afirmação geral.
- **O sinal no hiato de renda do setor público (p nominal 0,014, p ajustado BH 0,072) NÃO é
  um efeito estabelecido nem uma estimativa do efeito da Lei 12.990/2014**: não sobrevive à
  correção de multiplicidade (0 de 40 testes sobrevivem) e mistura a esfera federal (tratada)
  com a estadual/municipal (não tratada).
- **Nenhum dos dois desenhos identifica o MECANISMO** pelo qual um efeito (quando
  detectado) ocorre — a extensão de mecanismo do Desenho A é correlacional, explicitamente.
- **Nada aqui substitui o RDD da literatura** como estimativa de referência do efeito
  causal das cotas universitárias — ver seção 4.
- **"Tendências paralelas sustentadas" é uma leitura de PODER ESTATÍSTICO insuficiente
  pra REJEITAR a suposição, não uma prova de que a suposição é verdadeira** — com poucos
  pontos de coorte/trimestre, um teste pouco potente pode simplesmente não conseguir
  detectar uma divergência real que existe.
- **O resultado nulo do teste do Distrito Federal (seção 3) NÃO refuta a hipótese
  "federal" do resultado nacional** — é um teste de baixo poder (amostra de Indígena no DF
  é praticamente inexistente; mesmo pra Negra, o DF sozinho é uma fração pequena da
  amostra nacional) e um resultado atípico de UMA unidade geográfica específica. Ele
  complica a leitura simples, mas não decide a questão num sentido ou no outro.
