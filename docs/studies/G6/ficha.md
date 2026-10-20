# Ficha de pesquisa — `G6` · Poder estatístico: efeito mínimo detectável (EMD) de cada desenho do Bloco G

| Campo | Valor |
|---|---|
| ID no plano | `G6` (`docs/PLANO_DE_ANALISE.md`, Bloco G; pré-requisito da Onda 5) |
| Onda | 5 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
| PR | `onda5/g` |

> Seções 1–9 escritas **antes** de calcular o EMD e antes de estimar qualquer efeito (20/10/2026). Critério de saída
> da Onda 5: "EMD calculado por desenho; só rodar o que tiver poder".

## 1. Pergunta

Para cada desenho causal do Bloco G que tem dado, qual é o menor efeito que ele detectaria com 80% de poder a 5% de
significância (bilateral) — e esse EMD é menor que os efeitos plausíveis, a ponto de valer a pena estimar?

## 2. Tipo

Pré-requisito metodológico (nem `D` nem `Q`). Não estima efeito nenhum; decide o que roda.

## 3. Estimando

EMD = (z₀,₉₇₅ + z₀,₈₀) × DP(θ̂ | efeito nulo) ≈ 2,80 × DP, onde θ̂ é o estimador pré-registrado de cada desenho e o DP é
obtido por **simulação** do desenho com a estrutura de variância dos dados (não com fórmula de amostras i.i.d., que
ignora a correlação serial — o erro do desenho antigo, R2 da auditoria).

| Desenho | θ̂ | Unidade do EMD |
|---|---|---|
| G1 (Lei 12.711) | média dos coeficientes do event study em 2016–2019 (implantação completa) | p.p. de % negra entre ingressantes |
| G4 (salário mínimo) | β de `hiato_ut ~ α_u + γ_t + β·E_u·ln SM_t` | adimensional; β = −1 é repasse total (ficha G4) |
| G3, G2, G5 | — | não se aplica: sem dado (fichas G3, G2, G5) |

## 4. População

A de cada desenho (fichas G1 e G4).

## 5. Método

- **G1:** resíduos de `Y_it ~ α_i + γ_t` **só com 2009–2012** (antes da lei; nenhum dado depois de 2012 entra no
  cálculo do desvio-padrão). Estimam-se o DP residual por instituição (encolhido para a média, com pesos de ingressantes)
  e a autocorrelação de ordem 1 (ρ). Como 4 anos estimam ρ mal, a simulação usa a **grade ρ ∈ {0; 0,5; 0,8; ρ̂}** e o
  EMD reportado é o **maior** da grade. Simulam-se 2.000 painéis 2009–2023 AR(1) sob efeito nulo, com o mesmo conjunto
  de instituições, pesos e grupos tratado/controle do G1, e aplica-se o estimador do G1 a cada um.
- **G4:** resíduos de `hiato_ut ~ α_u + γ_t` no painel UF × trimestre 2012–2026 **sem o regressor de exposição** (o
  β não é estimado). ρ̂ por UF; mesma grade de ρ; 2.000 simulações com o regressor verdadeiro `E_u·ln SM_t`. Se houver
  efeito, o resíduo sem o regressor o contém e o EMD sai maior (conservador).
- **Regra de decisão (pré-registrada):** G1 — efeitos plausíveis de 2 a 10 p.p. (ficha G1, seção 5): EMD ≤ 2 → roda;
  2 < EMD ≤ 10 → roda e o resultado diz "só detectaria efeitos ≥ EMD"; EMD > 10 → **não roda** e a ficha diz isso.
  G4 — efeitos plausíveis entre β = −1,5 e 0, com β = −1 o repasse total: EMD ≤ 1 → roda; EMD > 1 → **não roda**.
- **Família de testes (FDR):** não se aplica (não há teste).

## 6. Dados

Os do G1 (Censo da Educação Superior 2009–2012, painel por instituição) e do G4 (PNADC trimestral 2012–2026).

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê |
|---|---|---|
| H1 | **G1 tem poder** (muitas instituições, painel longo) | EMD ≤ 3 p.p. |
| H2 | **G4 não tem poder** (27 UFs; exposição pouco variável) | EMD de β > 1 |

## 8. O que refutaria

O EMD é um cálculo, não um teste: "refutar" aqui é a simulação não reproduzir o EP analítico em ±25% no caso
ρ = 0 (checagem de implementação). Se isso acontecer, a simulação é revista antes de decidir.

## 9. Armadilhas

- 4 anos antes da lei estimam mal a autocorrelação → grade de ρ e o pior caso.
- O EMD depende do desenho (pesos, grupos, janela); mudar o desenho depois exige recalcular o EMD.
- "Sem poder" não quer dizer "sem efeito": o que não roda vira "não detectável com este dado", nunca "não funciona".

## 10. Resultados

<Preenchido depois de calcular.>

## 11. Afirmações permitidas

<Depois de calcular.>

## 12. Afirmações proibidas

- "A política não teve efeito" a partir de um desenho sem poder.

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-20 | Claude Code | criação (seções 1–9 antes de calcular) |
