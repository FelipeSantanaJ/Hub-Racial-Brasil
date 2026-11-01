# Parecer externo — Passada B (Ondas 4–6 e pós-plano)

Revisor hostil: estatística / sociologia quantitativa. Data: 20/10/2026. Repositório: `Hub-Racial-Brasil` @ 862de5f (código e docs) + cópia local de `data/raw` (insumos não versionados).
Rótulos: **[VERIFICADO]** = li o arquivo ou refiz o número; **[INFERIDO]** = consequência lógica do que li; **[HIPÓTESE]** = plausível, não testado por mim.
Scripts de recálculo (independentes do código do Hub): `/tmp/claude-0/-home-claude/8d303562-7ca9-5c39-86d8-37d49e9a4ed6/scratchpad/{g1_recalc,g1b,g1c,i1_sql,i1c,d44_recalc,h34_recalc,e3_recalc,h42_recalc,extra}.py`.

---

## 1. Cobertura de leitura

**Li (integral):** `docs/studies/INDICE.md`; fichas G1, G6, I1, D4.4, H3.4, H4.2, E3, E1, E4, H1, H2, E7; `docs/PROXIMOS_PASSOS.md`; `docs/CHANGELOG_METODOLOGICO.md` linhas 1–135; `src/processing/bloco_g.py`, `bloco_integracao.py`, `bloco_eh_externos.py`; `src/ingestion/{externos_educacao,censo_superior_painel,censo_2022}.py`; `tests/{test_bloco_g,test_bloco_integracao,test_bloco_eh}.py`; `.github/workflows/ci.yml`; `tests/conftest.py`; início de `src/auditoria/proveniencia.py`; `_meta.json` de `g1_cotas_federais` e `i1_censo_pnadc`; git log/diffs para checar a ordem do pré-registro.

**NÃO li (e portanto não opino com base nisso):** `src/processing/bloco_eh.py` (H1/H2/E1/E4 — só li as fichas e os testes); `src/inference/*` (inclui `saida.py`, onde o hash é calculado, e `variancia.py`); `ANALISE_CAUSAL_COTAS.md`; `PLANO_DE_ANALISE.md`; `LIMITACOES_E_METODOLOGIA.md`; `src/auditoria/*` (além do início de `proveniencia.py`); fichas G2–G5, E6, H3, H3.2; CHANGELOG após a linha 135; `conteudo/`, imagens e PPTX (fora de escopo). **Não refiz:** H1/H2 (−42%), E1/E4 (+3,1 × −7,7), E7, H3.2, G4/G2/G3/G5, simulação do EMD (G6), Callaway–Sant'Anna, bootstrap, p-valores de Wald, atrito bruto por raça a partir dos dois trimestres crus.

---

## 2. Régua do 10 (escrita antes das notas)

Um **10** significaria, para este tipo de projeto:

1. Qualquer número publicado é refeito por terceiro a partir do dado bruto, com o código identificado por hash, sem passos manuais.
2. Os testes cobrem também a *montagem* dos dados (filtros, junções, definições de variável), não só os estimadores.
3. Em cada desenho causal, a suposição de identificação é testada com poder adequado **ou** a conclusão é dada como limites (identificação parcial), nunca como regra binária que não poderia ter dado a outra resposta.
4. A regra de decisão pré-registrada pode, em princípio, produzir os dois resultados.
5. Os graus de liberdade do pesquisador que mais mexem no resultado (ano-base, limiar, controle, pesos, definição de categoria) têm sensibilidade reportada **com incerteza**.
6. Limitações citadas no texto são quantificadas, não só nomeadas.
7. Fontes diferentes só são declaradas "concordantes" com um critério que teria detectado discordância.
8. A redação das afirmações é derivável do resultado e do critério pré-fixado.

Nota 10 não existe em dado observacional de PNADC/Censo; a régua serve para medir a distância.

---

## 3. Notas por dimensão

