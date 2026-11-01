# Passada A — Parecer de revisor externo (Hub-Racial-Brasil, Fase 0 a Onda 3)

Data: 20/10/2026. Escopo: F, S0, S0.3, S1, S1.3–S1.5, T, T4, A, B1–B6, C1–C6, D1–D6, D8. Ignorados: `conteudo/`, imagens, PPTX.
Rótulos: [VERIFICADO], [INFERIDO], [HIPÓTESE]. Referências de memória: [a confirmar].

## 1. Cobertura da leitura

**Li:**
- `docs/PLANO_DE_ANALISE.md`, `docs/studies/INDICE.md`, auditorias (rodada1, rodada2, fase0_relatorio) e `LIMITACOES_E_METODOLOGIA.md` (linhas 100–210).
- `inference/variancia.py`, `tendencia.py`, `multiplicidade.py`, `precisao.py` e `utils/populacao.py`, inteiros.
- `bloco_d.py` (gelbach, shapley, oster, sensibilidade, rif) e a lista de funções de `bloco_b.py`.
- `tests/test_variancia.py`, `tests/test_golden_pipeline.py`, `.github/workflows/ci.yml`.
- Fichas inteiras: B1, D1, D8, B2, S1.3, C2, C3, C4, C6, S1. Fichas A, F e S0: seções 3–12 (a F saiu vazia na leitura). B3–B6 e D2–D6: só seções 10–12.

**Rodei:** recálculos a partir dos microdados brutos (2012T1, 2021T4, 2022T1, 2026T2) e de 18 parquets; `_meta.json` de 3 deles.

**NÃO li:** `CHANGELOG_METODOLOGICO.md`; `LIMITACOES_E_METODOLOGIA.md` fora das linhas lidas; `agregacoes_pnadc.py` (3.151 linhas), `bloco_a.py`, `bloco_c.py`, `bloco_s.py`, `bloco_t.py`, `bloco_d_estrutura.py`, `pnadc_core.py`, `extrator_pnadc.py`, `saida.py`; `microdado_sintetico.py` e os golden files em si; fichas S0.3, S1.4, S1.5, T, T4, C1, C5, e B3–B6/D2–D6 fora das seções 10–12; `_meta.json` da maioria dos parquets.

Consequências:
- Não opino sobre a SQL de `agregacoes_pnadc.py`, que cria os números publicados. Notas de "implementação" valem para `inference/` e `bloco_d.py`.
- **Versão do código:** li o clone do GitHub (commit 862de5f). O `packed-refs` local aponta origin/main = 75cd57c. Não confirmei que são o mesmo código.

## 2. Régua do 10

Um 10 neste escopo exigiria, para cada conclusão principal:
1. O estimando publicado é o analisado (manchete e decomposição na mesma escala).
2. EP validado contra algo independente do método (pesos replicados do IBGE).
3. Datas de quebra ou degrau justificadas por evento externo, ou tratadas como estimadas; tamanho do teste verificado por simulação no modelo exato publicado.
4. Hipóteses rivais que mudam sinal ou ordem de grandeza (reclassificação, seleção, composição) testadas ou limitadas numericamente.
5. Controles que são mediadores tratados como tal na sensibilidade.
6. Todo número reproduzível de árvore de código limpa, com teste automatizado contra dados reais ou golden real.
7. Supressão com n efetivo e CV do estimando publicado.

## 3. Notas por dimensão

