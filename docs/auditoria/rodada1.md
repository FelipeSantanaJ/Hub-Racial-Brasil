# Auditoria científica do Hub-Racial-Brasil — Rodada 1 (Etapa 1: diagnóstico e plano)

**Data:** 12/10/2026 · **Commit auditado:** `63563e3` (clone raso, 1 commit visível) · **Repositório alterado:** não (`git status` limpo)
**Status da auditoria: PARCIAL.** Esta rodada cobre o núcleo estatístico, o módulo causal e as saídas que alimentam a curadoria da Temporada 1. Não declaro a auditoria integral concluída (ver "Registro de cobertura").

---

## 0. Registro de cobertura (o que foi e o que não foi examinado)

| Componente | Situação |
|---|---|
| `src/utils/pnadc_core.py` (569 l) | **Lido integralmente** |
| `src/processing/analise_causal_cotas.py` (682 l) | **Lido integralmente** |
| `tests/` (13 testes) | **Executados: 13 passam** (1,1 s). Cobrem só `pnadc_core` |
| `src/processing/checagem_robustez_hiato.py` | Lido integralmente |
| `src/processing/agregacoes_pnadc.py` (3.023 l) | **Só trechos** (`CRIAR_BASE`, `gerar_theil_racial`, buscas por padrão). **Pendente** |
| `src/processing/graficos_*`, `apresentacao_*` (~4.800 l) | Só busca por padrões (bandas de IC). **Pendente** |
| `src/ingestion/` | `extrator_pnadc.py`: só lista de colunas; `baixar_deflator.py`: cabeçalho. **Pendente** |
| `docs/LIMITACOES_E_METODOLOGIA.md`, `PLANO.md` | Trechos. `ANALISE_FASE1/RACA_GENERO/CAUSAL_COTAS.md` **não lidos na íntegra** |
| Parquets em `data/processed` (98) | **11 conferidos**: `hiato_racial`, `checagem_robustez_hiato_racial`, `theil_racial`, `decomposicao_oaxaca_blinder`, `decomposicao_hiato_ocupacional`, `extremos_distribuicao_racial`, `percentil_de_valor_racial`, `did_cotas_universitarias`, `did_cotas_servico_publico` (+ heterogeneidade), `painel_cohortes_superior_completo` |
| 721 imagens, 2 PPTX, notebooks (vazio) | Não examinados |
| Histórico git, branches | **Não avaliável** (clone raso, 1 commit) |
| **Reestimação a partir de microdados** | **Impossível nesta rodada**: `data/raw/` não é versionado; só validei lógica de código e saídas agregadas |
| Histórico de conversas anteriores sobre o Hub | **Não tenho acesso.** Usei só os 7 documentos do Projeto de conteúdo e o repositório. Não finjo tê-lo consultado |

Todas as referências bibliográficas abaixo são **de memória e precisam ser confirmadas** antes de citar.

---

## Entregável 1 — Resumo executivo

**Estado atual.** Projeto analítico amplo (PNAD Contínua 2012–2026, 58 trimestres, ~98 tabelas agregadas), com disciplina incomum de documentar bugs e limitações. Pontos fortes reais: deflator oficial do IBGE na direção correta (multiplica), funções de Theil/Gini/quantil com testes sintéticos, Oaxaca-Blinder com erro-padrão clusterizado por UPA, desenho causal com placebos e pré-tendência reportados, e a prática de falar abertamente quando o resultado é nulo.

**Riscos prioritários**

