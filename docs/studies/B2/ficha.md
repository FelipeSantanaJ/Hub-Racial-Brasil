# Ficha de pesquisa — `B2` · A mudança do hiato no tempo é de composição ou de renda?

| Campo | Valor |
|---|---|
| ID no plano | `B2` (`docs/PLANO_DE_ANALISE.md`, Bloco B) |
| Onda | 2 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (proposto) |
| PR | `onda2/b-c` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

Quanto da mudança do hiato Branca × Negra entre 2012 e 2025T3–2026T2 vem de (a) mudança de **quem se declara**
preto ou pardo (reclassificação racial), (b) mudança nas **características** dos grupos (escolaridade, idade,
região, sexo), (c) mudança nos **retornos** dessas características e (d) mudança na **parte não associada às
covariáveis incluídas**?

## 2. Tipo

`C`. Decomposição contábil; nenhuma parte é "causa". "Retorno" e "parte não associada" não são preço de mercado nem
discriminação.

## 3. Estimando

1. **Reclassificação (Kitagawa dentro de Negra).** m_Negra = s_Preta·m_Preta + s_Parda·m_Parda. Entre as janelas:
   Δ ln m_Negra = componente de composição (Δs a médias iniciais) + componente dentro dos subgrupos. Em P1 e em P4.
2. **Teste de reclassificação por coorte.** % Preta entre as pessoas de 18+ de coortes de nascimento fixas
   (1950–1994) em 2012 × 2025: se sobe dentro da mesma coorte, não é demografia (nascimentos), é declaração
   (com ressalva de mortalidade e migração diferenciais).
3. **Juhn-Murphy-Pierce (versão de médias)** *(a confirmar: Juhn, Murphy & Pierce 1991)* do hiato médio em log:
   D_t = ΔX_t·β_t + Δθ_t·σ_t, com β e σ (desvio-padrão do resíduo) da regressão de ln(renda) dos **brancos** e θ = média
   do resíduo padronizado do grupo. Mudança D_1 − D_0 = (ΔX_1 − ΔX_0)β_1 [características] + ΔX_0(β_1 − β_0) [retornos]
   + (Δθ_1 − Δθ_0)σ_1 [posição não associada às covariáveis] + Δθ_0(σ_1 − σ_0) [dispersão residual].

## 4. População

P1 (componentes 1 e 3), P4 e pessoas 18+ (componentes 1 e 2). Renda `VD4016` real; covariáveis: faixa de idade
(6), instrução `VD3004` (7), região (5), sexo.

## 5. Método

- **Estimador:** WLS (`V1028`) por janela (4 trimestres empilhados) e grupo; Kitagawa com médias ponderadas.
- **Incerteza:** bootstrap Rao-Wu Estrato/UPA (100 réplicas por janela; as janelas são amostras quase
  independentes — 2012 e 2025–26 não compartilham domicílios), IC percentil.
- **FDR:** não se aplica (componentes de uma identidade).
- **Supressão:** não se aplica (grupos grandes).

## 6. Dados

PNAD Contínua trimestral v2: `V2010`, `V2007`, `V2009`, `VD3004`, `UF`, `VD4002`, `VD4016`, deflator; janelas
2012T1–T4 e 2025T3–2026T2.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Reclassificação fabrica convergência:** mais pessoas de renda média se declarando pretas/pardas sobem a média Negra | Componente de composição dentro de Negra positivo e relevante (≥ 25% da queda do hiato) |
| H2 | **A convergência é educacional:** a diferença de escolaridade diminuiu | Componente "características" negativo (reduz o hiato) e maior em módulo que os demais |
| H3 | **Retornos se moveram contra:** o prêmio da educação (que os brancos têm mais) caiu ou subiu | Componente "retornos" diferente de zero |
| H4 | **A parte não associada às covariáveis não mudou** | Componente "posição não associada" com IC incluindo zero |

## 8. O que refutaria

- H1 é refutada se o componente de composição dentro de Negra for < 10% da variação do hiato ou tiver IC incluindo zero.
- H1 também perde força se a % Preta **não** subir dentro de coortes fixas.

