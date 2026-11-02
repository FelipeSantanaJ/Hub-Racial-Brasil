# Verificações — Fase 0 (Rumo ao 8)

Data: 01/11/2026. Branch `rumo8/fase0`. A Fase 0 não produz número publicável novo; estas são checagens de estado de partida, cada uma por dois caminhos distintos. Scripts de checagem ficaram fora do repositório (scratch da sessão).

| # | O que | Caminho 1 | Caminho 2 | Valor 1 | Valor 2 | Tolerância | Resultado |
|---|---|---|---|---|---|---|---|
| V0.1 | Soma de V1028, 2012T1 | DuckDB sobre `pnadc_extraido_v2` (parquet) | leitura posicional do .txt do zip do FTP (layout SAS) | 196.656.839,0000025 | 196.656.839,0000264 | rel. 1e-9 | **passou** (rel. 5,0e-15) |
| V0.2 | Soma de V1028, 2026T2 | idem | idem | 213.515.590,0000060 | 213.515.590,0000150 | rel. 1e-9 | **passou** (rel. 4,2e-14) |
| V0.3 | Nº de linhas, 2012T1 / 2026T2 | COUNT(*) no parquet | linhas do .txt | 566.873 / 521.730 | 566.873 / 521.730 | exato | **passou** |
| V0.4 | Replicados calibrados ao mesmo total (2012T1) | soma V1028001 | soma V1028 | 196.656.839,0000098 | 196.656.839,0000264 | rel. 1e-9 | **passou** |
| V0.5 | Replicados calibrados ao mesmo total (2026T2) | soma V1028001 / V1028200 | soma V1028 | 213.515.590,0174 / 213.515.590,0000056 | 213.515.590,0000150 | rel. 1e-9 | **passou** (maior rel. 8,1e-11) |
| V0.6 | Mesma vintage em v1 e v2, 58 trimestres | soma V1028 no extrato v1 | soma V1028 no extrato v2 | — | — | rel. 1e-9 | **passou** (máx. 2,2e-16) |
| V0.7 | Pareceres copiados sem alteração | SHA-256 da origem (`~\Downloads`) | SHA-256 da cópia | A 52feef9c2f0c…; B d4828a4d3ef2… | idem | exato | **passou** |
| V0.8 | Hash dos arquivos de decisão | SHA-256 bruto | SHA-256 com quebras de linha normalizadas para LF | ver ESTADO.md | idem | exato | **passou** (iguais) |
| V0.9 | Nenhum número publicado mudou | `git diff --stat baseline-20261020 -- data/processed` | SHA-256 de cada parquet registrado em `baseline_rumo8.md` (Anexo 2) | vazio | — | exato | **passou** |

Não verificado de forma independente nesta fase:
- Presença dos replicados nos 56 trimestres que não foram baixados (inferida pelo layout único e pela republicação de 15/08/2025).
- Correspondência entre o V1028 local e o FTP nesses 56 trimestres (inferida pela ordem das datas: extração após o último Last-Modified).
- Contagem de ocorrências de `pendencias_textuais.md` (varredura léxica única; não houve segundo varredor).
