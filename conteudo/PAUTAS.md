# Banco de pautas

Cada pauta parte de um achado já publicado na árvore de análises. A coluna "Origem" diz onde
conferir o número antes de publicar. Período dos números: Brasil, 2026 T2, salvo indicação.

Status de todas as pautas: ⏳ não iniciada (produção a partir de C3, fev/2027).

## Série "O tamanho do hiato"

| ID | Gancho | Achado | Origem |
|---|---|---|---|
| P01 | "Em 14 anos, o hiato de renda caiu. Quanto?" | Hiato Branca vs. Negra de ~76% para ~66% (2012-2026); os 58 trimestres são estatisticamente significativos | `docs/img/hiato_racial_percentual.png`, `renda_por_raca.png` |
| P02 | "Mesmo diploma, mesmo salário?" | Superior completo: Branca R\$8.104 vs. Negra R\$5.701; diferença maior entre homens (~46%) que entre mulheres (~36%) | `renda_por_raca_escolaridade.png` |
| P26 | "A renda negra cresceu mais. A distância diminuiu?" | Negra cresceu mais (em %) em 101 de 181 recortes, mas a diferença em R\$ aumentou em 92 | `docs/tabela_crescimento_renda.xlsx` |
| P19 | "Preta e Parda: a diferença dentro da população negra" | O hiato Preta vs. Parda mudou de sinal: hoje Preta ganha ~6% menos | `hiato_preta_parda_percentual.png` |

## Série "É cor ou é outra coisa?"

| ID | Gancho | Achado | Origem |
|---|---|---|---|
| P03 | "É a ocupação ou é a cor da pele?" | Controlando idade, escolaridade e ocupação, o hiato cai de 67% para 24% — mas não some; Oaxaca-Blinder confirma ~22% (p < 0,001) | `decomposicao_hiato_ocupacional.png`, `oaxaca_blinder_decomposicao.png` |
| P04 | "Piso pegajoso e teto de vidro" | Hiato residual ~31% na base (P10), ~15% na mediana, ~36% no topo (P90) | `oaxaca_blinder_quantis.png` |
| P11 | "Negros trabalham menos horas?" | Jornada parecida (38,8h vs. 37,7h); hiato por hora (~65%) quase igual ao mensal (67%) | `renda_por_hora.png` |
| P15 | "14 anos depois, a parte que não se explica continua lá" | Parcela não explicada do hiato travada em ~46% desde 2012 | `apr_oaxaca_temporal.png` |
| P10 | "Diploma na mão, ocupação elementar" | Sobre-qualificação de Negra quase o dobro da de Branca | `sobrequalificacao.png` |

## Série "Onde cada um está na distribuição"

| ID | Gancho | Achado | Origem |
|---|---|---|---|
| P05 | "R\$3.000 por mês: meio ou topo?" | R\$3.000 é P57 para Branca e P76 para Negra; os 10% mais pobres ganham R\$1.500 (Branca) e R\$720 (Negra) | `percentil_de_valor_racial.png` |
| P06 | "Quem está no topo 10%?" | Negra é ~56% dos ocupados, 33% do topo 10% e 73% da base 10% | `ext_dist_brasil.png` |
| P18 | "Topo e base, por raça e gênero" | Topo 10%: Homem Branco R\$22.219 vs. Mulher Negra R\$8.710; base 10%: R\$943 vs. R\$378 | `ext_renda_raca_sexo_topo10.png`, `ext_renda_raca_sexo_base10.png` |
| P07 | "O topo negro estudou mais. E aí?" | Superior completo no topo 10% negro: 38% → ~58%; no topo branco, ~83% | `topo10_escolaridade.png` |
| P08 | "Quanto mais rico, maior a distância na escola" | Diferença de Superior completo: ~6 p.p. no Q1, ~32 p.p. no Q4 | `quartis_escolaridade.png` |
| P25 | "Desigualdade entre raças ou dentro delas?" | Só ~7% da desigualdade total vem de diferença entre raças; Gini de Branca é maior porque a renda negra é comprimida perto da base — não "situação melhor" | `theil_decomposicao.png`, `gini_por_raca.png` |

## Série "Trabalho"