1. **[Erro demonstrado, crítico] O erro-padrão de produção depende da escala dos pesos.** `erro_padrao_media_ponderada` usa `Σ w·(x−m)²/(Σw)²` (peso na 1ª potência), que trata `V1028` como peso de frequência. Mesmos dados, pesos ×500 → EP ÷22 (Seção 3, E1). Nos dados reais, o IC publicado de `hiato_racial.parquet` tem meia-largura de ~R$ 2 (2012 T1: 1.739,5–1.743,7) contra ~R$ 118 sob bootstrap por UPA. **A documentação do repositório registra a diferença de 54–90× e a classifica como "não é bug"; essa conclusão está errada.**
2. **[Risco] Quase toda inferência de células finas herda E1** (família `hiato_*`, curvas do event-study do desenho B, indicadores `significativo` na árvore de 374 imagens). A conclusão "58/58 trimestres significativos" no hiato nacional Branca–Negra **sobrevive** (z ≥ 17 sob o bootstrap). Não sei quantas flags de células finas virariam.
3. **[Risco, alto] Desenho causal B (Lei 12.990): resultado destacado não resiste à multiplicidade.** 40 testes de DiD reportados, 4 com p<0,05 (esperado ao acaso: 2,0); **nenhum sobrevive a Bonferroni/Holm/BH** (menor p ajustado 0,44/0,44/0,40). O "+2,0% (p=0,041)" e o "Centro-Oeste +5,6% (p=0,030)" são exploratórios, não achados.
4. **[Risco, alto] Desenho causal A (Lei 12.711):** o "resultado nulo" é informativo para Negra (IC95% implícito −2,5 a +2,4 p.p.) mas **não para Indígena** (−12,2 a +15,8 p.p.). Coorte e período estão entrelaçados (coortes "tratadas" só observadas em 2019–2026, incluindo a pandemia) e a inferência usa MQP i.i.d. sobre ~38 células.
5. **[Risco interpretativo] "É a profissão ou é a cor da pele?"** é falsa dicotomia: o Oaxaca-Blinder controla só idade, instrução e grande grupo ocupacional. Região, sexo, horas trabalhadas (`VD4031`, **já extraída**), informalidade e setor ficam no "resíduo".
6. **[Inconsistência editorial] 22% × 24% × 47%** descrevem estimandos diferentes do "resíduo"; a curadoria usa 22% em P08 e 24% em P10 com a mesma origem.
7. **[Engenharia]** microdados fora do repositório, sem lockfile, sem CI, testes só em `pnadc_core` (13 testes, todos com pesos iguais a 1; nenhum em `agregacoes_pnadc.py` nem no módulo causal), código morto de deflator (IPEA, direção oposta).

**Maior retorno científico:** corrigir E1 (um estimador, ~1 função) e regenerar as tabelas afetadas.
**Suspender até validação:** qualquer afirmação de significância sobre células finas; bandas de IC nos gráficos; os blocos P16–P18/R10 como estão.
**Não precisa parar:** os números pontuais do lote 1 (17/11) — conferidos contra os parquets (Seção "Impacto no calendário").

---

## Entregável 2 — Inventário verificável (amostra auditada)

| Componente | Método / fonte | Estado | Evidência |
|---|---|---|---|
| Hiato Branca–Negra (série 58 trim.) | Média ponderada, Welch caseiro | **Parcialmente validada**: ponto ✓; IC/p com erro (E1); conclusão de significância robusta | `hiato_racial.parquet` ×`checagem_robustez…` |
| Hiato % 75,8% (2012T1) → 66,2% (2026T2) | Razão à média Negra | **Validada (ponto)** | `hiato_racial.parquet` |
| Erro-padrão da média ponderada | Fórmula fechada | **Com erro demonstrado** | Teste de invariância à escala (E1) |
| Teste de Welch | Welch-Satterthwaite à mão | **Com erro de fórmula** (E2), impacto baixo com n grande | Leitura de `pnadc_core.py:279-284` |
| Bootstrap por UPA | 200 réplicas, UPA como bloco, **sem Estrato** | Parcialmente validada (checagem útil, não é o desenho completo) | `pnadc_core.py:73-107` |
| Oaxaca-Blinder (média, Reimers) | WLS + `cov_type='cluster'` por UPA | **Parcialmente validada**: implementação correta; especificação insuficiente (R5) | Fórmulas `:401-446` |
| RIF por quantil | KDE gaussiano ponderado | **Não validada** (sensibilidade à largura de banda e ao *heaping* não testada) | `:343-364` |
| Theil T entre/dentro (≈7%) | Decomposição exata | **Validada (matemática e número)**; escopo estreito (R1) | `theil_racial.parquet`: 5,97–8,47%, último 6,67% |
| Gini ponderado | Trapézios sobre Lorenz | Parcialmente validada; mantém zeros, Theil não (R1) | `:449-484` |
| Desenho causal A (cotas univ.) | DiD por coorte × raça, ~38 células | **Metodologicamente insuficiente** | R2 |
| Desenho causal B (cotas serviço público) | Event-study + tripla diferença | **Metodologicamente insuficiente**; curvas com EP de E1 | R3 |
| Deflator | IBGE, multiplicativo | **Validada** (direção e fonte); `carregar_deflator`/`aplicar_deflator` em `pnadc_core` são **código morto** e invertidos | `grep` |
| Topo/base 10% (33%/73%) | Limiar em R$ | **Validada**: 32,5%/72,6% (2026T2); "topo 10%" captura 11,2% da população (limiar R$7.000) | `extremos_distribuicao_racial.parquet` |
| Percentil de R$3.000 | Função inversa | **Validada**: Branca P57,2 · Negra P75,8 | `percentil_de_valor_racial.parquet` |
| Testes automáticos | pytest | 13 passam; **só pesos = 1** | `tests/test_pnadc_core.py` |
| Reprodutibilidade ponta a ponta | — | **Não foi possível avaliar** | `data/raw/` ausente |

