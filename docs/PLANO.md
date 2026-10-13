# Plano de Projeto — Datahub de Análise Racial no Brasil

Documento vivo: escopo, status e planejamento de cada etapa do projeto.

- **Início**: setembro de 2026
- **Ritmo**: 3-5h/semana (projeto pessoal)
- **Status**: ✅ **Etapa 1 (PNAD Contínua) concluída**. Etapas 2 em diante e toda a árvore de
  conteúdo estão **planejadas para 2027**.

---

## Estrutura do projeto: duas árvores

O projeto se organiza em duas árvores independentes, cada uma com suas etapas:

```
Datahub Racial Brasil
├── A. Árvore de Análises      (dados → análises → deck → dashboard)    este documento
│   ├── Etapa 1 — PNAD Contínua                                         ✅ concluída
│   ├── Etapa 2 — Censo Demográfico 2022                                ⏳ 2027
│   ├── Etapa 3 — Módulos anuais da PNAD Contínua (habitação, TIC...)   ⏳ 2027
│   ├── Etapa 4 — Saúde (DataSUS / PNS)                                 ⏳ 2027
│   ├── Etapa 5 — Outras fontes (violência, RAIS, INEP, TSE...)         ⏳ 2027
│   └── Etapa 6 — Dashboard público                                     ⏳ 2027
└── B. Árvore de Conteúdo      (Instagram / TikTok)                     conteudo/
    ├── C1 — Linha editorial e identidade visual                        ⏳ 2027
    ├── C2 — Banco de pautas                                            ⏳ 2027
    ├── C3 — Produção piloto                                            ⏳ 2027
    ├── C4 — Calendário de postagens                                    ⏳ 2027
    └── C5 — Métricas e revisão                                         ⏳ 2027
```

A árvore de análises produz os números; a árvore de conteúdo só consome achados já
validados e publicados nela — nunca gera número próprio. O plano completo da árvore de
conteúdo, o banco de pautas e o calendário de postagens ficam em [`conteudo/`](../conteudo/).

---

## Visão geral

### A. Árvore de Análises

| Etapa | Escopo | Status | Período |
|---|---|---|---|
| 1 | PNAD Contínua — renda, escolaridade, mercado de trabalho, 2012-2026 | ✅ concluída | set/2026 |
| 2 | Censo Demográfico 2022 — recorte abaixo do município (Área de Ponderação), moradia, recorte indígena | ⏳ não iniciada | planejada para 2027 (T1-T2) |
| 3 | Módulos suplementares anuais da PNAD Contínua — habitação, trabalho infantil, TIC, outras fontes de renda | ⏳ não iniciada | planejada para 2027 (T2) |
| 4 | Saúde — DataSUS (SIM/SINASC) e PNS | ⏳ não iniciada | planejada para 2027 (T3) |
| 5 | Outras fontes — violência, encarceramento, mercado formal, educação, representação política | ⏳ não iniciada | planejada para 2027 (T3-T4) |
| 6 | Dashboard público (Observable Framework) | ⏳ não iniciada | planejada para 2027 (T4) |

### B. Árvore de Conteúdo (Instagram/TikTok)

| Etapa | Escopo | Status | Período |
|---|---|---|---|
| C1 | Linha editorial, formatos e identidade visual | ⏳ não iniciada | planejada para jan/2027 |
| C2 | Banco de pautas a partir dos achados da Etapa 1 | ⏳ não iniciada | planejada para jan-fev/2027 |
| C3 | Produção piloto (carrosséis e vídeos curtos) | ⏳ não iniciada | planejada para fev-mar/2027 |
| C4 | Calendário de postagens — lançamento em 21/03/2027 | ⏳ não iniciada | planejada para mar-dez/2027 |
| C5 | Métricas e revisão trimestral | ⏳ não iniciada | planejada para jun, set e dez/2027 |

Detalhes em [`conteudo/README.md`](../conteudo/README.md).

---

# A. Árvore de Análises

## Etapa 1 — PNAD Contínua ✅

**Objetivo**: datasets agregados de renda, escolaridade e mercado de trabalho, cruzados por
**Raça/Cor × Gênero × Faixa etária** (e, nas análises de distribuição, Geração,
Escolaridade e Ocupação), para Brasil / Regiões / UFs / Município de São Paulo / Região
Metropolitana de São Paulo, de 2012 T1 até o trimestre mais recente publicado pelo IBGE
(2026 T2 no fechamento da etapa).

**Recorte racial**: três grupos centrais em pé de igualdade — **Branca**, **Negra**
(Preta + Parda) e **Indígena** — com Amarela sempre explicitada nas tabelas, nunca
descartada silenciosamente. Preta e Parda também são analisadas separadamente.

**Critério de "pronto"**: pipeline reprodutível do FTP do IBGE até `data/processed/`;
todos os cruzamentos do escopo com teste de significância onde há comparação; limitações
documentadas; deck de apresentação e galeria narrada.

### Escopo da Etapa 1

