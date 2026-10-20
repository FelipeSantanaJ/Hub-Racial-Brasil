# Ficha de pesquisa — `E1` · Em que idade e em que transição o hiato educacional aparece (frequência, funil)

| Campo | Valor |
|---|---|
| ID no plano | `E1`, `E2` (parte PNADC) (`docs/PLANO_DE_ANALISE.md`, Bloco E) |
| Onda | 4 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Proposto** |
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