---

## Entregável 3 — Matriz de problemas

### Erros demonstrados

| ID | Problema | Gravidade | Evidência | Correção mínima | Teste de aceitação |
|---|---|---|---|---|---|
| **E1** | `erro_padrao_media_ponderada` não é invariante à escala dos pesos (peso de frequência) | **Crítica** | Dados sintéticos, n=100.000: pesos constantes 1 → EP 9,67; 10 → 3,06; 500 → 0,43. Com pesos variáveis (média 501), linearização `Σw²(x−m)²/(Σw)²` dá 10,87 vs 0,43 de produção (razão 25,1 ≈ √média(w)=22,4). Dados reais: razão bootstrap/produção 54–90× (média 66,6×); IC de 2012T1 = ±R$2 | Trocar por estimador *design-based* (linearização de Taylor com `Estrato` e `UPA`, ou pesos replicados se existirem); reclassificar o trecho de `LIMITACOES…:112-132` | (a) EP invariante a `w → c·w`; (b) = `s/√n` com pesos iguais; (c) razão novo/bootstrap por UPA documentada nos 58 trimestres |
| **E2** | Welch: graus de liberdade usam `ep²/n`, mas `ep²` já é a variância da média | Média | Leitura de `pnadc_core.py:279-284` (Satterthwaite usa `s²/n = ep²`) | `df = (ep₁²+ep₂²)² / (ep₁⁴/(n₁−1) + ep₂⁴/(n₂−1))` (ou n efetivo de desenho) | Teste contra caso com `df` conhecido |
| **E3** | `theil_t` diz usar "mesma convenção do Gini" (exclui renda ≤ 0), mas o Gini mantém zeros | Baixa | `pnadc_core.py:512-516` vs `:451-453` | Corrigir docstring e decidir população única | Teste com zeros |
| **E4** | `carregar_deflator`/`aplicar_deflator` (IPEA, **divide**) coexistem com o deflator IBGE (**multiplica**) usado em produção | Baixa (latente) | `grep`: nenhum uso fora de `pnadc_core` | Remover | `grep` vazio |
| **E5** | `LIMITACOES…:110` diz que a PNADC pública "não distribui" réplicas de estratificação por `Estrato` (formulação ambígua); `Estrato` **é extraída** (`extrator_pnadc.py:47`) e nenhuma função de EP a usa | Média (lacuna a esclarecer) | Lista `VARIAVEIS_DESEJADAS` | Usar `Estrato` em E1; verificar no dicionário se há pesos replicados (**não verificado**) | — |

### Riscos metodológicos

