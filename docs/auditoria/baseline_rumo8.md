# Baseline do Rumo ao 8 (Fase 0)

Data: 01/11/2026. Branch `rumo8/fase0`. Tag `baseline-20261020` = 862de5f (HEAD de `main` em 20/10/2026, confirmado). Nada em `data/processed/` foi alterado nesta fase (`git diff baseline-20261020 -- data/processed` vazio).

## 0.1 Git

- HEAD de partida: `862de5f3b0fa6d205612f62537e201e42548aa13` = esperado. [VERIFICADO]
- Árvore: limpa, exceto a pasta `docs/rumo8/` (nova, não versionada), commitada em `01c2cdf` junto com os pareceres.
- Tag `baseline-20261020` criada (local; não enviada ao GitHub).

## 0.2 Pareceres

`docs/auditoria/pareceres_20-10-2026/PARECER_PASSADA_A.md` (16.447 B) e `PARECER_PASSADA_B.md` (23.214 B), copiados de `~\Downloads` em 01/11/2026; SHA-256 da cópia = SHA-256 da origem. [VERIFICADO]

## 0.3 Suíte de testes

- Com o Python global (3.12.10): **falha na coleta** (`ModuleNotFoundError: tqdm` em `tests/test_extrator_fonte.py`). O global não é o ambiente do projeto.
- Com `.venv` do repositório: **175 passed, 10 warnings em 90,1 s**. Warnings: `RuntimeWarning: invalid value encountered in scalar divide` em `src/processing/bloco_t.py:216` (`indice_representacao = share / pop_share[g]` com `pop_share` 0). [VERIFICADO] A warning é registro, não correção (não muda número nesta fase).

## 0.4 Ambiente

| Item | Resultado |
|---|---|
| Python (.venv) | 3.12.10; duckdb 1.5.5, pandas 3.0.5, pyarrow 25.0.1, numpy 2.5.2, scipy 1.18.1, statsmodels 0.15.0, tqdm 4.70.0, pytest 9.1.1 — **igual a `requirements.lock`** |
| polars | ausente (não é dependência do projeto) |
| R | **não instalado** (sem `Rscript` no PATH nem em Program Files) |
| Disco livre (C:) | 164,8 GB |
| ftp.ibge.gov.br | OK (HTTPS 200; porta 21 aberta) |
| download.inep.gov.br | HTTPS responde 403 ao HEAD (servidor existe; download por GET a confirmar na Fase 5) |
| dados.inep.gov.br | **DNS não resolve** (nome provavelmente não existe; o INEP publica em download.inep.gov.br) [INFERIDO] |
| ftp.datasus.gov.br | HTTPS: timeout; **FTP porta 21: aberta** (DATASUS distribui por FTP) |

**Decisão R/Python (proposta, a confirmar pelo Felipe no gate): validar o EP só em Python.**
Justificativa: (i) R não está instalado e o Felipe não trabalha em R, então código R não seria revisável por quem aprova; (ii) a regra 3 do prompt-mestre pede "caminho distinto", não "outro motor" obrigatoriamente: os pesos replicados do IBGE (V1028001–200, confirmados em 0.5) dão uma variância por fórmula independente da linearização de Taylor Estrato/UPA usada hoje, e isso é exatamente o teste de aceite 1.1 (razão EP-replicados/EP-Taylor); (iii) uma segunda implementação de Taylor pode ser escrita do zero em numpy, sem reaproveitar `variancia.py`. Custo: perde-se a checagem contra `survey`, que é a referência da área [INFERIDO]. Se o Felipe preferir R, a instalação (R + survey, srvyr, did, HonestDiD, fixest) precisa da autorização dele.

## 0.5 Pesos replicados

- Nos extratos locais (`pnadc_extraido` v1 e `pnadc_extraido_v2`), **nenhum** dos 58 trimestres (2012T1–2026T2) tem V1028001..V1028200: o extrator guarda só V1028 e apaga o zip depois (decisão de 12/10/2026 no código: "não extrair por enquanto"). O extrator já tem a opção `--pesos-replicados`, que grava um dataset separado em `pnadc_extraido_v2/pesos_replicados/`. [VERIFICADO]
- No dado do IBGE os replicados **existem**: o layout oficial (`Dicionario_e_input_20221031`) tem V1028001 (@479) a V1028200 (@3464), e os zips atuais de **2012T1 e 2026T2** foram baixados e lidos inteiros: todas as linhas com 3.478 posições, 0 linhas com replicado vazio, e soma de V1028001 e de V1028200 = soma de V1028 (calibrados ao mesmo total). [VERIFICADO para 2012 e 2026]
- Demais 56 trimestres: [INFERIDO] que também têm, pelo layout único e pela republicação conjunta de 15/08/2025. Confirmar na Fase 1 ao extrair (a extração com `--pesos-replicados` lê cada arquivo).
- Resposta à pergunta da fase: os replicados existem no microdado bruto e cobrem pelo menos 2 trimestres (verificados) e provavelmente os 58; localmente, 0 trimestres.

## 0.6 Vintage dos pesos

