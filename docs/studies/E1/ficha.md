# Ficha de pesquisa — `E1` · Em que idade e em que transição o hiato educacional aparece (frequência, funil)

| Campo | Valor |
|---|---|
| ID no plano | `E1`, `E2` (parte PNADC) (`docs/PLANO_DE_ANALISE.md`, Bloco E) |
| Onda | 4 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 20/10/2026) |
| PR | `onda4/e-h` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026).

## 1. Pergunta

Em que idade aparece a diferença de escolarização entre crianças e jovens brancos, negros e indígenas — na frequência
à escola, no atraso (estar numa etapa abaixo da esperada para a idade) ou na conclusão de cada etapa — e como isso
mudou entre 2012 e 2025–26?

## 2. Tipo

`D`. Descrição por idade em corte transversal (idade × coorte confundidas; B4). Não diz por que a diferença existe
(pobreza, trabalho, qualidade da escola: mecanismos do plano, evidência externa).

## 3. Estimando

- **E1 — frequência por idade simples** (5 a 29 anos): % que frequenta escola ou curso regular (`V3002` = 1), por raça;
  diferença Branca − Negra e Branca − Indígena em p.p.
- **E1 — conclusão por idade**: % com fundamental completo (`VD3004` ≥ 3) aos 16, % com médio completo (≥ 5) aos 19 e
  aos 25–29, % com superior completo (= 7) aos 25–29.
- **E2 — funil** (por idade, raça): (a) frequenta; (b) frequenta a etapa **adequada** (6–14 no fundamental; 15–17 no
  médio ou acima; 18–24 no superior), harmonizando `V3003` (2012–2015) e `V3003A` (desde 2016); (c) atraso = frequenta
  etapa abaixo da adequada; (d) fora da escola sem ter concluído a etapa adequada ("evasão" no sentido de estoque).
- **Idade em que o hiato "aparece":** a primeira idade em que a diferença de frequência ou de etapa adequada passa de
  5 p.p. com IC excluindo zero (limiar fixado aqui).
- **Períodos:** janelas 2012 (4 trimestres) e 2025T3–2026T2; série dos 2º trimestres para o hiato de conclusão do médio
  aos 19.

## 4. População

Pessoas de 5 a 29 anos da PNAD Contínua trimestral (todas, não P1); Branca, Negra, Indígena (Amarela e Ignorado fora).
Pesos `V1028`.

## 5. Método

- **Estimador:** proporções ponderadas por domínio (idade × raça).
- **Incerteza:** linearização Estrato/UPA (`variancia.influencia_media`); diferença entre raças pela diferença das
  influências (mesma amostra). Mudança entre janelas com a covariância das UPAs comuns.
- **FDR:** família = as diferenças Branca − grupo de um indicador × janela ao longo das idades (BH).
- **Supressão:** Indígena por idade simples tem n pequeno: célula com n < 30 ou CV > 30% não publica; também por faixas
  de 3 anos.

## 6. Dados

PNAD Contínua trimestral v2: `V2009`, `V2010`, `V3002`, `V3003` (2012–4T2015), `V3003A` (desde 2016), `VD3004`.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **A diferença nasce no fim do fundamental e no médio** (atraso acumulado, saída aos 15–17) | Frequência quase igual até 14 anos (\|dif\| < 2 p.p.); diferença de etapa adequada > 5 p.p. a partir de 12–15 anos |
| H2 | **A diferença nasce cedo** (pré-escola e anos iniciais) | Diferença de frequência ou etapa adequada > 5 p.p. já antes dos 10 anos |
| H3 | **Convergência na educação básica, não no superior** | Entre 2012 e 2025–26, a diferença de médio completo aos 19 cai (IC da mudança exclui zero), e a de superior completo aos 25–29 não cai |

## 8. O que refutaria

- H1 refutada se a diferença de frequência antes dos 14 anos for ≥ 2 p.p. ou se a de etapa adequada não passar de 5 p.p.
  até os 17.
- H2 refutada se nenhuma diferença > 5 p.p. (IC excluindo zero) aparecer antes dos 10 anos.
- H3 refutada se a diferença de superior aos 25–29 também cair com IC excluindo zero (convergência geral), ou se a do
  médio aos 19 não cair.

## 9. Armadilhas

- **Quebra do questionário de educação em 4T2015** (F6): `V3003` → `V3003A`; a harmonização das etapas regulares é
  própria (fundamental 03→04, médio 05→06, superior 07→08; conferida pela idade média de cada código) e fica
  *(a confirmar)* contra o dicionário.
