# Plano de análise — Desigualdade racial de renda no Brasil

**Versão 1.0 · 12/10/2026 · VALIDADO pelo Felipe (com as decisões abaixo)**
**Escopo:** renda do trabalho (raça e raça × gênero). Educação aparece como causa e como objeto (Bloco E). Origem social e mobilidade (Bloco H) entra **no escopo atual**, junto com E. Saúde, habitação e violência ficam para temporadas futuras.
**Referências bibliográficas citadas de memória: confirmar antes de usar em texto público.**

### Decisões de definição (12/10/2026)

| Tema | Decisão | Consequência |
|---|---|---|
| Renda de referência (F2) | **Rendimento habitual do trabalho principal** (`VD4016`/equivalente a confirmar no dicionário; o Hub hoje usa `VD4019`, que é o habitual de todos os trabalhos: **confirmar qual é qual antes de mudar**) | Se o Hub hoje usa "todos os trabalhos", a regeneração muda o estimando. Reportar a diferença entre as duas definições (Bloco F) |
| População de referência (F3) | **Ocupados com renda do trabalho principal > 0, 18 anos ou mais** (decidido no Ponto de parada 0, 12/10/2026; substitui "25–64 a confirmar"). **14+** (o recorte histórico do Hub) fica como teste de sensibilidade | Todo resultado dos Blocos A–D vale para essa população e declara isso na legenda |
| Quem fica de fora | Não ocupados; ocupados sem rendimento (ex.: trabalhador familiar auxiliar); rendimento zero | **Bloco S** mede quanto essa exclusão importa; **Bloco T** repete a análise com a população inteira |
| Educação × decomposição | Educação (E) **depois** da decomposição (D) | Onda 3 = D; Onda 4 = E + H |
| Dados administrativos | **Incluídos** no escopo (INEP, RAIS, Painel de Pessoal) | Entram nas Ondas 4 e 5; acesso a confirmar |
| Origem social e mobilidade (H) | **Entra agora**, não "fase posterior" | Onda 4, junto com E (compartilham a ligação filhos–pais) |
| Licença | Código **MIT**; dados derivados e textos **CC BY 4.0** | Fase 2 do prompt |

**Decisões do Ponto de parada 0 (12/10/2026)** — ver `docs/auditoria/fase0_relatorio.md` §9:
1. Faixa etária de referência: **18+**; 14+ como sensibilidade. Os Blocos S e T usam "todos com 18+" no lugar de "todos 25–64".
2. EP por **linearização de Taylor (Estrato/UPA)**; pesos replicados não extraídos por ora (extratores aceitam `--pesos-replicados`).
3. Extração v2 trimestral com horas do trabalho principal (`V4039`), variáveis escolares e de trabalho principal (`data/raw/pnadc_extraido_v2`).
4. Extração v2 anual: renda domiciliar (`VD5*`), fontes (`V500*A`), educação e trabalho; Visita 1 2012–2019 e 2022–2025, **Visita 5 para 2020–2021**.
5. **Sem vínculo institucional:** RAIS identificada e SEDAP/INEP ficam **fora de alcance**. G1/E6 só com dados públicos simplificados do INEP (sem raça por aluno); D3.5/D8.2 (dentro da firma) só com literatura.
6. Módulo de habitação versionado: o extrator anual é base de P5/Bloco T e `S01017` alimenta o H3.1.
7. CI em **Python 3.12**.

**Decisões do Ponto de parada 1 (13/10/2026):**
1. PRs das Fases 0 e 1 aprovados.
2. Gráficos: regenerar **uma vez só**, depois da troca de população/renda de referência (Fase 2).
3. Família do FDR: **padrão = comparações de uma tabela no mesmo período e na mesma abertura**
   (piso das tabelas descritivas); cada ficha de estudo declara a sua família conforme a pergunta;
   tendências usam HAC, não FDR sobre trimestres (`src/inference/multiplicidade.py`).

**Decisões do Ponto de parada 2 (13/10/2026; "pode seguir" aceitou as recomendações):**
1. PR da Fase 2 aprovado.
2. Regenerar com a população/renda de referência **uma vez só, na Onda 1**, junto com a ficha do
   Bloco F, o relatório antes × depois e os gráficos. Até lá o pipeline não roda para publicação.
3. Nessa regeneração, **todas** as tabelas de hiato migram para a população de referência (o Hub não
   fica com duas populações).
4. Theil e Gini passam a incluir **Amarela** no total (A4).

**Decisões do Ponto de parada 3 (13/10/2026; "sim" para as quatro recomendações da Rodada 2):**
1. Corrigir o E6 e regenerar **só** `decomposicao_raca_genero` (feito na Fase 3b).
2. Regra de supressão: n < 30 **ou** CV > 30% ⇒ não publica (fecha o ponto aberto 4).
3. Heaping nos limiares de quantil: repartir o peso dos empatados para cada fatia somar exatamente 10%/25%.
4. Carteira assinada = só CLT, com categoria própria para estatutário/militar.
Os itens 2–4 entram no código já, mas só valem na regeneração única da Onda 1.

**Complemento (13/10/2026, após o PR da Fase 3b):** Ignorado fica **sempre** fora do universo;
Amarela entra também no escopo `genero` de `extremos`; denominador de `pct_estatutario_militar` =
empregados 01–07 (aceito). **As análises principais do Hub são sempre Branca × Negra e Indígena**;
Amarela aparece quando entra no universo, sem ser foco.

