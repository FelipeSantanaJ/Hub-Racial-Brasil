# Ficha de pesquisa — `E3` · Aprendizado: a proficiência no SAEB difere por raça com o mesmo nível socioeconômico e na mesma escola?

| Campo | Valor |
|---|---|
| ID no plano | `E3` (`docs/PLANO_DE_ANALISE.md`, Bloco E) |
| Onda | 4 (parte 2, fontes do INEP) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
| PR | `onda4/inep-pof` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026). Download autorizado pelo Felipe em 20/10/2026.

## 1. Pergunta

Estudantes brancos, pretos, pardos e indígenas aprendem o mesmo? Quanto da diferença de proficiência em língua
portuguesa e matemática persiste com o mesmo nível socioeconômico (INSE) e dentro da mesma escola, e ela cresce do 5º
ano do fundamental ao fim do médio?

## 2. Tipo

`D`/`C`. Diferenças de proficiência medida (teste padronizado), não de "capacidade". Nada aqui é efeito causal.

## 3. Estimando

- Média da proficiência na escala SAEB (`PROFICIENCIA_LP_SAEB`, `PROFICIENCIA_MT_SAEB`) por cor/raça declarada pelo
  estudante (`TX_RESP_Q04`: A Branca, B Preta, C Parda, D Amarela, E Indígena; F/nulo = não declarada), no 5º e 9º
  anos do fundamental e na 3ª/4ª série do médio. Negra = Preta + Parda.
- Diferença Branca − grupo em **pontos** e em **desvios-padrão** da série (DP ponderado do total).
- Condicional: (a) INSE do aluno (`INSE_ALUNO`, linear + quadrático); (b) + rede pública/privada e localização;
  (c) **dentro da escola** (efeitos fixos de escola, por desvio da média ponderada).
- **Crescimento entre etapas:** diferença em DP no 9º ano − no 5º; no médio − no 9º (coortes diferentes, mesmo ano).

## 4. População

Estudantes com proficiência válida (`IN_PROFICIENCIA_*` = 1) do SAEB 2023, escolas públicas (censitário) e privadas
(amostra). Pesos `PESO_ALUNO_LP` / `PESO_ALUNO_MT`.

## 5. Método

- **Estimador:** médias ponderadas e WLS (`bloco_d.Sistema`); efeitos fixos de escola por Frisch-Waugh-Lovell.
- **Incerteza:** linearização com a **escola como conglomerado** e `ESTRATO` como estrato. A proficiência de cada aluno
  tem erro de medida (`ERRO_PADRAO_*`); não há valores plausíveis nos microdados: o erro de medida infla a variância
  individual mas não vicia as médias.
- **FDR:** família = as diferenças Branca − grupo de uma série × disciplina × especificação (BH).
- **Supressão:** n < 30 ou CV > 30%.

## 6. Dados

INEP, Microdados do SAEB 2023 (`TS_ALUNO_5EF`, `TS_ALUNO_9EF`, `TS_ALUNO_34EM`), baixados em 20/10/2026.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Desvantagem que se acumula** | Diferença Branca − Negra em DP maior no 9º ano que no 5º e maior no médio que no 9º |
| H2 | **É sobretudo nível socioeconômico** | Diferença condicional ao INSE < metade da bruta |
| H3 | **É sobretudo a escola** (segregação entre escolas) | Diferença dentro da escola < metade da condicional ao INSE |
| H4 | **Pretos e pardos diferem** | Diferença Branca − Preta > Branca − Parda, com IC da diferença excluindo zero |

## 8. O que refutaria

H1 refutada se a diferença em DP não crescer entre as etapas (IC da mudança incluindo zero ou negativa). H2 refutada se
a condicional ao INSE for ≥ metade da bruta. H3 refutada se a diferença dentro da escola for ≥ metade da condicional ao
INSE. H4 refutada se o IC da diferença Preta − Parda incluir zero.

## 9. Armadilhas

- **Não resposta** à cor/raça (nulo ou "não quero declarar") e ao questionário (sem INSE): reportar a proporção por série;
  quem não responde pode ser diferente.
- **Autodeclaração de crianças** (5º ano) é menos estável que a de adultos (a confirmar).
- **Seleção por etapa:** no médio, quem evadiu ou atrasou não está na série (E1) — a diferença no médio é entre quem
  chegou lá, o que a **subestima**.
- Coortes diferentes no mesmo ano: o "crescimento" entre etapas é transversal.
- O INSE é construído com o questionário do próprio aluno (bens, escolaridade dos pais).

## 10. Resultados