| Dimensão | Nota | A favor | O que falta para 10 | Corrigível com dado atual? |
|---|---|---|---|---|
| Reprodutibilidade aritmética (bruto → número) | **8** | 20+ números refeitos de forma independente, a maioria idêntica na 4ª casa (seção 5) | Rótulo "CR1" sem fator (n−1)/(n−k); passos de ingestão só rodam com dado não versionado | Sim |
| Rastreabilidade e testes | **5** | Testes com resposta conhecida para estimadores (`test_bloco_g.py` 23–89, `test_bloco_integracao.py` 10–63); `insumos.hash` existe | Filtros/definições de ingestão sem teste (`_censo_i1`, `base_h34`, `gerar_pares`); CI roda só com dado sintético (`ci.yml`); `_meta.json` com commit "-modificado" nas tabelas do escopo (código não identificado por hash) | Sim |
| Identificação causal (G1/G6) | **6** | Pré-registro verificado por git (fichas antes dos resultados; seções 1–9 da G1 inalteradas entre 372e951 e 2b3ad27; 10b marcada como posterior); postura final conservadora | Regra de decisão assimétrica (P1); ano-base em vale (P2); EMD subestimado (P3); RR sem interpretação (P4); tratamento mal datado (P5) | Parcialmente; o núcleo (artefato de declaração) é **estrutural**: precisa de microdado individual ou de cor pré-lei |
| Inferência estatística | **7** | Variância por linearização (Estrato/UPA), cluster por escola/UPA, BH-FDR, bootstrap por instituição | Poder calculado só com 4 anos pré-lei; M̄ post hoc | Sim |
| Validade de construtos / medida | **6** | Y1/Y1b/Y1c/Y3 é a abordagem certa para o problema da cor "não declarada"; I1 corrigiu sozinho o erro de leitura de P0180 | INSE como "controle" de um mediador, com erro de medida (P6); proxy de riqueza = aluguel autodeclarado ÷ taxa arbitrária (H3.4) | Em parte |
| Consistência entre fontes | **8** | I1 e D4.4 reproduzem exatamente; converge em 4 cortes de cauda (seção 5) | Critério de "concordância" fraco (P8); D4.4 sem gradiente de escala (reportado por mim, não por eles) | Sim |
| Seleção / atrito / corresidência | **6** | Atrito medido e ajustado por células; viés de corresidência quantificado em H1 | Ajuste só por observáveis; definições T2/T3 deixam de fora trabalhadores domésticos e públicos (P7); H2 usa renda dos pais contemporânea | Em parte (H4.2: sim, com `pnadc_extraido_v2`); H1/H2: **só dado novo** |
| Disciplina de afirmação | **8** | G1 "não afirmada"; fichas listam "afirmações permitidas" e "proibidas"; erros próprios declarados | I1 reinterpreta critério pré-registrado que falhou (P8); M̄ do 10b pode ser lido como robustez ou fragilidade (P4) | Sim |

---

## 4. Os 8 problemas mais graves

### P1. A regra de decisão da G1 não podia afirmar efeito — [VERIFICADO]
**Onde:** `docs/studies/G1/ficha.md` l.148–152; `G6/ficha.md` l.50–51 e 83–84.
**Por quê importa:** a G1 pré-registra "efeitos plausíveis de 2 a 10 p.p." e exige que o IC de Y1b exclua zero. O G6 calcula o EMD de Y1b em **18,1 p.p.** (pior caso). Se o efeito verdadeiro estiver na faixa plausível, Y1b jamais excluirá zero; logo H1 era "não afirmável" **por construção**, antes de ver o dado. Simetricamente, "H2 (artefato) não refutada" também carece de poder (Y1b: −5,0, IC −20,7 a 10,6). O leitor lê "não afirmado" como "provavelmente artefato"; o dado diz só "compatível com −21 a +11 no limite conservador e +9 a +26 no limite oposto".
**Correção mínima:** trocar a regra binária por **identificação parcial**: publicar o intervalo [Y1b, Y1c] como limites e dizer que o conjunto identificado inclui zero e inclui +17. Remover "não refutada" como frase isolada.
**Teste de aceitação:** nenhum texto público contém "cotas não aumentaram" ou "cotas aumentaram"; todo texto sobre G1 traz os dois limites na mesma tela.