- Hoje, 49 dos 58 zips no FTP têm sufixo `_20250815` ou Last-Modified de 15/08/2025 (os 53 trimestres de 2012T1–2025T1, menos as 4 republicações abaixo): é a republicação da série inteira em 15/08/2025, compatível com a reponderação pós-Censo 2022 [INFERIDO; a nota técnica do IBGE sobre a reponderação está a confirmar]. Republicações pontuais depois: 2015T4 (09/12/2025) e 2019T2, 2020T2, 2024T2 (23/03/2026). 2025T2–2026T2 são publicações originais posteriores (até 14/08/2026).
- Extração local: v1 em 04/09/2026 e v2 em 12–13/10/2026, as duas **depois** do último Last-Modified (14/08/2026). Logo, o V1028 local vem dos zips publicados hoje. [VERIFICADO em 2012T1 e 2026T2: soma de V1028 do FTP = local, diferença relativa ~5e-15; INFERIDO nos demais pela ordem das datas]
- v1 e v2 têm a **mesma** soma de V1028 em todos os 58 trimestres (|razão − 1| ≤ 2,2e-16): não houve troca de pesos entre as extrações. [VERIFICADO]
- A população estimada cresce de 196,657 mi (2012T1) a 213,516 mi (2026T2), com variação trimestral entre 0,09% e 0,21% e queda suave e monótona da taxa; **nenhum degrau em 2020T1 nem em 2022T1** (2022T1: +0,12%). [VERIFICADO]
- Conclusão: a série usa **uma única vintage** de calibração (a de 15/08/2025, com as quatro republicações pontuais acima, que não alteram a trajetória da soma). A HIPÓTESE do revisor (quebra de pesos perto de 2022) **não se confirma no total de população**. Ressalva: a soma total não detecta mudança na distribuição dos pesos ENTRE grupos (cor/raça, idade, UF); isso é tarefa da Fase 2 (rival "vintage de pesos" da queda de 2021). Os `_fonte.json` não existem em nenhuma partição (extrações anteriores a 13/10/2026 não gravavam), por isso a vintage local é reconstruída, não lida.

## 0.7 Proveniência (resumo; tabela completa no Anexo 2)

- 183 parquets em `data/processed/` (fora `_legado/`), todos versionados e com `_meta.json`.
- **77 com commit "-modificado"** (gerados com árvore suja), em 13 commits geradores diferentes. Entre eles estão os parquets da manchete e das conclusões-chave: `a2_metricas_hiato`, `a2_metricas_hiato_preta_parda`, `b1_degraus_hiato`, `b1_tendencia_hiato`, `g1_sensibilidade_rr`, `i1_censo_pnadc`.
- 106 limpos; 6 sem população documentada no meta; `deflator_ibge.parquet` tem commit "anterior…" (gerado antes do esquema de meta).
- Resposta à pergunta da fase: 77 de 183 têm proveniência suja (Anexo 2). Regenerar é tarefa da Fase 1 (problema 8 do anexo A).

## Anexo 1 — Vintage do V1028 por trimestre (tarefa 0.6)

pop = soma de V1028 no extrato v2 (milhões); Δ = variação % sobre o trimestre anterior; v2/v1 = razão das somas − 1.

