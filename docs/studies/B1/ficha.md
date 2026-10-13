# Ficha de pesquisa — `B1` · Tendência 2012–2026 do hiato, com EP robusto a autocorrelação e quebras

| Campo | Valor |
|---|---|
| ID no plano | `B1` (`docs/PLANO_DE_ANALISE.md`, Bloco B) |
| Onda | 2 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (proposto) |
| PR | `onda2/b-c` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

O hiato racial de renda caiu, subiu ou ficou estável de 2012 a 2026? Em que ritmo (p.p./ano e log-pontos/ano), com
incerteza que respeite a autocorrelação da série, e houve mudança de patamar na recessão (2015), na pandemia (2020)
ou no pós-pandemia (2022)?

## 2. Tipo

`D`. Tendência descritiva; as quebras são datas fixadas antes, não estimadas, e não têm leitura causal.

## 3. Estimando

- Inclinação β da reta hiato_t = α + β·t (t em anos), para as séries:
  - P1, trimestral: hiato % e log-pontos Branca × Negra, Branca × Indígena, Preta × Parda (`hiato_racial`,
    `hiato_branca_indigena`, `hiato_preta_parda`, `a2_metricas_hiato`);
  - Bloco T: hiato P4 (todos os adultos) Branca × Negra total, homens, mulheres (`sensibilidade_hiato_populacao`);
    hiato da renda domiciliar per capita (`t1_renda_domiciliar_per_capita`, anual, 2012–2025).
- Mudança de patamar: γ_k em hiato_t = α + β·t + Σ_k γ_k·1[t ≥ t_k], t_k ∈ {2015T1, 2020T1, 2022T1}.
- **R6:** refazer `ritmo_convergencia_hiatos` e `quebra_estrutural` com o mesmo EP.

## 4. População

P1 (ocupados 18+ com `VD4016` > 0) e, ao lado (Bloco T), P4 e a população inteira com renda domiciliar per capita.

## 5. Método

- **Estimador:** OLS sobre a série publicada (cada ponto já é uma estimativa design-based).
- **Incerteza:** **EWC** com t de Student (ν = ⌊0,4·T^(2/3)⌋ = 5 para T = 58; = 2 para as anuais), Newey-West e GLS
  AR(1) ao lado (`src/inference/tendencia.py`; escolha justificada por simulação nas pendências da Onda 1). Uma
  tendência é chamada de **confiável** só se os três ICs excluem zero e GLS tem o mesmo sinal.
- **FDR:** não se aplica a tendências (decisão do Ponto de parada 1: tendência usa correção de autocorrelação, não
  FDR sobre trimestres). As 3 quebras de uma série formam uma família (BH).
- **EMD:** para "o hiato B×I não sobe", EMD = (t_{0,975;ν} + t_{0,80;ν}) × EP da inclinação.

## 6. Dados

Tabelas já publicadas em `data/processed` (derivadas da PNAD Contínua trimestral v2 e anual v2).

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Convergência lenta** do hiato Branca × Negra em P1 (OLS i.i.d.: −0,78 p.p./ano) | β < 0 confiável |
| H2 | **Queda em degrau, não tendência:** o hiato caiu de patamar depois da pandemia e ficou estável | γ_2022 < 0 e β (com degraus) não distinguível de zero |
| H3 | **Divergência Branca × Indígena** (afirmação retirada por falta de HAC) | β > 0 confiável na série B×I |
| H4 | **Bloco T conta outra história:** na população inteira (P4, per capita) o hiato não cai | β de P4/T1 com IC incluindo zero |

## 8. O que refutaria

- H1 é refutada se o IC EWC da inclinação de Branca × Negra (P1) incluir zero.
- H3 é **refutada para fins de publicação** (a afirmação continua retirada) se a inclinação B×I não for confiável.

## 9. Armadilhas

- Série com degrau (pandemia) faz a reta "ver" tendência que é degrau: por isso o modelo com degraus.
- 58 trimestres não são 58 evidências (rotação de domicílios) — o EWC trata, mas cobre ≈ 89% com AR(1) 0,7.
- Hiato % e log-pontos podem discordar quando o nível muda muito (convergência proporcional).
- Composição racial muda no tempo (F1): a tendência mistura renda com reclassificação (B2).

## 10. Resultados

`b1_tendencia_hiato.parquet` e `b1_degraus_hiato.parquet`. Inclinação por ano (IC 95% EWC; "confiável" = EWC,
Newey-West e GLS AR(1) excluem zero):

