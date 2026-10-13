# Ficha de pesquisa — `S1.3` · Limites do hiato sob suposições explícitas sobre quem não é observado

| Campo | Valor |
|---|---|
| ID no plano | `S1.3` (`docs/PLANO_DE_ANALISE.md`, Bloco S) |
| Onda | 1 (pendências) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (proposto) |
| PR | `onda1/pendencias` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

Se a renda do trabalho que as pessoas de 18+ fora de P1 teriam ("renda potencial") fosse conhecida, qual seria o
hiato racial? Como não é, que intervalo de hiatos é compatível com os dados sob cada suposição explícita sobre
essa renda — e o sinal do hiato (Branca > Negra) se mantém em todas?

## 2. Tipo

`C`. Identificação parcial (limites), sem modelo de seleção. **Por que não Heckman:** a correção de Heckman exige
uma variável que mude a chance de estar em P1 sem mudar a renda potencial (restrição de exclusão). As candidatas
usuais na PNADC — filhos pequenos, estado conjugal, renda de outros moradores, transferências — afetam também a
renda potencial (penalidade da maternidade, escolha de ocupação, salário de reserva) e diferem por raça; nenhuma é
crível. Sem ela, o Heckman identifica só pela forma funcional (normalidade), que é justamente o que queremos evitar.

## 3. Estimando

Para o grupo g, θ_g = média (ou mediana) da renda potencial do trabalho principal entre **todas** as pessoas de 18+
do grupo. Com p_g = Pr(P1 | g) e F_obs,g a distribuição observada em P1:

| Suposição (S) | Limites de θ_g (média) | Limites de θ_g (mediana) |
|---|---|---|
| S-a **sem suposição** (só suporte [0, y_max]; y_max = P99 nacional de P1 na janela) | [p·m, p·m + (1−p)·y_max] | Manski: [Q(1 − 0,5/p), Q(0,5/p)] se p > 0,5; senão [0, y_max] |
| S-b **seleção positiva** (quem está fora ganharia no máximo a média do próprio grupo; dominância estocástica para a mediana) | [p·m, m] | [Q(1 − 0,5/p) ou 0, mediana observada] |
| S-c **seleção positiva com piso** (quem está fora ganharia entre o P10 observado do grupo e a média) | [p·m + (1−p)·P10, m] | não se aplica |
| S-d **aparamento à la Lee** *(a confirmar: Lee 2009)* | o grupo com maior p é aparado em (p_maior − p_menor)/p_maior pelo topo (limite inferior) ou pela base (limite superior); o outro fica na média observada | não se aplica |

Hiato % = 100 × (θ_Branca/θ_grupo − 1) ∈ [100·(L_B/U_g − 1), 100·(U_B/L_g − 1)].
Comparações: Branca × Negra (total, homens, mulheres), Branca × Indígena. Janelas: 2012 e 2025T3–2026T2.

## 4. População

- **Universo:** pessoas de 18+ (Ignorado fora). P1 = ocupados com `VD4016` > 0.
- **Renda:** `VD4016` real (deflator habitual), R$ do trimestre de referência de cada visita (as 4 visitas da
  janela ficam empilhadas; a diferença de preços dentro de um ano é pequena e igual para os grupos).
- **Exclusões:** não há; o ponto é justamente incluir quem P1 exclui.

## 5. Método

- **Estimador:** fórmulas da tabela acima, com médias, quantis (`pnadc_core.quantil_ponderado`) e médias aparadas
  ponderadas. S-d é uma leitura de sensibilidade: Lee foi feito para efeitos de tratamento com monotonicidade; aqui
  "raça" não é tratamento, e o aparamento só pergunta "e se os que sobram no grupo de maior participação fossem os
  de maior/menor renda?".
- **Incerteza:** bootstrap de Rao-Wu Estrato/UPA (`bloco_a.multiplicadores_rao_wu`, 200 réplicas) para os dois
  limites; IC de Imbens–Manski *(a confirmar: Imbens & Manski 2004)*: [L − c·σ_L, U + c·σ_U], com c tal que
  Φ(c + Δ/max(σ_L, σ_U)) − Φ(−c) = 0,95 (Δ = U − L). y_max fica fixo (não reamostrado).
- **FDR:** não se aplica (limites, sem teste de hipótese nula pontual).
- **EMD:** não se aplica.
- **Supressão:** Indígena com n < 30 em P1 numa janela não sai (não deve ocorrer em 4 trimestres).

## 6. Dados

| Fonte | Variáveis | Período | Extrato / arquivo | Acesso |
|---|---|---|---|---|
| PNAD Contínua trimestral | `V2007`, `V2009`, `V2010`, `VD4002`, `VD4016`, deflator, `UPA`, `Estrato`, `V1028` | 2012; 2025T3–2026T2 | `data/raw/pnadc_extraido_v2` | público |

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **O hiato de P1 subestima o hiato potencial** (os excluídos negros teriam renda mais baixa que os brancos excluídos) | Sob S-b/S-c, o limite superior do hiato bem acima do hiato de P1; limite inferior perto de P1 |
| H2 | **A seleção é parecida entre grupos** (p_Branca ≈ p_Negra) | Limites S-d estreitos (poucos p.p. em torno de P1), sobretudo para homens |
| H3 | **Sem suposição, nada se sabe** | Limites S-a contendo zero (sinal não identificado) |

