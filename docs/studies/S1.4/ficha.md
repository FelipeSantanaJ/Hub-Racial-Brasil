# Ficha de pesquisa — `S1.4` · Margem extensiva (emprego) × intensiva (horas) × renda por hora

| Campo | Valor |
|---|---|
| ID no plano | `S1.4` (`docs/PLANO_DE_ANALISE.md`, Bloco S) |
| Onda | 1 (pendências) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 13/10/2026) |
| PR | `onda1/pendencias` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

A diferença racial na renda do trabalho por adulto (P4: todas as pessoas de 18+, quem está fora de P1 com zero)
vem de quantas pessoas estão em P1 (margem extensiva), de quantas horas trabalham (margem intensiva) ou de quanto
ganham por hora?

## 2. Tipo

`C`. Identidade contábil exata, sem causalidade: decompõe o hiato em três fatores que se multiplicam.

## 3. Estimando

Para o grupo g (pessoas de 18+), com totais ponderados T (pessoas), P (em P1), H (horas habituais semanais do
trabalho principal, `V4039`, em P1) e Y (renda `VD4016` real em P1):

    renda por adulto = Y/T = (P/T) × (H/P) × (Y/H)
                       = Pr(P1) × horas médias × renda por hora trabalhada

Em log-pontos, o hiato Branca × g se soma exatamente:

    ln(Ȳ_B/Ȳ_g) = Δ ln Pr(P1) + Δ ln horas + Δ ln renda por hora

Reporta cada termo (log-pontos, IC 95%) e a participação no total (%). A renda por hora é a razão de totais
(Y/H ÷ 4,345 semanas), ponderada pelas horas — não a média das rendas por hora individuais (essa é a do A7).
Comparações: Branca × Negra (total, homens, mulheres) e Branca × Indígena; todos os trimestres 2012T1–2026T2.

## 4. População

- **Universo:** pessoas de 18+ (Ignorado fora). Ocupados sem rendimento e não ocupados entram em T (contam como
  zero na renda por adulto).
- **Renda:** `VD4016` × deflator habitual (R$ do último trimestre).
- **Horas:** `V4039` (habituais, trabalho principal); sem ausentes em P1 (verificado: 0% nos 2º trimestres).
- **Sensibilidade:** a versão domiciliar está no T1; a versão por hora individual está no A7.

## 5. Método

- **Estimador:** razões de totais ponderados (`V1028`).
- **Incerteza:** linearização Estrato/UPA. Para ln X (X total), z_i = w_i x_i / X; cada termo é diferença de logs
  de razões de totais, e os três termos e o total saem numa única matriz de covariância
  (`variancia.variancia_linearizada` com z matricial).
- **FDR:** não se aplica (decomposição descritiva; leitura por IC).
- **Supressão:** Indígena por sexo não é publicado (n de P1 por trimestre pequeno para horas e renda por hora com
  CV aceitável); Indígena total sai com nota.

## 6. Dados

| Fonte | Variáveis | Período | Extrato / arquivo | Acesso |
|---|---|---|---|---|
| PNAD Contínua trimestral | `V2007`, `V2009`, `V2010`, `VD4002`, `VD4016`, `V4039`, deflator, `UPA`, `Estrato`, `V1028` | 2012T1–2026T2 | `data/raw/pnadc_extraido_v2` | público |

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **É renda por hora.** Negros trabalham quase tantas horas quanto brancos e estão em P1 em proporção parecida; a diferença está no valor da hora | Δ ln renda por hora ≥ 80% do total em todos os recortes |
| H2 | **Entre mulheres, a margem extensiva pesa.** Mulheres negras estão menos em P1 (S0.1: 49% × 54%) | Δ ln Pr(P1) responde por ≥ 15% do hiato das mulheres; < 5% para homens |
| H3 | **Horas compensam.** Negros trabalham mais horas, o que reduz o hiato mensal | Δ ln horas negativo |

## 8. O que refutaria

- H1 é refutada se a participação da renda por hora no hiato total ficar abaixo de 70% em Branca × Negra total.
- H2 é refutada se o termo de Pr(P1) para mulheres tiver IC que inclui zero no último trimestre.

## 9. Armadilhas

- A participação percentual de cada termo só tem leitura quando os três têm o mesmo sinal; com sinais opostos,
  reportar log-pontos, não %.
- Horas são **habituais declaradas** e sofrem heaping (40, 44 horas).
- Pandemia (2020–21): horas e P1 mudaram junto com a coleta por telefone (F6).
- "Renda por hora" mistura salário da ocupação e diferença de ocupação: não é "o preço do mesmo trabalho" (Bloco D).

## 10. Resultados

`s14_margens_intensiva_extensiva.parquet`, 2026T2, diferença Branca − grupo em log-pontos (IC 95%):

| Comparação | Total (renda por adulto) | Pr(P1) | Horas | Renda por hora | % renda por hora | % Pr(P1) |
|---|---|---|---|---|---|---|
| Branca × Negra | 0,541 | 0,036 (0,029 a 0,044) | 0,026 (0,022 a 0,029) | 0,479 (0,458 a 0,500) | **88,5** | 6,7 |
| Branca × Negra, homens | 0,545 | 0,011 (0,003 a 0,019) | 0,023 (0,019 a 0,027) | 0,511 (0,485 a 0,537) | 93,7 | 2,1 |
| Branca × Negra, mulheres | 0,566 | 0,086 (0,074 a 0,098) | 0,039 (0,033 a 0,044) | 0,441 (0,418 a 0,464) | 78,0 | **15,2** |
| Branca × Indígena | 0,605 | 0,069 (0,008 a 0,130) | 0,040 (−0,001 a 0,080) | 0,496 (0,366 a 0,627) | 82,0 | 11,4 |

Níveis em 2026T2: Pr(P1) 62,7% (Branca) × 60,5% (Negra); horas habituais 40,0 × 39,0 por semana; renda por hora
R$ 26,96 × R$ 16,70. Hiato da renda do trabalho por adulto = 71,8%.

No tempo (Branca × Negra, 2º trimestres): a parte de Pr(P1) sobe de 7,3% do total (2012) para 9,2% (2016) e **15,9%
(2020)**, e volta a 6,7% (2026). Entre mulheres: 15,4% → 17,2% → 23,5% → 15,2%.

**Leitura das hipóteses.** H1 confirmada: a renda por hora responde por 88,5% do hiato por adulto (IC do termo de
0,458 a 0,500 log-pontos). H2 confirmada: Pr(P1) responde por 15,2% do hiato entre mulheres e 2,1% entre homens.
H3 **refutada**: pessoas brancas declaram **mais** horas (+2,6 log-pontos), não menos; horas ampliam o hiato mensal.

## 11. Afirmações permitidas

- "Cerca de 9 em cada 10 partes do hiato racial de renda do trabalho por adulto vêm da diferença na renda por hora
  trabalhada; entre mulheres, 15% vêm de estar menos ocupadas com renda (2º tri. 2026)."
- "Na pandemia, a parte do hiato que vem de estar ou não ocupado com renda dobrou (de 7% em 2012 para 16% em 2020)."
  (com a ressalva da coleta por telefone, F6)

## 12. Afirmações proibidas

- "Pessoas negras ganham menos porque trabalham menos" ou o contrário, sem o número de cada termo.
- Ler a renda por hora como discriminação salarial.

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
| 2026-10-13 | Felipe Santana | aprovada com ressalvas |
