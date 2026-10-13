# Changelog metodológico

Registro de toda mudança que altera (ou pode alterar) um número publicado ou a forma de
calculá-lo: data, o quê, por quê, impacto. Mais recente primeiro.

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
  inclui Amarela no universo e nas raças reportadas; Ignorado e o escopo `genero` ficam como estavam.
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