**Decisões da Onda 1 (13/10/2026):**
1. A faixa 14–17 continua com renda nas tabelas com dimensão de faixa etária, **fora das análises** (que usam 18+).
2. Pelo critério do S1 (P4/P5 mudam o hiato de forma "grande", sobretudo para mulheres), **o Bloco T passa a eixo
   principal** (decisão delegada pelo Felipe a Claude): todo hiato de renda do trabalho (P1) é publicado ao lado do
   hiato de todos os adultos (P4) e/ou da renda domiciliar per capita (T1).

---

## 0. Como ler este plano

### 0.1 O princípio que organiza tudo

"Por quê?" tem três respostas de natureza diferente, e misturá-las é o erro mais comum do campo:

| Nível | Pergunta que responde | O que a PNAD sozinha consegue | Rótulo |
|---|---|---|---|
| **D** — Descrição | Quanto? Onde? Quando? | Sim, com rigor | `D` |
| **C** — Contabilidade | Quanto do hiato está *associado* a diferenças em X? | Sim (decomposições), sem causalidade | `C` |
| **Q** — Quase-experimento | O que mudou *por causa de* uma política/choque? | Raramente; melhor com dado administrativo | `Q` |
| **M** — Mecanismo | *Por que* X difere entre grupos (discriminação, rede, território, herança)? | **Não.** Exige outra fonte, desenho experimental ou literatura | `M` |

**Regra editorial e científica:** o Hub responde `D` e `C` com seus dados. Nas perguntas `M`, o Hub *organiza evidência externa* (estudos de auditoria, dados administrativos, literatura) e diz com clareza o que não consegue ver. Nenhuma conclusão `M` sai de uma decomposição `C`.

### 0.2 Ficha mínima de cada pergunta

Toda pergunta que virar estudo recebe: **estimando** (o que exatamente se mede) · **população** · **método** · **dados** · **hipóteses concorrentes** · **o que refutaria** · **armadilhas** · **estado de publicação** (Aprovado / Aprovado com ressalvas / Bloqueado).

### 0.3 Lentes teóricas (o que dá sentido às decomposições)

Cada bloco declara qual teoria está testando, para não decompor sem pergunta:

- **Capital humano** (Becker/Mincer): a diferença é de qualificação → Bloco D2.
- **Discriminação** (taste-based, estatística) e **segregação ocupacional**: diferença de tratamento em contratação, promoção e salário → D3, D5.
- **Estratificação e acúmulo de desvantagens** (Tilly, *Durable Inequality*; DiPrete & Eirich; Merton): desvantagem cedo se acumula ao longo do ciclo de vida → Blocos E e H.
- **Racismo estrutural / institucional**: o processo gera desigualdade sem agente discriminador identificável → Blocos E, D4, G.
- **Interseccionalidade** (Crenshaw): efeitos não aditivos de raça e gênero → Bloco C.
- **Tradição brasileira**: Hasenbalg (*Discriminação e Desigualdades Raciais no Brasil*, 1979), Silva, Telles (*Race in Another America*, 2004), Osorio, Soares, Campante/Crespo/Leite (Brasil, discriminação). *Confirmar.*

---

## Bloco F — Fundações (antes de qualquer número)

Sem isso, todo bloco abaixo é frágil. Vale 1–2 semanas e vira a camada "metodologia" que acompanha tudo.

| ID | Pergunta | Tipo | Observação |
|---|---|---|---|
| F1 | **Quem é "Negra", "Branca", "Indígena", "Amarela"?** Como a composição declarada mudou 2012–2026 (reclassificação de pardos, Censo 2022)? | D | Autodeclaração é fluida. A mudança de composição altera a *média do grupo* sem mudar ninguém: separar efeito de composição de efeito de renda. |
| F2 | **Qual é o conceito de renda?** **Decidido:** rendimento habitual do trabalho principal. Documentar as demais (todos os trabalhos, todas as fontes, por hora, domiciliar per capita) e **quando cada uma é usada** | D | Tabela de sensibilidade: o hiato A2 sob cada conceito, com IC. Confirmar no dicionário qual variável é "trabalho principal" e qual é "todos os trabalhos" e o que o Hub usa hoje |
| F3 | **Quem entra na população?** **Decidido:** ocupados com rendimento do trabalho principal > 0 | D | Gini e Theil na mesma população (resolve E3/R1). Exclusões medidas no Bloco S |
| F4 | **Quanto da renda está medida?** Subdeclaração, *heaping* em valores redondos, topo (PNAD tende a subestimar o topo) | D | Afeta Gini, topo 10%, razão P90/P10. |
| F5 | **Incerteza correta:** variância *design-based* (Estrato/UPA), pesos replicados se existirem, correção de multiplicidade | — | É o B1 da auditoria. |
| F6 | **Quebras de série:** reponderação pós-Censo 2022, coleta por telefone 2020–21, recessão 2015–16, salário mínimo | D | Cada quebra precisa de marca no gráfico e de teste de sensibilidade. |

**Entregável do Bloco F:** documento de definições (um por conceito) + tabela de sensibilidade "como o hiato muda conforme cada escolha F2/F3". Isso por si só é um resultado publicável: *"o hiato é X% a Y%, dependendo de como você mede"*.

---

## Bloco A — A diferença existe? De quanto é?

**Lente:** descrição pura. Qualquer leitor de revista precisa disso antes de qualquer "por quê".

