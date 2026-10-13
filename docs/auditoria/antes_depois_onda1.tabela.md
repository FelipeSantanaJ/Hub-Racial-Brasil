| Tabela | Linhas | Pontos idênticos (dif. máx. rel.) | EP novo/antigo: mediana (mín–máx) | Nominal: sim→não / não→sim | FDR: sim→não / não→sim | Colunas novas |
|---|---|---|---|---|---|---|
| `alfabetizacao.parquet` | 3344 | sim (8.1e-15) | — | — | — | `cv_alfabetizado`, `n_alfabetizado`, `publicavel`, `publicavel_alfabetizado` |
| `checagem_robustez_hiato_racial.parquet` | 58 | n/a: ordem/chave 'n_branca' diverge | — | — | — | — |
| `decomposicao_hiato_ocupacional.parquet` | 5 | n/a: ordem/chave 'n_branca' diverge | — | — | — | — |
| `decomposicao_oaxaca_blinder.parquet` | 7 | n/a: ordem/chave 'n_favorecido' diverge | — | — | — | — |
| `decomposicao_oaxaca_blinder_indigena.parquet` | 7 | n/a: ordem/chave 'n_favorecido' diverge | — | — | — | — |
| `decomposicao_oaxaca_blinder_pretaparda.parquet` | 7 | n/a: ordem/chave 'n_favorecido' diverge | — | — | — | — |
| `decomposicao_raca_genero.parquet` | 522 | **NÃO** (3.2e-01) | — | — | — | — |
| `desalento_subutilizacao.parquet` | 105969 | n/a: ordem/chave 'geografia' diverge | — | — | — | `cv_desalento`, `cv_forca_potencial`, `n_desalento`, `n_forca_potencial`, `publicavel`, `publicavel_desalento`, `publicavel_forca_potencial` |
| `desocupacao_por_escolaridade.parquet` | 1218 | sim (9.8e-15) | — | — | — | `cv_desocupacao`, `n_desocupacao`, `publicavel`, `publicavel_desocupacao` |
| `did_cotas_servico_publico.parquet` | 5 | **NÃO** (1.7e-01) | — | — | — | — |
| `did_cotas_servico_publico_curvas.parquet` | 115 | n/a: ordem/chave 'n_publico' diverge | — | — | — | — |
| `did_cotas_servico_publico_heterogeneidade.parquet` | 35 | **NÃO** (2.8e+00) | — | — | — | — |
| `did_cotas_servico_publico_heterogeneidade_curvas.parquet` | 805 | n/a: ordem/chave 'n_publico' diverge | — | — | — | — |
| `dupla_desvantagem.parquet` | 58 | **NÃO** (9.9e-02) | — | — | — | — |
| `escolaridade.parquet` | 544540 | n/a: ordem/chave 'geografia' diverge | — | — | — | `cv_populacao`, `n_populacao`, `publicavel`, `publicavel_populacao` |
| `extremos_composicao_racial.parquet` | 10285 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `extremos_distribuicao_racial.parquet` | 1392 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `extremos_renda_racial.parquet` | 696 | n/a: ordem/chave 'n_extremo' diverge | — | — | — | — |
| `faixas_salario_minimo.parquet` | 174 | **NÃO** (2.5e-01) | — | — | — | `cv_acima_3sm`, `cv_ate_1sm`, `cv_ate_2sm`, `n_acima_3sm`, `n_ate_1sm`, `n_ate_2sm`, `publicavel`, `publicavel_acima_3sm`, `publicavel_ate_1sm`, `publicavel_ate_2sm` |
| `funcao_quantil_racial.parquet` | 1044 | **NÃO** (1.5e-01) | — | — | — | — |
| `gini_por_raca.parquet` | 232 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `habitacao_hiato_racial.parquet` | 144 | sim (0.0e+00) | 1,0 (1,0–1,0) | 0 / 0 | 0 / 0 | — |
| `habitacao_hiato_racial_genero.parquet` | 288 | sim (0.0e+00) | 1,0 (1,0–1,0) | 0 / 0 | 1 / 0 | — |
| `habitacao_hiato_regional.parquet` | 90 | sim (0.0e+00) | 1,0 (1,0–1,0) | 0 / 0 | 0 / 0 | — |
| `hiato_arvore.parquet` | 13811 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `hiato_branca_indigena.parquet` | 58 | **NÃO** (1.8e-01) | 1,0 (0,8–1,0) | 0 / 0 | 0 / 0 | — |
| `hiato_capital_interior.parquet` | 116 | **NÃO** (6.8e-02) | — | 0 / 0 | 0 / 0 | — |
| `hiato_escolaridade_historico_pretaparda.parquet` | 406 | **NÃO** (3.9e+01) | — | 8 / 6 | 32 / 0 | — |
| `hiato_escolaridade_historico_todas.parquet` | 406 | **NÃO** (2.8e-01) | — | 0 / 0 | 0 / 0 | — |
| `hiato_escolaridade_pretaparda.parquet` | 7 | **NÃO** (7.5e-01) | — | 1 / 0 | 1 / 0 | — |
| `hiato_escolaridade_todas.parquet` | 7 | **NÃO** (2.8e-01) | — | 0 / 0 | 0 / 0 | — |
| `hiato_faixa_etaria_escolaridade_pretaparda.parquet` | 28 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `hiato_faixa_etaria_escolaridade_todas.parquet` | 28 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `hiato_faixa_etaria_historico_pretaparda.parquet` | 232 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `hiato_faixa_etaria_historico_todas.parquet` | 232 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `hiato_faixa_etaria_pretaparda.parquet` | 4 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `hiato_faixa_etaria_todas.parquet` | 4 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `hiato_formal_informal.parquet` | 116 | **NÃO** (5.9e-02) | — | 0 / 0 | 0 / 0 | — |
| `hiato_genero_escolaridade_pretaparda.parquet` | 14 | **NÃO** (1.7e+00) | — | 1 / 0 | 2 / 0 | — |
| `hiato_genero_escolaridade_todas.parquet` | 14 | **NÃO** (4.7e-01) | — | 0 / 0 | 0 / 0 | — |
| `hiato_genero_faixa_etaria_escolaridade_pretaparda.parquet` | 56 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `hiato_genero_faixa_etaria_escolaridade_todas.parquet` | 56 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `hiato_genero_faixa_etaria_pretaparda.parquet` | 8 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `hiato_genero_faixa_etaria_todas.parquet` | 8 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `hiato_genero_geracao_escolaridade_pretaparda.parquet` | 65 | **NÃO** (1.2e+01) | — | 0 / 0 | 6 / 0 | — |
| `hiato_genero_geracao_escolaridade_todas.parquet` | 67 | **NÃO** (3.1e+00) | — | 0 / 2 | 0 / 2 | — |
| `hiato_genero_geracao_pretaparda.parquet` | 10 | **NÃO** (5.9e+00) | — | 0 / 1 | 1 / 0 | — |
| `hiato_genero_geracao_todas.parquet` | 10 | **NÃO** (3.9e-01) | — | 0 / 1 | 0 / 1 | — |
| `hiato_genero_historico_pretaparda.parquet` | 116 | **NÃO** (1.4e+01) | — | 3 / 4 | 7 / 2 | — |
| `hiato_genero_historico_todas.parquet` | 116 | **NÃO** (5.4e-02) | — | 0 / 0 | 0 / 0 | — |
| `hiato_genero_pretaparda.parquet` | 2 | **NÃO** (6.8e-02) | — | 0 / 0 | 0 / 0 | — |
| `hiato_genero_todas.parquet` | 2 | **NÃO** (3.2e-02) | — | 0 / 0 | 0 / 0 | — |
| `hiato_geracao_escolaridade_pretaparda.parquet` | 33 | **NÃO** (1.7e+01) | — | 0 / 0 | 2 / 0 | — |
| `hiato_geracao_escolaridade_todas.parquet` | 34 | **NÃO** (1.2e+00) | — | 0 / 0 | 0 / 0 | — |
| `hiato_geracao_historico_pretaparda.parquet` | 220 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `hiato_geracao_pretaparda.parquet` | 5 | **NÃO** (3.5e-01) | — | 0 / 1 | 0 / 1 | — |
| `hiato_geracao_todas.parquet` | 5 | **NÃO** (6.5e-02) | — | 0 / 0 | 0 / 0 | — |
| `hiato_por_geracao.parquet` | 220 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `hiato_preta_parda.parquet` | 58 | **NÃO** (7.6e+00) | 1,0 (0,9–1,0) | 2 / 3 | 2 / 3 | — |
| `hiato_racial.parquet` | 58 | **NÃO** (4.9e-02) | 1,0 (0,9–1,0) | 0 / 0 | 0 / 0 | — |
| `hiato_regional.parquet` | 290 | **NÃO** (1.3e-01) | — | 0 / 0 | 0 / 0 | — |
| `hiato_regional_indigena.parquet` | 290 | **NÃO** (1.8e+00) | — | 4 / 2 | 5 / 2 | — |
| `hiato_regional_pretaparda.parquet` | 1566 | **NÃO** (2.3e+02) | — | 24 / 44 | 151 / 1 | — |
| `hiato_setor_publico_privado.parquet` | 116 | **NÃO** (8.6e-02) | — | 0 / 0 | 0 / 0 | — |
| `horas_trabalhadas.parquet` | 105969 | n/a: ordem/chave 'geografia' diverge | — | — | — | `cv_horas`, `cv_renda_hora`, `n_horas`, `n_renda_hora`, `publicavel`, `publicavel_horas`, `publicavel_renda_hora` |
| `informalidade.parquet` | 105969 | n/a: ordem/chave 'geografia' diverge | — | — | — | `cv_carteira`, `cv_estatutario_militar`, `cv_previdencia`, `n_carteira`, `n_estatutario_militar`, `n_previdencia`, `pct_estatutario_militar`, `pop_estatutario_militar`, `publicavel`, `publicavel_carteira`, `publicavel_estatutario_militar`, `publicavel_previdencia` |
| `mecanismo_renda_cohortes_cotas.parquet` | 2 | n/a: ordem/chave 'n_favorecido' diverge | — | — | — | — |
| `oaxaca_blinder_temporal.parquet` | 60 | n/a: ordem/chave 'n_favorecido' diverge | — | — | — | — |
| `ocupacao.parquet` | 105969 | n/a: ordem/chave 'geografia' diverge | — | — | — | `cv_desocupacao`, `n_desocupacao`, `publicavel`, `publicavel_desocupacao` |
| `percentil_de_valor_racial.parquet` | 1044 | **NÃO** (8.8e-02) | — | — | — | — |
| `perfil_quartis_racial.parquet` | 8256 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `perfil_quartis_racial_indigena.parquet` | 71 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `perfil_quartis_racial_pretaparda.parquet` | 8255 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `perfil_topo10_racial.parquet` | 2063 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `perfil_topo10_racial_indigena.parquet` | 17 | n/a: ordem/chave 'n_topo10' diverge | — | — | — | — |
| `perfil_topo10_racial_pretaparda.parquet` | 2056 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `quartis_multi_racial.parquet` | 21520 | n/a: número de linhas mudou: comparação por posição impossível | — | — | — | — |
| `quebra_estrutural.parquet` | 3 | **NÃO** (2.7e-01) | — | — | — | — |
| `renda.parquet` | 105969 | n/a: ordem/chave 'geografia' diverge | — | — | — | `cv_renda`, `n_renda`, `publicavel`, `publicavel_renda` |
| `renda_completa.parquet` | 20377 | **NÃO** (8.6e-01) | — | — | — | `cv_renda`, `n_renda`, `publicavel`, `publicavel_renda` |
| `renda_completa_geracao.parquet` | 20735 | **NÃO** (3.2e+00) | — | — | — | `cv_renda`, `n_renda`, `publicavel`, `publicavel_renda` |
| `renda_multidimensional_faixa.parquet` | 2869 | **NÃO** (5.5e-01) | — | — | — | `cv_renda`, `n_renda`, `publicavel`, `publicavel_renda` |
| `renda_multidimensional_geracao.parquet` | 2830 | **NÃO** (9.5e-01) | — | — | — | `cv_renda`, `n_renda`, `publicavel`, `publicavel_renda` |
| `renda_por_escolaridade.parquet` | 143157 | n/a: ordem/chave 'geografia' diverge | — | — | — | `cv_renda`, `n_renda`, `publicavel`, `publicavel_renda` |
| `renda_por_geracao.parquet` | 105569 | n/a: ordem/chave 'geografia' diverge | — | — | — | `cv_renda`, `n_renda`, `publicavel`, `publicavel_renda` |
| `ritmo_convergencia_hiatos.parquet` | 3 | **NÃO** (3.7e-01) | — | — | — | — |
| `sobrequalificacao.parquet` | 23109 | n/a: ordem/chave 'geografia' diverge | — | — | — | `cv_sobrequalificado`, `n_sobrequalificado`, `publicavel`, `publicavel_sobrequalificado` |
| `theil_racial.parquet` | 58 | **NÃO** (9.7e-02) | — | — | — | — |
| `transicao_desemprego_emprego.parquet` | 10 | sim (2.9e-16) | 1,0 (1,0–1,0) | — | — | — |
| `transicao_informal_formal.parquet` | 10 | sim (3.1e-16) | 1,0 (1,0–1,0) | — | — | — |

Outros 11 parquets sem colunas de inferência: estimativas idênticas e nenhuma coluna nova.