| Bloco | Conteúdo | Status |
|---|---|---|
| 1.1 | Pipeline de dados: extração, deflator oficial, recortes, validação | ✅ |
| 1.2 | Agregações base e primeiras visualizações | ✅ |
| 1.3 | Matriz completa de interseções (raça × gênero × faixa etária × geração × escolaridade × ocupação; Preta × Parda) | ✅ |
| 1.4 | Decomposição do hiato: padronização direta, Oaxaca-Blinder, RIF por quantil | ✅ |
| 1.5 | Distribuição: geração, topo 10%, quartis, função quantil em R$, Gini/Theil | ✅ |
| 1.6 | Estrutura do mercado de trabalho: região, segregação, setores, informalidade, jornada, desalento, quebras estruturais | ✅ |
| 1.7 | Aprofundamentos: instabilidade de renda, retorno da escolaridade, Oaxaca-Blinder ano a ano, dupla desvantagem, convergência, validação cruzada com o IBGE | ✅ |
| 1.8 | Três grupos em pé de igualdade: Branca-Indígena, Preta-Parda, decomposição raça × gênero, painel rotativo | ✅ |
| 1.9 | Identificação causal: Leis de Cotas como variação exógena, com heterogeneidade geográfica | ✅ |
| 1.10 | Robustez estatística e testes automatizados | ✅ |
| 1.11 | Entregáveis: deck em árvore, tabela de crescimento da renda, galeria narrada | ✅ |

Achados narrados em [ANALISE_FASE1.md](ANALISE_FASE1.md),
[ANALISE_RACA_GENERO.md](ANALISE_RACA_GENERO.md) e
[ANALISE_CAUSAL_COTAS.md](ANALISE_CAUSAL_COTAS.md); limitações e decisões metodológicas em
[LIMITACOES_E_METODOLOGIA.md](LIMITACOES_E_METODOLOGIA.md).

---

### 1.1 Pipeline de dados

**Extração** (`src/ingestion/extrator_pnadc.py`): download direto do FTP do IBGE, parsing do
layout SAS de largura fixa, conversão em Parquet particionado
(`data/raw/pnadc_extraido/parquet/ano=AAAA/trimestre=T/`). Idempotente por trimestre
(marcador `_SUCCESS`), com retry e backoff para a instabilidade do FTP. O layout é baixado a
cada execução; variável pedida e ausente no layout gera aviso explícito.

- Série: 58 trimestres (2012 T1 → 2026 T2), **29.926.646** registros pessoa-trimestre;
  contagens conferidas contra `_resumo_extracao.csv` sem divergência.
- Distribuição racial (V2010, 2026 T2): Branca 39,2% · Parda 50,2% · Preta 9,6% · Indígena
  0,6% · Amarela 0,4% · Ignorado ~0% — confirma a amostra pequena de Indígena (~2.900
  registros em 521 mil no trimestre).
- Peso amostral (`V1028`): zero registros nulos ou ≤ 0 no trimestre mais recente.
- `VD4011` (grupamento ocupacional): o nome correto no layout é `VD4011`, não `VD4011A`;
  a série completa foi extraída com essa coluna para a decomposição por ocupação.

**Deflator oficial** (`src/ingestion/baixar_deflator.py` →
`data/processed/deflator_ibge.parquet`, 1.566 linhas): o IBGE publica o deflator da PNAD
Contínua na própria pasta de documentação dos microdados (`Documentacao/Deflatores.zip`),
por UF e trimestre, com fatores separados para renda habitual e efetiva. Só as 4 janelas
que coincidem com os trimestres fixos são usadas. O fator é **multiplicado** pelo valor
nominal (no trimestre de referência, 2026 T2, vale exatamente 1,0). Validação: nominal e
real batem linha a linha no trimestre de referência; em 2012 T1, real ≈ 2,2× nominal.

**Recortes** (`src/utils/pnadc_core.py`): estatística ponderada (média, erro padrão, IC,
coeficiente de variação), teste de Welch, Gini ponderado, recortes raciais e de gênero,
níveis geográficos e paleta de cores.

**Validação contra os dados reais** — três decisões que vieram dessa checagem:

- `V2010`, `V2007`, `UF`, `Capital` e `RM_RIDE` são colunas de **texto** no layout do IBGE
  (formato `$N.`). Os dicionários de mapeamento (`CODIGOS_RACA`, `CODIGOS_SEXO`,
  `REGIAO_POR_UF`) usam chaves string; com chaves inteiras, todos os recortes saíam `NaN`
  sem erro. Retestados, os recortes reproduzem exatamente a distribuição bruta de `V2010`.
- `Capital` e `RM_RIDE` não são flags 1/2: trazem o código da UF quando o registro é da
  capital/RM e ficam em branco caso contrário. Testado em 2026 T2: 8.645 registros de SP
  capital vs. 31.410 do interior de SP.
- Lição que vale para o projeto inteiro: código que compila e "parece certo" é testado
  contra o dado real antes de virar base de qualquer agregação.

### 1.2 Agregações base e primeiras visualizações

`src/processing/agregacoes_pnadc.py` cruza Raça/Cor (6 categorias brutas do IBGE — Preta e
Parda não são pré-somadas no dataset base) × Gênero × Faixa etária × 5 níveis geográficos
(Brasil / Região / UF / SP capital-interior / RM SP capital-vs-não-capital) × trimestre:

