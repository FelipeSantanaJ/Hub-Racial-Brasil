# Ficha de pesquisa — `B5` · Quanto da variação do hiato é ciclo e quanto é tendência?

| Campo | Valor |
|---|---|
| ID no plano | `B5` (`docs/PLANO_DE_ANALISE.md`, Bloco B) |
| Onda | 2 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 13/10/2026) |
| PR | `onda2/b-c` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

O hiato racial sobe ou desce com o ciclo econômico (medido pela taxa de desocupação), depois de descontar a
tendência? A resposta é diferente para quem trabalha (P1) e para todos os adultos (P4)?

## 2. Tipo

`D`. Associação entre duas séries; a taxa de desocupação é um indicador de ciclo, não uma causa isolável.

## 3. Estimando

c em hiato_t = α + β·t + c·desocupação_t + δ·pandemia_t + sazonalidade + e_t, em p.p. de hiato por p.p. de
desocupação; séries P1 e P4, Branca × Negra (total, homens, mulheres). Desocupação = desocupados ÷ força de
trabalho, 14+ (definição do IBGE), calculada dos microdados por trimestre. Também: variância da série explicada por
tendência vs. por ciclo (R² parciais).

## 4. População

P1 e P4 (Bloco T), como no S1.

## 5. Método

- **Estimador:** OLS sobre as séries publicadas (`sensibilidade_hiato_populacao`) + taxa de desocupação.
- **Incerteza:** EWC (ν = 5), Newey-West e GLS AR(1) ao lado; "associação confiável" só se os três concordam.
- **FDR:** família = as 6 séries (P1, P4 × total/homens/mulheres), BH sobre o p de c.

## 6. Dados

PNAD Contínua trimestral v2 (desocupação: `VD4001`, `VD4002`, `V1028`); tabelas do S1.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **P4 contracíclico:** na crise, pessoas negras perdem mais ocupação e o hiato entre todos os adultos sobe | c > 0 em P4 |
| H2 | **P1 pró-cíclico por seleção:** na crise saem de P1 os de menor renda (mais negros), e o hiato entre ocupados cai | c < 0 em P1 |
| H3 | **Sem ciclo:** o hiato é tendência + ruído | c com IC incluindo zero nas duas |

## 8. O que refutaria

- H1 é refutada se c em P4 (total) tiver IC EWC incluindo zero ou for negativo.
- H2 é refutada se c em P1 for ≥ 0 com IC excluindo zero.

## 9. Armadilhas

- Desocupação e hiato podem ter tendências comuns (ambos caem depois de 2021): sem o termo de tendência a associação
  seria espúria; com ele, o ciclo é identificado só pelos desvios.
- Pandemia: desocupação e coleta mudaram juntas; a dummy separa só o nível.
- 58 pontos: poder baixo para o termo de ciclo (reportar EMD).

## 10. Resultados

`b5_ciclo_tendencia.parquet` (+ `b5_taxa_desocupacao.parquet`). Coeficiente da desocupação em p.p. de hiato por p.p.
de desocupação, com tendência, dummy 2020–21 e trimestre (IC 95% EWC):

| População | Comparação | Coeficiente | Confiável (3 métodos)? | R² sem desocupação → com |
|---|---|---|---|---|
| P1 | Branca × Negra | +0,60 (0,20 a 1,00) | não (GLS AR(1) inclui zero) | 0,61 → 0,71 |
| P1 | mulheres | +0,56 (0,19 a 0,93) | não | 0,42 → 0,55 |
| P4 | Branca × Negra | **+1,58 (1,06 a 2,11)** | sim | 0,43 → 0,75 |
| P4 | homens | +1,62 (0,89 a 2,35) | sim | 0,51 → 0,76 |
| P4 | mulheres | +1,41 (0,97 a 1,85) | sim | 0,41 → 0,68 |

**Leitura das hipóteses.** H1 confirmada: entre todos os adultos, cada ponto de desocupação a mais está associado a
+1,6 p.p. no hiato (contracíclico). H2 refutada: em P1 o sinal também é positivo (não há queda do hiato por seleção na
crise); a associação não passa no critério dos três métodos. H3 refutada para P4. Desocupação e tendência juntas
explicam 75% da variância de P4; sem a desocupação, 43%.

## 11. Afirmações permitidas

- "Quando o desemprego sobe 1 ponto, o hiato de renda do trabalho entre todos os adultos brancos e negros sobe cerca
  de 1,6 ponto (IC 95%: 1,1 a 2,1), descontada a tendência."

## 12. Afirmações proibidas

- "O desemprego causa o hiato."

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
| 2026-10-13 | Felipe Santana | aprovada com ressalvas |