| ID | Pergunta | Tipo | Método | Armadilhas |
|---|---|---|---|---|
| A1 | Existe diferença de renda entre Brancos e Negros? | D | Diferença de médias/medianas com IC *design-based* | Já é "sim"; a pergunta interessante é de quanto e onde |
| A2 | De quanto? Em R$, em razão, em log-pontos, em "Negro ganha X% do que Branco ganha" | D | Quatro métricas lado a lado | Hiato % hoje é relativo à renda Negra (C1 da auditoria): escolher e rotular |
| A3 | **Onde na distribuição?** Hiato por quantil (P10…P99), teto de vidro, piso pegajoso | D/C | Quantis incondicionais; razões P90/P50, P50/P10 | Médias escondem a história; a distribuição é a história |
| A4 | **Quanto da desigualdade total é entre raças?** | D | Theil T e L (MLD) entre/dentro; Gini | Theil ≈ 7% ≠ "só 7% é racial" (regra do projeto). Incluir sempre o par de contexto |
| A5 | **Probabilidade de estar no topo/na base** por raça; sobre-/sub-representação | D | Razão de chances; índice de representação por décimo | Limiar em R$ vs. limiar por percentil dão populações diferentes |
| A6 | **Dominância estocástica:** a distribuição Branca está acima da Negra em *todos* os pontos? | D | CDFs, teste de dominância de 1ª ordem | Resultado forte e pouco usado; a resposta pode ter exceções |
| A7 | Mesmo diferença com **renda por hora** e **renda domiciliar per capita**? | D | Repetir A2–A4 | Hora corrige jornada; per capita corrige composição familiar. Podem mudar a história |

**Já existe no Hub:** A1, A2, A3 (parcial), A4, A5 (parcial). **Novo:** A6, A7, métricas de A2 padronizadas.

---

## Bloco B — Está aumentando ou diminuindo? Em que ritmo?

**Lente:** desigualdade como processo no tempo. É onde o dado mais engana.

| ID | Pergunta | Tipo | Método | Armadilhas |
|---|---|---|---|---|
| B1 | Qual a tendência 2012–2026 do hiato? Em que ritmo (p.p./ano; log-pontos/ano)? | D | Regressão de tendência com EP robusto a autocorrelação (HAC) e quebras estruturais | 58 trimestres não são 58 evidências independentes (rotação dos domicílios) |
| B2 | A tendência é **efeito de composição ou de renda**? (A composição racial e educacional mudou) | C | Decomposição no tempo: Kitagawa–Oaxaca–Blinder; Juhn-Murphy-Pierce; RIF no tempo | Reclassificação racial (F1) pode fabricar "convergência" |
| B3 | A convergência ocorre em todos os quantis? | D/C | RIF/quantis por ano | Convergência no meio e divergência no topo é um achado clássico |
| B4 | **Coortes:** os jovens de hoje têm hiato menor que seus pais na mesma idade? | D | Análise de coorte sintética (pseudo-painel) com idade × período × coorte | O problema APC (idade-período-coorte) não é identificável sem restrição. Declarar a restrição |
| B5 | Quanto da variação é **ciclo** (recessão 2015–16, pandemia) e quanto é tendência? | D | Filtro/modelo com termos de ciclo; comparação de episódios | A pandemia mudou *quem* aparece na amostra (seleção) |
| B6 | O ritmo atual leva a que a paridade seja alcançada em que ano? | D | **Projeção condicional explícita** | Extrapolação linear é apenas ilustração. Nunca publicar "em 2090 haverá igualdade" sem as premissas na tela |

**Já existe:** série do hiato (B1 parcial, sem HAC), Theil no tempo, coortes de superior completo. **Novo:** B2, B3, B4 formal, B5, B6.

---

## Bloco C — Raça × gênero (interseccionalidade)

**Lente:** raça e gênero **não são aditivos**. A pergunta central é a interação.

| ID | Pergunta | Tipo | Método | Armadilhas |
|---|---|---|---|---|
| C1 | Quatro células (homem Branco, mulher Branca, homem Negro, mulher Negra): ranking e hiatos | D | A2–A4 por célula | Mulher Negra não é "soma" de dois hiatos |
| C2 | **O hiato de gênero é igual dentro de cada raça?** O hiato racial é igual dentro de cada gênero? | D/C | Modelo com interação; decomposição por célula | Efeitos de interação precisam de n suficiente (Indígena) |
| C3 | Quanto da desvantagem da mulher Negra é "raça", "gênero" e "interação"? | C | Decomposição de 3 vias (Shapley/Shorrocks) em vez de sequencial | A ordem muda o resultado em decomposição sequencial |
| C4 | **Penalidade da maternidade** por raça: efeito de ter filhos pequenos na renda e na participação | C/D | Comparação com/sem filhos, por coorte etária; event-study de nascimento só com painel (limitado) | PNAD não tem painel longo: usar coortes de idade com cautela |
| C5 | **Trabalho de cuidado e doméstico remunerado:** peso do emprego doméstico na ocupação feminina Negra e seu hiato | D | Participação e renda por posição na ocupação | Informalidade e subdeclaração |
| C6 | Estado conjugal/chefia do domicílio: efeito sobre a renda e sobre a oferta de trabalho | C | Controles na decomposição | Endogeneidade forte (casar/ter filhos é escolha condicionada) |