| ID | Risco | Gravidade | Evidência | Correção proposta |
|---|---|---|---|---|
| **R1** | Theil e Gini sobre populações diferentes; Theil só com Branca/Negra/Indígena (Amarela fora), só renda > 0, só ocupados | Média | `theil_racial.parquet`, `gerar_theil_racial` | Documentar escopo na legenda do "7%"; sensibilidade a Theil L (MLD) e a incluir Amarela |
| **R2** | **Desenho A**: células coorte×raça (~38), MQP i.i.d.; coorte × período entrelaçados (coortes ≥1994 só observadas 2019–2026; 2001 só em 2026); pré-tendência "sustentada" = p ≥ 0,05 (ausência de evidência, com 11 coortes); placebos subpotentes; exposição diluída (só instituições federais) e política concorrente não modelada | **Alta** | `did_cotas_universitarias.parquet`; aritmética de coortes | **Restringir**: reportar IC e efeito mínimo detectável; reescrever como "intervalo compatível com…" |
| **R3** | **Desenho B**: (i) EP das curvas via E1; (ii) DiD com **uma** dummy pós, sem efeitos fixos de trimestre; (iii) janela −10…+12 trimestres cobre 2012T1–2017T3, incluindo a recessão 2015–16 com impacto assimétrico na composição do setor privado ("controle"); (iv) tratamento = todo o setor público, lei = só federal; (v) **40 testes sem correção** | **Alta** | `did_cotas_servico_publico*.parquet`; `multipletests` | **Reespecificar**: FE de trimestre, controle de composição, sensibilidade de pré-tendência (HonestDiD, Rambachan & Roth — *a confirmar*), correção Holm/BH por família |
| **R4** | RIF: densidade por KDE sobre renda com *heaping* em valores redondos; largura de banda não testada | Média | `rif_quantil` | Variar largura de banda e suavizar; reportar faixa |
| **R5** | Oaxaca-Blinder: controles = faixa etária, instrução, ocupação. **Faltam** região/UF, sexo, horas (`VD4031`, já extraída), informalidade, setor; ocupação é mediador. Parcela "não explicada" varia **47–98%** conforme o conjunto de controles | **Alta (interpretação)** | `decomposicao_oaxaca_blinder.parquet` | Rodar ≥3 especificações com/sem região+horas; rotular "resíduo não explicado pelas covariáveis", nunca "cor da pele" |
| **R6** | Hiatos de séries trimestrais tratados como 58 evidências independentes; PNAD tem rotação de domicílios (5 visitas) | Média | Desenho amostral da PNADC | Reportar tendência com EP robusto a autocorrelação (HAC) |
| **R7** | Significância por célula na árvore de 374 imagens sem controle de multiplicidade | Média | Não quantificado | Flag de FDR por família |

### Problemas de comunicação / preferência editorial

| ID | Problema | Onde |
|---|---|---|
| **C1** | O hiato % é relativo à renda **Negra** (Branca ganha 66% a mais ≠ "Negra ganha 66% menos"; Negra = ~60% da renda Branca em 2026T2) | P01/P02 |
| **C2** | "22%" (coef. restrito 0,2023 log-pontos → e^0,2023−1 = 22,4%), "24%" (padronização direta, 24,3%) e "47%" (parcela não explicada do hiato em log-pontos) são estimandos distintos; P08 diz ~22%, P10 diz 24% "idem P08" | P04/P08/P10 |
| **C3** | Título "É a profissão, ou é a cor da pele?" (ver R5) | P08 |
| **C4** | Banda de IC nos gráficos (`graficos_fase1.py:1025-1092`; `graficos_causal_cotas.py:36`) deriva de E1 | P01, P16–P18 |
| **C5** | `conteudo/README.md` do repositório diz "planejada para 2027, lançamento 21/03/2027"; o Projeto lança em 17/11/2026 | Duas "máquinas de conteúdo" |

### Limitações dos dados (inevitáveis)

Microdados não versionados; PNADC é corte transversal repetido (não painel); amostra pequena de Indígena em células finas; sem renda familiar, origem social, qualidade da escola ou território residencial; Censo (Fase 2) bloqueado e DataSUS não iniciado.

---

## Entregável 4 — Nova agenda científica (educação → trabalho)

**Achado de cobertura:** o pipeline extrai só `VD3004`/`VD3005` (instrução e anos de estudo), `V3001`, `V3009A`, `V3014`. **Não há variáveis de frequência escolar, atraso/distorção idade-série nem abandono.** O Hub é hoje centrado em renda; educação entra como covariável, não como objeto.

```
Q0. Como se formam e acumulam as desigualdades educacionais raciais?
 ├─ Q1. Em que transição surge o hiato? (frequência por idade; conclusão EF/EM/ES por coorte)
 │    H1 acesso diferencial · H2 evasão · H3 distorção idade-série · H4 composição por origem (não observável aqui)
 ├─ Q2. Do acesso ao ensino superior à conclusão (Hub já tem: % Superior completo aos 25–29 por coorte)
 │    H5 política (cotas) · H6 expansão privada/FIES · H7 composição
 └─ Q3. Educação → trabalho
      ├─ Q3a. Retorno observado da escolaridade por raça/gênero/quantil  (Hub já tem: renda×escolaridade, RIF)
      ├─ Q3b. Sobrequalificação e segregação ocupacional (Hub já tem)
      └─ Q3c. O que sobra comparando mesma escolaridade+ocupação+região+horas?  (R5 → especificação ampliada)
```

