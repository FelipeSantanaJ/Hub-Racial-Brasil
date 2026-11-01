# Rumo ao 8 — como usar esta pasta

Pasta: `docs/rumo8/`. Objetivo: levar o Hub-Racial-Brasil de nota 5,6 para >= 8 nas dimensões corrigíveis, com pré-registro, verificação independente e gates de aprovação. Metas e teto honesto: `01_METAS_E_TETO.md`.

## Antes da primeira sessão (você)

1. Copie `PARECER_PASSADA_A.md` e `PARECER_PASSADA_B.md` para `docs/auditoria/pareceres_20-10-2026/` e marque em `ESTADO.md`.
2. Leia `ANEXO_B_ajustes_do_felipe.md` e `ANEXO_C_criterios_manchete.md`. Ajuste os limiares **agora**; depois da Fase 2 eles não mudam. Marque "congelados: SIM" em `ESTADO.md`.
3. Faça a Fase P (`FASE_P_pedidos.md`): envie os pedidos. É independente do resto e tem prazo externo.

## Em toda sessão

Abra o Claude Code na raiz do repositório e diga:

> Leia `docs/rumo8/ORQUESTRADOR.md` e execute.

O orquestrador lê `ESTADO.md`, descobre a fase, carrega só o arquivo dela, executa, registra checkpoints e **para no gate**.

## No gate (você)

1. Leia `docs/auditoria/relatorio_<fase>.md` e as fichas da fase.
2. Preencha "Decisões do Felipe" nas fichas (ou diga ao Claude Code o que decidiu).
3. Se aprovar, diga na sessão: **"aprovo a Fase N"**. O orquestrador registra a data e a sua mensagem em `ESTADO.md`. Sem essa frase, a fase seguinte não começa.
4. Faça o merge do PR da fase e abra uma sessão nova com a mesma frase.

## Ordem

P (você) → 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 (só com dado novo) → 8 → R (sessão nova, sem este histórico).

## Esforço relativo

| Fase | Conteúdo | Esforço |
|---|---|---|
| P | Pedidos de acesso (você) | Baixo |
| 0 | Baseline e ambiente | Baixo |
| 1 | Inferência e engenharia | Alto |
| 2 | Estimando, população e rivais da queda de 2021 | Alto |
| 3 | Decomposição, mediadoras e escala | Médio |
| 4 | Desenho causal (G1) | Médio |
| 5 | Trilha educacional | Alto |
| 6 | Saúde, habitação e violência | Alto |
| 7 | Dados que chegam | Médio, condicional |
| 8 | Fechamento dos textos públicos | Médio |
| R | Reavaliação independente | Baixo |

## Arquivos

| Arquivo | Para quê |
|---|---|
| `ORQUESTRADOR.md` | O prompt único |
| `ESTADO.md` | Memória entre sessões (status, checkpoints, aprovações) |
| `00_MESTRE.md` | Regras fixas de todas as fases |
| `01_METAS_E_TETO.md` | Onde estamos e o teto honesto |
| `02_REGUA_DE_ACEITE.md` | Meta e teste de aceite por dimensão |
| `FASE_*.md` | Um arquivo por fase (lidos só quando chega a vez) |
| `ANEXO_A_consolidacao.md` | Os 10 problemas e seus testes de aceitação |
| `ANEXO_B_ajustes_do_felipe.md` | O que você ajusta antes de começar |
| `ANEXO_C_criterios_manchete.md` | Critérios pré-fixados que podem mudar a manchete |

## Regras que protegem o rigor

- O Claude Code não edita os arquivos de regra nem os anexos; propõe em `PROPOSTAS_DE_MUDANCA.md`.
- Hashes dos arquivos de decisão ficam em `ESTADO.md`; mudança depois da Fase 0 é detectada.
- Textos públicos só mudam na Fase 8.
- A reavaliação (Fase R) acontece numa sessão que não viu o trabalho sendo feito.