| Trimestre | Zip no FTP hoje | Last-Modified | Extraído v1 | Extraído v2 | pop (mi) | Δ % | v2/v1 − 1 |
|---|---|---|---|---|---|---|---|
| 2012T1 | PNADC_012012_20250815.zip | Fri, 15 Aug 2025 13:20:34 GMT | 2026-09-04 | 2026-10-12 | 196,657 |  | 0.0e+00 |
| 2012T2 | PNADC_022012_20250815.zip | Fri, 15 Aug 2025 13:20:34 GMT | 2026-09-04 | 2026-10-12 | 197,062 | 0,21 | 0.0e+00 |
| 2012T3 | PNADC_032012_20250815.zip | Fri, 15 Aug 2025 13:20:41 GMT | 2026-09-04 | 2026-10-12 | 197,471 | 0,21 | 0.0e+00 |
| 2012T4 | PNADC_042012_20250815.zip | Fri, 15 Aug 2025 13:20:41 GMT | 2026-09-04 | 2026-10-12 | 197,875 | 0,20 | 0.0e+00 |
| 2013T1 | PNADC_012013_20250815.zip | Fri, 15 Aug 2025 13:20:50 GMT | 2026-09-04 | 2026-10-12 | 198,276 | 0,20 | 2.2e-16 |
| 2013T2 | PNADC_022013_20250815.zip | Fri, 15 Aug 2025 13:20:50 GMT | 2026-09-04 | 2026-10-13 | 198,658 | 0,19 | -1.1e-16 |
| 2013T3 | PNADC_032013_20250815.zip | Fri, 15 Aug 2025 13:20:58 GMT | 2026-09-04 | 2026-10-13 | 199,05 | 0,20 | 0.0e+00 |
| 2013T4 | PNADC_042013_20250815.zip | Fri, 15 Aug 2025 13:20:58 GMT | 2026-09-04 | 2026-10-13 | 199,436 | 0,19 | 0.0e+00 |
| 2014T1 | PNADC_012014_20250815.zip | Fri, 15 Aug 2025 13:21:06 GMT | 2026-09-04 | 2026-10-13 | 199,819 | 0,19 | 0.0e+00 |
| 2014T2 | PNADC_022014_20250815.zip | Fri, 15 Aug 2025 13:21:06 GMT | 2026-09-04 | 2026-10-13 | 200,185 | 0,18 | 0.0e+00 |
| 2014T3 | PNADC_032014_20250815.zip | Fri, 15 Aug 2025 13:21:15 GMT | 2026-09-04 | 2026-10-13 | 200,558 | 0,19 | 0.0e+00 |
| 2014T4 | PNADC_042014_20250815.zip | Fri, 15 Aug 2025 13:21:15 GMT | 2026-09-04 | 2026-10-13 | 200,928 | 0,18 | 0.0e+00 |
| 2015T1 | PNADC_012015_20250815.zip | Fri, 15 Aug 2025 13:21:23 GMT | 2026-09-04 | 2026-10-13 | 201,293 | 0,18 | 2.2e-16 |
| 2015T2 | PNADC_022015_20250815.zip | Fri, 15 Aug 2025 13:21:23 GMT | 2026-09-04 | 2026-10-13 | 201,642 | 0,17 | 0.0e+00 |
| 2015T3 | PNADC_032015_20250815.zip | Fri, 15 Aug 2025 13:21:32 GMT | 2026-09-04 | 2026-10-13 | 201,998 | 0,18 | 0.0e+00 |
| 2015T4 | PNADC_042015_20251210.zip | Tue, 09 Dec 2025 14:15:35 GMT | 2026-09-04 | 2026-10-13 | 202,35 | 0,17 | 0.0e+00 |
| 2016T1 | PNADC_012016_20250815.zip | Fri, 15 Aug 2025 13:21:41 GMT | 2026-09-04 | 2026-10-13 | 202,698 | 0,17 | 0.0e+00 |
| 2016T2 | PNADC_022016_20250815.zip | Fri, 15 Aug 2025 13:21:41 GMT | 2026-09-04 | 2026-10-13 | 203,034 | 0,17 | 0.0e+00 |
| 2016T3 | PNADC_032016_20250815.zip | Fri, 15 Aug 2025 13:21:49 GMT | 2026-09-04 | 2026-10-13 | 203,374 | 0,17 | 0.0e+00 |
| 2016T4 | PNADC_042016_20250815.zip | Fri, 15 Aug 2025 13:21:49 GMT | 2026-09-04 | 2026-10-13 | 203,709 | 0,16 | 0.0e+00 |
| 2017T1 | PNADC_012017_20250815.zip | Fri, 15 Aug 2025 13:21:58 GMT | 2026-09-04 | 2026-10-13 | 204,041 | 0,16 | 0.0e+00 |
| 2017T2 | PNADC_022017_20250815.zip | Fri, 15 Aug 2025 13:21:58 GMT | 2026-09-04 | 2026-10-13 | 204,357 | 0,15 | 0.0e+00 |
| 2017T3 | PNADC_032017_20250815.zip | Fri, 15 Aug 2025 13:22:07 GMT | 2026-09-04 | 2026-10-13 | 204,68 | 0,16 | 0.0e+00 |
| 2017T4 | PNADC_042017_20250815.zip | Fri, 15 Aug 2025 13:22:07 GMT | 2026-09-04 | 2026-10-13 | 204,999 | 0,16 | 0.0e+00 |
| 2018T1 | PNADC_012018_20250815.zip | Fri, 15 Aug 2025 13:22:16 GMT | 2026-09-04 | 2026-10-13 | 205,314 | 0,15 | 0.0e+00 |
| 2018T2 | PNADC_022018_20250815.zip | Fri, 15 Aug 2025 13:22:16 GMT | 2026-09-04 | 2026-10-13 | 205,615 | 0,15 | 0.0e+00 |
| 2018T3 | PNADC_032018_20250815.zip | Fri, 15 Aug 2025 13:22:24 GMT | 2026-09-04 | 2026-10-13 | 205,921 | 0,15 | 0.0e+00 |
| 2018T4 | PNADC_042018_20250815.zip | Fri, 15 Aug 2025 13:22:24 GMT | 2026-09-04 | 2026-10-13 | 206,224 | 0,15 | 0.0e+00 |
| 2019T1 | PNADC_012019_20250815.zip | Fri, 15 Aug 2025 13:22:33 GMT | 2026-09-04 | 2026-10-13 | 206,523 | 0,14 | 2.2e-16 |
| 2019T2 | PNADC_022019_20260324.zip | Mon, 23 Mar 2026 12:33:36 GMT | 2026-09-04 | 2026-10-13 | 206,808 | 0,14 | 0.0e+00 |
| 2019T3 | PNADC_032019_20250815.zip | Fri, 15 Aug 2025 13:22:41 GMT | 2026-09-04 | 2026-10-13 | 207,099 | 0,14 | 0.0e+00 |
| 2019T4 | PNADC_042019_20250815.zip | Fri, 15 Aug 2025 13:22:41 GMT | 2026-09-04 | 2026-10-13 | 207,387 | 0,14 | 0.0e+00 |
| 2020T1 | PNADC_012020_20250815.zip | Fri, 15 Aug 2025 13:22:49 GMT | 2026-09-04 | 2026-10-13 | 207,67 | 0,14 | 0.0e+00 |
| 2020T2 | PNADC_022020_20260324.zip | Mon, 23 Mar 2026 12:28:02 GMT | 2026-09-04 | 2026-10-13 | 207,943 | 0,13 | 0.0e+00 |
| 2020T3 | PNADC_032020_20250815.zip | Fri, 15 Aug 2025 13:22:53 GMT | 2026-09-04 | 2026-10-13 | 208,218 | 0,13 | 0.0e+00 |
| 2020T4 | PNADC_042020_20250815.zip | Fri, 15 Aug 2025 13:22:54 GMT | 2026-09-04 | 2026-10-13 | 208,49 | 0,13 | 0.0e+00 |
| 2021T1 | PNADC_012021_20250815.zip | Fri, 15 Aug 2025 13:22:59 GMT | 2026-09-04 | 2026-10-13 | 208,758 | 0,13 | 0.0e+00 |
| 2021T2 | PNADC_022021_20250815.zip | Fri, 15 Aug 2025 13:23:00 GMT | 2026-09-04 | 2026-10-13 | 209,013 | 0,12 | 0.0e+00 |
| 2021T3 | PNADC_032021_20250815.zip | Fri, 15 Aug 2025 13:23:06 GMT | 2026-09-04 | 2026-10-13 | 209,274 | 0,12 | 0.0e+00 |
| 2021T4 | PNADC_042021_20250815.zip | Fri, 15 Aug 2025 13:23:07 GMT | 2026-09-04 | 2026-10-13 | 209,53 | 0,12 | -1.1e-16 |
| 2022T1 | PNADC_012022_20250815.zip | Fri, 15 Aug 2025 13:23:13 GMT | 2026-09-04 | 2026-10-13 | 209,783 | 0,12 | 0.0e+00 |
| 2022T2 | PNADC_022022_20250815.zip | Fri, 15 Aug 2025 13:23:14 GMT | 2026-09-04 | 2026-10-13 | 210,024 | 0,11 | 0.0e+00 |
| 2022T3 | PNADC_032022_20250815.zip | Fri, 15 Aug 2025 13:23:23 GMT | 2026-09-04 | 2026-10-13 | 210,27 | 0,12 | 0.0e+00 |
| 2022T4 | PNADC_042022_20250815.zip | Fri, 15 Aug 2025 13:23:23 GMT | 2026-09-04 | 2026-10-13 | 210,513 | 0,12 | 0.0e+00 |
| 2023T1 | PNADC_012023_20250815.zip | Fri, 15 Aug 2025 13:23:33 GMT | 2026-09-04 | 2026-10-13 | 210,752 | 0,11 | 0.0e+00 |
| 2023T2 | PNADC_022023_20250815.zip | Fri, 15 Aug 2025 13:23:33 GMT | 2026-09-04 | 2026-10-13 | 210,98 | 0,11 | 0.0e+00 |
| 2023T3 | PNADC_032023_20250815.zip | Fri, 15 Aug 2025 13:23:41 GMT | 2026-09-04 | 2026-10-13 | 211,212 | 0,11 | 0.0e+00 |
| 2023T4 | PNADC_042023_20250815.zip | Fri, 15 Aug 2025 13:23:41 GMT | 2026-09-04 | 2026-10-13 | 211,44 | 0,11 | 0.0e+00 |
| 2024T1 | PNADC_012024_20250815.zip | Fri, 15 Aug 2025 13:23:49 GMT | 2026-09-04 | 2026-10-13 | 211,665 | 0,11 | 0.0e+00 |
| 2024T2 | PNADC_022024_20260324.zip | Mon, 23 Mar 2026 12:24:29 GMT | 2026-09-04 | 2026-10-13 | 211,882 | 0,10 | 0.0e+00 |
| 2024T3 | PNADC_032024_20250815.zip | Fri, 15 Aug 2025 13:23:58 GMT | 2026-09-04 | 2026-10-13 | 212,1 | 0,10 | 0.0e+00 |
| 2024T4 | PNADC_042024_20250815.zip | Fri, 15 Aug 2025 13:23:58 GMT | 2026-09-04 | 2026-10-13 | 212,314 | 0,10 | 0.0e+00 |
| 2025T1 | PNADC_012025.zip | Fri, 15 Aug 2025 13:24:06 GMT | 2026-09-04 | 2026-10-13 | 212,525 | 0,10 | 0.0e+00 |
| 2025T2 | PNADC_022025.zip | Mon, 25 Aug 2025 12:00:07 GMT | 2026-09-04 | 2026-10-13 | 212,726 | 0,09 | 0.0e+00 |
| 2025T3 | PNADC_032025.zip | Mon, 17 Nov 2025 12:00:14 GMT | 2026-09-04 | 2026-10-13 | 212,93 | 0,10 | 0.0e+00 |
| 2025T4 | PNADC_042025.zip | Thu, 26 Feb 2026 12:00:14 GMT | 2026-09-04 | 2026-10-13 | 213,131 | 0,09 | 0.0e+00 |
| 2026T1 | PNADC_012026.zip | Fri, 24 Apr 2026 11:33:57 GMT | 2026-09-04 | 2026-10-13 | 213,328 | 0,09 | 0.0e+00 |
| 2026T2 | PNADC_022026.zip | Fri, 14 Aug 2026 12:00:10 GMT | 2026-09-04 | 2026-10-13 | 213,516 | 0,09 | 0.0e+00 |