**Primeira pergunta prioritária (ficha completa):** *Q3c — o hiato salarial entre pessoas com escolaridade e ocupação semelhantes é robusto a região, horas e informalidade?*
- **Estimando:** diferença condicional de log-renda (decompositiva/associativa; **não causal**).
- **Dados:** os já extraídos (`UF`, `V1022`, `VD4031`, `VD4009`, `VD4010`, `VD4011`).
- **Método:** Oaxaca-Blinder em 3–4 especificações aninhadas + RIF em P10/P50/P90 com variação de banda.
- **Hipóteses concorrentes:** composição regional (H8), jornada (H9), informalidade (H10), discriminação/segregação (H11).
- **Refutaria H8/H9/H10 como únicas explicações:** resíduo estável (±3 p.p.) ao adicionar cada bloco.
- **Esforço:** 2–3 dias. **Reaproveita:** `decomposicao_oaxaca_blinder`, base `CRIAR_BASE`.

As demais perguntas ficam como **árvore**, com ficha completa a desenvolver na rodada 2 (não invento literatura aqui).

---

## Entregável 5 — Catálogo de novas análises (priorizado)

| # | Análise | Tipo | Lacuna | Reaproveita | Dados novos | Valor | Viab. | Esforço* | Prior. |
|---|---|---|---|---|---|---|---|---|---|
| N1 | EP *design-based* (UPA+Estrato) + regeneração das tabelas | Correção | E1 | `pnadc_core` | — | Muito alto | Alta | 0,5–1 d + compute | **P0** |
| N2 | Reespecificação do desenho B (FE trimestre, composição, multiplicidade, sensibilidade) | Causal | R3 | `analise_causal_cotas.py` | — | Alto | Média | 2–3 d | P1 |
| N3 | Desenho A com IC/EMD e unidade individual (cluster por coorte) | Causal | R2 | painel de coortes | — | Alto | Média | 1–2 d | P1 |
| N4 | OB com especificações ampliadas (região, horas, informalidade) | Decompositiva | R5 | OB existente | `VD4031` já extraída | Alto | Alta | 2–3 d | P1 |
| N5 | Testes *golden-file* + CI | Engenharia | Cobertura de testes | `tests/` | — | Alto | Alta | 1–2 d | P1 |
| N6 | Frequência escolar/distorção idade-série por coorte | Descritiva | Q1 | `CRIAR_BASE` | extrair `V3002`, `V3003A` etc. (**confirmar no dicionário**) | Alto | Média | 3–5 d | P2 |
| N7 | Renda domiciliar per capita como controle de classe | Associativa | Classe × raça | — | variáveis `VD5*` (**confirmar**) | Alto | Média | 2–3 d | P2 |
| N8 | Sensibilidade do RIF (banda, *heaping*) | Metodológica | R4 | `rif_quantil` | — | Médio | Alta | 1 d | P2 |
| N9 | Mapa Censo 2022 (segregação residencial) | Descritiva | Território | — | Censo (bloqueado: login GovBR) | Alto | **Bloqueada** | — | P3 |

\*Estimativas grosseiras de trabalho humano; custo de processamento não medido.

---

## Entregável 6 — Arquitetura-alvo (migração incremental, sem reescrever)

Estrutura atual (`src/ingestion`, `src/processing`, `src/utils`, `tests`, `docs`, `data/processed`) é adequada. Mudanças mínimas:

```
src/
  inference/     # NOVO: variância design-based, bootstrap, multiplicidade (extrai de pnadc_core)
  methods/       # decomposições, distributivos (hoje em pnadc_core)
  studies/       # um módulo por estudo (hoje: funções soltas em agregacoes_pnadc.py de 3.000 l)
docs/
  studies/<id>/plano.md · ficha.md   # pergunta, estimando, pesos, hipóteses, limites, status de publicação
data/
  processed/*.parquet + _meta.json   # versão do código, hash dos insumos, método de EP
```

- **Proveniência:** cada parquet ganha `se_metodo`, `commit`, `periodo` (hoje inexistentes).
- **Testes:** (i) invariância à escala dos pesos; (ii) *golden-file* sobre um microdado sintético de ~5.000 linhas que percorre `CRIAR_BASE`→agregação; (iii) CI no GitHub Actions; (iv) `requirements.lock`.
- **Rastreabilidade gráfico → conclusão:** cada imagem de `docs/img` referenciada por uma `ficha.md`.

---

