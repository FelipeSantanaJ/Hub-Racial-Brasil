# Fase 0 — Baseline e ambiente (esforço baixo)

```text
FASE 0 — Baseline e ambiente. Branch: rumo8/fase0. Não altere números publicados.

OBJETIVO
Congelar o estado de partida, medir o que existe e decidir o ambiente, para que as fases seguintes tenham comparação antes/depois e dados disponíveis.

TAREFAS
0.1 git status; confirmar o HEAD (esperado 862de5f; se for outro, registre as diferenças). Criar a tag baseline-20261020 no HEAD.
0.2 Conferir que docs/auditoria/pareceres_20-10-2026/ tem PARECER_PASSADA_A.md e PARECER_PASSADA_B.md (a consolidação está em docs/rumo8/ANEXO_A_consolidacao.md). Se faltar, pare e peça ao Felipe.
0.3 Rodar a suíte (python -m pytest -q) e registrar o resultado e o tempo.
0.4 Ambiente: Python (versões; duckdb, polars, statsmodels, scipy), R (Rscript --version; instalar/checar: survey, srvyr, did, HonestDiD, fixest se possível), espaço livre em disco, acesso de rede a ftp.ibge.gov.br, dados.inep.gov.br, ftp.datasus.gov.br. Decidir e registrar: o EP será validado em R (survey) ou só em Python.
0.5 Pesos replicados: verificar, nos microdados brutos de data/raw, se existem V1028001..V1028200 (ou equivalentes) para pelo menos 2 trimestres, e em quais anos. Listar.
0.6 Vintage dos pesos: para cada trimestre 2012T1–2026T2 registrar de que versão dos microdados/pesos vem o V1028 usado (reponderação pós-Censo 2022 incluída). Verificar se a série mistura vintages e se isso coincide com 2020T1 ou 2022T1. [HIPÓTESE do revisor: possível quebra de pesos perto de 2022]
0.7 Inventário de proveniência: para cada parquet em escopo, ler o _meta.json e listar commit, "-modificado" sim/não, data. Gerar docs/auditoria/baseline_rumo8.md.
0.8 Mapa de dependências: grep em README.md, docs/*.md, conteudo/ e nomes de gráficos para todo texto que dependa dos 10 problemas do anexo A. Gerar docs/auditoria/pendencias_textuais.md (arquivo, linha, frase, problema do anexo A). NÃO edite os textos.
0.9 data/raw/MANIFEST.md: inventário do que já existe (fonte, data, tamanho, hash).
0.10 OPCIONAL (peça confirmação ao Felipe antes): acrescentar ao README uma única linha "Leitura principal em revisão (ver docs/auditoria)". Nada além disso.
0.11 Integridade dos arquivos de decisão: calcule sha256 de docs/rumo8/00_MESTRE.md, ANEXO_B_ajustes_do_felipe.md e ANEXO_C_criterios_manchete.md e registre em docs/rumo8/ESTADO.md (seção Integridade). Nas sessões seguintes, o orquestrador verifica; divergência = parar.

PERGUNTAS DO MEIO DO CAMINHO
- Os replicados existem e cobrem quantos trimestres?
- O V1028 usado é de uma única vintage?
- Quais parquets do escopo têm proveniência suja?

ACEITE
- baseline_rumo8.md e pendencias_textuais.md existem e estão completos.
- pytest registrado; nenhum número publicado mudou (diff de parquets vazio).
- Decisão R/Python registrada com justificativa.

GATE: pare e peça aprovação.
```

---
