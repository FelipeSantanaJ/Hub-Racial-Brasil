# Ficha de pesquisa — `D4` · Território: composição regional e hiato por UF e tipo de área

| Campo | Valor |
|---|---|
| ID no plano | `D4.1`, `D4.2`, `D4.3` (`D4.4` bloqueado: Censo 2022) (`docs/PLANO_DE_ANALISE.md`, Bloco D) |
| Onda | 3 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-14 / 2026-10-14 |
| Estado de publicação | **Proposto** |
| PR | `onda3/d` |

> Seções 1–9 escritas **antes** de rodar (14/10/2026).

## 1. Pergunta

Quanto do hiato nacional vem de pessoas negras morarem em UFs de renda mais baixa (composição), quanto existe dentro
de cada UF, e onde o hiato é maior (UF, capital × interior, urbano × rural)?

## 2. Tipo

`C` (entre × dentro) e `D` (hiato por lugar). Onde as pessoas moram é herança histórica (escravidão, migração,
colonização do Sul) — composição territorial não é "explicação neutra".

## 3. Estimando

- **D4.1 — Kitagawa entre/dentro de UF** do hiato em média de ln renda (P1): hiato = Σ_u (s_B,u − s_N,u)(ȳ_B,u + ȳ_N,u)/2
  [entre UFs] + Σ_u (ȳ_B,u − ȳ_N,u)(s_B,u + s_N,u)/2 [dentro], s = participação da UF no grupo. EP pelo método delta
  sobre as 108 médias/proporções (mesma linearização).
- **D4.2 — hiato por UF:** bruto (diferença de médias de ln) e condicional (idade, sexo, instrução) em cada UF, IC 95% e
  BH entre as 27 UFs. Correlação (Spearman, entre UFs) do hiato condicional com a % de pessoas negras em P1 na UF.
- **D4.3 — tipo de área** (`V1023`: capital; resto da RM; resto da RIDE; resto da UF) e **urbano × rural** (`V1022`):
  hiato bruto e condicional.
- **Períodos:** janelas 2012 e 2025T3–2026T2.

## 4. População

P1, Branca × Negra (Indígena fora: n por UF insuficiente). Renda `VD4016` real (deflator por UF — o deflator do IBGE
corrige preço no tempo, **não** diferenças de custo de vida entre UFs).

## 5. Método

- **Estimador:** médias ponderadas e WLS (`bloco_d.Sistema`) por domínio.
- **Incerteza:** linearização Estrato/UPA; delta numérico (`bloco_c.delta_generico`) para o Kitagawa.
- **FDR:** família = as 27 UFs de uma janela × medida (bruto/condicional).
- **Supressão:** UF × raça com n < 30 ou CV > 30% não publica (nenhuma esperada em P1).

## 6. Dados

PNAD Contínua trimestral v2: `UF`, `V1022`, `V1023`, demais variáveis do D1.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Composição territorial pesa:** negros concentrados em UFs mais pobres | Componente entre UFs ≥ 25% do hiato nacional |
| H2 | **Hiato maior onde negros são minoria** (Sul, parte do Sudeste) | Correlação de Spearman entre hiato condicional por UF e % negra < 0, com IC excluindo zero |
| H3 | **Hiato maior nas capitais** (mercados mais diversificados, mais topo) | Hiato condicional na capital > resto da UF |

## 8. O que refutaria

- H1 refutada se o componente entre UFs for < 25% do hiato (o D1 testa um limiar menor, 15%, com território completo).
- H2 refutada se o IC da correlação (bootstrap sobre UFs, a partir das estimativas e EP) incluir zero.
- H3 refutada se o IC da diferença capital − resto da UF incluir zero.

## 9. Armadilhas

- **Custo de vida** difere entre UFs e entre capital e interior: hiatos dentro da UF não sofrem com isso; o componente
  "entre UFs" sim (superestima a diferença real de bem-estar).
- **Migração seletiva** (quem migra para SP não é igual a quem fica).
- 27 comparações: FDR obrigatório; UFs pequenas do Norte têm IC largos.
- Mudança de amostra/reponderação da PNADC (2021, a confirmar) muda pesos por UF.