### P2. O ano-base 2012 é um vale; o efeito cai pela metade com base pré-lei — [VERIFICADO]
**Onde:** `bloco_g.py` l.193–205 (`event_study`, base=2012); `G1/ficha.md` l.154–156.
**O que refiz:** δ2009=5,0, δ2010=4,6, δ2011=2,9 (todos positivos em relação a 2012). Em relação à **média 2009–11**, o efeito 2016–19 é **+4,89 (EP 3,19; IC −1,4 a 11,1)** (publicado: +9,04). Com base 2011: **+6,6**. Com base 2009, δ2012 = **−5,0** (EP 4,0): em 2012 a diferença tratadas−controle estava 5 p.p. abaixo de 2009. A ficha faz a conta aritmética (9,0 − 4,1) mas a trata como "fragilidade declarada", sem EP, e o título numérico continua sendo +9,0.
**Por quê importa:** todos os derivados (Δmax do RR, comparação com o EMD, "Y1 sobe 9,0 acima do EMD") herdam o vale. Com 4,9 o efeito fica abaixo do EMD até de acordo com a própria regra.
**Correção mínima:** reportar como principal a estimativa contra a média pré-lei, com EP; manter a de base-2012 como alternativa.
**Teste de aceitação:** a tabela `g1_cotas_federais` tem as duas colunas; o texto cita a menor.

### P3. EMD subestimado e ausência de erro tipo M — [VERIFICADO/INFERIDO]
**Onde:** `G6/ficha.md` l.45–52, 83; `bloco_g.py` `emd_g1`.
**O que refiz:** EMD pior caso do G6 = 8,5. Com o EP efetivamente observado (3,10 publicado; 3,25 com fator completo), EMD = 2,8×EP = **8,7–9,1**. O EMD vem de resíduos de **4 anos** (2009–12), com ρ̂=−0,31 (viés de Nickell, [a confirmar] Nickell 1981) encolhido por 0,5. A estimativa (9,0) está **no** EMD: é exatamente o caso em que o "significativo" exagera. Com EP 3,1: efeito verdadeiro 5 → poder 36%, |estimativa| média entre significativos 8,2 (×1,6); verdadeiro 2 → poder 10%, ×3,8; verdadeiro 9 → poder 83%, ×1,1. Ou seja, **qualquer valor significativo desse desenho é, em média, ≥ 8**, seja o efeito 5 ou 9.
**Correção mínima:** reportar o EMD pelo EP realizado; incluir retrodesign (Gelman & Carlin 2014 [a confirmar paginação]); aplicar a regra "roda se EMD ≤ 10" apenas como filtro de viabilidade, não como licença de leitura.
**Teste de aceitação:** a ficha traz "exagero esperado se significativo" para a faixa 2–10 p.p.

### P4. Rambachan–Roth post hoc: M̄ de ruptura não é interpretável — [VERIFICADO/INFERIDO]
**Onde:** `G1/ficha.md` l.160–176; `bloco_g.py` `rr_magnitudes_relativas`.
**O que refiz:** M̄ de ruptura 0,931 (2013–15) e 0,171 (2016–19), contra 0,979 e 0,188 publicados (diferença = fator de pequena amostra do EP). Δmax = 2,85 = |δ2011 − 0| = o salto 2011→2012 **inteiro**. Ou seja, o "tamanho de uma violação típica de tendência" é a diferença entre 2011 e o ano-base, estimada com EP ≈ 2,2. É um único valor ruidoso, e M̄ de ruptura é função mecânica do horizonte médio h (5,5 em 2016–19 vs 2,0 em 2013–15): 0,19 versus 0,98 reflete em boa parte h, não fragilidade diferencial. A ficha lê "o efeito de 2013–2015 resiste, o de 2016–2019 não resiste nem a um quinto"; o mesmo número poderia ser lido como "o RR não distingue".
**Correção mínima:** não publicar M̄; se quiser sensibilidade a tendências, usar o HonestDiD (restrição de suavidade) ou os limites do P1.
**Teste de aceitação:** nenhuma afirmação pública depende de M̄.

