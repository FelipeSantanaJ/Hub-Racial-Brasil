# Mapa de cobertura do plano de análise (v1.0)

**Data:** 13/10/2026 · **Base:** `docs/PLANO_DE_ANALISE.md` v1.0 (com as decisões dos Pontos de parada 0 e 1)
× o que existe hoje em `data/processed` (101 parquets), `docs/` e `src/`.

**Legenda**
- **Já existe**: responde a pergunta como o plano pede.
- **Existe, precisa refazer**: há tabela/gráfico, mas fora do padrão do plano. Quase sempre por pelo
  menos um destes motivos, indicados na coluna "Por quê":
  `pop` = recorte histórico (14+, renda de todos os trabalhos `VD4019`) em vez da referência (18+, `VD4016`);
  `ic` = sem IC ou com gráfico de IC antigo; `esp` = especificação ou método insuficiente (auditoria);
  `ser` = só foto do último trimestre, sem série; `met` = métrica pedida não calculada.
- **Novo**: nada no Hub.
- **Bloqueado por dado**: depende de fonte que não temos ou não podemos obter (decisão de 12/10/2026: sem
  vínculo institucional, logo sem RAIS identificada nem SEDAP/INEP).
- **NÃO VERIFICADO**: não conferi o conteúdo da tabela/documento contra a pergunta; a classificação é
  pelo nome e pelo gerador.