| Série | 2012 → fim | Inclinação (p.p./ano) | Confiável? | Desde 2022 (p.p./ano) |
|---|---|---|---|---|
| P1 · Branca × Negra | 74,2% → 65,7% | **−0,78** (−1,25 a −0,32) | sim | +0,55 (−0,14 a 1,25) |
| P1 · Branca × Negra (log-pontos/ano) | 0,555 → 0,505 | −0,0046 (−0,0073 a −0,0019) | sim | — |
| P1 · Branca × Indígena | 78,4% → 70,9% | +0,52 (−0,16 a 1,21) | **não** | +1,5 (−9,2 a 12,1) |
| P1 · Preta × Parda | 0,3% → −6,0% | −0,31 (−0,51 a −0,12) | sim | −0,87 (−1,66 a −0,09) |
| P4 · Branca × Negra | 79,0% → 71,8% | −0,91 (−1,88 a 0,05) | não (ρ = 0,89) | −0,05 (−0,25 a 0,15) |
| P4 · Branca × Negra, mulheres | 78,8% → 76,1% | −0,74 (−1,73 a 0,25) | não | −0,15 |
| T1 · Branca × Negra (domiciliar, anual) | 98,7% → 81,7% | −1,24 (−3,13 a 0,66) | não (ν = 2; NW: −1,93 a −0,55) | — |

**Degraus** (modelo com tendência comum e mudanças de patamar em 2015T1, 2020T1, 2022T1):

| Série | Tendência com degraus | Degrau 2015T1 | Degrau 2020T1 | Degrau 2022T1 |
|---|---|---|---|---|
| P1 · Branca × Negra (p.p.) | **−0,16 (−0,63 a 0,30)** | +1,2 (−0,8 a 3,2) | −2,5 (−6,9 a 1,9) | **−5,0 (−6,8 a −3,1)** |
| P4 · Branca × Negra (p.p.) | −0,08 (−1,06 a 0,91) | +4,8 (0,5 a 9,0) | −2,5 | **−10,3 (−16,9 a −3,6)** |
| P4 · mulheres (p.p.) | −0,02 | **+4,4 (1,6 a 7,2)** | +0,5 | **−12,1 (−19,1 a −5,2)** |

**R6 refeito** (`ritmo_convergencia_hiatos`, `quebra_estrutural`; antes × depois em
`docs/auditoria/antes_depois_pre_b1_onda2.json`): as inclinações pontuais não mudam (mesma reta); o EP agora é EWC.
Branca × Indígena continua **sem tendência confiável** (p = 0,11): a afirmação "o hiato Branca × Indígena sobe"
segue retirada. A coluna "anos para zerar" saiu (é o B6). No teste tipo Chow, com EWC e BH entre os 3 eventos, a
reforma da previdência (2019T4) **deixa de ser significativa** (p ajustado 0,17); reforma trabalhista (2017T3) e
recessão (2015T1) seguem (p ajustado 0,04). O coeficiente de patamar passou a medir o salto **na data do evento**
(antes, por parametrização, media a diferença extrapolada até 2012T1 e não tinha leitura).

**Leitura das hipóteses.** H1 confirmada na série inteira, mas **H2 também**: quando se permite mudança de patamar,
a tendência de P1 some (−0,16 p.p./ano, IC inclui zero) e tudo vem de um degrau de −5 p.p. em 2022; desde 2022 a
série está plana. H3 refutada para publicação (B×I sem tendência confiável). H4 parcialmente: na população inteira a
queda é de degrau (2022) e não há tendência confiável; a renda domiciliar per capita cai, mas com 14 anos o EWC não
confirma (só o Newey-West).

## 11. Afirmações permitidas

- "Entre 2012 e 2026 o hiato de renda do trabalho entre pessoas brancas e negras ocupadas caiu em média 0,8 p.p. por
  ano (IC 95%: 0,3 a 1,2), mas a queda se concentrou em um degrau depois da pandemia (−5 p.p. em 2022); desde 2022
  não há tendência de queda."
- "Não há evidência de que o hiato entre pessoas brancas e indígenas esteja aumentando ou diminuindo."

## 12. Afirmações proibidas

- "O hiato vai acabar em 20XX" (é o B6, com premissas).
- "O hiato Branca × Indígena está aumentando" sem tendência confiável.
- Ler as quebras como efeito de política.

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