## Anexo 2 — Proveniência dos parquets de data/processed (tarefa 0.7)

Todos os 183 estão versionados no git e têm `_meta.json`. "commit" = commit gravado no meta (7 caracteres). SHA-256 = hash do arquivo no baseline (para o diff de parquets nas fases seguintes).

### Resumo por commit gerador

| Commit | -modificado | Parquets |
|---|---|---|
| 18b352e | não | 8 |
| 22180a1 | SIM | 13 |
| 2219b86 | SIM | 7 |
| 4af95aa | SIM | 7 |
| 6544305 | SIM | 4 |
| 7bae2e2 | SIM | 1 |
| 822740c | SIM | 1 |
| 8a4429c | não | 10 |
| a651cd0 | SIM | 7 |
| ae25575 | SIM | 2 |
| anterio | não | 1 |
| be8c34d | SIM | 1 |
| bf6ef01 | SIM | 8 |
| c1202a1 | não | 79 |
| c1202a1 | SIM | 17 |
| cc24b07 | não | 3 |
| e22733d | SIM | 2 |
| e27278b | não | 3 |
| ea4e10a | não | 2 |
| ea4e10a | SIM | 3 |
| f7eedc9 | SIM | 4 |

### Parquets sem população documentada no meta

- `data/processed/a2_metricas_hiato.parquet`
- `data/processed/a3_hiato_quantis.parquet`
- `data/processed/a4_desigualdade_decomposicao.parquet`
- `data/processed/s03_perfil_fora_populacao_referencia.parquet`
- `data/processed/s14_margens_intensiva_extensiva.parquet`
- `data/processed/s15_selecao_no_tempo.parquet`

### Tabela completa

