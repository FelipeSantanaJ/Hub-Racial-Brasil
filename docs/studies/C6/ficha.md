# Ficha de pesquisa — `C6` · Estado conjugal e chefia do domicílio: renda e oferta de trabalho por raça

| Campo | Valor |
|---|---|
| ID no plano | `C6` (`docs/PLANO_DE_ANALISE.md`, Bloco C) |
| Onda | 2 (feito depois do ponto de parada, por decisão do Felipe em 13/10/2026) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-14 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 14/10/2026) |
| PR | `onda2/b-c` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

Ser a pessoa responsável pelo domicílio e viver em casal estão associados de forma diferente à ocupação com renda, às
horas e à renda de pessoas brancas e negras (por sexo)? E controlar por essas condições muda o hiato racial de renda?

## 2. Tipo

`C`. Associação condicional em corte transversal. **Endogeneidade forte:** casar, chefiar e ter filhos são escolhas
condicionadas pela renda; nenhum coeficiente é efeito causal. "Controlar" por essas variáveis pode absorver parte do
próprio hiato (são mediadoras).

## 3. Estimando

- Coeficientes de `chefe` (`V2005` = 01) e `em_casal` (responsável com cônjuge no domicílio, ou cônjuge `V2005` 02/03)
  em: (a) Pr(P1) (p.p.); (b) ln renda em P1; (c) horas habituais em P1 (`V4039`). Controles: idade (anos simples),
  instrução, região, filho(a) de 0–5 (definição do C4). Por raça (Branca, Negra) × sexo; diferença Negra − Branca.
- Hiato racial condicional em ln renda (coeficiente de Negra), por sexo, com controles básicos (idade, instrução,
  região) e com + chefia, casal e filho pequeno; e a **mudança** do coeficiente.
- Pessoas de 25–59 anos; janelas 2012 e 2025T3–2026T2.

## 4. População

Pessoas de 25–59 anos (Branca, Negra; Ignorado e Amarela fora; Indígena fora por amostra). Renda `VD4016` real.

## 5. Método

- **Estimador:** WLS (`V1028`); `bloco_c.wls_design` com ψ só dos coeficientes de interesse.
- **Incerteza:** linearização da função de influência por Estrato/UPA; universo da linearização = pessoas de 25–59 da
  janela. Diferenças entre raças e entre especificações pela diferença dos ψ (mesma amostra).
- **FDR:** família = os coeficientes (2 condições × 3 desfechos × diferença racial) de um sexo × janela.
- **EMD:** reportado para as diferenças raciais (2,8 × EP).

## 6. Dados

PNAD Contínua trimestral v2 (`V2005`, `V1008`, `V1014`, `V2009`, `V2007`, `V2010`, `VD3004`, `UF`, `VD4002`,
`VD4016`, `V4039`).

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Prêmio do chefe/casado é maior para homens brancos** (sinal de "provedor" valorizado) | Coeficiente de casal em ln renda dos homens maior para Branca |
| H2 | **Chefia feminina negra é sobretudo necessidade** (mulher negra chefe sem cônjuge trabalha mais, ganha menos) | Para mulheres negras: chefe ↑ Pr(P1) e horas, sem prêmio de renda |
| H3 | **Arranjo familiar explica pouco do hiato** | Mudança do coeficiente de Negra < 10% do hiato condicional básico |

## 8. O que refutaria

- H3 é refutada se a inclusão de chefia, casal e filho reduzir o coeficiente de Negra em mais de 10% (em módulo) com IC
  da mudança excluindo zero.
- H1 é refutada se a diferença Negra − Branca no coeficiente de casal (homens, ln renda) tiver IC incluindo zero.

## 9. Armadilhas

- Causalidade reversa (renda alta → casar; renda baixa → morar com os pais).
- "Chefe" é declarado pelo informante; em casais, a convenção de quem é o responsável mudou no tempo (a confirmar).
- Pessoas que moram com os pais (filhos adultos) ficam como não chefes e não em casal: o grupo de referência mistura
  solteiros que moram sozinhos e filhos adultos.
- Mediação: controlar por arranjo familiar não é "explicar" o hiato.

## 10. Resultados

`c6_conjugal_chefia.parquet` e `c6_hiato_condicional.parquet`. Pessoas de 25–59 anos; coeficientes com idade, instrução,
região e filho(a) de 0–5 (IC 95%). Janela 2025T3–2026T2:

| Sexo | Desfecho | Condição | Branca | Negra | Negra − Branca |
|---|---|---|---|---|---|
| Homens | ln renda (P1) | em casal | +0,213 (0,195 a 0,230) | +0,157 (0,145 a 0,170) | **−0,055 (−0,076 a −0,035)** |
| | ln renda (P1) | chefe | +0,108 | +0,102 | −0,005 (−0,024 a 0,013) |
| | Pr(P1), p.p. | em casal | +11,5 | +11,9 | +0,4 (−0,5 a 1,3) |
| | horas (P1) | em casal | +1,5 | +1,2 | −0,3 (−0,6 a −0,05) |
| Mulheres | ln renda (P1) | chefe | +0,006 (−0,010 a 0,022) | **−0,043 (−0,056 a −0,030)** | −0,048 (−0,069 a −0,028) |
| | ln renda (P1) | em casal | +0,104 | +0,085 | −0,018 (−0,040 a 0,003) |
| | Pr(P1), p.p. | em casal | −3,2 | −4,8 | −1,6 (−2,7 a −0,5) |
| | Pr(P1), p.p. | chefe | +1,4 | +1,7 | +0,3 (−0,8 a 1,3) |
| | horas (P1) | chefe | −0,7 | −1,0 | −0,3 (−0,6 a −0,02) |

**Hiato racial condicional** (coeficiente de Negra em ln renda, P1, controles básicos → + chefia, casal e filho 0–5):
homens −0,136 → −0,139 (mudança −0,002; −0,004 a −0,001; 1,7%); mulheres −0,162 → −0,158 (mudança +0,004; 0,003 a 0,005;
−2,5%). Em 2012: homens −0,151 → −0,147; mulheres −0,138 → −0,140.

Em 2012 o padrão era parecido, com duas diferenças: o "prêmio" de chefia para mulheres existia nos dois grupos (+0,12 Branca,
+0,10 Negra) e a chefia estava associada a +12 a +14 p.p. de Pr(P1) para mulheres (em 2025–26, +1,4 a +1,7).

**Leitura das hipóteses.** H3 confirmada: o arranjo familiar muda o hiato racial condicional em menos de 2,5% (as mudanças
são estatisticamente distinguíveis de zero, mas pequenas). H1 confirmada: o "prêmio" de renda de viver em casal é maior para
homens brancos (+0,21) que para negros (+0,16). H2 em parte: mulheres negras chefes ganham **menos** que as não chefes
(−4 log-pontos; para brancas, nenhuma diferença), mas não trabalham mais horas nem estão mais ocupadas que as brancas chefes
— o padrão de "necessidade" aparece na renda, não na oferta de trabalho.

## 11. Afirmações permitidas

- "Com a mesma idade, escolaridade e região, a estrutura familiar (chefia, viver em casal, filho pequeno) quase não muda o
  hiato racial de renda: ele cai menos de 3% quando se leva isso em conta."
- "Entre homens que vivem em casal, a renda é mais alta que entre os demais nas duas raças, mas a diferença é maior entre
  brancos (associação, não efeito)."

## 12. Afirmações proibidas

- "Casar aumenta a renda dos homens brancos."
- "O hiato é explicado pela estrutura familiar."

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
