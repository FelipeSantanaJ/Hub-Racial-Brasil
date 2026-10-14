# Ficha de pesquisa — `S1.5` · A seleção mudou no tempo (recessão 2015–16, pandemia)?

| Campo | Valor |
|---|---|
| ID no plano | `S1.5` (`docs/PLANO_DE_ANALISE.md`, Bloco S) |
| Onda | 1 (pendências) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 13/10/2026) |
| PR | `onda1/pendencias` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

A diferença racial em quem está em P1 (S0.1, S0.2) e o quanto o hiato muda quando se incluem os de fora (Δ do
S1 = hiato P4 − hiato P1) mudaram durante a recessão de 2015–16 e a pandemia, em relação a 2012–14?

## 2. Tipo

`D`. Séries com episódios marcados; diferença de nível médio entre episódios com EP robusto a autocorrelação.
Não separa causa (ciclo econômico × mudança de coleta na pandemia).

## 3. Estimando

Três séries, por Branca × Negra (total, homens, mulheres) e Branca × Indígena (total):

| Série | Fonte | Frequência |
|---|---|---|
| (a) diferença de participação em P1, Branca − grupo (p.p.) | S0.1, `composicao_populacao_referencia` | trimestral |
| (b) Δ do S1: hiato P4 − hiato P1 (p.p.) | S1.1, `sensibilidade_hiato_populacao` | trimestral |
| (c) EMM ajustado de Pr(P1), grupo − Branca (p.p.) | S0.2 refeito por ano (4 trimestres empilhados; 2026 = 2 trimestres) | anual |

Episódios (fixados antes): 2012–14 (referência) · 2015–16 (recessão) · 2017–19 · 2020–21 (pandemia; coleta por
telefone) · 2022–26. Estimando de cada episódio: nível médio da série; diferença para 2012–14.

## 4. População

Pessoas de 18+ (Ignorado fora); P1 = ocupados com `VD4016` > 0. As mesmas definições do S0 e do S1.

## 5. Método

- **Estimador:** regressão da série em dummies de episódio (sem constante); diferença para 2012–14
  (`src/inference/tendencia.medias_episodios_hac`).
- **Incerteza (revista ao rodar, 13/10/2026):** séries trimestrais (a, b) com covariância **EWC** e t de Student
  com ν = 5 g.l. (`tendencia.cov_ewc`; escolhido por simulação porque o Newey-West com defasagem 4 cobre só ≈ 78%
  com AR(1) de 0,7 em 58 pontos — ver `src/inference/tendencia.py`). Série anual (c): com 15 pontos o EWC teria
  ν = 2 e variância instável; usa-se o IC design-based de cada ano (S0.2) e anos tratados como independentes
  (aproximação: a rotação liga anos vizinhos; a covariância positiva ignorada tende a **subestimar** a variância da
  média de um episódio e a **superestimar** a da diferença entre episódios).
- **FDR:** família = as 4 diferenças de episódio de uma série × recorte; BH dentro da família.
- **EMD:** para afirmar "não mudou" na pandemia, calcular o EMD = 2,8 × EP da diferença (80% de poder, 5%) e só
  dizer "não mudou" se o EMD for menor que 1 p.p. (série a) ou 3 p.p. (série b).

## 6. Dados

PNAD Contínua trimestral, `data/raw/pnadc_extraido_v2`, 2012T1–2026T2; tabelas já publicadas do S0.1 e S1.1.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Ciclo pega mais os negros** (últimos a entrar, primeiros a sair) | Diferença de participação (a) e Δ do S1 (b) maiores na recessão e na pandemia que em 2012–14 |
| H2 | **Seleção estável** | Diferenças de episódio com IC incluindo zero e EMD pequeno |
| H3 | **Pandemia muda a amostra, não a seleção** (telefone: perde informais e pobres, mais negros) | Salto em 2020–21 que some em 2022, sem salto na recessão |

## 8. O que refutaria

- H1 é refutada se a diferença recessão − 2012–14 em (a) for negativa ou tiver IC incluindo zero, para total e
  mulheres.
- H3 não pode ser separada de H1 só com estes dados: se houver salto só em 2020–21, o texto fica "ciclo ou coleta,
  não distinguível".