## Entregável 7 — Backlog priorizado

| ID | Item | Cat. | Prior. | Gravidade resolvida | Valor | Viab. | Esforço | Dependências | Risco se ficar sem correção |
|---|---|---|---|---|---|---|---|---|---|
| B1 | Corrigir EP (E1) | Correção | **P0** | Crítica | Muito alto | Alta | 0,5–1 d | microdados na máquina do dono | Todo IC/p de células finas enganoso |
| B2 | Retratar "não é bug" em `LIMITACOES…` e regenerar tabelas/gráficos afetados com `se_metodo` | Correção+Com. | **P0** | Alta | Alto | Alta | 1 d + compute | B1 | Documentação contraditória |
| B3 | Corrigir Welch (E2); padronizar `tabela_hiatos_significancia`; flag FDR por família | Correção | P0 | Média | Médio | Alta | 0,5 d | B1 | Flags inflados |
| B4 | Reespecificar desenhos A/B (N2, N3) | Causal | P1 | Alta | Alto | Média | 3–5 d | B1 | Conclusões causais não defensáveis |
| B5 | Testes *golden-file* + CI + lockfile (N5) | Engenharia | P1 | Média | Alto | Alta | 1–2 d | — | Regressões silenciosas |
| B6 | OB ampliado (N4) | Decompositiva | P1 | Alta (interp.) | Alto | Alta | 2–3 d | — | "Resíduo" lido como discriminação |
| B7 | Código morto (E4), docstrings (E3), `conteudo/` marcado como *superseded* | Eng./Doc. | P2 | Baixa | Médio | Alta | 0,5 d | decisão do dono | Duas máquinas de conteúdo |
| B8 | Agenda educacional (N6, N7) | Nova análise | P2 | — | Alto | Média | 1–2 sem | B5 | — |

---

## Entregável 8 — Cronograma executável

Reconciliado com o prazo do lançamento (17/11/2026; ~36 dias): **a auditoria não precisa bloquear o lote 1**.

| Fase | Quando | Conteúdo | Marco de validação |
|---|---|---|---|
| **0** (agora) | até 18/10 | Aprovação da Etapa 2 para B1–B3; regras de congelamento do lote 1 (abaixo) | Decisões 1–2 respondidas |
| **1** | 19–31/10 | B1–B3 + B5 (testes de invariância) | EP invariante; razão novo/bootstrap documentada; tabelas regeneradas e *diff* publicado |
| **2** | novembro | B4, B6 (em paralelo à semana de lançamento só se sobrar tempo) | Fichas `studies/` dos blocos de cotas |
| **3** | dez/2026 | B8 (agenda educacional) | Primeiro estudo educacional com plano analítico |
| **4–5** | 2027 | Integração de fontes (Censo, módulos suplementares), publicação | Fora do escopo desta rodada |

**Fora de escopo agora:** reescrever `agregacoes_pnadc.py`; dashboard; Censo; DataSUS.

---

## Estados de publicação (critérios objetivos)

| Estado | Entra quando | Sai quando |
|---|---|---|
| **Aprovado** | Número reproduzido contra parquet gerado **após** B1; estimando e população definidos; incerteza com método validado; conclusão proporcional | Mudança de método/dado |
| **Aprovado com ressalvas** | Número reproduzido, mas incerteza provisória **ou** interpretação exige ressalva obrigatória **na mesma tela** | B1/B2 concluídos e ressalva removida |
| **Bloqueado** | Mensagem central depende de significância de célula fina (E1), de efeito causal sem identificação defensável, ou de teste único em família não corrigida | Reespecificação + nova ficha aprovada |

### Impacto no calendário de conteúdo (só itens que verifiquei)

