# ESTADO — Rumo ao 8

Este arquivo é a memória do plano entre sessões. O Claude Code atualiza status e checkpoints. **Só o Felipe aprova fases.**

Base: commit 862de5f (20/10/2026). Criado em 01/11/2026.

## Pré-condição

- Anexos B e C revisados e congelados pelo Felipe: **SIM** (01/11/2026; limiares propostos mantidos sem alteração; Felipe: "pode congelar os anexos e copiar os pareceres por mim?")
- Pareceres A e B copiados para `docs/auditoria/pareceres_20-10-2026/`: **SIM** (01/11/2026; origem `~\Downloads`, cópia conferida por SHA-256)

## Fases

Status possíveis: NAO_INICIADA · EM_ANDAMENTO · AGUARDANDO_APROVACAO · APROVADA · BLOQUEADA · DISPENSADA · A_FAZER_FELIPE

| Fase | Conteúdo | Status | Branch / PR | Início | Fim | Aprovação do Felipe (data e mensagem) |
|---|---|---|---|---|---|---|
| P | Pedidos de acesso (LAI, Censo, POF) | A_FAZER_FELIPE | — | | | — |
| 0 | Baseline e ambiente | APROVADA | rumo8/fase0 | 01/11/2026 | 01/11/2026 | 01/11/2026: "aprovo a fase 0" — aprovada por Felipe |
| 1 | Inferência e engenharia | NAO_INICIADA | rumo8/fase1 | | | |
| 2 | Estimando, população e rivais da queda de 2021 | NAO_INICIADA | rumo8/fase2 | | | |
| 3 | Decomposição, mediadoras e escala | NAO_INICIADA | rumo8/fase3 | | | |
| 4 | Desenho causal (G1) | NAO_INICIADA | rumo8/fase4 | | | |
| 5 | Trilha educacional (EF1–EF8) | NAO_INICIADA | rumo8/fase5 | | | |
| 6 | Saúde, habitação e violência | NAO_INICIADA | rumo8/fase6 | | | |
| 7 | Dados que chegam (condicional) | NAO_INICIADA | rumo8/fase7 | | | |
| 8 | Fechamento dos textos públicos | NAO_INICIADA | rumo8/fase8 | | | |
| R | Reavaliação independente (sessão nova) | NAO_INICIADA | — | | | — |

## Integridade (criada na Fase 0; verificada em toda sessão)

| Arquivo | sha256 |
|---|---|
| 00_MESTRE.md | b20860cfe1d90a90800571e72f68bc5ee4aa8c11f3e84ed67ce3ef767d206184 |
| ANEXO_B_ajustes_do_felipe.md | 76f896256b696566698da636b7129c7e303c4676ab395dbc4d472b6d7bccec32 |
| ANEXO_C_criterios_manchete.md | 6aeb4549c17ecb65eb5b4636e63813ea25fb1e981a7dfef25e777681a749ab54 |

Método (01/11/2026): SHA-256 do conteúdo com quebras de linha normalizadas para LF (`bytes.replace(b"\r\n", b"\n")`), porque o repositório usa `core.autocrlf=true` e um checkout no Windows troca LF por CRLF sem mudar o texto. Na data do registro, hash bruto = hash normalizado.

## Dados recebidos (preenchido pelo Felipe)

| Fonte | Pedido enviado em | Resposta em | Arquivo/local | Observação |
|---|---|---|---|---|
| LAI nº 1 (preenchimento cor/raça, SIAPE) | | | | |
| LAI nº 2 (G3, Lei 12.990) | | | | |
| Censo 2022 controlado | | | | |
| Censo 2022 SAR | | | | |
| POF 2024–25 | | | | |

## Checkpoints da fase em andamento

<!-- uma linha por tarefa: data · tarefa · commit · resultado · o que falta -->

