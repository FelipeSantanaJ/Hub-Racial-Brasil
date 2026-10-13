# Auditoria científica do Hub-Racial-Brasil — Rodada 2 (cobertura pendente)

**Data:** 13/10/2026 · **Commit auditado:** `main` @ `92d9545` (após as Fases 0–2) · **Repositório alterado nesta rodada:** só arquivos de auditoria (este relatório, `src/auditoria/checagem_parquets.py`, `docs/auditoria/checagem_parquets.json`)
**Status: PARCIAL**, mas cobre o que a Rodada 1 deixou pendente (registro abaixo). Nenhum achado foi corrigido aqui: as correções entram no próximo PR, depois da sua aprovação.

---

## 0. Registro de cobertura

| Componente | Rodada 1 | Rodada 2 |
|---|---|---|
| `src/processing/agregacoes_pnadc.py` (3.023 l) | Trechos | **Lido** nos geradores de renda, escolaridade, ocupação, informalidade, horas, alfabetização, desalento, sobrequalificação, padronização direta, perfis topo/quartis, extremos, quartis multi, árvore, hiato regional/setor/capital/formal, multidimensionais, históricos, Gini/Theil, raça × gênero, dupla desvantagem, segregação, ritmo, quebra, transições, `CRIAR_BASE`. Não li linha a linha `gerar_renda_multidimensional_geracao` e `gerar_renda_completa_geracao` (espelhos das versões por faixa) |
| `src/processing/graficos_*`, `apresentacao_*` | Busca por bandas | Busca sistemática por limites de eixo, IC, suavização e rótulos; leitura das funções de hiato. **Não** abri as 721 imagens |
| `src/ingestion/extrator_pnadc.py`, `baixar_deflator.py` | Cabeçalhos | **Lidos**; deflator e versão dos microdados conferidos contra os dados |
| `docs/ANALISE_FASE1.md` | Não lido | ~25 números conferidos por amostragem contra os parquets |
| `docs/ANALISE_RACA_GENERO.md` | Não lido | **Lido**; todos os números das tabelas conferidos |
| `docs/ANALISE_CAUSAL_COTAS.md` | Não lido | **Lido**; todos os números conferidos |
| 101 parquets | 11 conferidos | **Todos**: chaves, NaN, faixas, amostra pequena; 6 consistências cruzadas (`src/auditoria/checagem_parquets.py`) |

Referências citadas de memória continuam *(a confirmar)*.

---

## 1. Resumo executivo