### P5. "Data de tratamento 2013 para todas" é falsa nos dados; contaminação do controle — [VERIFICADO]
**Onde:** `G1/ficha.md` l.44–52; `bloco_g.py` l.140–172.
**O que refiz (painel 2012):** entre as 73 tratadas, o primeiro ano com reserva étnica ≥5% é 2013 (30), 2014 (16), 2015 (12), 2016–2020 (13) e **nunca** (2). Entre os 40 controles, **15 (46% do peso de 2012)** adotam ≥5% depois de 2012 (9 até 2015). Com controle "limpo" (nunca ≥5%, 25 instituições) o efeito é 8,6 (EP 3,5), idêntico ao relatado: a contaminação **não** produz o número, mas a leitura "2013–2015 = efeito imediato" fica sem sentido, pois o tratamento entra em coortes. Também: 5 maiores tratadas = 24% do peso; 3 maiores controles = 32% do peso do controle. Retirando um por vez dos 5 maiores controles, o efeito vai de 7,4 a 9,8.
**Correção mínima:** reportar o CS (já existe: +6,4 e +8,7) como principal ao lado do event study e dizer que a data única é nominal; documentar o prazo de implantação gradual da Lei 12.711 [a confirmar no texto da lei].
**Teste de aceitação:** a ficha apresenta a distribuição de coortes de adoção.

### P6. E3: INSE como "controle" de mediador, com erro de medida; o passo "dentro da escola" é em boa parte composição de SES — [VERIFICADO/INFERIDO]
**Onde:** `E3/ficha.md` l.57–58, 75, 120–121; `bloco_eh_externos.py` l.106–114.
**O que refiz (9º ano, LP):** bruta 21,81 (0,4236 DP); +INSE 14,71 (0,2857); dentro da escola 10,55 (0,2050) — idênticos aos publicados. INSE em 20 faixas: 14,75 (a forma funcional não importa). Mas **acrescentando o INSE médio da escola** (sem efeito fixo): **10,64 (0,207 DP)**, praticamente o mesmo que o efeito fixo. Ou seja, o INSE individual (autodeclarado, ICC entre escolas 0,46) subcorrige; o "ganho" de 14,7 → 10,6 é em grande parte contexto socioeconômico da escola, não "a escola" em sentido causal. A ficha conclui que H2 e H3 são "refutadas" porque sobram 50–70%. Com erro de medida no INSE, a fração explicada por SES está **subestimada** — o viés vai na direção de não achar o que se procura.
**Correção mínima:** reportar a sequência de razões como limites (não como partição), incluindo a especificação com INSE médio da escola.
**Teste de aceitação:** a ficha não usa "refutada" para H2/H3 sem a especificação com contexto.

### P7. H4.2: definições T2/T3 deixam de fora ocupações de maior peso para negros; atrito só em observáveis — [VERIFICADO/HIPÓTESE]
**Onde:** `bloco_integracao.py` l.407–416 (`TRANS`, `ESTADO_SQL`); `H4.2/ficha.md` l.31, 96, 113–119.
**O que refiz:** T2 −2,799; T1 +1,043; T3 +1,319 (idênticos). Atrito (da tabela publicada e de `_celulas.parquet`): 87,4% (Brancos) × 85,3% (Negros); nos estados de origem de T2/T1: sem carteira 84,7 × 82,1; desocupado 84,6 × 82,5. O ajuste por células muda a diferença de T2 de −2,80 para −2,84. Fator máximo de célula = 64. **Mas** só `VD4009 ∈ {01, 02, 09}` e `VD4002` definem estados; trabalhadores domésticos (03/04) e setor público (05–07) caem em "outro_ocupado" [códigos a confirmar no dicionário]. T2 mede "sem carteira privado → com carteira privado"; passar de doméstico sem carteira para com carteira **não conta**. Direção do viés: indeterminada, mas o grupo excluído é desproporcionalmente negro [HIPÓTESE]. O ajuste é MAR em observáveis; saída do domicílio ao perder o emprego (MNAR) não é testada.
**Correção mínima:** refazer T2/T3 com "empregado privado + doméstico" como origem e destino alternativos (dado: `pnadc_extraido_v2`); limites de Manski para o atrito.
**Teste de aceitação:** a diferença de T2 em 3 definições está na ficha.