Fase 0 (detalhes em `docs/auditoria/baseline_rumo8.md`):
- 01/11/2026 · 0.1 · 01c2cdf · HEAD = 862de5f (esperado); tag `baseline-20261020` criada (local) · nada
- 01/11/2026 · 0.2 · 01c2cdf · pareceres A e B presentes em `docs/auditoria/pareceres_20-10-2026/` · nada
- 01/11/2026 · 0.3 · (ver commit da Fase 0) · `.venv`: 175 passed, 10 warnings, 90,1 s; Python global falha na coleta (sem tqdm) · nada
- 01/11/2026 · 0.4 · idem · Python ok e igual ao lock; R ausente; IBGE ok; INEP 403 no HEAD; DATASUS só FTP · decidido: só Python (Felipe, 01/11/2026)
- 01/11/2026 · 0.5 · idem · replicados: 0 trimestres no extrato local; presentes no bruto (verificado 2012T1 e 2026T2) · extrair com `--pesos-replicados` na Fase 1
- 01/11/2026 · 0.6 · idem · vintage única (republicação de 15/08/2025 + 4 pontuais); sem degrau na população em 2020T1/2022T1 · distribuição dos pesos entre grupos fica para a Fase 2
- 01/11/2026 · 0.7 · idem · 183 parquets; 77 "-modificado" · regenerar na Fase 1
- 01/11/2026 · 0.8 · idem · `pendencias_textuais.md`: 1.108 frases candidatas (varredura léxica) · "por quê" e "frase proposta" nas fases seguintes
- 01/11/2026 · 0.9 · fora do git · `data/raw/MANIFEST.md`: 271 itens, 724 arquivos, 4,43 GB · versionado (Desvio 1)
- 01/11/2026 · 0.10 · (commit pós-aprovação) · linha "Leitura principal em revisão (ver docs/auditoria)" no topo do README, autorizada pelo Felipe ("4 e 5 - pode seguir") · nada
- 01/11/2026 · 0.11 · idem · hashes registrados na seção Integridade · nada

## Desvios do plano

<!-- algo não existe, variável ausente, dado indisponível, decisão adiada: data · fase · o que aconteceu · decisão do Felipe -->

1. 01/11/2026 · Fase 0 · `data/raw/` está no `.gitignore`, então `data/raw/MANIFEST.md` (regra 14 e tarefa 0.9) fica fora do git. Proposta: exceção `!data/raw/MANIFEST.md` no `.gitignore` · decisão do Felipe (01/11/2026): "pode versionar" — feito (`data/raw/*` + `!data/raw/MANIFEST.md`)
2. 01/11/2026 · Fase 0 · O Python global não tem as dependências do projeto (sem tqdm). Todas as fases usam `.venv\Scripts\python.exe` · decisão do Felipe: _pendente_ (informativo)
3. 01/11/2026 · Fase 0 · R não instalado. Proposta: validar o EP só em Python (replicados do IBGE contra Taylor + reimplementação independente); justificativa em `baseline_rumo8.md` §0.4 · decisão do Felipe (01/11/2026): "validar em python"
4. 01/11/2026 · Fase 0 · `dados.inep.gov.br` não resolve no DNS; `download.inep.gov.br` responde 403 ao HEAD; DATASUS acessível só por FTP. Afeta as Fases 5 e 6, não a Fase 0 · decisão do Felipe: _pendente_ (informativo)
5. 01/11/2026 · Fase 0 · Para responder 0.5/0.6 baixei 2 zips do IBGE (2012T1, 2026T2; 450 MB), li e apaguei; registrados no MANIFEST com URL e SHA-256. Não estava literalmente na tarefa · decisão do Felipe: _pendente_ (informativo)
6. 01/11/2026 · Fase 0 · Hash de integridade com quebras de linha normalizadas para LF (ver seção Integridade), em vez de hash bruto do arquivo · decisão do Felipe: _pendente_

## Critérios de manchete disparados

<!-- registrado pela Fase 2 e seguintes: critério, resultado, manchete resultante -->