- `renda.parquet` (105.969 linhas, colunas `_nominal` e `_real`), `escolaridade.parquet`
  (544.540), `ocupacao.parquet` (105.969).
- Cada nível geográfico roda como query separada e é concatenado em pandas — um único
  `UNION ALL` com os 5 níveis travava o DuckDB; separado, o pipeline completo roda em menos
  de 3 minutos.
- Checagem de sanidade (Brasil, 2026 T2, nominal): renda habitual Branca R\$4.506 vs.
  Preta R\$2.600 / Parda R\$2.708; desocupação Branca 4,2% vs. Preta 6,9% / Parda 6,1%;
  superior completo Branca 26,4% vs. Preta 11,9% / Parda 12,2% — direção e magnitude
  batem com as estatísticas públicas do IBGE.
- Em R\$ reais (preços de 2026 T2): renda Branca de R\$3.768 (2012 T1) para R\$4.506; Negra
  de R\$2.077 para R\$2.687; razão Branca/Negra de 1,81× para 1,68×.

`src/processing/graficos_fase1.py` gera a série de renda por raça publicada no README
(Indígena com média móvel de 4 trimestres) e os cortes por gênero, faixa etária e nível de
instrução. Achado central: o hiato racial **sobrevive ao controle por escolaridade** e se
abre mais no Superior completo (Branca R\$8.104 vs. Negra R\$5.701, Brasil, 2026 T2) — maior
entre homens (~46%) que entre mulheres (~36%). Identidade visual em tons terrosos, paleta
categórica validada para contraste e daltonismo.

### 1.3 Matriz completa de interseções

Cobertura sistemática de raça × gênero × faixa etária × geração × escolaridade ×
ocupação, com "um gráfico combinado + um por categoria" para cada dimensão, e a mesma
estrutura repetida para Preta × Parda.

- Heatmap de 4 dimensões (raça × gênero × faixa etária × nível de instrução,
  `renda_completa.parquet`, 20.377 linhas, só Brasil) e sua versão por geração
  (`renda_completa_geracao.parquet`).
- Tabelas-base multidimensionais (`gerar_renda_multidimensional_faixa` /
  `_geracao`: raça × sexo × [faixa etária ou geração] × nível de instrução × grupamento
  ocupacional, últimos 8 trimestres agrupados); qualquer combinação é obtida colapsando
  dimensões por média ponderada.
- **Combinação deliberadamente fora**: raça × faixa etária × geração — as duas medem idade
  (atual vs. ano de nascimento); cruzá-las só cria células minúsculas sem informação nova.
- Hiato com teste de Welch em todas as 24 combinações da seção "Renda média"
  (`gerar_hiatos_multidimensionais`) e hiato histórico trimestre a trimestre por gênero,
  faixa etária, escolaridade e geração (`gerar_hiato_historico_por_categoria`).
- Hiato Branca vs. Negra (`hiato_racial.parquet`): os 58 trimestres são estatisticamente
  significativos a 95%; o hiato caiu de ~76% para ~66% entre 2012 e 2026.
- Preta vs. Parda (`gerar_hiato_preta_parda`): o hiato **mudou de sinal** — Preta chegou a
  ganhar mais que Parda em vários trimestres até ~2015, hoje ganha consistentemente menos
  (-6% no trimestre mais recente).

### 1.4 Decomposição do hiato: ocupação explica, ou é cor da pele?

Pergunta: controlando por idade e escolaridade, o hiato existe porque negros e brancos
estão em ocupações diferentes, ou persiste dentro da mesma ocupação?

**Padronização direta** (`gerar_decomposicao_hiato_ocupacional`, últimos 8 trimestres,
ocupados com ocupação identificada, células com ≥ 30 pessoas de cada raça):

| Controle | Hiato | Amostra de Negra incluída |
|---|---|---|
| Nenhum (hiato bruto) | 67,0% (R\$1.884) | 100% |
| + faixa etária | 63,9% (R\$1.797) | 100% |
| + faixa etária + escolaridade | 30,3% (R\$851) | 99,99% |
| + faixa etária + escolaridade + ocupação | **24,3% (R\$684)** | 99,91% |

**Oaxaca-Blinder** (`pnadc_core.decomposicao_oaxaca_blinder`, twofold, coeficientes de
referência = média dos dois grupos, Reimers 1983; modelo restrito para o teste formal do
resíduo; erro padrão clusterizado por UPA):

| Controles | Explicada | Não-explicada | Coef. residual (log) | p-valor |
|---|---|---|---|---|
| + faixa etária | 1,6% | 98,4% | 0,422 | < 0,001 |
| + faixa etária + escolaridade | 44,8% | 55,2% | 0,235 | < 0,001 |
| + faixa etária + escolaridade + ocupação | 52,6% | 47,4% | 0,202 | < 0,001 |

O resíduo final (0,202 log-pontos) equivale a um hiato de **~22,4%** — muito próximo dos
24,3% da padronização direta. Dois métodos convergindo no mesmo número.

**Ocupação sozinha**: leva o hiato de 67,0% para **33,4%** (padronização direta) e explica
**40,4%** no Oaxaca-Blinder (p < 0,001) — quase tanto quanto idade + escolaridade juntas.

