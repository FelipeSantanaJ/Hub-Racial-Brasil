# Changelog metodológico

Registro de toda mudança que altera (ou pode alterar) um número publicado ou a forma de
calculá-lo: data, o quê, por quê, impacto. Mais recente primeiro.

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
  dividem o mesmo período e a mesma abertura** (`src/inference/multiplicidade.py`; a família de
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
