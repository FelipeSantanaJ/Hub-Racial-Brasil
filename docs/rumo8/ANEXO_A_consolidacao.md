# Anexo A — Os 10 problemas (consolidação de 31/10/2026) com correção mínima e aceite

| # | Problema | Correção mínima | Teste de aceitação | Fase |
|---|---|---|---|---|
| 1 | "Degrau de 2022T1" mal datado e teste sobredimensionado (queda é rampa de ~12 p.p. em 2021; tamanho 19–27% a 5%) | Data estimada (sup-Wald com crítico simulado); "rampa em 2021, estável antes e depois" | Monte Carlo 4–7% a 5%; data estimada cai em 2021 | 1 |
| 2 | G1 reportado como +9,0; contra a média pré-lei é +4,9 (IC -1,4 a 11,1); EMD subestimado | Principal contra a média pré-lei, com EP; retrodesign | `g1_cotas_federais` com as colunas; texto cita a menor | 4 |
| 3 | Regra do G1 assimétrica; M̄ não interpretável | Publicar [Y1b, Y1c] = [-5,0; +17,5], sem M̄ | Nenhum texto diz "aumentaram"/"não aumentaram"; limites juntos | 4 |
| 4 | Decomposição em outro estimando que a manchete (78% associado x ~71% em PPML; ~9 lp x ~15,7%) | log-OLS e PPML lado a lado, com a escala dita | E0 fecha com ln(razão de médias) | 3 |
| 5 | Reclassificação racial não limitada | Taxa medida no painel + tabela de limites (troca x seleção) | Frase permitida cita o intervalo compatível com 0–3 p.p. de troca | 2 |
| 6 | EP sem validação independente; CR1 sem (n-1)/(n-k) | Replicados em 2 trimestres; fator completo | Razão EP-replicados/EP-Taylor dentro de ±10% | 1 |
| 7 | Mediadoras tratadas como controles (Oster, Cinelli-Hazlett; E3 com INSE individual) | Só pré-tratamento em Oster/RV; razões do E3 como limites | D8 separa "mediadoras" e "pré-tratamento"; sem "refutada" sem a especificação com contexto | 3 |
| 8 | Proveniência "-modificado"; CI só sintético; filtros de ingestão sem teste; Theil 6,67 x 6,96 | Regenerar de árvore limpa; golden real; testes de ingestão | CI falha com "-modificado" ou golden real divergente | 1 |
| 9 | Células finas: 9 de 24 aprovadas com n_kish < 30; Indígena PNADC 40% x Censo 117% sem explicação | n_kish >= 30 e CV do hiato; explicar ou retirar | Nenhuma célula com n_kish < 30; discrepância decomposta | 2, 3 |
| 10 | Critérios pré-registrados reinterpretados (I1: 0,586 < 0,6 e "validada"); especificações fora do FDR | "H1 refutada pelo critério; disatenuada 0,78"; contar especificações | Cada ficha lista o n de especificações; I1 diz "refutada" | 1, 3 |

Lacunas que nenhuma passada cobriu e que as fases acima fecham: não resposta de rendimento por raça e trimestre (Fase 2); coleta por telefone em 2020–21 (Fase 2); auditoria do SQL de `agregacoes_pnadc.py` (Fase 1.6); multiplicidade global (Fase 1.4); `bloco_eh.py` e fichas G2–G5 (as fases 3–5 reabrem); vintage de pesos (Fase 0/2).

---