## 9. Armadilhas

- **Reclassificação é parcialmente não identificável:** a PNADC não acompanha a mesma pessoa por anos; o teste de
  coorte mistura reclassificação com mortalidade/migração diferenciais.
- A decomposição de Kitagawa dentro de Negra trata Preta e Parda como fixos; se quem muda de categoria tem renda
  diferente da média do grupo de origem, o componente "dentro" também carrega reclassificação.
- JMP depende da escolha do grupo de referência (Branca) e das covariáveis; "posição não associada" ≠ discriminação.
- Deflator: as janelas estão em R$ do mesmo trimestre de referência; a log-diferença entre grupos não depende dele.

## 10. Resultados

`b2_decomposicao_tempo.parquet` (bootstrap Rao-Wu, 100 réplicas por janela) e `b2_composicao_racial_coortes.parquet`.
Janelas 2012 (4 trimestres) e 2025T3–2026T2; log-pontos.

**1. Reclassificação (Kitagawa dentro de Negra).**

| | P1 | P4 (todos os adultos) |
|---|---|---|
| Hiato (ln média Branca − ln média Negra) | 0,559 → 0,511 | 0,600 → 0,545 |
| Variação do hiato | **−0,048 (−0,076 a −0,020)** | −0,055 (−0,084 a −0,025) |
| % Preta dentro de Negra | 15,6% → 20,8% | 14,9% → 20,0% |
| Componente de composição Preta/Parda na média Negra | **−0,0004 (−0,0014 a 0,0005)** | +0,0022 (0,0012 a 0,0032) |
| Componente dentro dos subgrupos | +0,207 (0,196 a 0,222) | +0,229 |

**2. Teste por coorte.** A % Preta sobe **dentro das mesmas coortes de nascimento** entre 2012 e 2025 (ex.: nascidos em
1970–74: 7,8% → 11,8%; 1985–89: 7,3% → 11,7%) — a mudança de composição não vem de nascimentos; é reclassificação na
declaração (ou mortalidade/migração diferenciais, que não explicariam 4 p.p. em 13 anos).

**3. Juhn-Murphy-Pierce (versão de médias), P1, média de ln(renda):** D = 0,464 → 0,427.

| Componente | Log-pontos (IC 95%) | % da variação |
|---|---|---|
| Variação total | −0,037 (−0,054 a −0,019) | 100% |
| Características (ΔX: idade, instrução, região, sexo) | **−0,015 (−0,025 a −0,006)** | 42% |
| Retornos (Δβ dos brancos) | **−0,018 (−0,027 a −0,011)** | 49% |
| Posição não associada às covariáveis (Δθ) | −0,006 (−0,017 a 0,006) | 17% |
| Dispersão residual (Δσ) | +0,003 (0,001 a 0,004) | −7% |

**Leitura das hipóteses.** H1 **refutada**: houve reclassificação (a % Preta subiu 4 p.p. dentro das mesmas coortes),
mas ela não fabricou convergência, porque pretos e pardos têm renda média parecida — o componente de composição é
zero em P1 e +0,002 em P4. H2 parcialmente: as características explicam 42% da queda (e não mais que os retornos). H3
confirmada: a queda dos retornos às características em que os brancos estão à frente (sobretudo escolaridade) explica
metade da convergência. H4 confirmada: a parte não associada às covariáveis não mudou de forma distinguível de zero.

## 11. Afirmações permitidas

- "A queda do hiato entre 2012 e 2025–26 veio, em partes parecidas, de a escolaridade e as demais características das
  pessoas negras terem se aproximado das das brancas e de essas características passarem a ser menos remuneradas; a
  parte não associada às características observadas não mudou."
- "Mais pessoas passaram a se declarar pretas (a % sobe dentro das mesmas gerações), mas isso não explica a queda do
  hiato." (com a ressalva de que a decomposição trata Preta e Parda como grupos fixos)

## 12. Afirmações proibidas

- "A convergência é falsa" (o que se mede é quanto dela vem de composição).
- "A parte não explicada é discriminação."

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