| Dimensão | Nota | A favor (onde) | Faltou (corrigível?) |
|---|---|---|---|
| A. População, renda, raça | 6,5 | População única documentada (`populacao.py` 52–56); P1 e P4 reproduzem exato; S0.2 testa seleção de entrada. | Reclassificação não limitada; renda só do trabalho principal. Corrigível com dados atuais. |
| B. EP e inferência | 7 | Taylor Estrato/UPA com domínio reproduz a ~3 casas; Rao-Wu como segunda implementação; auditoria pegou erro de escala dos pesos. | Validação só contra a mesma família de aproximações. Corrigível: replicados V1028001–200 existem. |
| C. Tendência e quebras | 4 | EWC + Newey-West + GLS reportados juntos; ρ dos resíduos na tabela. | Forma e data do "degrau" erradas; teste sobredimensionado. Corrigível. |
| D. Decomposição D1 | 5,5 | Gelbach fecha exato; Shapley, Oster, Cinelli-Hazlett no desenho; ficha avisa que não é causal. | Estimando ≠ manchete; mediadoras como controles. Corrigível. |
| E. Reprodutibilidade | 4,5 | Seeds explícitas; `_meta.json` por parquet; golden sintético. | CI só sintético; proveniência "-modificado"; documentação defasada. Corrigível. |
| F. Comunicação | 7,5 | "Afirmações proibidas" por ficha; E6 corrigido; regra do Theil; "não detectado" ≠ "não funciona". | Comunicação melhor que a análise em 2 pontos: degrau e reclassificação. |

## 4. Os 8 problemas mais graves

### 1. O "degrau de 2022T1 (−5 p.p.)" está mal datado e o teste é sobredimensionado
- **Localização:** `tendencia.py`, `degraus_ewc` (141–159) e `cov_ewc` (49–59); ficha B1; datas pré-registradas no plano. Dependem dele B6 ("2110") e D1-H4.
- **Rótulo:** [VERIFICADO] números; [HIPÓTESE] mecanismo.
- **Evidência:**
  - Série P1: 76,7 (2020T3) → 75,2 → 71,8 → 69,8 → 67,2 → 62,8 (2021T4) → 63,0 (2022T1) → 67,1 (2022T2). O salto 2021T4→2022T1 é +0,15 p.p. A queda foi uma rampa de ~12 p.p. em 2021.
  - Varredura de datas: SSR mínimo em 2021T2 (157) e 2021T3 (161); em 2022T1 é 294. AIC: rampa em 2021 = 222,6; degrau 2022T1 = 264,8.
  - Antes de 2020/21: média 74,3, inclinação ≈ 0,01–0,05 p.p./ano (IC NW inclui zero). Depois: média 66,0, inclinação +0,41 (IC NW −0,02 a 0,83). Diferença pós−pré = −8,32 p.p. (IC −9,26 a −7,37). A "tendência de −0,78 p.p./ano" do B1 é a descida de 2021.
  - Tamanho do teste (Monte Carlo, 400 réplicas, AR(1), modelo de 3 degraus publicado, ν=5): 19,5% (ρ=0), 23,5% (ρ=0,5), 27% (ρ=0,8) a 5% nominal. A simulação do projeto (docstring, linhas 10–13) cobriu só a inclinação. sup|t| observado 18,15 contra crítico simulado ~9–11. A mudança de nível é robusta; data, forma e ICs não.
- **Correção mínima:** tratar a data como estimada (sup-Wald/Chow com crítico simulado) e reportar "rampa em 2021; antes e depois estáveis". Retirar "degrau de 2022T1".
- **Teste de aceitação:** Monte Carlo no modelo publicado devolve tamanho 4–7% a 5% nominal; data estimada cai em 2021.

### 2. Reclassificação racial não é testada na margem que importa
- **Localização:** ficha B2 (refuta H1 testando só Preta/Parda dentro de Negra; componente −0,0004); `b2_composicao_racial_coortes.parquet`.
- **Rótulo:** [VERIFICADO] aritmética; [HIPÓTESE] seleção.
- **Evidência:** nas coortes 1950–1990, entre 2012 e 2025, % Branca cai em média −2,75 p.p., Preta sobe +3,5, Parda cai −1,2: deslocamento líquido Branca→Preta, que o Kitagawa dentro de Negra não vê. Em 2012T1, troca aleatória de 2,5 p.p. da população adulta de Branca para Negra levaria o hiato de 74,25 para 68,3 (−5,9 de 8,6 p.p. observados). Se quem troca são os brancos mais pobres, o hiato sobe para ~87–93; se são os mais ricos, cai a valores absurdos. Efeito de primeira ordem, sinal dependente da seleção não identificada.
- **Correção mínima:** trocar "H1 refutada" por tabela de limites (troca × seleção) e dizer que a seleção não é identificada.
- **Teste de aceitação:** a ficha traz a tabela e a frase permitida cita o intervalo de hiato compatível com 0–3 p.p. de troca.