**O que se sustenta.** As estimativas pontuais conferem: Brasil = soma das regiões = soma das UFs; a decomposição de Theil fecha; o hiato nacional é idêntico em duas tabelas independentes; não há chaves duplicadas nem valores fora de faixa. Cerca de 20 dos ~25 números conferidos no `ANALISE_FASE1.md` batem. Todos os números do `ANALISE_CAUSAL_COTAS.md` e do `ANALISE_RACA_GENERO.md` batem, salvo os casos abaixo. O microdado é de **uma só versão, já reponderada pelo Censo 2022**: a população total de 2024 fica entre 211,7 e 212,3 milhões, contra 212,6 milhões na projeção nova e mais de 216 milhões na antiga ([IBGE](https://biblioteca.ibge.gov.br/visualizacao/livros/liv102274_informativo.pdf); [Folha PE](https://www.folhape.com.br/economia/ibge-vai-ajustar-dados-passados-de-desemprego-entenda-o-porque/427244/)). Os zips são de 15/08/2025 e a extração, de 04/09/2026. Não há quebra de reponderação: o maior salto trimestral da população 14+ é de 0,35%.

**O que não se sustenta.**
1. **[Erro, alta] `decomposicao_raca_genero.parquet`:** as 4 combinações masculinas (232 linhas) têm `efeito_genero` = R$ 1.258 e `interacao` = −R$ 1.258, quando deveriam ser 0. O código usa sempre "Mulher Branca" no termo de gênero. O documento mostra 0, então documento e tabela publicada divergem (E6).
2. **[Erro, média] Dois números do `ANALISE_FASE1.md` não se reproduzem:** desalento (texto 3,4/7,4/5,9%; dado 2,0/4,5/4,1%) e carteira assinada (texto 72/63/52%; dado 75,4/66,5/53,2%) (E7, E8).
3. **[Erro de interpretação, média] `ANALISE_CAUSAL_COTAS.md`:**
   - chama de "efeito significativo" e "resultado mais bem-identificado" um p = 0,041 numa família de 40 testes em que nenhum sobrevive ao FDR;
   - diz que eram "~6 testes";
   - omite dois p < 0,05 de participação no Centro-Oeste;
   - argumenta que "diluído ⇒ efeito real provavelmente maior" (E9).
4. **[Risco, média] Não há regra de supressão:** médias de renda publicadas com n < 30 em 12% das células nacionais e 40% das de UF de `renda.parquet`; e `n_amostra` conta pessoas sem renda, superestimando a amostra da média (R8).
5. **[Risco, média] Heaping:** os "quartis" capturam de 22% a 31% da população, não 25%, e o topo 10% chega a 11,8% (R9).

**Maior retorno:** corrigir E6 (uma linha de código + regeneração da tabela) e revisar os três documentos (E7–E9) antes de qualquer uso público.

---

## 2. Matriz de problemas

### Erros demonstrados

| ID | Problema | Gravidade | Evidência | Correção mínima | Teste de aceitação |
|---|---|---|---|---|---|
| **E6** | `gerar_decomposicao_raca_genero`: para alvo masculino, `efeito_genero` deveria ser HB − Y(Homem, Branca) = 0, mas o código usa `mb = media(base_df, "Branca", "Mulher")` sempre (`agregacoes_pnadc.py:2829`). Resultado: `efeito_genero` = R$ 1.258 e `interacao` = −R$ 1.258 nas 4 combinações masculinas, 232 de 522 linhas. `gap_total` e `efeito_raca` estão certos | **Alta** (número publicado errado) | Parquet 2026T2: Homem Negra `efeito_genero` 1258,4, `interacao` −1258,4; o docstring da função e `ANALISE_RACA_GENERO.md` §2 dizem 0 | `mb = media(base_df, "Branca", sexo_t)` e regenerar a tabela | Teste: com `sexo_t = "Homem"`, `efeito_genero == 0` e `interacao == 0`; com `"Mulher"`, os valores atuais se mantêm |
| **E7** | `ANALISE_FASE1.md:197`: desalento "Negra 7,4%, Indígena 5,9%, Branca 3,4% (2026 T2)" | Média | Parquet e microdado (desalentados ÷ fora da força, 14+): **Branca 2,0%, Negra 4,5%, Indígena 4,1%**. Nenhuma definição testada reproduz o texto | Reescrever com o número do parquet e dizer o denominador | Número do texto = parquet (tolerância de 0,1 p.p.) |
| **E8** | `ANALISE_FASE1.md:180`: carteira "Branca 72%, Negra 63%, Indígena 52%" | Média | Parquet (`pct_com_carteira`, que conta militar/estatutário como "com carteira"): **75,4/66,5/53,2**. Só CLT: 71,7/63,0/48,3. O texto não corresponde a nenhuma das duas | Escolher a definição (ver R19), regenerar e corrigir o texto | Idem |
| **E9** | `ANALISE_CAUSAL_COTAS.md` §2–3: "efeito significativo", "resultado mais bem-identificado de toda a análise", "Centro-Oeste tem o efeito mais forte e mais bem-identificado", "um p = 0,041 isolado entre ~6 testes"; e "um efeito significativo mesmo diluído é sinal de que o efeito real provavelmente é maior" | Média (interpretação pública) | São 40 testes de DiD (5 + 35), **0 sobrevivem ao BH** (menor p ajustado: 0,164 e 0,348). O texto omite que a participação de Negra (p = 0,021) e de Parda (p = 0,011) no Centro-Oeste também passa do nominal. O argumento da diluição ignora a "maldição do vencedor": um resultado selecionado por ser significativo tende a superestimar o efeito *(a confirmar: Gelman & Carlin, 2014)* | Reescrever as seções como exploratórias; estado **Bloqueado** até o B4b; reportar `did_p_valor_bh` | Nenhuma frase de "efeito significativo" sem o p ajustado na mesma frase |
| **E10** | `ANALISE_RACA_GENERO.md` §2: "gap_total = efeito_raça + efeito_gênero − interação" | Baixa | Nos dados, `gap_total = efeito_raca + efeito_genero + interacao` (soma confere nas 522 linhas). O "%" da tabela é relativo à renda do **Homem Branco**, ao contrário do hiato % do resto do Hub, que é relativo ao grupo de menor renda (C1) | Corrigir o sinal; dizer a base do % | — |
| **E11** | Docstring de `gerar_alfabetizacao` e `LIMITACOES…`: tratam `V3014` como "frequência escolar" e concluem que a cobertura (~6–8% entre 14–17) inviabiliza o indicador | Baixa | `V3014` = "Concluiu o curso que frequentou" (só se aplica a quem frequentou antes). Frequência é `V3002`, já extraída na v2. A conclusão sobre a viabilidade de E1 estava baseada na variável errada | Corrigir o texto; E1 usa `V3002` | — |

### Riscos metodológicos

| ID | Risco | Gravidade | Evidência | Correção proposta |
|---|---|---|---|---|
| **R8** | **Sem regra de precisão/supressão** em tabelas de nível. `n_amostra = COUNT(*)` conta todas as pessoas da célula, mas a média de renda é só sobre quem tem renda | Média | `renda.parquet`: 38.971 de 105.969 células com n < 30 (Brasil 12%, UF 40%, RM SP 38%); `escolaridade` 320.058 linhas com n < 30; tabelas multidimensionais de hiato com células de n = 1–8 | Colunas `n_renda` e `cv` (CV design-based); regra única (ex.: n < 30 ou CV > 30% não publica). É o ponto aberto 4 do plano |
| **R9** | **Heaping nos limiares** de quartil/decil: corte com `<`/`>=` põe todos os empatados de um lado | Média | Quartis capturam de 22,1% a 30,9% (Q4); topo 10% chega a 11,8%. Afeta as composições de `perfil_*` e `quartis_multi` | Repartir o peso dos empatados no limiar para cada fatia somar exatamente 25%/10% (ou sortear o desempate com semente fixa) |
| **R10** | Escopo "Brasil" de `extremos_*` exclui Amarela e Ignorado do universo | Baixa | Amarela = 1,35% do topo 10% nacional (2026T2); a participação Branca no topo sai inflada em ~1 p.p. | Universo com todos; Amarela explícita |
| **R11** | IC do hiato % nos gráficos = IC absoluto ÷ média Negra, ignorando a incerteza do denominador | Baixa | `graficos_fase1.py:1025-1026` | Usar `variancia.razao_delta_design` (já existe) |
| **R12** | Séries de nível com eixo truncado (base = 92% do mínimo; árvore: 90%) | Baixa (visual) | `graficos_fase1.py:166-168`, `graficos_arvore.py:102` | Manter nas linhas, mas anotar "eixo não começa em zero"; barras já começam em zero |
| **R13** | Média móvel de 4 trimestres **centrada** (usa trimestres futuros; nas pontas, menos pontos) | Baixa | `rolling(4, center=True, min_periods=2)` em `graficos_*` | Rotular "média móvel centrada" ou usar janela só para trás |
| **R14** | "Sobrequalificação" = Superior completo em "Ocupações elementares" (grupo 9) apenas | Baixa (interpretação) | `gerar_sobrequalificacao` | Dizer na legenda; ver D2.4 (índice de correspondência educação-ocupação) |
| **R15** | **Versão dos microdados não registrada**: o extrator não guarda o nome/data do zip baixado | Média | Confirmado por inferência (datas e população), não por registro. A Visita 1 de **2025** (extrato v1, usado na habitação) é da publicação anterior (input 08/05/2026; a vigente é de 23/09/2026); a v2 já usa a nova | Gravar nome do zip e `Last-Modified` no `_resumo_extracao` e no `insumos` do `_meta.json` |
| **R16** | Extrator converte em silêncio valores não numéricos para NaN (`to_numeric(errors="coerce")`) e só imprime variável ausente | Baixa | `extrator_pnadc.py` | Contar e registrar coerções; falhar se uma variável pedida faltar na série toda |
| **R17** | Renda real é rebaseada a cada trimestre novo (deflator = 1 no último trimestre): todo número em R$ "real" muda a cada atualização | Baixa (comunicação) | `baixar_deflator.py` | Sempre escrever "R$ de 2026T2"; o hash de insumos já detecta a troca |
| **R18** | Rótulo "RM São Paulo — Não-capital (proxy ABC Paulista)" | Baixa | A categoria inclui todos os demais 38 municípios da RM (Guarulhos, Osasco…), não só o ABC | "Demais municípios da RM de SP" |
| **R19** | `pct_com_carteira` conta militar/estatutário como "com carteira" | Baixa (definição) | `CRIAR_BASE`, `tem_carteira_assinada` (VD4009 = 07 → TRUE) | Renomear para "vínculo protegido" ou separar estatutários |
| **R20** | Índice de Duncan sem IC; viés para cima em amostra pequena (Indígena, pooled) *(a confirmar: Carrington & Troske, 1997)* | Baixa | `segregacao_*` | Reportar com IC por bootstrap e versão corrigida do viés |

### Comunicação

| ID | Problema | Onde |
|---|---|---|
| **C6** | "Proxy de discriminação" como rótulo do resíduo (viola a regra R5/D8) | Docstrings de `pnadc_core.decomposicao_oaxaca_blinder` e `gerar_oaxaca_blinder_temporal` |
| **C7** | Faixas aproximadas no texto: hiato regional "Sudeste 65–85%, Sul 45–55%" (dado: 62–86% e 40–54%); setor público "45–50%" (dado: 42–60%) | `ANALISE_FASE1.md:155-156, 320` |
| **C8** | "Homens negros saem do desemprego mais rápido… condiz com maior rotatividade" apresentado como explicação; é hipótese (`M`) | `ANALISE_RACA_GENERO.md` §4 |

---

## 3. O que foi conferido e passou

| Checagem | Resultado |
|---|---|
| Chaves duplicadas (101 parquets) | Nenhuma |
| Valores fora de faixa (p-valor, %, taxas, Gini, Theil, renda, pesos, Duncan, deflator; IC invertido) | Nenhum |
| Brasil = soma das regiões = soma das UFs (`renda.populacao_estimada`) | Desvio relativo máximo 1×10⁻¹⁴ |
| Theil entre + dentro = total | Exato |
| `hiato_racial`: absoluto = Branca − Negra; % = absoluto ÷ Negra | Exato |
| `hiato_arvore` (sem abertura) = `hiato_racial` | Exato |
| População 14+ estimada, salto trimestral máximo | 0,35% (sem quebra de reponderação) |
| Deflator IBGE: 27 UFs × trimestre, 1,0 no trimestre de referência, variação trimestral entre −3,95% e +2,01% | OK (o efetivo é ≈ 1,005 na referência, coerente com renda efetiva do mês anterior) |
| Padronização direta (`decomposicao_hiato_ocupacional`): suporte comum | 99,9–100% da amostra Negra incluída em todas as etapas |
| `ANALISE_FASE1.md` | Conferem: hiato R$ 2.037 (2020T3), R$ 1.513 (2021T4, mínimo), R$ 1.912 (2026T2); resíduo OB 22,4%; RIF P10/P50/P90 30,6/14,9/36,1%; P10/P50/P90 em R$; R$ 3.000 = P57,2/P75,8; renda/hora ~65%; alfabetização 60+ 93/80/72%; topo 10% Superior 38→57%/83%; Q4 Superior 71/39%; Q4 mulheres 39/33%; Theil 6,67%; Duncan setorial 10,0%; Superior completo por sexo (R$ 10.150/6.955; 6.572/4.826). Não conferem: E7, E8, C7; "Médio completo no topo: 23%" (dado: 25%) |
| `ANALISE_CAUSAL_COTAS.md` | Todos os números (tabelas de A e B, mecanismo, heterogeneidade) conferem com os parquets; o problema é interpretativo (E9) |
| `ANALISE_RACA_GENERO.md` | OB Indígena (44,5/55,5%, coef 0,263), Preta × Parda (coef 0,003, p = 0,449; P10 +, P90 −), Duncan (16,8/3,1/4,7/17,0%), ritmo (−0,85 p.p./ano, R² 0,58, ~78 anos), transições (todas as taxas) conferem. Não conferem: E6, E10 |

Detalhe: `docs/auditoria/checagem_parquets.json`.

---

## 4. Diferenças em relação à Rodada 1

| Rodada 1 | Rodada 2 |
|---|---|
| "Reponderação pós-Censo 2022: não verificado" | **Verificado**: extrato único e reponderado |
| "P03, P12–P15, P19–P25, P28, P30 não verificados" | Os números de origem dessas pautas estão quase todos no `ANALISE_FASE1.md`; ~20 conferem, mas E7/E8 atingem as pautas de desalento e informalidade **se** elas usam esses números (NÃO VERIFICADO: não tenho o mapa pauta → número) |
| Frequência escolar "não extraída" | Confirmado, e a justificativa no código estava baseada na variável errada (E11) |

## 5. O que não foi possível verificar

- **Taxa de pareamento do painel** (~68%, citada no `ANALISE_RACA_GENERO.md`): a consulta de conferência não terminou em 5 minutos. NÃO VERIFICADO.
- **Salário mínimo de 2026** (R$ 1.630, "valor anunciado" no código): NÃO VERIFICADO.
- **As 721 imagens**: não abertas uma a uma.
- **População 14+ contra a SIDRA/IBGE**: não comparada.

## 6. Riscos remanescentes

- E6 está numa tabela usada em `docs/` e possivelmente em pautas.
- Sem regra de supressão (R8), qualquer gráfico por UF ou por célula fina pode mostrar ruído como achado.

## 7. Decisões que dependem do Felipe

1. **Corrigir agora** E6 (código + regeneração de 1 tabela) e reescrever as passagens de E7–E11 e C6–C8 num PR "Fase 3b: correções da Rodada 2"? Recomendo **sim**, antes da Onda 1.
2. **Regra de supressão** (R8): n < 30 **ou** CV > 30% → não publica? Recomendo começar por essa regra e revisar no Bloco F.
3. **Heaping** (R9): repartir o peso no limiar (recomendado) ou manter e só documentar?
4. **Carteira** (R19/E8): "com carteira" só CLT e uma categoria separada "estatutário/militar"? Recomendo **sim**.
