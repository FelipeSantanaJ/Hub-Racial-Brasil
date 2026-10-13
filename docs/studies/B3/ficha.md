# Ficha de pesquisa — `B3` · A convergência ocorre em todos os pontos da distribuição?

| Campo | Valor |
|---|---|
| ID no plano | `B3` (`docs/PLANO_DE_ANALISE.md`, Bloco B) |
| Onda | 2 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 13/10/2026) |
| PR | `onda2/b-c` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

O hiato Branca × Negra caiu igualmente na base (P10), no meio (P50) e no topo (P90) da distribuição de renda, de
2012 a 2026? E na renda domiciliar per capita?

## 2. Tipo

`D`. Hiato em quantis incondicionais por período; tendência por quantil. (A decomposição por quantil — RIF-OB — é o
D1.3 da Onda 3.)

## 3. Estimando

- Hiato no quantil q: 100 × (Q_Branca(q)/Q_Negra(q) − 1) e em log-pontos, q ∈ {10, 25, 50, 75, 90}, em cada trimestre
  (P1) e em cada ano (renda domiciliar per capita, T1: P10, P50, P90).
- Inclinação por quantil (log-pontos/ano) e diferença entre as janelas 2012 e 2025T3–2026T2 (log-pontos).

## 4. População

P1 (renda `VD4016` real) e, ao lado, todas as pessoas com `VD5008` (T1, anual).

## 5. Método

- **Estimador:** quantil ponderado (`pnadc_core.quantil_ponderado`, mesma convenção do A3).
- **Incerteza:** tendência com EWC (58 trimestres; ν = 5) e Newey-West/GLS AR(1) ao lado; diferença entre janelas
  com bootstrap Rao-Wu (100 réplicas por janela; IC percentil).
- **FDR:** família = os 5 quantis de uma comparação (BH sobre as diferenças entre janelas).

## 6. Dados

PNAD Contínua trimestral v2 (P1) e `t1_renda_domiciliar_per_capita` (anual v2).

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Convergência pela base** (salário mínimo comprime a base) | Queda maior no P10/P25 que no P90 |
| H2 | **Teto de vidro persistente:** o topo não converge | Inclinação no P90 com IC incluindo zero ou positiva |
| H3 | **Convergência uniforme** | Inclinações iguais entre quantis (ICs sobrepostos) |

## 8. O que refutaria

- H2 é refutada se a inclinação do P90 for negativa e confiável (três ICs excluindo zero).
- H1 é refutada se a queda do P10 entre janelas for menor que a do P90.

## 9. Armadilhas

- **Heaping:** P25 e às vezes P10 caem no salário mínimo; o hiato em quantil pode ficar "parado" porque os dois grupos
  têm o mesmo valor redondo (IC de largura zero ≠ precisão). Dizer isso sempre.
- Salário mínimo real subiu muito no período: a base converge por política, não necessariamente por mercado.
- Quantis incondicionais ≠ efeito por quantil.

## 10. Resultados

`b3_hiato_quantis_serie.parquet`, `b3_tendencia_quantis.parquet`, `b3_quantis_janelas.parquet`. Hiato Branca × Negra
em log-pontos (ln quantil Branca − ln quantil Negra), P1:

| Quantil | 2012 (4 trim.) | 2025T3–2026T2 | Diferença (IC 95% bootstrap) | Tendência/ano (IC EWC) | Confiável? |
|---|---|---|---|---|---|
| P10 | 0,642 | 0,724 | **+0,082 (0,027 a 0,132)** | −0,010 (−0,023 a 0,004) | não |
| P25 | 0,147 | 0,136 | −0,012 (−0,020 a −0,005) | −0,007 (−0,011 a −0,003) | sim |
| P50 | 0,334 | 0,376 | **+0,043 (0,018 a 0,080)** | −0,001 (−0,005 a 0,003) | não |
| P75 | 0,511 | 0,496 | −0,015 (−0,027 a −0,005) | −0,004 (−0,011 a 0,004) | não |
| P90 | 0,671 | 0,669 | −0,002 (−0,028 a 0,069) | −0,003 (−0,011 a 0,004) | não |

As 5 diferenças entre janelas, menos a do P90, passam no BH. Renda domiciliar per capita (T1, anual, log-pontos):
P10 0,579 → 0,457, P50 0,531 → 0,452, P90 0,744 → 0,674; nenhuma tendência confiável com 14 anos (ν = 2).

**Heaping.** O P25 das pessoas negras cai no salário mínimo (R$ 1.621 em 2026T2) e o das brancas num valor redondo
logo acima (R$ 1.800): o hiato de ~0,14 lp no P25 e o IC estreito refletem esses valores redondos, não precisão.
Quantis de 2026T2: Branca R$ 1.500 / 1.800 / 3.000 / 5.000 / 10.000; Negra R$ 766 / 1.621 / 2.000 / 3.000 / 5.000. A série trimestral por quantil salta entre valores redondos
(ex.: P90 de 100% em 2026T2 = R$ 10.000 ÷ R$ 5.000).

**Leitura das hipóteses.** H1 refutada: na base (P10, abaixo do mínimo, onde está a informalidade) o hiato **aumentou**
(+0,08 lp); só o P25, preso ao salário mínimo, convergiu um pouco. H2 consistente: no P90 nada mudou (diferença −0,002;
IC inclui zero). H3 refutada: os quantis se moveram em direções diferentes. A queda do hiato médio (B1) não aparece no
P50 (subiu +0,04 lp): veio do meio-alto (P75) e do piso do mínimo.

## 11. Afirmações permitidas

- "Entre 2012 e 2025–26, o hiato racial entre os 10% que menos ganham aumentou, enquanto no salário mínimo ele caiu um
  pouco e no topo (P90) não mudou." (com a nota de heaping)

## 12. Afirmações proibidas

- "O salário mínimo reduziu o hiato" (é o G4, desenho próprio).

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
| 2026-10-13 | Felipe Santana | aprovada com ressalvas |