## 9. Armadilhas

- **Sobreposição de amostras** (rotação): os trimestres não são independentes — por isso HAC.
- **Pandemia:** coleta por telefone e queda da taxa de resposta (F6); a reponderação não corrige tudo.
- **Composição racial muda no tempo** (F1: Preta 7,7% → 11,2%): a série mistura reclassificação com seleção.
- **2026** tem só 2 trimestres na série anual (c).

## 10. Resultados

`s15_selecao_no_tempo.parquet` (séries) e `s15_selecao_episodios.parquet` (episódios). Branca × Negra; diferença de
cada episódio para 2012–14 (IC 95%):

| Série | Recorte | Nível 2012–14 | Recessão 2015–16 | 2017–19 | Pandemia 2020–21 | 2022–26 |
|---|---|---|---|---|---|---|
| (a) participação em P1, Branca − Negra (p.p.) | Total | 2,43 | +0,56 (0,01 a 1,11) | **+1,55** (1,12 a 1,99) | +1,05 (0,42 a 1,69) | −0,13 (−0,71 a 0,45) |
| | Mulheres | 4,45 | +0,49 (0,13 a 0,84) | +0,81 (0,48 a 1,15) | +0,77 (0,36 a 1,19) | −0,19 (−0,65 a 0,26) |
| (b) hiato P4 − hiato P1 (p.p.) | Total | 7,16 | +1,99 (0,11 a 3,87) | **+5,22** (3,75 a 6,70) | +4,30 (1,79 a 6,80) | −0,69 (−2,55 a 1,17) |
| | Mulheres | 16,37 | +2,36 (0,58 a 4,14) | +3,52 (1,96 a 5,08) | **+5,12** (2,57 a 7,66) | −1,87 (−4,05 a 0,31) |
| (c) EMM ajustado de Pr(P1), Negra − Branca (p.p.) | Total | +1,45 | −0,66 (−0,94 a −0,39) | **−1,12** (−1,36 a −0,87) | −0,88 (−1,22 a −0,54) | −0,19 (−0,42 a 0,03) |

O hiato P2 − P1 (incluir ocupados sem rendimento) **diminuiu** em todos os episódios (total: −1,07 p.p. em 2022–26),
porque os ocupados sem rendimento encolheram. Indígena: diferenças de episódio com IC incluindo zero na série (a);
na (b), +5,0 p.p. (1,6 a 8,4) na pandemia.

**Leitura das hipóteses.** H1 confirmada para a recessão **e o período seguinte**: a desvantagem negra em entrar em
P1 cresceu na recessão e foi maior em 2017–19 (recuperação lenta) do que na própria recessão, tanto bruta (a) quanto
ajustada por idade, escolaridade e região (c); o efeito sobre o hiato de P4 (b) dobrou. H2 refutada. H3 refutada como
explicação única: o aumento começa em 2015 e atinge o máximo em 2017–19, antes da coleta por telefone; a pandemia
não é um salto isolado. Em 2022–26 as três séries voltam ao nível de 2012–14 (EMD de 0,79 p.p. na série a e de
2,5 p.p. na b, abaixo dos limiares de 1 e 3 p.p. fixados no item 5: **pode-se dizer "voltou ao nível de 2012–14"**).

| Saída | Arquivo | `se_metodo` | Commit |
|---|---|---|---|
| Séries | `data/processed/s15_selecao_no_tempo.parquet` | — | este PR |
| Episódios | `data/processed/s15_selecao_episodios.parquet` | EWC; anuais design-based | este PR |

## 11. Afirmações permitidas

- "A desvantagem de pessoas negras em estar ocupadas com renda aumentou durante a recessão de 2015–16 e ficou ainda
  maior em 2017–19; voltou ao nível de 2012–14 depois de 2022."
- "Entre 2017 e 2019, incluir quem estava fora do mercado aumentava o hiato racial em 12 p.p., contra 7 p.p. em
  2012–14."

## 12. Afirmações proibidas

- "A pandemia piorou a seleção de negros" sem separar coleta de ciclo.
- Tratar a inclinação de 58 trimestres como 58 evidências.

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
| 2026-10-13 | Felipe Santana | aprovada com ressalvas |