### P8. I1: critério pré-registrado falhou e a leitura o reinterpreta; critério de concordância tem pouco poder — [VERIFICADO]
**Onde:** `I1/ficha.md` l.61, 68, 104–111.
**O que refiz:** hiato Branca×Negra Censo **69,68%**, PNADC **66,35%** (diferença 3,3, EP 2,3: z=1,4). Correlação entre UFs **0,586** (publicado 0,59) < 0,6, que a própria ficha define como refutação de H1. A ficha escreve "concordam, mas a correlação fica abaixo do limiar" e conclui "o hiato nacional da PNADC é validado pelo Censo". Pelo critério fixado, H1 foi **refutada**. Disatenuando pela confiabilidade (Censo 0,94; PNADC 0,60, EP mediano por UF da PNADC = 8,4 p.p. vs DP entre UFs de 12,0), a correlação sobe para **0,78** (ainda < 0,8 pré-registrado). O critério "≤ 5 p.p. no Brasil" com EP de 2,3 só detectaria discordâncias > ~4,5 p.p.
**Correção mínima:** escrever "H1 refutada pelo critério; ressalva: ruído amostral da PNADC por UF explica a maior parte (correlação disatenuada 0,78)". A validação nacional se apoia melhor no gráfico por corte de cauda (seção 5), não no limiar.
**Teste de aceitação:** a ficha diz "refutada" quando o critério falha.

---

## 5. Recálculos (≥ 6 pedidos; refiz 14 grupos)

Todos a partir de `data/raw` (parquets do Censo da Educação Superior, Censo 2022, SAEB 2023, POF 2017–18, PNADC 2022T3 e pares H4.2), sem importar o código do Hub.

| Número | Publicado | Meu | Diferença | Obs. |
|---|---|---|---|---|
| G1 Y1, 2016–19 (p.p.) | +9,04 (EP 3,10) | +9,04 (EP 3,25) | 0,00 (EP +5%) | EP: o Hub usa G/(G−1) sem (n−1)/(n−k) |
| G1 Y1, 2013–15 / 2020–23 | +11,44 / +1,49 | +11,44 / +1,49 | 0 | |
| G1 Y1b / Y1c / Y3, 2016–19 | −5,0 / +17,5 / −22,5 | −5,02 / +17,46 / −22,48 | ≤ 0,04 | |
| G1 δ por ano (2009–2023) | 5,01; 4,59; 2,85; 8,20; … | idênticos | 0 | |
| G1 sem pesos / limiar 10% / controle limpo | +5,8 / +7,5 / +8,6 | +5,81 / +7,53 / +8,60 | ≤ 0,03 | |
| G1 efeito contra média pré-lei | ≈5 (9,0−4,1, sem IC) | **+4,89 (EP 3,19)**; base 2011: +6,61 | — | novo (P2) |
| G1 M̄ de ruptura 2016–19 / 2013–15 | 0,188 / 0,979 | 0,171 / 0,931 | ≈ −8% / −5% | efeito do fator no EP |
| I1 hiato Branca×Negra, Censo | 69,677 | 69,677 | 0 | |
| I1 hiato PNADC 2022T3 | 66,354 | 66,354 | 0 | |
| I1 Branca×Indígena, Censo / PNADC | 116,84 / 39,97 | 116,84 / 39,97 | 0 | n indígenas PNADC = 958 |
| I1 corte P99,9 e "não imputada" | 64,84 / 70,16 | 64,84 / 70,16 | 0 | |
| I1 hiato por corte de renda (Censo / PNADC) | — | R$10 mil 39,1/40,2; 20 mil 53,4/53,8; 30 mil 60,3/59,4; 50 mil 64,8/64,0 | — | converge em todos os cortes |
| I1 correlação UF | 0,59 | 0,586 (Spearman 0,60) | 0 | disatenuada 0,78 |
| D4.4 Duncan nacional / dentro do município | 0,3899 / 0,2126 | 0,3899 / 0,2126 | 0 | |
| D4.4 aleatório (dentro) | 0,0390 | 0,0390 | 0 | |
| D4.4 setores suprimidos | 41.288 (4.047.172 pessoas) | idem | 0 | |
| D4.4 escala (grandes municípios, D − aleatório) | não reportado | setor 0,24; subdistrito 0,18; distrito 0,08 | — | blocos de 10 setores consecutivos: 0,21 |
| E3 9º LP: bruta / +INSE / dentro da escola (DP) | 0,4236 / 0,2857 / 0,2050 | idem (4 casas) | 0 | |
| H3.4 razão de riqueza (cap fixo) / variável | 2,03 / 2,20 | 2,025 / 2,204 | 0 | |
| H3.4 média Negra, cap 5% | R$ 27.198,6 | R$ 27.198,6 | 0 | |
| H4.2 T1 / T2 / T3 (Negra − Branca, p.p.) | 1,043 / −2,799 / 1,319 | 1,043 / −2,799 / 1,319 | 0 | EP (UPA) 0,19 / 0,125 / 0,049 vs 0,19 / 0,123 / 0,049 |