**Já existe:** raça × gênero em `ANALISE_RACA_GENERO.md` (auditado na Onda 2: números de renda conferidos pelo C1/C3; a "interação" da `decomposicao_raca_genero` é −DiD em R$ e uma ordem sequencial, reconciliada com Shapley no C3; ritmo de convergência refeito no B1). **Feito na Onda 2:** C1–C6 (fichas em `docs/studies`).

---

## Bloco S — Seleção: o recorte "ocupados com renda" distorce o hiato?

**Lente:** a população de referência (F3) é ocupados com renda do trabalho principal > 0. Se a *entrada* nessa população difere por raça e gênero, o hiato medido nela mistura "quanto ganha" com "quem consegue estar aqui". Este bloco responde **quanto o recorte importa**, e é o **primeiro a rodar na Onda 1**, porque valida (ou não) a decisão F3.

### S0. Quem fica de fora?

| ID | Pergunta | Tipo | Método |
|---|---|---|---|
| S0.1 | Composição da população total 18+ em: (a) ocupados com renda > 0; (b) ocupados sem rendimento / rendimento zero (ex.: trabalhador familiar auxiliar); (c) desocupados; (d) fora da força de trabalho (desalento, cuidados, estudo) | D | Tabela por raça, gênero e raça × gênero; evolução 2012–2026 |
| S0.2 | A probabilidade de estar em (a) difere por raça e por raça × gênero, controlando por idade, escolaridade e região? | C | Logit/probit ponderado, efeitos marginais, IC *design-based* |
| S0.3 | Entre quem está fora de (a), as características diferem entre os grupos (escolaridade, idade, filhos pequenos, chefia)? | D | Perfis comparados |

### S1. O hiato muda quando mudamos a população? (teste explícito pedido pelo Felipe)

Calcular o hiato Branca–Negra e os hiatos de raça × gênero em **cinco populações**, com a mesma renda de referência quando aplicável:

| População | Renda usada | Pergunta que responde |
|---|---|---|
| P1 — ocupados com renda > 0 (**referência**) | trabalho principal | Linha de base |
| P2 — ocupados (incluindo sem rendimento, renda = 0) | trabalho principal | Efeito de excluir os sem rendimento |
| P3 — ocupados com renda > 0 | **todos os trabalhos** | Efeito do conceito de renda (F2) |
| P4 — todos 18+ (não ocupados = 0) | trabalho principal | Hiato "extensivo": inclui quem não consegue entrar |
| P5 — todos 18+ | **renda domiciliar per capita** (todas as fontes) | Hiato de bem-estar material (Bloco T) |

**Critério pré-definido de "diferença grande"** (convenção do plano, não regra universal): o hiato em P2/P4 é considerado materialmente diferente do de P1 se a diferença for **maior que 10% em termos relativos *e* maior que o IC95% combinado** da diferença. Reportar a diferença, o IC e a decisão, sem arredondar a favor de nenhuma narrativa. Se a diferença for grande, o Bloco T deixa de ser opcional e vira eixo principal.

Fazer o teste: por raça (Branca × Negra, e também Preta × Parda × Indígena × Amarela quando a amostra permitir, com nota de amostra) e por raça × gênero (4 células), **no tempo** (série 2012–2026), e por quantil (o efeito de seleção pode estar só na base).

| ID | Pergunta | Tipo | Método | Armadilhas |
|---|---|---|---|---|
| S1.1 | O hiato racial é diferente em P1, P2, P3, P4, P5? De quanto? | D | Hiatos comparados com IC e critério acima | Em P4 o "zero" dos não ocupados é uma convenção forte; ler junto com S1.3 |
| S1.2 | Idem para raça × gênero | D | Idem | O efeito de seleção costuma ser maior para mulheres Negras (hipótese, não achado) |
| S1.3 | Limites (bounds) do hiato sob suposições explícitas sobre os não observados | C | Limites de Manski; Lee bounds *(a confirmar)* | Heckman só com variável de exclusão crível; usar limites, não correção pontual |
| S1.4 | Margem intensiva (horas) vs. extensiva (emprego) | C | Decomposição em Pr(emprego) × horas × renda por hora | |
| S1.5 | A seleção mudou no tempo (recessão 2015–16, pandemia)? | D | Série de S0.1 e S1.1 | Pandemia: coleta por telefone e saída de trabalhadores informais |

**Regra:** tudo nos Blocos A–D vale para P1 e diz isso. Toda afirmação do tipo "o hiato é X" carrega "entre ocupados com renda do trabalho principal".

---

## Bloco T — Panorama da população inteira

**Lente:** o que acontece com quem não está em P1? Este bloco usa **todos**, com conceitos de renda que existem para todos. Roda na Onda 1 em versão curta (T1–T3); expande se S1 mostrar diferença grande.

| ID | Pergunta | Tipo | Método | Armadilhas |
|---|---|---|---|---|
| T1 | Renda domiciliar per capita por raça e por raça × gênero do responsável | D | Médias, quantis, Gini, Theil (população: todas as pessoas) | A unidade é o domicílio; compartilhar renda entre membros altera a leitura individual |
| T2 | Pobreza e extrema pobreza por raça (linhas de referência a documentar) | D | Taxas, intensidade (FGT) | Linhas de pobreza são convenções; mostrar mais de uma |
| T3 | Dependência de renda de outras fontes (transferências, aposentadoria) por raça | D | Composição da renda por fonte | PNADC mede transferências com erro (subdeclaração) |
| T4 | Distribuição da população por faixa de renda domiciliar per capita | D | Décimos/quintos por raça | |
| T5 | O hiato de P5 "conta a mesma história" do hiato de P1? | C | Comparar com S1.1 | |

