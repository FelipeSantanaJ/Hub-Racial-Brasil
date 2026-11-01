# Fase 5 — Trilha educacional: por que a escolaridade difere? (esforço alto)

Esta fase responde à pergunta central: "parte do hiato de renda é associada à escolaridade; **por que existe diferença de escolaridade**?" Usa IDs `EF1`–`EF8` (o ID `E11` já foi usado numa correção do projeto).

```text
FASE 5 — Trilha educacional. Branch: rumo8/fase5. IDs: EF1–EF8.

PERGUNTA-MÃE
Por que a escolaridade de pessoas negras é menor e em que ponto da trajetória a diferença se forma? Quanto dessa diferença é associada a renda familiar, origem, território, trabalho precoce, fluxo escolar e acesso ao superior?

PRINCÍPIOS
- Instrução é mediadora do hiato de renda (regra 4). Esta trilha NÃO prova discriminação e NÃO prova o contrário.
- Cadeia de porquês (regra 10): cada nível tem pergunta, dado, hipótese, o que refutaria e critério. Pare quando o dado acabar e registre o ponto de parada.
- Taxas de transição CONDICIONAIS (chegou até a etapa k e passou) devem ser separadas de NÍVEIS (completou k). Nível e transição não se confundem.
- PNADC é corte repetido, não painel; "coorte" é grupo de nascimento aproximado (diga isso).

DADOS
Existentes: PNADC (E1, B4), Censo da Educação Superior (E6, G1), SAEB (E3), Censo Escolar (E7), POF, Censo 2022.
Novos (autorizados pelo Felipe; baixe só de fonte oficial, registre no MANIFEST):
 - PNAD Contínua Educação (módulo anual): motivos de não frequentar/abandonar, por idade, raça e sexo. [a confirmar: anos disponíveis e nomes das variáveis no dicionário]
 - Módulo de trabalho de crianças e adolescentes da PNAD Contínua. [a confirmar: anos]
 - Suplemento de mobilidade/origem social do IBGE (se vigente). [a confirmar qual e quando]
 - Censo Escolar (matrículas, rendimento, distorção idade-série, abandono, reprovação, por cor/raça, etapa, rede, localização). Verifique se há identificador de aluno para fluxo individual; se não houver, use razão de matrículas entre séries consecutivas por coorte aparente e declare a aproximação.
 - INEP: indicadores de fluxo/trajetória, se houver corte por raça. [a confirmar]
 - SIM e SINASC (DataSUS): homicídio de 15–29 anos e gravidez na adolescência por raça (denominadores: população por raça e idade do Censo 2022, público até UF). Avalie primeiro a QUALIDADE do campo raça (ignorados) por UF e ano.

NÍVEIS (uma ficha pré-registrada por nível; o último fecha a síntese)

EF1 — O que e quando (níveis e transições)
 Pergunta: em que etapa a diferença de escolaridade entre Branca e Negra aparece, e se é diferença de ACESSO, de PERMANÊNCIA ou de CONCLUSÃO?
 Tarefas: probabilidade condicional de frequentar, concluir EF até os 16, EM até os 19, ingressar no superior aos 18–24 (dado EM completo) e concluir aos 25–29, por raça e coorte (B4); Kitagawa por etapa; compare com E1.
 Refutaria: se as transições condicionais forem iguais e a diferença só aparecer no nível, o problema é anterior (acesso inicial).

EF2 — Trabalho precoce e a escolha estudar-trabalhar
 Pergunta: jovens negros de 14–19 trabalham mais e mais cedo, e isso precede o abandono ou o segue?
 Tarefas: % que só estuda, estuda e trabalha, só trabalha, nem estuda nem trabalha, por raça, sexo e coorte; horas; renda; PNAD Educação (motivo declarado) e módulo de trabalho infantil. Cuidado: trabalhar na adolescência é mediadora e pode ser consequência do abandono (causalidade reversa); declare e use ordem temporal quando o painel permitir.
 Refutaria: se a diferença racial em trabalhar sumir após renda domiciliar e escolaridade dos pais, o mecanismo é pobreza e não raça por si.

EF3 — Fluxo escolar (Censo Escolar)
 Pergunta: onde a diferença se forma entre reprovação, distorção idade-série e abandono, por etapa, rede e localização?
 Tarefas: taxas por cor/raça (atenção: completude do campo cor/raça no Censo Escolar por ano), por etapa (EF anos iniciais, anos finais, EM), rede (pública/privada), rural/urbano; transição EF->EM; abandono no EM (1ª -> 3ª série).
 Refutaria: se a diferença some dentro da mesma escola e série, o problema é entre escolas (E7).

EF4 — Origem e território
 Pergunta: a diferença persiste entre filhos de pais com a mesma escolaridade e renda domiciliar similar, e no mesmo território?
 Tarefas: H1/H2 revisados (viés de corresidência quantificado); renda domiciliar per capita (T4); segregação escolar (E7) e residencial (D4.4); rural/urbano e UF. Resultado em LIMITES e não em partição: "sobra X–Y p.p. não associada a esses fatores".
 Refutaria: se a diferença some com origem e território, a trilha é mais socioeconômica do que racial no dado disponível (dito com a ressalva da regra 4).

EF5 — Hipóteses rivais e complementares (rodar todas, cada uma com refutação)
 R1 Gravidez, cuidado e trabalho doméstico não remunerado: SINASC (mãe adolescente por raça e escolaridade), motivos declarados de não frequentar (PNAD Educação), afazeres domésticos na PNADC (se houver), principalmente mulheres negras.
 R2 Violência e território: homicídio de 15–29 por raça e UF (SIM), segregação (D4.4/E7) e abandono por UF. Descritivo; não infira causalidade.
 R3 Distância, transporte e infraestrutura: rural/urbano, infraestrutura (E7), acesso ao EM.
 R4 Renda familiar e transferências: pobreza domiciliar (T), Bolsa Família/CadÚnico apenas em agregados públicos; G5 segue bloqueado se não houver microdado.
 R5 Qualidade da escola e do ensino: SAEB (E3) dentro da escola e com INSE médio (Fase 3), E7.
 R6 [adicione outras, se o dado indicar]: discriminação na escola (disciplina, suspensões) NÃO é observada nestes dados; registre como lacuna e não como ausência.

EF6 — Acesso e conclusão no superior
 Pergunta: entre quem concluiu o EM, a diferença no ingresso e na conclusão do superior é de acesso, de tipo de curso/IES ou de evasão?
 Tarefas: E6 revisado: ingresso, curso, IES, reserva, conclusão por coorte de ingresso, evasão. Ligue ao G1 apenas com os limites da Fase 4; não afirme efeito das cotas.

EF7 — Da escola ao salário
 Pergunta: depois de completar o mesmo nível, a renda difere? (D2.) Qual parte da trilha EF1–EF6 chega ao hiato de renda?
 Tarefas: D2 revisto (retornos, quantis, sobrequalificação) sem "controle"; "caminhos descritivos" com a sequência de associações, não decomposição causal.

EF8 — Síntese: mapa do funil
 Entregue UM mapa: cada elo (acesso -> permanência -> conclusão EF -> EM -> superior -> salário) com a diferença Branca x Negra, o EP, a classificação da evidência (descritiva / associacional / quase-causal / não identificada), o fator mais associado, e o PONTO DE PARADA da cadeia de porquês (o que o dado não deixa ver e o que seria preciso).
 Fichas EF1–EF7 devem ser consistentes com EF8; conflitos são sinalizados.

ACEITE
- Todas as fichas EF commitadas ANTES dos resultados, com refutação e frases proibidas.
- Nenhuma frase diz "explicado por" nem "devido à escolaridade"; usa "associado a" com escala.
- EF8 contém o ponto de parada de cada ramo e a lista do que exige dado novo.
- Qualidade do campo raça (Censo Escolar, SIM, SINASC) documentada antes dos resultados.
- Verificação independente de >= 10 números da trilha (regra 3).

GATE: relatório; aprovação ficha a ficha.
```

---
