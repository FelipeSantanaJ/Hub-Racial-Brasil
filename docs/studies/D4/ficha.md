# Ficha de pesquisa — `D4` · Território: composição regional e hiato por UF e tipo de área

| Campo | Valor |
|---|---|
| ID no plano | `D4.1`, `D4.2`, `D4.3` (`D4.4` bloqueado: Censo 2022) (`docs/PLANO_DE_ANALISE.md`, Bloco D) |
| Onda | 3 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-14 / 2026-10-14 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
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

## 10. Resultados

Tabela: `d4_territorio` (Kitagawa, hiato por UF com BH, tipo de área, situação, correlação entre UFs).

**D4.1 — Kitagawa entre/dentro de UF (Branca × Negra, média de ln renda)**

| | 2012 | 2025T3–2026T2 |
|---|---|---|
| Hiato total | 0,464 | 0,427 |
| Entre UFs (composição) | 0,146 (0,138–0,155) — 31,5% | **0,119 (0,113–0,126) — 28,0%** |
| Dentro das UFs | 0,318 — 68,5% | 0,308 — 72,0% |

O componente "entre UFs" do Kitagawa (28%) é maior que a contribuição do território no Gelbach do D1 (19,6%): o
Kitagawa não controla instrução — parte do que parece "lugar" é a instrução menor das UFs mais pobres.

**D4.2 — hiato condicional (idade, sexo, instrução) por UF, janela recente:** todas as 27 UFs têm hiato > 0 após BH.
Menores: PB 0,065 (0,015–0,115), PI 0,092, RR 0,096, MS 0,101. Maiores: DF **0,186 (0,148–0,225)**, TO 0,173, PA
0,171, RJ 0,161, MA 0,159, AM 0,157. Sul: PR 0,104, SC 0,118, RS 0,138; SP 0,129. Brutos de 0,19 (RR) a 0,48 (DF).
Correlação de Spearman entre o hiato condicional e a % de negros em P1: 0,06 (simulação: −0,12 a 0,34; reamostrando
UFs: −0,36 a 0,46); em 2012, 0,13.

**D4.3 — tipo de área e situação (lp)**

| Recorte (2025T3–2026T2) | Bruto | + idade, sexo, instrução | + território (UF, urbano, tipo de área) |
|---|---|---|---|
| Capital | 0,531 | 0,251 | **0,182 (0,167–0,197)** |
| Resto da RM | 0,305 | 0,184 | 0,115 |
| Resto da UF | 0,431 | 0,259 | **0,110 (0,101–0,119)** |
| Capital − resto da UF | +0,100 (0,069–0,130) | −0,008 (−0,027 a 0,011) | **+0,072 (0,054–0,090)** |
| Urbana | 0,402 | 0,219 | 0,133 |
| Rural | 0,489 | 0,401 | 0,095 (0,077–0,113) |

**Desvio do registro prévio (declarado):** a coluna "+ território" foi acrescentada **depois** de ver a primeira
rodada. O "resto da UF" junta o interior de todas as UFs; sem controlar a UF, a comparação capital × interior (e
urbano × rural) mistura composição regional — o hiato rural "maior" (0,401) era o interior do Nordeste e do Norte,
e some com a UF (0,095). A especificação pré-registrada (sem território) continua na tabela.

**Leitura das hipóteses**

- **H1 (composição territorial ≥ 25%):** **confirmada** pelo Kitagawa (28,0%; 31,5% em 2012), com a ressalva acima.
- **H2 (hiato maior onde negros são minoria):** **refutada** — sem correlação (0,06; IC inclui zero). O Sul não tem
  hiato condicional maior que o resto do país; os maiores estão no DF, no Norte e no RJ.
- **H3 (hiato maior nas capitais):** **refutada na especificação pré-registrada** (−0,008; IC inclui zero) e
  **confirmada com território** (+0,072; 0,054–0,090). Leitura: dentro da mesma UF, o hiato é maior na capital.

## 11. Afirmações permitidas

- "Cerca de 28% do hiato nacional vem de pessoas negras viverem mais em UFs de renda mais baixa; 72% existe dentro
  das próprias UFs."
- "Em todas as 27 UFs há hiato com a mesma idade, sexo e instrução; é maior no DF (≈ 17%) e menor na Paraíba (≈ 6%)."
- "Dentro da mesma UF, o hiato é maior na capital que no interior."

## 12. Afirmações proibidas

- "O Sul é mais desigual racialmente" (sem evidência).
- "No campo o racismo é maior" (o hiato rural maior é composição regional).
- Converter o componente "entre UFs" em diferença de bem-estar (custo de vida não ajustado).
