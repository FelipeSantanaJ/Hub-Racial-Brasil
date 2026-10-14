# Ficha de pesquisa — `F` · Fundações: definições do Hub

| Campo | Valor |
|---|---|
| ID no plano | `F1`–`F6` (`docs/PLANO_DE_ANALISE.md`, Bloco F) |
| Onda | 1 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 13/10/2026; F4 e F6 parciais) |
| PR | Onda 1 (`onda1/regeneracao`) |

Esta ficha é o **documento de definições** do critério de saída da Onda 1. Cada conceito tem uma definição, a
variável do IBGE, onde está no código e o que foi medido sobre ele.

## F2 — Conceito de renda

| | Definição |
|---|---|
| **Referência** | Rendimento mensal **habitual do trabalho principal** (`VD4016`), deflacionado pelo deflator habitual do IBGE (multiplica o nominal), a preços do último trimestre da série |
| Onde | `src/utils/populacao.py` (`sql_colunas_renda_tabelas`); nas tabelas, `renda_habitual_*` |
| Alternativas disponíveis | Todos os trabalhos (`VD4019`, `renda_todos_trabalhos_*`), efetivo do trabalho principal (`VD4017`), por hora (`VD4016` ÷ (`V4039` × 4,345)), domiciliar per capita (`VD5008`, só anual) |
| Sensibilidade | S1: P3 (todos os trabalhos) muda o hiato Branca × Negra em +1,2 p.p. em média, nunca acima do critério; P5 (domiciliar per capita) muda em +12 a +22 p.p., acima do critério nos 14 anos |
| Quando usar cada uma | Hiato de remuneração do trabalho: referência. Bem-estar material: domiciliar per capita (Bloco T). Jornada: por hora |

## F3 — População

| | Definição |
|---|---|
| **Referência (P1)** | Ocupados (`VD4002 = 1`) de **18+** (`V2009`) com `VD4016` > 0 |
| Onde | `src/utils/populacao.py` (`REFERENCIA`, `filtro_sql`, flags `em_populacao_referencia*`) |
| Vale para | **Toda análise de renda** desde a Onda 1 (`src/utils/catalogo_tabelas.py`). As tabelas com faixa etária guardam também 14–17 como dado, fora das análises. Tabelas de outros indicadores (escolaridade, ocupação, desalento, alfabetização, sobrequalificação, informalidade, segregação) mantêm o universo do indicador (14+) |
| Quanto pesa | Em 2026T2, P1 = 62,7% das pessoas brancas de 18+, 60,5% das negras, 58,5% das indígenas; entre mulheres, 53,5% / 49,1% (S0.1) |
| Sensibilidade | S1: P2 (com ocupados sem rendimento) ≈ P1; **P4 (todos os adultos, zero para não ocupados) aumenta o hiato em 8,9 p.p. em média, 17,5 entre mulheres** |

## F1 — Quem é cada grupo racial

- Autodeclaração (`V2010`): Branca, Preta, Parda, Amarela, Indígena, Ignorado. "Negra" = Preta + Parda.
  **Ignorado fica sempre fora**; as análises principais são Branca × Negra e Indígena (decisão de 13/10/2026).
- Composição declarada das pessoas de 18+ (`composicao_racial_declarada.parquet`): Branca 47,7% (2012) → 42,7%
  (2026); Preta 7,7% → 11,2%; Parda 43,8% → 45,1%; Indígena 0,2% → 0,4%; Amarela 0,6–0,7%.
- **Consequência:** a média de cada grupo muda também porque quem se declara em cada grupo muda (efeito de
  composição). Separar composição de renda é o B2 (Onda 2). NÃO VERIFICADO: quanto da mudança é reclassificação de
  pessoas e quanto é demografia (a PNAD não acompanha a mesma pessoa por tempo suficiente).

## F4 — Quanto da renda está medida