**Hipótese que eu levantei e foi refutada:** dupla contagem em `ALUGUEL_ESTIMADO` (H3.4). O arquivo tem **1 linha por domicílio** (48.935 linhas = 48.935 domicílios; `FATOR_ANUALIZACAO`=1; `QUADRO`=00); soma = primeira linha = média. Sem dupla contagem. 5% dos aluguéis são imputados (`COD_IMPUT_VALOR`=1).

**Não consegui refazer:** H1/H2 (−42%), E1/E4 (+3,1 × −7,7), E7, H3.2, G4 (exigem PNADC anual/Censo Escolar que não carreguei); o atrito bruto por raça a partir dos dois trimestres crus (usei a tabela publicada); a simulação AR(1) do EMD; Callaway–Sant'Anna; o bootstrap.

---

## 6. Hipóteses rivais por conclusão principal

| Conclusão | Rival | Veredito |
|---|---|---|
| G1: "Y1 sobe; compatível com artefato de declaração" | Efeito real da lei | **Mencionada, não testável** com este dado (P1) |
| | Reversão à média / vale em 2012 | **Mencionada sem teste** → testada por mim: efeito 4,9 (IC −1,4 a 11,1) |
| | Contaminação do controle por leis estaduais | **Testada** pelos autores (8,6) e por mim: **derrotada** como fonte do número |
| | REUNI/SiSU/expansão | Mencionada (H3); sem teste; pré-tendência fraca |
| | Mudança no preenchimento institucional do campo cor | [HIPÓTESE]; ignorada (a queda de Y3 é o mesmo fenômeno) |
| E3: "a diferença não é sobretudo SES nem escola" | Erro de medida do INSE / SES não observado | **Ignorada** → testada por mim: −28% com INSE médio da escola |
| | Forma funcional do INSE | **Derrotada** (20 faixas: 14,75 vs 14,71) |
| H4.2: "desvantagem de T2 é composição" | Atrito seletivo | **Testada** (−2,80 → −2,84): derrotada em observáveis; MNAR não testado |
| | Definição de categoria (doméstico/público) | **Ignorada** (P7) |
| H3.4: "riqueza imobiliária 2,0×" | Dupla contagem do aluguel | **Derrotada** (por mim) |
| | Cap rate constante por faixa | **Mencionada**: 2,03 → 2,20 é puramente suposição |
| | Aluguel autodeclarado enviesado por região/raça | **Parcialmente** (controle UF/décimo); sem teste direto com `INVENTARIO` |
| I1: "Censo e PNADC convergem" | Cauda de renda | **Testada** (P99,9): Censo−PNADC 0,8±1,95 |
| | PNADC com peso pré-Censo | Testada: %Negra 20+ 54,84 vs 54,92: **derrotada** |
| D4.4: "segregação 0,21 dentro do município" | Viés de unidades pequenas | **Tratada** (benchmark binomial, 0,039) |
| | MAUP | **Ignorada** → testada por mim: gradiente 0,24 → 0,18 → 0,08 |

