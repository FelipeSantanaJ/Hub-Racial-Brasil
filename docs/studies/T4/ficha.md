# Ficha de pesquisa — `T4` · Quem está em cada décimo de renda domiciliar per capita

| Campo | Valor |
|---|---|
| ID no plano | `T4` (`docs/PLANO_DE_ANALISE.md`, Bloco T) |
| Onda | 1 (pendências) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 13/10/2026) |
| PR | `onda1/pendencias` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

Considerando todas as pessoas (todas as idades) e a renda domiciliar per capita, como cada raça se distribui pelos
décimos nacionais, e quanto a chance de estar no topo 10% e na base 10% difere entre pessoas negras, indígenas e
brancas — 2012 a 2025?

## 2. Tipo

`D`. Versão do A5 para a população inteira (Bloco T é eixo principal desde a Onda 1).

## 3. Estimando

- Para cada décimo d (limiares nacionais do ano) e raça g: participação de g no décimo (%), participação de g na
  população (%) e índice de representação = participação no décimo ÷ participação na população (1 = proporcional).
- Razão de chances de estar no topo 10% e na base 10%, Negra e Indígena vs. Branca, com IC 95%.
- Com IC: a proporção de cada grupo em cada décimo (Pr(décimo d | g)), da qual o índice deriva.

## 4. População

- **Universo:** todas as pessoas, todas as idades, da PNAD Contínua anual (Visita 1; Visita 5 em 2020–2021), exceto
  pensionistas, empregados domésticos e seus parentes (`V2005` 17–19, sem `VD5008`), como no T1.
- **Renda:** `VD5008` (renda habitual domiciliar per capita), nominal do ano (os décimos são do próprio ano).
- **Exclusões:** Ignorado fora dos grupos (fica no total e nos limiares).

## 5. Método

- **Estimador:** limiares de décimo ponderados (`V1032`) com repartição do peso empatado no limiar
  (`pnadc_core.fracao_na_fatia`, a mesma regra do A5; a renda domiciliar per capita tem muitos empates, inclusive
  em zero).
- **Incerteza:** Pr(décimo d | g) e razão de chances por linearização Estrato/UPA (os limiares tratados como fixos,
  como no A5). O domicílio é a unidade de conglomeração dentro da UPA: pessoas do mesmo domicílio têm a mesma renda
  per capita, o que a linearização por UPA já incorpora.
- **FDR:** não se aplica (sem teste publicado; leitura por IC).
- **Supressão:** Indígena por décimo com n < 30 ou CV > 30% não publica.

## 6. Dados

| Fonte | Variáveis | Período | Extrato / arquivo | Acesso |
|---|---|---|---|---|
| PNAD Contínua anual | `VD5008`, `V2010`, `V2005`, `V1032`, `UPA`, `Estrato` | 2012–2025 | `data/raw/pnadc_anual_v2` | público |

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **A sub-representação no topo é maior na renda domiciliar** que na renda do trabalho (A5: RC do topo 0,32) porque a família negra tem mais dependentes por renda | RC do topo em T4 < RC do topo em A5 |
| H2 | **Transferências comprimem a base** e reduzem a sobre-representação negra no D1 em relação ao trabalho | Índice de representação Negra no D1 de T4 menor que no A5 |
| H3 | **Convergência lenta:** o índice de representação Negra no topo sobe de 2012 a 2025 | RC do topo maior em 2025 que em 2012, com ICs que não se sobrepõem |

## 8. O que refutaria

- H1 é refutada se a RC do topo da Negra em T4 for ≥ 0,32 (valor do A5 em 2026T2) com IC acima disso.
- H3 é refutada se os ICs da RC do topo de 2012 e 2025 se sobrepuserem.

## 9. Armadilhas

- **A5 × T4 não são a mesma população** (ocupados com renda × todas as pessoas) nem o mesmo conceito (trabalho ×
  domicílio): a comparação de H1 é de "duas lentes", não de efeito.
- **Renda zero** (domicílios sem renda) concentra empates no D1: a repartição do peso no limiar é essencial.
- **2020–21 vem da Visita 5** (outro conjunto de domicílios; pandemia).
- **Valores nominais:** só os décimos e as razões são comparáveis no tempo, não os limiares em R$.
- Composição racial muda no tempo (F1).

## 10. Resultados

`t4_decimos_renda_domiciliar.parquet`. Razão de chances (vs. Branca, IC 95%):

| Ano | Topo 10%, Negra | Topo 10%, Indígena | Base 10%, Negra | Base 10%, Indígena |
|---|---|---|---|---|
| 2012 | 0,255 (0,240 a 0,270) | 0,29 (0,18 a 0,45) | 3,00 (2,85 a 3,16) | 3,5 (2,5 a 4,9) |
| 2016 | 0,231 (0,216 a 0,246) | 0,32 (0,22 a 0,49) | 2,91 (2,76 a 3,07) | 4,1 (2,6 a 6,4) |
| 2020 (Visita 5) | 0,256 (0,239 a 0,274) | 0,27 (0,15 a 0,50) | 2,48 (2,32 a 2,64) | 4,7 (3,2 a 7,0) |
| 2025 | **0,274 (0,259 a 0,290)** | 0,21 (0,15 a 0,30) | **2,38 (2,25 a 2,51)** | 3,2 (2,4 a 4,3) |

Índice de representação em 2025 (1 = proporcional): Negra 1,31 no D1 e 0,51 no D10; Indígena 1,69 e 0,40; Branca
0,59 e 1,63. Em 2025, 5,1% das pessoas negras e 16,3% das brancas estão no topo 10%; 13,1% e 5,9% na base 10%.

**Leitura das hipóteses.** H1 confirmada: na renda domiciliar per capita a chance de uma pessoa negra estar no topo
10% (RC 0,274; IC até 0,290) é menor que na renda do trabalho de P1 (A5, 2026T2: 0,316; IC desde 0,300). H2 refutada:
o índice da Negra no D1 é o mesmo nas duas lentes (1,31 no T4 em 2025; 1,32 no A5 em 2025T2). H3 refutada: a RC do
topo de 2012 (0,240 a 0,270) e a de 2025 (0,259 a 0,290) se sobrepõem — **não há convergência mensurável no topo**.
Na base há: a RC caiu de 3,00 para 2,38 (ICs disjuntos).

## 11. Afirmações permitidas

- "Em 2025, uma pessoa negra tinha cerca de um quarto da chance de uma pessoa branca de estar entre os 10% com maior
  renda domiciliar per capita (razão de chances 0,27); em 2012 era 0,26."
- "A sobre-representação de pessoas negras entre os 10% mais pobres diminuiu: a razão de chances caiu de 3,0 (2012)
  para 2,4 (2025)."

## 12. Afirmações proibidas

- "Pessoas negras são X% dos pobres" sem dizer que o critério é o décimo da renda domiciliar per capita.
- Comparar o limiar em R$ entre anos.

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
| 2026-10-13 | Felipe Santana | aprovada com ressalvas |
