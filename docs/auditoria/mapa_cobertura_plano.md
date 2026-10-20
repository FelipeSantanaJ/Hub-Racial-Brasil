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
| B2 | Já existe | `b2_decomposicao_tempo` (reclassificação Preta/Parda + JMP de médias), `b2_composicao_racial_coortes`. RIF por janela no D1.3 (Onda 3) | — |
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
| T2 | Já existe | `t2_pobreza` (FGT 0/1/2; ¼ SM, ½ SM, 50% da mediana; US$ 3,00, 4,20 e 8,30/dia em PPC 2021 desde a Onda 2, insumo `linhas_pobreza_ppc`) | — |
| T3 | Já existe | `t3_fontes_de_renda` (2016+) | — |
| T4 | Já existe | `t4_decimos_renda_domiciliar` | — |
| T5 | Já existe | S1 (P1 × P5) e ficha T | — |

## Bloco D — Por que a diferença existe? (decomposição)

| ID | Estado | Onde | Por quê |
|---|---|---|---|
| D1.1 | Já existe (Onda 3) | `d1_aninhada` (E0–E8: idade, sexo, instrução, território, horas, vínculo, ocupação, atividade; janelas + série anual), `d1_ob_reimers`. As antigas `decomposicao_oaxaca_blinder*` e `decomposicao_hiato_ocupacional` ficam para comparação | — |
| D1.2 | Já existe (Onda 3) | `d1_contribuicao_blocos` (Gelbach com EP que inclui a incerteza de β; Shapley sobre 8 blocos), `d1_mudanca_janelas` | — |
| D1.3 | Já existe (Onda 3) | `d1_rif_ob` (P10–P90, bandas × 0,5/1/2, bootstrap Rao-Wu na banda × 1) | — |
| D1.4 | Já existe (Onda 3) | `d1_sensibilidade_omitidas` (Oster; Cinelli-Hazlett RV e limites por bloco) | — |
| D2.1 | Já existe (Onda 3) | Contribuição da instrução no D1 | — |
| D2.2 | Já existe (Onda 3) | `d2_hiato_por_nivel` (hiato bruto e condicional por nível de VD3004; BH) | — |
| D2.3 | Já existe (Onda 3) | `d2_quantis_nivel` (P10/P50/P90 dentro do nível; bootstrap Rao-Wu) | — |
| D2.4 | Já existe (Onda 3) | `d2_sobrequalificacao` (três definições; Gelbach entre diplomados). A antiga `sobrequalificacao` usa só o grupo 09 | — |
| D2.5 | — | Remete ao Bloco E | — |
| D3.1 | Já existe (Onda 3) | Contribuição da ocupação no D1 | — |
| D3.2 | Já existe (Onda 3) | `d3_segregacao` (Duncan e Theil H; grupamento e CBO-4; benchmark aleatório; série anual) | — |
| D3.3 | Já existe (Onda 3) | `d3_hiato_dentro_ocupacao` (efeitos fixos de CBO de 4 dígitos) | — |
| D3.4 | Já existe (Onda 3) | Fichas D1 e D3 (E6 × E8 × CBO-4; texto sobre mediação) | — |
| D3.5 | Bloqueado por dado | Dentro da firma exige RAIS identificada (sem vínculo institucional). Só literatura | — |
| D4.1 | Já existe (Onda 3) | `d4_territorio` (Kitagawa entre/dentro de UF) | — |
| D4.2 | Já existe (Onda 3) | `d4_territorio` (Branca × Negra por UF, bruto e condicional, BH entre as 27; correlação com % negra) | — |
| D4.3 | Já existe (Onda 3) | `d4_territorio` (tipo de área V1023 e situação V1022, com e sem território) | — |
| D4.4 | Feito (Onda 6, parte descritiva) | `d44_segregacao_residencial` (Censo 2022, setores) | mecanismo (`M`) fora de alcance |
| D5.1 | Já existe | Contribuição das horas no D1; S1.4 (renda por hora) | — |
| D5.2 | Já existe (Onda 3) | Contribuição do vínculo no D1; `hiato_formal_informal`, `hiato_setor_publico_privado`, `informalidade` | — |
| D5.3 | Já existe (Onda 3) | `d5_posicao_ocupacao` (MQO linear por posição e previdência, bruto e condicional; por nível) | DFL não feito (`met`) |
| D5.4 | Bloqueado por dado (parcial) | Literatura + RAIS/CAGED públicos; RAIS identificada fora de alcance | — |
| D6.1 | Já existe (Onda 3) | `d6_hiato_idade` (perfil idade-renda por raça) | — |
| D6.2 | Já existe (Onda 3) | `d6_hiato_idade` (hiato bruto e condicional por faixa; 50–59 − 25–29); coortes no B4 | — |
| D7.1 | Já existe (Onda 2) | C4–C6 (maternidade, chefia, estado conjugal) | — |
| D8.1 | Já existe (Onda 3) | Ficha D8 (faixa do resíduo a partir do D1, D2, D3, D4) | — |
| D8.2 | Bloqueado por dado | RAIS identificada; literatura de auditoria NÃO VERIFICADA nesta onda | — |
| D8.3 | Já existe (Onda 3) | Ficha D8 (texto de conclusão do bloco) | — |

