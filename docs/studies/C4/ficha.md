# Ficha de pesquisa — `C4` · Penalidade da maternidade por raça

| Campo | Valor |
|---|---|
| ID no plano | `C4` (`docs/PLANO_DE_ANALISE.md`, Bloco C) |
| Onda | 2 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 13/10/2026) |
| PR | `onda2/b-c` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

Mulheres de 25 a 44 anos com filho(a) de 0 a 5 anos no domicílio estão menos ocupadas com renda e ganham menos que as
sem filho pequeno, com a mesma idade, escolaridade e região? Essa diferença ("penalidade") é maior para mulheres
negras que para brancas? E para homens (contraste)?

## 2. Tipo

`C/D`. Associação condicional em corte transversal. **Não é efeito causal** de ter filho (quem tem filho pequeno
difere em características não observadas; a PNADC não tem painel longo para um event-study de nascimento).

## 3. Estimando

- **Mãe/pai de criança 0–5 (definição principal):** pessoa responsável (`V2005` = 01) com criança de 0–5 que é filha
  do responsável (`V2005` 04 ou 05), ou cônjuge (02/03) com criança 0–5 filha do casal ou enteada (04 ou 06), no mesmo
  domicílio (chave `UPA`+`V1008`+`V1014`). Sensibilidade: "há criança de 0–5 no domicílio" (qualquer parentesco).
- Desfechos: (a) Pr(P1) (margem extensiva); (b) ln renda em P1 (intensiva); (c) renda do trabalho por pessoa,
  fora de P1 = 0 (P4 — versão do Bloco T).
- Penalidade_g = coeficiente de "mãe 0–5" na regressão do desfecho em mãe 0–5 + idade (anos simples) + instrução +
  região, para cada raça g; diferença Negra − Branca. Em p.p. (a, c em % da média de quem não tem filho) e log-pontos (b).
- Por faixa 25–34 e 35–44; homens no mesmo desenho. Janelas 2012 e 2025T3–2026T2.

## 4. População

Pessoas de 25–44 anos (Branca, Negra; Indígena com nota de amostra), por sexo. Excluídas: pessoas que não são
responsável nem cônjuge ficam só na definição de sensibilidade.

## 5. Método

- **Estimador:** WLS (`V1028`) com dummies; penalidade = coeficiente.
- **Incerteza:** linearização da função de influência do WLS por Estrato/UPA (`bloco_c.wls_design`). Universo da
  linearização = pessoas de 25–44 anos da janela (ajuste feito ao rodar, por memória: UPAs sem ninguém nessa idade
  ficam fora, aproximação de domínio documentada em `variancia.py`).
- **FDR:** família = as penalidades (3 desfechos × 2 raças) de um sexo × janela.
- **EMD:** para "a penalidade não difere por raça", EMD = 2,8 × EP da diferença.

## 6. Dados

PNAD Contínua trimestral v2 (`V2005`, `V1008`, `V1014`, `V2009`, `V2007`, `V2010`, `VD3004`, `UF`, `VD4002`,
`VD4016`).

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Penalidade maior para negras** (menos acesso a creche, rede de apoio, trabalho formal com licença) | Penalidade em Pr(P1) mais negativa para Negra |
| H2 | **Penalidade maior para brancas** (mais renda do cônjuge permite sair do mercado) | Penalidade em Pr(P1) mais negativa para Branca |
| H3 | **Prêmio de paternidade** para homens, sem diferença racial | Coeficiente ≥ 0 para homens nas duas raças |

## 8. O que refutaria

H1 é refutada se a diferença Negra − Branca na penalidade em Pr(P1) for ≥ 0 ou tiver IC incluindo zero (2025–26).

## 9. Armadilhas

- **Seleção para a maternidade** (idade da primeira gestação difere por raça): controlar por idade em anos simples.
- **Corresidência:** só se vê a criança se ela mora no domicílio; mães que não moram com os filhos ficam como "sem".
- Avós e outras parentes cuidadoras ficam fora da definição principal (e dentro da de sensibilidade).
- Controlar por escolaridade pode absorver efeito (escolaridade e fecundidade são conjuntas).

## 10. Resultados

`c4_penalidade_maternidade.parquet`. Coeficiente de "filho(a) de 0–5 no domicílio" com idade (anos simples),
instrução e região; responsáveis e cônjuges de 25–44 anos (definição principal). IC 95%:

| Janela · sexo | Desfecho | Branca | Negra | Negra − Branca | % da média de quem não tem filho (B × N) |
|---|---|---|---|---|---|
| 2025–26 · mulheres | Pr(P1), p.p. | −13,8 (−15,0 a −12,5) | −15,8 (−16,8 a −14,8) | **−2,0 (−3,6 a −0,5)** | −17,6% × −23,7% |
| | ln renda em P1 | −0,015 (−0,043 a 0,013) | **−0,073 (−0,095 a −0,052)** | −0,058 (−0,092 a −0,024) | — |
| | renda do trabalho por mulher (fora de P1 = 0), R$ | −244 (−389 a −98) | −376 (−429 a −324) | −133 (−288 a 22) | −7,3% × −21,3% |
| 2012 · mulheres | Pr(P1), p.p. | −12,8 | −13,3 | −0,5 (−1,9 a 1,0); EMD 2,1 p.p. | −18,7% × −22,0% |
| | ln renda em P1 | −0,015 (n.s.) | −0,061 | −0,045 (−0,074 a −0,017) | — |
| 2025–26 · homens | Pr(P1), p.p. | +1,7 (1,1 a 2,4) | +2,5 (1,9 a 3,0) | +0,7 (−0,1 a 1,5) | — |
| | ln renda em P1 | **+0,058 (0,034 a 0,082)** | +0,009 (−0,007 a 0,024) | −0,049 (−0,078 a −0,021) | — |

Por idade (mulheres, Pr(P1), 2025–26): 25–34 anos −16,6 (B) × −18,2 (N), diferença −1,6 (−3,9 a 0,7); 35–44 anos
−10,8 × −12,7, diferença −1,9 (−4,2 a 0,4) — cada faixa sozinha não tem poder para a diferença. Sensibilidade (qualquer
criança de 0–5 no domicílio, todas as pessoas): mesma direção, Negra − Branca em Pr(P1) de −2,3 (−3,7 a −0,8).
Indígena: penalidade em Pr(P1) de −11,0 (−20,3 a −1,7), IC largo.

**Leitura das hipóteses.** H1 confirmada em 2025–26: a queda em Pr(P1) associada a ter filho pequeno é 2 p.p. maior para
mulheres negras (IC exclui zero, p ajustado 0,02); em 2012 a diferença não era distinguível (EMD 2,1 p.p.). Entre as que
estão em P1, só as mães negras ganham menos que as não mães (−7 log-pontos). H2 refutada. H3 refutada: há "prêmio de
paternidade" de renda para homens brancos (+5,8 lp) e não para negros (+0,9, n.s.).

## 11. Afirmações permitidas

- "Entre mulheres de 25 a 44 anos, ter filho de até 5 anos em casa está associado a 16 pontos a menos na chance de estar
  ocupada com renda para as negras e 14 para as brancas, comparando mulheres com a mesma idade, escolaridade e região."
  (associação, não efeito)
- "Pais brancos com filhos pequenos ganham mais que homens brancos sem filhos pequenos; entre homens negros, não há
  essa diferença."

## 12. Afirmações proibidas

- "Ter filho reduz a renda das mulheres negras em X%" (causal).

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
| 2026-10-13 | Felipe Santana | aprovada com ressalvas |
