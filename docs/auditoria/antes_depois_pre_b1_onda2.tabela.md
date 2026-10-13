| Tabela | Linhas | Pontos idênticos (dif. máx. rel.) | EP novo/antigo: mediana (mín–máx) | Nominal: sim→não / não→sim | FDR: sim→não / não→sim | Colunas novas |
|---|---|---|---|---|---|---|
| `quebra_estrutural.parquet` | 3 | **NÃO** (3.0e+00) | — | — | — | `coef_mudanca_inclinacao_pp_por_ano`, `ep_mudanca_inclinacao`, `ep_mudanca_patamar`, `gl_ewc`, `p_valor`, `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `ritmo_convergencia_hiatos.parquet` | 3 | n/a: ordem/chave 'tendencia_confiavel' diverge | — | — | — | `ep_ewc`, `ep_gls_ar1`, `ep_iid`, `ep_newey_west`, `ic_inferior`, `ic_log_inferior`, `ic_log_superior`, `ic_superior`, `inclinacao_gls_ar1`, `inclinacao_pct_por_ano_log`, `rho_residuos`, `tendencia_log_confiavel` |

Outros 0 parquets sem colunas de inferência: estimativas idênticas e nenhuma coluna nova.
