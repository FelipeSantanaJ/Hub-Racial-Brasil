# Pendências textuais — mapa de dependências (Fase 0, tarefa 0.8)

Gerado em 01/11/2026 no branch `rumo8/fase0` a partir de 862de5f, por varredura LÉXICA (regex por problema do anexo A) em README.md, docs/*.md (raiz), conteudo/**/*.md, texto dos 2 PPTX e nomes dos arquivos em docs/img. **Nenhum texto foi editado** (regra 12 do prompt-mestre; edição só na Fase 8).

Limites: é uma lista de CANDIDATOS. Há falsos positivos (ex.: "explica" em contexto metodológico) e pode haver falsos negativos (frase que depende do problema sem usar os termos). As fases 1–7 acrescentam aqui as linhas que descobrirem, com "por quê" e "frase proposta" (colunas vazias por enquanto). Frases idênticas no mesmo arquivo foram agrupadas.

## Problemas (anexo A)

| Código | Problema | Ocorrências (linhas) |
|---|---|---|
| C1 | manchete 74%→66% (anexo C1; depende de 1, 5, 6) | 9 |
| 1 | degrau 2022T1 / teste de quebra | 28 |
| 2 | G1 +9,0 vs média pré-lei; EMD | 21 |
| 3 | regra assimétrica do G1; M̄; limites juntos | 5 |
| 4 | decomposição em outro estimando; 'explicado' | 75 |
| 5 | reclassificação racial não limitada | 4 |
| 6 | EP sem validação independente; CR1 | 1134 |
| 7 | mediadoras como controles (Oster, C-H, INSE) | 24 |
| 8 | proveniência '-modificado'; Theil 6,67 x 6,96 | 33 |
| 9 | células finas; Indígena PNADC x Censo | 909 |
| 10 | critérios reinterpretados (I1); FDR | 38 |

Total: 1739 linhas/slides/arquivos com ao menos um termo; 1108 frases distintas por arquivo.