---

## 7. Perguntas não feitas (valor × viabilidade)

Cada uma com dado, hipótese, o que refutaria e poder. Não recomendo rodar todas.

1. **G1 dose-resposta:** entre as 73 tratadas, ΔY1 (2016–19 vs 2009–11) regride em ΔY3 (queda de não declarados) e na parcela `QT_ING_RVETNICO/QT_ING`. *Dado:* o mesmo painel. *Hipótese:* se é artefato, ΔY1 acompanha ΔY3; se é efeito real, acompanha a reserva étnica. *Refuta:* coeficiente de ΔY3 ≈ 0 com IC excluindo o valor previsto pelo artefato. *Poder:* moderado (73 unidades), vale a tentativa porque custa horas. **Alto valor, alta viabilidade.**
2. **H3.4 validação com `INVENTARIO`:** comparar a razão aluguel/cap com o valor declarado de imóveis nos inventários da POF. *Dado:* `pof_inventario.parquet` já no repositório. *Refuta:* razão por raça fora de 2,0 ± 0,3. *Poder:* alto (178 mil moradores). **Alto valor, média viabilidade.**
3. **H4.2 definições alternativas** (P7). *Dado:* `pnadc_extraido_v2`. **Médio valor, média viabilidade.**
4. **E3 cota de erro de medida:** reportar a razão com INSE médio da escola como limite inferior da parte "não SES". **Médio valor, baixa dificuldade** (já feito acima).
5. **D4.4 em três escalas** (setor, subdistrito, distrito) na tabela principal. **Médio valor, baixa dificuldade.**
6. **H1/H2 com suplemento de mobilidade** (PNAD, dado novo) para testar a seleção por corresidência na elasticidade, não só no nível. **Alto valor, mas é dado novo — não rodar agora.**

---

## 8. O que resiste ao ataque

- **Integridade do pré-registro** (git) e honestidade dos desvios declarados (P0180, SAEB sem peso, 18+ → 20+).
- **Aritmética:** 20+ números idênticos na 4ª casa a partir do bruto; sem dupla contagem na POF.
- **I1 como evidência de convergência distribucional:** Censo e PNADC acompanham-se em quatro cortes de renda (39/40, 53/54, 60/59, 65/64), e a composição racial 20+ coincide (54,92 × 54,84). Essa evidência é mais forte que o critério pré-registrado.
- **D4.4:** benchmark binomial correto (reproduzido) e o excesso de Duncan sobrevive a blocos de até 10 setores (0,24 → 0,21); não é artefato de setores pequenos. Mas é função da escala administrativa.
- **E3 / H4.2 / H3.4:** resultados estáveis a forma funcional do INSE, ao ajuste de atrito e ao conjunto de pesos; as conclusões qualitativas (hiato persiste com SES; diferença de formalização é majoritariamente composição) não mudam com meus testes, só ficam menos categóricas.
- **A postura final da G1** ("não afirmado") é a correta; o problema é como ela é derivada e comunicada (P1–P4), não o veredito.

---

### Resumo do que mudaria uma linha pública

1. G1: sempre com os dois limites (Y1b, Y1c) e com a estimativa contra média pré-lei (+4,9, IC −1,4 a 11,1), nunca "+9,0" sozinho.
2. I1: "H1 refutada pelo critério; correlação disatenuada 0,78; convergência robusta aos cortes de renda".
3. E3: razões como limites, com a especificação de contexto.
4. H3.4: "2,03× (cap fixo); 2,20× se cap varia com o valor (suposição)".
5. D4.4: sempre "no setor censitário (~460 pessoas); com unidades maiores o número cai".
