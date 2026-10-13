# Ficha de pesquisa — `S1` · O hiato muda quando mudamos a população?

| Campo | Valor |
|---|---|
| ID no plano | `S1.1`, `S1.2` (`docs/PLANO_DE_ANALISE.md`, Bloco S); serve também a `F2`/`F3` (Bloco F) |
| Onda | 1 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 13/10/2026) |
| PR | Onda 1 (`onda1/regeneracao`) |

## 1. Pergunta

O hiato de renda Branca × Negra (e Branca × Indígena, e Branca × Negra dentro de cada sexo) muda de forma
material quando a população de referência (P1: ocupados 18+ com renda do trabalho principal > 0) é trocada por
populações mais amplas ou por outro conceito de renda?

## 2. Tipo

`D` (descrição). **Justificativa:** compara o mesmo estimador sob recortes diferentes; não decompõe nem atribui
causa. Uma diferença entre P1 e P4 mostra quanto do hiato "extensivo" vem de quem não está ocupado, não por quê.

## 3. Estimando

Hiato % = 100 × (média Branca ÷ média do grupo − 1), relativo ao grupo de menor renda (convenção do Hub), por
trimestre (P1–P4) e por ano (P1 × P5). Diferença Δ = hiato(Pk) − hiato(P1), em pontos percentuais.

## 4. População

| | Universo (18+) | Renda |
|---|---|---|
| P1 (referência) | Ocupados com `VD4016` > 0 | `VD4016` (habitual, trabalho principal), real |
| P2 | Ocupados; sem rendimento = 0 | `VD4016` |
| P3 | Ocupados com `VD4019` > 0 | `VD4019` (todos os trabalhos) |
| P4 | Todas as pessoas; não ocupados = 0 | `VD4016` |
| P5 | Todas as pessoas | `VD5008` (domiciliar per capita, habitual de trabalhos + efetivo de outras fontes), PNADC anual |

- **Exclusões e quanto pesam:** `composicao_populacao_referencia.parquet` (S0.1).
- **Sensibilidade obrigatória:** esta ficha É a sensibilidade de F2/F3. 14+ fica para depois (só muda a margem de
  idade; o recorte histórico do Hub era 14+ com `VD4019`, que é P3 com 14+).

## 5. Método

- **Estimador:** `sensibilidade_populacao.hiatos_populacoes`: as médias de cada população são domínios de um mesmo
  universo (todas as pessoas 18+ do trimestre/ano); o hiato é uma razão de médias.
- **Incerteza:** linearização de Taylor com Estrato/UPA (`linearizacao_taylor_estrato_upa`); o EP de Δ inclui a
  covariância entre as populações (amostras sobrepostas). Testado contra o método delta de `variancia.py`.
- **Critério de "diferença grande" (fixado no plano antes de rodar):** |Δ| > 10% do hiato de P1 **e**
  |Δ| > 1,96 × EP(Δ). Se valer para P2 ou P4, o Bloco T vira eixo principal.
- **Família de testes (FDR):** não se aplica: o critério é de magnitude com IC, não um teste de hipótese por
  célula. A leitura é da série inteira, não de trimestres isolados.
- **EMD:** não se aplica (não há afirmação de "não há diferença" sem IC; o IC de Δ é reportado).
- **Supressão:** comparações com Indígena trazem n por grupo; leitura por trimestre com cautela.

## 6. Dados

| Fonte | Variáveis | Período | Extrato | Acesso |
|---|---|---|---|---|
| PNAD Contínua trimestral | V2010, V2007, V2009, VD4002, VD4016, VD4019, V1028, UPA, Estrato + deflator | 2012T1–2026T2 | `data/raw/pnadc_extraido_v2` | público |
| PNAD Contínua anual (Visita 1; Visita 5 em 2020–21) | V2010, V2007, V2009, VD4002, VD4016, VD5008, V1032, UPA, Estrato | 2012–2025 | `data/raw/pnadc_anual_v2` | público |

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | A seleção para P1 é parecida entre raças | P2 e P4 com hiato próximo de P1 (Δ pequeno) |
| H2 | Negros têm menos acesso à ocupação com renda (desocupação, desalento, sem rendimento) | P4 com hiato **maior** que P1; Δ maior para mulheres |
| H3 | O conceito de renda importa (trabalho secundário mais frequente entre brancos) | P3 com hiato maior que P1 |
| H4 | A família redistribui renda (domicílio) | P5 diferente de P1, sinal incerto (tamanho de família, rendas não do trabalho) |