---

## Bloco D — Por que a diferença existe? (decomposição `C`; mecanismos `M`)

**População e renda:** ocupados com renda do trabalho principal > 0 (F2/F3); toda tabela do bloco declara isso e, quando S1 mostrar diferença material, reporta também P2/P4.
**Esta é a parte da qual Felipe deu o exemplo.** Estrutura em árvore. Cada nó tem duas colunas: *o que o Hub responde* (`C`) e *o que exige fonte externa* (`M`).

### D1. Quanto do hiato é "explicado" por diferenças observáveis?

| Questão | Método | Detalhe |
|---|---|---|
| D1.1 Qual fração do hiato (em log-renda) desaparece ao comparar pessoas com mesma idade, escolaridade, ocupação, região, jornada, informalidade, sexo? | Oaxaca-Blinder (Reimers) **em especificações aninhadas** (6–8) | Mostra *como o "resíduo" muda* a cada bloco: é o resultado, não um número único |
| D1.2 Quanto cada bloco contribui, sem depender da ordem? | **Decomposição de Gelbach (2016) / Shapley-Shorrocks** | Resolve a dependência de ordem da decomposição sequencial |
| D1.3 A decomposição vale em todos os quantis? | RIF-OB (Firpo-Fortin-Lemieux) com sensibilidade a banda | O "peso da educação" no P10 ≠ no P90 |
| D1.4 O resultado é robusto a variáveis omitidas? | Sensibilidade de Oster (δ), Cinelli-Hazlett | Quantifica *quão forte* uma omissão teria que ser para anular a conclusão |

**Regra de rotulagem:** "resíduo" = *parte do hiato não associada às covariáveis incluídas*. **Nunca** "discriminação" nem "cor da pele" (regra R5 da auditoria).

### D2. Quanto vem da diferença de educação? (e por que a educação difere → Bloco E)

| Questão | Tipo | Método |
|---|---|---|
| D2.1 Quanto do hiato é associado a diferença de **anos/nível** de estudo? | C | Contribuição de educação em D1.2 |
| D2.2 O **retorno** da escolaridade é igual por raça? (mesma educação, renda diferente?) | C | Interações raça × nível; Blau-Kahn "efeito preço" |
| D2.3 Diferença nos retornos por **nível** (médio, técnico, superior) e por **quantil** | C | RIF por nível |
| D2.4 **Sobrequalificação:** mesmo diploma, ocupação de menor nível? | C/D | Índice de correspondência educação-ocupação |
| D2.5 Por que a educação difere? | **→ Bloco E** | |

### D3. Quanto vem da diferença de ocupação?

| Questão | Tipo | Método |
|---|---|---|
| D3.1 Quanto do hiato é associado a **onde** cada grupo está (grandes grupos, setores, posição na ocupação)? | C | Contribuição de ocupação em D1.2 |
| D3.2 Quão segregados são os grupos entre ocupações? Evolução no tempo | D | Índices de Duncan e de entropia |
| D3.3 **Dentro da mesma ocupação**, quanto é o hiato? (efeito "dentro") | C | OB com FE de ocupação detalhada (CBO 4 dígitos) |
| D3.4 Ocupação é causa ou **mediadora**? | Conceitual | Dois conjuntos de controles: com e sem ocupação. Dizer em voz alta que ocupação é mediador de educação e de discriminação |
| D3.5 Por que as ocupações diferem? ("escolha" de ocupação) | **M** | Ver abaixo |

**Nota sobre "escolha":** o termo carrega uma hipótese. Reformular como *"alocação"* ou *"entrada"* em ocupações. O que a literatura distingue: (a) restrição de qualificação, (b) discriminação na contratação/promoção, (c) redes e informação, (d) preferências e expectativas moldadas por contexto, (e) restrição espacial (onde moram × onde há emprego). O Hub só mostra *quanto* se associa a cada; separar (b) de (c) de (d) exige:
- **Experimentos de campo e de auditoria** (currículos com nomes/fotos) — literatura externa.
- **Dados administrativos com firma** (RAIS identificada): decomposição entre-firma × dentro-da-firma (Card-Heining-Kline). *Verificar acesso à RAIS identificada.*
- **Dado de redes/indicação:** raramente disponível.

### D4. Território e composição regional

| Questão | Tipo | Método |
|---|---|---|
| D4.1 Quanto do hiato nacional é **efeito de composição regional** (negros concentrados em regiões mais pobres)? | C | Decomposição entre-região × dentro-da-região (inclui o paradoxo de Simpson) |
| D4.2 O hiato dentro de cada região/UF/metrópole | D | Hiato por UF com EP *design-based* e correção de multiplicidade |
| D4.3 Capital × interior; metrópole × resto | D | Interação com `V1022`/capital |
| D4.4 Segregação residencial e acesso a emprego | **M** | Exige Censo 2022 (bloqueado) |

### D5. Jornada, informalidade, setor, vínculo

