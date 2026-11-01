# Fase 2 — Estimando, população e rivais da queda de 2021 (esforço alto)

```text
FASE 2 — Estimando, população e rivais da queda de 2021. Branch: rumo8/fase2. Corrige o problema 5 do anexo A, o filtro de população e a rival principal da narrativa "o hiato caiu".

PRÉ-REGISTRE (commit separado) o critério de manchete C1 do anexo C antes de rodar qualquer coisa.

PERGUNTAS DO MEIO DO CAMINHO (cada uma vira ficha com hipótese e refutação)
Q2.1 Quem respondeu renda? Nos ocupados, qual a taxa de não resposta de rendimento (ocupado com ocupação definida e sem VD4016) por raça e trimestre? Mudou em 2020T2–2021?
Q2.2 A troca de coleta (presencial -> telefone, 2020–21) mudou quem está na amostra ou como declara renda? Teste descontinuidades em não resposta, composição (idade, instrução, região, posição na ocupação) e distribuição de renda nas janelas de 2020T2 e do retorno ao presencial. Declare o que o dado NÃO permite separar (o microdado não traz o modo de coleta por pessoa) [VERIFICAR]; use o calendário como proxy e diga isso.
Q2.3 Composição: refaça o hiato de 2021 com a composição de P1 de 2019 (reponderação tipo DFL) e decomponha a queda de 2020T3->2021T4 em (i) entradas e saídas de P1 (quem trabalha e declara) e (ii) renda dentro de P1. A queda persiste em P4 (população mais ampla) e em coortes de nascimento?
Q2.4 Reclassificação. Use o painel da PNADC (a infraestrutura já existe no H4.2/pnadc_extraido_v2): entre as mesmas pessoas em entrevistas distintas, qual a proporção em que V2010 muda, por tipo de transição (Branca->Preta, Parda->Branca etc.), por faixa de renda e ao longo do tempo? Os que mudam têm renda diferente? Produza (a) a taxa MEDIDA de troca e (b) a tabela de limites do hiato em função da troca e da seleção (quem troca: mais pobres, mais ricos). Isso substitui o cenário aritmético da Passada A (2,5 p.p. de troca = 5,9 dos 8,6 p.p.) por limite empírico.
Q2.5 Vintage de pesos (da Fase 0): se a série mistura vintages, refaça o hiato com pesos de uma vintage única onde possível e quantifique a diferença.
Q2.6 Nivelamento por baixo: na janela 2020T3->2021T4, a renda média real caiu mais para brancos (-16%) do que para negros (-9%) [VERIFICADO pela Passada A]. Quem perdeu? Hiato por quantil (P10, P25, P50, P75, P90, P99) antes e depois, e fluxos de entrada e saída de ocupação por raça.
Q2.7 Medida de renda: renda habitual x efetiva; trabalho principal x todos os trabalhos; topo da distribuição (cauda de Pareto, topcoding). Quanto cada escolha mexe no hiato de 2012T1 e 2026T2?
Q2.8 Universo VD4016 > 0: substitua os parâmetros arbitrários do S1.3 (limite superior = média do grupo; piso = P10) por GRADE de sensibilidade; calcule limites de Manski e uma imputação (hot-deck por células raça x sexo x idade x instrução x UF) como sensibilidade, dizendo que é suposição.
Q2.9 Indígena: o hiato Branca x Indígena é 117% no Censo e 40% na PNADC (n = 958) [VERIFICADO pela Passada B]. Teste as hipóteses: universo (ocupados 18+ e VD4016 > 0), definição de renda, cobertura de terras indígenas, quesito de autodeclaração (V2010 x Censo), tamanho de amostra e pesos. Decomponha a discrepância. Regra pré-fixada: se não for explicável, a PNADC NÃO é usada para renda indígena em nenhuma peça.
Q2.10 Preta x Parda: hiato Preta x Branca e Parda x Branca separados; deriva de autoidentificação entre Preta e Parda ao longo do tempo (da Q2.4). O agrupamento "Negra" esconde algo?

ACEITE
- Manchete C1 avaliada pelo critério do anexo C, com o resultado e a faixa identificada por escrito (mesmo que mantenha a manchete).
- Tabela de limites (troca x seleção) com a taxa de troca MEDIDA.
- Não resposta de rendimento por raça x trimestre publicada em tabela.
- Decomposição composição x renda da queda de 2021, com IC.
- Indígena: discrepância 117 x 40 decomposta, ou PNADC retirada para renda indígena (registrar).
- Toda frase proposta para texto público listada em pendencias_textuais.md; nada publicado alterado.

GATE: relatório; destaque explícito se algum critério do anexo C disparou.
```

---
