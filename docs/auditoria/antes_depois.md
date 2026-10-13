# Antes × depois — regeneração da Fase 1 (B1 + B3)

**Gerado em:** 13/10/2026 · **Código:** branch `auditoria/fase1-p0`, commit `da7b04b` (registrado no `_meta.json` de cada tabela)
**Antes:** cópia de `data/processed` no commit `63563e3` (`data/processed/_legado/pre_b1_63563e3/`, local) · **Base de microdados:** extrato v1, a mesma de antes
**Comparador:** `python -m src.auditoria.antes_depois --legado pre_b1_63563e3` (detalhe por tabela em `antes_depois.json`)

## Resumo

| Pergunta | Resposta |
|---|---|
| Alguma estimativa pontual mudou? | **Não.** 101 de 101 parquets têm pontos idênticos (diferença relativa máxima 1,2×10⁻¹¹, arredondamento de ponto flutuante). Nenhuma linha entrou ou saiu |
| EP do hiato nacional Branca–Negra | Novo/antigo: mediana **57,1×** (45,2–82,4) |
| EP novo × bootstrap Rao-Wu Estrato/UPA (aceitação do B1) | Mediana **1,005** (mín. 0,944; máx. 1,047), 58 trimestres |
| Hiato nacional continua significativo? | **Sim, nos 58 trimestres** (z de 18,8 a 36,6) |
| Flags `significativo` nas tabelas de hiato (20.378 linhas) | Antes: 20.030 sim. Agora: **15.355 sim nominal** (4.675 sim→não, 0 não→sim) e **14.921 sim com FDR** (5.109 sim→não, 0 não→sim) |
| Onde as flags caíram | Comparações **Preta × Parda** (diferenças pequenas entre grupos próximos) e células finas: `hiato_regional_pretaparda` (1.185 de 1.566), `hiato_arvore` (2.293 de 14.598; a fração significativa cai de 99,7% para 88,1% na comparação Negra e de 99,0% para 70,4% na Indígena), históricos Preta × Parda, `hiato_preta_parda` (44 de 58 trimestres) e `hiato_regional_indigena` (41 de 290) |
| Onde nada mudou | Branca × Negra nacional, por região, gênero, faixa etária, geração, setor público/privado, capital/interior e formal/informal: 0 flags alteradas |
| Desenho B (Lei 12.990) | 40 testes de DiD, 4 com p < 0,05 (1 + 3). **Nenhum sobrevive ao BH** (menor p ajustado 0,164 na tabela principal e 0,348 na heterogeneidade). Confirma o R3 da auditoria. Esses p-valores vêm da regressão do statsmodels e não mudaram |
| Desenho A (Lei 12.711) | 0 de 48 significativos, antes e depois |
| Gap Homem Branco × Mulher Negra / raça × gênero | 58/58 e 521/522 continuam significativos (1 combinação sim→não) |

## O que mudou no conteúdo das tabelas

- **Colunas novas** (nada removido): `significativo_nominal`, `p_valor_bh`, `significativo_fdr` (com prefixo `gap_total_`, `did_`, `did_nivel_` onde o p-valor tem outro nome). `significativo` foi mantido e agora é igual a `significativo_nominal`. As tabelas de habitação ganharam também `ep_media`, `ep_hiato`, `gl_welch` e `n_amostra`, porque gravam a saída inteira de `tabela_hiatos_significancia`.
- **Habitação:** a linha do grupo de referência (hiato 0) teve o p-valor trocado de 1,0 para NaN, para não entrar na família do BH.
- **IC e p-valores** de todas as tabelas que passam por `tabela_hiatos_significancia`, `intervalo_confianca_media_ponderada` ou `_curva_event_study`.
- **`_meta.json`** ao lado de 61 parquets: `se_metodo`, `commit`, família do FDR, data.
- **Sem mudança de IC/p** (inferência por regressão do statsmodels, que não passa pelo B1): Oaxaca-Blinder (4 tabelas), quebra estrutural, ritmo de convergência, Desenho A e resumos do Desenho B. Os `_meta.json` delas dizem isso.

## Por tabela