## 8. O que refutaria

- A conclusão "o hiato racial existe para além do recorte" é refutada se o limite **inferior** do hiato sob S-b
  (ou S-c) for ≤ 0 em alguma comparação Branca × Negra.
- H2 é refutada se a largura dos limites S-d passar de 10 p.p. para mulheres.

## 9. Armadilhas

- **y_max** escolhido (P99) é arbitrário; o limite S-a é dominado por ele. Reportar como "sem suposição sobre a
  forma, mas com teto de renda".
- **p ≤ 0,5** (mulheres): a mediana sem suposição não tem limites informativos (vai de 0 a y_max). É o resultado,
  não um erro.
- **Seleção positiva é uma suposição forte**, plausível para desempregados e desalentados, menos para estudantes
  de alta renda e aposentados com renda alta. Os limites valem "se" a suposição valer.
- **Lee (S-d)** supõe monotonicidade, que aqui não tem leitura causal: é só um aparamento de sensibilidade.
- **Heaping:** quantis caem em valores redondos; limites de mediana podem coincidir entre réplicas (IC estreito por
  heaping, não por precisão).

## 10. Resultados

`s13_limites_hiato.parquet`, janela 2025T3–2026T2; hiato % da **média** (Branca ÷ grupo − 1). Entre parênteses, o IC
de Imbens–Manski (bootstrap Rao-Wu, 200 réplicas). Pr(P1): Branca 62,6%, Negra 60,5%; mulheres 53,3% e 49,2%.

| Comparação | Hiato em P1 | S-a sem suposição | S-b seleção positiva | S-c seleção positiva + piso P10 | S-d aparamento à la Lee |
|---|---|---|---|---|---|
| Branca × Negra | 66,8 | [−74; 611] | [**4,3**; 176] (IC desde 2,6) | [24,3; 136] (IC desde 22,5) | [35,0; 72,0] (31,9 a 75,0) |
| Branca × Negra, homens | 71,4 | [−57; 370] | [25,2; 137] | [38,9; 115] | [54,5; 73,1] |
| Branca × Negra, mulheres | 63,1 | [−84; 1.023] | [**−13,1**; 232] | [**6,7**; 165] (IC desde 4,9) | [19,0; 74,9] |
| Branca × Indígena | 61,7 | [−75; 611] | [1,1; 176] (IC desde −8,4) | [20,5; 140] (IC desde 9,2) | [18,2; 71,3] (3,1 a 89,7) |

Mediana: sem suposição, os limites contêm zero em todas as comparações; para mulheres negras (Pr(P1) = 49,2% ≤ 50%) a
mediana não tem limite superior finito — nem sob seleção positiva. Em 2012 o quadro é o mesmo (S-b: total [7,5; 196];
mulheres [−16,0; 269]; S-c mulheres [6,9; 190]).

**Leitura das hipóteses.** H3 confirmada: sem suposição sobre a renda potencial, o sinal do hiato não é identificado
(limites de −74% a +611%). H1 **não pode ser avaliada** com limites: sob S-b e S-c o intervalo se estende bem acima
**e** bem abaixo do hiato de P1 — os dados não dizem se o recorte P1 sub- ou superestima o hiato potencial. H2 refutada:
mesmo com Pr(P1) quase igual entre homens (73,1% × 72,3%), o aparamento de 1,1% do topo branco desloca o hiato em
19 p.p. (a média é sensível ao topo); entre mulheres, a largura é de 56 p.p.

**Critério do item 8.** Sob S-b, o limite inferior das mulheres é negativo (−13,1%): **sob seleção positiva pura,
o sinal do hiato entre mulheres não está identificado**. Basta acrescentar que quem está fora ganharia ao menos o P10
do próprio grupo (S-c) para o sinal ficar identificado em todas as comparações Branca × Negra.

| Saída | Arquivo | `se_metodo` | Commit |
|---|---|---|---|
| Limites e IC | `data/processed/s13_limites_hiato.parquet` | `bootstrap_rao_wu_estrato_upa_200` | este PR |

## 11. Afirmações permitidas

- "Se as pessoas fora do mercado ganhassem, no máximo, a média do seu grupo e, no mínimo, o que ganham os 10% de
  menor renda do grupo, o hiato de renda Branca × Negra entre todos os adultos estaria entre 24% e 136%."
- "Sem nenhuma suposição sobre quem não trabalha, não é possível afirmar nem o sinal do hiato potencial." (para mostrar
  que todo número de hiato carrega uma suposição sobre a seleção)

## 12. Afirmações proibidas

- "O hiato verdadeiro é X%" (o resultado é um intervalo sob uma suposição).
- Tratar o limite de S-a como estimativa.
- "Corrigimos a seleção" (não há correção pontual).

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
