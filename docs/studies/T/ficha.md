# Ficha de pesquisa — `T` · Panorama da população inteira (T1–T3)

| Campo | Valor |
|---|---|
| ID no plano | `T1`, `T2`, `T3` (`docs/PLANO_DE_ANALISE.md`, Bloco T) |
| Onda | 1 (eixo principal desde o S1) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 13/10/2026) |
| PR | Onda 1, parte 2 (`onda1/parte2`); linhas em PPC na Onda 2 (`onda2/b-c`, PR #9) |

## 1. Pergunta

Quando se olha **todo mundo** (inclusive quem não trabalha, crianças e idosos) pela renda do domicílio, qual é a
desigualdade racial de renda, pobreza e fontes de renda, e como ela mudou entre 2012 e 2025?

## 2. Tipo

`D`. Não decompõe nem atribui causa. A renda domiciliar mistura renda do trabalho de todos os moradores,
transferências e tamanho da família.

## 3. Estimando

- **T1:** média, mediana, P10, P90 e Gini da renda domiciliar per capita (`VD5008`) por cor/raça da pessoa e por
  cor/raça × sexo da pessoa responsável pelo domicílio; hiato % = 100 × (média Branca ÷ média do grupo − 1), IC 95%.
  Theil T entre/dentro (pessoas com renda > 0).
- **T2:** FGT(0) (% de pessoas abaixo da linha), FGT(1) (hiato médio de pobreza) e FGT(2) (severidade), com IC 95%,
  por cor/raça e por cor/raça × sexo da pessoa.
- **T3:** % das pessoas que vivem em domicílio que recebe cada fonte; participação de cada fonte no total da renda
  domiciliar das pessoas de cada grupo.

## 4. População

- **Universo:** todas as pessoas (todas as idades) da PNAD Contínua anual; pensionistas, empregados domésticos e
  parentes (`V2005` 17–19) fora, como no IBGE.
- **Renda:** `VD5008` = renda habitual dos trabalhos + efetiva de outras fontes, do domicílio, ÷ moradores.
  **Nominal do ano** (o extrato não traz os deflatores anuais CO1/CO2).
- **Linhas de pobreza (por pessoa, por mês):** ¼ salário mínimo (critério de renda do BPC), ½ salário mínimo
  (baixa renda do CadÚnico), 50% da mediana nacional do ano e, desde a Onda 2, as linhas internacionais do Banco
  Mundial de **US$ 3,00, 4,20 e 8,30 por pessoa por dia em PPC de 2021** (nota do Banco Mundial de 05/06/2025)
  convertidas para R$ nominais do ano (ver Método).

## 5. Método

- Incerteza: linearização Estrato/UPA (médias, FGT, razão de médias por delta). Gini e quantis sem IC nesta versão.
- **Linhas em PPC** (`src/ingestion/linhas_pobreza_ppc.py` → `data/processed/linhas_pobreza_ppc.parquet`):
  linha_R$(ano) = US$/dia × PPC_2021 × IPC(ano) ÷ IPC(2021) × 365/12 (por pessoa por mês). PPC_2021 =
  `PA.NUS.PRVT.PP` de 2021 = **2,4499 R$ por dólar internacional** (consumo final das famílias); IPC =
  `FP.CPI.TOTL` (2010 = 100; 2021 = 187,117; 2025 = 234,414). Fonte: API v2 do Banco Mundial (WDI), Brasil,
  acessada em 13/10/2026 (`lastupdated` 2026-10-08). Há IPC para todos os anos de 2012 a 2025; ano sem IPC
  ficaria sem a linha ("NÃO VERIFICADO"), nunca extrapolado. Valores (R$/pessoa/mês):

  | Linha | 2012 | 2019 | 2021 | 2025 |
  |---|---|---|---|---|
  | US$ 3,00 | 134,28 | 199,99 | 223,55 | 280,06 |
  | US$ 4,20 | 188,00 | 279,99 | 312,97 | 392,08 |
  | US$ 8,30 | 371,52 | 553,31 | 618,49 | 774,82 |

  Para comparação, ¼ SM em 2025 = R$ 379,50 e ½ SM = R$ 759,00.
- T3: a renda domiciliar é reconstruída somando, por domicílio, a renda habitual de todos os trabalhos (`VD4019`) e
  as fontes `V5001A2`–`V5008A2`; a mediana da diferença relativa contra a `VD5007` do IBGE é **0** em todos os anos.

## 6. Dados

PNAD Contínua anual, `data/raw/pnadc_anual_v2`: Visita 1 (2012–2019, 2022–2025) e Visita 5 (2020–2021, sem
Visita 1 publicada). T3 só de 2016 em diante: as fontes separadas entram com a mudança de questionário de 2015
(ano parcial).

## 7. Hipóteses concorrentes

| # | Hipótese | Previsão |
|---|---|---|
| H1 | O hiato domiciliar é o hiato do trabalho, ampliado pela menor ocupação | hiato T1 > hiato P1, sobretudo para mulheres |
| H2 | Transferências compensam parte da desvantagem | maior participação de BF/BPC entre negros e indígenas; hiato menor em 2020 (auxílio) |

## 8. O que refutaria

H2 seria enfraquecida se o hiato domiciliar não caísse nos anos de transferências maiores (2020, 2023–2025).

## 9. Armadilhas

- **2020–2021 vêm da Visita 5 e da pandemia** (auxílio emergencial aparece em "Outros programas sociais", que vai
  de 0,1% para 0,8–2,7% da renda em 2021): não comparar 2020–21 com os demais sem essa ressalva.
- Mudança do Bolsa Família (2021 Auxílio Brasil; 2023 novo Bolsa Família) muda o que cada código capta.
- O responsável pelo domicílio é declarado; domicílios chefiados por mulheres têm composição diferente.
- Valores nominais: comparar níveis em R$ só dentro do ano.
- **Linhas internacionais × renda da PNADC.** As taxas do T2 em PPC **não são** as taxas oficiais do Banco Mundial
  para o Brasil (Poverty and Inequality Platform) e não devem ser apresentadas como tais: (i) o Hub usa `VD5008`
  (renda **habitual** dos trabalhos + efetiva de outras fontes), nominal do ano, todas as idades, sem pensionistas e
  domésticos (V2005 17–19); o Banco Mundial harmoniza a renda à sua maneira (conceito exato de renda, tratamento de
  rendas zero e ajustes: NÃO VERIFICADO); (ii) a conversão usa o IPC nacional médio do ano, sem deflação espacial
  nem ajuste para o mês de referência da renda; (iii) o fator de PPC é revisado pelo Banco Mundial (os valores
  mudam a cada atualização do WDI). Use as linhas em PPC para **comparar grupos raciais** e a evolução no tempo
  dentro do Hub, não para comparar o nível com outras fontes.
- Rendas zero pesam muito na base: com US$ 3,00, o FGT(1) das pessoas brancas (1,6%) é mais da metade do FGT(0)
  (2,9%), porque quem tem renda domiciliar zero entra com hiato de pobreza 1.

## 10. Resultados

Tabelas: `t1_renda_domiciliar_per_capita.parquet`, `t2_pobreza.parquet`, `t3_fontes_de_renda.parquet`.

**T1 — hiato % da renda domiciliar per capita (Branca vs. grupo, pessoas de todas as idades)**

| | 2012 | 2016 | 2019 | 2021* | 2023 | 2024 | 2025 (IC 95%) |
|---|---|---|---|---|---|---|---|
| Negra | 98,7% | 102,5% | 98,7% | 96,2% | 87,3% | 78,6% | **81,7%** (77,2–86,2) |
| Indígena | 92,6% | 86,9% | 107,3% | 101,9% | 112,0% | 91,7% | **105,5%** (86,9–124,2) |

Por responsável do domicílio, 2025 (vs. domicílios de homem branco): mulher branca 32,3%; homem negro 81,7%;
**mulher negra 145,5%** (137,1–153,9); homem indígena 132,5%; mulher indígena 150,0%. Em 2012: 11,6%; 100,3%;
117,6%; 83,6%; 139,3% — a desvantagem de domicílios chefiados por mulheres negras **aumentou**.
Gini total 0,540 (2012) → 0,511 (2025); Theil entre raças ~9–11% do total.

**T2 — % de pessoas abaixo da linha**

| Linha | Grupo | 2012 | 2019 | 2021* | 2025 (IC 95%) |
|---|---|---|---|---|---|
| ¼ SM | Branca | 5,7 | 6,2 | 8,3 | 4,5 (4,3–4,8) |
| | Negra | 15,3 | 16,2 | 18,7 | **9,8** (9,5–10,1) |
| | Indígena | 19,4 | 22,5 | 18,6 | 13,8 (9,6–17,9) |
| ½ SM | Branca | 18,5 | 17,7 | 21,7 | 14,8 (14,2–15,4) |
| | Negra | 39,3 | 37,4 | 42,2 | **29,3** (28,8–29,9) |
| | Indígena | 44,7 | 42,9 | 45,9 | 37,1 (31,7–42,5) |
| 50% da mediana | Branca | 13,7 | 14,6 | 15,1 | 13,9 |
| | Negra | 31,4 | 32,2 | 31,5 | 28,3 |

**T2 — linhas internacionais (PPC de 2021), % de pessoas abaixo da linha**

| Linha (R$/mês em 2025) | Grupo | 2012 | 2019 | 2021* | 2022 | 2025 (IC 95%) |
|---|---|---|---|---|---|---|
| US$ 3,00 (R$ 280) | Branca | 4,7 | 4,5 | 6,6 | 3,8 | 2,9 (2,7–3,1) |
| | Negra | 12,7 | 12,3 | 15,0 | 9,3 | **5,9** (5,7–6,2) |
| | Indígena | 15,1 | 17,6 | 16,1 | 8,9 | 8,5 (4,7–12,3) |
| US$ 4,20 (R$ 392) | Branca | 8,0 | 7,6 | 10,2 | 6,4 | 4,9 (4,7–5,2) |
| | Negra | 20,5 | 19,4 | 22,5 | 15,6 | **10,7** (10,3–11,0) |
| | Indígena | 25,4 | 27,2 | 21,8 | 17,5 | 14,1 (10,0–18,2) |
| US$ 8,30 (R$ 775) | Branca | 24,2 | 22,2 | 26,5 | 21,3 | 16,4 (15,9–17,0) |
| | Negra | 47,7 | 44,2 | 48,8 | 40,4 | **31,9** (31,4–32,5) |
| | Indígena | 50,0 | 48,4 | 52,9 | 45,7 | 39,0 (33,6–44,3) |
| | Total | 36,7 | 34,8 | 39,1 | 32,1 | 25,2 (24,8–25,7) |

Em 2025, a proporção de pessoas negras abaixo da linha é **2,0×** a de brancas com US$ 3,00, 2,2× com US$ 4,20 e
1,9× com US$ 8,30 — a mesma razão de ~2× das linhas em salário mínimo. Hiato de pobreza (FGT1) com US$ 8,30 em 2025:
Negra 12,1% (11,9–12,4) × Branca 6,0% (5,7–6,2). Mulheres negras: 33,8% (33,2–34,4) abaixo de US$ 8,30 (homens
negros 30,1%; mulheres brancas 17,0%). As linhas de US$ 3,00 e 4,20 ficam perto de ¼ SM (abaixo e acima), e a de
US$ 8,30 perto de ½ SM: o retrato é o mesmo das linhas nacionais.

A pobreza **absoluta** (em salários mínimos) caiu muito desde 2022; a **relativa** (50% da mediana) quase não
mudou: pessoas negras seguem ~2× mais pobres que brancas. Mulheres negras: 31,0% abaixo de ½ SM em 2025
(homens negros 27,7%; mulheres brancas 15,3%).

**T3 — fontes (2025)**

| | Branca | Negra | Indígena |
|---|---|---|---|
| Trabalho, % da renda domiciliar | 78,6 | 76,9 | 73,6 |
| Aposentadoria e pensão, % | 14,1 | 13,4 | 12,7 |
| Bolsa Família, % da renda | 1,0 | 4,1 | 6,8 |
| BPC, % da renda | 0,8 | 2,2 | 2,5 |
| Pessoas em domicílio com Bolsa Família | 12,5% | 29,1% | 38,7% |
| Pessoas em domicílio com BPC | 4,2% | 6,8% | 6,8% |

\\* 2020–2021: Visita 5.

## 11. Afirmações permitidas

- "Em 2025, a renda domiciliar por pessoa de pessoas brancas era 82% maior que a de pessoas negras (IC 95%: 77% a
  86%); em 2012 era 99% maior."
- "29% das pessoas negras viviam com menos de meio salário mínimo por pessoa em 2025, contra 15% das brancas."
- "Bolsa Família chega a 29% das pessoas negras, mas responde por 4% da renda dos seus domicílios: a renda vem
  sobretudo do trabalho."
- "Em 2025, 32% das pessoas negras viviam abaixo da linha de US$ 8,30 por dia (PPC de 2021) pelo cálculo do Hub com a
  renda habitual da PNAD Contínua, contra 16% das brancas."

## 12. Afirmações proibidas

- "A pobreza acabou caindo por causa do Bolsa Família" (descrição, não causa).
- Comparar níveis em R$ entre anos (valores nominais).
- Comparar 2020–21 com os demais anos sem dizer que é a Visita 5 durante a pandemia.
- Apresentar as taxas em PPC como "a pobreza extrema do Brasil segundo o Banco Mundial" ou compará-las em nível com
  as da Poverty and Inequality Platform.