| Tabela | Linhas | Pontos idênticos (dif. máx. rel.) | EP novo/antigo: mediana (mín–máx) | Nominal: sim→não / não→sim | FDR: sim→não / não→sim | Colunas novas |
|---|---|---|---|---|---|---|
| `checagem_robustez_hiato_racial.parquet` | 58 | sim (1.2e-15) | — | — | — | `correlacao_medias`, `ep_bootstrap_estrato_upa`, `ep_bootstrap_upa_legado`, `ep_linearizacao`, `ep_linearizacao_sem_covariancia`, `n_branca`, `n_estratos`, `n_estratos_upa_unica`, `n_negra`, `n_upas`, `p_valor_linearizacao`, `razao_linearizacao_sobre_bootstrap`, `se_metodo`, `z_bootstrap_estrato_upa`, `z_linearizacao` |
| `decomposicao_raca_genero.parquet` | 522 | sim (6.6e-15) | — | — | — | `gap_total_p_valor_bh`, `gap_total_significativo_fdr`, `gap_total_significativo_nominal` |
| `did_cotas_servico_publico.parquet` | 5 | sim (8.6e-13) | — | — | — | `did_p_valor_bh`, `did_significativo_fdr`, `did_significativo_nominal` |
| `did_cotas_servico_publico_curvas.parquet` | 115 | sim (9.3e-14) | 30,3 (24,5–38,2) | — | — | — |
| `did_cotas_servico_publico_heterogeneidade.parquet` | 35 | sim (4.2e-12) | — | — | — | `did_p_valor_bh`, `did_significativo_fdr`, `did_significativo_nominal` |
| `did_cotas_servico_publico_heterogeneidade_curvas.parquet` | 805 | sim (1.2e-11) | 24,8 (17,7–43,0) | — | — | — |
| `did_cotas_universitarias.parquet` | 8 | sim (7.2e-14) | — | — | — | `did_nivel_p_valor_bh`, `did_nivel_significativo_fdr`, `did_nivel_significativo_nominal` |
| `did_cotas_universitarias_heterogeneidade.parquet` | 40 | sim (1.5e-13) | — | — | — | `did_nivel_p_valor_bh`, `did_nivel_significativo_fdr`, `did_nivel_significativo_nominal` |
| `dupla_desvantagem.parquet` | 58 | sim (5.5e-15) | — | — | — | `gap_total_p_valor_bh`, `gap_total_significativo_fdr`, `gap_total_significativo_nominal` |
| `habitacao_hiato_racial.parquet` | 144 | sim (1.1e-13) | 53,0 (41,2–79,7) | 2 / 0 | 2 / 0 | `ep_hiato`, `ep_media`, `gl_welch`, `n_amostra`, `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `habitacao_hiato_racial_genero.parquet` | 288 | sim (1.1e-12) | 39,6 (17,6–59,9) | 28 / 0 | 29 / 0 | `ep_hiato`, `ep_media`, `gl_welch`, `n_amostra`, `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `habitacao_hiato_regional.parquet` | 90 | sim (1.7e-13) | 48,2 (27,1–101,7) | 10 / 0 | 10 / 0 | `ep_hiato`, `ep_media`, `gl_welch`, `n_amostra`, `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_arvore.parquet` | 14598 | sim (2.3e-12) | — | 2293 / 0 | 2467 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_branca_indigena.parquet` | 58 | sim (1.8e-15) | 28,2 (19,6–45,0) | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_capital_interior.parquet` | 116 | sim (1.6e-15) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_escolaridade_historico_pretaparda.parquet` | 406 | sim (1.5e-12) | — | 348 / 0 | 379 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_escolaridade_historico_todas.parquet` | 406 | sim (3.5e-15) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_escolaridade_pretaparda.parquet` | 7 | sim (1.8e-14) | — | 5 / 0 | 6 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_escolaridade_todas.parquet` | 7 | sim (2.4e-15) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_faixa_etaria_escolaridade_pretaparda.parquet` | 33 | sim (7.2e-13) | — | 25 / 0 | 28 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_faixa_etaria_escolaridade_todas.parquet` | 34 | sim (3.3e-15) | — | 7 / 0 | 7 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_faixa_etaria_historico_pretaparda.parquet` | 290 | sim (3.2e-13) | — | 220 / 0 | 240 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_faixa_etaria_historico_todas.parquet` | 290 | sim (4.5e-15) | — | 3 / 0 | 3 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_faixa_etaria_pretaparda.parquet` | 5 | sim (2.3e-14) | — | 3 / 0 | 3 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_faixa_etaria_todas.parquet` | 5 | sim (3.0e-15) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_formal_informal.parquet` | 116 | sim (1.4e-15) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_escolaridade_pretaparda.parquet` | 14 | sim (1.5e-14) | — | 10 / 0 | 12 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_escolaridade_todas.parquet` | 14 | sim (2.0e-15) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_faixa_etaria_escolaridade_pretaparda.parquet` | 64 | sim (2.0e-13) | — | 53 / 0 | 57 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_faixa_etaria_escolaridade_todas.parquet` | 66 | sim (5.3e-14) | — | 19 / 0 | 19 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_faixa_etaria_pretaparda.parquet` | 10 | sim (2.1e-14) | — | 6 / 0 | 6 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_faixa_etaria_todas.parquet` | 10 | sim (7.6e-16) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_geracao_escolaridade_pretaparda.parquet` | 65 | sim (4.1e-13) | — | 46 / 0 | 53 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_geracao_escolaridade_todas.parquet` | 67 | sim (4.8e-15) | — | 20 / 0 | 21 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_geracao_pretaparda.parquet` | 10 | sim (4.4e-14) | — | 4 / 0 | 5 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_geracao_todas.parquet` | 10 | sim (1.0e-15) | — | 1 / 0 | 1 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_historico_pretaparda.parquet` | 116 | sim (1.0e-12) | — | 93 / 0 | 99 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_historico_todas.parquet` | 116 | sim (1.1e-15) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_pretaparda.parquet` | 2 | sim (2.7e-15) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_genero_todas.parquet` | 2 | sim (4.1e-16) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_geracao_escolaridade_pretaparda.parquet` | 33 | sim (1.1e-13) | — | 25 / 0 | 28 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_geracao_escolaridade_todas.parquet` | 34 | sim (2.8e-15) | — | 7 / 0 | 8 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_geracao_historico_pretaparda.parquet` | 232 | sim (3.5e-13) | — | 174 / 0 | 189 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_geracao_pretaparda.parquet` | 5 | sim (8.5e-15) | — | 3 / 0 | 3 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_geracao_todas.parquet` | 5 | sim (6.4e-16) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_por_geracao.parquet` | 232 | sim (3.3e-15) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_preta_parda.parquet` | 58 | sim (1.0e-12) | 31,5 (26,1–48,4) | 44 / 0 | 44 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_racial.parquet` | 58 | sim (1.3e-15) | 57,1 (45,2–82,4) | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_regional.parquet` | 290 | sim (1.5e-15) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_regional_indigena.parquet` | 290 | sim (1.5e-14) | — | 41 / 0 | 42 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_regional_pretaparda.parquet` | 1566 | sim (4.8e-12) | — | 1185 / 0 | 1348 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `hiato_setor_publico_privado.parquet` | 116 | sim (1.4e-15) | — | 0 / 0 | 0 / 0 | `p_valor_bh`, `significativo_fdr`, `significativo_nominal` |
| `transicao_desemprego_emprego.parquet` | 10 | sim (2.0e-16) | 34,9 (30,1–37,9) | — | — | — |
| `transicao_informal_formal.parquet` | 10 | sim (1.7e-16) | 33,8 (24,9–35,8) | — | — | — |

Outros 47 parquets sem colunas de inferência: estimativas idênticas e nenhuma coluna nova.

Notas: "EP novo/antigo" só aparece quando a tabela guarda o IC ou o `se` (as demais guardam só o p-valor). As tabelas com `—` nas flags não tinham coluna `significativo`: a mudança de flags delas está no resumo acima. A razão de EP nas curvas do event-study (30×) usa o EP por célula; a soma entre células continua ignorando covariâncias (limitação documentada, B4b).
