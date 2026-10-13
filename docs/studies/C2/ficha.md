# Ficha de pesquisa — `C2` · O hiato de gênero é igual dentro de cada raça? (interação formal)

| Campo | Valor |
|---|---|
| ID no plano | `C2` (`docs/PLANO_DE_ANALISE.md`, Bloco C) |
| Onda | 2 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (proposto) |
| PR | `onda2/b-c` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

O hiato de gênero é o mesmo entre pessoas brancas e negras? Equivalentemente: o hiato racial é o mesmo entre homens e
mulheres? A diferença (interação) mudou de 2012 a 2026?

## 2. Tipo

`D/C`. Interação descritiva (sem controles) e condicional (com controles); nenhuma é efeito causal.

## 3. Estimando

- **Log das médias:** I = [ln HB − ln HN] − [ln MB − ln MN] (DiD em log-pontos das médias aritméticas). I > 0: hiato
  racial maior entre homens que entre mulheres (em termos relativos).
- **Modelo:** ln y = β0 + β1·Negra + β2·Mulher + β3·Negra×Mulher (+ Indígena e suas interações) [+ idade, instrução,
  região na versão condicional]; β3 = interação em log-pontos da média geométrica.
- **R$:** DiD das médias aritméticas (comparável ao `interacao` de `decomposicao_raca_genero`, que é −DiD).
- Ao lado (Bloco T): a mesma DiD em log das médias de P4 e da renda domiciliar per capita (anual).
- Série trimestral; tendência de I com EWC (`tendencia.tendencia_hac`).

## 4. População

P1; P4; renda domiciliar per capita (anual, 18+, raça × sexo da pessoa).

## 5. Método

- **Incerteza:** linearização Estrato/UPA — para I, z = Σ ±(z_média/média) das 4 células; para β3, função de
  influência do WLS (X'WX)⁻¹x_i w_i e_i, linearizada por UPA.
- **FDR:** família = as 2 interações (Negra, Indígena) de um trimestre × especificação.
- **EMD:** para "a interação Indígena é zero", EMD = 2,8 × EP; reportar.

## 6. Dados

PNAD Contínua trimestral v2; anual v2.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Interseção multiplicativa:** os hiatos se compõem proporcionalmente (sem interação em log) | I com IC incluindo zero |
| H2 | **Achatamento pelo piso:** mulheres negras estão perto do salário mínimo, o que comprime o hiato racial entre mulheres | I > 0 (hiato racial menor entre mulheres) |
| H3 | **Dupla desvantagem super-aditiva** | I < 0 |

## 8. O que refutaria

H2 é refutada se I (log das médias, P1, último ano) tiver IC incluindo zero ou for negativo.

## 9. Armadilhas

- A conclusão depende da escala: em R$ a interação pode ter sinal oposto ao da interação em log (a existente é em R$).
- Indígena × sexo tem n pequeno: interação com IC largo (reportar EMD).
- Interação condicional (com controles) responde outra pergunta (mesmas características).

## 10. Resultados

`c123_racaxsexo_celulas.parquet` (DiD), `c2_interacao_regressao.parquet` (β3), `c2_interacao_tendencia.parquet`.
I > 0 = hiato racial maior entre homens que entre mulheres.

| Medida (Branca × Negra) | 2012T2 | 2026T2 (IC 95%) | Tendência 2012–2026 (EWC) |
|---|---|---|---|
| I, log das médias aritméticas, P1 | 0,068 | **0,054 (0,029 a 0,080)** | −0,0025/ano (−0,0036 a −0,0014), confiável |
| I em R$, P1 (= −`interacao` de `decomposicao_raca_genero`) | R$ 812 (2012T1) | R$ 638 (530 a 747) | −16 R$/ano, confiável |
| β3 (média geométrica), sem controles, P1 | 0,032 (0,014 a 0,049) | 0,003 (−0,014 a 0,021) | — |
| β3 com controles (idade, instrução, região), P1 | 0,019 (0,004 a 0,034) | −0,006 (−0,021 a 0,009) | — |
| I, log das médias, P4 (todos os adultos) | −0,005 | −0,020 (−0,049 a 0,008) | −0,0026/ano, confiável |
| I, renda domiciliar per capita (2025) | −0,008 | −0,024 (−0,048 a 0,001) | — |

Hiato racial entre homens 0,534 e entre mulheres 0,480 (P1, log-pontos, 2026T2); hiato de gênero entre brancos 0,266 e
entre negros 0,212. **Indígena:** I = 0,238 (−0,058 a 0,534) em P1 — IC largo; EMD ≈ 0,42 lp: não dá para afirmar nem
negar interação para Indígena.

**Leitura das hipóteses.** H2 confirmada **para médias aritméticas**: o hiato racial é menor entre mulheres que entre
homens (I = 0,054), e a diferença está diminuindo. Na média geométrica (o "meio" da distribuição) a interação existia
em 2012 e **desapareceu** em 2026 (β3 = 0,003): **H1 vale hoje para a média geométrica**. Entre todos os adultos (P4) e na
renda domiciliar, a interação não se distingue de zero. H3 refutada (I nunca é negativa com IC excluindo zero).

## 11. Afirmações permitidas

- "Entre quem trabalha, a diferença racial de renda média é um pouco menor entre mulheres (as negras ganham 62% do que
  ganham as brancas) do que entre homens (59%); essa diferença entre os sexos vem diminuindo."
- "No meio da distribuição (média geométrica), raça e gênero hoje se combinam de forma multiplicativa, sem interação."

## 12. Afirmações proibidas

- "Ser mulher negra é menos grave que a soma" a partir de interação em R$ (depende da escala).

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