Tabela: `e3_saeb_proficiencia`. SAEB 2023; 2,09 mi (5º ano), 2,09 mi (9º ano) e 1,53 mi (3ª/4ª série EM) alunos com
proficiência; 84–90% com INSE. Sem cor/raça declarada: 10,3% (5º), 4,6% (9º), 3,4% (EM). 0,2–0,4% dos registros saíram
por falta de peso. Diferenças Branca − grupo em **desvios-padrão da série** (DP ≈ 51–53 pontos); IC 95% com a escola
como conglomerado.

**Médias (escala SAEB)**

| Série | Disciplina | Branca | Parda | Preta | Indígena |
|---|---|---|---|---|---|
| 5º ano EF | LP / MT | 225,8 / 237,6 | 214,6 / 224,8 | 194,0 / 204,7 | 199,0 / 207,5 |
| 9º ano EF | LP / MT | 273,7 / 271,9 | 254,5 / 252,8 | 243,0 / 240,9 | 236,9 / 236,5 |
| 3ª/4ª série EM | LP / MT | 292,4 / 287,8 | 272,0 / 268,2 | 264,8 / 260,0 | 247,0 / 250,0 |

**Diferença Branca − Negra (DP)**

| Série | Disciplina | Bruta | + INSE | + INSE, rede, lugar, UF | + INSE, dentro da escola |
|---|---|---|---|---|---|
| 5º ano | LP | 0,29 | 0,16 | 0,11 | 0,09 |
| | MT | 0,32 | 0,16 | 0,11 | 0,08 |
| 9º ano | LP | **0,42** | 0,29 | 0,24 | **0,21** |
| | MT | 0,41 | 0,24 | 0,19 | 0,14 |
| 3ª/4ª EM | LP | 0,42 | 0,30 | 0,25 | 0,18 |
| | MT | 0,42 | 0,26 | 0,21 | 0,14 |

Em pontos, 9º ano LP: bruta 21,8 (21,1–22,5); + INSE 14,7 (14,2–15,2); dentro da escola 10,6 (10,1–11,0).

**Razões:** + INSE ÷ bruta de 0,50 (5º MT; 0,49–0,52) a 0,70 (EM LP; 0,68–0,73); dentro da escola ÷ + INSE de 0,52
(5º MT) a 0,72 (9º LP; 0,70–0,74).

**Crescimento entre etapas (DP, EP conservador):** 9º − 5º: LP +0,13 (0,11–0,15), MT +0,10 (0,07–0,12); médio − 9º: LP
−0,00 (−0,03 a 0,02), MT +0,01 (−0,03 a 0,05).

**Pretos × pardos:** desvantagem adicional dos pretos sobre os pardos (pontos), bruta / com INSE: 5º LP 19,8 / 17,2;
9º LP 11,5 / 11,0; EM LP 6,9 / 6,5 (todos com IC excluindo zero).

**Indígenas:** 9º ano LP, bruta 0,70 DP; dentro da escola, 0,37.

**Leitura das hipóteses**

- **H1 (acúmulo):** **em parte** — a diferença cresce do 5º ao 9º ano (+0,10 a +0,13 DP), mas não do 9º ao médio. A
  estabilidade no médio é compatível com a seleção de quem chega lá (E1: a diferença de etapa adequada aparece aos 15).
- **H2 (é sobretudo nível socioeconômico):** **refutada** — com o mesmo INSE sobram 50% a 70% da diferença.
- **H3 (é sobretudo a escola):** **refutada** — dentro da mesma escola sobram 52% a 72% da diferença condicional ao INSE. No 5º ano em matemática as duas razões (0,50 e 0,52) têm IC que inclui a metade: ali H2 e H3 ficam no limite.
- **H4 (pretos e pardos diferem):** **confirmada** — pretos têm proficiência menor que pardos em todas as séries, com o
  mesmo INSE; a distância diminui da 5ª série ao médio (e a não declaração é maior no 5º ano).

## 11. Afirmações permitidas

- "No 9º ano, estudantes negros têm proficiência em língua portuguesa 0,4 desvio-padrão abaixo da de estudantes brancos;
  com o mesmo nível socioeconômico e na mesma escola, a diferença é 0,2 desvio-padrão (SAEB 2023)."
- "Estudantes pretos têm proficiência menor que pardos com o mesmo nível socioeconômico."

## 12. Afirmações proibidas

- Qualquer leitura de capacidade inata; "negros aprendem menos" sem o contexto.
- "A escola não importa" (a segregação entre escolas é grande — E7; o resultado é que a diferença **também** existe
  dentro da escola).
- Ler o crescimento entre séries como trajetória de uma mesma coorte.
