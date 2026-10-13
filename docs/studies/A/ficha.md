# Ficha de pesquisa — `A` · A diferença existe? De quanto é? (A2–A7)

| Campo | Valor |
|---|---|
| ID no plano | `A2`–`A7` (`docs/PLANO_DE_ANALISE.md`, Bloco A). `A1` = `hiato_racial` (já existia) |
| Onda | 1 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (proposto) |
| PR | Onda 1, parte 2 (`onda1/parte2`) |

## 1. Pergunta

De quanto é a diferença de renda do trabalho entre pessoas brancas, negras e indígenas, medida de várias formas,
onde ela está na distribuição e quanto da desigualdade total ela representa?

## 2. Tipo

`D`. Nenhuma decomposição causal; A4 é contabilidade de desigualdade (entre × dentro), não explicação.

## 3. Estimando

- **A2/A7:** diferença em R$, razão Branca/grupo, log-pontos ln(razão), "% da renda Branca" (100/razão) e hiato %
  (razão − 1), com IC 95%; renda mensal (A2) e por hora (A7).
- **A3:** quantis P10–P99 por raça, hiato por quantil, razões P90/P50, P50/P10, P90/P10.
- **A4:** Gini total; Theil T e Theil L (MLD) com parcela entre raças.
- **A5:** participação de cada raça em cada décimo nacional e índice de representação; razão de chances de estar
  no topo 10% e na base 10%.
- **A6:** F_grupo(c) − F_Branca(c) em 99 pontos (percentis da distribuição conjunta).

## 4. População

P1 (ocupados 18+ com `VD4016` > 0), renda habitual real do trabalho principal, 2012T1–2026T2. Branca, Negra
(Preta+Parda), Indígena e Amarela; Ignorado fora. A versão domiciliar per capita (A7) é o T1.

## 5. Método

- A2/A5/A6: linearização Estrato/UPA (razão por delta; log-OR por delta sobre proporções de domínio; limiares
  dos décimos tratados como fixos). A3: bootstrap Rao-Wu Estrato/UPA, 200 réplicas, IC por percentis, nos 2º
  trimestres (15 anos). A4: sem IC. A5: peso empatado nos limiares repartido (R9).
- Testes: `tests/test_bloco_a.py` (coerência das métricas, Theil L fecha, quantis = `pnadc_core`, Rao-Wu).

## 6. Dados

PNAD Contínua trimestral, extrato v2 + deflator IBGE.

## 7. Hipóteses concorrentes

| # | Hipótese | Previsão |
|---|---|---|
| H1 | O hiato é igual ao longo da distribuição | hiato por quantil constante |
| H2 | Piso pegajoso e teto de vidro | hiato maior em P10 e P90+ |

## 8. O que refutaria

H2 seria refutada por hiato por quantil plano ou decrescente do P10 ao P99.

## 9. Armadilhas

- **Valores redondos:** os quantis caem em R$ 1.500, R$ 3.000, R$ 5.000, R$ 10.000…; vários IC de quantil saem
  com largura zero no bootstrap (P90 Branca = R$ 10.000 em todas as réplicas). **Isso não é precisão perfeita**: é
  a massa declarada no valor redondo. O P25 Negra (R$ 1.621) é o salário mínimo de 2026.
- A5 trata os limiares dos décimos como fixos (o IC da razão de chances fica um pouco estreito).
- Composição racial declarada mudou (F1).

## 10. Resultados

Tabelas: `a2_metricas_hiato`, `a3_hiato_quantis`, `a4_desigualdade_decomposicao`, `a5_representacao_decimos`,
`a6_dominancia` (`data/processed`).

**A2 — Branca × Negra, renda mensal (2º trimestre)**

| Ano | Diferença | Razão | Log-pontos | Negra ganha … da Branca | Hiato % (IC 95%) |
|---|---|---|---|---|---|
| 2012 | R$ 1.705 | 1,75 | 0,56 | 57,2% | 74,7% (70,2–79,3) |
| 2019 | R$ 1.776 | 1,73 | 0,55 | 57,7% | 73,5% (68,0–78,9) |
| 2026 | R$ 1.856 | 1,66 | 0,51 | **60,4%** | **65,7%** (62,1–69,2) |

Branca × Indígena 2026: 70,9% (47,1–94,7). **A7, por hora**: Branca × Negra 63,3% (59,6–66,9) em 2026, 71,9% em 2012.

**A3 — hiato por quantil, Branca × Negra (2026 T2)**: P10 96%, P25 11%, P50 50%, P75 67%, P90 100%, P95 100%,
P99 94%. Desde 2012 o padrão em U se mantém: alto na base e no topo, mínimo no P25 (onde o salário mínimo iguala os
grupos). P50/P10 é maior entre negros (2,6–3,1) que entre brancos (1,8–2,5): mais desigualdade na base.

**A4**: Gini 0,491 (2012) → 0,474 (2026). Parcela entre raças: Theil T 7,7% → 7,0%; Theil L 9,0% → 7,9%.

**A5 — 2026 T2**: chance de estar no **topo 10%** nacional: Negra 5,5% vs. Branca 15,6% (razão de chances 0,32; IC
0,30–0,33); Indígena 3,8% (0,21; 0,13–0,36). Na **base 10%**: Negra 13,2% vs. Branca 6,0% (2,38; 2,27–2,51). Em 2012:
0,28 e 2,67. Índice de representação de pessoas negras: 1,32 no D1, 0,55 no D10.

**A6**: a distribuição Branca **domina** a Negra em todos os 15 anos (diferença positiva e significativa em
todos os pontos; z mínimo 9,8, em 2016). Contra a Indígena: diferença positiva em todos os pontos de todos os anos, mas
significativa em todos os pontos só em 6 dos 15 anos (amostra pequena).

## 11. Afirmações permitidas

- "No 2º trimestre de 2026, pessoas negras ocupadas ganhavam, em média, 60% do que ganhavam pessoas brancas (renda
  do trabalho principal)."
- "Uma pessoa negra ocupada tem um terço da chance de uma pessoa branca de estar entre os 10% que mais ganham, e
  2,4 vezes a chance de estar entre os 10% que menos ganham."
- "Em qualquer valor de renda, a proporção de pessoas negras que ganham até esse valor é maior que a de pessoas
  brancas, em todos os anos de 2012 a 2026."

## 12. Afirmações proibidas

- Ler o IC de largura zero de um quantil como "sem incerteza".
- "Só 7% da desigualdade é racial" sem o contexto de Theil (ver regra do projeto).