## Bloco E — Educação

| ID | Estado | Onde | Por quê |
|---|---|---|---|
| E1 | Já existe (Onda 4) | `e1_escolarizacao_idade` (frequência, etapa adequada, atraso, conclusão por idade simples; V3003/V3003A harmonizados) | atraso dentro do fundamental (`V3006`) não feito |
| E2 | Já existe (Onda 4) | Funil PNADC em `e1_escolarizacao_idade`; Censo Escolar público é por escola (matrículas por cor/raça, sem aluno): `e7_escolas_segregacao` | progressão/evasão por aluno com raça só via SEDAP |
| E3 | Já existe (Onda 4) | `e3_saeb_proficiencia` (SAEB 2023 traz cor/raça do aluno, INSE e proficiência; bruto, + INSE, dentro da escola) | — |
| E4 | Já existe, parte PNADC (Onda 4) | `e4_rede_escola` (rede por etapa e raça; condicional a lugar e escolaridade/renda dos pais; composição da graduação) | tipo de escola fino: Censo Escolar |
| E5 | Já existe (Onda 4) | Ficha H1 (`h1_transmissao_educacional`, `h1_corresidencia`) | — |
| E6 | Já existe, descritivo (Onda 4) | `e6_superior_composicao` (Censo da Educação Superior 2014 e 2023, por curso: ingresso, matrícula, conclusão por cor/raça; reserva de vagas). Por aluno: só SEDAP | desenho causal: G1 |
| E7 | Já existe (Onda 4) | `e7_escolas_segregacao` (Censo Escolar 2024: segregação entre escolas, infraestrutura dentro do município) | bairro: Censo 2022 |
| E8 | Novo | Só literatura (`M`) | — |

## Bloco G — Políticas e causalidade

| ID | Estado | Onde | Por quê |
|---|---|---|---|
| G1 | Feito (Onda 5) | `g1_cotas_federais`, `g1_series_grupos` (Censo da Educação Superior 2009–2023 por instituição; event study + Callaway–Sant'Anna). Efeito não separável do artefato de declaração (ficha G1) | substitui o desenho A (`did_cotas_universitarias*`) |
| G2 | Bloqueado por dado | aluno ligado à RAIS (restrito) | ficha G2 |
| G3 | Bloqueado por dado | cor/raça do SIAPE não pública; PEP sem cor/raça (IPEA 2021) | ficha G3 |
| G4 | Bloqueado por poder | EMD de β 1,45–3,4 > 1 (ficha G6); estimador pronto (`bloco_g.g4_estimar`) e não aplicado | ficha G4 |
| G5 | Bloqueado por dado | CadÚnico (acesso restrito); T3 cobre a contabilidade | ficha G5 |
| G6 | Feito (Onda 5) | `g6_emd` (EMD por simulação AR(1)) | ficha G6 |

## Bloco H — Origem social, mobilidade e patrimônio

| ID | Estado | Onde | Por quê |
|---|---|---|---|
| H1.1–H1.4 | Já existe (Onda 4) | `h1_transmissao_educacional`, `h1_corresidencia` (viés de corresidência medido). Suplemento de mobilidade só na PNAD antiga de 2014 | — |
| H2.1–H2.4 | Já existe (Onda 4) | `h2_origem_renda` (E8 com e sem origem; Gelbach; elasticidade proxy), `h2_mobilidade_quintis` | — |
| H3.1 | Já existe (Onda 4) | `h3_patrimonio_proxy` (bruto e no mesmo décimo de renda, UF e situação; 2016–2019/2022–2025; a Visita 5 não tem `S01017`). A antiga `habitacao_hiato_racial*` fica para comparação | — |
| H3.2 | Já existe (Onda 4) | `h32_pof_bens` (POF 2017–2018: bens duráveis no mesmo décimo de renda) | — |
| H3.3 | Já existe (Onda 4) | `h3_patrimonio_proxy` (aluguel e aplicações de adultos 18+, bruto e condicional) e T3 (domicílios) | — |
| H3.4 | Feito como proxy (Onda 6) | `h34_riqueza_imobiliaria` (moradia própria pela POF); riqueza total segue sem dado | — |
| H4.1 | Existe, precisa refazer | Igual a D6.1/B4 | `pop` |
| H4.2 | Feito (Onda 6) | `h42_transicoes`, `h42_atrito_tendencia` (ligação estrita, atrito, série anual); substitui `transicao_*` | — |

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

> O resumo acima é o retrato da Fase 2 (13/10/2026); o estado de cada pergunta é atualizado na própria linha. Onda 5
> (20/10/2026): G1 e G6 feitos; G2, G3 e G5 bloqueados por dado; G4 bloqueado por poder. Painel Estatístico de
> Pessoal: sem cor/raça segundo o IPEA (2021) — ver ficha G3.
> Onda 6 (20/10/2026): D4.4, H3.4 (proxy) e H4.2 feitos; I1 (Censo 2022 × PNADC) novo; Censo 2022 deixou de ser
> "Bloqueado" (agregados por setor e amostra pública no FTP do IBGE).