**RIF por quantil** (Firpo-Fortin-Lemieux 2009, controles completos):

| Ponto da distribuição | Não-explicada | Hiato residual |
|---|---|---|
| P10 (base) | 58,2% | ~30,6% |
| P50 (mediana) | 45,5% | ~14,9% |
| P90 (topo) | 41,1% | ~36,1% |

Formato em **U**: "piso pegajoso" na base e "teto de vidro" no topo. As duas funções foram
validadas com dados sintéticos de parâmetros conhecidos antes de rodar nos dados reais.

### 1.5 Distribuição da renda

- **Geração** — coorte de nascimento sintética (`ano − V2009`, Deaton 1985): Baby Boomer,
  Geração X, Millennial e Geração Z. O hiato varia muito por geração (30% na Geração Z,
  ~90-100% no Baby Boomer); o do Baby Boomer cresce conforme a coorte envelhece (provável
  efeito de seleção de quem segue trabalhando).
- **Topo 10%** (P90 calculado dentro de cada raça): a parcela com Superior completo no topo
  dos negros foi de 38% (2012) para ~58%, contra ~83% no topo dos brancos. O topo negro tem
  mais que o dobro de Médio completo (23%) que o branco (10%).
- **4 quartis** (P25/P50/P75 dentro de cada raça): o hiato de Superior completo entre Negra
  e Branca vai de ~6 p.p. no Q1 a ~32 p.p. no Q4.
- **Heaping** documentado: renda autodeclarada concentra em valores redondos; quando o
  limiar cai num deles, o recorte captura um pouco mais que 10% (~11,5% Branca, ~12,8%
  Negra). A coluna `pct_populacao_capturada` registra o valor real.
- **Função quantil em R\$ e sua inversa** (`percentil_ponderado_de_valor`, validada por
  round-trip): R\$3.000 está no **P57** da distribuição de Branca e no **P76** da de Negra; os
  10% mais pobres ganham R\$1.500 (Branca) e R\$720 (Negra). O hiato bruto por percentil
  também tem formato em U (108% no P10, 23-50% no meio, 100% no P90).
- **Gini e Theil**: Branca tem Gini mais alto que Negra (distribuição negra mais comprimida
  perto da base, não "situação melhor"); só ~7% da desigualdade total vem de diferença entre
  raças — 93% é dentro de cada raça.
- **Topo 10% / base 10% / quartis em 3 escopos** (`gerar_extremos_racial`,
  `gerar_quartis_multi_racial`): limiar Brasil, dentro de gênero e dentro de raça×gênero.
  Negra é ~56% dos ocupados, mas 33% do topo 10% e 73% da base 10%. Renda média do topo
  10%: Branca·Homem R\$22.219 vs. Negra·Mulher R\$8.710; da base 10%: R\$943 vs. R\$378.

### 1.6 Estrutura do mercado de trabalho

- **Hiato por Região** (`hiato_regional.parquet`, Welch trimestre a trimestre).
- **Segregação** (índice de Duncan): ocupacional **17,0%**, setorial ~10%.
- **Setor público vs. privado**: hiato menor no público (~45-50%) que no privado (~58-68%).
- **Sobre-qualificação** (Superior completo em ocupação elementar): taxa de Negra quase o
  dobro da de Branca em quase toda a série.
- **Informalidade**: % com carteira Branca 72%, Negra 63%, Indígena 52% (2026 T2).
- **Jornada**: parecida entre os grupos (38,8h / 37,7h / 36,7h), mas o hiato por hora
  (~65%) é quase igual ao mensal (67%) — é remuneração por hora, não jornada.
- **Alfabetização 60+**: Branca 93%, Negra 80%, Indígena 72%.
- **Desalento**: Negra e Indígena desistem de procurar emprego a taxas 2-4× a de Branca.
- **Frequência escolar (V3014) fora do escopo**: cobertura de só ~6-8% na população de
  14-17 anos em vários trimestres, sem confirmação de que a subamostra é aleatória.
- **Quebra estrutural** (OLS com dummy pós-evento + interação com tendência):

| Evento | Mudança de patamar | Mudança de inclinação | Significativo? |
|---|---|---|---|
| Reforma trabalhista (2017 T3) | +9,45 p.p. (p<0,001) | −0,43 p.p./trim. (p<0,001) | Sim |
| Reforma da previdência (2019 T4) | +8,87 p.p. (p=0,004) | −0,37 p.p./trim. (p<0,001) | Sim |
| Recessão (2015 T1) | +5,58 p.p. (p=0,004) | −0,08 p.p./trim. (p=0,74, NS) | Sim (só no patamar) |

Correlação temporal numa série agregada de 58 pontos, não inferência causal.

### 1.7 Aprofundamentos