### 3. O resíduo do D1 é de outro estimando que a manchete
- **Localização:** ficha D1; `d1_aninhada.parquet`; `bloco_d.py`.
- **Rótulo:** [VERIFICADO].
- **Evidência:** "78% associado / ~9 lp" é diferença de médias de ln renda (média geométrica); a manchete (hiato ~66%) é de média aritmética. PPML com as mesmas covariáveis em 2026T2: E0=0,505 (= ln 1,66), E8=0,146, 71,1% associado, resíduo ≈15,7% da renda (0,146 lp) contra ~9 lp no log-OLS. Em 2012T1: 71,5% associado.
- **Correção mínima:** reportar log-OLS e PPML lado a lado e dizer em que escala está a "parte não associada".
- **Teste de aceitação:** o E0 do modelo de decomposição fecha com ln(razão de médias) da manchete.

### 4. O EP nunca foi validado contra nada independente do método
- **Localização:** `variancia.py`; `LIMITACOES_E_METODOLOGIA.md` (razão linearização/bootstrap mediana 1,005; mín. 0,944; máx. 1,047).
- **Rótulo:** [VERIFICADO] (duas implementações da mesma aproximação "ultimate cluster"); [INFERIDO] (ordem de grandeza provavelmente correta).
- **Por que importa:** base de todo IC e da regra CV≤30%. Pesos replicados do IBGE existem nos microdados; `posest` não é usado.
- **Correção mínima:** extrair os replicados de 2 trimestres e comparar EP de média, hiato e razão.
- **Teste de aceitação:** razão EP-replicados/EP-Taylor dentro de ±10% nas células principais.

### 5. Mediadoras tratadas como controles de confusão em Oster e Cinelli-Hazlett
- **Localização:** fichas D1 e D8; `bloco_d.py`, `oster()` (δ=β_longo/mov).
- **Rótulo:** [INFERIDO].
- **Por que importa:** instrução, ocupação, vínculo e território são em boa parte consequências da raça. O movimento do coeficiente até zero mede mediação, não viés. "δ=0,85" e RV não dizem o que o texto sugere sobre omitidas. A ficha D3.4 avisa parcialmente.
- **Correção mínima:** reservar Oster/RV a um modelo só com pré-tratamento (idade, região de nascimento, coorte); chamar o resto de decomposição descritiva.
- **Teste de aceitação:** D8 distingue "mediadoras" e "pré-tratamento" na tabela de controles.

### 6. Supressão ignora n efetivo e usa o CV errado
- **Localização:** `precisao.py`, `publicavel` (42–47).
- **Rótulo:** [VERIFICADO].
- **Evidência:** em 2026T2, Indígena e Amarela × UF: 24 de 54 células aprovadas; em 9 dessas 24 o n efetivo de Kish é <30 (ex.: n=36, n_kish=32; n=31, n_kish=21). CV de n≈30 com renda assimétrica é ruidoso. O CV da média de um grupo não é o CV do hiato publicado.
- **Correção mínima:** n_kish ≥ 30 e CV do estimando publicado (hiato ou razão).
- **Teste de aceitação:** nenhuma célula publicada com n_kish < 30.

### 7. Proveniência e deriva de documentação
- **Localização:** `_meta.json` de `d1_aninhada` (commit a651cd09…-modificado) e `b1_degraus_hiato` (22180a1e…-modificado); `ci.yml`; fichas de Theil.
- **Rótulo:** [VERIFICADO].
- **Evidência:** dois parquets gerados de árvore com modificações não commitadas (`hiato_racial` tem commit limpo, c1202a10…). CI só com dados sintéticos; nenhum teste compara parquets reais com o código. Theil "entre": 6,67% na documentação (definição 14+, todos os trabalhos) × 6,96% no parquet atual (P1); o parquet reproduz, a documentação ficou defasada.
- **Correção mínima:** regenerar com árvore limpa; golden com microdado real de 1 trimestre; atualizar o texto do Theil.
- **Teste de aceitação:** CI falha se `_meta.json` tiver "-modificado" ou se o golden real divergir.