| Questão | Tipo | Método |
|---|---|---|
| D5.1 Quanto vem de **horas trabalhadas**? (`VD4031` já extraída) | C | Renda por hora; contribuição das horas em D1.2 |
| D5.2 Quanto vem de **informalidade** e de **conta própria** vs. empregado? | C | Contribuição de posição/formalidade |
| D5.3 Qual a **probabilidade** de cada grupo estar em cada posição, condicional a educação? | C | Logit multinomial, DFL |
| D5.4 Por que a informalidade difere? | **M** | Literatura + RAIS/CAGED |

### D6. Idade, experiência, coorte

| Questão | Tipo | Método |
|---|---|---|
| D6.1 Trajetórias de renda por idade e raça (perfil idade-renda) | D | Perfis por coorte sintética |
| D6.2 O hiato **cresce com a idade** (acúmulo) ou é estável? | D/C | Hiato por faixa etária e coorte |

### D7. Família e ciclo de vida

| Questão | Tipo | Método |
|---|---|---|
| D7.1 Chefia feminina, filhos, arranjo familiar e renda | C | Entra em C4–C6 |

### D8. O resíduo

| Questão | Método |
|---|---|
| D8.1 Qual é a faixa plausível do resíduo, dado o que não observamos? | Intervalos de Oster/Cinelli-Hazlett |
| D8.2 Há outro dado em que podemos medir o resíduo de outro modo? | Estudos de auditoria; RAIS identificada (comparação dentro da mesma firma e função) |
| D8.3 **O que concluímos?** | "Resíduo robusto não é prova de discriminação: é a parte que as covariáveis incluídas não capturam. Quatro hipóteses concorrentes: discriminação, qualidade diferente da educação, variáveis omitidas (rede, origem), erros de medida" |

---

## Bloco E — De onde vêm as diferenças de educação?

**Lente:** estratificação e acúmulo de desvantagens. É aqui que a pergunta "por que" começa a pesar, porque educação é o grande mediador.

Usa variáveis que **ainda não estão extraídas** (frequência escolar, atraso idade-série). *Confirmar no dicionário.*

| ID | Pergunta | Tipo | Método | Dados |
|---|---|---|---|---|
| E1 | Em **qual idade/transição** o hiato educacional aparece? | D | Frequência escolar por idade simples (0–29) por raça; conclusão EF/EM/ES por coorte | PNADC: frequência, nível, `V3002`, `V3003A` |
| E2 | Há diferença de **acesso** (matrícula) ou de **permanência** (evasão) ou de **progressão** (reprovação/distorção)? | D | Funil: matrícula → frequência → conclusão, por raça | PNADC; Censo Escolar INEP (confirmar o que traz sobre raça) |
| E3 | **Qualidade**: aprendizado difere (ou só anos de escola)? | D | Proficiência por raça controlada por NSE (indicador de nível socioeconômico) | **SAEB** (microdados INEP) |
| E4 | **Tipo de escola** (pública/privada, federal, tempo integral): quem acessa? | D | Distribuição por tipo de escola | Censo Escolar, SAEB |
| E5 | **Origem familiar:** quanto da diferença está associada à escolaridade dos pais, renda domiciliar, composição familiar? | C | Para quem vive com os pais: associação entre escolaridade dos pais e dos filhos, por raça | PNADC (corresidência — seleção); POF. **Declarar o viés de corresidência** |
| E6 | **Ensino superior:** acesso, ingresso por modalidade (ampla concorrência, cota), evasão, conclusão | D/Q | Censo da Educação Superior (INEP), ENADE | **Muito melhor que a PNADC para cotas** |
| E7 | **Território:** escola e infraestrutura por município/bairro | D | Censo Escolar + território | Censo 2022 se disponível |
| E8 | **Efeito do tempo escolar nos retornos:** educação a mais *gera* renda ou só sinaliza? | **M** | Literatura (retornos causais com IV/discontinuidades) | Externo |

**Mecanismos a mapear (cada um com evidência externa, se existir):** pobreza e trabalho infantil · violência escolar · expectativas docentes · discriminação em sala · distância e transporte · qualidade da escola do bairro · currículo (Lei 10.639) · política de acesso (cotas, ProUni, FIES, REUNI).

---

## Bloco G — Políticas e causalidade

**Princípio:** onde existe dado administrativo com raça, ele é melhor que a PNADC para avaliar política. A PNADC só entra como pano de fundo populacional.

