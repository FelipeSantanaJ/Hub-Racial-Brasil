# Gráficos a regenerar após o B1/B3 (Etapa 2, Fase 1)

> **Atualização (13/10/2026, Onda 1): todas as imagens de `docs/img` e os decks foram regenerados** com o
> EP corrigido, a população de referência e a ponderação corrigida das médias. Pendências que continuam:
> IC do hiato % ainda divide o IC absoluto pela média Negra (R11); legendas de Oaxaca-Blinder e quebra
> estrutural (Onda 3 / R6); 3 imagens da árvore já vazias antes (células de mulheres sem instrução).
> O texto abaixo é o registro histórico da Fase 1.

**Estado: nenhum gráfico foi regenerado na Fase 1** (instrução do prompt). As imagens em
`docs/img` abaixo ainda mostram IC, p-valor ou asteriscos calculados com a fórmula antiga
(E1) e o Welch antigo (E2). **Não usar em publicação até a regeneração.**

Levantamento por busca de `ic_inferior`, `ic_superior`, `se`, `p_valor`, `significativo`,
`fill_between` e `errorbar` em `src/processing/graficos_*.py` e `apresentacao_*.py`
(12/10/2026). As séries de pontos (sem banda nem asterisco) não dependem do EP e não
entram aqui.

## Depende do EP corrigido (B1) — banda de IC ou asterisco de Welch

| Gerador (arquivo:linha) | Imagem(ns) em `docs/img` | O que muda | Parquet de origem |
|---|---|---|---|
| `graficos_fase1.py:1025-1030` `grafico_hiato_percentual` | `hiato_racial_percentual.png` | Banda de IC 95% (≈57× mais larga) | `hiato_racial` |
| `graficos_fase1.py:1059` `grafico_hiato_absoluto` | `hiato_racial_absoluto.png` | Banda de IC | `hiato_racial` |
| `graficos_fase1.py:1087-1092` `grafico_hiato_preta_parda_percentual` | `hiato_preta_parda_percentual.png` | Banda de IC | `hiato_preta_parda` |
| `graficos_fase1.py:1287` `_grafico_hiato_bar` | `hiato_genero_*`, `hiato_faixa_etaria_*`, `hiato_escolaridade_*`, `hiato_geracao_*` (barras, 1 dimensão) | Asteriscos `***/**/*/n.s.` | `hiato_<dims>_<escopo>` |
| `graficos_fase1.py:1315`, `:1375` `_grafico_hiato_heatmap(_paineis)` | `hiato_<2 ou 3 dims>_{todas,pretaparda}.png` | Asteriscos | `hiato_<dims>_<escopo>` |
| `graficos_arvore.py:167` `_fig_hiato_bar` + `:309` `_hiato_snap_1` | 21 imagens `arv_*_hiato_snapshot*.png` (inclui `arv_raca_hiato_snapshot.png`) | Asteriscos | `hiato_arvore` |
| `graficos_arvore.py:228` `_fig_hiato_heatmap` | 10 imagens `arv_*_hiato_<fatia>.png` (heatmaps raça × gênero/geração × instrução) | Asteriscos | `hiato_arvore` |
| `graficos_causal_cotas.py:36` `grafico_event_study` | `causal_eventstudy_participacao_{negra,preta,parda,indigena}.png`, `causal_eventstudy_hiato_renda.png` | Banda de IC (EP por célula) | `did_cotas_servico_publico_curvas` |
| `apresentacao_fase1.py:226` (legenda do slide) | `docs/Datahub_Racial_Brasil_Fase1.pptx` | Texto "todos os 58 trimestres são estatisticamente significativos" continua **verdadeiro** (z ≥ 18,8); o subtítulo "Welch, IC 95%" precisa da imagem nova | — |

## Não depende do E1, mas a legenda precisa de revisão

| Gerador | Imagem | Motivo |
|---|---|---|
| `graficos_fase1.py:1654-1663` `grafico_oaxaca_blinder_decomposicao` | `oaxaca_blinder_decomposicao.png`, `decomposicao_hiato_ocupacional.png` | p-valor do WLS cluster por UPA (não usa o EP corrigido); rótulo do resíduo precisa seguir a regra R5 (Onda 3) |
| `graficos_fase1.py:1689` `grafico_oaxaca_blinder_quantis` | `oaxaca_blinder_quantis.png` | Idem; RIF sem sensibilidade de banda (R4) |
| `graficos_fase1.py:1793` `grafico_quebra_estrutural` | `hiato_quebra_estrutural.png` | OLS i.i.d. sobre a série (R6, sem HAC) |
| `graficos_causal_cotas.py` (coortes) | `causal_cohortes_universitaria_{negra,indigena}.png` | Desenho A (R2): reespecificação na Onda 5 |

## Contagem

- Dependem do EP/Welch corrigido: 5 do `graficos_fase1` em série/barras principais + 22 multidimensionais
  (`hiato_<dims>_<escopo>.png`, inclusive as históricas) + 31 da árvore + 5 de event-study
  ≈ **63 imagens** e 1 slide. Conferência imagem a imagem: **NÃO VERIFICADA** (contagem por padrão de nome).
- Total em `docs/img`: **721** arquivos (540 `arv_*`).
- Para regenerar: rodar `graficos_fase1`, `graficos_arvore` e `graficos_causal_cotas` depois do
  PR da Fase 1. As legendas de asterisco devem passar a usar `significativo_fdr` (ou explicitar que são nominais).
