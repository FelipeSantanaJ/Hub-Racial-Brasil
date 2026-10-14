# Ficha de pesquisa — `D3` · Ocupação: segregação e hiato dentro da mesma ocupação

| Campo | Valor |
|---|---|
| ID no plano | `D3.2`, `D3.3`, `D3.4` (`D3.1` está no D1; `D3.5` só literatura) (`docs/PLANO_DE_ANALISE.md`, Bloco D) |
| Onda | 3 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-14 / 2026-10-14 |
| Estado de publicação | **Proposto** |
| PR | `onda3/d` |

> Seções 1–9 escritas **antes** de rodar (14/10/2026).

## 1. Pergunta

Quão separados pessoas brancas e negras estão entre ocupações, isso mudou desde 2012, e quanto do hiato de renda
persiste **dentro da mesma ocupação detalhada** (CBO-Domiciliar de 4 dígitos)?

## 2. Tipo

`D` (segregação) e `C` (hiato dentro da ocupação). A ocupação é **mediadora** (D3.4): resulta de instrução, rede,
território e discriminação na contratação/promoção. Por que as ocupações diferem (D3.5) é `M`: o Hub não responde.

## 3. Estimando

- **D3.2 — segregação ocupacional** Branca × Negra entre ocupados em P1: índice de dissimilaridade de Duncan (D) e
  índice de informação de Theil (H, entropia), em dois níveis — grupamento `VD4011` (10 grupos) e CBO de 4 dígitos
  (`V4010`, ~430 códigos). Como D e H crescem com células pequenas, cada valor vem com o **valor esperado sob
  alocação aleatória** (raça sorteada mantendo o tamanho das ocupações; 20 sorteios) e o excesso sobre ele.
  Série: 2º trimestres de 2012 a 2026. Janelas 2012 e 2025T3–2026T2 com IC por bootstrap de Rao-Wu (100).
- **D3.3 — hiato dentro da ocupação:** coeficiente de Negra em ln renda com efeitos fixos de CBO de 4 dígitos
  (absorvidos por desvio da média ponderada da ocupação) e os demais controles da E8 do D1 (idade, sexo, instrução,
  território, horas, vínculo, atividade). Comparado com a E8 (grupamento de 10 grupos) e com a E7 sem ocupação.
- **D3.4:** quadro "com e sem ocupação" (E6 × E8 × CBO-4) e o texto sobre mediação.

## 4. População

P1, Branca × Negra (Indígena: só no D3.3, com ressalva de amostra). CBO ignorada/mal definida (`V4010` nulo ou 0000)
fica como categoria própria no D3.3 e fora da segregação.

## 5. Método

- **Segregação:** D = ½ Σ_o |b_o/B − n_o/N|; H = Σ_o (t_o/T)(E − E_o)/E, com E a entropia de dois grupos (ponderada
  por `V1028`).
- **D3.3:** WLS após retirar a média ponderada de y e de X dentro de cada CBO (Frisch-Waugh-Lovell); EP pela
  influência linearizada por Estrato/UPA (sem correção pelos ~430 parâmetros de ocupação, desprezível com n ≈ 800 mil;
  ocupações com uma só observação não contribuem).
- **FDR:** não há bateria de testes.

## 6. Dados

PNAD Contínua trimestral v2: `V4010`, `VD4011`, demais variáveis do D1.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Segregação em queda:** a dessegregação acompanhou a expansão educacional | D e H (CBO-4, excesso sobre o aleatório) menores em 2025–26 que em 2012, com IC da mudança excluindo zero |
| H2 | **O hiato é sobretudo "entre ocupações":** com a ocupação detalhada o hiato condicional cai muito | Coeficiente com FE de CBO-4 ≤ 70% do coeficiente da E8 |
| H2' | **O hiato persiste dentro da ocupação** (mesma ocupação, salário diferente) | Coeficiente com FE de CBO-4 > 70% do da E8 |

## 8. O que refutaria

- H1 refutada se a mudança do excesso de segregação (CBO-4) tiver IC incluindo zero ou for positiva.
- H2 × H2': decide-se pela razão FE-CBO-4 ÷ E8 (limiar de 70% fixado aqui); se o IC da razão cruzar 70%, nenhuma das
  duas é afirmada.

## 9. Armadilhas

- **Viés de células pequenas** em D e H (por isso o benchmark aleatório).
- **CBO-Domiciliar** é codificada a partir de texto livre; erros de codificação jogam pessoas em códigos vizinhos e
  tendem a reduzir a segregação medida.
- **Mediação:** absorver a ocupação "explica" o hiato por um canal que pode ser ele mesmo discriminatório (D3.4).
- **Dentro da ocupação ≠ mesma firma, mesma função:** sem RAIS identificada (D3.5/D8.2), o hiato dentro da CBO mistura
  firma, setor e função.
