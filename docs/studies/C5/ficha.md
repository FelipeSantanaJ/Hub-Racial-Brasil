# Ficha de pesquisa — `C5` · Trabalho doméstico remunerado e o hiato das mulheres

| Campo | Valor |
|---|---|
| ID no plano | `C5` (`docs/PLANO_DE_ANALISE.md`, Bloco C) |
| Onda | 2 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (proposto) |
| PR | `onda2/b-c` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

Quanto do emprego das mulheres negras está no trabalho doméstico remunerado, como isso mudou de 2012 a 2026, e quanto
do hiato de renda entre mulheres brancas e negras está associado a essa diferença de inserção?

## 2. Tipo

`D` (participação e renda) e `C` (decomposição de Kitagawa da diferença de médias).

## 3. Estimando

- % das ocupadas (P1) em trabalho doméstico (`VD4009` = 03 com carteira ou 04 sem carteira), por raça; e, ao lado
  (Bloco T), % das mulheres de 18+ (todas) que são trabalhadoras domésticas.
- % com carteira entre as domésticas, por raça; renda média das domésticas por raça e hiato dentro do trabalho
  doméstico.
- **Kitagawa** da diferença de renda média Branca − Negra entre mulheres em P1, com duas "posições"
  (doméstica × outras): diferença = Σ (s_B − s_N)·(m_B + m_N)/2 [composição] + Σ (m_B − m_N)·(s_B + s_N)/2 [dentro].
  Contrafactual: renda média das mulheres negras se tivessem a % de domésticas das brancas, mantidas as médias.
- Série trimestral; tendência da participação com EWC.

## 4. População

Mulheres de 18+: P1 (participação entre ocupadas com renda e renda) e todas (Bloco T).

## 5. Método

- **Incerteza:** linearização Estrato/UPA (proporções e médias de domínio); componentes de Kitagawa por
  combinação dos z das médias e proporções.
- **FDR:** não se aplica (descrição com IC).

## 6. Dados

PNAD Contínua trimestral v2 (`VD4009`, `VD4002`, `VD4016`, `V2007`, `V2010`, `V2009`).

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **O doméstico ainda concentra mulheres negras** | % das ocupadas negras em doméstico ≥ 1,5 × a das brancas em 2026 |
| H2 | **Declínio do doméstico** reduz o hiato entre mulheres | % de domésticas negras cai no período e o componente de composição do Kitagawa diminui |
| H3 | **O hiato está dentro, não entre**: a maior parte do hiato entre mulheres está fora do doméstico | Componente "dentro" > 75% |

## 8. O que refutaria

H1 é refutada se a razão Negra/Branca da % de domésticas tiver IC incluindo 1,5 ou abaixo em 2026T2.

## 9. Armadilhas

- `VD4009` 03/04 = trabalhador doméstico (inclui diaristas); subdeclaração de vínculo e de renda.
- A decomposição em duas posições é grossa; a posição "outras" mistura tudo (Bloco D faz melhor).
- Composição muda com a idade: domésticas são mais velhas.

## 10. Resultados

`c5_trabalho_domestico.parquet` (trimestral, com `n`, `cv`, `publicavel`) e `c5_tendencia.parquet`. Mulheres de 18+:

| Indicador (2º tri.) | 2012 | 2026 (IC 95%) | Tendência/ano (EWC) |
|---|---|---|---|
| % domésticas entre as ocupadas com renda — Negra | 20,6% | **14,3% (13,9 a 14,7)** | −0,40 p.p. (−0,47 a −0,34), confiável |
| idem — Branca | 11,1% | **7,9% (7,5 a 8,3)** | −0,21 p.p., confiável |
| Razão Negra ÷ Branca | 1,85 | **1,82 (1,72 a 1,91)** | — |
| % domésticas entre todas as mulheres 18+ (Bloco T) — Negra × Branca | 9,4% × 5,6% | 7,0% × 4,2% | ambas caem, confiável |
| % com carteira entre as domésticas — Negra × Branca | 28,8% × 36,0% | 22,2% × 23,7% | — |
| Hiato % dentro do trabalho doméstico (Branca ÷ Negra − 1) | 16,0% | 17,0% (12,7 a 21,3) | — |
| Diferença de renda média, mulheres em P1 (R$ de 2026T2) | 1.312 | 1.530 (1.444 a 1.616) | — |
| Kitagawa: composição (doméstica × outras) | R$ 147 (11,2%) | **R$ 128 (8,4%; 7,7 a 9,1)** | −0,13 p.p./ano no %, confiável |
| Kitagawa: dentro das posições | R$ 1.165 | R$ 1.402 (91,6%) | — |

Contrafactual (contábil): com a % de domésticas das mulheres brancas, a renda média das mulheres negras em P1 seria
R$ 2.569 (2.529 a 2.609), contra R$ 2.483 observados. Indígena: % de domésticas 12,7% (8,9 a 16,6); % com carteira e
renda das domésticas indígenas não publicáveis na maior parte dos trimestres (regra n ≥ 30 e CV ≤ 30%).

**Leitura das hipóteses.** H1 confirmada: a proporção de domésticas entre as ocupadas negras é 1,82 vez a das brancas
(IC exclui 1,5), razão estável desde 2012. H2 parcialmente: o trabalho doméstico encolheu (−6 p.p. entre as negras) e a
parte do hiato entre mulheres associada a ele caiu de 11% para 8%, mas o hiato total em R$ aumentou. H3 confirmada:
92% da diferença está **dentro** das posições. A formalização das domésticas caiu nos dois grupos (carteira de 29–36%
para 22–24%).

## 11. Afirmações permitidas

- "Em 2026, 14% das mulheres negras ocupadas com renda eram trabalhadoras domésticas, contra 8% das brancas — quase o
  dobro, a mesma proporção de 2012, embora as duas taxas tenham caído."
- "A concentração no trabalho doméstico responde por cerca de 8% da diferença de renda entre mulheres brancas e negras;
  o resto está dentro das mesmas posições." (contábil)

## 12. Afirmações proibidas

- "Se não houvesse trabalho doméstico, o hiato seria X" (contrafactual contábil, não causal).

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
