# Ficha de pesquisa — `C3` · Quanto da desvantagem da mulher negra é "raça", "gênero" e "interação"?

| Campo | Valor |
|---|---|
| ID no plano | `C3` (`docs/PLANO_DE_ANALISE.md`, Bloco C) |
| Onda | 2 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (proposto) |
| PR | `onda2/b-c` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

Da diferença de renda entre homens brancos (HB) e mulheres negras (MN), quanto se atribui a raça, quanto a gênero e
quanto ao termo não aditivo — sem que a resposta dependa da ordem em que se "tira" cada fator?

## 2. Tipo

`C`. Contabilidade de dois fatores; atribuir um termo de interação é convenção, não fato.

## 3. Estimando

Em log-pontos das médias (L_c = ln média da célula) e em R$:
- **Shapley** *(a confirmar: Shorrocks 2013)*: φ_raça = ½[(L_HB − L_HN) + (L_MB − L_MN)];
  φ_gênero = ½[(L_HB − L_MB) + (L_HN − L_MN)]; φ_raça + φ_gênero = L_HB − L_MN (exato).
- **Interação** (o que Shapley reparte meio a meio): I = (L_HB − L_HN) − (L_MB − L_MN), reportada à parte.
- **As duas ordens sequenciais** (raça primeiro; gênero primeiro), para mostrar a dependência de ordem (= ±I/2).
- Reconciliação com o existente: em R$, `decomposicao_raca_genero` usa efeito_raça = HB − HN, efeito_gênero = HB − MB,
  interação = −DiD; Shapley = efeito + interação/2.
- O mesmo para Indígena; ao lado, P4 e renda domiciliar per capita.

## 4. População

P1; P4; renda domiciliar per capita (anual).

## 5. Método

Linearização Estrato/UPA das 4 médias (z de cada célula), combinação linear dos ln → EP de cada componente.
Família FDR: não se aplica (componentes de uma identidade).

## 6. Dados

PNAD Contínua trimestral v2; anual v2.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Raça pesa mais** que gênero na desvantagem da mulher negra (P1) | φ_raça > φ_gênero |
| H2 | **Gênero pesa mais** em P4 (mulheres fora do mercado) | φ_gênero > φ_raça em P4 |
| H3 | **A ordem importa pouco** | |I|/2 < 10% do gap total |

## 8. O que refutaria

H1 é refutada se φ_raça − φ_gênero tiver IC incluindo zero ou for negativo (P1, último ano).

## 9. Armadilhas

- Shapley é uma regra de repartição, não uma descoberta: a interação é dividida meio a meio por definição.
- Escala: em R$ e em log os pesos mudam.
- A existente `decomposicao_raca_genero` é uma ordem sequencial específica (HB como base): não comparar seus
  "efeitos" com os de Shapley sem a reconciliação.

## 10. Resultados

`c123_racaxsexo_celulas.parquet` e `c123_racaxsexo_domiciliar_anual.parquet`. Distância homem branco − mulher negra,
log-pontos das médias (IC 95%):

| Conceito | Total | Shapley raça | Shapley gênero | % raça | φ_raça − φ_gênero | Interação (I) |
|---|---|---|---|---|---|---|
| P1, 2026T2 | 0,746 | **0,507 (0,486 a 0,528)** | 0,239 (0,228 a 0,251) | 68% | **+0,268 (0,246 a 0,290)** | 0,054 |
| P1, 2012T2 | 0,878 | 0,559 | 0,319 | 64% | +0,240 | 0,068 |
| P4, 2026T2 | 1,146 | 0,556 (0,533 a 0,578) | **0,591 (0,578 a 0,604)** | 48% | **−0,035 (−0,059 a −0,011)** | −0,020 |
| Domiciliar per capita, 2025 | 0,687 | 0,583 (0,558 a 0,608) | 0,105 (0,094 a 0,115) | 85% | +0,478 | −0,024 |

Em R$ (P1, 2026T2): total R$ 2.755 = raça R$ 1.849 + gênero R$ 906. **Ordem sequencial** (P1, 2026T2): "raça primeiro"
dá raça 0,534 + gênero 0,212; "gênero primeiro" dá gênero 0,266 + raça 0,480 — a diferença entre as ordens é I/2 = 0,027
lp (3,6% do total).

**Reconciliação com `decomposicao_raca_genero`** (R$, Mulher Negra, 2026T2): efeito_raça (HB − HN) = R$ 2.168,
efeito_gênero (HB − MB) = R$ 1.225, interação = −R$ 638 = −I. Shapley = efeito + interação/2: raça 2.168 − 319 = R$ 1.849;
gênero 1.225 − 319 = R$ 906. A tabela existente é a ordem "cada fator a partir de HB", não uma regra simétrica.

Indígena (P1): total 0,664 (0,389 a 0,939) = raça 0,516 + gênero 0,147 (IC de gênero inclui zero).

**Leitura das hipóteses.** H1 confirmada em P1 (raça 68% da distância; φ_raça − φ_gênero = +0,268, IC exclui zero) e na
renda domiciliar (85%). H2 confirmada: entre todos os adultos, gênero pesa um pouco mais que raça (φ_gênero −
φ_raça = 0,035, IC exclui zero). H3 confirmada: a ordem muda os componentes em 3,6% do total.

## 11. Afirmações permitidas

- "Da diferença de renda do trabalho entre homens brancos e mulheres negras ocupados (2º tri. 2026), cerca de dois
  terços se associam à raça e um terço ao gênero, numa divisão que não depende da ordem (Shapley)."
- "Contando todos os adultos, gênero e raça pesam quase o mesmo; na renda domiciliar por pessoa, a raça responde por
  85% da distância." (contabilidade, não mecanismo)

## 12. Afirmações proibidas

- "X% da desvantagem da mulher negra é racismo e Y% é machismo" (contabilidade ≠ mecanismo).

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