## 8. O que refutaria

A decisão F3 (usar P1 como referência) **não** é refutada por Δ grande em P2/P4: isso só obriga a publicar P1
junto com P4/P5 (Bloco T como eixo). Ela seria revista se P1 se mostrasse instável (EP muito maior que o de P4)
ou se a direção do hiato mudasse entre populações.

## 9. Armadilhas

- Em P4 o "zero" dos não ocupados é uma convenção forte: mistura renda com acesso; ler junto com S0.1/S0.2.
- P5 é anual e nominal (o hiato % dentro do ano não depende do deflator); 2020–21 vêm da Visita 5 (quebra de
  série possível). Não há 2026 no anual.
- Coleta por telefone em 2020–21 muda quem aparece na amostra (S1.5).
- Reclassificação racial (F1) muda a composição dos grupos ao longo do tempo.

## 10. Resultados

**Trimestral, 2012T1–2026T2 (58 trimestres)** — `sensibilidade_hiato_populacao.parquet`. Δ = hiato(Pk) − hiato(P1).

| Comparação | P1 2026T2 (EP) | Δ P2 médio | Δ P3 médio | Δ P4 médio (mín.–máx.) | Trimestres com "diferença grande" em P4 |
|---|---|---|---|---|---|
| Branca × Negra | 65,7% (1,8) | +0,6 p.p. | +1,2 p.p. | **+8,9** (+4,3 a +18,6) | **40 de 58** |
| Branca × Negra, homens | 70,6% (2,2) | +0,6 | +1,4 | +4,9 (+0,3 a +13,9) | 13 de 58 |
| Branca × Negra, mulheres | 61,6% (1,9) | +0,9 | +0,8 | **+17,5** (+11,4 a +28,7) | **58 de 58** |
| Branca × Indígena | 70,9% (12,1) | +2,9 | 0,0 | +16,3 (+1,1 a +32,3) | 35 de 58 |

P2 e P3 **nunca** passam no critério (Branca × Negra; P2 em 3 trimestres para Indígena). Em 2026T2, Branca × Negra:
P4 = 71,8% (Δ = +6,1 p.p., EP(Δ) = 0,7; Δ relativo = 9,4%, logo abaixo do limiar de 10% nesse trimestre).

**Anual, 2012–2025: P1 × P5 (renda domiciliar per capita)** — `sensibilidade_hiato_p5_anual.parquet`.

| Ano | P1 | P5 | | Ano | P1 | P5 |
|---|---|---|---|---|---|---|
| 2012 | 72,9% | 94,5% | | 2020* | 73,2% | 86,6% |
| 2016 | 77,8% | 97,6% | | 2022 | 64,8% | 84,3% |
| 2019 | 72,5% | 95,1% | | 2024 | 65,5% | 76,3% |
| | | | | 2025 | 66,7% | 78,8% |

\* 2020–21 da Visita 5. Branca × Negra: P5 passa no critério nos **14 de 14** anos; mulheres 14/14 (Δ médio +26 p.p.);
homens 11/14 (+10,5); Branca × Indígena 7/14 (+24,5; EP grande).

**Leitura.** O conceito de renda dentro dos ocupados (P1 × P3) e a inclusão dos ocupados sem rendimento (P2)
quase não mexem no hiato. O que mexe é **quem não está ocupado** (P4) e **a unidade domiciliar** (P5): os dois
aumentam o hiato, e o aumento é concentrado nas **mulheres**. Pelo critério fixado no plano, a diferença é
"grande" ⇒ **o Bloco T deixa de ser opcional e vira eixo principal** (decisão a confirmar no Ponto de parada).

## 11. Afirmações permitidas

- "Entre ocupados de 18+ com renda do trabalho principal, a renda média de pessoas brancas era 65,7% maior que a
  de pessoas negras no 2º trimestre de 2026 (IC 95%: 62,1% a 69,2%)."
- "O hiato quase não muda com o conceito de renda (trabalho principal ou todos os trabalhos)."
- "Contando todos os adultos (quem não está ocupado entra com renda zero), o hiato é maior, sobretudo entre
  mulheres: +17,5 p.p. em média entre 2012 e 2026." (sempre dizendo a convenção do zero)

## 12. Afirmações proibidas

- "O hiato real é X%" sem dizer a população e o conceito de renda.
- Qualquer leitura causal de Δ ("a discriminação no acesso ao emprego explica Y p.p.").