| # | Análise | Dataset | Achado |
|---|---|---|---|
| 1 | Renda efetiva ÷ habitual (instabilidade) | de `renda.parquet` | ver gráfico |
| 2 | Retorno da escolaridade por raça | de `renda_por_escolaridade.parquet` | Superior completo "vale" ~2,65× o Médio para Branca, ~2,37× para Negra |
| 3 | Hiato Capital × Interior | `hiato_capital_interior.parquet` | — |
| 4 | Desocupação por raça × escolaridade | `desocupacao_por_escolaridade.parquet` | — |
| 5 | Hiato formal × informal | `hiato_formal_informal.parquet` | — |
| 6 | % ≤ 1 SM / > 3 SM por raça | `faixas_salario_minimo.parquet` | — |
| 7 | Oaxaca-Blinder + RIF ano a ano | `oaxaca_blinder_temporal.parquet` | **parcela não-explicada travada em ~46% há 14 anos**, apesar da escolaridade de negros subir |
| 8 | Dupla desvantagem Homem Branco ↔ Mulher Negra | `dupla_desvantagem.parquet` | raça ~65% do gap, interação (~20%) > efeito gênero puro (~15%) |
| 9 | "Quanto tempo até fechar o hiato" | fit em `hiato_racial.parquet` | tendência 2012-26 → ~2104; pós-recessão 2016-26 → ~2073 (ilustrativo) |
| 10 | Validação cruzada com o IBGE | — | reproduz os números oficiais dentro de ~1-3 p.p. |

Validação cruzada com "Desigualdades Sociais por Cor ou Raça no Brasil" (IBGE, 2ª ed.,
nov/2022, dados de 2021):

| Indicador (2021) | IBGE | Este projeto |
|---|---|---|
| Desocupação Branca / Preta / Parda | 11,3 / 16,5 / 16,2 % | 10,8 / 16,1 / 15,0 % |
| Informalidade Branca / Preta / Parda | 32,7 / 43,4 / 47,0 % | 35,1 / 44,2 / 47,7 % |
| Hiato de renda Branca vs. Preta/Negra | ~76 % (vs. Preta) | ~70 % (vs. Negra) |

