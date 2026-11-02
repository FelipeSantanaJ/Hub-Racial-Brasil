# Relatório — Fase 0 do Rumo ao 8 (Baseline e ambiente)

Data: 01/11/2026. Branch `rumo8/fase0` (a partir de `main` @ 862de5f). Tag `baseline-20261020`.
Detalhes: [baseline_rumo8.md](baseline_rumo8.md) · [pendencias_textuais.md](pendencias_textuais.md) · [verificacoes_fase0.md](verificacoes_fase0.md) · `data/raw/MANIFEST.md` (fora do git).

## O que foi feito

| Tarefa | Resultado |
|---|---|
| 0.1 | HEAD = 862de5f (esperado). Tag `baseline-20261020` criada (local). |
| 0.2 | Pareceres A e B presentes e iguais à origem (SHA-256). |
| 0.3 | `.venv`: **175 passed, 10 warnings, 90,1 s**. Com o Python global a suíte nem coleta (falta tqdm). |
| 0.4 | Python da `.venv` igual ao `requirements.lock`; **R ausente**; 164,8 GB livres; IBGE ok, INEP com ressalvas, DATASUS só por FTP. **Proposta: EP validado só em Python.** |
| 0.5 | Replicados V1028001–200: **0 trimestres no extrato local**; presentes e completos no bruto do IBGE (verificado em 2012T1 e 2026T2; inferido nos demais). |
| 0.6 | V1028 de **uma única vintage** (republicação de 15/08/2025 + 4 republicações pontuais); população sem degrau em 2020T1 e 2022T1. |
| 0.7 | 183 parquets; **77 com "-modificado"**, entre eles os da manchete (`a2_metricas_hiato`, `b1_*`) e `g1_sensibilidade_rr`, `i1_censo_pnadc`. |
| 0.8 | `pendencias_textuais.md`: 1.108 frases candidatas em README, docs, conteudo/, 2 PPTX e nomes de gráficos. Nenhum texto editado. |
| 0.9 | `data/raw/MANIFEST.md`: 271 itens, 724 arquivos, 4,43 GB, com SHA-256. |
| 0.10 | **Não executada** (opcional; precisa da sua confirmação). |
| 0.11 | Hashes de 00_MESTRE, ANEXO_B e ANEXO_C registrados em ESTADO.md. |

## Respostas às perguntas da fase

- **Os replicados existem e cobrem quantos trimestres?** No microdado do IBGE, sim: verificados 2 trimestres (2012T1 e 2026T2), todos preenchidos. Inferido que existem nos 58 [INFERIDO]. No extrato local, nenhum, porque é preciso extrair de novo com `--pesos-replicados` (Fase 1).
- **O V1028 usado é de uma única vintage?** Sim, no total de população [VERIFICADO para a soma; INFERIDO para a origem dos 56 trimestres não baixados]. A hipótese de quebra de pesos perto de 2022 não aparece no total. Ainda não foi testado se a distribuição dos pesos ENTRE grupos de cor/raça mudou: isso é da Fase 2.
- **Quais parquets têm proveniência suja?** 77 de 183 (lista no Anexo 2 do baseline).

## Números antes e depois

Nenhum número publicado mudou: `git diff baseline-20261020 -- data/processed` vazio [VERIFICADO]. A Fase 0 não gera número publicável.

## Testes de aceitação

| Aceite | Resultado |
|---|---|
| `baseline_rumo8.md` e `pendencias_textuais.md` existem e estão completos | **Passou**, com ressalva: as pendências são candidatas de uma varredura léxica, com falsos positivos e possíveis falsos negativos; as fases seguintes completam "por quê" e "frase proposta" |
| pytest registrado | **Passou** (175/175 na `.venv`) |
| Nenhum número publicado mudou (diff de parquets vazio) | **Passou** |
| Decisão R/Python registrada com justificativa | **Passou** como proposta (só Python); a confirmação é sua |

## O que ficou sem verificação

- Replicados e vintage nos 56 trimestres não baixados (inferidos).
- URLs exatas das fontes INEP, Censo 2022 e POF no MANIFEST (marcadas [a confirmar]; o código não as registra).
- Se `download.inep.gov.br` aceita GET (o HEAD deu 403).
- A nota técnica do IBGE sobre a reponderação de 2025 não foi lida [a confirmar].

## O que exige decisão do Felipe

1. **Aprovar a Fase 0** ("aprovo a Fase 0").
2. **R ou Python** para validar o EP. Recomendo só Python, pelos motivos em `baseline_rumo8.md` §0.4. Se escolher R, autorize a instalação.
3. **Versionar `data/raw/MANIFEST.md`?** Hoje ele fica fora do git por causa do `.gitignore`. A proposta é uma exceção `!data/raw/MANIFEST.md`.
4. **0.10 (opcional):** acrescentar ao README a linha "Leitura principal em revisão (ver docs/auditoria)". Sim ou não.
5. **Normalização LF nos hashes de integridade:** confirmar o método (Desvio 6 em ESTADO.md).
6. **Push do branch `rumo8/fase0` e PR:** não fiz push. O merge é seu.