## README.md

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| 4 | **branca** e **indígena** no Brasil (Amarela sempre explicitada, nunca descartada) — renda, | 9 | | |
| 24 | erro-padrão (corrigido: ver "O que é validado" abaixo e [docs/auditoria/](docs/auditoria/)). Ondas 1 a 4 do | 6,10 | | |
| 31 | > **Leitura principal (13/10/2026):** o hiato racial de renda caiu de 2012 a 2026, mas **em degrau** (−5 p.p. em | 1 | | |
| 32 | > 2022), não em tendência contínua; desde 2022 ele está plano. Toda tendência do Hub usa erro-padrão robusto a | 6 | | |
| 34 | > erro-padrão corrigido e a população de referência. | 6 | | |
| 41 | recente). A população indígena tem amostra pequena na PNAD Contínua — a linha usa média | 9 | | |
| 49 | O achado mais forte da Etapa 1: o hiato de renda entre Branca e Negra/Indígena não desaparece | 9 | | |
| 57 | Testado trimestre a trimestre a partir dos microdados, com erro-padrão que respeita o desenho | 6 | | |
| 59 | significativos (z entre 19,5 e 37,2) — o hiato caiu de 74,2% (2012 T1) para 65,7% (2026 T2), quase todo num | C1 | | |
| 60 | degrau depois da pandemia (2022), sem tendência contínua de queda ([B1](docs/studies/B1/ficha.md)). O | 1 | | |
| 61 | hiato % é **relativo à renda média Negra** (Branca ganha ~66% a mais; Negra ganha ~60% da | C1 | | |
| 93 | ![Hiato em degrau](docs/img/onda2_b1_degraus_hiato.png) | 1 | | |
| 95 | O hiato Branca × Negra entre ocupados caiu de 74% (2012) para 66% (2026), mas **em degrau**: com o erro-padrão que | C1,1,6 | | |
| 99 | ponto de desocupação, [B5](docs/studies/B5/ficha.md)). A reclassificação racial existiu (mais pessoas se declaram | 5 | | |
| 116 | de renda Branca × Negra (0,43 log-pontos em 2025–26) cai para 0,09: cerca de **78% do hiato está associado a essas | 4 | | |
| 128 | menos carteira assinada, mas são empregadoras 2,4 p.p. menos ([D5](docs/studies/D5/ficha.md)); para indígenas, a | 9 | | |
| 132 | As tabelas antigas (`decomposicao_oaxaca_blinder*`, `decomposicao_hiato_ocupacional` e o gráfico de RIF por quantil) | 4 | | |
| 146 | pais com a mesma escolaridade e renda reduz em cerca de 40% a parte do hiato de renda não associada às características | 9 | | |
| 173 | no trabalho (Censo: 69,7%; PNADC: 66,4%). Para indígenas, o Censo mostra uma diferença bem maior (+117%) que a PNADC, | 9 | | |
| 174 | cuja amostra de indígenas é pequena ([I1](docs/studies/I1/ficha.md)). | 9,10 | | |
| 192 | A Lei de Cotas (Onda 5, [G1](docs/studies/G1/ficha.md)) não tem efeito afirmável com os dados públicos: a proporção de | 2 | | |
| 222 | decomposição do índice de Theil mostra que só ~7% da desigualdade TOTAL de renda no Brasil | 8 | | |
| 242 | Negra=Preta+Parda / Indígena): 11 itens — Raça; ×Gênero; ×Faixa Etária; ×Geração; | 9 | | |
| 245 | Branca vs. Indígena, com teste de Welch. **Cada imagem aparece em exatamente um slide**, e | 6,9 | | |
| 251 | ocupacional/setorial (Duncan), quebra estrutural, novas variáveis (informalidade, | 1 | | |
| 252 | renda/hora, alfabetização, desalento, sobre-qualificação), Gini/Theil, hiato setor | 8 | | |
| 253 | público×privado, decomposição Oaxaca-Blinder/RIF e a função quantil da renda em R$. A | 4 | | |
| 280 | src/inference/ # variância design-based, multiplicidade, gravação com proveniência | 8 | | |
| 340 | ## O que é validado | 10 | | |
| 344 | \| Estimativas pontuais do hiato, Theil, Gini, quantis, topo/base 10% \| Conferidas na auditoria Rodada 1 e idênticas após a correção de 12/10/2026 \| `docs/auditoria/rodada1.md`, `docs/auditoria/antes_depois.md` \| | 8 | | |
| 345 | \| Erro-padrão, IC e p-valores das tabelas de hiato \| **Corrigidos em 12/10/2026** (linearização com Estrato/UPA); razão linearização/bootstrap = 1,005 nos 58 trimestres \| `docs/LIMITACOES_E_METODOLOGIA.md`, `checagem_rob… | 6 | | |
| 348 | \| Desenhos causais (cotas) \| **Não validados**: resultados exploratórios; nenhum teste do Desenho B sobrevive à correção de multiplicidade \| `docs/auditoria/rodada1.md` (R2, R3) \| | 10 | | |
| 360 | - Amostra pequena de Indígena e de células finas; Amarela fora de Theil/Gini. | 8,9 | | |
| 378 | indígena — planejada para 2027 | 9 | | |

## docs/ANALISE_CAUSAL_COTAS.md

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| 4 | decomposições, Gini/Theil, segregação) é descritivo/correlacional, mesmo quando o método é | 8 | | |
| 12 | > FDR de Benjamini-Hochberg**; os menores p ajustados são 0,072 (nacional) e 0,191 | 10 | | |
| 59 | \| Indígena \| -0,14 pp/ano, p=0,86 \| +1,81 pp, p=0,80 \| ver parquet \| | 9 | | |
| 79 | ![Lei de Cotas Universitárias — Branca vs. Indígena](img/causal_cohortes_universitaria_indigena.png) | 9 | | |
| 82 | limiar de 1994 sem nenhum "degrau" visível — consistente com o DiD nulo. Isso é uma leitura | 1 | | |
| 91 | Branca-Negra, controlando por idade/escolaridade/ocupação (Oaxaca-Blinder, mesmo método | 4,7 | | |
| 92 | de `gerar_decomposicao_oaxaca_blinder`), é diferente entre quem nasceu antes ou depois de | 4 | | |
| 100 | O resíduo (o que sobra do hiato mesmo controlando por escolaridade/ocupação/idade) é um | 7 | | |
| 105 | (mesmo controlando por faixa etária, a composição etária dentro de cada faixa pode diferir); | 7 | | |
| 121 | Dois outcomes: (a) participação de Negra/Preta/Parda/Indígena entre ocupados do setor | 9 | | |
| 126 | diferença de médias ponderadas com erro padrão somado em quadratura — porque uma regressão | 6 | | |
| 130 | DiD global) é uma regressão de verdade sobre o microdado, com erro-padrão clusterizado por | 6 | | |
| 131 | UPA — mesmo padrão de `pnadc_core.decomposicao_oaxaca_blinder`. | 4 | | |
| 133 | ### Participação: nenhum efeito significativo, e a identificação FALHA pra Indígena | 9 | | |
| 138 | \| Indígena \| +0,009, p=0,046 \| **NÃO sustentadas** \| +0,039, p=0,07; p_BH=0,16 \| | 9 | | |
| 142 | **Para Indígena, a identificação NÃO se sustenta** — a tendência pré-lei já era | 9 | | |
| 144 | Reportado como está: qualquer leitura do coeficiente de DiD pra Indígena nesse outcome não | 9 | | |
| 154 | ![Participação de Indígena no setor público](img/causal_eventstudy_participacao_indigena.png) | 9 | | |
| 175 | e não ~6, como dizia a versão anterior deste texto. Nenhum sobrevive ao FDR. Um p nominal de | 10 | | |
| 186 | 4. **Erro-padrão da curva.** A soma entre células ainda ignora covariâncias (limitação | 6 | | |
| 194 | `n_minimo` em toda região/área/DF nos dois desenhos; Indígena só fecha em Norte (vs. Resto | 9 | | |
| 209 | Indígena (Norte vs. Resto do Brasil, e área Urbana) tem tendências paralelas sustentadas | 9 | | |
| 231 | sobrevive ao FDR. A versão anterior deste texto chamava o hiato do Centro-Oeste de "efeito | 10 | | |
| 285 | "federal" do resultado nacional** — é um teste de baixo poder (amostra de Indígena no DF | 9 | | |

## docs/ANALISE_FASE1.md

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| 18 | organizado como uma **árvore cruzada** de renda por raça (Branca / Negra / Indígena), sem | 9 | | |
| 53 | Hiato grande e persistente entre Branca e Negra/Indígena ao longo de toda a série. | 9 | | |
| 62 | Com teste de significância estatística (Welch, IC 95%) calculado trimestre a trimestre a | 6 | | |
| 82 | Pergunta: controlando por idade, escolaridade e ocupação, o hiato de renda negros vs. | 7 | | |
| 93 | Idade sozinha quase não explica nada. Escolaridade explica mais da metade do hiato. Ocupação | 4 | | |
| 94 | explica uma fatia adicional — mas **mesmo comparando pessoas da mesma idade, mesma | 4 | | |
| 96 | não explicam. Não é prova direta de discriminação (outros fatores não medidos aqui — horas | 4 | | |
| 100 | **E quanto ocupação SOZINHA explica, sem controlar idade/escolaridade primeiro?** A barra | 4 | | |
| 101 | "Só ocupação (isolado)" no mesmo gráfico responde: o hiato cai de 66% pra **34%** — ou seja, | C1 | | |
| 102 | ocupação por si só (uma única variável) já explica quase tanto quanto idade+escolaridade | 4 | | |
| 112 | **Mesma pergunta, com teste de significância formal** — regressão (Oaxaca-Blinder): | 4 | | |
| 114 | ![Decomposição de Oaxaca-Blinder](img/oaxaca_blinder_decomposicao.png) | 4 | | |
| 121 | ![Hiato residual por quantil](img/oaxaca_blinder_quantis.png) | 4 | | |
| 127 | A mesma barra "só ocupação" aqui: explica **40% do hiato** de log-renda, com significância | 4,9 | | |
| 129 | explicam neste método, mas ainda assim substancial pra uma única variável. | 4 | | |
| 143 | (Branca/Negra/Indígena), célula em branco = amostra insuficiente naquele cruzamento (mais | 9 | | |
| 144 | comum com Indígena, sample menor). | 9 | | |
| 180 | ![Quebra estrutural](img/hiato_quebra_estrutural.png) | 1 | | |
| 182 | Teste tipo Chow (simplificado) nos 3 eventos já mapeados como possíveis pontos de inflexão, | 1 | | |
| 198 | (`informalidade.parquet`, Brasil, 14+): Branca 71,7%, Negra 63,0%, Indígena 48,4%. Militares e | 9 | | |
| 203 | > estatutários (Branca 75,4%, Negra 66,5%, Indígena 53,1% em 2026 T2). Um texto ainda anterior dizia | 9 | | |
| 210 | Indígena, 2026 T2), e o hiato na renda POR HORA (63%) é quase idêntico ao hiato na renda mensal | 9 | | |
| 211 | (66%). O hiato é | C1 | | |
| 217 | Negra vs. 72% Indígena alfabetizados entre 60+ anos (2026 T2). | 9 | | |
| 223 | Negras e 4,1% das Indígenas, contra 2,0% das Brancas. Desalento vai além da taxa de | 9 | | |
| 240 | Baby Boomer oscila bastante (média anual entre 78% e 99%), sem tendência clara; parte dessa | 4 | | |
| 255 | (Indígena fica de fora — amostra insuficiente pra um P90 confiável por trimestre.) | 9 | | |
| 334 | Negra em todos os 58 trimestres (2026 T2: 0,489 vs. 0,423; Indígena 0,440; Amarela, incluída desde a | 9 | | |
| 338 | ![Decomposição de Theil](img/theil_decomposicao.png) | 8 | | |
| 340 | Só ~7% (6,96% em 2026 T2, com Amarela no total desde a Onda 1) da desigualdade TOTAL de renda no Brasil vem de diferença ENTRE raças — os outros 93% | 8 | | |
| 365 | profissional diferente. Indígena tem amostra pequena aqui (poucas pessoas com Superior | 9 | | |
| 459 | R\$5.483 vs. Indígena R\$5.493, Brasil, 2026 T2). | 9 | | |
| 536 | - Indígena tem amostra pequena — séries temporais de raça isolada usam média móvel centrada de 4 | 9 | | |
| 550 | decomposição de Oaxaca-Blinder (incl. por quantil), passaram por teste de significância | 4 | | |
| 551 | formal (Welch e/ou o coeficiente de regressão, respectivamente); as demais comparações | 6 | | |
| 556 | erro padrão inflado por um fator de ~√n em relação ao valor correto — bug puramente de | 6 | | |

## docs/ANALISE_RACA_GENERO.md

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| 1 | # Análise Raça × Gênero — aprofundamento Branca/Negra/Indígena e Preta/Parda | 9 | | |
| 3 | Bloco dedicado a tratar os TRÊS grupos raciais (Branca, Negra, Indígena) em pé de | 9 | | |
| 4 | igualdade metodológica — não só Branca vs. Negra com Indígena como nota de rodapé — e a | 9 | | |
| 21 | ## 1. Levando o toolkit pesado também pra Branca-Indígena e Preta-Parda | 9 | | |
| 23 | ### Oaxaca-Blinder | 4 | | |
| 25 | - **Branca vs. Indígena** (`decomposicao_oaxaca_blinder_indigena.parquet`): controlando | 4,7,9 | | |
| 27 | explicado por essas três características observáveis, **56,7%** é resíduo | 4 | | |
| 29 | ~31% (`exp(0,269)-1`), com p < 0,001 (EP do WLS com cluster por UPA; não passa pela linearização do B1). Comparando com Branca-Negra | 6 | | |
| 32 | explica 32,5% do hiato Branca-Indígena, próximo do que explica pra Branca-Negra. | 4,9 | | |
| 33 | - **Preta vs. Parda** (`decomposicao_oaxaca_blinder_pretaparda.parquet`): decomposto | 4 | | |
| 40 | confiável aqui: controlando por idade+escolaridade+ocupação, o hiato médio Preta-Parda | 7 | | |
| 45 | controlando por X); no P90 (topo), é negativo e significativo (−0,032; Preta < Parda | 7 | | |
| 46 | controlando por X) — um "teto de vidro" especificamente para Preta DENTRO da própria | 7 | | |
| 52 | - **Ocupacional, Branca vs. Indígena** (`segregacao_ocupacional_indigena.parquet`): | 9 | | |
| 56 | de renda Branca-Indígena ser um pouco maior que Branca-Negra. | 9 | | |
| 59 | Branca-Negra/Branca-Indígena (~17%). Preta e Parda têm perfis ocupacionais bem | 9 | | |
| 64 | - **Setorial, Branca vs. Indígena**: **não publicado** — nem agregando os 58 trimestres | 9 | | |
| 70 | - **Branca vs. Indígena, por Região** (`hiato_regional_indigena.parquet`, série | 9 | | |
| 82 | - **Dentro de Indígena** (`perfil_topo10_racial_indigena.parquet`, | 9 | | |
| 83 | `perfil_quartis_racial_indigena.parquet`): só publicável como UMA janela pooled | 9 | | |
| 84 | (últimos 8 trimestres, 2024T3-2026T2) — trimestre a trimestre a amostra de Indígena | 9 | | |
| 91 | Homem Negro, Mulher Negra, Homem Indígena, Mulher Indígena, Homem Preto, Mulher Preta, | 9 | | |
| 113 | \| Mulher Indígena \| 48,5% \| R$2.464 \| R$1.225 \| -R$1.148 \| | 9 | | |
| 114 | \| Homem Indígena \| 47,0% \| R$2.464 \| R$0 \| R$0 \| | 9 | | |
| 122 | 1. **Homem Indígena tem o MAIOR "efeito raça puro" isolado** (R$2.464, maior até que o | 9 | | |
| 124 | forte pra Indígena que pra qualquer recorte de Negra. Ainda assim, o gap TOTAL de | 9 | | |
| 125 | Mulher Indígena (48,5%) fica ABAIXO do de Mulher Preta/Negra/Parda (52-55%) — porque | 9 | | |
| 126 | o termo de interação de Mulher Indígena é o mais negativo de todos (-R$1.148). | 9 | | |
| 129 | efeito-gênero previsse. Isso NÃO significa que ser mulher negra/indígena "não | 9 | | |
| 133 | leitura já aplicado ao Gini/Theil por raça no projeto (ver LIMITACOES). | 8 | | |
| 137 | grupos não-brancos/não-indígenas. | 9 | | |
| 139 | Indígena não precisou de nenhum agrupamento de trimestres aqui — mesmo Indígena×sexo | 9 | | |
| 143 | ## 3. Ritmo de convergência do hiato — Branca-Negra, Branca-Indígena, Preta-Parda | 9 | | |
| 146 | > ao lado); "tendência confiável" = os três IC excluem zero. Branca-Negra: −0,78 p.p./ano (IC −1,25 a −0,32), | 10 | | |
| 147 | > confiável — mas com degraus no modelo a tendência some e a queda é um degrau de −5 p.p. em 2022. Branca-Indígena: | 1,9 | | |
| 157 | \| Branca-Negra \| 65,7% \| -0,78 \| 0,58 \| Sim \| ~84 anos \| | 10 | | |
| 158 | \| Branca-Indígena \| 70,9% \| +0,53 (bruta, p=0,11) / +0,67 (suavizada) \| 0,05 (bruta) / 0,20 (suavizada) \| Só na série suavizada \| — (não converge) \| | 9 | | |
| 164 | - **Branca-Indígena é a série mais ruidosa das três** (menor amostra por trimestre): | 9 | | |
| 166 | versão suavizada (média móvel de 4 trimestres para trás; os gráficos de Indígena | 9 | | |
| 169 | Branca-Indígena está aumentando** até o teste com HAC (Onda 2). Como o hiato está subindo (divergindo), não faz sentido nenhum "anos | 9 | | |
| 192 | sobretudo de Indígena, abaixo do `n_minimo`; ver LIMITACOES). | 9 | | |
| 202 | \| Indígena \| Homem \| 37,6% \| 10,4% \| | 9 | | |
| 203 | \| Indígena \| Mulher \| 24,9% \| 10,7% \| | 9 | | |
| 209 | 1. **Homens negros/pardos/pretos/indígenas SAEM do desemprego mais rápido que homens | 9 | | |
| 218 | grupo não-branco**, e MENOR AINDA pra Indígena (10,4-10,7%, a mais baixa das | 9 | | |
| 221 | trabalhadores negros/indígenas circulam mais rápido por empregos (geralmente | 9 | | |
| 225 | Mesmo Indígena, que era a preocupação central de amostra nesse item, chegou a | 9 | | |

## docs/CHANGELOG_METODOLOGICO.md

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| 8 | ## 20/10/2026 — Depois do plano: gráficos da Onda 6 e Rambachan–Roth no G1 (branch `pos-plano/graficos-onda6-g1`) | 2,3 | | |
| 14 | - **G1 — Rambachan–Roth** (magnitudes relativas, versão conservadora; **análise posterior, não pré-registrada**): M̄ de | 2,3,7 | | |
| 15 | ruptura 0,98 em 2013–2015 e 0,19 em 2016–2019 (`g1_sensibilidade_rr`). A conclusão do G1 não muda. | 1,2 | | |
| 22 | - **Decisões do Felipe (20/10/2026, "sim pra todos"):** fichas D4.4, I1, H3.4 e H4.2 aprovadas com ressalvas; PR #15 | 10 | | |
| 23 | liberado; gráficos da Onda 6 no deck publicado; seguir com os próximos passos (Rambachan–Roth no G1; Censo com | 2,3 | | |
| 32 | 0,21 dentro do município (0,04 por acaso); 70% do Theil entre municípios; a renda dos setores de pessoas brancas é | 8 | | |
| 34 | - **I1** (novo): o Censo 2022 confirma o hiato nacional da PNADC (Branca × Negra 69,7% × 66,4% em 2022, diferença | 10 | | |
| 36 | hiato Branca × Indígena é 117% no Censo × 40% na PNADC — os números indígenas de renda da PNADC são frágeis. | 9 | | |
| 51 | - **Decisões do Felipe (20/10/2026, "está tudo autorizado"):** fichas G6 e G1 aprovadas com ressalvas; G2, G3, G4 e | 2 | | |
| 56 | - **Fichas G1–G6 commitadas antes de rodar** (desenho, efeitos plausíveis e regra "só roda o que tiver poder"). | 2 | | |
| 57 | - **G6 (EMD):** G1 detecta efeitos ≥ 8,5 p.p. na % negra entre declarados (roda com ressalva); G4 (salário mínimo) tem | 2 | | |
| 58 | EMD de β entre 1,45 e 3,4 — não detectaria nem o repasse integral (β = −1) → **não estimado**. | 2 | | |
| 59 | - **G1 (Lei 12.711):** event study com 73 federais sem reserva própria × 40 estaduais/municipais. A % negra entre | 2 | | |
| 60 | declarados sobe +9,0 p.p. (IC 3,0 a 15,1) em 2016–2019, mas a % sem cor declarada cai 22,5 p.p. e a versão | 2 | | |
| 83 | - **Principais achados:** no 9º ano, estudantes negros têm proficiência 0,42 DP abaixo dos brancos; com o mesmo INSE e na | 7 | | |
| 125 | vínculo, ocupação e atividade; Gelbach e Shapley; OB de Reimers; RIF-OB; Oster e Cinelli-Hazlett). As tabelas | 7 | | |
| 126 | `decomposicao_oaxaca_blinder*` e `decomposicao_hiato_ocupacional` (3 controles) **não mudam** e ficam para | 4 | | |
| 133 | - **Principais achados (Branca × Negra, ocupados com renda, 2025T3–2026T2):** ~78% do hiato (0,427 lp) associado às | 4 | | |
| 135 | ganhou (14% → 19%); parte não associada 0,094 lp, parada desde 2012 e **frágil** a omitidas (Oster δ = 0,85); hiato | 7 | | |
| 138 | controles, pessoas negras não têm menos carteira, mas são empregadoras 2,4 p.p. menos; indígenas seguem com menos | 9 | | |
| 150 | a leitura "degrau em 2022, sem tendência contínua" passa a ser a principal do Hub (README e deck); C6 feito | 1 | | |
| 153 | premissa na tela), substituída pela projeção condicional do B6; legenda da quebra estrutural no deck corrigida | 1 | | |
| 172 | zero (antes: R² ≥ 0,1). Inclinações pontuais iguais; Branca × Indígena segue sem tendência confiável; no teste tipo | 9 | | |
| 173 | Chow (com BH entre os 3 eventos) a **reforma da previdência deixa de ser significativa**; o coeficiente de patamar | 1 | | |
| 174 | passa a medir o salto na data do evento. Saem da tabela de ritmo a série suavizada de Branca × Indígena e o "anos | 9 | | |
| 178 | - **Principais achados:** a queda do hiato P1 foi um degrau de −5 p.p. em 2022, não tendência contínua (B1); o | 1 | | |
| 179 | hiato entre todos os adultos é contracíclico (+1,6 p.p. por p.p. de desocupação, B5); a reclassificação racial | 5 | | |
| 199 | com defasagem 4 cobre só ≈ 78% (nominal 95%) com AR(1) de 0,7 em 58 trimestres. Adotado o EWC (cossenos com pesos | 4 | | |
| 205 | - **F4:** o % de rendas em múltiplos de R$ 1.000 dobrou (17% → 40%) por **composição nominal** (+29,5 p.p.), não | 9 | | |
| 210 | do deck são suprimidos (3 casos: mulheres sem instrução, hiato vs. Indígena/Negra). | 9 | | |
| 238 | por quantil com bootstrap Rao-Wu; Theil L; representação por décimo e razão de chances (topo 10%: 0,32); dominância | 8 | | |
| 256 | 14+ do indicador. Renda por hora: `VD4016` ÷ horas do trabalho principal (`V4039`). Gini e Theil | 8 | | |
| 262 | trimestres seguem significativos após o FDR (z de 19,5 a 37,2). Branca × Indígena 2026T2: 72,7 → | 9,10 | | |
| 263 | 70,9%. Theil entre raças 6,67 → 6,96%. Resíduo de Oaxaca-Blinder (3 controles) 22,4 → 22,8%. | 4,8 | | |
| 295 | hiato Branca × Indígena (inclinação bruta p = 0,11; só a série suavizada sobe, sem HAC). No Desenho B das | 9 | | |
| 296 | cotas, o hiato de renda nacional passa a p = 0,014 (p_BH = 0,072) — segue sem sobreviver ao FDR. | 10 | | |
| 343 | das células nacionais e 40% das de UF de `renda.parquet` tinham n < 30. | 9 | | |
| 355 | `gerar_perfil_topo10_quartis_pretaparda`, `gerar_perfil_topo10_quartis_indigena`, | 9 | | |
| 384 | - **Impacto previsto** (prévia sem gravar parquet, Brasil, 14+): em 2026T2, Branca/Negra/Indígena | 9 | | |
| 387 | (Negra; −3,52 a −4,93) e −5,04 p.p. (Indígena; −3,21 a −8,57). A diferença Branca–Negra em | 9 | | |
| 394 | denominador explícito (2,0/4,5/4,1% para Branca/Negra/Indígena, 2026T2). A carteira passa a | 9 | | |
| 398 | que são 40 testes de DiD (5 + 35) e que 0 sobrevivem ao FDR, e inclui os dois p < 0,05 de | 10 | | |
| 407 | - **C6**: "proxy de discriminação" sai das docstrings de `decomposicao_oaxaca_blinder` e | 4 | | |
| 408 | `gerar_oaxaca_blinder_temporal` e do subtítulo em `graficos_aprofundamentos.py`. O resíduo passa | 4 | | |
| 434 | Passam a usar essa definição: `hiato_racial`, `gini_por_raca`, `theil_racial`, os três | 8 | | |
| 435 | `decomposicao_oaxaca_blinder*` e `checagem_robustez_hiato`. Gini e Theil ficam na mesma | 4,8 | | |
| 448 | ### Proveniência padronizada | 8 | | |
| 452 | `src/utils/catalogo_tabelas.py`), período, família do FDR. Para as tabelas atuais o meta foi | 10 | | |
| 468 | ### B1 — Erro-padrão design-based (corrige E1) | 6 | | |
| 471 | `tabela_hiatos_significancia` passam a calcular a variância por **linearização de Taylor com | 6 | | |
| 481 | (45–82×); razão EP linearização / bootstrap Rao-Wu Estrato-UPA mediana **1,005** | 6 | | |
| 490 | ### B3 — Welch, multiplicidade, Theil, deflator (E2, E3, E4, R3, R7) | 6,8 | | |
| 492 | - **Welch (E2).** Graus de liberdade com o EP **da média** | 6 | | |
| 496 | normal é desprezível; pesa em células finas (Indígena). | 9 | | |
| 502 | - **Theil/Gini (E3).** Docstring do Theil corrigida: a função de Gini **não** exclui zeros. Em | 8 | | |
| 509 | ### B2 — Proveniência e regeneração | 8 | | |
| 512 | `commit`, família do FDR e data. Os que usam inferência de regressão do statsmodels (que **não** | 10 | | |
| 523 | diferença com covariância, bootstrap × linearização, UPA única, Welch, FDR, Gini/Theil com | 6,8,10 | | |
| 524 | zeros, Oaxaca-Blinder com resposta conhecida, remoção do deflator, **guarda que falha se o | 4 | | |

## docs/LIMITACOES_E_METODOLOGIA.md

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| 16 | Amarela, Parda, Indígena, Ignorado. `data/processed/*.parquet` mantém essas 6 categorias | 9 | | |
| 22 | análise é Branca/Negra/Indígena — mas ambos têm amostra pequena (Amarela ~0,4% da amostra, | 9 | | |
| 25 | ## Amostra pequena para população Indígena | 9 | | |
| 27 | Autodeclaração indígena é ~0,6% da amostra da PNAD Contínua (ex.: ~2.900 registros em 521 mil | 9 | | |
| 29 | Cruzamentos mais finos (ex.: mulheres indígenas de 60+ anos numa UF específica) podem ter | 9 | | |
| 33 | só o denominador do indicador. O Censo Demográfico (Etapa 2) tem quesito e cobertura dedicados à população indígena | 9 | | |
| 34 | (incl. terras indígenas) e deve ser tratado como fonte mais robusta para esse recorte | 9 | | |
| 50 | - **CV.** Erro-padrão design-based (linearização de Taylor com Estrato e UPA, | 6 | | |
| 94 | ver `docs/PLANO.md` para os detalhes de onde ele vem e como foi validado), a preços do | 10 | | |
| 129 | descontínua, gerando um "degrau" na população total estimada (`SUM(V1028)`) em algum | 1 | | |
| 134 | suaviza essas revisões retroativamente em vez de aplicar um degrau, ou o efeito aparece em | 1 | | |
| 143 | possivelmente com efeito desigual entre raças — checado no bloco de quebra estrutural. | 1 | | |
| 155 | ## Aprofundamento estatístico: Oaxaca-Blinder, RIF, segregação, quebra estrutural | 1,4 | | |
| 158 | > E0–E8, Gelbach com EP que inclui a incerteza de β, Shapley, RIF-OB com três bandas, Oster e Cinelli-Hazlett). O que | 7 | | |
| 159 | > segue descreve a implementação antiga (`pnadc_core.decomposicao_oaxaca_blinder`, 3 controles), mantida para | 4 | | |
| 163 | - **Decomposição de Oaxaca-Blinder** (`pnadc_core.decomposicao_oaxaca_blinder`): os pesos | 4 | | |
| 165 | inicial, o erro-padrão do teste de significância (`residuo_restrito_erro_padrao`) vinha | 6 | | |
| 169 | completo: o Estrato não entra no `cov_type='cluster'` (e os pesos replicados existem nos | 6 | | |
| 171 | - **Correção de 12/10/2026 — erro-padrão dos hiatos** (`pnadc_core.tabela_hiatos_significancia`, | 6 | | |
| 189 | - **Método atual:** linearização de Taylor com Estrato e UPA (`src/inference/variancia.py`), | 6 | | |
| 193 | razão linearização/bootstrap tem mediana **1,005** (mín. 0,944; máx. 1,047) | 6 | | |
| 198 | mediana da série) e as flags de significância de células finas; ver | 9 | | |
| 202 | - Pesos replicados (`V1028001`–`V1028200`) existem nos microdados do IBGE, mas não estão | 6 | | |
| 208 | > - **Hiato histórico por Welch** (`pnadc_core.tabela_hiatos_significancia`, usada em | 6 | | |
| 209 | > `gerar_hiato_racial` e toda a família de hiatos): mesma limitação do Oaxaca-Blinder acima | 4 | | |
| 211 | > Welch aqui é calculado à mão, não via regressão. Checagem de robustez feita | 6 | | |
| 215 | > `data/processed/checagem_robustez_hiato_racial.parquet`): o erro-padrão bootstrap ficou | 6 | | |
| 216 | > **54×-90× maior** (média 67×) que o erro-padrão em produção — bem mais dramático que a | 6 | | |
| 217 | > inflação de 2-3× vista no Oaxaca-Blinder. Causa identificada (não é bug): renda tem cauda | 4 | | |
| 222 | > do que a fórmula fechada (que nunca trata UPA como bloco) ou do que um erro-padrão | 6 | | |
| 225 | > trimestres continuam significativos** mesmo sob esse erro-padrão muito mais conservador — | 6 | | |
| 226 | > o hiato (~R\$1.750-2.040) segue de longe maior que o erro-padrão bootstrap (~R\$55-90). | 6 | | |
| 228 | > significância resiste a um método de erro-padrão bem mais rigoroso. | 6 | | |
| 233 | - **Teste de quebra estrutural** (`agregacoes_pnadc.gerar_quebra_estrutural`): é um teste de | 1 | | |
| 234 | Chow simplificado — uma quebra conhecida a priori (a data do evento), testada isoladamente | 1 | | |
| 241 | — Indígena fica de fora (amostra pequena demais pra uma distribuição de 11 categorias | 9 | | |
| 259 | **Os números publicados caem:** em 2026T2, Branca/Negra/Indígena passam de 75,4/66,5/53,1% para | 9 | | |
| 261 | (Indígena). `transicao_informal_formal` mantém o sentido: "formal" em t1 = CLT ou | 9 | | |
| 319 | ## Gini/Theil por raça, setor econômico e sobre-qualificação | 8 | | |
| 326 | - **Theil T, decomposição entre/dentro**: `pnadc_core.decomposicao_theil_entre_dentro` | 8 | | |
| 328 | T_entre ponderado pela participação populacional de cada grupo). Validada com 3 casos | 10 | | |
| 331 | total; um único grupo → decomposição bate exatamente com o `theil_t` calculado direto. | 8 | | |
| 334 | demográficos amplos como raça/gênero tipicamente explicam uma fatia pequena da | 4 | | |
| 350 | amplo, mas não entra nesse indicador). Indígena tem amostra pequena aqui (poucas pessoas | 9 | | |
| 368 | `decomposicao_oaxaca_blinder.parquet`, controles=`grupamento_ocupacional` sem mais nada): | 4 | | |
| 371 | Resultado: hiato bruto 67,0% → 33,4% controlando só por ocupação (padronização direta); | 7 | | |
| 372 | 40,4% de "% explicada" via Oaxaca-Blinder (p<0,001) — em ambos os métodos, ocupação sozinha | 4 | | |
| 373 | explica quase tanto quanto idade+escolaridade JUNTAS. | 4 | | |
| 383 | ## Seção "Renda média" do PPT: hiato multidimensional com Welch | 6 | | |
| 389 | dois, a combinação "Raça" sozinha, seguem sendo série histórica completa). Rodar Welch por | 6 | | |
| 453 | (Bonferroni, FDR/Benjamini-Hochberg). Isso é uma limitação conhecida, não uma omissão: | 10 | | |
| 463 | - **Onde a ressalva pesa mais**: cortes com amostra pequena (Indígena em geral, células | 9 | | |
| 466 | ("Amostra pequena para população Indígena" etc.). A ausência de correção formal nesses | 9 | | |
| 473 | ## Aprofundamento raça×gênero: Branca-Indígena e Preta-Parda em pé de igualdade | 9 | | |
| 476 | amostra novas encontradas ao levar o toolkit pesado (Oaxaca-Blinder, segregação de Duncan, | 4 | | |
| 477 | hiato regional, topo10/quartis) pros pares Branca-Indígena e Preta-Parda: | 9 | | |
| 479 | - **Segregação setorial (VD4010) Branca-Indígena: não publicada.** Mesmo agrupando os 58 | 9 | | |
| 484 | - **Indígena: pooled snapshot em vez de série trimestral, em três lugares novos.** | 9 | | |
| 485 | Segregação ocupacional Branca-Indígena (`segregacao_ocupacional_indigena.parquet`) e | 9 | | |
| 486 | topo10%/quartis dentro de Indígena (`perfil_topo10_racial_indigena.parquet`, | 9 | | |
| 487 | `perfil_quartis_racial_indigena.parquet`) só publicam UMA janela (últimos 8 trimestres, | 9 | | |
| 488 | mesmo padrão já usado em `gerar_decomposicao_oaxaca_blinder_indigena` e | 4,9 | | |
| 492 | pessoas indígenas/trimestre entregam isoladamente). | 9 | | |
| 494 | envolvendo Indígena precisou de pooling. Hiato regional Branca-Indígena por Região | 9 | | |
| 495 | (`hiato_regional_indigena.parquet`) e a decomposição raça×gênero | 9 | | |
| 497 | agrupamento — a amostra de Indígena só fica pequena demais quando o corte abre uma | 9 | | |
| 500 | - **Oaxaca-Blinder Preta-Parda: "% do hiato explicado" sai instável, não é bug.** O hiato | 4 | | |
| 502 | parcela-explicada/não-explicada por um `hiato_total` perto de zero produz percentuais | 4 | | |
| 504 | (`decomposicao_oaxaca_blinder_pretaparda.parquet`). O coeficiente residual em | 4 | | |
| 508 | ANALISE_RACA_GENERO.md. Ao reportar Oaxaca-Blinder pra qualquer par com hiato bruto | 4 | | |
| 523 | inteiro (2012-2026), Brasil apenas — mesmo Indígena, que era a preocupação central de | 9 | | |
| 530 | suficiente quando o hiato é positivo (caso Branca-Negra/Branca-Indígena), mas quebra | 9 | | |
| 566 | (R²=1, todo grau de liberdade consumido) e o erro padrão sai indefinido (aviso de | 6 | | |
| 571 | sobre o microdado, com erro-padrão clusterizado por UPA. Lição geral: rodar uma | 6 | | |
| 572 | regressão com uma dummy por período só tem erro-padrão válido se cada célula | 6 | | |
| 608 | causais. Indígena só fecha em Região Norte (as outras 4 regiões chegam a n=1 por | 9 | | |
| 611 | — testado como Norte vs. Resto do Brasil (2 categorias, não 5) e só Urbana; Indígena no | 9 | | |

## docs/PLANO.md

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| 34 | validados e publicados nela — nunca gera número próprio. O plano completo da árvore de | 10 | | |
| 46 | \| 2 \| Censo Demográfico 2022 — recorte abaixo do município (Área de Ponderação), moradia, recorte indígena \| ⏳ não iniciada \| planejada para 2027 (T1-T2) \| | 9 | | |
| 77 | (Preta + Parda) e **Indígena** — com Amarela sempre explicitada nas tabelas, nunca | 9 | | |
| 91 | \| 1.4 \| Decomposição do hiato: padronização direta, Oaxaca-Blinder, RIF por quantil \| ✅ \| | 4 | | |
| 92 | \| 1.5 \| Distribuição: geração, topo 10%, quartis, função quantil em R$, Gini/Theil \| ✅ \| | 8 | | |
| 94 | \| 1.7 \| Aprofundamentos: instabilidade de renda, retorno da escolaridade, Oaxaca-Blinder ano a ano, dupla desvantagem, convergência, validação cruzada com o IBGE \| ✅ \| | 4 | | |
| 95 | \| 1.8 \| Três grupos em pé de igualdade: Branca-Indígena, Preta-Parda, decomposição raça × gênero, painel rotativo \| ✅ \| | 9 | | |
| 117 | - Distribuição racial (V2010, 2026 T2): Branca 39,2% · Parda 50,2% · Preta 9,6% · Indígena | 9 | | |
| 118 | 0,6% · Amarela 0,4% · Ignorado ~0% — confirma a amostra pequena de Indígena (~2.900 | 9 | | |
| 132 | **Recortes** (`src/utils/pnadc_core.py`): estatística ponderada (média, erro padrão, IC, | 6 | | |
| 133 | coeficiente de variação), teste de Welch, Gini ponderado, recortes raciais e de gênero, | 6 | | |
| 167 | (Indígena com média móvel de 4 trimestres) e os cortes por gênero, faixa etária e nível de | 9 | | |
| 171 | categórica validada para contraste e daltonismo. | 10 | | |
| 188 | - Hiato com teste de Welch em todas as 24 combinações da seção "Renda média" | 6 | | |
| 192 | significativos a 95%; o hiato caiu de ~76% para ~66% entre 2012 e 2026. | C1 | | |
| 197 | ### 1.4 Decomposição do hiato: ocupação explica, ou é cor da pele? | 4 | | |
| 199 | Pergunta: controlando por idade e escolaridade, o hiato existe porque negros e brancos | 7 | | |
| 212 | **Oaxaca-Blinder** (`pnadc_core.decomposicao_oaxaca_blinder`, twofold, coeficientes de | 4 | | |
| 214 | resíduo; erro padrão clusterizado por UPA): | 6 | | |
| 225 | **Ocupação sozinha**: leva o hiato de 67,0% para **33,4%** (padronização direta) e explica | 4 | | |
| 226 | **40,4%** no Oaxaca-Blinder (p < 0,001) — quase tanto quanto idade + escolaridade juntas. | 4 | | |
| 237 | validadas com dados sintéticos de parâmetros conhecidos antes de rodar nos dados reais. | 10 | | |
| 253 | - **Função quantil em R\$ e sua inversa** (`percentil_ponderado_de_valor`, validada por | 10 | | |
| 257 | - **Gini e Theil**: Branca tem Gini mais alto que Negra (distribuição negra mais comprimida | 8 | | |
| 267 | - **Hiato por Região** (`hiato_regional.parquet`, Welch trimestre a trimestre). | 6 | | |
| 272 | - **Informalidade**: % com carteira Branca 72%, Negra 63%, Indígena 52% (2026 T2). | 9 | | |
| 275 | - **Alfabetização 60+**: Branca 93%, Negra 80%, Indígena 72%. | 9 | | |
| 276 | - **Desalento**: Negra e Indígena desistem de procurar emprego a taxas 2-4× a de Branca. | 9 | | |
| 279 | - **Quebra estrutural** (OLS com dummy pós-evento + interação com tendência): | 1 | | |
| 299 | \| 7 \| Oaxaca-Blinder + RIF ano a ano \| `oaxaca_blinder_temporal.parquet` \| **parcela não-explicada travada em ~46% há 14 anos**, apesar da escolaridade de negros subir \| | 4 | | |
| 319 | Regra para Indígena: destravar amostra pequena agrupando trimestres antes de descartar um | 9 | | |
| 323 | 1. **Toolkit completo para Branca-Indígena e Preta-Parda**: Oaxaca-Blinder, segregação de | 4,9 | | |
| 324 | Duncan, hiato regional, topo 10% e quartis. Só a segregação **setorial** Branca-Indígena | 9 | | |
| 329 | Homem Branco): Homem Indígena tem o maior efeito-raça isolado, mas o termo de interação | 9 | | |
| 330 | de Mulher Indígena é o mais negativo. | 9 | | |
| 332 | lentamente (~78 anos, extrapolação ingênua); Branca-Indígena e Preta-Parda estão | 9 | | |
| 336 | ~68%. Homens negros, pardos, pretos e indígenas saem do desemprego mais rápido que | 9 | | |
| 338 | transição informal → formal (Indígena a mais baixa, ~10,5%) conta a história oposta. | 9 | | |
| 352 | p=0,86), sem efeito de nível (p=0,97 Negra, p=0,80 Indígena). "Não detectei efeito" não é | 9 | | |
| 356 | para Indígena (p=0,046 no pré-lei). Hiato de renda: o resultado mais bem identificado — | 9 | | |
| 370 | 1. **Erro padrão clusterizado por UPA** nos três modelos do Oaxaca-Blinder: coeficientes | 4,6 | | |
| 371 | idênticos, erro padrão entre 1,8× e 4,4× maior; nenhuma das 67 linhas testadas muda de significância | 6 | | |
| 375 | Welch: erro padrão 54×-90× maior (média 67×), puxado por UPAs com rendas extremas | 6 | | |
| 387 | quantil, casos sintéticos de Theil, erro padrão ponderado contra s/√n e guarda contra | 6,8 | | |
| 404 | Branca vs. Indígena, em slides separados (a série de Indígena usa média móvel de 4 | 9 | | |
| 405 | trimestres), sempre com Welch. Homens em linha tracejada, mulheres em linha sólida. | 6 | | |
| 416 | linha por folha de renda da árvore, renda Branca/Negra/Indígena em 2012 T1 e 2026 T2. Negra | 9 | | |
| 446 | identificáveis na PNAD Contínua pública. Quesito dedicado à população indígena (etnia, | 9 | | |
| 447 | terra indígena), mais robusto que a PNAD. | 9 | | |
| 477 | \| 6 \| Recorte indígena expandido (etnia, terra indígena) \| 2h \| ⏳ \| | 9 | | |
| 511 | \| 4 \| Hiato racial e racial × gênero ano a ano, com Welch; corte regional \| ⏳ \| | 6 | | |
| 557 | já validados, produção piloto, calendário de postagens com lançamento em **21/03/2027** (Dia | 10 | | |
| 571 | - **Amostra Indígena pequena e de alta variância** na PNAD — agrupar trimestres quando | 9 | | |

## docs/PLANO_DE_ANALISE.md

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| 3 | **Versão 1.0 · 12/10/2026 · VALIDADO pelo Felipe (com as decisões abaixo)** | 10 | | |
| 16 | \| Origem social e mobilidade (H) \| **Entra agora**, não "fase posterior" \| Onda 4, junto com E (compartilham a ligação filhos–pais) \| | 7 | | |
| 21 | 2. EP por **linearização de Taylor (Estrato/UPA)**; pesos replicados não extraídos por ora (extratores aceitam `--pesos-replicados`). | 6 | | |
| 24 | 5. **Sem vínculo institucional:** RAIS identificada e SEDAP/INEP ficam **fora de alcance**. G1/E6 só com dados públicos simplificados do INEP (sem raça por aluno); D3.5/D8.2 (dentro da firma) só com literatura. | 2 | | |
| 31 | 3. Família do FDR: **padrão = comparações de uma tabela no mesmo período e na mesma abertura** | 10 | | |
| 33 | tendências usam HAC, não FDR sobre trimestres (`src/inference/multiplicidade.py`). | 10 | | |
| 41 | 4. Theil e Gini passam a incluir **Amarela** no total (A4). | 8 | | |
| 52 | empregados 01–07 (aceito). **As análises principais do Hub são sempre Branca × Negra e Indígena**; | 9 | | |
| 101 | \| F1 \| **Quem é "Negra", "Branca", "Indígena", "Amarela"?** Como a composição declarada mudou 2012–2026 (reclassificação de pardos, Censo 2022)? \| D \| Autodeclaração é fluida. A mudança de composição altera a *média do g… | 5,9 | | |
| 103 | \| F3 \| **Quem entra na população?** **Decidido:** ocupados com rendimento do trabalho principal > 0 \| D \| Gini e Theil na mesma população (resolve E3/R1). Exclusões medidas no Bloco S \| | 8 | | |
| 105 | \| F5 \| **Incerteza correta:** variância *design-based* (Estrato/UPA), pesos replicados se existirem, correção de multiplicidade \| — \| É o B1 da auditoria. \| | 6 | | |
| 121 | \| A4 \| **Quanto da desigualdade total é entre raças?** \| D \| Theil T e L (MLD) entre/dentro; Gini \| Theil ≈ 7% ≠ "só 7% é racial" (regra do projeto). Incluir sempre o par de contexto \| | 8 | | |
| 137 | \| B2 \| A tendência é **efeito de composição ou de renda**? (A composição racial e educacional mudou) \| C \| Decomposição no tempo: Kitagawa–Oaxaca–Blinder; Juhn-Murphy-Pierce; RIF no tempo \| Reclassificação racial (F1) po… | 4,5 | | |
| 143 | **Já existe:** série do hiato (B1 parcial, sem HAC), Theil no tempo, coortes de superior completo. **Novo:** B2, B3, B4 formal, B5, B6. | 8 | | |
| 154 | \| C2 \| **O hiato de gênero é igual dentro de cada raça?** O hiato racial é igual dentro de cada gênero? \| D/C \| Modelo com interação; decomposição por célula \| Efeitos de interação precisam de n suficiente (Indígena) \| | 9 | | |
| 173 | \| S0.2 \| A probabilidade de estar em (a) difere por raça e por raça × gênero, controlando por idade, escolaridade e região? \| C \| Logit/probit ponderado, efeitos marginais, IC *design-based* \| | 7 | | |
| 190 | Fazer o teste: por raça (Branca × Negra, e também Preta × Parda × Indígena × Amarela quando a amostra permitir, com nota de amostra) e por raça × gênero (4 células), **no tempo** (série 2012–2026), e por quantil (o efeit… | 9 | | |
| 210 | \| T1 \| Renda domiciliar per capita por raça e por raça × gênero do responsável \| D \| Médias, quantis, Gini, Theil (população: todas as pessoas) \| A unidade é o domicílio; compartilhar renda entre membros altera a leitura… | 8 | | |
| 227 | \| D1.1 Qual fração do hiato (em log-renda) desaparece ao comparar pessoas com mesma idade, escolaridade, ocupação, região, jornada, informalidade, sexo? \| Oaxaca-Blinder (Reimers) **em especificações aninhadas** (6–8) \| … | 4 | | |
| 230 | \| D1.4 O resultado é robusto a variáveis omitidas? \| Sensibilidade de Oster (δ), Cinelli-Hazlett \| Quantifica *quão forte* uma omissão teria que ser para anular a conclusão \| | 7 | | |
| 274 | \| D5.3 Qual a **probabilidade** de cada grupo estar em cada posição, condicional a educação? \| C \| Logit multinomial, DFL \| | 4 | | |
| 294 | \| D8.1 Qual é a faixa plausível do resíduo, dado o que não observamos? \| Intervalos de Oster/Cinelli-Hazlett \| | 7 | | |
| 310 | \| E3 \| **Qualidade**: aprendizado difere (ou só anos de escola)? \| D \| Proficiência por raça controlada por NSE (indicador de nível socioeconômico) \| **SAEB** (microdados INEP) \| | 7 | | |
| 327 | \| G1 \| **Lei 12.711 (cotas)** aumentou o ingresso de estudantes Negros em instituições federais? \| Q \| DiD moderno com adoção escalonada (Callaway-Sant'Anna, Sun-Abraham) *confirmar*; ou descontinuidade onde houver nota … | 2 | | |
| 332 | \| G6 \| Poder estatístico: qual efeito mínimo detectável cada desenho tem? \| Pré-requisito \| Cálculo prévio (MDE) \| — \| Se o EMD for maior que efeitos plausíveis, **não rodar** e dizer isso \| | 2 | | |
| 334 | **Regras de comunicação:** "efeito não detectado" ≠ "cotas não funcionam"; todo resultado causal carrega IC, EMD e pré-registro do desenho. | 2 | | |
| 358 | \| H2.2 \| Quanto do hiato de D1 **diminui** ao controlar pela origem? \| C \| Resíduo antes/depois do controle de origem \| Se não diminui, a origem observada não explica o resíduo; se diminui, parte do "resíduo" era herança… | 4 | | |
| 388 | \| Censo 2022 \| D4.4, E7, segregação, indígenas em amostra grande \| Agregados por setor e microdados da amostra (acesso público, só UF) no FTP do IBGE: em uso na Onda 6 (verificado em 20/10/2026); município/área de ponder… | 9 | | |
| 389 | \| Censo da Educação Superior (INEP) \| E6, G1 \| Não iniciado \| | 2 | | |
| 408 | \| **5** \| Bloco G (políticas, com dado administrativo) \| EMD calculado por desenho; só rodar o que tiver poder \| | 2 | | |
| 409 | \| **6** \| Integração (Censo 2022 se destravado, riqueza via fontes externas, H3.4, H4.2) \| Fichas D4.4, I1, H3.4 e H4.2 com resultados; mapa de cobertura atualizado (definido em 20/10/2026, ao abrir a Onda 6) \| | 10 | | |
| 431 | 4. ~~Limite mínimo de amostra por célula para raça × gênero × Indígena/Amarela (definir regra de supressão).~~ **Fechado em 13/10/2026 (Ponto de parada 3):** n < 30 no denominador do indicador **ou** CV design-based > 30… | 9 | | |

## docs/PROXIMOS_PASSOS.md

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| 15 | > (branca, preta, parda, amarela, indígena, não informada), **órgão** e **cargo/carreira**, e, quando disponível, se o | 9 | | |
| 24 | Os microdados públicos só identificam a UF e trazem a idade em faixas de 5 anos (ficha I1). O hiato de renda por | 10 | | |
| 25 | município, a segregação combinada com renda individual e indígenas por território exigem o arquivo de **acesso | 9 | | |
| 33 | - **G1 — Rambachan–Roth (magnitudes relativas):** feito como análise posterior, não pré-registrada (ficha G1, 10b). O | 2,3,7 | | |
| 41 | - **G1 com o FLCI exato** de Rambachan–Roth (pacote `HonestDiD`, em R) — mais estreito que a versão conservadora. | 2,3 | | |
| 44 | - **Hiato indígena:** usar o Censo 2022 (I1) como referência em vez da PNADC em todas as peças públicas. | 9,10 | | |

## conteudo/CALENDARIO_2027.md

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| 27 | \| 19/04 \| segunda \| Dia dos Povos Indígenas \| | 9 | | |
| 30 | \| 09/08 \| segunda \| Dia Internacional dos Povos Indígenas \| | 9 | | |
| 38 | \| abr \| Como ler o dado + povos indígenas \| M01, M02, P13, P12 \| | 9 | | |
| 56 | \| 4 \| 13/04 \| 16/04 \| M02 — "Por que o dado indígena tem mais ressalva" \| **Seg 19/04**: card Dia dos Povos Indígenas \| | 9 | | |
| 71 | \| 19 \| 27/07 \| 30/07 \| P22 — "O caso da mulher indígena" \| \| | 9 | | |
| 72 | \| 20 \| 03/08 \| 06/08 \| P04 — "Piso pegajoso e teto de vidro" \| **Seg 09/08**: card Dia Internacional dos Povos Indígenas \| | 9 | | |
| 80 | \| 28 \| 28/09 \| 01/10 \| P15 — "14 anos depois, a parte que não se explica continua lá" \| **C5**: 2ª revisão trimestral \| | 4 | | |
| 86 | \| 34 \| 09/11 \| 12/11 \| F02 — Recorte indígena do Censo (Etapa 2) · reserva: P13 com os demais indicadores indígenas \| \| | 9 | | |

## conteudo/PAUTAS.md

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| 17 | \| P01 \| "Em 14 anos, o hiato de renda caiu. Quanto?" \| Hiato Branca vs. Negra de ~76% para ~66% (2012-2026); os 58 trimestres são estatisticamente significativos \| `docs/img/hiato_racial_percentual.png`, `renda_por_raca.… | C1 | | |
| 26 | \| P03 \| "É a ocupação ou é a cor da pele?" \| Controlando idade, escolaridade e ocupação, o hiato cai de 67% para 24% — mas não some; Oaxaca-Blinder confirma ~22% (p < 0,001) \| `decomposicao_hiato_ocupacional.png`, `oaxac… | 4,7 | | |
| 27 | \| P04 \| "Piso pegajoso e teto de vidro" \| Hiato residual ~31% na base (P10), ~15% na mediana, ~36% no topo (P90) \| `oaxaca_blinder_quantis.png` \| | 4 | | |
| 29 | \| P15 \| "14 anos depois, a parte que não se explica continua lá" \| Parcela não explicada do hiato travada em ~46% desde 2012 \| `apr_oaxaca_temporal.png` \| | 4 | | |
| 41 | \| P25 \| "Desigualdade entre raças ou dentro delas?" \| Só ~7% da desigualdade total vem de diferença entre raças; Gini de Branca é maior porque a renda negra é comprimida perto da base — não "situação melhor" \| `theil_dec… | 8 | | |
| 48 | \| P12 \| "Carteira assinada, por raça" \| Branca 72%, Negra 63%, Indígena 52% \| `informalidade_carteira_assinada.png` \| | 9 | | |
| 49 | \| P14 \| "Quem desiste de procurar emprego" \| Desalento de Negra e Indígena 2-4× o de Branca \| `desalento.png` \| | 9 | | |
| 50 | \| P23 \| "Sair do desemprego rápido nem sempre é boa notícia" \| Homens negros saem do desemprego mais rápido (36-38% vs. 33%) por rotatividade em trabalho precário; informal → formal: Indígena a mais baixa (~10,5%) \| `doc… | 9 | | |
| 57 | \| P22 \| "O caso da mulher indígena" \| Homem Indígena tem o maior efeito-raça isolado; para Mulher Indígena, o termo de interação é o mais negativo \| `docs/ANALISE_RACA_GENERO.md` \| | 9 | | |
| 59 | ## Série "Povos indígenas" | 9 | | |
| 63 | \| P13 \| "Alfabetização depois dos 60" \| Branca 93%, Negra 80%, Indígena 72% \| `alfabetizacao_60mais.png` \| | 9 | | |
| 64 | \| M02 \| "Por que o dado indígena tem mais ressalva" \| Amostra de ~2.900 pessoas por trimestre na PNAD; média móvel e agrupamento de trimestres; o Censo (Etapa 2) é a fonte mais robusta \| `docs/LIMITACOES_E_METODOLOGIA.md… | 9 | | |
| 84 | \| M03 \| "O que é 'estatisticamente significativo'" \| Teste de Welch e IC, com o hiato como exemplo \| `docs/LIMITACOES_E_METODOLOGIA.md` \| | 6 | | |
| 87 | \| M05 \| "Correlação não é causa" \| Quebra estrutural (reformas) vs. desenho causal das cotas \| `docs/ANALISE_CAUSAL_COTAS.md` \| | 1 | | |
| 94 | \| F02 \| "Terra indígena, etnia e renda" \| Etapa 2 — Censo 2022 \| | 9 | | |

## conteudo/README.md

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| 40 | 4. **Ressalvas viram conteúdo**: amostra pequena de Indígena, correlação × causalidade e | 9 | | |
| 42 | 5. **Linguagem**: "Negra" = Preta + Parda (definição dita uma vez por post); Indígena e | 9 | | |
| 104 | \| Etapa 2 — Censo 2022 \| Recorte ABC Paulista e recorte indígena \| a partir do 2º semestre de 2027, se a etapa fechar \| | 9 | | |

## docs/Datahub_Racial_Brasil_ARVORE.pptx

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| slide 3 | 1 de renda · 3 de hiato · Renda por raça (Branca / Negra=Preta+Parda / Indígena): série 2012–2026. Hiato: série separada por comparação (vs. Negra / vs. Indígena); o snapshot é 1 gráfico com as 2 barras. Série de Indígen… | 9 | | |
| slide 5, slide 14, slide 17, slide 20, slide 32, slide 34 … (+52) | hiato = renda média Branca − renda média do grupo, % relativo ao grupo · Welch trimestre a trimestre | 6 | | |
| slide 5 | Hiato de renda Branca vs. Negra — Raça (Brasil) — 2012–2026 (Welch). | 6 | | |
| slide 6 | Hiato de renda — Branca vs. Indígena — Brasil | 9 | | |
| slide 6, slide 15, slide 18, slide 21, slide 33, slide 35 … (+51) | hiato = renda média Branca − renda média do grupo, % relativo ao grupo · Welch trimestre a trimestre · série de Indígena suavizada (média móvel centrada de 4 trimestres, amostra pequena) | 6,9 | | |
| slide 6 | Hiato de renda Branca vs. Indígena — Raça (Brasil) — 2012–2026 (Welch). | 6,9 | | |
| slide 7 | Hiato de renda — Branca vs. Negra e vs. Indígena — Brasil | 9 | | |
| slide 7, slide 22, slide 23, slide 42, slide 43, slide 62 … (+5) | % de diferença de renda · Welch: *** p<0,001 ** p<0,01 * p<0,05 · n.s. = não signif. · 2º tri. 2026 | 6 | | |
| slide 7 | Hiato Branca vs. Negra e Branca vs. Indígena — 2º tri. 2026. | 9 | | |
| slide 14 | Hiato de renda Branca vs. Negra por sexo — 2012–2026 (Welch). | 6 | | |
| slide 15, slide 23 | Hiato de renda por gênero — Branca vs. Indígena — Brasil | 9 | | |
| slide 15 | Hiato de renda Branca vs. Indígena por sexo — 2012–2026 (Welch). | 6,9 | | |
| slide 17 | Hiato de renda Branca vs. Negra — Mulheres — 2012–2026 (Welch). | 6 | | |
| slide 18 | Hiato de renda — Mulheres — Branca vs. Indígena — Brasil | 9 | | |
| slide 18 | Hiato de renda Branca vs. Indígena — Mulheres — 2012–2026 (Welch). | 6,9 | | |
| slide 20 | Hiato de renda Branca vs. Negra — Homens — 2012–2026 (Welch). | 6 | | |
| slide 21 | Hiato de renda — Homens — Branca vs. Indígena — Brasil | 9 | | |
| slide 21 | Hiato de renda Branca vs. Indígena — Homens — 2012–2026 (Welch). | 6,9 | | |
| slide 23 | Hiato Branca vs. Indígena por sexo — 2º tri. 2026. | 9 | | |
| slide 27, slide 47, slide 67 | Renda média real — Indígena — Brasil | 9 | | |
| slide 27 | Renda média real por faixa etaria — Indígena — série histórica. | 9 | | |
| slide 32, slide 102, slide 122 | Hiato de renda Branca vs. Negra por faixa etaria — 2012–2026 (Welch). | 6 | | |
| slide 33, slide 43 | Hiato de renda por faixa etaria — Branca vs. Indígena — Brasil | 9 | | |
| slide 33, slide 103, slide 123 | Hiato de renda Branca vs. Indígena por faixa etaria — 2012–2026 (Welch). | 6,9 | | |
| slide 34 | Hiato de renda Branca vs. Negra — 18-24 anos — 2012–2026 (Welch). | 6 | | |
| slide 35 | Hiato de renda — 18-24 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 35 | Hiato de renda Branca vs. Indígena — 18-24 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 36 | Hiato de renda Branca vs. Negra — 25-39 anos — 2012–2026 (Welch). | 6 | | |
| slide 37 | Hiato de renda — 25-39 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 37 | Hiato de renda Branca vs. Indígena — 25-39 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 38 | Hiato de renda Branca vs. Negra — 40-59 anos — 2012–2026 (Welch). | 6 | | |
| slide 39 | Hiato de renda — 40-59 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 39 | Hiato de renda Branca vs. Indígena — 40-59 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 40 | Hiato de renda Branca vs. Negra — 60+ anos — 2012–2026 (Welch). | 6 | | |
| slide 41 | Hiato de renda — 60+ anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 41 | Hiato de renda Branca vs. Indígena — 60+ anos — 2012–2026 (Welch). | 6,9 | | |
| slide 43, slide 113, slide 133 | Hiato Branca vs. Indígena por faixa etaria — 2º tri. 2026. | 9 | | |
| slide 47 | Renda média real por geracao — Indígena — série histórica. | 9 | | |
| slide 52, slide 143, slide 163 | Hiato de renda Branca vs. Negra por geracao — 2012–2026 (Welch). | 6 | | |
| slide 53, slide 63 | Hiato de renda por geracao — Branca vs. Indígena — Brasil | 9 | | |
| slide 53, slide 144, slide 164 | Hiato de renda Branca vs. Indígena por geracao — 2012–2026 (Welch). | 6,9 | | |
| slide 54 | Hiato de renda Branca vs. Negra — Baby Boomer — 2012–2026 (Welch). | 6 | | |
| slide 55 | Hiato de renda — Baby Boomer — Branca vs. Indígena — Brasil | 9 | | |
| slide 55 | Hiato de renda Branca vs. Indígena — Baby Boomer — 2012–2026 (Welch). | 6,9 | | |
| slide 56 | Hiato de renda Branca vs. Negra — Geração X — 2012–2026 (Welch). | 6 | | |
| slide 57 | Hiato de renda — Geração X — Branca vs. Indígena — Brasil | 9 | | |
| slide 57 | Hiato de renda Branca vs. Indígena — Geração X — 2012–2026 (Welch). | 6,9 | | |
| slide 58 | Hiato de renda Branca vs. Negra — Millennial — 2012–2026 (Welch). | 6 | | |
| slide 59 | Hiato de renda — Millennial — Branca vs. Indígena — Brasil | 9 | | |
| slide 59 | Hiato de renda Branca vs. Indígena — Millennial — 2012–2026 (Welch). | 6,9 | | |
| slide 60 | Hiato de renda Branca vs. Negra — Geração Z — 2012–2026 (Welch). | 6 | | |
| slide 61 | Hiato de renda — Geração Z — Branca vs. Indígena — Brasil | 9 | | |
| slide 61 | Hiato de renda Branca vs. Indígena — Geração Z — 2012–2026 (Welch). | 6,9 | | |
| slide 63, slide 154, slide 174 | Hiato Branca vs. Indígena por geracao — 2º tri. 2026. | 9 | | |
| slide 67 | Renda média real por nivel instrucao — Indígena — série histórica. | 9 | | |
| slide 75, slide 187, slide 215 | Hiato de renda Branca vs. Negra por nivel instrucao — 2012–2026 (Welch). | 6 | | |
| slide 76, slide 92 | Hiato de renda por nivel instrucao — Branca vs. Indígena — Brasil | 9 | | |
| slide 76, slide 188, slide 216 | Hiato de renda Branca vs. Indígena por nivel instrucao — 2012–2026 (Welch). | 6,9 | | |
| slide 77 | Hiato de renda Branca vs. Negra — Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 78 | Hiato de renda — Sem instrução — Branca vs. Indígena — Brasil | 9 | | |
| slide 78 | Hiato de renda Branca vs. Indígena — Sem instrução — 2012–2026 (Welch). | 6,9 | | |
| slide 79 | Hiato de renda Branca vs. Negra — Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 80 | Hiato de renda — Fundamental incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 80 | Hiato de renda Branca vs. Indígena — Fundamental incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 81 | Hiato de renda Branca vs. Negra — Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 82 | Hiato de renda — Fundamental compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 82 | Hiato de renda Branca vs. Indígena — Fundamental compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 83 | Hiato de renda Branca vs. Negra — Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 84 | Hiato de renda — Médio incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 84 | Hiato de renda Branca vs. Indígena — Médio incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 85 | Hiato de renda Branca vs. Negra — Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 86 | Hiato de renda — Médio compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 86 | Hiato de renda Branca vs. Indígena — Médio compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 87 | Hiato de renda Branca vs. Negra — Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 88 | Hiato de renda — Superior incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 88 | Hiato de renda Branca vs. Indígena — Superior incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 89 | Hiato de renda Branca vs. Negra — Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 90 | Hiato de renda — Superior compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 90 | Hiato de renda Branca vs. Indígena — Superior compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 92, slide 203, slide 232 | Hiato Branca vs. Indígena por nivel instrucao — 2º tri. 2026. | 9 | | |
| slide 97, slide 138, slide 179 | Renda média real — Mulheres — Indígena — Brasil | 9 | | |
| slide 97 | Renda média real por faixa etaria — Indígena — Mulheres — série histórica. | 9 | | |
| slide 103, slide 113 | Hiato por faixa etaria — Mulheres — Branca vs. Indígena — Brasil | 9 | | |
| slide 104 | Hiato de renda Branca vs. Negra — Mulheres · 18-24 anos — 2012–2026 (Welch). | 6 | | |
| slide 105 | Hiato de renda — Mulheres · 18-24 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 105 | Hiato de renda Branca vs. Indígena — Mulheres · 18-24 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 106 | Hiato de renda Branca vs. Negra — Mulheres · 25-39 anos — 2012–2026 (Welch). | 6 | | |
| slide 107 | Hiato de renda — Mulheres · 25-39 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 107 | Hiato de renda Branca vs. Indígena — Mulheres · 25-39 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 108 | Hiato de renda Branca vs. Negra — Mulheres · 40-59 anos — 2012–2026 (Welch). | 6 | | |
| slide 109 | Hiato de renda — Mulheres · 40-59 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 109 | Hiato de renda Branca vs. Indígena — Mulheres · 40-59 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 110 | Hiato de renda Branca vs. Negra — Mulheres · 60+ anos — 2012–2026 (Welch). | 6 | | |
| slide 111 | Hiato de renda — Mulheres · 60+ anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 111 | Hiato de renda Branca vs. Indígena — Mulheres · 60+ anos — 2012–2026 (Welch). | 6,9 | | |
| slide 112, slide 113, slide 153, slide 154, slide 202, slide 203 … (+4) | % de diferença de renda · Welch: *** p<0,001 ** p<0,01 * p<0,05 · n.s. = não signif. · 2º tri. 2026 · só mulheres | 6 | | |
| slide 117, slide 158, slide 207 | Renda média real — Homens — Indígena — Brasil | 9 | | |
| slide 117 | Renda média real por faixa etaria — Indígena — Homens — série histórica. | 9 | | |
| slide 123, slide 133 | Hiato por faixa etaria — Homens — Branca vs. Indígena — Brasil | 9 | | |
| slide 124 | Hiato de renda Branca vs. Negra — Homens · 18-24 anos — 2012–2026 (Welch). | 6 | | |
| slide 125 | Hiato de renda — Homens · 18-24 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 125 | Hiato de renda Branca vs. Indígena — Homens · 18-24 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 126 | Hiato de renda Branca vs. Negra — Homens · 25-39 anos — 2012–2026 (Welch). | 6 | | |
| slide 127 | Hiato de renda — Homens · 25-39 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 127 | Hiato de renda Branca vs. Indígena — Homens · 25-39 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 128 | Hiato de renda Branca vs. Negra — Homens · 40-59 anos — 2012–2026 (Welch). | 6 | | |
| slide 129 | Hiato de renda — Homens · 40-59 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 129 | Hiato de renda Branca vs. Indígena — Homens · 40-59 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 130 | Hiato de renda Branca vs. Negra — Homens · 60+ anos — 2012–2026 (Welch). | 6 | | |
| slide 131 | Hiato de renda — Homens · 60+ anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 131 | Hiato de renda Branca vs. Indígena — Homens · 60+ anos — 2012–2026 (Welch). | 6,9 | | |
| slide 132, slide 133, slide 173, slide 174, slide 231, slide 232 … (+4) | % de diferença de renda · Welch: *** p<0,001 ** p<0,01 * p<0,05 · n.s. = não signif. · 2º tri. 2026 · só homens | 6 | | |
| slide 138 | Renda média real por geracao — Indígena — Mulheres — série histórica. | 9 | | |
| slide 144, slide 154 | Hiato por geracao — Mulheres — Branca vs. Indígena — Brasil | 9 | | |
| slide 145 | Hiato de renda Branca vs. Negra — Mulheres · Baby Boomer — 2012–2026 (Welch). | 6 | | |
| slide 146 | Hiato de renda — Mulheres · Baby Boomer — Branca vs. Indígena — Brasil | 9 | | |
| slide 146 | Hiato de renda Branca vs. Indígena — Mulheres · Baby Boomer — 2012–2026 (Welch). | 6,9 | | |
| slide 147 | Hiato de renda Branca vs. Negra — Mulheres · Geração X — 2012–2026 (Welch). | 6 | | |
| slide 148 | Hiato de renda — Mulheres · Geração X — Branca vs. Indígena — Brasil | 9 | | |
| slide 148 | Hiato de renda Branca vs. Indígena — Mulheres · Geração X — 2012–2026 (Welch). | 6,9 | | |
| slide 149 | Hiato de renda Branca vs. Negra — Mulheres · Millennial — 2012–2026 (Welch). | 6 | | |
| slide 150 | Hiato de renda — Mulheres · Millennial — Branca vs. Indígena — Brasil | 9 | | |
| slide 150 | Hiato de renda Branca vs. Indígena — Mulheres · Millennial — 2012–2026 (Welch). | 6,9 | | |
| slide 151 | Hiato de renda Branca vs. Negra — Mulheres · Geração Z — 2012–2026 (Welch). | 6 | | |
| slide 152 | Hiato de renda — Mulheres · Geração Z — Branca vs. Indígena — Brasil | 9 | | |
| slide 152 | Hiato de renda Branca vs. Indígena — Mulheres · Geração Z — 2012–2026 (Welch). | 6,9 | | |
| slide 158 | Renda média real por geracao — Indígena — Homens — série histórica. | 9 | | |
| slide 164, slide 174 | Hiato por geracao — Homens — Branca vs. Indígena — Brasil | 9 | | |
| slide 165 | Hiato de renda Branca vs. Negra — Homens · Baby Boomer — 2012–2026 (Welch). | 6 | | |
| slide 166 | Hiato de renda — Homens · Baby Boomer — Branca vs. Indígena — Brasil | 9 | | |
| slide 166 | Hiato de renda Branca vs. Indígena — Homens · Baby Boomer — 2012–2026 (Welch). | 6,9 | | |
| slide 167 | Hiato de renda Branca vs. Negra — Homens · Geração X — 2012–2026 (Welch). | 6 | | |
| slide 168 | Hiato de renda — Homens · Geração X — Branca vs. Indígena — Brasil | 9 | | |
| slide 168 | Hiato de renda Branca vs. Indígena — Homens · Geração X — 2012–2026 (Welch). | 6,9 | | |
| slide 169 | Hiato de renda Branca vs. Negra — Homens · Millennial — 2012–2026 (Welch). | 6 | | |
| slide 170 | Hiato de renda — Homens · Millennial — Branca vs. Indígena — Brasil | 9 | | |
| slide 170 | Hiato de renda Branca vs. Indígena — Homens · Millennial — 2012–2026 (Welch). | 6,9 | | |
| slide 171 | Hiato de renda Branca vs. Negra — Homens · Geração Z — 2012–2026 (Welch). | 6 | | |
| slide 172 | Hiato de renda — Homens · Geração Z — Branca vs. Indígena — Brasil | 9 | | |
| slide 172 | Hiato de renda Branca vs. Indígena — Homens · Geração Z — 2012–2026 (Welch). | 6,9 | | |
| slide 179 | Renda média real por nivel instrucao — Indígena — Mulheres — série histórica. | 9 | | |
| slide 188, slide 203 | Hiato por nivel instrucao — Mulheres — Branca vs. Indígena — Brasil | 9 | | |
| slide 189 | Hiato de renda Branca vs. Negra — Mulheres · Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 190 | Hiato de renda Branca vs. Negra — Mulheres · Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 191 | Hiato de renda — Mulheres · Fundamental incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 191 | Hiato de renda Branca vs. Indígena — Mulheres · Fundamental incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 192 | Hiato de renda Branca vs. Negra — Mulheres · Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 193 | Hiato de renda — Mulheres · Fundamental compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 193 | Hiato de renda Branca vs. Indígena — Mulheres · Fundamental compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 194 | Hiato de renda Branca vs. Negra — Mulheres · Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 195 | Hiato de renda — Mulheres · Médio incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 195 | Hiato de renda Branca vs. Indígena — Mulheres · Médio incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 196 | Hiato de renda Branca vs. Negra — Mulheres · Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 197 | Hiato de renda — Mulheres · Médio compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 197 | Hiato de renda Branca vs. Indígena — Mulheres · Médio compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 198 | Hiato de renda Branca vs. Negra — Mulheres · Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 199 | Hiato de renda — Mulheres · Superior incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 199 | Hiato de renda Branca vs. Indígena — Mulheres · Superior incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 200 | Hiato de renda Branca vs. Negra — Mulheres · Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 201 | Hiato de renda — Mulheres · Superior compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 201 | Hiato de renda Branca vs. Indígena — Mulheres · Superior compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 207 | Renda média real por nivel instrucao — Indígena — Homens — série histórica. | 9 | | |
| slide 216, slide 232 | Hiato por nivel instrucao — Homens — Branca vs. Indígena — Brasil | 9 | | |
| slide 217 | Hiato de renda Branca vs. Negra — Homens · Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 218 | Hiato de renda — Homens · Sem instrução — Branca vs. Indígena — Brasil | 9 | | |
| slide 218 | Hiato de renda Branca vs. Indígena — Homens · Sem instrução — 2012–2026 (Welch). | 6,9 | | |
| slide 219 | Hiato de renda Branca vs. Negra — Homens · Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 220 | Hiato de renda — Homens · Fundamental incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 220 | Hiato de renda Branca vs. Indígena — Homens · Fundamental incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 221 | Hiato de renda Branca vs. Negra — Homens · Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 222 | Hiato de renda — Homens · Fundamental compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 222 | Hiato de renda Branca vs. Indígena — Homens · Fundamental compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 223 | Hiato de renda Branca vs. Negra — Homens · Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 224 | Hiato de renda — Homens · Médio incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 224 | Hiato de renda Branca vs. Indígena — Homens · Médio incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 225 | Hiato de renda Branca vs. Negra — Homens · Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 226 | Hiato de renda — Homens · Médio compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 226 | Hiato de renda Branca vs. Indígena — Homens · Médio compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 227 | Hiato de renda Branca vs. Negra — Homens · Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 228 | Hiato de renda — Homens · Superior incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 228 | Hiato de renda Branca vs. Indígena — Homens · Superior incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 229 | Hiato de renda Branca vs. Negra — Homens · Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 230 | Hiato de renda — Homens · Superior compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 230 | Hiato de renda Branca vs. Indígena — Homens · Superior compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 233 | 56 de renda · 59 de hiato · Quebra CRUZADA gênero×faixa×escolaridade — 70 células (série de renda + série de hiato Branca-vs-Negra por célula). Indígena via 2 heatmaps por gênero (vs. Negra / vs. Indígena). | 9 | | |
| slide 237, slide 239, slide 241, slide 243, slide 245, slide 247 … (+104) | hiato = renda média Branca − renda média do grupo, % relativo ao grupo · Welch trimestre a trimestre · (Indígena por célula sem amostra — ver heatmaps do item) | 6,9 | | |
| slide 237 | Hiato Branca vs. Negra — Mulheres, 18-24 anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 239 | Hiato Branca vs. Negra — Mulheres, 18-24 anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 241 | Hiato Branca vs. Negra — Mulheres, 18-24 anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 243 | Hiato Branca vs. Negra — Mulheres, 18-24 anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 245 | Hiato Branca vs. Negra — Mulheres, 18-24 anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 247 | Hiato Branca vs. Negra — Mulheres, 18-24 anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 249 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 251 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 253 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 255 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 257 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 259 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 261 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 263 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 265 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 267 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 269 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 271 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 273 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 275 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 277 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 279 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 281 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 283 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 285 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 287 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 289 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 292 | Hiato Branca vs. Negra — Homens, 18-24 anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 294 | Hiato Branca vs. Negra — Homens, 18-24 anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 296 | Hiato Branca vs. Negra — Homens, 18-24 anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 298 | Hiato Branca vs. Negra — Homens, 18-24 anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 300 | Hiato Branca vs. Negra — Homens, 18-24 anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 302 | Hiato Branca vs. Negra — Homens, 18-24 anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 304 | Hiato Branca vs. Negra — Homens, 18-24 anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 306 | Hiato Branca vs. Negra — Homens, 25-39 anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 308 | Hiato Branca vs. Negra — Homens, 25-39 anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 310 | Hiato Branca vs. Negra — Homens, 25-39 anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 312 | Hiato Branca vs. Negra — Homens, 25-39 anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 314 | Hiato Branca vs. Negra — Homens, 25-39 anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 316 | Hiato Branca vs. Negra — Homens, 25-39 anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 318 | Hiato Branca vs. Negra — Homens, 25-39 anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 320 | Hiato Branca vs. Negra — Homens, 40-59 anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 322 | Hiato Branca vs. Negra — Homens, 40-59 anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 324 | Hiato Branca vs. Negra — Homens, 40-59 anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 326 | Hiato Branca vs. Negra — Homens, 40-59 anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 328 | Hiato Branca vs. Negra — Homens, 40-59 anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 330 | Hiato Branca vs. Negra — Homens, 40-59 anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 332 | Hiato Branca vs. Negra — Homens, 40-59 anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 334 | Hiato Branca vs. Negra — Homens, 60+ anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 336 | Hiato Branca vs. Negra — Homens, 60+ anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 338 | Hiato Branca vs. Negra — Homens, 60+ anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 340 | Hiato Branca vs. Negra — Homens, 60+ anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 342 | Hiato Branca vs. Negra — Homens, 60+ anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 344 | Hiato Branca vs. Negra — Homens, 60+ anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 346 | Hiato Branca vs. Negra — Homens, 60+ anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 349 | Hiato Branca vs. Indígena — Mulheres: faixa etaria × escolaridade — Brasil | 9 | | |
| slide 349 | Hiato Branca vs. Indígena por faixa etaria e escolaridade, só mulheres — 2º tri. 2026. | 9 | | |
| slide 352 | Hiato Branca vs. Indígena — Homens: faixa etaria × escolaridade — Brasil | 9 | | |
| slide 352 | Hiato Branca vs. Indígena por faixa etaria e escolaridade, só homens — 2º tri. 2026. | 9 | | |
| slide 356 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 358 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 360 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 362 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 364 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 366 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 368 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 370 | Hiato Branca vs. Negra — Mulheres, Geração X, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 372 | Hiato Branca vs. Negra — Mulheres, Geração X, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 374 | Hiato Branca vs. Negra — Mulheres, Geração X, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 376 | Hiato Branca vs. Negra — Mulheres, Geração X, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 378 | Hiato Branca vs. Negra — Mulheres, Geração X, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 380 | Hiato Branca vs. Negra — Mulheres, Geração X, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 382 | Hiato Branca vs. Negra — Mulheres, Geração X, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 384 | Hiato Branca vs. Negra — Mulheres, Millennial, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 386 | Hiato Branca vs. Negra — Mulheres, Millennial, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 388 | Hiato Branca vs. Negra — Mulheres, Millennial, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 390 | Hiato Branca vs. Negra — Mulheres, Millennial, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 392 | Hiato Branca vs. Negra — Mulheres, Millennial, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 394 | Hiato Branca vs. Negra — Mulheres, Millennial, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 396 | Hiato Branca vs. Negra — Mulheres, Millennial, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 399 | Hiato Branca vs. Negra — Mulheres, Geração Z, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 401 | Hiato Branca vs. Negra — Mulheres, Geração Z, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 403 | Hiato Branca vs. Negra — Mulheres, Geração Z, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 405 | Hiato Branca vs. Negra — Mulheres, Geração Z, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 407 | Hiato Branca vs. Negra — Mulheres, Geração Z, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 409 | Hiato Branca vs. Negra — Mulheres, Geração Z, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 412 | Hiato Branca vs. Negra — Homens, Baby Boomer, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 414 | Hiato Branca vs. Negra — Homens, Baby Boomer, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 416 | Hiato Branca vs. Negra — Homens, Baby Boomer, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 418 | Hiato Branca vs. Negra — Homens, Baby Boomer, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 420 | Hiato Branca vs. Negra — Homens, Baby Boomer, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 422 | Hiato Branca vs. Negra — Homens, Baby Boomer, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 424 | Hiato Branca vs. Negra — Homens, Baby Boomer, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 426 | Hiato Branca vs. Negra — Homens, Geração X, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 428 | Hiato Branca vs. Negra — Homens, Geração X, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 430 | Hiato Branca vs. Negra — Homens, Geração X, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 432 | Hiato Branca vs. Negra — Homens, Geração X, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 434 | Hiato Branca vs. Negra — Homens, Geração X, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 436 | Hiato Branca vs. Negra — Homens, Geração X, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 438 | Hiato Branca vs. Negra — Homens, Geração X, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 440 | Hiato Branca vs. Negra — Homens, Millennial, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 442 | Hiato Branca vs. Negra — Homens, Millennial, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 444 | Hiato Branca vs. Negra — Homens, Millennial, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 446 | Hiato Branca vs. Negra — Homens, Millennial, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 448 | Hiato Branca vs. Negra — Homens, Millennial, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 450 | Hiato Branca vs. Negra — Homens, Millennial, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 452 | Hiato Branca vs. Negra — Homens, Millennial, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 454 | Hiato Branca vs. Negra — Homens, Geração Z, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 456 | Hiato Branca vs. Negra — Homens, Geração Z, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 458 | Hiato Branca vs. Negra — Homens, Geração Z, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 460 | Hiato Branca vs. Negra — Homens, Geração Z, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 462 | Hiato Branca vs. Negra — Homens, Geração Z, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 464 | Hiato Branca vs. Negra — Homens, Geração Z, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 466 | Hiato Branca vs. Negra — Homens, Geração Z, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 469 | Hiato Branca vs. Indígena — Mulheres: geracao × escolaridade — Brasil | 9 | | |
| slide 469 | Hiato Branca vs. Indígena por geracao e escolaridade, só mulheres — 2º tri. 2026. | 9 | | |
| slide 472 | Hiato Branca vs. Indígena — Homens: geracao × escolaridade — Brasil | 9 | | |
| slide 472 | Hiato Branca vs. Indígena por geracao e escolaridade, só homens — 2º tri. 2026. | 9 | | |
| slide 475, slide 477, slide 479, slide 481, slide 483, slide 485 … (+22) | hiato = renda média Branca − renda média do grupo, % relativo ao grupo · Welch trimestre a trimestre · ambos os gêneros · (Indígena por célula: ver heatmaps do item) | 6,9 | | |
| slide 475 | Hiato Branca vs. Negra — Baby Boomer, Sem instrução, ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 477 | Hiato Branca vs. Negra — Baby Boomer, Fundamental incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 479 | Hiato Branca vs. Negra — Baby Boomer, Fundamental compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 481 | Hiato Branca vs. Negra — Baby Boomer, Médio incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 483 | Hiato Branca vs. Negra — Baby Boomer, Médio compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 485 | Hiato Branca vs. Negra — Baby Boomer, Superior incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 487 | Hiato Branca vs. Negra — Baby Boomer, Superior compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 489 | Hiato Branca vs. Negra — Geração X, Sem instrução, ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 491 | Hiato Branca vs. Negra — Geração X, Fundamental incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 493 | Hiato Branca vs. Negra — Geração X, Fundamental compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 495 | Hiato Branca vs. Negra — Geração X, Médio incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 497 | Hiato Branca vs. Negra — Geração X, Médio compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 499 | Hiato Branca vs. Negra — Geração X, Superior incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 501 | Hiato Branca vs. Negra — Geração X, Superior compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 503 | Hiato Branca vs. Negra — Millennial, Sem instrução, ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 505 | Hiato Branca vs. Negra — Millennial, Fundamental incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 507 | Hiato Branca vs. Negra — Millennial, Fundamental compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 509 | Hiato Branca vs. Negra — Millennial, Médio incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 511 | Hiato Branca vs. Negra — Millennial, Médio compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 513 | Hiato Branca vs. Negra — Millennial, Superior incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 515 | Hiato Branca vs. Negra — Millennial, Superior compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 517 | Hiato Branca vs. Negra — Geração Z, Sem instrução, ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 519 | Hiato Branca vs. Negra — Geração Z, Fundamental incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 521 | Hiato Branca vs. Negra — Geração Z, Fundamental compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 523 | Hiato Branca vs. Negra — Geração Z, Médio incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 525 | Hiato Branca vs. Negra — Geração Z, Médio compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 527 | Hiato Branca vs. Negra — Geração Z, Superior incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 529 | Hiato Branca vs. Negra — Geração Z, Superior compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 531 | Hiato Branca vs. Indígena — geração × escolaridade (ambos os gêneros) — Brasil | 9 | | |
| slide 531 | Hiato Branca vs. Indígena por geração e escolaridade, ambos os gêneros — 2º tri. 2026. | 9 | | |

## docs/Datahub_Racial_Brasil_Fase1.pptx

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| slide 3 | Estudos com ficha, hipóteses escritas antes de rodar e IC design-based (docs/studies). Onda 5 (Lei de Cotas): sem efeito afirmável (ficha G1). | 2 | | |
| slide 5, slide 6, slide 7, slide 8 | Erro-padrão robusto a autocorrelação (EWC). Fichas B1–B6. | 6 | | |
| slide 5 | A queda de 2012–2026 é um degrau em 2022 (−5,0 p.p.; IC −6,8 a −3,1); sem tendência contínua, e plana desde 2022 (B1). | 1 | | |
| slide 17 | Cerca de 78% do hiato está associado a instrução, território, ocupação, vínculo e horas; os três primeiros pesam ≈ 20% cada (D1). | 4 | | |
| slide 21 | No 9º ano, 0,42 DP de diferença; com o mesmo INSE e na mesma escola, 0,14–0,21 DP. Cresce do 5º ao 9º ano (E3). | 7 | | |
| slide 27, slide 28, slide 29, slide 30 | Censo 2022 (universo e amostra), POF e painel da PNAD Contínua. Fichas D4.4, I1, H3.4, H4.2. | 10 | | |
| slide 27 | O Censo 2022 confirma o hiato da PNADC (70% × 66%); para indígenas o Censo mostra +117% — a PNADC subestima (I1). | C1,9,10 | | |
| slide 36 | 1 de renda · 3 de hiato · Renda por raça (Branca / Negra=Preta+Parda / Indígena): série 2012–2026. Hiato: série separada por comparação (vs. Negra / vs. Indígena); o snapshot é 1 gráfico com as 2 barras. Série de Indígen… | 9 | | |
| slide 38, slide 47, slide 50, slide 53, slide 65, slide 67 … (+52) | hiato = renda média Branca − renda média do grupo, % relativo ao grupo · Welch trimestre a trimestre | 6 | | |
| slide 38 | Hiato de renda Branca vs. Negra — Raça (Brasil) — 2012–2026 (Welch). | 6 | | |
| slide 39 | Hiato de renda — Branca vs. Indígena — Brasil | 9 | | |
| slide 39, slide 48, slide 51, slide 54, slide 66, slide 68 … (+51) | hiato = renda média Branca − renda média do grupo, % relativo ao grupo · Welch trimestre a trimestre · série de Indígena suavizada (média móvel centrada de 4 trimestres, amostra pequena) | 6,9 | | |
| slide 39 | Hiato de renda Branca vs. Indígena — Raça (Brasil) — 2012–2026 (Welch). | 6,9 | | |
| slide 40 | Hiato de renda — Branca vs. Negra e vs. Indígena — Brasil | 9 | | |
| slide 40, slide 55, slide 56, slide 75, slide 76, slide 95 … (+5) | % de diferença de renda · Welch: *** p<0,001 ** p<0,01 * p<0,05 · n.s. = não signif. · 2º tri. 2026 | 6 | | |
| slide 40 | Hiato Branca vs. Negra e Branca vs. Indígena — 2º tri. 2026. | 9 | | |
| slide 47 | Hiato de renda Branca vs. Negra por sexo — 2012–2026 (Welch). | 6 | | |
| slide 48, slide 56 | Hiato de renda por gênero — Branca vs. Indígena — Brasil | 9 | | |
| slide 48 | Hiato de renda Branca vs. Indígena por sexo — 2012–2026 (Welch). | 6,9 | | |
| slide 50 | Hiato de renda Branca vs. Negra — Mulheres — 2012–2026 (Welch). | 6 | | |
| slide 51 | Hiato de renda — Mulheres — Branca vs. Indígena — Brasil | 9 | | |
| slide 51 | Hiato de renda Branca vs. Indígena — Mulheres — 2012–2026 (Welch). | 6,9 | | |
| slide 53 | Hiato de renda Branca vs. Negra — Homens — 2012–2026 (Welch). | 6 | | |
| slide 54 | Hiato de renda — Homens — Branca vs. Indígena — Brasil | 9 | | |
| slide 54 | Hiato de renda Branca vs. Indígena — Homens — 2012–2026 (Welch). | 6,9 | | |
| slide 56 | Hiato Branca vs. Indígena por sexo — 2º tri. 2026. | 9 | | |
| slide 60, slide 80, slide 100 | Renda média real — Indígena — Brasil | 9 | | |
| slide 60 | Renda média real por faixa etaria — Indígena — série histórica. | 9 | | |
| slide 65, slide 135, slide 155 | Hiato de renda Branca vs. Negra por faixa etaria — 2012–2026 (Welch). | 6 | | |
| slide 66, slide 76 | Hiato de renda por faixa etaria — Branca vs. Indígena — Brasil | 9 | | |
| slide 66, slide 136, slide 156 | Hiato de renda Branca vs. Indígena por faixa etaria — 2012–2026 (Welch). | 6,9 | | |
| slide 67 | Hiato de renda Branca vs. Negra — 18-24 anos — 2012–2026 (Welch). | 6 | | |
| slide 68 | Hiato de renda — 18-24 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 68 | Hiato de renda Branca vs. Indígena — 18-24 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 69 | Hiato de renda Branca vs. Negra — 25-39 anos — 2012–2026 (Welch). | 6 | | |
| slide 70 | Hiato de renda — 25-39 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 70 | Hiato de renda Branca vs. Indígena — 25-39 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 71 | Hiato de renda Branca vs. Negra — 40-59 anos — 2012–2026 (Welch). | 6 | | |
| slide 72 | Hiato de renda — 40-59 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 72 | Hiato de renda Branca vs. Indígena — 40-59 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 73 | Hiato de renda Branca vs. Negra — 60+ anos — 2012–2026 (Welch). | 6 | | |
| slide 74 | Hiato de renda — 60+ anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 74 | Hiato de renda Branca vs. Indígena — 60+ anos — 2012–2026 (Welch). | 6,9 | | |
| slide 76, slide 146, slide 166 | Hiato Branca vs. Indígena por faixa etaria — 2º tri. 2026. | 9 | | |
| slide 80 | Renda média real por geracao — Indígena — série histórica. | 9 | | |
| slide 85, slide 176, slide 196 | Hiato de renda Branca vs. Negra por geracao — 2012–2026 (Welch). | 6 | | |
| slide 86, slide 96 | Hiato de renda por geracao — Branca vs. Indígena — Brasil | 9 | | |
| slide 86, slide 177, slide 197 | Hiato de renda Branca vs. Indígena por geracao — 2012–2026 (Welch). | 6,9 | | |
| slide 87 | Hiato de renda Branca vs. Negra — Baby Boomer — 2012–2026 (Welch). | 6 | | |
| slide 88 | Hiato de renda — Baby Boomer — Branca vs. Indígena — Brasil | 9 | | |
| slide 88 | Hiato de renda Branca vs. Indígena — Baby Boomer — 2012–2026 (Welch). | 6,9 | | |
| slide 89 | Hiato de renda Branca vs. Negra — Geração X — 2012–2026 (Welch). | 6 | | |
| slide 90 | Hiato de renda — Geração X — Branca vs. Indígena — Brasil | 9 | | |
| slide 90 | Hiato de renda Branca vs. Indígena — Geração X — 2012–2026 (Welch). | 6,9 | | |
| slide 91 | Hiato de renda Branca vs. Negra — Millennial — 2012–2026 (Welch). | 6 | | |
| slide 92 | Hiato de renda — Millennial — Branca vs. Indígena — Brasil | 9 | | |
| slide 92 | Hiato de renda Branca vs. Indígena — Millennial — 2012–2026 (Welch). | 6,9 | | |
| slide 93 | Hiato de renda Branca vs. Negra — Geração Z — 2012–2026 (Welch). | 6 | | |
| slide 94 | Hiato de renda — Geração Z — Branca vs. Indígena — Brasil | 9 | | |
| slide 94 | Hiato de renda Branca vs. Indígena — Geração Z — 2012–2026 (Welch). | 6,9 | | |
| slide 96, slide 187, slide 207 | Hiato Branca vs. Indígena por geracao — 2º tri. 2026. | 9 | | |
| slide 100 | Renda média real por nivel instrucao — Indígena — série histórica. | 9 | | |
| slide 108, slide 220, slide 248 | Hiato de renda Branca vs. Negra por nivel instrucao — 2012–2026 (Welch). | 6 | | |
| slide 109, slide 125 | Hiato de renda por nivel instrucao — Branca vs. Indígena — Brasil | 9 | | |
| slide 109, slide 221, slide 249 | Hiato de renda Branca vs. Indígena por nivel instrucao — 2012–2026 (Welch). | 6,9 | | |
| slide 110 | Hiato de renda Branca vs. Negra — Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 111 | Hiato de renda — Sem instrução — Branca vs. Indígena — Brasil | 9 | | |
| slide 111 | Hiato de renda Branca vs. Indígena — Sem instrução — 2012–2026 (Welch). | 6,9 | | |
| slide 112 | Hiato de renda Branca vs. Negra — Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 113 | Hiato de renda — Fundamental incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 113 | Hiato de renda Branca vs. Indígena — Fundamental incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 114 | Hiato de renda Branca vs. Negra — Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 115 | Hiato de renda — Fundamental compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 115 | Hiato de renda Branca vs. Indígena — Fundamental compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 116 | Hiato de renda Branca vs. Negra — Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 117 | Hiato de renda — Médio incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 117 | Hiato de renda Branca vs. Indígena — Médio incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 118 | Hiato de renda Branca vs. Negra — Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 119 | Hiato de renda — Médio compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 119 | Hiato de renda Branca vs. Indígena — Médio compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 120 | Hiato de renda Branca vs. Negra — Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 121 | Hiato de renda — Superior incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 121 | Hiato de renda Branca vs. Indígena — Superior incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 122 | Hiato de renda Branca vs. Negra — Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 123 | Hiato de renda — Superior compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 123 | Hiato de renda Branca vs. Indígena — Superior compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 125, slide 236, slide 265 | Hiato Branca vs. Indígena por nivel instrucao — 2º tri. 2026. | 9 | | |
| slide 130, slide 171, slide 212 | Renda média real — Mulheres — Indígena — Brasil | 9 | | |
| slide 130 | Renda média real por faixa etaria — Indígena — Mulheres — série histórica. | 9 | | |
| slide 136, slide 146 | Hiato por faixa etaria — Mulheres — Branca vs. Indígena — Brasil | 9 | | |
| slide 137 | Hiato de renda Branca vs. Negra — Mulheres · 18-24 anos — 2012–2026 (Welch). | 6 | | |
| slide 138 | Hiato de renda — Mulheres · 18-24 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 138 | Hiato de renda Branca vs. Indígena — Mulheres · 18-24 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 139 | Hiato de renda Branca vs. Negra — Mulheres · 25-39 anos — 2012–2026 (Welch). | 6 | | |
| slide 140 | Hiato de renda — Mulheres · 25-39 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 140 | Hiato de renda Branca vs. Indígena — Mulheres · 25-39 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 141 | Hiato de renda Branca vs. Negra — Mulheres · 40-59 anos — 2012–2026 (Welch). | 6 | | |
| slide 142 | Hiato de renda — Mulheres · 40-59 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 142 | Hiato de renda Branca vs. Indígena — Mulheres · 40-59 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 143 | Hiato de renda Branca vs. Negra — Mulheres · 60+ anos — 2012–2026 (Welch). | 6 | | |
| slide 144 | Hiato de renda — Mulheres · 60+ anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 144 | Hiato de renda Branca vs. Indígena — Mulheres · 60+ anos — 2012–2026 (Welch). | 6,9 | | |
| slide 145, slide 146, slide 186, slide 187, slide 235, slide 236 … (+4) | % de diferença de renda · Welch: *** p<0,001 ** p<0,01 * p<0,05 · n.s. = não signif. · 2º tri. 2026 · só mulheres | 6 | | |
| slide 150, slide 191, slide 240 | Renda média real — Homens — Indígena — Brasil | 9 | | |
| slide 150 | Renda média real por faixa etaria — Indígena — Homens — série histórica. | 9 | | |
| slide 156, slide 166 | Hiato por faixa etaria — Homens — Branca vs. Indígena — Brasil | 9 | | |
| slide 157 | Hiato de renda Branca vs. Negra — Homens · 18-24 anos — 2012–2026 (Welch). | 6 | | |
| slide 158 | Hiato de renda — Homens · 18-24 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 158 | Hiato de renda Branca vs. Indígena — Homens · 18-24 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 159 | Hiato de renda Branca vs. Negra — Homens · 25-39 anos — 2012–2026 (Welch). | 6 | | |
| slide 160 | Hiato de renda — Homens · 25-39 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 160 | Hiato de renda Branca vs. Indígena — Homens · 25-39 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 161 | Hiato de renda Branca vs. Negra — Homens · 40-59 anos — 2012–2026 (Welch). | 6 | | |
| slide 162 | Hiato de renda — Homens · 40-59 anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 162 | Hiato de renda Branca vs. Indígena — Homens · 40-59 anos — 2012–2026 (Welch). | 6,9 | | |
| slide 163 | Hiato de renda Branca vs. Negra — Homens · 60+ anos — 2012–2026 (Welch). | 6 | | |
| slide 164 | Hiato de renda — Homens · 60+ anos — Branca vs. Indígena — Brasil | 9 | | |
| slide 164 | Hiato de renda Branca vs. Indígena — Homens · 60+ anos — 2012–2026 (Welch). | 6,9 | | |
| slide 165, slide 166, slide 206, slide 207, slide 264, slide 265 … (+4) | % de diferença de renda · Welch: *** p<0,001 ** p<0,01 * p<0,05 · n.s. = não signif. · 2º tri. 2026 · só homens | 6 | | |
| slide 171 | Renda média real por geracao — Indígena — Mulheres — série histórica. | 9 | | |
| slide 177, slide 187 | Hiato por geracao — Mulheres — Branca vs. Indígena — Brasil | 9 | | |
| slide 178 | Hiato de renda Branca vs. Negra — Mulheres · Baby Boomer — 2012–2026 (Welch). | 6 | | |
| slide 179 | Hiato de renda — Mulheres · Baby Boomer — Branca vs. Indígena — Brasil | 9 | | |
| slide 179 | Hiato de renda Branca vs. Indígena — Mulheres · Baby Boomer — 2012–2026 (Welch). | 6,9 | | |
| slide 180 | Hiato de renda Branca vs. Negra — Mulheres · Geração X — 2012–2026 (Welch). | 6 | | |
| slide 181 | Hiato de renda — Mulheres · Geração X — Branca vs. Indígena — Brasil | 9 | | |
| slide 181 | Hiato de renda Branca vs. Indígena — Mulheres · Geração X — 2012–2026 (Welch). | 6,9 | | |
| slide 182 | Hiato de renda Branca vs. Negra — Mulheres · Millennial — 2012–2026 (Welch). | 6 | | |
| slide 183 | Hiato de renda — Mulheres · Millennial — Branca vs. Indígena — Brasil | 9 | | |
| slide 183 | Hiato de renda Branca vs. Indígena — Mulheres · Millennial — 2012–2026 (Welch). | 6,9 | | |
| slide 184 | Hiato de renda Branca vs. Negra — Mulheres · Geração Z — 2012–2026 (Welch). | 6 | | |
| slide 185 | Hiato de renda — Mulheres · Geração Z — Branca vs. Indígena — Brasil | 9 | | |
| slide 185 | Hiato de renda Branca vs. Indígena — Mulheres · Geração Z — 2012–2026 (Welch). | 6,9 | | |
| slide 191 | Renda média real por geracao — Indígena — Homens — série histórica. | 9 | | |
| slide 197, slide 207 | Hiato por geracao — Homens — Branca vs. Indígena — Brasil | 9 | | |
| slide 198 | Hiato de renda Branca vs. Negra — Homens · Baby Boomer — 2012–2026 (Welch). | 6 | | |
| slide 199 | Hiato de renda — Homens · Baby Boomer — Branca vs. Indígena — Brasil | 9 | | |
| slide 199 | Hiato de renda Branca vs. Indígena — Homens · Baby Boomer — 2012–2026 (Welch). | 6,9 | | |
| slide 200 | Hiato de renda Branca vs. Negra — Homens · Geração X — 2012–2026 (Welch). | 6 | | |
| slide 201 | Hiato de renda — Homens · Geração X — Branca vs. Indígena — Brasil | 9 | | |
| slide 201 | Hiato de renda Branca vs. Indígena — Homens · Geração X — 2012–2026 (Welch). | 6,9 | | |
| slide 202 | Hiato de renda Branca vs. Negra — Homens · Millennial — 2012–2026 (Welch). | 6 | | |
| slide 203 | Hiato de renda — Homens · Millennial — Branca vs. Indígena — Brasil | 9 | | |
| slide 203 | Hiato de renda Branca vs. Indígena — Homens · Millennial — 2012–2026 (Welch). | 6,9 | | |
| slide 204 | Hiato de renda Branca vs. Negra — Homens · Geração Z — 2012–2026 (Welch). | 6 | | |
| slide 205 | Hiato de renda — Homens · Geração Z — Branca vs. Indígena — Brasil | 9 | | |
| slide 205 | Hiato de renda Branca vs. Indígena — Homens · Geração Z — 2012–2026 (Welch). | 6,9 | | |
| slide 212 | Renda média real por nivel instrucao — Indígena — Mulheres — série histórica. | 9 | | |
| slide 221, slide 236 | Hiato por nivel instrucao — Mulheres — Branca vs. Indígena — Brasil | 9 | | |
| slide 222 | Hiato de renda Branca vs. Negra — Mulheres · Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 223 | Hiato de renda Branca vs. Negra — Mulheres · Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 224 | Hiato de renda — Mulheres · Fundamental incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 224 | Hiato de renda Branca vs. Indígena — Mulheres · Fundamental incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 225 | Hiato de renda Branca vs. Negra — Mulheres · Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 226 | Hiato de renda — Mulheres · Fundamental compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 226 | Hiato de renda Branca vs. Indígena — Mulheres · Fundamental compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 227 | Hiato de renda Branca vs. Negra — Mulheres · Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 228 | Hiato de renda — Mulheres · Médio incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 228 | Hiato de renda Branca vs. Indígena — Mulheres · Médio incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 229 | Hiato de renda Branca vs. Negra — Mulheres · Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 230 | Hiato de renda — Mulheres · Médio compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 230 | Hiato de renda Branca vs. Indígena — Mulheres · Médio compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 231 | Hiato de renda Branca vs. Negra — Mulheres · Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 232 | Hiato de renda — Mulheres · Superior incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 232 | Hiato de renda Branca vs. Indígena — Mulheres · Superior incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 233 | Hiato de renda Branca vs. Negra — Mulheres · Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 234 | Hiato de renda — Mulheres · Superior compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 234 | Hiato de renda Branca vs. Indígena — Mulheres · Superior compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 240 | Renda média real por nivel instrucao — Indígena — Homens — série histórica. | 9 | | |
| slide 249, slide 265 | Hiato por nivel instrucao — Homens — Branca vs. Indígena — Brasil | 9 | | |
| slide 250 | Hiato de renda Branca vs. Negra — Homens · Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 251 | Hiato de renda — Homens · Sem instrução — Branca vs. Indígena — Brasil | 9 | | |
| slide 251 | Hiato de renda Branca vs. Indígena — Homens · Sem instrução — 2012–2026 (Welch). | 6,9 | | |
| slide 252 | Hiato de renda Branca vs. Negra — Homens · Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 253 | Hiato de renda — Homens · Fundamental incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 253 | Hiato de renda Branca vs. Indígena — Homens · Fundamental incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 254 | Hiato de renda Branca vs. Negra — Homens · Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 255 | Hiato de renda — Homens · Fundamental compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 255 | Hiato de renda Branca vs. Indígena — Homens · Fundamental compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 256 | Hiato de renda Branca vs. Negra — Homens · Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 257 | Hiato de renda — Homens · Médio incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 257 | Hiato de renda Branca vs. Indígena — Homens · Médio incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 258 | Hiato de renda Branca vs. Negra — Homens · Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 259 | Hiato de renda — Homens · Médio compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 259 | Hiato de renda Branca vs. Indígena — Homens · Médio compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 260 | Hiato de renda Branca vs. Negra — Homens · Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 261 | Hiato de renda — Homens · Superior incompl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 261 | Hiato de renda Branca vs. Indígena — Homens · Superior incompl. — 2012–2026 (Welch). | 6,9 | | |
| slide 262 | Hiato de renda Branca vs. Negra — Homens · Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 263 | Hiato de renda — Homens · Superior compl. — Branca vs. Indígena — Brasil | 9 | | |
| slide 263 | Hiato de renda Branca vs. Indígena — Homens · Superior compl. — 2012–2026 (Welch). | 6,9 | | |
| slide 266 | 56 de renda · 59 de hiato · Quebra CRUZADA gênero×faixa×escolaridade — 70 células (série de renda + série de hiato Branca-vs-Negra por célula). Indígena via 2 heatmaps por gênero (vs. Negra / vs. Indígena). | 9 | | |
| slide 270, slide 272, slide 274, slide 276, slide 278, slide 280 … (+104) | hiato = renda média Branca − renda média do grupo, % relativo ao grupo · Welch trimestre a trimestre · (Indígena por célula sem amostra — ver heatmaps do item) | 6,9 | | |
| slide 270 | Hiato Branca vs. Negra — Mulheres, 18-24 anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 272 | Hiato Branca vs. Negra — Mulheres, 18-24 anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 274 | Hiato Branca vs. Negra — Mulheres, 18-24 anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 276 | Hiato Branca vs. Negra — Mulheres, 18-24 anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 278 | Hiato Branca vs. Negra — Mulheres, 18-24 anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 280 | Hiato Branca vs. Negra — Mulheres, 18-24 anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 282 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 284 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 286 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 288 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 290 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 292 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 294 | Hiato Branca vs. Negra — Mulheres, 25-39 anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 296 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 298 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 300 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 302 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 304 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 306 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 308 | Hiato Branca vs. Negra — Mulheres, 40-59 anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 310 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 312 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 314 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 316 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 318 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 320 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 322 | Hiato Branca vs. Negra — Mulheres, 60+ anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 325 | Hiato Branca vs. Negra — Homens, 18-24 anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 327 | Hiato Branca vs. Negra — Homens, 18-24 anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 329 | Hiato Branca vs. Negra — Homens, 18-24 anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 331 | Hiato Branca vs. Negra — Homens, 18-24 anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 333 | Hiato Branca vs. Negra — Homens, 18-24 anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 335 | Hiato Branca vs. Negra — Homens, 18-24 anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 337 | Hiato Branca vs. Negra — Homens, 18-24 anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 339 | Hiato Branca vs. Negra — Homens, 25-39 anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 341 | Hiato Branca vs. Negra — Homens, 25-39 anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 343 | Hiato Branca vs. Negra — Homens, 25-39 anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 345 | Hiato Branca vs. Negra — Homens, 25-39 anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 347 | Hiato Branca vs. Negra — Homens, 25-39 anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 349 | Hiato Branca vs. Negra — Homens, 25-39 anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 351 | Hiato Branca vs. Negra — Homens, 25-39 anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 353 | Hiato Branca vs. Negra — Homens, 40-59 anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 355 | Hiato Branca vs. Negra — Homens, 40-59 anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 357 | Hiato Branca vs. Negra — Homens, 40-59 anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 359 | Hiato Branca vs. Negra — Homens, 40-59 anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 361 | Hiato Branca vs. Negra — Homens, 40-59 anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 363 | Hiato Branca vs. Negra — Homens, 40-59 anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 365 | Hiato Branca vs. Negra — Homens, 40-59 anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 367 | Hiato Branca vs. Negra — Homens, 60+ anos, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 369 | Hiato Branca vs. Negra — Homens, 60+ anos, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 371 | Hiato Branca vs. Negra — Homens, 60+ anos, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 373 | Hiato Branca vs. Negra — Homens, 60+ anos, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 375 | Hiato Branca vs. Negra — Homens, 60+ anos, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 377 | Hiato Branca vs. Negra — Homens, 60+ anos, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 379 | Hiato Branca vs. Negra — Homens, 60+ anos, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 382 | Hiato Branca vs. Indígena — Mulheres: faixa etaria × escolaridade — Brasil | 9 | | |
| slide 382 | Hiato Branca vs. Indígena por faixa etaria e escolaridade, só mulheres — 2º tri. 2026. | 9 | | |
| slide 385 | Hiato Branca vs. Indígena — Homens: faixa etaria × escolaridade — Brasil | 9 | | |
| slide 385 | Hiato Branca vs. Indígena por faixa etaria e escolaridade, só homens — 2º tri. 2026. | 9 | | |
| slide 389 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 391 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 393 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 395 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 397 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 399 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 401 | Hiato Branca vs. Negra — Mulheres, Baby Boomer, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 403 | Hiato Branca vs. Negra — Mulheres, Geração X, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 405 | Hiato Branca vs. Negra — Mulheres, Geração X, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 407 | Hiato Branca vs. Negra — Mulheres, Geração X, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 409 | Hiato Branca vs. Negra — Mulheres, Geração X, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 411 | Hiato Branca vs. Negra — Mulheres, Geração X, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 413 | Hiato Branca vs. Negra — Mulheres, Geração X, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 415 | Hiato Branca vs. Negra — Mulheres, Geração X, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 417 | Hiato Branca vs. Negra — Mulheres, Millennial, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 419 | Hiato Branca vs. Negra — Mulheres, Millennial, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 421 | Hiato Branca vs. Negra — Mulheres, Millennial, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 423 | Hiato Branca vs. Negra — Mulheres, Millennial, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 425 | Hiato Branca vs. Negra — Mulheres, Millennial, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 427 | Hiato Branca vs. Negra — Mulheres, Millennial, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 429 | Hiato Branca vs. Negra — Mulheres, Millennial, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 432 | Hiato Branca vs. Negra — Mulheres, Geração Z, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 434 | Hiato Branca vs. Negra — Mulheres, Geração Z, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 436 | Hiato Branca vs. Negra — Mulheres, Geração Z, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 438 | Hiato Branca vs. Negra — Mulheres, Geração Z, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 440 | Hiato Branca vs. Negra — Mulheres, Geração Z, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 442 | Hiato Branca vs. Negra — Mulheres, Geração Z, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 445 | Hiato Branca vs. Negra — Homens, Baby Boomer, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 447 | Hiato Branca vs. Negra — Homens, Baby Boomer, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 449 | Hiato Branca vs. Negra — Homens, Baby Boomer, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 451 | Hiato Branca vs. Negra — Homens, Baby Boomer, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 453 | Hiato Branca vs. Negra — Homens, Baby Boomer, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 455 | Hiato Branca vs. Negra — Homens, Baby Boomer, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 457 | Hiato Branca vs. Negra — Homens, Baby Boomer, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 459 | Hiato Branca vs. Negra — Homens, Geração X, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 461 | Hiato Branca vs. Negra — Homens, Geração X, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 463 | Hiato Branca vs. Negra — Homens, Geração X, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 465 | Hiato Branca vs. Negra — Homens, Geração X, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 467 | Hiato Branca vs. Negra — Homens, Geração X, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 469 | Hiato Branca vs. Negra — Homens, Geração X, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 471 | Hiato Branca vs. Negra — Homens, Geração X, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 473 | Hiato Branca vs. Negra — Homens, Millennial, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 475 | Hiato Branca vs. Negra — Homens, Millennial, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 477 | Hiato Branca vs. Negra — Homens, Millennial, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 479 | Hiato Branca vs. Negra — Homens, Millennial, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 481 | Hiato Branca vs. Negra — Homens, Millennial, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 483 | Hiato Branca vs. Negra — Homens, Millennial, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 485 | Hiato Branca vs. Negra — Homens, Millennial, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 487 | Hiato Branca vs. Negra — Homens, Geração Z, Sem instrução — 2012–2026 (Welch). | 6 | | |
| slide 489 | Hiato Branca vs. Negra — Homens, Geração Z, Fundamental incompl. — 2012–2026 (Welch). | 6 | | |
| slide 491 | Hiato Branca vs. Negra — Homens, Geração Z, Fundamental compl. — 2012–2026 (Welch). | 6 | | |
| slide 493 | Hiato Branca vs. Negra — Homens, Geração Z, Médio incompl. — 2012–2026 (Welch). | 6 | | |
| slide 495 | Hiato Branca vs. Negra — Homens, Geração Z, Médio compl. — 2012–2026 (Welch). | 6 | | |
| slide 497 | Hiato Branca vs. Negra — Homens, Geração Z, Superior incompl. — 2012–2026 (Welch). | 6 | | |
| slide 499 | Hiato Branca vs. Negra — Homens, Geração Z, Superior compl. — 2012–2026 (Welch). | 6 | | |
| slide 502 | Hiato Branca vs. Indígena — Mulheres: geracao × escolaridade — Brasil | 9 | | |
| slide 502 | Hiato Branca vs. Indígena por geracao e escolaridade, só mulheres — 2º tri. 2026. | 9 | | |
| slide 505 | Hiato Branca vs. Indígena — Homens: geracao × escolaridade — Brasil | 9 | | |
| slide 505 | Hiato Branca vs. Indígena por geracao e escolaridade, só homens — 2º tri. 2026. | 9 | | |
| slide 508, slide 510, slide 512, slide 514, slide 516, slide 518 … (+22) | hiato = renda média Branca − renda média do grupo, % relativo ao grupo · Welch trimestre a trimestre · ambos os gêneros · (Indígena por célula: ver heatmaps do item) | 6,9 | | |
| slide 508 | Hiato Branca vs. Negra — Baby Boomer, Sem instrução, ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 510 | Hiato Branca vs. Negra — Baby Boomer, Fundamental incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 512 | Hiato Branca vs. Negra — Baby Boomer, Fundamental compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 514 | Hiato Branca vs. Negra — Baby Boomer, Médio incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 516 | Hiato Branca vs. Negra — Baby Boomer, Médio compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 518 | Hiato Branca vs. Negra — Baby Boomer, Superior incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 520 | Hiato Branca vs. Negra — Baby Boomer, Superior compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 522 | Hiato Branca vs. Negra — Geração X, Sem instrução, ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 524 | Hiato Branca vs. Negra — Geração X, Fundamental incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 526 | Hiato Branca vs. Negra — Geração X, Fundamental compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 528 | Hiato Branca vs. Negra — Geração X, Médio incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 530 | Hiato Branca vs. Negra — Geração X, Médio compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 532 | Hiato Branca vs. Negra — Geração X, Superior incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 534 | Hiato Branca vs. Negra — Geração X, Superior compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 536 | Hiato Branca vs. Negra — Millennial, Sem instrução, ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 538 | Hiato Branca vs. Negra — Millennial, Fundamental incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 540 | Hiato Branca vs. Negra — Millennial, Fundamental compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 542 | Hiato Branca vs. Negra — Millennial, Médio incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 544 | Hiato Branca vs. Negra — Millennial, Médio compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 546 | Hiato Branca vs. Negra — Millennial, Superior incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 548 | Hiato Branca vs. Negra — Millennial, Superior compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 550 | Hiato Branca vs. Negra — Geração Z, Sem instrução, ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 552 | Hiato Branca vs. Negra — Geração Z, Fundamental incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 554 | Hiato Branca vs. Negra — Geração Z, Fundamental compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 556 | Hiato Branca vs. Negra — Geração Z, Médio incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 558 | Hiato Branca vs. Negra — Geração Z, Médio compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 560 | Hiato Branca vs. Negra — Geração Z, Superior incompl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 562 | Hiato Branca vs. Negra — Geração Z, Superior compl., ambos os gêneros — 2012–2026 (Welch). | 6 | | |
| slide 564 | Hiato Branca vs. Indígena — geração × escolaridade (ambos os gêneros) — Brasil | 9 | | |
| slide 564 | Hiato Branca vs. Indígena por geração e escolaridade, ambos os gêneros — 2º tri. 2026. | 9 | | |
| slide 592 | Uma linha por folha de renda da árvore (181 linhas): renda média real Branca, Negra e Indígena no primeiro e no último trimestre, % de crescimento de cada raça, e os hiatos em R$ (Branca-Negra e Branca-Indígena) no iníci… | 9 | | |
| slide 592 | Leitura geral: quem cresceu mais (em %) — Negra em 71 folhas, Indígena em 56, Branca em 46 — mas a diferença Branca-Negra em R$ AUMENTOU em 92 das 181. O hiato relativo cai enquanto a distância absoluta sobe. | 9 | | |
| slide 593 | Instabilidade de renda, retorno da escolaridade, Capital×Interior, desocupação×escolaridade, formal×informal, salários mínimos, Oaxaca-Blinder ano a ano, dupla desvantagem, projeção condicional (B6). | 4 | | |
| slide 595 | Se a curva de uma raça é mais inclinada, cada degrau de escolaridade 'vale' mais R$ pra ela. | 1 | | |
| slide 596 | se o ritmo de 2012–2026 (-0,78 p.p./ano) continuar: zero por volta de 2110 (2079–2231); no ritmo desde 2022 (+0,55 p.p./ano): sem data | 10 | | |
| slide 596 | A queda de 2012–2026 veio de um degrau em 2022 (B1); desde então a série está plana. Ficha: docs/studies/B6. | 1 | | |
| slide 597 | % de diferença · Welch trimestre a trimestre · série 2012–2026 | 6 | | |
| slide 599 | formal = contribui para a previdência · % de diferença · Welch · série 2012–2026 | 6 | | |
| slide 599 | A informalidade explica parte do hiato, ou ele sobrevive dentro do emprego protegido? | 4 | | |
| slide 602 | Decomposição de Oaxaca-Blinder do hiato Branca vs. Negra — ano a ano | 4 | | |
| slide 602 | controles: faixa etária + escolaridade + ocupação · parcela explicada por composição vs. não-explicada (não explicada = parte não associada às covariáveis incluídas) | 4 | | |
| slide 608, slide 609, slide 610, slide 611 | Quanto idade, escolaridade e ocupação explicam do hiato Branca vs. Negra. | 4 | | |
| slide 608 | Padronização direta: 66% bruto → 31% (+escolaridade) → 25% (+ocupação, residual). Ocupação sozinha: 34%. | C1 | | |
| slide 623 | Teste tipo Chow com EP robusto (EWC): mudança significativa em 2 dos 3 eventos (a reforma da previdência não). | 1 | | |
| slide 625 | % com carteira (só CLT, entre empregados): Branca 72%, Negra 63%, Indígena 48% (2026 T2). | 9 | | |
| slide 627 | 60+ anos: Branca 93%, Negra 80%, Indígena 72% alfabetizados. | 9 | | |
| slide 628 | Fora da força de trabalho, Negra e Indígena desistem de procurar emprego a taxas 2-4x a de Branca. | 9 | | |

## docs/img/apr_oaxaca_temporal.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | apr oaxaca temporal | 4 | | |

## docs/img/arv_escol_comb_serie_indigena.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | arv escol comb serie indigena | 9 | | |

## docs/img/arv_faixa_comb_serie_indigena.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | arv faixa comb serie indigena | 9 | | |

## docs/img/arv_geracao_comb_serie_indigena.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | arv geracao comb serie indigena | 9 | | |

## docs/img/arv_ges_homens_comb_serie_indigena.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | arv ges homens comb serie indigena | 9 | | |

## docs/img/arv_ges_mulheres_comb_serie_indigena.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | arv ges mulheres comb serie indigena | 9 | | |

## docs/img/arv_gfx_homens_comb_serie_indigena.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | arv gfx homens comb serie indigena | 9 | | |

## docs/img/arv_gfx_mulheres_comb_serie_indigena.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | arv gfx mulheres comb serie indigena | 9 | | |

## docs/img/arv_gge_homens_comb_serie_indigena.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | arv gge homens comb serie indigena | 9 | | |

## docs/img/arv_gge_mulheres_comb_serie_indigena.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | arv gge mulheres comb serie indigena | 9 | | |

## docs/img/causal_cohortes_universitaria_indigena.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | causal cohortes universitaria indigena | 9 | | |

## docs/img/causal_eventstudy_participacao_indigena.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | causal eventstudy participacao indigena | 9 | | |

## docs/img/hiato_quebra_estrutural.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | hiato quebra estrutural | 1 | | |

## docs/img/oaxaca_blinder_decomposicao.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | oaxaca blinder decomposicao | 4 | | |

## docs/img/oaxaca_blinder_quantis.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | oaxaca blinder quantis | 4 | | |

## docs/img/onda2_b1_degraus_hiato.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | onda2 b1 degraus hiato | 1 | | |

## docs/img/onda4_e3_saeb_inse_escola.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | onda4 e3 saeb inse escola | 7 | | |

## docs/img/onda5_g1_event_study.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | onda5 g1 event study | 2 | | |

## docs/img/onda6_i1_censo_pnadc.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | onda6 i1 censo pnadc | 10 | | |

## docs/img/theil_decomposicao.png

| Linha | Frase | Problema(s) | Por quê | Frase proposta |
|---|---|---|---|---|
| (nome do gráfico) | theil decomposicao | 8 | | |
