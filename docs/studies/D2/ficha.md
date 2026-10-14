# Ficha de pesquisa — `D2` · Mesma educação, renda diferente? Retornos, quantis e sobrequalificação por raça

| Campo | Valor |
|---|---|
| ID no plano | `D2.2`, `D2.3`, `D2.4` (`D2.1` está no D1; `D2.5` remete ao Bloco E) (`docs/PLANO_DE_ANALISE.md`, Bloco D) |
| Onda | 3 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-14 / 2026-10-14 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
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

## 10. Resultados

Tabelas: `d2_hiato_por_nivel`, `d2_quantis_nivel`, `d2_sobrequalificacao` (`src/processing/bloco_d_estrutura.py`).
Log-pontos (lp) de ln renda; IC 95%.

**D2.2 — hiato Branca × Negra dentro de cada nível, condicional a idade, sexo e território** (bruto entre parênteses)

| Nível | 2012 | 2025T3–2026T2 |
|---|---|---|
| Sem instrução | 0,112 (0,301) | 0,149 (0,353) |
| Fundamental incompleto | 0,115 (0,279) | 0,109 (0,264) |
| Fundamental completo | 0,116 (0,247) | 0,073 (0,228) |
| Médio incompleto | 0,107 (0,258) | 0,084 (0,217) |
| Médio completo | 0,122 (0,234) | 0,100 (0,216) |
| Superior incompleto | 0,123 (0,184) | 0,077 (0,159) |
| **Superior completo** | **0,246** (0,322) | **0,237 (0,221–0,253)** (0,314) |
| Superior − fundamental incompleto | 0,131 (0,109–0,154) | **0,128 (0,107–0,150)** |

Branca × Indígena, superior completo, janela recente: 0,372 (0,212–0,533); diferença para fundamental incompleto
0,184 (0,008–0,360).

**D2.3 — quantis dentro do nível, Branca × Negra (lp; bootstrap Rao-Wu 200)**

| Nível | Quantil | 2012 | 2025T3–2026T2 |
|---|---|---|---|
| Superior completo | P10 | 0,279 (0,251–0,313) | 0,228 (0,228–0,231)* |
| | P50 | 0,316 | 0,261 (0,242–0,319) |
| | P90 | 0,443 (0,364–0,470) | **0,406 (0,400–0,448)** |
| Médio completo / superior incompleto | P10 | 0,186 | 0,482 (0,429–0,568) |
| | P50 | 0,206 | 0,157 |
| | P90 | 0,357 | 0,227 (0,220–0,230)* |

\* IC quase nulo = quantil preso num valor redondo (heaping), não precisão.

**D2.4 — sobrequalificação de diplomados (superior completo em P1)**

| Definição | Branca | Negra | Negra − Branca condicional (p.p.) |
|---|---|---|---|
| Principal (grupos 04–09), 2025–26 | 24,9% | 31,4% | **+6,1 (5,2–7,0)** |
| Principal, 2012 | 19,9% | 24,5% | +5,1 (4,1–6,1) |
| Antiga (só grupo 09), 2025–26 | 1,0% | 2,1% | +1,1 (0,8–1,3) |
| Estrita (grupos 03–09), 2025–26 | 37,8% | 44,7% | +7,2 (6,2–8,2) |

Gelbach do hiato entre diplomados (bruto 0,314 lp, 2025–26): território 0,057 (18,0%); **sobrequalificação 0,034
(0,030–0,039; 10,9%)**; idade 0,012; sexo 0,007. Em 2012: sobrequalificação 0,018 (5,7% de 0,322). A sobrequalificação
aumentou entre os diplomados (das duas raças) e passou a pesar o dobro no hiato entre eles.

**Leitura das hipóteses**

- **H1 (teto de vidro educacional):** **confirmada.** O hiato condicional entre diplomados (0,237) é o dobro do dos
  demais níveis (0,07–0,15), nas duas janelas; diferença para o fundamental incompleto 0,128 (0,107–0,150). Também
  para indígenas (0,184; 0,008–0,360).
- **H2 (mesmo diploma, ocupação inferior):** **em parte.** Negros diplomados estão mais em ocupações abaixo do diploma
  (+6,1 p.p. condicional, nas três definições), mas o bloco responde por 10,9% do hiato entre diplomados — abaixo do
  limiar de 20%. A maior parte do hiato entre diplomados fica dentro da mesma faixa de ocupação.
- **H3 (teto de vidro dentro do diploma):** **confirmada** com ressalva de heaping: entre diplomados, P90 (0,406) >
  P10 (0,228), IC sem sobreposição, nas duas janelas. Entre os de nível médio o padrão se inverte na janela recente
  (P10 0,482 — efeito do salário mínimo no P10 de um grupo e não do outro).

## 11. Afirmações permitidas

- "Com o mesmo nível de instrução, idade, sexo e lugar, pessoas negras com diploma superior ganham cerca de 21% menos
  que pessoas brancas com diploma (0,24 lp); nos demais níveis, cerca de 7% a 14% menos."
- "31% das pessoas negras com diploma superior trabalham em ocupações que não exigem diploma, contra 25% das brancas."

## 12. Afirmações proibidas

- "O diploma não compensa para negros" (o retorno do diploma em relação a não ter diploma é alto para os dois grupos;
  o que muda é o hiato relativo).
- Atribuir o hiato entre diplomados à discriminação: qualidade, curso e instituição não são observados.
- Citar o IC do P10 de diplomados (heaping).