| ID | Veredito | Condições |
|---|---|---|
| P01/P02 | **Aprovado com ressalvas** | Números ✓ (75,8% → 66,2%; R$ 2.037 em 2020T3, R$ 1.912 em 2026T2). Remover/regenerar a banda de IC; escrever "relativo à renda média Negra" na mesma tela (C1) |
| P04 | **Aprovado com ressalvas** | 67,0 → 63,9 → 30,3 → 24,3 ✓; é padronização direta com 3 covariáveis |
| P05/P07 | **Aprovado com ressalvas** | 32,5% / 72,6% ✓ (2026T2); nota: "topo 10%" capta 11,2% da população |
| P06 | **Aprovado** | R$3.000 = P57,2 (Branca) e P75,8 (Negra) ✓ |
| P08/P10 | **Aprovado com ressalvas** | Escolher **um** estimando (recomendo 22,4%, coeficiente restrito, e dizer "controlando por idade, instrução e ocupação"); **trocar o título** (R5); citar no corpo "não inclui região, horas, sexo" |
| P11 | **Aprovado com ressalvas** | ~14,9% (mediana), ~30,6% (P10), ~36,2% (P90) ✓; sensibilidade do RIF não testada |
| P26/P27 | **Aprovado com ressalvas** | ~7% ✓ (6,0–8,5%; último 6,67%); escopo: Branca/Negra/Indígena, renda > 0 |
| **P16–P18, P29, R10** | **Bloqueado** como estão | Reespecificação (B4). P17/P29 (metodologia, "o que isso não prova") podem sair **antes**, pois reduzem risco |
| P03, P12–P15, P19–P25, P28, P30 | **Não verificado nesta rodada** | — |

O lote 1 do calendário-mestre (apresentação, P01, P02, P03*, P04, P05, P06, P08, P10) **não depende dos blocos bloqueados**. \*P03 precisa de conferência.

---

## Entregável 9 — Registro de incertezas

- Não reestimei nada com microdados: **a magnitude correta do EP** é inferência (consistência entre E1 e o bootstrap), não medição. A razão residual ~2,7× (66,6/25) pode refletir agrupamento por UPA, caudas pesadas, ou ambos.
- Se `V1028001…V1028200` (pesos replicados) existem nos microdados públicos: **não verificado**.
- Quantas flags `significativo` de células finas mudariam: **desconhecido**.
- `agregacoes_pnadc.py`, gráficos, extrator e demais documentos: **pendentes**.
- Afirmações de ordem de grandeza sobre FIES/ProUni/REUNI como confundidores do desenho A: **de memória, a confirmar**.
- Variáveis educacionais e de renda domiciliar disponíveis na PNADC: **a confirmar no dicionário**.
- Referências a confirmar: Rambachan & Roth (2023, *Review of Economic Studies*); Roth (2022, *AER: Insights*); Fortin, Lemieux & Firpo (2011, *Handbook of Labor Economics*); Oaxaca & Ransom (1999, *Journal of Econometrics*); Deaton (1985, *Journal of Econometrics*); Lumley (2010, *Complex Surveys*).

---

## Entregável 10 — Decisões que dependem de você

| # | Decisão | Minha recomendação |
|---|---|---|
| 1 | Autorizar a Etapa 2 (alterar o repositório) para **B1–B3** | **Sim.** É a mudança de maior retorno e menor risco |
| 2 | Congelamento do lote 1 | **Sim:** publicar só estimativas pontuais e o hiato nacional; nenhuma afirmação de "significativo" em célula fina; sem banda de IC em P01 até B2 |
| 3 | Blocos de cotas na Temporada 1 | Manter P17/P29 no calendário; **reespecificar P16/P18 antes de publicar**. Se faltar tempo, empurrar o bloco para a T2 em vez de publicar com ressalva |
| 4 | Destino de `conteudo/` no repositório (plano de 2027) | Marcar como *superseded* pelos documentos do Projeto, para não manter duas máquinas de conteúdo |
| 5 | Atualizar `estado-atual` com os achados acima | Sim; apontarei exatamente as linhas |

---

## Os cinco primeiros itens a executar (Etapa 2)

| # | Item | Critério de aceitação | Dependências |
|---|---|---|---|
| 1 | **B1** — estimador de variância *design-based* | Invariância a `w→c·w`; = `s/√n` com pesos iguais; razão vs. bootstrap por UPA nos 58 trimestres documentada | Microdados na máquina do dono |
| 2 | **B2** — retratar "não é bug" e regenerar tabelas/gráficos | `se_metodo` em cada parquet; relatório *old×new* (pontos idênticos, EP novo) | 1 |
| 3 | **B3** — Welch + FDR por família | Teste unitário do `df`; coluna `significativo_fdr` | 1 |
| 4 | **B5** — testes de invariância + *golden-file* + CI | `pytest` verde no CI; teste falha se a fórmula antiga voltar | — |
| 5 | **B4** — reespecificar desenhos A/B | IC e EMD no A; FE de trimestre, correção de multiplicidade e sensibilidade no B; ficha `studies/` aprovada | 1 |
