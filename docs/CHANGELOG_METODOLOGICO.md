# Changelog metodológico

Registro de toda mudança que altera (ou pode alterar) um número publicado ou a forma de
calculá-lo: data, o quê, por quê, impacto. Mais recente primeiro.

---

## 13/10/2026 — Onda 2: Blocos B e C (branch `onda2/b-c`)

- **Decisões do Felipe (14/10/2026):** ficha C6 aprovada com ressalvas; PRs #8 e #9 liberados para mesclagem; Onda 3
  autorizada. Nenhum número muda.

- **Decisões do Felipe (13/10/2026, depois do PR #9):** fichas B1–B6 e C1–C5 aprovadas com ressalvas; EWC aceito;
  a leitura "degrau em 2022, sem tendência contínua" passa a ser a principal do Hub (README e deck); C6 feito
  (ficha proposta); gráficos das Ondas 1 e 2 no deck publicado (seção "Leitura principal", 18 slides; 635 no total).
- **Aprofundamentos:** saiu `apr_convergencia.png` (extrapolação linear até "fecharia por volta de 2078", sem IC nem
  premissa na tela), substituída pela projeção condicional do B6; legenda da quebra estrutural no deck corrigida
  ("2 dos 3 eventos").
- **Linhas internacionais de pobreza em PPC (T2, feitas depois de o Felipe liberar a leitura dos dados externos):**
  US$ 3,00, 4,20 e 8,30 por pessoa por dia (PPC de 2021; nota do Banco Mundial de 05/06/2025), convertidas para R$
  nominais do ano por mês: linha_R$(ano) = US$/dia × PPC_2021 × IPC(ano)/IPC(2021) × 365/12, com PPC_2021 =
  `PA.NUS.PRVT.PP` (2,4499 R$/dólar internacional) e IPC = `FP.CPI.TOTL` (API v2 do Banco Mundial, acesso em
  13/10/2026). Em 2025: R$ 280,06, 392,08 e 774,82. Insumo `data/processed/linhas_pobreza_ppc.parquet`
  (`src/ingestion/linhas_pobreza_ppc.py`; IPC disponível para 2012–2025, nenhum ano sem linha). O `t2_pobreza` passa
  de 462 para 924 linhas; as 462 antigas saíram **idênticas** (dif. máx. rel. 6,5e-16;
  `docs/auditoria/antes_depois_pre_ppc.json`; legado em `data/processed/_legado/pre_ppc/`). O `antes_depois` passou a
  comparar só as linhas que já existiam quando uma tabela ganha linhas. Resultado: em 2025, 31,9% (31,4–32,5) das
  pessoas negras abaixo de US$ 8,30 × 16,4% (15,9–17,0) das brancas; razão ~2× nas três linhas, como nas linhas em
  salário mínimo. Ressalva na ficha T: não são as taxas oficiais do Banco Mundial para o Brasil (renda habitual
  nominal da PNADC, IPC nacional, sem deflação espacial). Nenhum número publicado antes muda.

- **Estudos novos** (fichas B1–B6 e C1–C5 com hipóteses escritas antes de rodar; `src/processing/bloco_b.py`,
  `bloco_c.py`, `graficos_onda2.py`). Sempre com a versão do Bloco T ao lado (P4 e/ou renda domiciliar per capita).
- **R6 (refeito, muda números publicados):** `ritmo_convergencia_hiatos` e `quebra_estrutural` passam a EP EWC
  (`src/inference/tendencia.py`), com Newey-West e GLS AR(1) ao lado; "tendência confiável" = os três IC excluem
  zero (antes: R² ≥ 0,1). Inclinações pontuais iguais; Branca × Indígena segue sem tendência confiável; no teste tipo
  Chow (com BH entre os 3 eventos) a **reforma da previdência deixa de ser significativa**; o coeficiente de patamar
  passa a medir o salto na data do evento. Saem da tabela de ritmo a série suavizada de Branca × Indígena e o "anos
  para zerar" (substituído pelo B6). Antes × depois: `docs/auditoria/antes_depois_pre_b1_onda2.json`; legado em
  `data/processed/_legado/pre_b1_onda2/`. Textos atualizados: `ANALISE_FASE1.md`, `ANALISE_RACA_GENERO.md`,
  `LIMITACOES_E_METODOLOGIA.md`; gráfico `hiato_quebra_estrutural.png` regenerado.
- **Principais achados:** a queda do hiato P1 foi um degrau de −5 p.p. em 2022, não tendência contínua (B1); o
  hiato entre todos os adultos é contracíclico (+1,6 p.p. por p.p. de desocupação, B5); a reclassificação racial
  existiu mas não fabricou convergência (B2); na base da distribuição o hiato aumentou (B3); coortes nascidas depois
  de 1990 têm hiato menor na mesma idade (B4); sem data finita de paridade no ritmo pós-2022 (B6); raça responde por
  ~2/3 da distância homem branco − mulher negra entre ocupados e ~metade entre todos os adultos (C3); trabalho
  doméstico: 14% das ocupadas negras × 8% das brancas (C5).
- `_meta.json` de tabelas gravadas antes de o catálogo ter a entrada foram corrigidos só em `populacao` e `insumos`.

---

## 13/10/2026 — Pendências da Onda 1 (branch `onda1/pendencias`)

- **Decisões do Felipe (13/10/2026, depois do PR):** fichas S0.3, S1.3, S1.4, S1.5 e T4 aprovadas com ressalvas;
  EWC aceito como método principal de tendência; download do fator de PPC autorizado (linhas internacionais do T2:
  ver a entrada da Onda 2).

- **Estudos novos** (fichas com hipóteses escritas antes de rodar; `src/processing/bloco_s.py`, `bloco_t.py`):
  S0.3 (perfis de quem está fora de P1), S1.3 (limites do hiato; sem Heckman), S1.4 (Pr(P1) × horas × renda por
  hora), S1.5 (seleção no tempo, por episódio) e T4 (décimos de renda domiciliar per capita). Nenhum número já
  publicado muda.
- **Tendência com autocorrelação (`src/inference/tendencia.py`, base do B1 da Onda 2).** Por simulação, Newey-West
  com defasagem 4 cobre só ≈ 78% (nominal 95%) com AR(1) de 0,7 em 58 trimestres. Adotado o EWC (cossenos com pesos
  iguais, t com ν = 5 g.l.; ≈ 89% no mesmo cenário), com Newey-West e GLS AR(1) reportados ao lado; "tendência
  confiável" só quando os três excluem zero. Nenhum método é confiável com ρ ≥ 0,9.
- **R11 (gráficos):** a banda de IC do hiato % (`hiato_racial_percentual.png`, `hiato_preta_parda_percentual.png`)
  passa a usar o método delta (`a2_metricas_hiato`; nova `a2_metricas_hiato_preta_parda`), em vez do IC absoluto ÷
  média do grupo. Diferença pequena (≈ 0,1 p.p. no limite em 2026), mas o método antigo ignorava o denominador.
- **F4:** o % de rendas em múltiplos de R$ 1.000 dobrou (17% → 40%) por **composição nominal** (+29,5 p.p.), não
  por mais arredondamento (−7,3 p.p. dentro de faixas fixas): `heaping_renda_faixas`.
- **F6:** todos os gráficos de série marcam recessão 2015–16 (hachura), pandemia / telefone 2020–21 (faixa) e o
  questionário de educação de 4T2015 (linha pontilhada) — `graficos_fase1.marcar_quebras`.
- **Árvore:** células sem dado publicável não geram mais imagem vazia ("Amostra insuficiente"); o gráfico e a folha
  do deck são suprimidos (3 casos: mulheres sem instrução, hiato vs. Indígena/Negra).
- **Linhas de pobreza em PPC (T2):** seguem pendentes (exigem baixar o fator de PPC; sem autorização do Felipe).

---

## 13/10/2026 — Decisões do Felipe sobre a Onda 1 (branch `onda1/pendencias`)

- Fichas F, S0, S1, T e A **aprovadas com ressalvas** (deixam de ser "proposto").
- Salário mínimo de 2026 = **R$ 1.621** confirmado pelo Felipe. Nenhum número muda.

---

## 13/10/2026 — Onda 1, parte 2 (branch `onda1/parte2`)

- **Faixa 14–17 de volta às tabelas (correção pedida pelo Felipe).** A parte 1 tinha tirado a renda de 14–17 das
  tabelas; o pedido era só não usá-la nas análises. `renda`, `renda_completa`, `renda_multidimensional_faixa` e
  `horas_trabalhadas` voltam a ter 14–17 (ocupados 14+ com `VD4016` > 0; colunas `renda_14mais_*` da `CRIAR_BASE`).
  Valores de 18+ **idênticos** nas quatro tabelas. Gráficos e `tabela_crescimento` ignoram 14–17 ao combinar células
  (`graficos_fase1.FAIXAS_FORA_DAS_ANALISES`); 677 das 682 imagens ficaram idênticas e 5 heatmaps perderam a coluna
  14–17 vazia. Tabelas sem faixa etária (por escolaridade, geração, faixas de SM) seguem 18+.
- **`openpyxl`** nos requirements; `docs/tabela_crescimento_renda.xlsx` regenerado (coerente com o CSV).
- **Rodapé dos gráficos encurtado**: o texto da parte 1 ficava cortado nas figuras de 10 polegadas.
- **Salário mínimo de 2026 = R$ 1.621** (era R$ 1.630, não verificado; ver `LIMITACOES…`). `faixas_salario_minimo`
  regenerada: só 2026 muda (até −0,4 p.p.).
- **Bloco T (T1–T3)** — `src/processing/bloco_t.py`, ficha `docs/studies/T`. Hiato da renda domiciliar per capita
  Branca × Negra 98,7% (2012) → 81,7% (2025); pobreza (½ SM) 39,3% → 29,3% entre pessoas negras, 18,5% → 14,8% entre
  brancas; domicílios chefiados por mulheres negras: hiato de 145% em relação aos chefiados por homens brancos.
- **Bloco A (A2–A7)** — `src/processing/bloco_a.py`, ficha `docs/studies/A`. Quatro métricas do hiato com IC; hiato
  por quantil com bootstrap Rao-Wu; Theil L; representação por décimo e razão de chances (topo 10%: 0,32); dominância
  estocástica (Branca domina Negra em todos os anos).
- **Decisão (delegada):** Bloco T vira eixo principal (`PLANO_DE_ANALISE.md`).
- Gráficos novos: `docs/img/onda1_*.png` (`src/processing/graficos_onda1.py`).

---

## 13/10/2026 — Onda 1: regeneração única com a população de referência (branch `onda1/regeneracao`)

Decisões dos Pontos de parada 2 e 3. **Tudo abaixo já vale nos parquets, gráficos e decks.**

### População e renda de referência em todas as tabelas de renda

- **O quê.** `renda_habitual_*`/`renda_efetiva_*` da `CRIAR_BASE` passam a ser `VD4016`/`VD4017`
  (trabalho principal) **só para a população de referência** (ocupados 18+ com `VD4016` > 0;
  `populacao.sql_colunas_renda_tabelas`). Todo gerador de renda migra sem mudar código; o recorte
  histórico fica em `renda_todos_trabalhos_*`. Tabelas de outros indicadores (escolaridade, ocupação,
  desalento, alfabetização, sobrequalificação, informalidade, segregação, transições) mantêm o universo
  14+ do indicador. Renda por hora: `VD4016` ÷ horas do trabalho principal (`V4039`). Gini e Theil
  incluem Amarela (A4). Produção passa ao **extrato v2** (idêntico ao v1 nas colunas comuns: 0 linhas
  diferentes em 58 trimestres, `docs/auditoria/extrato_v1_v2_identicos.json`).
- **Impacto medido** (`docs/auditoria/antes_depois_onda1.json`; legado em
  `data/processed/_legado/pre_onda1_1bd6472/`): hiato % Branca × Negra cai em média **1,36 p.p.**
  (−2,52 a +0,02; 2012T1 75,8 → 74,2%; 2026T2 66,2 → 65,7%), igual à prévia da Fase 2; os 58
  trimestres seguem significativos após o FDR (z de 19,5 a 37,2). Branca × Indígena 2026T2: 72,7 →
  70,9%. Theil entre raças 6,67 → 6,96%. Resíduo de Oaxaca-Blinder (3 controles) 22,4 → 22,8%.
  Tabelas que não são de renda: **pontos idênticos** (`antes_depois_onda1_rotulo_rmsp.json`, com o
  rótulo novo da RM SP mapeado). A faixa 14–17 sai das análises (37 imagens da árvore e 2 da galeria
  removidas; 682 imagens em `docs/img`); a renda dela volta às tabelas por faixa etária na parte 2
  (ver a entrada seguinte).
- Itens 2–4 da Fase 3b passam a valer: supressão (`n_*`, `cv_*`, `publicavel*`), heaping (fatias de
  exatamente 10/25%), carteira só CLT (2026T2: 71,7 / 63,0 / 48,4%).

### Correção: ponderação das médias nos gráficos (achado da Onda 1)

- **O quê.** Os gráficos combinavam células (sexo, faixa, Preta + Parda) ponderando a média de renda por
  `populacao_estimada` (todas as pessoas da célula) em vez do peso de quem tem renda. As tabelas de nível
  passam a gravar `peso_<ind>` (Σ pesos no denominador de cada indicador) e `graficos_fase1.peso_para` /
  `media_ponderada_celulas` ponderam por ele (também em `graficos_aprofundamentos` e
  `tabela_crescimento`).
- **Por quê / impacto.** Com a ponderação antiga, sobre as tabelas antigas, o hiato % dos gráficos ficava
  **4,3 p.p. acima** do hiato do microdado em média (+1,2 a +8,1) e a renda média Negra de 2026T2 saía
  R$ 2.687 em vez de R$ 2.888. Agora o gráfico reproduz o hiato oficial (65,7% em 2026T2). Números de
  texto tirados dos gráficos (ex.: renda por escolaridade) herdavam o viés e foram recalculados.

### Bloco F e Bloco S (Onda 1)

- `src/processing/sensibilidade_populacao.py` e fichas `docs/studies/{F,S0,S1}/ficha.md`. **Resultado
  central:** P2 e P3 ≈ P1; **P4 (todos os adultos, zero para não ocupados) aumenta o hiato em 8,9 p.p. em
  média (17,5 entre mulheres; "diferença grande" em 40 de 58 trimestres, 58 de 58 entre mulheres)** e
  **P5 (domiciliar per capita) em 12 a 22 p.p. (grande nos 14 anos)**. Pelo critério do plano, o Bloco T
  vira eixo principal (decisão pendente no Ponto de parada da Onda 1).

### Textos e decks

- `ANALISE_FASE1.md`, `ANALISE_RACA_GENERO.md`, `ANALISE_CAUSAL_COTAS.md` e `README.md` com os números
  novos. Duas afirmações caíram: o hiato do Baby Boomer "cresce" (não sustentado) e a tendência de alta do
  hiato Branca × Indígena (inclinação bruta p = 0,11; só a série suavizada sobe, sem HAC). No Desenho B das
  cotas, o hiato de renda nacional passa a p = 0,014 (p_BH = 0,072) — segue sem sobreviver ao FDR.
- O deck publicado `Datahub_Racial_Brasil_Fase1.pptx` é gerado por `apresentacao_final` (620 slides;
  eram 657 com as folhas 14–17); `apresentacao_fase1` gera um deck antigo e não deve sobrescrevê-lo
  (README corrigido). `Datahub_Racial_Brasil_ARVORE.pptx` regenerado (534 slides; o arquivo anterior,
  412 slides, já não correspondia ao código — NÃO VERIFICADO desde quando).
- `docs/tabela_crescimento_renda.csv` regenerado; **`docs/tabela_crescimento_renda.xlsx` NÃO** (falta
  `openpyxl` no ambiente) e por isso está **desatualizado e diverge do CSV** até ser regerado.

---

## 13/10/2026 — Etapa 2, Fase 3b: correções da Rodada 2 (branch `auditoria/fase3b-correcoes`)

Origem: `docs/auditoria/rodada2.md` e decisões do Ponto de parada 3 (13/10/2026). Só o item 1
(E6) **já vale** nos parquets; os itens 2–4 estão no código e testados, mas **só valem na
regeneração única da Onda 1**.

### 1. E6 — decomposição raça × gênero com alvo masculino — **JÁ VALE (tabela regenerada)**

- **O quê.** `gerar_decomposicao_raca_genero` usava sempre Mulher Branca no termo de gênero
  (`mb = media(base_df, "Branca", "Mulher")`). Agora usa a Branca do mesmo sexo do alvo; o
  cálculo saiu para `decompor_raca_genero` (função pura, `tests/test_decomposicao_raca_genero.py`).
- **Por quê.** Com alvo masculino, `efeito_genero` = HB − Y(Homem, Branca) = 0 por definição; a
  tabela publicada trazia R$ 1.258 (2026T2) e a `interacao` compensava com −R$ 1.258.
- **Impacto medido** (`docs/auditoria/antes_depois_e6.json`; cópia anterior em
  `data/processed/_legado/pre_e6_138151e/`, local): mudam **só** `efeito_genero` e `interacao`
  das **232 linhas masculinas** (diferença máxima R$ 1.489); `gap_total`, `efeito_raca`, rendas,
  p-valores e as 290 linhas femininas ficam idênticos (|dif| ≤ 3×10⁻¹²). A soma
  `gap_total = efeito_raca + efeito_genero + interacao` fecha nas 522 linhas.
- Regenerada com `python -m src.auditoria.regenerar_tabela gerar_decomposicao_raca_genero`, que
  materializa a `CRIAR_BASE` e chama só esse gerador (a função usa `renda_habitual_real`, que a
  troca de população não afeta).

### 2. Regra de supressão (R8) — **no código; vale na regeneração da Onda 1**

- **O quê.** As tabelas de nível ganham, para cada indicador, `n_<ind>` (n do DENOMINADOR),
  `cv_<ind>` (CV design-based) e `publicavel_<ind>`, mais `publicavel` (indicador principal).
  Regra: **n ≥ 30 e CV ≤ 30%**; estimativa zero ou CV indefinido ⇒ não publicável. Nenhum valor é
  apagado. A regra vai no `_meta.json` (`regra_supressao`). Tabelas: `renda`, `renda_por_*`,
  `renda_completa*`, `renda_multidimensional_*`, `escolaridade`, `ocupacao`,
  `desocupacao_por_escolaridade`, `informalidade`, `horas_trabalhadas`, `alfabetizacao`,
  `desalento_subutilizacao`, `sobrequalificacao`, `faixas_salario_minimo`.
- **Como.** `src/inference/precisao.py` combina totais por (célula, estrato, UPA) somados no
  DuckDB pela fórmula de `variancia_linearizada` (domínio = célula). Validação em 2026T2
  (`python -m src.auditoria.validacao_cv`; `docs/auditoria/validacao_cv.json`): diferença relativa
  máxima **2×10⁻¹⁵** contra `erro_padrao_media_design` sobre o microdado, em 120 células (renda
  média, proporção com carteira e total ponderado).
- **Por quê.** `n_amostra = COUNT(*)` conta quem não entra no indicador e não havia regra: 12%
  das células nacionais e 40% das de UF de `renda.parquet` tinham n < 30.
- **Impacto previsto.** Só colunas novas; nenhum número muda. Em `renda` 2026T2, passam na regra
  78,9% das células do Brasil, 64,6% das regionais, 53,2% das de UF e 46,6% das da RM de SP. O
  golden-file de `renda` foi regerado (intencional): as 13 colunas antigas ficam idênticas e
  entram 4 colunas novas.

### 3. Valores redondos nos limiares de quantil (R9) e Amarela em `extremos` (R10) — **no código; vale na regeneração da Onda 1**

- **O quê.** `pnadc_core.fracao_na_fatia` dá a cada observação a fração do seu peso que cai na
  fatia [q_inf, q_sup] da distribuição ponderada, e reparte o peso de quem está empatado no limiar.
  Cada fatia soma **exatamente** 10% (topo/base) ou 25% (quartis). Usada (via `_fatia_ponderada` /
  `_quartis_ponderados`) em `gerar_perfil_topo10_racial`, `gerar_perfil_quartis_racial`,
  `gerar_perfil_topo10_quartis_pretaparda`, `gerar_perfil_topo10_quartis_indigena`,
  `gerar_extremos_racial` e `gerar_quartis_multi_racial`. `n_topo10`/`n_quartil`/`n_extremo`
  passam a contar quem tem fração > 0. R10: o escopo `brasil` de `extremos_distribuicao_racial`
  e o escopo `genero` incluem Amarela no universo e nas raças reportadas (escopo `genero` acrescentado
  por decisão de 13/10/2026, após o PP3). Ignorado fica sempre fora.
- **Por quê.** Com renda declarada em valores redondos, o corte `>= limiar` capturava de 22% a 31%
  nos quartis e até 12,8% no topo 10%.
- **Impacto previsto** (prévia 2026T2, sem gravar parquet): o topo 10% passa de 11,5% (Branca) e
  12,8% (Negra) de captura para 10,0%. Os quartis Negra passam de 23,6/23,2/22,4/30,9% para 25% cada.
  Superior completo no topo 10%: Negra 56,9% → 61,4%; Branca 83,0% → 84,3%. No topo 10% nacional,
  a participação Branca vai de 67,3% (antes, sem Amarela, corte simples) para 67,3% (com Amarela e
  repartição): os dois efeitos se compensam (−0,9 p.p. de Amarela, +0,9 p.p. da repartição). Amarela
  = 1,45%. **Números do `ANALISE_FASE1.md` sobre o topo e os quartis mudam na Onda 1.**
- Testes: `TestFracaoNaFatia` (soma = 100%; sem empates, igual ao corte simples salvo a observação
  que contém o limiar; massa empatada ⇒ fatias exatas) e `tests/test_heaping_tabelas.py`
  (geradores sobre sintético com 20% em R$ 3.000: captura = 10/25 exatos; composições somam 100).

### 4. Carteira assinada = só CLT (R19/E8) — **no código; vale na regeneração da Onda 1**

- **O quê.** Na `CRIAR_BASE`, `tem_carteira_assinada` = TRUE só para VD4009 01/03/05, FALSE para
  02/04/06 e NULL para o resto. Até aqui o 07 (militar/estatutário) era TRUE. Nova coluna
  `vinculo_trabalho` (CLT, Sem carteira, Estatutário/militar, Empregador, Conta própria, Familiar
  auxiliar; códigos conferidos no dicionário do IBGE). `gerar_informalidade` mantém
  `pct_com_carteira`, agora CLT ÷ empregados 01–06, e ganha `pop_estatutario_militar` e
  `pct_estatutario_militar` (07 ÷ empregados 01–07). `transicao_informal_formal` passa a usar
  `vinculo_trabalho IN ('CLT', 'Estatutário/militar')` no evento de t1, o que mantém o resultado
  idêntico ao atual.
- **Por quê.** "Com carteira" incluía quem não tem carteira (estatutário), e o número publicado
  (75,4/66,5/53,2) não era o da CLT.
- **Impacto previsto** (prévia sem gravar parquet, Brasil, 14+): em 2026T2, Branca/Negra/Indígena
  passam de **75,4/66,5/53,1%** para **71,7/63,0/48,3%** (estatutário/militar: 13,0/9,7/9,3% dos
  empregados). Na série 2012–2026 a queda média é de −3,56 p.p. (Branca; −2,98 a −4,08), −3,92 p.p.
  (Negra; −3,52 a −4,93) e −5,04 p.p. (Indígena; −3,21 a −8,57). A diferença Branca–Negra em
  2026T2 vai de 8,9 para 8,7 p.p. A definição antiga recalculada reproduz o parquet publicado.
- Teste: `tests/test_carteira.py`.

### 5. Textos, rótulos e registro da extração — **sem mudar números**

- **E7/E8** (`ANALISE_FASE1.md`): o desalento passa a ser descrito com os valores do parquet e o
  denominador explícito (2,0/4,5/4,1% para Branca/Negra/Indígena, 2026T2). A carteira passa a
  75,4/66,5/53,1%, com o denominador explícito e uma nota sobre a nova definição (item 4).
- **E9** (`ANALISE_CAUSAL_COTAS.md` §2–3): reescrito como exploratório, com estado **Bloqueado até
  o B4b**. Cada p citado vem com o p ajustado (`did_p_valor_bh`) na mesma frase. O texto diz agora
  que são 40 testes de DiD (5 + 35) e que 0 sobrevivem ao FDR, e inclui os dois p < 0,05 de
  participação no Centro-Oeste (Negra p = 0,021 e Parda p = 0,011; p_BH = 0,348). Sai o argumento
  "diluído ⇒ efeito real maior".
- **E10/C8** (`ANALISE_RACA_GENERO.md`): a fórmula fica `gap = raça + gênero + interação`, a base
  do % é a renda do Homem Branco e a tabela foi conferida contra o parquet regenerado no item 1. A
  "maior rotatividade" passa a ser hipótese explícita.
- **E11**: a docstring de `gerar_alfabetizacao`, o `LIMITACOES…` e o `ANALISE_FASE1.md` diziam que
  `V3014` era frequência escolar. `V3014` é "concluiu o curso que frequentou"; frequência escolar
  é `V3002`.
- **C6**: "proxy de discriminação" sai das docstrings de `decomposicao_oaxaca_blinder` e
  `gerar_oaxaca_blinder_temporal` e do subtítulo em `graficos_aprofundamentos.py`. O resíduo passa
  a ser "parte não associada às covariáveis incluídas".
- **C7** (`ANALISE_FASE1.md`): faixas pelo mínimo e máximo dos parquets. Regional: Sudeste
  61,6–85,9%, Sul 40,1–54,0%. Setor: Público 42,0–59,7%, Privado 54,6–68,0%; o Público fica abaixo
  do Privado nos 58 trimestres.
- **R18**: o rótulo `rm_sp` passa a "RM São Paulo - Demais municípios". Nenhum gráfico filtra por
  ele; os parquets mantêm o rótulo antigo até a regeneração da Onda 1.
- **R13**: os rótulos de gráfico (`graficos_fase1.py`, `graficos_arvore.py`) e os textos dizem
  "média móvel centrada de 4 trimestres". Vale nos próximos gráficos; `docs/arvore_manifest.json`
  é gerado junto com as imagens e só muda com elas. O ritmo de convergência usa média móvel
  para trás (não centrada), e o `ANALISE_RACA_GENERO.md` dizia que era "o mesmo padrão" dos
  gráficos: corrigido.
- **R15**: os dois extratores fazem HEAD no zip e gravam `_fonte.json` na partição (nome do zip,
  URL, `Last-Modified`, tamanho), e o `_resumo_extracao.csv` passa a ter essas colunas. Nada foi
  baixado; as partições atuais não têm o arquivo (colunas vazias até a próxima extração).

---

## 13/10/2026 — Etapa 2, Fase 2 (branch `auditoria/fase2-infra`)

### População e renda de referência em código (Bloco F) — **implementado, NÃO regenerado**

- **O quê.** `src/utils/populacao.py` define, num só lugar, a renda de referência (**habitual do
  trabalho principal, `VD4016`**, deflator habitual do IBGE) e a população de referência
  (**ocupados de 18+ com `VD4016` > 0**; 14+ como sensibilidade). A `CRIAR_BASE` ganha
  `renda_referencia_nominal/real`, `em_populacao_referencia` e `em_populacao_referencia_14mais`.
  Passam a usar essa definição: `hiato_racial`, `gini_por_raca`, `theil_racial`, os três
  `decomposicao_oaxaca_blinder*` e `checagem_robustez_hiato`. Gini e Theil ficam na mesma
  população (fecha E3/R1). As demais tabelas seguem no recorte histórico (14+, `VD4019`) e estão
  marcadas no catálogo e no mapa de cobertura.
- **Por quê.** Decisões de 12/10/2026 (`docs/PLANO_DE_ANALISE.md`, Bloco F; Ponto de parada 0).
- **Impacto previsto** (prévia só de pontos, sem regenerar; hiato % Branca–Negra nacional, 58
  trimestres): cai em média **1,36 p.p.** (de −2,52 a +0,02); a maior parte vem do conceito de renda
  (todos os trabalhos → trabalho principal: −1,18 p.p. em média, ainda com 14+); a idade 18+ soma o
  resto. Ex.: 2012T1 75,8% → 74,3%; 2026T2 66,2% → 65,7%. A nova população mantém 97,4–99,2% da
  população ponderada atual. **Os números publicados mudam na próxima regeneração**, que vem com
  relatório antes × depois e a ficha do Bloco F.
- **Golden-file regerado (intencional):** no sintético, o hiato passou de 31,9%/22,6% para
  32,7%/24,0% (18+ e `VD4016`).

### Proveniência padronizada

- `_meta.json` no esquema `hub-racial-meta/1` ao lado de **todos** os 101 parquets: commit e
  módulo, hash do manifesto dos insumos, `se_metodo`, população (catálogo
  `src/utils/catalogo_tabelas.py`), período, família do FDR. Para as tabelas atuais o meta foi
  preenchido retroativamente (`meta_retroativo: true`); o pipeline passa a gravá-lo sozinho.

### Outros (sem impacto numérico)

- Licenças (MIT código; CC BY 4.0 dados derivados e textos), README (contagem de imagens corrigida:
  721 em `docs/img`, 89 na galeria, e não 134), `conteudo/` marcado como *superseded*, modelo de
  ficha de estudo (`docs/studies/`), mapa de cobertura do plano.

---

## 12/10/2026 — Etapa 2 da auditoria, Fase 1 (branch `auditoria/fase1-p0`)

Origem: `docs/auditoria/rodada1.md` (E1–E5, R3, R7) e decisões do Ponto de parada 0
(`docs/auditoria/fase0_relatorio.md` §9; `docs/PLANO_DE_ANALISE.md`).

### B1 — Erro-padrão design-based (corrige E1)

- **O quê.** `pnadc_core.erro_padrao_media_ponderada`, `intervalo_confianca_media_ponderada` e
  `tabela_hiatos_significancia` passam a calcular a variância por **linearização de Taylor com
  Estrato e UPA** (`src/inference/variancia.py`) e exigem `upa` e `estrato`. Médias de grupo são
  estimadas como **domínios** dentro do universo passado; o EP da diferença de médias **inclui a
  covariância** entre os grupos. `CRIAR_BASE` ganha a coluna `estrato`. Estratos com uma UPA:
  centrados na média geral dos totais (nunca descartados; contagem nos diagnósticos).
- **Por quê.** A fórmula antiga `Σw(x−m)²/(Σw)²` tratava V1028 como peso de frequência: o EP
  dependia da escala dos pesos e ignorava a conglomeração. A documentação anterior chamava a
  diferença de 54–90× de "não é bug"; estava errada (retratação em
  `docs/LIMITACOES_E_METODOLOGIA.md`, "Correção de 12/10/2026").
- **Impacto medido.** Hiato Branca–Negra, 58 trimestres: EP novo/antigo mediana **57×**
  (45–82×); razão EP linearização / bootstrap Rao-Wu Estrato-UPA mediana **1,005**
  (0,944–1,047); z mínimo **18,8**, logo a significância do hiato nacional **se mantém**.
  Estimativas pontuais **idênticas** (ver `docs/auditoria/antes_depois.md`). Decomposição da
  razão: ~29–30× vêm da escala do peso e ~1,5–1,7× da conglomeração por UPA.
- **Também:** `_curva_event_study` (Desenho B) usa EP por célula design-based e o hiato % por
  método delta linearizado com covariância; a soma entre células ainda ignora covariâncias
  (limitação documentada; reespecificação no B4b). `erro_padrao_cluster_bootstrap` fica como
  LEGADO; a checagem passa a usar `erro_padrao_bootstrap_estrato_upa` (Rao-Wu).

### B3 — Welch, multiplicidade, Theil, deflator (E2, E3, E4, R3, R7)

- **Welch (E2).** Graus de liberdade com o EP **da média**
  `(ep₁²+ep₂²)²/(ep₁⁴/(n₁−1)+ep₂⁴/(n₂−1))` e **n efetivo de desenho** `n_ef = s²_w/EP²` (n/deff)
  em vez do n bruto. p-valor por `t.sf` (antes `1 − cdf`, que zerava p muito pequenos). Nova
  coluna `gl_welch`. Impacto: com n efetivo na casa das centenas ou mais, a diferença para a
  normal é desprezível; pesa em células finas (Indígena).
- **Multiplicidade.** Toda tabela com `p_valor` ganha `significativo_nominal`, `p_valor_bh` e
  `significativo_fdr` (Benjamini-Hochberg). **Família = comparações de uma mesma tabela que
  dividem o mesmo período e a mesma abertura** (padrão aprovado em 13/10/2026; fichas de estudo podem declarar família própria) (`src/inference/multiplicidade.py`; a família de
  cada parquet está no `_meta.json`). `significativo` é mantido como alias de
  `significativo_nominal` até os gráficos serem regenerados.
- **Theil/Gini (E3).** Docstring do Theil corrigida: a função de Gini **não** exclui zeros. Em
  produção as duas já usavam a mesma população (renda > 0); a partir da Fase 2 ela vem de
  `src/utils/populacao.py`.
- **Deflator (E4).** `carregar_deflator`/`aplicar_deflator` (IPEA, **dividiam** o nominal)
  removidos; `grep` mostrou que não tinham uso. Produção segue com o deflator do IBGE
  (multiplica), sem mudança.

### B2 — Proveniência e regeneração

- Todo parquet com EP/IC/p-valor ganha `<arquivo>.parquet._meta.json` com `se_metodo`,
  `commit`, família do FDR e data. Os que usam inferência de regressão do statsmodels (que **não**
  passa pelo B1) são marcados como tal (`wls_statsmodels_cluster_upa`, `ols_iid_sobre_serie_trimestral`,
  `wls_statsmodels_iid_celulas_coorte`).
- Tabelas regeneradas com os dados do extrato v1 (mesma base); cópia anterior em
  `data/processed/_legado/pre_b1_63563e3/` (local, fora do git). Relatório:
  `docs/auditoria/antes_depois.md`. Gráficos **não** regenerados:
  `docs/auditoria/graficos_a_regenerar.md`.

### B5 — Testes e CI

- 40 testes (eram 13): invariância à escala, `s/√n`, Monte Carlo com conglomerados, domínio,
  diferença com covariância, bootstrap × linearização, UPA única, Welch, FDR, Gini/Theil com
  zeros, Oaxaca-Blinder com resposta conhecida, remoção do deflator, **guarda que falha se o
  peso voltar na 1ª potência** e **golden-file** sobre microdado sintético
  (`tests/golden/`). CI no GitHub Actions (Python 3.12) com `requirements.lock`.

### Extração v2 e decisões de definição (sem impacto nos números desta fase)

- Extratores gravam em pastas novas (`data/raw/pnadc_extraido_v2`, `data/raw/pnadc_anual_v2`),
  com variáveis escolares, de trabalho principal (`V4039`, `V4010`…), renda domiciliar (`VD5*`)
  e Visita 5 para 2020–2021. A base de produção continua a v1 até a Fase 2.
- População de referência decidida: **ocupados com renda do trabalho principal > 0, 18+**
  (14+ como sensibilidade). Implementação na Fase 2; ainda **não** aplicada aos números.