| Parquet | Commit | -modificado | Gerado em | Insumo | Método de EP | SHA-256 |
|---|---|---|---|---|---|---|
| a2_metricas_hiato.parquet | bf6ef01 | **SIM** | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `1791b715ed7089a7…` |
| a2_metricas_hiato_preta_parda.parquet | 2219b86 | **SIM** | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `1ebccf3b17605ac9…` |
| a3_hiato_quantis.parquet | bf6ef01 | **SIM** | 2026-10-13 | trimestral_v2 | bootstrap_rao_wu_estrato_upa_200 | `0621a9e8b932b06a…` |
| a4_desigualdade_decomposicao.parquet | bf6ef01 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `60b4e5716dcf2d60…` |
| a5_representacao_decimos.parquet | bf6ef01 | **SIM** | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `37accc912c69c43d…` |
| a6_dominancia.parquet | bf6ef01 | **SIM** | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `32a3c6af41dd3694…` |
| alfabetizacao.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `93c6030070ec4ac3…` |
| b1_degraus_hiato.parquet | 22180a1 | **SIM** | 2026-10-13 | derivado | ewc_lazarus_lewis_stock_watson; sensibilidades newey_west e gls_ar1 | `15d3d9266bf5953e…` |
| b1_tendencia_hiato.parquet | 22180a1 | **SIM** | 2026-10-13 | derivado | ewc_lazarus_lewis_stock_watson; sensibilidades newey_west e gls_ar1 | `6c3a489d7ac1ae9b…` |
| b2_composicao_racial_coortes.parquet | 8a4429c | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `8079d687bbfa5a23…` |
| b2_decomposicao_tempo.parquet | 8a4429c | não | 2026-10-13 | trimestral_v2 | bootstrap_rao_wu_estrato_upa_100 | `f91aa21b09cf273b…` |
| b3_hiato_quantis_serie.parquet | 22180a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `e11bbb60352d151e…` |
| b3_quantis_janelas.parquet | 22180a1 | **SIM** | 2026-10-13 | trimestral_v2 | bootstrap_rao_wu_estrato_upa_100 | `cec4e88ad0e7660b…` |
| b3_tendencia_quantis.parquet | 22180a1 | **SIM** | 2026-10-13 | trimestral_v2 | ewc_lazarus_lewis_stock_watson; sensibilidades newey_west e gls_ar1 | `929a31687c3bccae…` |
| b4_apc.parquet | 22180a1 | **SIM** | 2026-10-13 | trimestral_v2 | wls_variancias_conhecidas | `5df05fa7f2c258db…` |
| b4_celulas_idade_ano.parquet | 22180a1 | **SIM** | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `6556debf3bba2fd7…` |
| b4_mesma_idade_coortes.parquet | 22180a1 | **SIM** | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `f85fe3a7434089d1…` |
| b5_ciclo_tendencia.parquet | 22180a1 | **SIM** | 2026-10-13 | trimestral_v2 | ewc_lazarus_lewis_stock_watson; sensibilidades newey_west e gls_ar1 | `b8dc7251b152db95…` |
| b5_taxa_desocupacao.parquet | 22180a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `02c47da0de51bcb1…` |
| b6_projecao_condicional.parquet | 22180a1 | **SIM** | 2026-10-13 | derivado | ewc_lazarus_lewis_stock_watson; sensibilidades newey_west e gls_ar1 | `54199f0f551f62ac…` |
| c123_racaxsexo_celulas.parquet | 8a4429c | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `aac2216cfa7fdc3c…` |
| c123_racaxsexo_domiciliar_anual.parquet | 8a4429c | não | 2026-10-13 | anual_v2 | linearizacao_taylor_estrato_upa | `5a17f3bd2ccdb04a…` |
| c1_quantis_celulas.parquet | 8a4429c | não | 2026-10-13 | trimestral_v2 | bootstrap_rao_wu_estrato_upa_200 | `5a5fbdb8119f124a…` |
| c1_theil_celulas.parquet | 8a4429c | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `6b1478c952e41c34…` |
| c2_interacao_regressao.parquet | 8a4429c | não | 2026-10-13 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `e583dfd392fe40e1…` |
| c2_interacao_tendencia.parquet | 8a4429c | não | 2026-10-13 | trimestral_v2 | ewc_lazarus_lewis_stock_watson; sensibilidades newey_west e gls_ar1 | `803035dffc70747a…` |
| c4_penalidade_maternidade.parquet | be8c34d | **SIM** | 2026-10-13 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `4f2b30f55e2ebfc1…` |
| c5_tendencia.parquet | 8a4429c | não | 2026-10-13 | trimestral_v2 | ewc_lazarus_lewis_stock_watson; sensibilidades newey_west e gls_ar1 | `43e5fda9de05775f…` |
| c5_trabalho_domestico.parquet | 8a4429c | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `5d00baf6836b2802…` |
| c6_conjugal_chefia.parquet | ae25575 | **SIM** | 2026-10-13 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `06e17b40411b60be…` |
| c6_hiato_condicional.parquet | ae25575 | **SIM** | 2026-10-13 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `4ad8e5608cd05bc3…` |
| checagem_robustez_hiato_racial.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `e81b82843cbd914a…` |
| composicao_populacao_referencia.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `9047335736b693d0…` |
| composicao_racial_declarada.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `8338b315df9853dc…` |
| d1_aninhada.parquet | a651cd0 | **SIM** | 2026-10-14 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `300e171341382aee…` |
| d1_contribuicao_blocos.parquet | a651cd0 | **SIM** | 2026-10-14 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `bffd4f9e53623b28…` |
| d1_extensiva_p1.parquet | a651cd0 | **SIM** | 2026-10-14 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `9fe0d440ca549d3e…` |
| d1_mudanca_janelas.parquet | a651cd0 | **SIM** | 2026-10-14 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `391dbc6fdb11bdc7…` |
| d1_ob_reimers.parquet | a651cd0 | **SIM** | 2026-10-14 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `4ef5f5d69e14fc97…` |
| d1_rif_ob.parquet | a651cd0 | **SIM** | 2026-10-14 | trimestral_v2 | bootstrap_rao_wu_estrato_upa_100 (banda × 1) | `d281fbe862c2a714…` |
| d1_sensibilidade_omitidas.parquet | a651cd0 | **SIM** | 2026-10-14 | trimestral_v2 | sem_inferencia | `79e5a78d544a2341…` |
| d2_hiato_por_nivel.parquet | 18b352e | não | 2026-10-14 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `a9d70a836772ae22…` |
| d2_quantis_nivel.parquet | 18b352e | não | 2026-10-14 | trimestral_v2 | bootstrap_rao_wu_estrato_upa_200 | `14f930c750a6da4f…` |
| d2_sobrequalificacao.parquet | 18b352e | não | 2026-10-14 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `c560a3d99ed62371…` |
| d3_hiato_dentro_ocupacao.parquet | 18b352e | não | 2026-10-14 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `8c53d139a2652440…` |
| d3_segregacao.parquet | 18b352e | não | 2026-10-14 | trimestral_v2 | bootstrap_rao_wu_estrato_upa_100 (só janelas) | `66d49e4acc29071d…` |
| d44_segregacao_residencial.parquet | ea4e10a | não | 2026-10-20 | ibge_censo_2022_setores | sem_inferencia | `23ad1defd41765ec…` |
| d4_territorio.parquet | 18b352e | não | 2026-10-14 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `ff46ff45df9f5bba…` |
| d5_posicao_ocupacao.parquet | 18b352e | não | 2026-10-14 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `feac056a9e5d0e9f…` |
| d6_hiato_idade.parquet | 18b352e | não | 2026-10-14 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `11901d2438d08dd1…` |
| decomposicao_hiato_ocupacional.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `c31e9d3f70d6e617…` |
| decomposicao_oaxaca_blinder.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | wls_statsmodels_cluster_upa | `019d30312d48651c…` |
| decomposicao_oaxaca_blinder_indigena.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | wls_statsmodels_cluster_upa | `44c749804fc2acde…` |
| decomposicao_oaxaca_blinder_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | wls_statsmodels_cluster_upa | `1e0b6fd7166c9d53…` |
| decomposicao_raca_genero.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `d1898f24592a792e…` |
| deflator_ibge.parquet | anterio | não | 2026-09-04 | ibge_deflator | sem_inferencia | `191f03f800947f31…` |
| desalento_subutilizacao.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `b49bbf67628c75b0…` |
| desocupacao_por_escolaridade.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `13c348e05fa984f5…` |
| did_cotas_servico_publico.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | wls_statsmodels_cluster_upa | `065d86fc18b56c8c…` |
| did_cotas_servico_publico_curvas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `9e9337cc450849f4…` |
| did_cotas_servico_publico_heterogeneidade.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | wls_statsmodels_cluster_upa | `b1185c6d0d9efda9…` |
| did_cotas_servico_publico_heterogeneidade_curvas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `acb6a5d7f0017c67…` |
| did_cotas_universitarias.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | wls_statsmodels_iid_celulas_coorte | `2d9e11580eb21f0a…` |
| did_cotas_universitarias_heterogeneidade.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | wls_statsmodels_iid_celulas_coorte | `1e7e9c63d28c95d5…` |
| dupla_desvantagem.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `73625f1edf19c2e2…` |
| e1_escolarizacao_idade.parquet | 4af95aa | **SIM** | 2026-10-20 | trimestral_v2 | linearizacao_taylor_estrato_upa | `7499b5f69aa9472c…` |
| e3_saeb_proficiencia.parquet | f7eedc9 | **SIM** | 2026-10-20 | inep_saeb_2023 | wls_influencia_linearizacao_estrato_escola | `240fc77f55f40c87…` |
| e4_rede_escola.parquet | 4af95aa | **SIM** | 2026-10-20 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `0bc410d680cb30d2…` |
| e6_superior_composicao.parquet | f7eedc9 | **SIM** | 2026-10-20 | inep_censo_superior | sem_inferencia | `6f543ec7e73c1d8b…` |
| e7_escolas_segregacao.parquet | f7eedc9 | **SIM** | 2026-10-20 | inep_censo_escolar_2024 | sem_inferencia | `b4f35629f8700fe9…` |
| escolaridade.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `34d2d4389770d21c…` |
| extremos_composicao_racial.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `92f241db1d570b0c…` |
| extremos_distribuicao_racial.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `88acd78611da75e2…` |
| extremos_renda_racial.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `147ccfabd2c1bdfa…` |
| faixas_salario_minimo.parquet | bf6ef01 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `e9ca2ef95d499280…` |
| funcao_quantil_racial.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `4c3e2224fbdd57ae…` |
| g1_cotas_federais.parquet | cc24b07 | não | 2026-10-20 | inep_censo_superior_2009_2023 | cr1_instituicao_e_bootstrap_instituicao | `ccbded272f658ac1…` |
| g1_sensibilidade_rr.parquet | 822740c | **SIM** | 2026-10-20 | inep_censo_superior_2009_2023 | rambachan_roth_magnitudes_relativas_conservador | `025d5c03469ee534…` |
| g1_series_grupos.parquet | cc24b07 | não | 2026-10-20 | inep_censo_superior_2009_2023 | sem_inferencia | `5c7d4b0842fd7ffe…` |
| g6_emd.parquet | cc24b07 | não | 2026-10-20 | g_misto | simulacao_ar1 | `8e50a43b41ce0670…` |
| gini_por_raca.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `50149d0acc4af1a1…` |
| h1_corresidencia.parquet | 4af95aa | **SIM** | 2026-10-20 | trimestral_v2 | linearizacao_taylor_estrato_upa | `3cda1d3d95790eb4…` |
| h1_transmissao_educacional.parquet | 4af95aa | **SIM** | 2026-10-20 | trimestral_v2 | linearizacao_taylor_estrato_upa | `e58df4794502ff0c…` |
| h2_mobilidade_quintis.parquet | 4af95aa | **SIM** | 2026-10-20 | trimestral_v2 | linearizacao_taylor_estrato_upa | `ef08ccfb50aae4c5…` |
| h2_origem_renda.parquet | 4af95aa | **SIM** | 2026-10-20 | trimestral_v2 | wls_influencia_linearizacao_estrato_upa | `3a9ac258d99a3b16…` |
| h32_pof_bens.parquet | f7eedc9 | **SIM** | 2026-10-20 | ibge_pof_2017_18 | wls_influencia_linearizacao_estrato_upa | `8bdc17843c47f91c…` |
| h34_riqueza_imobiliaria.parquet | ea4e10a | não | 2026-10-20 | ibge_pof_2017_18 | wls_influencia_linearizacao_estrato_upa | `431ab1d55a50b172…` |
| h3_patrimonio_proxy.parquet | 4af95aa | **SIM** | 2026-10-20 | anual_v2 | wls_influencia_linearizacao_estrato_upa | `ca2f8e43555f7721…` |
| h42_atrito_tendencia.parquet | ea4e10a | **SIM** | 2026-10-20 | trimestral_v2 | ewc_e_sem_inferencia | `0375eb22df4a6e82…` |
| h42_transicoes.parquet | ea4e10a | **SIM** | 2026-10-20 | trimestral_v2 | linearizacao_estrato_upa | `535db919733ca182…` |
| habitacao_hiato_racial.parquet | e27278b | não | 2026-10-13 | anual_visita1_v1 | linearizacao_taylor_estrato_upa | `68238756ded440a6…` |
| habitacao_hiato_racial_genero.parquet | e27278b | não | 2026-10-13 | anual_visita1_v1 | linearizacao_taylor_estrato_upa | `f7570e31bb1bc140…` |
| habitacao_hiato_regional.parquet | e27278b | não | 2026-10-13 | anual_visita1_v1 | linearizacao_taylor_estrato_upa | `4c41bacf5ef8e75c…` |
| heaping_renda.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `9c9ea11119ce86f0…` |
| heaping_renda_faixas.parquet | 2219b86 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `aafcfd6f54210f3d…` |
| hiato_arvore.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `9b0a32f88c04b02c…` |
| hiato_branca_indigena.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `90badf4b0c98e82b…` |
| hiato_capital_interior.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `b4478a200e1cd619…` |
| hiato_escolaridade_historico_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `b6a323aaa9c244d6…` |
| hiato_escolaridade_historico_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `73a2b0fc31735310…` |
| hiato_escolaridade_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `93c31857e95426c2…` |
| hiato_escolaridade_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `1b5f6112a340e764…` |
| hiato_faixa_etaria_escolaridade_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `d4d64b2c47f4aa70…` |
| hiato_faixa_etaria_escolaridade_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `acc688637840bb54…` |
| hiato_faixa_etaria_historico_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `a0ed116bc58ef942…` |
| hiato_faixa_etaria_historico_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `739b95d8ac58b934…` |
| hiato_faixa_etaria_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `da73f1daa27b35e7…` |
| hiato_faixa_etaria_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `d94baeb1e1f0f3bf…` |
| hiato_formal_informal.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `e7b1d2ceefdcfb8d…` |
| hiato_genero_escolaridade_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `d4891d368d32dec1…` |
| hiato_genero_escolaridade_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `ad7eaeeb3000a086…` |
| hiato_genero_faixa_etaria_escolaridade_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `3a854017cbea6b65…` |
| hiato_genero_faixa_etaria_escolaridade_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `ca7e5aee7daa5109…` |
| hiato_genero_faixa_etaria_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `15c30de398dbfce5…` |
| hiato_genero_faixa_etaria_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `ac944decae54bac2…` |
| hiato_genero_geracao_escolaridade_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `b24520c1487aea1e…` |
| hiato_genero_geracao_escolaridade_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `6bd877b45ccd6d9e…` |
| hiato_genero_geracao_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `8abdbb5999be4776…` |
| hiato_genero_geracao_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `842793afb805ab56…` |
| hiato_genero_historico_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `ec4b6e1278da6354…` |
| hiato_genero_historico_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `09491f7606013cf7…` |
| hiato_genero_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `3d2f85a534bce740…` |
| hiato_genero_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `1da297e86bdd7644…` |
| hiato_geracao_escolaridade_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `5eb20455f406d35e…` |
| hiato_geracao_escolaridade_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `b2df4e075beb4758…` |
| hiato_geracao_historico_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `53b16de1a48c2119…` |
| hiato_geracao_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `f6924f276b7d7be8…` |
| hiato_geracao_todas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `1ac30e25a1b1dfd1…` |
| hiato_por_geracao.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `667ea4d4d519234d…` |
| hiato_preta_parda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `ff1eafd8b82180d6…` |
| hiato_racial.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `ef24898339c70f98…` |
| hiato_regional.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `92c90ae86c1ce34d…` |
| hiato_regional_indigena.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `237db88d186086f8…` |
| hiato_regional_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `bc21663d6ebad6cd…` |
| hiato_setor_publico_privado.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `aa6e407bef8ca266…` |
| horas_trabalhadas.parquet | 6544305 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `0f64bf3f18205a32…` |
| i1_censo_pnadc.parquet | ea4e10a | **SIM** | 2026-10-20 | censo2022_e_pnadc | linearizacao_domicilio_uf_censo_e_estrato_upa_pnadc | `232142214a79fefc…` |
| informalidade.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `580c3d1de5e27a0c…` |
| linhas_pobreza_ppc.parquet | e22733d | **SIM** | 2026-10-13 | wb_ppc_ipc | sem_inferencia | `530b5d664ed79fc3…` |
| mecanismo_renda_cohortes_cotas.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | wls_statsmodels_cluster_upa | `e9794f1b698a00b7…` |
| oaxaca_blinder_temporal.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | wls_statsmodels_cluster_upa | `29eef9a74bfc5b4a…` |
| ocupacao.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `e226c79ee4f80662…` |
| painel_cohortes_superior_completo.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `6ec7047e261bc9c4…` |
| painel_cohortes_superior_completo_area.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `e99ca5be0cf00149…` |
| painel_cohortes_superior_completo_regiao.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `a09f3bb451e51624…` |
| percentil_de_valor_racial.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `768d8d3f6434a8f8…` |
| perfil_quartis_racial.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `7bfaeb2b913eff60…` |
| perfil_quartis_racial_indigena.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `f0bd388e97763d7a…` |
| perfil_quartis_racial_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `023e3480bc8430a2…` |
| perfil_topo10_racial.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `c15a63e960b0285d…` |
| perfil_topo10_racial_indigena.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `0973a819d9dc8310…` |
| perfil_topo10_racial_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `ad967682e64bb282…` |
| quartis_multi_racial.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `5e826243773101e8…` |
| quebra_estrutural.parquet | 22180a1 | **SIM** | 2026-10-13 | derivado | ewc_lazarus_lewis_stock_watson; sensibilidades newey_west e gls_ar1 | `bcc7c04f7d7f91fb…` |
| renda.parquet | 6544305 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `dd737c0a69069ade…` |
| renda_completa.parquet | 6544305 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `367d5f0df8cffd60…` |
| renda_completa_geracao.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `cca789733b2b3b2a…` |
| renda_multidimensional_faixa.parquet | 6544305 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `ed94789933382e83…` |
| renda_multidimensional_geracao.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `fd41f59be1c34613…` |
| renda_por_escolaridade.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `80f6a10571c130a1…` |
| renda_por_geracao.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `38158855e5220b02…` |
| ritmo_convergencia_hiatos.parquet | 22180a1 | **SIM** | 2026-10-13 | derivado | ewc_lazarus_lewis_stock_watson; sensibilidades newey_west e gls_ar1 | `72933d89a86c4eb8…` |
| s03_perfil_fora_populacao_referencia.parquet | 2219b86 | **SIM** | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `0e52c939af33ac3d…` |
| s13_limites_hiato.parquet | 2219b86 | **SIM** | 2026-10-13 | trimestral_v2 | bootstrap_rao_wu_estrato_upa_200 | `c136cab2cf8680d8…` |
| s14_margens_intensiva_extensiva.parquet | 2219b86 | **SIM** | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `c7d25974abbfa369…` |
| s15_selecao_episodios.parquet | 7bae2e2 | **SIM** | 2026-10-13 | trimestral_v2 | ewc_lazarus_lewis_stock_watson; sensibilidades newey_west e gls_ar1; séries anuais: design-based por ano | `d26050c5db77847b…` |
| s15_selecao_no_tempo.parquet | 2219b86 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `595d58fb59d2c8f3…` |
| segregacao_ocupacional.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `070cd2bec56efb23…` |
| segregacao_ocupacional_indigena.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `ffe145bc3eca9328…` |
| segregacao_ocupacional_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `7fbcf0dc4ab053f7…` |
| segregacao_setorial.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `98eb1df32526b447…` |
| segregacao_setorial_pretaparda.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `0122c76354e89eae…` |
| selecao_entrada_populacao_referencia.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | logit_sanduiche_linearizacao_estrato_upa | `41744a1d7fa7494e…` |
| sensibilidade_hiato_p5_anual.parquet | c1202a1 | **SIM** | 2026-10-13 | anual_v2 | linearizacao_taylor_estrato_upa | `650316485376f68a…` |
| sensibilidade_hiato_populacao.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `d34565ce1dfdcdc4…` |
| sobrequalificacao.parquet | c1202a1 | **SIM** | 2026-10-13 | trimestral_v2 | sem_inferencia | `4a334805887d357b…` |
| t1_renda_domiciliar_per_capita.parquet | bf6ef01 | **SIM** | 2026-10-13 | anual_v2 | linearizacao_taylor_estrato_upa | `f60ed4a2ea2d8d26…` |
| t2_pobreza.parquet | e22733d | **SIM** | 2026-10-13 | anual_v2 | linearizacao_taylor_estrato_upa | `95aa04ce213b9ef9…` |
| t3_fontes_de_renda.parquet | bf6ef01 | **SIM** | 2026-10-13 | anual_v2 | sem_inferencia | `03b4398a19a8c8e7…` |
| t4_decimos_renda_domiciliar.parquet | 2219b86 | **SIM** | 2026-10-13 | anual_v2 | linearizacao_taylor_estrato_upa | `eaeadcba76a73645…` |
| theil_racial.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | sem_inferencia | `479fb0567c6ccd5e…` |
| transicao_desemprego_emprego.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `7e6563eac6d86ba2…` |
| transicao_informal_formal.parquet | c1202a1 | não | 2026-10-13 | trimestral_v2 | linearizacao_taylor_estrato_upa | `9ae996455a3bde34…` |