- **Heaping** (`heaping_renda.parquet`, renda nominal do trabalho principal em P1): % com valor múltiplo de
  R$ 1.000 — Branca 22,8% (2012T1) → 48,3% (2026T2); Negra 11,4% → 32,7%; Indígena 8,7% → 29,6%. Múltiplos de
  R$ 100: 86% / 76% / 78% em 2026T2. O arredondamento **cresceu muito** e é **maior entre brancos**.
- Tratamento já adotado: nos limiares de quantil, o peso empatado é repartido (R9, `pnadc_core.fracao_na_fatia`).
- **Por que o % em múltiplos de R$ 1.000 dobrou (resolvido em 13/10/2026; `heaping_renda_faixas.parquet`,
  `sensibilidade_populacao.gerar_heaping_faixas`).** Não é mudança de comportamento: dentro de cada faixa NOMINAL fixa,
  o % múltiplo de R$ 1.000 é estável de 2012 a 2026 (R$ 2.000–4.999: 56% → 48%; R$ 5.000–9.999: 82% → 83%; R$ 10.000+:
  95% → 95%), e o % de rendas arredondadas a até 2 algarismos significativos fica entre 81% e 86% (exceto 2016 e 2021,
  ~95%, anos em que o salário mínimo — R$ 880 e R$ 1.100 — tem 2 algarismos). O que mudou foi **onde as rendas
  nominais estão**: em 2012, 18% das pessoas de P1 ganhavam R$ 2.000 ou mais; em 2026, 62% (inflação + crescimento).
  Decomposição *shift-share* 2012 → 2026 (2º trimestres): de 17,3% para 39,6% (+22,3 p.p.) = **+29,5 p.p. de
  composição** (mais gente em faixas onde arredondar cai em milhares) **−7,3 p.p. dentro das faixas** (sobretudo a
  faixa R$ 1.000–1.999, onde o salário mínimo de 2026, R$ 1.621, não é redondo). A diferença racial também é
  composição: Branca +31,3 / −6,4 p.p.; Negra +28,7 / −7,5 p.p.; dentro de cada faixa, brancos e negros arredondam
  quase igual (R$ 2.000–4.999 em 2026: 49,2% × 47,7%).
- **Consequência:** o heaping é uma propriedade de **escala relativa** (pessoas arredondam a 1–2 algarismos), não uma
  piora da qualidade da declaração. Quantis continuam caindo em valores redondos (IC de largura zero ≠ precisão).
- **NÃO VERIFICADO:** se houve mudança de instrução ao entrevistador sobre arredondamento (documentação de campo não
  consultada); subdeclaração e topo da distribuição (comparação com IRPF/contas nacionais) — não feito.

## F5 — Incerteza

Linearização de Taylor com Estrato e UPA (`src/inference/variancia.py`), validada contra bootstrap Rao-Wu (razão
mediana 1,005 na Fase 1; na regeneração da Onda 1, 0,973 e 0,979 em 2026T1 e 2026T2); FDR por família
(`src/inference/multiplicidade.py`); regra de supressão n < 30 ou CV > 30% (`src/inference/precisao.py`).

## F6 — Quebras de série

Marcar nos gráficos e testar sensibilidade: 4T2015 (questionário de educação), 2020–21 (coleta por telefone;
Visita 5 no anual), recessão 2015–16, reponderação pela projeção pós-Censo 2022 (o extrato já está reponderado,
Rodada 2). **Marcas feitas** (13/10/2026, `graficos_fase1.marcar_quebras`): hachura na recessão 2015–16, faixa cinza
em 2020–21 e linha pontilhada em 4T2015, em todos os gráficos de série (Fase 1, árvore, Onda 1). **Sensibilidade:**
o S1.5 compara a seleção por episódio; a separação ciclo × tendência do hiato é o B5 (Onda 2). A reponderação não tem
marca própria (o extrato inteiro já está na projeção nova; não há série "antes" para comparar).

## Afirmações proibidas (todas as tabelas)

- Qualquer número de renda sem dizer a população (P1) e o conceito (trabalho principal).
- "O hiato é X%" como se fosse único: S1 mostra que vai de ~66% (P1) a ~79% (P5) em 2025.