| ID | Gancho | Achado | Origem |
|---|---|---|---|
| P09 | "No concurso público o hiato é menor" | Hiato ~45-50% no setor público vs. ~58-68% no privado | `hiato_setor_publico_privado.png` |
| P12 | "Carteira assinada, por raça" | Branca 72%, Negra 63%, Indígena 52% | `informalidade_carteira_assinada.png` |
| P14 | "Quem desiste de procurar emprego" | Desalento de Negra e Indígena 2-4× o de Branca | `desalento.png` |
| P23 | "Sair do desemprego rápido nem sempre é boa notícia" | Homens negros saem do desemprego mais rápido (36-38% vs. 33%) por rotatividade em trabalho precário; informal → formal: Indígena a mais baixa (~10,5%) | `docs/ANALISE_RACA_GENERO.md` |

## Série "Gênero e raça juntos"

| ID | Gancho | Achado | Origem |
|---|---|---|---|
| P16 | "Dupla desvantagem: raça + gênero" | Gap Homem Branco ↔ Mulher Negra: raça ~65%, interação ~20%, gênero puro ~15% | `apr_dupla_desvantagem.png` |
| P22 | "O caso da mulher indígena" | Homem Indígena tem o maior efeito-raça isolado; para Mulher Indígena, o termo de interação é o mais negativo | `docs/ANALISE_RACA_GENERO.md` |

## Série "Povos indígenas"

| ID | Gancho | Achado | Origem |
|---|---|---|---|
| P13 | "Alfabetização depois dos 60" | Branca 93%, Negra 80%, Indígena 72% | `alfabetizacao_60mais.png` |
| M02 | "Por que o dado indígena tem mais ressalva" | Amostra de ~2.900 pessoas por trimestre na PNAD; média móvel e agrupamento de trimestres; o Censo (Etapa 2) é a fonte mais robusta | `docs/LIMITACOES_E_METODOLOGIA.md` |

## Série "Políticas públicas"

| ID | Gancho | Achado | Origem |
|---|---|---|---|
| P20 | "As cotas no serviço público mudaram alguma coisa?" | Hiato de renda no setor público encolheu ~2% a mais que no privado após a lei (p = 0,041); Centro-Oeste +5,6% (p = 0,030). Desenho preliminar | `causal_eventstudy_hiato_renda.png`, `docs/ANALISE_CAUSAL_COTAS.md` |
| P21 | "Não achei efeito. Isso quer dizer que não há?" | Cotas universitárias: resultado nulo com tendências paralelas sustentadas; falta poder estatístico, não prova de ausência | `causal_cohortes_universitaria_negra.png` |

## Série "Tendência"

| ID | Gancho | Achado | Origem |
|---|---|---|---|
| P17 | "No ritmo atual, quando o hiato fecha?" | Tendência 2012-26 → ~2104; pós-recessão 2016-26 → ~2073 (ilustrativo, com ressalvas) | `apr_convergencia.png` |

## Série "Como ler este dado" (método)

| ID | Gancho | Conteúdo | Origem |
|---|---|---|---|
| M01 | "Como o IBGE mede raça" | Autodeclaração, 5 categorias, Negra = Preta + Parda, Amarela sempre explicitada | `docs/LIMITACOES_E_METODOLOGIA.md` |
| M03 | "O que é 'estatisticamente significativo'" | Teste de Welch e IC, com o hiato como exemplo | `docs/LIMITACOES_E_METODOLOGIA.md` |
| M04 | "Por que valores 'reais' e não nominais" | Deflator oficial do IBGE, preços de 2026 T2 | `docs/PLANO.md` (bloco 1.1) |
| P24 | "Conferimos nossos números com os do IBGE" | Desocupação, informalidade e hiato reproduzidos dentro de ~1-3 p.p. | `apr_validacao_ibge.png` |
| M05 | "Correlação não é causa" | Quebra estrutural (reformas) vs. desenho causal das cotas | `docs/ANALISE_CAUSAL_COTAS.md` |

## Pautas que dependem de etapas futuras (2027)

| ID | Gancho | Depende de |
|---|---|---|
| F01 | "O ABC Paulista que a PNAD não mostra" | Etapa 2 — Censo 2022 |
| F02 | "Terra indígena, etnia e renda" | Etapa 2 — Censo 2022 |
| F03 | "Saneamento: o hiato que não se vê da rua" | Etapa 3 — Habitação |
| F04 | "Atualização: o hiato no último trimestre" | Extensão — atualização trimestral |