- **Coorte e período:** a idade 19 em 2012 e em 2026 são coortes diferentes; não é trajetória individual.
- **Reclassificação racial** (B2): a composição de quem se declara negro muda entre as janelas.
- EJA mistura idades; aparece como etapa abaixo da adequada para quem tem 15–24.
- 2020–21 (pandemia, telefone) fora das janelas e marcado na série.

## 10. Resultados

Tabela: `e1_escolarizacao_idade` (`src/processing/bloco_eh.py`). Diferenças Branca − grupo em p.p.; IC 95%.

**Frequência e etapa adequada, Branca − Negra, por idade**

| Idade | Frequenta 2012 | Frequenta 2025–26 | Etapa adequada 2012 | Etapa adequada 2025–26 |
|---|---|---|---|---|
| 6–14 | 0,6 | 0,0 | 1,1 | −0,1 |
| 14 | 1,7 | 0,3 | 2,0 | 0,4 |
| **15** | 1,8 | 1,1 | **18,2** (16,5–19,9) | **10,0** (8,1–11,9) |
| 16 | 3,5 | 0,6 | 17,2 | 6,5 |
| 18–24 | 6,9 | **11,8** (10,8–12,8) | 13,1 | 14,0 |
| 25–29 | 3,2 | 4,6 | — | — |

**Conclusão de etapas** (% e diferença Branca − Negra)

| Indicador | 2012 Branca / Negra | Dif. 2012 | 2025–26 Branca / Negra | Dif. 2025–26 | Mudança |
|---|---|---|---|---|---|
| Fundamental completo aos 16 | 76,3 / 59,2 | 17,1 | 90,2 / 83,2 | 7,0 (5,6–8,4) | — |
| Médio completo aos 19 | 61,4 / 41,0 | 20,5 | 81,1 / 68,3 | 12,8 (10,9–14,7) | **−7,7 (−10,3 a −5,2)** |
| Médio completo aos 25–29 | 70,7 / 52,1 | 18,6 | 85,1 / 73,0 | 12,1 (11,2–13,0) | −6,5 (−7,8 a −5,2) |
| Superior completo aos 25–29 | 23,1 / 7,6 | 15,4 | 34,8 / 16,3 | **18,5 (17,3–19,7)** | **+3,1 (+1,5 a +4,6)** |

Branca − Indígena, janela recente: médio aos 19 14,9 (5,0–24,8); superior aos 25–29 22,8 (16,3–29,3).
Fora da escola sem médio completo aos 25–29: 17,0 p.p. a mais para negros em 2012, 11,6 em 2025–26.

**Limitação do indicador (descoberta ao ler os resultados):** "etapa adequada" conta o fundamental como adequado até os
14 anos, então o atraso **dentro** do fundamental só aparece aos 15. A diferença de etapa adequada "nasce" aos 15 por
construção; o atraso pode vir de antes. Medi-lo exige a série (`V3006`), não feito nesta onda.

**Leitura das hipóteses**

- **H1 (a diferença nasce no fim do fundamental/médio):** **confirmada** — frequência quase igual até os 14 (≤ 1,7 p.p. em
  2012, ≤ 0,3 em 2025–26) e diferença de etapa adequada de 10 p.p. aos 15 (18 em 2012), com a ressalva acima.
- **H2 (a diferença nasce cedo):** **refutada** para frequência e etapa — nenhuma diferença > 5 p.p. antes dos 10 anos
  (o maior valor foi 4,6 aos 6 anos em 2012; −1,7 em 2025–26).
- **H3 (convergência na básica, não no superior):** **confirmada, e mais forte:** a diferença de médio completo caiu
  7,7 p.p., e a de superior completo **aumentou** 3,1 p.p. — os dois grupos ganharam diploma, os brancos mais.
- Aos 18–24, a diferença de **frequência** cresceu (6,9 → 11,8 p.p.): a desigualdade se deslocou para a entrada no
  superior.

## 11. Afirmações permitidas

- "Até os 14 anos, crianças brancas e negras frequentam a escola na mesma proporção; aos 15, 10% a mais das brancas
  já estão no ensino médio (2025–26)."
- "A diferença no ensino médio completo aos 19 anos caiu de 21 para 13 pontos desde 2012; a de diploma superior aos
  25–29 aumentou, de 15 para 19 pontos."

## 12. Afirmações proibidas

- "A desigualdade educacional só começa aos 15 anos" (o indicador não vê atraso dentro do fundamental).
- Tratar as idades como trajetória de uma mesma geração.