**Atualização da Onda 1 (13/10/2026):** todas as tabelas de renda foram regeneradas na população de
referência (18+, `VD4016`), com supressão (`n_*`, `cv_*`, `publicavel`), repartição do peso empatado nos
limiares de quantil e carteira só CLT. O motivo `pop` das linhas abaixo **deixa de valer**: onde ele era
o único motivo, a linha passa a "Já existe" na leitura do Ponto de parada da Onda 1; os outros motivos
(`ic`, `esp`, `ser`, `met`) continuam. Estudos novos da Onda 1: F (definições), S0, S1 — ver
`docs/studies/INDICE.md`. T1–T3 e A2–A7 entraram na parte 2 (PR #7); S0.3, S1.3–S1.5, T4 e as pendências
técnicas (R11, F4, F6, imagens vazias da árvore) nas pendências da Onda 1 (`onda1/pendencias`).

## Bloco F — Fundações

| ID | Estado | Onde / o que falta | Por quê |
|---|---|---|---|
| F1 | Novo | Composição declarada 2012–2026 e efeito composição × renda: nada | — |
| F2 | Existe, precisa refazer | `VD4016` e `VD4019` na base; prévia do hiato sob os dois conceitos no CHANGELOG (13/10/2026). Falta a tabela de sensibilidade com IC (todas as fontes, por hora, domiciliar per capita) | `met` |
| F3 | Existe, precisa refazer | `src/utils/populacao.py` (definição e flags 18+/14+); falta a tabela de sensibilidade de população | `met` |
| F4 | Já existe (parcial) | `heaping_renda`, `heaping_renda_faixas` (o heaping dobrou por composição nominal; shift-share). Subdeclaração e topo: não feito | `met` (topo) |
| F5 | Já existe | `src/inference/` (linearização Estrato/UPA, Rao-Wu, FDR); `checagem_robustez_hiato_racial`. Réplicas não usadas por decisão | — |
| F6 | Existe, precisa refazer | Marcas de 4T2015, recessão 2015–16 e 2020–21 em todos os gráficos de série (`graficos_fase1.marcar_quebras`, pendências da Onda 1). Falta: `quebra_estrutural` com EP robusto (B1/B5, Onda 2) | `esp` |

## Bloco A — A diferença existe? De quanto?

| ID | Estado | Onde | Por quê |
|---|---|---|---|
| A1 | Existe, precisa refazer | `hiato_racial`, `hiato_branca_indigena`, `hiato_preta_parda`, `renda*` | `pop` |
| A2 | Já existe | `a2_metricas_hiato` (R$, razão, log-pontos, % da renda Branca, hiato %, IC) | — |
| A3 | Já existe | `a3_hiato_quantis` (P10…P99, razões P90/P50 e P50/P10, bootstrap Rao-Wu, 2º trimestres) | — |
| A4 | Já existe | `a4_desigualdade_decomposicao` (Gini, Theil T e L com Amarela) | — |
| A5 | Já existe | `a5_representacao_decimos` (índice de representação por décimo; razão de chances topo/base 10%) | — |
| A6 | Já existe | `a6_dominancia` (Branca domina Negra em todos os anos) | — |
| A7 | Já existe | `a2_metricas_hiato` (conceito `por_hora`, `V4039`) e `t1_renda_domiciliar_per_capita` | — |

## Bloco B — Tendência e ritmo

| ID | Estado | Onde | Por quê |
|---|---|---|---|
| B1 | Já existe | `b1_tendencia_hiato`, `b1_degraus_hiato`; `ritmo_convergencia_hiatos` e `quebra_estrutural` refeitos com EP EWC (Onda 2) | — |
| B2 | Já existe | `b2_decomposicao_tempo` (reclassificação Preta/Parda + JMP de médias), `b2_composicao_racial_coortes`. RIF no tempo fica no D1.3 (Onda 3) | — |
| B3 | Já existe | `b3_hiato_quantis_serie`, `b3_tendencia_quantis`, `b3_quantis_janelas` | — |
| B4 | Já existe | `b4_mesma_idade_coortes`, `b4_celulas_idade_ano`, `b4_apc` (restrição de Deaton-Paxson declarada; sensibilidade AC) | — |
| B5 | Já existe | `b5_ciclo_tendencia`, `b5_taxa_desocupacao` | — |
| B6 | Já existe | `b6_projecao_condicional` (premissas P-a, P-b, P-c; "sem data finita" quando o ritmo inclui zero) | — |

## Bloco C — Raça × gênero

| ID | Estado | Onde | Por quê |
|---|---|---|---|
| C1 | Já existe | `c123_racaxsexo_celulas` (P1 e P4), `c123_racaxsexo_domiciliar_anual`, `c1_quantis_celulas`, `c1_theil_celulas` | — |
| C2 | Já existe | `c123_racaxsexo_celulas` (DiD), `c2_interacao_regressao` (β3 com EP design-based), `c2_interacao_tendencia` | — |
| C3 | Já existe | `c123_racaxsexo_celulas` (Shapley, ordens sequenciais; reconciliado com `decomposicao_raca_genero`) | — |
| C4 | Já existe | `c4_penalidade_maternidade` (UPA + V1008 + V1014; responsáveis/cônjuges; sensibilidade com qualquer criança 0–5) | — |
| C5 | Já existe | `c5_trabalho_domestico`, `c5_tendencia` | — |
| C6 | Já existe | `c6_conjugal_chefia`, `c6_hiato_condicional` (associação; endogeneidade declarada) | — |

## Bloco S — Seleção (o recorte "ocupados com renda" distorce o hiato?)

| ID | Estado | Onde | Por quê |
|---|---|---|---|
| S0.1 | Já existe | `composicao_populacao_referencia` | — |
| S0.2 | Já existe | `selecao_entrada_populacao_referencia` (efeito marginal com EP design-based) | — |
| S0.3 | Já existe | `s03_perfil_fora_populacao_referencia` (ficha `S0.3`) | — |
| S1.1 | Já existe | `sensibilidade_hiato_populacao` (P1–P4) e `sensibilidade_hiato_p5_anual` | — |
| S1.2 | Já existe | Idem, por sexo | — |
| S1.3 | Já existe | `s13_limites_hiato` (Manski, seleção positiva, piso, aparamento à la Lee; IC de Imbens–Manski) | — |
| S1.4 | Já existe | `s14_margens_intensiva_extensiva` | — |
| S1.5 | Já existe | `s15_selecao_no_tempo`, `s15_selecao_episodios` (EP EWC) | — |

## Bloco T — População inteira

| ID | Estado | Onde | Por quê |
|---|---|---|---|
| T1 | Já existe | `t1_renda_domiciliar_per_capita` (por raça da pessoa e raça × sexo do responsável) | — |
| T2 | Já existe | `t2_pobreza` (FGT 0/1/2; ¼ SM, ½ SM, 50% da mediana). Linhas em PPC pendentes | `met` (PPC) |
| T3 | Já existe | `t3_fontes_de_renda` (2016+) | — |
| T4 | Já existe | `t4_decimos_renda_domiciliar` | — |
| T5 | Já existe | S1 (P1 × P5) e ficha T | — |

## Bloco D — Por que a diferença existe? (decomposição)

| ID | Estado | Onde | Por quê |
|---|---|---|---|
| D1.1 | Existe, precisa refazer | `decomposicao_oaxaca_blinder*` (3 especificações: idade, instrução, ocupação), `decomposicao_hiato_ocupacional` | `pop`, `esp` (R5: faltam região, sexo, horas, informalidade, setor, posição) |
| D1.2 | Novo | Gelbach/Shapley: nada | — |
| D1.3 | Existe, precisa refazer | RIF por quantil (gráfico `oaxaca_blinder_quantis.png`; função `rif_quantil`) | `esp` (R4: banda/heaping) |
| D1.4 | Novo | Oster/Cinelli-Hazlett: nada | — |
| D2.1 | Existe, precisa refazer | Contribuição de instrução nas especificações do OB | `pop`, `esp` |
| D2.2 | Existe, precisa refazer | `renda_por_escolaridade`, `hiato_escolaridade_*` (hiato por nível); sem interação raça × nível em regressão | `pop`, `esp` |
| D2.3 | Novo | RIF por nível: nada | — |
| D2.4 | Existe, precisa refazer | `sobrequalificacao` (Superior completo em ocupação de menor nível) | `pop`; NÃO VERIFICADO o índice usado |
| D2.5 | — | Remete ao Bloco E | — |
| D3.1 | Existe, precisa refazer | Contribuição de ocupação no OB | `pop`, `esp` |
| D3.2 | Existe, precisa refazer | `segregacao_ocupacional*`, `segregacao_setorial*` (Duncan); falta índice de entropia | `met` |
| D3.3 | Novo | OB com FE de CBO 4 dígitos: `V4010` extraída na v2, nada calculado | — |
| D3.4 | Existe, precisa refazer | OB tem especificação com e sem ocupação; falta o enquadramento de mediador por escrito | `esp` |
| D3.5 | Bloqueado por dado | Dentro da firma exige RAIS identificada (sem vínculo institucional). Só literatura | — |
| D4.1 | Novo | Decomposição entre/dentro de região: nada | — |
| D4.2 | Existe, precisa refazer | `hiato_regional` (região), `hiato_regional_pretaparda` (UF, Preta × Parda). Falta Branca × Negra por UF | `pop`, `met` |
| D4.3 | Existe, precisa refazer | `hiato_capital_interior`; urbano/rural (`V1022`) na base, sem tabela | `pop` |
| D4.4 | Bloqueado por dado | Segregação residencial exige Censo 2022 (GovBR) | — |
| D5.1 | Existe, precisa refazer | `horas_trabalhadas`; horas do trabalho principal (`V4039`) só na v2 | `pop`, `met` |
| D5.2 | Existe, precisa refazer | `hiato_formal_informal`, `hiato_setor_publico_privado`, `informalidade` | `pop` |
| D5.3 | Novo | Logit multinomial/DFL: nada | — |
| D5.4 | Bloqueado por dado (parcial) | Literatura + RAIS/CAGED públicos; RAIS identificada fora de alcance | — |
| D6.1 | Existe, precisa refazer | `renda_por_geracao`, `renda_completa_geracao` | `pop` |
| D6.2 | Existe, precisa refazer | `hiato_faixa_etaria_historico_*`, `hiato_por_geracao` | `pop` |
| D7.1 | Novo | Ver C4–C6 | — |
| D8.1 | Novo | Faixa do resíduo (Oster): nada | — |
| D8.2 | Bloqueado por dado | RAIS identificada; só literatura de auditoria | — |
| D8.3 | Novo | Texto de conclusão do bloco | — |

## Bloco E — Educação

| ID | Estado | Onde | Por quê |
|---|---|---|---|
| E1 | Novo | `V3002`, `V3003A`, `V3006` extraídas na v2; nenhuma tabela. Quebra em 4T2015 | — |
| E2 | Novo (parcial bloqueado) | PNADC: possível. Censo Escolar por aluno com raça: só SEDAP (fora de alcance); público simplificado: NÃO VERIFICADO se traz raça agregada por escola | — |
| E3 | Novo (parcial bloqueado) | SAEB público (694 MB, 2023); raça no SAEB público: NÃO VERIFICADO | — |
| E4 | Existe, precisa refazer | Rede pública/privada (`V3002A`, desde 4T2015) extraída na v2; nada calculado | — |
| E5 | Novo | Ligação filhos–pais via `V2005` (extraída); viés de corresidência a quantificar | — |
| E6 | Bloqueado por dado (parcial) | Censo da Educação Superior por aluno com raça/cota: só SEDAP. Agregados públicos por curso: possível, NÃO VERIFICADO | — |
| E7 | Bloqueado por dado | Território fino: Censo 2022 / Censo Escolar por escola | — |
| E8 | Novo | Só literatura (`M`) | — |

## Bloco G — Políticas e causalidade

| ID | Estado | Onde | Por quê |
|---|---|---|---|
| G1 | Existe, precisa refazer | Desenho A: `did_cotas_universitarias*`, `painel_cohortes_superior_completo*`, `docs/ANALISE_CAUSAL_COTAS.md`. Dado administrativo por aluno fora de alcance (SEDAP) | `esp` (R2: células i.i.d., coorte × período, EMD ausente) |
| G2 | Existe, precisa refazer | `mecanismo_renda_cohortes_cotas` (correlacional) | `esp` |
| G3 | Existe, precisa refazer | Desenho B: `did_cotas_servico_publico*`. **0 de 40 testes sobrevivem ao FDR**; `ANALISE_CAUSAL_COTAS.md` §2–3 reescrito como exploratório em 13/10/2026 (E9), estado **Bloqueado até o B4b**. Painel de Pessoal: raça/cor NÃO VERIFICADA | `esp` (R3) |
| G4 | Novo | Salário mínimo (bite index): nada | — |
| G5 | Bloqueado por dado | CadÚnico (acesso restrito) | — |
| G6 | Novo | EMD por desenho: nada | — |

## Bloco H — Origem social, mobilidade e patrimônio

| ID | Estado | Onde | Por quê |
|---|---|---|---|
| H1.1–H1.4 | Novo | `V2005` + escolaridade (`VD3004`) dos moradores permitem a ligação; nada calculado. Suplemento de mobilidade só na PNAD antiga de 2014 | — |
| H2.1–H2.4 | Novo | Depende de H1 e D1 | — |
| H3.1 | Existe, precisa refazer | `habitacao_hiato_racial*` (`imovel_proprio`, de `S01017`), Visita 1, 2016–2019/2022–2025 | `esp` (unidade é pessoa; população não é a de referência; lacuna 2020–21 agora coberta pela Visita 5 extraída) |
| H3.2 | Novo | POF: não baixada | — |
| H3.3 | Novo | `V5007A` (aluguel) e `V5008A` (aplicações) extraídos na v2; nada calculado | — |
| H3.4 | Bloqueado por dado | Riqueza: IR/RAIS não acessíveis; só proxy | — |
| H4.1 | Existe, precisa refazer | Igual a D6.1/B4 | `pop` |
| H4.2 | Existe, precisa refazer | `transicao_desemprego_emprego`, `transicao_informal_formal` (painel de 5 visitas, pooled) | `esp` (atrito; sem série) |

## Resumo

| Estado | Perguntas |
|---|---|
| Já existe | 1 (F5) |
| Existe, precisa refazer | 38 |
| Novo | 44 |
| Bloqueado por dado, total ou parcial | 10 (D3.5, D4.4, D5.4, D8.2, E2, E3, E6, E7, G5, H3.4) |
| Remete a outro bloco | 1 (D2.5 → Bloco E) |
| **Total** | **94** |

Contagem feita por script sobre as linhas das tabelas acima (H1.1–H1.4 e H2.1–H2.4 contadas como 4
cada). Itens com **NÃO VERIFICADO**: `sobrequalificacao` (índice usado), raça/cor no SAEB público, no
Censo Escolar simplificado e no Painel Estatístico de Pessoal.