### 8. Multiplicidade e forking paths fora da família declarada
- **Localização:** C2 (interação em log das médias, β3, com controles, P4); C4 (H1 "confirmada" com −2,0 p.p., frase permitida compara 16 × 14); S1.3; D4 (coluna "+ território" adicionada após ver a primeira rodada).
- **Rótulo:** [VERIFICADO] fichas; [INFERIDO] impacto.
- **Evidência:** C2 tem várias especificações e escalas fora da conta da família FDR. S1.3 depende de dois parâmetros arbitrários (limite superior = média do grupo; piso = P10): "entre 24% e 136%" é consequência deles. C4 usa só responsável/cônjuge (corresidência diferencial por raça).
- **Correção mínima:** contar especificações na família (ou curva de especificações); declarar a amostra de C4 na frase permitida; mostrar sensibilidade de S1.3 ao limite.
- **Teste de aceitação:** cada ficha lista o nº de especificações testadas e o p ajustado as considera.

## 5. Recálculos independentes

| Número | Publicado | Meu recálculo | Diferença |
|---|---|---|---|
| Hiato P1 2012T1 | 74,245% (EP 2,367) | 74,245% (EP 2,367) | 0 |
| Hiato P1 2026T2 | 65,66% (EP 1,816) | 65,663% (EP 1,816) | 0 |
| Hiato P1 2021T4 | 62,83% | 62,828% | 0 |
| Hiato P1 2022T1 | 62,98% | 62,976% | 0 |
| Hiato P4 2012T1 / 2026T2 | 79,0% / 71,8% | 78,96% / 71,81% | ≤0,04 p.p. |
| Hiato P4 2021T4 / 2022T1 | 71,0% / 72,0% | 70,98% / 71,97% | ≤0,03 p.p. |
| Theil entre (com Amarela) 2012T1 / 2026T2 | 7,32% / 6,96% | 7,32% / 6,96% | 0 |
| Theil entre, definição histórica | 6,67% (documentação) | 6,67% | 0 (parquet atual dá 6,96%) |
| B1 inclinação | −0,784 (EWC −1,25 a −0,32) | −0,784 (−1,25; −0,32) | 0 |
| B1 degrau 2022T1 (3 degraus) | −5,0 p.p. | −4,99 | ≤0,01 |
| D1 recente: E0 / E8 / associado | 0,427 / 0,094 / 77,9% | 0,422 / 0,090 / 78,6% (só 2026T2) | pequena (1 trimestre) |
| D1 2012: E0 / E8 / associado | 0,464 / 0,101 / 78,2% | 0,457 / 0,104 / 77,2% (só 2012T1) | pequena |
| Gelbach recente (instrução; território; ocupação; vínculo; horas) | 20,9; 19,6; 19,1; 13,8; 4,6 | 21,3; 19,4; 19,0; 14,7; 5,2 | ≤0,9 p.p. |
| Oster δ (Rmax=1,3R̃) | 0,85 (recente); 0,82 (2012) | 0,81 (2026T2); 0,88 (2012T1) | ≤0,06 |
| E6, Homem Negra: efeito_genero e interação | 0 e 0 | 0 e 0 | 0 |
| E6, Mulher Negra 2026T2 | 2168,0 + 1225,2 − 638,3 = 2754,9 | confere | 0 |

Observações:
- Hiato, Taylor, Theil e B1 reproduzem exatamente, mas meu recálculo de Taylor é o mesmo método e não valida a variância (problema 4).
- D1 usa janela de 4 trimestres e eu usei 1; por isso "aproximada".
- Conferência indireta: PPML em 2026T2 dá E0=0,505, que coincide com ln(1,66) da manchete (problema 3).

