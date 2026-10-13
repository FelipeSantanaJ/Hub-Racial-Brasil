# Ficha de pesquisa — `C1` · Quatro células raça × sexo: ranking e hiatos

| Campo | Valor |
|---|---|
| ID no plano | `C1` (`docs/PLANO_DE_ANALISE.md`, Bloco C) |
| Onda | 2 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (proposto) |
| PR | `onda2/b-c` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

Como se ordenam homens brancos, mulheres brancas, homens negros e mulheres negras (e as células indígenas) em renda
— média, quantis e desigualdade — e quanto cada célula ganha em relação aos homens brancos, entre quem trabalha (P1),
entre todos os adultos (P4) e na renda domiciliar per capita?

## 2. Tipo

`D`. Métricas do A2–A4 aplicadas às células.

## 3. Estimando

Para cada célula c ∈ {Branca, Negra, Indígena} × {Homem, Mulher}, referência = homem branco (HB):
- A2: média, razão HB/c, log-pontos, "c ganha X% da renda de HB" (P1, P4 e renda domiciliar per capita);
- A3: P10, P50, P90 e razão HB/c em cada um (P1; bootstrap);
- A4: Theil T e L entre as 6 células e participação "entre" no total (P1).
Série trimestral 2012T1–2026T2 (A2, P1 e P4); A3 nas janelas 2012T2 e 2026T2; renda domiciliar anual 2012–2025.

## 4. População

P1; P4 (todas as pessoas 18+, fora de P1 com renda zero); renda domiciliar per capita (`VD5008`, todas as pessoas
de 18+, por raça × sexo **da pessoa**).

## 5. Método

- **Estimador:** médias e razões ponderadas; quantis `pnadc_core.quantil_ponderado`; Theil de `bloco_a`.
- **Incerteza:** linearização Estrato/UPA (método delta para razão e log); quantis por bootstrap Rao-Wu (200).
- **FDR:** família = as 5 comparações com HB de um trimestre × conceito (BH).
- **Supressão:** n < 30 ou CV > 30% (Indígena × sexo é publicável trimestre a trimestre: n mínimo histórico 136).

## 6. Dados

PNAD Contínua trimestral v2 e anual v2.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Ordem raça antes de gênero:** HB > MB > HN > MN em P1 | Média de MB > HN |
| H2 | **Ordem gênero antes de raça** | HN > MB |
| H3 | **P4 reordena:** com quem está fora de P1 (mais mulheres), MB cai abaixo de HN | Em P4, HN > MB mesmo que em P1 MB > HN |

## 8. O que refutaria

H1 é refutada se o IC da diferença MB − HN (P1, último trimestre) incluir zero ou for negativo.

## 9. Armadilhas

- Mulher negra não é "soma" de dois hiatos (interação é o C2).
- Médias puxadas pelo topo; ler com os quantis.
- Renda domiciliar per capita é partilhada no domicílio: a "renda" de uma mulher fora do mercado reflete a do cônjuge.

## 10. Resultados

`c123_racaxsexo_celulas.parquet` (série trimestral, P1 e P4), `c123_racaxsexo_domiciliar_anual.parquet`,
`c1_quantis_celulas.parquet`, `c1_theil_celulas.parquet`. 2026T2, média em R$ (IC 95%) e % da renda do homem branco:

| Célula | P1 (ocupados com renda) | % de HB | P4 (todos os adultos) | % de HB | Domiciliar per capita 2025 |
|---|---|---|---|---|---|
| Homens brancos (HB) | 5.238 (5.109 a 5.368) | 100 | 3.835 | 100 | 3.452 |
| Mulheres brancas (MB) | 4.013 (3.926 a 4.100) | **77** | 2.146 (2.095 a 2.196) | **56** | 3.146 |
| Homens negros (HN) | 3.070 (3.031 a 3.110) | **59** | 2.223 (2.191 a 2.254) | **58** | 1.950 |
| Mulheres negras (MN) | 2.483 (2.446 a 2.521) | 47 | 1.219 | 32 | 1.736 |
| Homens indígenas | 2.775 (2.451 a 3.098) | 53 | 1.969 | 51 | 1.703 |
| Mulheres indígenas | 2.697 (1.958 a 3.437; CV 14%) | 51 | 1.296 | 34 | 1.628 |

Razão HB/célula em log-pontos (P1, 2026T2): MB 0,266 (0,247 a 0,285); HN 0,534 (0,509 a 0,560); MN 0,746 (0,721 a
0,772). Em 2012: 0,353; 0,592; 0,878 — as três distâncias diminuíram. Quantis (2026T2, log HB/célula): MN 0,99 no
P10, 0,51 no P50, 0,80 no P90; MB 0,30 / 0,18 / 0,22 (valores redondos: P10 de MN = R$ 600, P90 de HB = R$ 10.000).
Theil T: a parte **entre** as 8 células raça × sexo é 8,5% da desigualdade total em 2026T2 (10,2% em 2012); entre raças
7,0%, entre sexos 1,3%.

**Leitura das hipóteses.** H1 confirmada em P1: MB − HN = +0,268 lp (0,246 a 0,290) — mulheres brancas ganham mais que
homens negros. H2 refutada. **H3 confirmada:** entre todos os adultos (P4), homens negros passam as mulheres brancas
(ln MB − ln HN = −0,035; −0,059 a −0,011), porque muito mais mulheres estão fora de P1. Na renda domiciliar per capita a
ordem é dominada por raça (homens e mulheres do mesmo grupo dividem o domicílio): MB 3.146 contra HN 1.950.

## 11. Afirmações permitidas

- "Entre quem trabalha com renda (2º tri. 2026), mulheres negras ganham em média 47% do que ganham homens brancos;
  mulheres brancas, 77%; homens negros, 59%."
- "Contando todos os adultos (quem não tem renda do trabalho entra com zero), homens negros passam à frente das
  mulheres brancas, e mulheres negras ficam com 32% da renda do trabalho por homem branco."

## 12. Afirmações proibidas

- Ler o ranking como "quem sofre mais discriminação".

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