| ID | Pergunta | Tipo | Desenho recomendado | Dados | Observação |
|---|---|---|---|---|---|
| G1 | **Lei 12.711 (cotas)** aumentou o ingresso de estudantes Negros em instituições federais? | Q | DiD moderno com adoção escalonada (Callaway-Sant'Anna, Sun-Abraham) *confirmar*; ou descontinuidade onde houver nota de corte | **Censo da Educação Superior (INEP)** por instituição/ano; SiSU | O desenho atual com coortes da PNADC é fraco (R2 da auditoria) |
| G2 | O ingresso por cota gerou **mais conclusão e renda** depois? | Q | Seguimento de coortes de ingressantes | ENADE, PNADC por coorte, RAIS | Longo prazo; coortes tratadas só entram no mercado a partir de ~2017 |
| G3 | **Lei 12.990** (reserva de 20% em concursos federais) mudou a composição racial do funcionalismo federal? | Q | Event-study com dado do servidor federal (cadastro de pessoal) | SIAPE/Painel Estatístico de Pessoal (confirmar raça/cor e acesso) | A PNADC não identifica servidor federal; melhor dado administrativo |
| G4 | O **salário mínimo** (valorização 2005–2014) comprimiu o hiato? | Q | Variação regional de exposição (Bite index) | PNADC + valor do mínimo | Hipótese fraca de identificação: apresentar como `C` |
| G5 | Programas de transferência e o hiato educacional/de renda | Q | — | CadÚnico (acesso restrito) | Provavelmente fora de escopo |
| G6 | Poder estatístico: qual efeito mínimo detectável cada desenho tem? | Pré-requisito | Cálculo prévio (MDE) | — | Se o EMD for maior que efeitos plausíveis, **não rodar** e dizer isso |

**Regras de comunicação:** "efeito não detectado" ≠ "cotas não funcionam"; todo resultado causal carrega IC, EMD e pré-registro do desenho.

---

## Bloco H — Origem social, mobilidade e patrimônio (no escopo atual; Onda 4, junto com E)

**Lente:** acúmulo de desvantagens e transmissão intergeracional (Tilly; DiPrete & Eirich; literatura de mobilidade, *confirmar autores brasileiros*). Responde parte do "por quê" que o Bloco D não alcança: **parte do hiato de hoje já estava dada na origem**. É também o limite da PNADC: ela mede o presente, e a origem só aparece de forma indireta.

**Restrição de dados central:** a PNADC não pergunta a escolaridade nem a ocupação dos pais. Só é possível vincular pais e filhos **quando moram juntos** (relação de parentesco com o responsável do domicílio). Isso gera **viés de corresidência** (quem sai de casa mais cedo, ou perde contato, não entra), e o viés pode diferir por raça. Todo resultado do bloco precisa declarar isso. Verificar na Fase 0 se existe algum módulo de mobilidade social em edições da PNAD/PNADC (a confirmar).

### H1. Transmissão educacional

| ID | Pergunta | Tipo | Método | Armadilhas |
|---|---|---|---|---|
| H1.1 | Entre jovens (18–29) que moram com os pais, quanto a escolaridade dos pais prediz a deles, por raça? | C | Matriz de transição pais→filhos; associação (elasticidade, correlação, razão de chances) | Corresidência seleciona; jovens ainda estudando entram incompletos |
| H1.2 | **Mobilidade educacional ascendente:** qual a probabilidade de ultrapassar a escolaridade dos pais, por raça (e raça × gênero)? | C | Probabilidade de mobilidade ascendente/descendente/imobilidade | Teto: pais com superior não têm como "subir" |
| H1.3 | A associação pais→filhos é **igual** por raça (mesmo ponto de partida, mesmo ponto de chegada)? | C | Interação raça × escolaridade dos pais | Pais negros têm menos escolaridade em média: comparar na mesma origem |
| H1.4 | Mudou entre coortes (a transmissão está enfraquecendo)? | D | Coortes de nascimento sintéticas | Reforça o problema APC (ver B4) |

### H2. Transmissão e origem na renda

| ID | Pergunta | Tipo | Método | Armadilhas |
|---|---|---|---|---|
| H2.1 | **Mesma origem, destinos iguais?** Entre filhos de pais com a mesma escolaridade, o hiato racial de renda persiste? | C | OB com escolaridade dos pais como controle (para a subamostra corresidente); comparar o resíduo com o de D1 | Subamostra selecionada; não generalizar para toda a população |
| H2.2 | Quanto do hiato de D1 **diminui** ao controlar pela origem? | C | Resíduo antes/depois do controle de origem | Se não diminui, a origem observada não explica o resíduo; se diminui, parte do "resíduo" era herança |
| H2.3 | **Renda domiciliar de origem** (renda dos pais quando se vê o jovem em casa) × renda individual atual | C | Elasticidade intergeracional *proxy* | A renda do jovem em casa não é a renda dos pais "na infância" |
| H2.4 | Cada raça tem a mesma **probabilidade de chegar ao topo** partindo da base? | C | Matriz de transição por décimo de renda dos pais (quando a renda dos pais é observável) | Muito sensível à amostra e ao viés de corresidência |

### H3. Patrimônio e riqueza (o ponto cego)

| ID | Pergunta | Tipo | Fonte | Observação |
|---|---|---|---|---|
| H3.1 | Casa própria e condição de ocupação do domicílio por raça | D | PNADC (variável de condição do domicílio, a confirmar), Censo 2022 (bloqueado) | Proxy fraca de patrimônio |
| H3.2 | Posse de bens duráveis e ativos | D | POF (microdados IBGE) | A POF amostra menos que a PNADC; limites de desagregação |
| H3.3 | Renda de capital/aluguel/aposentadoria por raça | D | PNADC (rendimentos de outras fontes) | Subdeclaração conhecida |
| H3.4 | Riqueza: qual o tamanho da lacuna, com intervalo? | D | POF; estudos externos; RAIS/IR (não acessível) | **Limite assumido:** com dados públicos só dá proxy. Dizer explicitamente que a lacuna de riqueza é maior que o de renda na literatura (a confirmar) e que o Hub não a mede diretamente |

### H4. Mobilidade na vida adulta (dentro de uma coorte)

| ID | Pergunta | Tipo | Método | Armadilhas |
|---|---|---|---|---|
| H4.1 | A trajetória de renda ao longo da vida diverge por raça (acúmulo de vantagem/desvantagem)? | D | Perfis idade-renda por coorte (B4/D6) | Compartilha método com D6; evita duplicar |
| H4.2 | Entrada e saída de ocupações/posições (via rotação de domicílios) | C | Painel parcial de 5 visitas da PNADC (se viável) | A rotação permite transições de curto prazo; atrito não aleatório |

**Declaração obrigatória em todo H:** "associação entre origem observada e destino; não efeito causal da origem; amostra restrita a quem mora com os pais".

---

## Mapa de fontes (o que cada fonte responde)

| Fonte | Responde | Estado no Hub |
|---|---|---|
| **PNAD Contínua** | A, B, C, D (C), E1–E2 parcial | Em uso |
| PNADC — módulos educação/mobilidade | E1, E5, H | Verificar disponibilidade |
| Censo 2022 | D4.4, E7, segregação, indígenas em amostra grande | Bloqueado (GovBR) |
| Censo da Educação Superior (INEP) | E6, G1 | Não iniciado |
| Censo Escolar e SAEB (INEP) | E2–E4, E7 | Não iniciado |
| ENEM / ENADE (INEP) | E6, acesso | Não iniciado |
| RAIS (identificada/pública) / CAGED | D3, D5, G3 | Não iniciado; verificar acesso |
| Painel de Pessoal do Executivo Federal | G3 | Não iniciado |
| POF | Consumo, patrimônio parcial, H | Não iniciado |
| Estudos de auditoria/experimentos | D3.5, D8 | Literatura (revisão sistemática) |

---

## Ordem de execução (ondas; avançam por critério de saída, não por data)

| Onda | Conteúdo | Critério de saída |
|---|---|---|
| **0** | Auditoria P0: B1–B3, B5 (EP correto, testes, CI) | Tabelas regeneradas; relatório antes/depois aprovado |
| **1** | Bloco F (fundações) + **Bloco S (S0–S1, valida a decisão F3)** + Bloco T (T1–T3, versão curta) + Bloco A (A2–A7) | Documento de definições + tabela de sensibilidade de população/renda aprovada; decisão: a diferença entre P1 e P2/P4 é "grande" pelo critério do plano? Se sim, T vira eixo principal |
| **2** | Bloco B (tendência e coortes) + Bloco C + S1.4–S1.5 | Fichas de B1–B6, C1–C5 aprovadas |
| **3** | Bloco D completo (OB aninhado, Gelbach/Shapley, RIF, território) | D1–D8 com resíduo rotulado; sensibilidade rodada |
| **4** | **Bloco E (educação) + Bloco H (origem, mobilidade, patrimônio)**. Extração de variáveis escolares e da ligação filhos–pais; fontes INEP; POF | Primeiro estudo educacional; H1–H2 com viés de corresidência quantificado; H2.2 compara o resíduo de D1 com e sem origem |
| **5** | Bloco G (políticas, com dado administrativo) | EMD calculado por desenho; só rodar o que tiver poder |
| **6** | Integração (Censo 2022 se destravado, riqueza via fontes externas, H3.4, H4.2) | A decidir após Onda 5 |

Dentro da Onda 4, **H1 e E5 compartilham a mesma base** (ligação filhos–pais): construir uma vez.

**Cada onda termina com:** ficha de pesquisa por estudo · estado de publicação · lista de gráficos permitidos · lista de afirmações **proibidas** (o que o resultado *não* prova).

## O que **não** vamos perguntar (com a razão)

- *"A desigualdade é causada por racismo?"* — não é uma pergunta empírica única. Decompomos em componentes mensuráveis e dizemos o que cada dado alcança.
- *"Quanto do hiato é discriminação?"* — com PNADC só se estima o resíduo; não é discriminação. Só aparece com desenho próprio (auditoria, administrativo).
- *"Quando acaba a desigualdade?"* — só como projeção condicional (B6), nunca como previsão.
- *"Qual raça tem mais X?"* sem contexto de composição e incerteza.
- Saúde, violência, habitação: **outras temporadas.**

## Decisões fechadas e pontos ainda abertos

**Fechadas (12/10/2026):** renda de referência = trabalho principal; população = ocupados com renda > 0; Bloco S/T medem o efeito do recorte; educação (E) depois de D; dados administrativos incluídos; Bloco H no escopo agora (Onda 4); licença MIT + CC BY 4.0.

**Ainda abertos (verificar na Fase 0 do prompt, não decidir no escuro):**
1. Qual variável o Hub usa hoje como renda (`VD4019` = todos os trabalhos? `VD4016` = trabalho principal?) e qual faixa etária. Se divergir da decisão, regenerar com a decisão e reportar a diferença.
2. Acesso a RAIS identificada, Painel de Pessoal e microdados INEP; custo de obtenção.
3. Existência de módulo de mobilidade social na PNAD/PNADC (para H).
4. ~~Limite mínimo de amostra por célula para raça × gênero × Indígena/Amarela (definir regra de supressão).~~ **Fechado em 13/10/2026 (Ponto de parada 3):** n < 30 no denominador do indicador **ou** CV design-based > 30% ⇒ não publica; valores mantidos com a coluna `publicavel` (`src/inference/precisao.py`; `docs/LIMITACOES_E_METODOLOGIA.md`). Revisar no Bloco F.
5. **Pendente (20/10/2026, G3):** pedido via Lei de Acesso à Informação de ingressantes do Executivo federal por ano × cor/raça × órgão/carreira (2008–2025), para destravar a avaliação da Lei 12.990. O Felipe decidiu não pedir agora; verificar em outro momento (ficha `docs/studies/G3`).
