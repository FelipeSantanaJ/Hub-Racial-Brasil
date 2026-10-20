# Ficha de pesquisa — `E3` · Aprendizado: a proficiência no SAEB difere por raça com o mesmo nível socioeconômico e na mesma escola?

| Campo | Valor |
|---|---|
| ID no plano | `E3` (`docs/PLANO_DE_ANALISE.md`, Bloco E) |
| Onda | 4 (parte 2, fontes do INEP) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Proposto** |
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