## 6. Hipóteses rivais por conclusão principal

| Conclusão | Rival | Veredito |
|---|---|---|
| Hiato caiu de ~74% para ~66% | Reclassificação Branca→Negra | **Ignorada** (B2 testa o contraste errado) |
| Hiato caiu de ~74% para ~66% | Nivelamento por baixo em 2021 (Branca −16%, Negra −9% em renda média real, 2020T3→2021T4) e reversão de composição pandêmica | **Mencionada sem testar** [mecanismo = HIPÓTESE; números verificados] |
| Queda tendencial de −0,78 p.p./ano | Mudança de nível única em 2021, tendência nula antes e depois | **Não derrotada** |
| "Degrau" em 2022T1 | Rampa em 2021 | **Ignorada** |
| 78% do diferencial "associado" | Escala diferente (PPML ≈ 71%) | **Ignorada** |
| Parte não associada ≈ 9 lp | Escala aritmética ≈ 16% da renda | **Ignorada** |
| Menor presença negra em P1 é composição (S0) | Controle por escolaridade absorve desigualdade já racial | **Mencionada e declarada** (ficha S0 §9, §12) |
| Cotas: efeito não detectado | Falta de poder | **Mencionada** nos textos permitidos (arquivos do bloco T não lidos) |
| Hiato 2030+ (B6 "2110") | Forma da tendência (problema 1) | **Ignorada** |

## 7. Perguntas não feitas (valor × viabilidade)

1. **Quem estava na amostra em 2021T1–T4?** Alta viabilidade. Decompor a queda de 12 p.p. em composição de P1 (entradas/saídas) × renda dentro de P1. Hipótese: parte relevante é seleção. Refutaria: queda persiste em P4 e em coortes de nascimento. Poder: n grande.
2. **Hiato por quantil em 2021 e depois** (A3 existe nos 2º trimestres). Alta viabilidade, baixo custo. O nivelamento por baixo é no topo ou na base?
3. **EP com pesos replicados em 2 trimestres.** Média viabilidade (233 MB/trimestre), muito valor: valida tudo.
4. **Limites de reclassificação (troca × seleção).** Alta viabilidade, só aritmética.
5. **D1 em PPML na manchete.** Alta viabilidade, algumas horas.
6. **Hiato 2021T1 vs 2021T4 por posição na ocupação**, separando mudança de ocupação de renda dentro da ocupação. Média viabilidade.
7. **Tendência 2022T2–2026T2 (+0,41; IC NW −0,02 a 0,83): divergência ou ruído?** Com 17 pontos há pouco poder; o resultado provável é "indeterminado", e isso deve ser dito.

## 8. O que resiste ao ataque

- **EP e hiato por trimestre:** reproduzem exatamente a partir dos microdados (P1 e P4, 4 trimestres). A Rodada 1 pegou e corrigiu o erro de escala dos pesos.
- **Theil:** o parquet reproduz exato; a regra de contexto ("7% nunca sozinho") está escrita em ficha e regra do projeto.
- **Gelbach:** fecha exato com E0−E8 (ex.: 0,3319 em 2026T2).
- **E6:** corrigido e conferido.
- **Disciplina de rótulos:** cada ficha tem hipóteses concorrentes, "o que refutaria" e afirmações proibidas; o desvio de D4 foi declarado.
- **S0.2:** a menor presença negra em P1 não é discriminação de entrada controlada por idade, instrução, região e sexo (com a ressalva de que instrução é ela mesma desigual).

## Recomendação antes do lançamento (20/11)

- Não publicar "degrau de 2022T1" nem "queda tendencial". Usar: "o hiato caiu de ~74% para ~66% ao longo de 2021 e ficou estável desde então".
- Não publicar "78% associado" sem a escala e sem o par de contexto.
- Os itens 4 e 5 da seção 7 cabem em dias. O item 3 (pesos replicados) é o que mais ganha credibilidade, se houver tempo.
