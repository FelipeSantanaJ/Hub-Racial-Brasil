# Ficha de pesquisa — `D2` · Mesma educação, renda diferente? Retornos, quantis e sobrequalificação por raça

| Campo | Valor |
|---|---|
| ID no plano | `D2.2`, `D2.3`, `D2.4` (`D2.1` está no D1; `D2.5` remete ao Bloco E) (`docs/PLANO_DE_ANALISE.md`, Bloco D) |
| Onda | 3 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-14 / 2026-10-14 |
| Estado de publicação | **Proposto** |
| PR | `onda3/d` |

> Seções 1–9 escritas **antes** de rodar (14/10/2026).

## 1. Pergunta

Pessoas brancas e negras com o mesmo nível de instrução ganham o mesmo? A diferença é maior em algum nível, em algum
ponto da distribuição dentro do nível, e quanto dela, entre diplomados, está associado a trabalhar em ocupação abaixo
do diploma?

## 2. Tipo

`C`/`D`. Diferenças condicionais em corte transversal. O nível de instrução não mede qualidade da escola, curso nem
instituição (Bloco E); um hiato dentro do nível pode refletir essas diferenças — não é "retorno discriminatório".

## 3. Estimando

- **D2.2 — hiato por nível:** em ln renda (P1), coeficiente de Negra (e de Indígena) dentro de cada nível de `VD3004`,
  numa regressão com interação raça × nível e controles de idade (faixas), sexo e território (UF, urbano, tipo de
  área). Também o hiato bruto (diferença de médias de ln) por nível. Diferença superior completo − fundamental
  incompleto do hiato condicional (teste de H1).
- **D2.3 — quantis dentro do nível:** hiato Branca − Negra em P10, P50 e P90 de ln renda entre pessoas com **superior
  completo** e com **médio completo/superior incompleto**; bootstrap de Rao-Wu (200 réplicas).
- **D2.4 — sobrequalificação:** entre pessoas com superior completo em P1, % em ocupação de grupamento `VD4011` 04–09
  (abaixo do nível de competência 3–4 da ISCO-08 *(a confirmar)*); sensibilidade: só grupo 09 (critério da tabela
  antiga `sobrequalificacao`) e 03–09 (estrito). Diferença Negra − Branca bruta e condicional (idade, sexo,
  território). Gelbach do hiato entre diplomados com o bloco "sobrequalificado" ao lado de idade, sexo e território.
- **Períodos:** janelas 2012 e 2025T3–2026T2.

## 4. População

P1 (ocupados 18+ com renda habitual do trabalho principal > 0), Branca, Negra, Indígena; renda `VD4016` real em log.
Indígena só no D2.2 (n pequeno por nível: célula sem n ≥ 30 ou CV > 30% não publica).

## 5. Método

- **Estimador:** WLS (`V1028`) via `bloco_d.Sistema`; quantis ponderados (convenção de `pnadc_core.quantil_ponderado`).
- **Incerteza:** função de influência linearizada por Estrato/UPA (regressões, proporções); bootstrap de Rao-Wu para
  quantis (heaping: valores redondos dão IC estreitos que não são precisão).
- **FDR:** família = os 7 hiatos condicionais por nível de uma raça × janela (BH).
- **EMD:** reportado para a diferença superior − fundamental incompleto (2,8 × EP).

## 6. Dados

PNAD Contínua trimestral v2: `VD3004`, `VD4011`, `V2009`, `V2007`, `V2010`, `UF`, `V1022`, `V1023`, `VD4016`, pesos e
desenho; deflator do IBGE.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Teto de vidro educacional:** a desvantagem relativa cresce com a instrução | Hiato condicional no superior completo > no fundamental incompleto (IC da diferença exclui zero) |
| H1' | **Instrução nivela:** com diploma o hiato some ou cai | Hiato condicional no superior < no fundamental |
| H2 | **Mesmo diploma, ocupação inferior:** negros diplomados ficam mais em ocupações abaixo do diploma | Diferença condicional de sobrequalificação Negra − Branca > 0 e bloco "sobrequalificado" ≥ 20% do hiato bruto entre diplomados |
| H3 | **Teto de vidro dentro do diploma:** entre diplomados o hiato é maior no topo | Hiato em P90 > P10 entre pessoas com superior completo (IC não se sobrepõem) |

## 8. O que refutaria

- H1 refutada se o IC da diferença superior − fundamental incompleto incluir zero (então "não distinguível") ou se for
  negativo (vale H1').
- H2 refutada se a diferença condicional de sobrequalificação tiver IC incluindo zero, ou se o bloco ficar < 20%.
- H3 refutada se os IC de P90 e P10 se sobrepuserem ou P10 > P90.

## 9. Armadilhas

- **Qualidade e área do curso** não observadas: pesam no hiato entre diplomados (curso de maior retorno, instituição);
  o Hub não separa isso (Bloco E, INEP).
- **Interação depende da escala:** hiato em log-pontos por nível; em R$ o hiato cresce mecanicamente com o nível.
- **Composição do nível ao longo do tempo:** a expansão do superior (cotas, ProUni, EAD) mudou quem é diplomado entre
  2012 e 2026; comparar janelas com essa ressalva.
- **Sobrequalificação normativa** (pelo grupamento) é grosseira: técnicos de nível médio (grupo 03) podem exigir
  diploma em algumas carreiras; por isso as três definições.
- Mudança do questionário de educação em 4T2015 (F6) não afeta as janelas, mas afeta séries.