Diferenças cabem em universo e definição. Fontes:
[IBGE](https://www.ibge.gov.br/estatisticas/sociais/populacao/25844-desigualdades-sociais-por-cor-ou-raca.html),
[Agência Brasil](https://agenciabrasil.ebc.com.br/economia/noticia/2022-11/ibge-renda-media-de-trabalhador-branco-e-757-maior-que-de-pretos).

### 1.8 Três grupos em pé de igualdade

Regra para Indígena: destravar amostra pequena agrupando trimestres antes de descartar um
cruzamento; se nem o agrupamento máximo fecha o mínimo de 30, o corte fica em branco e
documentado. A amostra foi medida antes de implementar cada corte.

1. **Toolkit completo para Branca-Indígena e Preta-Parda**: Oaxaca-Blinder, segregação de
   Duncan, hiato regional, topo 10% e quartis. Só a segregação **setorial** Branca-Indígena
   não fecha amostra nem com os 58 trimestres agrupados. No par Preta-Parda, o hiato bruto
   é pequeno (~-5,8%), então a leitura confiável é o coeficiente residual em log-pontos —
   ele revela um "teto de vidro" específico de Preta dentro da população negra.
2. **Decomposição raça × gênero** (`decomposicao_raca_genero.parquet`, nove combinações vs.
   Homem Branco): Homem Indígena tem o maior efeito-raça isolado, mas o termo de interação
   de Mulher Indígena é o mais negativo.
3. **Ritmo de convergência** (`ritmo_convergencia_hiatos.parquet`): Branca-Negra converge
   lentamente (~78 anos, extrapolação ingênua); Branca-Indígena e Preta-Parda estão
   divergindo no ritmo atual.
4. **Painel rotativo real** (UPA/V1008/V1016/V2003): mesma pessoa só quando `V1016` avança
   exatamente +1 entre trimestres consecutivos, com checagem de sexo e idade. Taxa de match
   ~68%. Homens negros, pardos, pretos e indígenas saem do desemprego mais rápido que
   homens brancos (36-38% vs. 33%) — sinal de rotatividade em trabalho mais precário; a
   transição informal → formal (Indígena a mais baixa, ~10,5%) conta a história oposta.

Achados completos em [ANALISE_RACA_GENERO.md](ANALISE_RACA_GENERO.md).

### 1.9 Identificação causal: Leis de Cotas

Tudo antes deste bloco é descritivo. Aqui as duas Leis de Cotas entram como variação
exógena, num desenho declaradamente **preliminar**. A PNAD não tem nota de vestibular nem
instituição de ensino, então o RDD da literatura (Mello 2022; Francis-Tan &
Tannuri-Pianto) não é replicável; o desenho possível é diff-in-diff por coorte de exposição.

- **Desenho A — cotas universitárias (Lei 12.711/2012)**: DiD por coorte de nascimento,
  % Superior completo medido sempre aos 25-29 anos, teste de tendências paralelas e
  placebos em 2008/2016. Resultado **nulo**: tendências paralelas sustentadas (p=0,42 e
  p=0,86), sem efeito de nível (p=0,97 Negra, p=0,80 Indígena). "Não detectei efeito" não é
  "não há efeito".
- **Desenho B — cotas no serviço público federal (Lei 12.990/2014)**: event-study, setor
  privado como controle. Participação: nenhum efeito significativo; identificação falha
  para Indígena (p=0,046 no pré-lei). Hiato de renda: o resultado mais bem identificado —
  tendências paralelas com folga (p=0,61), DiD +0,020 log (~2%, p=0,041): o hiato dentro do
  setor público encolheu mais que no privado depois da lei.
- **Heterogeneidade geográfica** (Região, urbano/rural, DF): identificação falha em pontos
  específicos (Negra-Norte e Negra-Rural no Desenho A; Negra-Nordeste, Parda-Nordeste e
  Parda-Sul na participação do Desenho B). A hipótese do DF não se confirmou (p=0,89); o
  Centro-Oeste como região teve o efeito mais forte e bem identificado (+5,6% no hiato de
  renda, p=0,030).

Texto completo, com a seção "o que isso NÃO prova", em
[ANALISE_CAUSAL_COTAS.md](ANALISE_CAUSAL_COTAS.md).

### 1.10 Robustez estatística e testes automatizados

1. **Erro padrão clusterizado por UPA** nos três modelos do Oaxaca-Blinder: coeficientes
   idênticos, erro padrão entre 1,8× e 4,4× maior; nenhuma das 67 linhas testadas muda de significância
   (pior p-valor da série temporal: 1,9e-73).
2. **Bootstrap por cluster** (`pnadc_core.erro_padrao_cluster_bootstrap`,
   `src/processing/checagem_robustez_hiato.py`, 200 réplicas) sobre a série de hiato por
   Welch: erro padrão 54×-90× maior (média 67×), puxado por UPAs com rendas extremas
   reamostradas em bloco. Mesmo assim os **58 trimestres continuam significativos**
   (`checagem_robustez_hiato_racial.parquet`).
3. **Múltiplas comparações**: sem correção formal; o tamanho de efeito (60-70 p.p.) é
   ordens de grandeza maior que o que ruído explicaria. Limitação registrada, com atenção
   especial aos cortes de amostra pequena.
4. **Testes automatizados** (`tests/test_pnadc_core.py`, pytest, 13 casos): round-trip de
   quantil, casos sintéticos de Theil, erro padrão ponderado contra s/√n e guarda contra
   inflação ~√n, Gini nos dois extremos.

### 1.11 Entregáveis

**Deck em árvore** (`src/processing/graficos_arvore.py`, `graficos_extremos.py`,
`graficos_aprofundamentos.py`, `apresentacao_final.py` →
[`Datahub_Racial_Brasil_Fase1.pptx`](Datahub_Racial_Brasil_Fase1.pptx), ~657 slides).
Regras de desenho:

- Árvore **cruzada** de renda por raça (Mulheres × 14-17 anos é um gráfico próprio), com
  11 itens: Raça; × Gênero; × Faixa etária; × Geração; × Escolaridade; e os cruzamentos até
  Raça × Gênero × [Faixa | Geração] × Escolaridade, mais Raça × Geração × Escolaridade com
  os dois gêneros juntos.
- **Cada imagem aparece em exatamente um slide.** Título, subtítulo, legenda e fonte são
  caixas de texto editáveis; o PNG traz só dados, eixos e rótulos.
- Folha de renda = série histórica 2012-2026. Folha de hiato = Branca vs. Negra **e**
  Branca vs. Indígena, em slides separados (a série de Indígena usa média móvel de 4
  trimestres), sempre com Welch. Homens em linha tracejada, mulheres em linha sólida.
- Célula sem amostra vira placeholder "Amostra insuficiente" (ex.: 14-17 anos × Superior
  completo).
- Depois da árvore: topo 10% / base 10% / quartis nos 3 escopos, ponteiro para a tabela de
  crescimento, Aprofundamentos e "Outras análises".
- [`Datahub_Racial_Brasil_ARVORE.pptx`](Datahub_Racial_Brasil_ARVORE.pptx) (412 slides):
  deck de conferência só com a árvore (itens 1-10).
- Manifesto da árvore em [`arvore_manifest.json`](arvore_manifest.json).

**Tabela de crescimento da renda** (`src/processing/tabela_crescimento.py` →
[`tabela_crescimento_renda.xlsx`](tabela_crescimento_renda.xlsx) e `.csv`, 181 linhas): uma
linha por folha de renda da árvore, renda Branca/Negra/Indígena em 2012 T1 e 2026 T2. Negra
cresceu mais (em %) em 101 das 181 folhas, mas a diferença em R\$ aumentou em 92 — o hiato
relativo cai enquanto a distância absoluta sobe.

**Galeria narrada**: [ANALISE_FASE1.md](ANALISE_FASE1.md), com a leitura de cada gráfico
exploratório, incluindo a família Preta vs. Parda.

**Números finais da etapa**: 721 gráficos em `docs/img/`, 98 datasets em
`data/processed/`.

---

## Extensões da Etapa 1 planejadas para 2027

| Extensão | Motivo |
|---|---|
| Série **trimestral** das transições do painel rotativo para Branca/Negra/Preta/Parda | Amostra comporta; hoje a série é agregada no período inteiro |
| Versão faixa etária do item 11 (Faixa × Escolaridade, gêneros juntos) | Simetria com a versão por geração |
| Regerar as imagens de "Outras análises" como figura crua | Padronizar com a árvore (título como caixa de texto) |
| Correção de desempate no limiar do topo 10% | Reduzir o efeito do heaping |
| Investigar a regra de coleta de V3014 (frequência escolar) | Permitir publicar evasão escolar com segurança |
| Atualização trimestral da série (2026 T3 em diante) | Manter a série corrente conforme o IBGE publica |

---

## Etapa 2 — Censo Demográfico 2022 ⏳ (planejada para 2027, T1-T2)

**Objetivo**: renda, escolaridade, condições domiciliares e mercado de trabalho por
**Raça/Cor × Gênero**, com **recorte abaixo do município** (Área de Ponderação), resolvendo o
que a PNAD não permite — em especial o ABC Paulista, cujos municípios não são
identificáveis na PNAD Contínua pública. Quesito dedicado à população indígena (etnia,
terra indígena), mais robusto que a PNAD.

**Recorte racial**: os mesmos três grupos da Etapa 1, com Amarela explicitada. Confirmar no
dicionário oficial o código da variável de cor/raça (esperado `V0606` ou equivalente, **não
confirmado**) e se ela usa as mesmas 5 categorias da PNAD.

**Acesso aos microdados**: o IBGE disponibiliza a amostra do Censo 2022 em 3 níveis:

| Nível | Requisito | Granularidade geográfica |
|---|---|---|
| Público | Nenhum | Só até **UF** — não resolve o objetivo da etapa |
| **Controlado** | Login **GovBR** + formulário + **termo de compromisso assinado digitalmente** | **Área de Ponderação** — setores censitários contíguos dentro dos limites municipais |
| Sala de Acesso Restrito | Presencial, no IBGE (Rio) | Base completa — fora de escopo |

O nível necessário é o **Controlado**. O termo proíbe redistribuir os microdados brutos —
só o agregado, que é o que o projeto publica (`data/raw/` já fica fora do git). Não há prazo
documentado de aprovação do pedido de acesso; o tempo de espera é um risco de cronograma.

**Critério de "pronto"**: parquets em `data/processed/` com os cruzamentos por Área de
Ponderação e pelo menos um gráfico com o ganho sobre a Etapa 1 — idealmente o recorte do ABC
Paulista.

| # | Etapa | Estimativa | Status |
|---|---|---|---|
| 0 | Solicitar acesso controlado em [microdados.ibge.gov.br](https://microdados.ibge.gov.br/) (GovBR + termo); baixar microdados da amostra + dicionário | 1-2h + espera de aprovação | ⏳ não iniciada |
| 1 | Validar o dicionário: variável de cor/raça, código de Área de Ponderação, variáveis de renda/escolaridade/domicílio | 2h | ⏳ |
| 2 | `extrator_censo.py` no padrão do extrator da PNAD, processando os arquivos baixados na etapa 0 | 3h | ⏳ |
| 3 | Recorte racial de 3 grupos (mesma lógica de `pnadc_core.py`) | 2h | ⏳ |
| 4 | Agregações por Área de Ponderação × raça × gênero: renda, escolaridade, condições domiciliares (saneamento, tipo de domicílio, densidade) | 6h | ⏳ |
| 5 | Recorte ABC Paulista — Áreas de Ponderação de Santo André / São Bernardo / São Caetano vs. o agregado "RM SP não-capital" da Etapa 1 | 3h | ⏳ |
| 6 | Recorte indígena expandido (etnia, terra indígena) | 2h | ⏳ |
| 7 | Limitações: comparabilidade Censo × PNAD (anos e coleta diferentes; checagem cruzada com IPUMS/Data Zoom) | 2h | ⏳ |
| 8 | Visualizações + README/docs | 4h | ⏳ |

Total: ~25h ativas, ~5-7 semanas no ritmo do projeto, mais a espera da etapa 0.

---

## Etapa 3 — Módulos suplementares anuais da PNAD Contínua ⏳ (planejada para 2027, T2)

Além da divulgação trimestral usada na Etapa 1, o IBGE publica uma **divulgação anual** com
temas suplementares coletados em visitas específicas. É FTP público sem login, então pode
correr em paralelo à espera de acesso do Censo. Priorização pelo quadro oficial "PNAD
Contínua – Pesquisas Suplementares Anuais 2012-2025":

- **Prioridade 1** (série longa, preenche lacuna da Etapa 1): Habitação (visita 1,
  2016-2019 / 2022-2025), Trabalho de crianças e adolescentes (visita 5, 5-17 anos), Outras
  formas de trabalho (visita 5), Educação (trimestre 2), TIC (trimestre 4), Rendimento de
  outras fontes (separa trabalho de aposentadoria/aluguel/transferência — ângulo de
  patrimônio).
- **Prioridade 2** (corte interseccional forte, 1-3 anos): Segurança alimentar (2023-2024),
  Pessoas com deficiência (2022), Trabalho por plataformas digitais (2022/2024/2025),
  Teletrabalho (2022), Atenção primária à saúde (2022, ponte para a Etapa 4).
- **Prioridade 3** (pontual): Sensação de segurança / furto e roubo (2021), Turismo,
  COVID-19 (2023).

**Primeiro módulo: Habitação** — a melhor proxy de patrimônio que a PNAD oferece
(saneamento, adensamento, material construtivo, posse do imóvel).

| # | Etapa | Status |
|---|---|---|
| 1 | Extrator por ano (`extrator_pnadc_visita_anual.py`): a visita 1 publica um input SAS próprio por ano, então o layout é lido ano a ano; peso calibrado da divulgação anual (`V1032`) | ⏳ não iniciada |
| 2 | Harmonização de variáveis que mudam de nome entre anos (banheiro, esgoto, combustível de cozinha), conferindo o significado de cada código e não só o nome | ⏳ |
| 3 | Indicadores: esgoto adequado, água de rede geral, parede de alvenaria, imóvel próprio, banheiro exclusivo, adensamento excessivo (> 2 pessoas/dormitório, convenção FGV/FJP) | ⏳ |
| 4 | Hiato racial e racial × gênero ano a ano, com Welch; corte regional | ⏳ |
| 5 | Decomposição composição regional × hiato dentro da região | ⏳ |
| 6 | Visualizações, limitações e próximos módulos da prioridade 1 | ⏳ |

---

## Etapa 4 — Saúde ⏳ (planejada para 2027, T3)

Natalidade, mortalidade (incluindo materna e infantil por raça/cor) e acesso a serviços:
SIM, SINASC e outros sistemas do DataSUS (registros administrativos), complementados pela
PNS (edições 2013/2019/2024, autorreportada). Detalhamento de etapas no início de 2027.

---

## Etapa 5 — Outras fontes ⏳ (planejada para 2027, T3-T4)

Módulos independentes entre si, priorizados por esforço × impacto:

| Módulo | Fonte | Acesso | Esforço | Ângulo |
|---|---|---|---|---|
| Violência | Atlas da Violência (IPEA + FBSP) | CSV agregado | Baixo (2-3h) | Homicídios por raça/gênero |
| Encarceramento | INFOPEN/Depen | CSV/planilhas | Baixo-médio | População carcerária por raça |
| Representação política | TSE, dados abertos | CSV de candidaturas | Baixo-médio | Candidaturas/eleitos por raça (autodeclaração desde 2014) |
| Mercado formal | RAIS/CAGED (PDET, FTP público) | Microdados administrativos | Médio-alto | Salário, admissão/desligamento por raça no emprego formal |
| Educação | INEP — Censo Escolar + ENEM | Microdados grandes | Alto | Desempenho e acesso educacional por raça/cor |

**Referências de metodologia para validação cruzada**: IPUMS (microdados harmonizados entre
países e anos), `lodown` (asdfree.com, desenho amostral e pesos), `microdadosBrasil` (leitura
de PNAD/Censo/POF, útil para conferir contagens) e Data Zoom (PUC-Rio, convenções de
deflação e painel rotativo). Uso pretendido: validação, não substituição do pipeline.

---

## Etapa 6 — Dashboard público ⏳ (planejada para 2027, T4)

Publicação das análises consolidadas em Observable Framework, desacoplada do pipeline de
dados. Primeiro recorte: filtros de gênero × escolaridade × geração sobre as séries de
renda e de hiato — o deck em árvore já cobre todos os estados desse filtro, então o
dashboard pode nascer direto dos parquets da Etapa 1. O dashboard também vira a fonte de
link das postagens da árvore de conteúdo.

---

# B. Árvore de Conteúdo (Instagram/TikTok)

Árvore separada, planejada para 2027: linha editorial, banco de pautas a partir dos achados
já validados, produção piloto, calendário de postagens com lançamento em **21/03/2027** (Dia
Internacional pela Eliminação da Discriminação Racial) e revisão trimestral por métricas.

- Plano e etapas: [`conteudo/README.md`](../conteudo/README.md)
- Banco de pautas: [`conteudo/PAUTAS.md`](../conteudo/PAUTAS.md)
- Calendário de postagens 2027: [`conteudo/CALENDARIO_2027.md`](../conteudo/CALENDARIO_2027.md)

---

## Riscos e pontos de atenção

- **ABC Paulista não é identificável na PNAD Contínua pública** — só RM/RIDE, sem código de
  município. O mais granular possível é "RM São Paulo, não-capital", que mistura o ABC com
  outras cidades da Grande São Paulo. Resolvido só pelo Censo (Etapa 2).
- **Amostra Indígena pequena e de alta variância** na PNAD — agrupar trimestres quando
  necessário e tratar o Censo como fonte mais robusta para esse recorte.
- **Acesso controlado ao Censo** sem prazo de aprovação documentado — pode atrasar a Etapa 2;
  a Etapa 3 (sem login) roda em paralelo.
- **Mudança de layout do IBGE** entre anos — o extrator lê o layout a cada execução e avisa
  sobre variáveis ausentes; nas divulgações anuais o layout muda por ano.
- **Quebras conhecidas**: recessão 2015-2016, pandemia (2020-2021, coleta por telefone e
  amostra menor), reforma trabalhista (2017) e da previdência (2019).
- **Instabilidade do FTP do IBGE** — extratores com retry, backoff e idempotência por
  partição.
- **Tamanho dos dados**: microdados brutos (~500 MB na série trimestral, +~9 MB por
  trimestre) ficam em `data/raw/`, fora do git; só agregados são versionados.
- **Categorização de raça/cor**: Amarela sempre explicitada, nunca descartada em silêncio.
