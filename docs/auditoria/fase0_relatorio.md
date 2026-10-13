# Fase 0 — Linha de base (Etapa 2 da auditoria)

**Data:** 12/10/2026 · **Branch:** `auditoria/fase0-baseline` · **Commit de partida:** `63563e3`
**Lógica alterada:** nenhuma. Esta fase só adiciona arquivos (inventário, script de inventário, este relatório).
**Plano de referência:** `docs/PLANO_DE_ANALISE.md` **v1.0 (validado 12/10/2026)** — confirmado no cabeçalho do arquivo.

---

## 1. O que foi feito

| Item | Arquivo / ação |
|---|---|
| Branch | `auditoria/fase0-baseline` (a partir de `main` @ `63563e3`) |
| Testes | `pytest` no `.venv` do repositório (Python **3.12.10**; o CI pedido na Fase 1 é 3.11 — ver §6) |
| Inventário | `docs/auditoria/baseline.json`, gerado por `src/auditoria/inventario_parquets.py` (novo, só lê) |
| Verificações | layout SAS e dicionários `.xls` do IBGE já presentes em `data/raw/**/_tmp/`; consultas DuckDB nos 190 parquets brutos; páginas oficiais (só leitura; requisições `HEAD` para tamanho, **nada baixado**) |

Arquivos também incluídos neste PR por serem pré-requisito da Etapa 2 e ainda não versionados: `docs/auditoria/rodada1.md`, `docs/PLANO_DE_ANALISE.md`.
**Fora deste PR (não são desta etapa, não toquei):** `src/ingestion/extrator_pnadc_visita_anual.py`, `src/processing/agregacoes_habitacao.py`, `data/processed/habitacao_*.parquet` (3 arquivos não versionados).

## 2. Testes e inventário

- `pytest`: **13 passed** (2,4 s). Igual à Rodada 1.
- Inventário: **101 parquets** em `data/processed` (98 versionados + 3 `habitacao_*` não versionados), **1.482.371 linhas** no total. Para cada um: linhas, colunas e tipos, SHA-256 do arquivo, hash do conteúdo, data de modificação, flag `versionado_git`.
- Determinismo: o inventário rodado duas vezes produz `hash_conteudo` idêntico nos 101 arquivos. O `hash_conteudo` é o que será comparado nos relatórios antes × depois (o hash do arquivo pode mudar só pela versão do pyarrow).
- **61 parquets** têm colunas de EP/IC/p-valor/`significativo` (busca por nome de coluna). É a lista de partida dos "afetados" do B2; a lista final virá do rastreio dos chamadores na Fase 1. 3 deles são os `habitacao_*` (fora do escopo desta etapa até você decidir).

## 3. Pesos replicados (item 4)

**Existem nos microdados oficiais, mas não foram extraídos.**

| Fonte | Evidência |
|---|---|
| Trimestral | `input_PNADC_trimestral.txt` (layout de 31/10/2022 em `data/raw/pnadc_extraido/_tmp/dicionario/`): `V1028001`…`V1028200`, "Peso REPLICADO 1…200", posições 479–3478, 15 caracteres cada, **no mesmo arquivo de dados** de cada trimestre |
| Anual (visita 1) | `input_PNADC_2025_visita1_20260508.txt`: `V1032001`…`V1032200` (200 réplicas do peso anual `V1032`) |
| Extrato atual | `VARIAVEIS_DESEJADAS` (`extrator_pnadc.py:45-60`) só tem `V1028`; os parquets brutos têm 43 colunas, nenhuma réplica |

**Custo para tê-los:** reextrair os 58 trimestres. O zip de 2026T2 tem **233 MB** (`HEAD`), então ≈ **13 GB de download** no total. Armazenamento: 200 colunas `double` × ~28 milhões de linhas ≈ 45 GB descomprimidos (em parquet comprimido, menos; **não medido**).
**Consequência para o B1:** a linearização de Taylor com `Estrato` + `UPA` (já extraídos) não depende das réplicas. Recomendação: implementar o B1 por linearização e deixar `erro_padrao_media_replicados` implementada e testada em dado sintético, mas **sem uso em produção** até você decidir se a reextração vale o custo. O que o IBGE usa para gerar as réplicas (bootstrap? jackknife? fator de escala da variância) está no dicionário/nota metodológica: **NÃO VERIFICADO** — sem isso, a fórmula de variância das réplicas não pode ser fixada.

## 4. Variáveis escolares (item 5)

Todas as abaixo **existem no layout trimestral**; **extraídas hoje só** `V3001`, `V3009A`, `V3014`, `VD3004`, `VD3005`.

| Variável | Descrição (dicionário IBGE) | Período | Extraída? |
|---|---|---|---|
| `V3002` | Frequenta escola? (1 Sim, 2 Não) | 1T2012–atual | não |
| `V3002A` | Rede da escola (privada/pública) | **4T2015**–atual | não |
| `V3003` | Curso que frequenta (versão antiga) | 1T2012–**3T2015** | não |
| `V3003A` | Curso que frequenta (creche… doutorado) | **4T2015**–atual | não |
| `V3004`, `V3005`, `V3005A` | Duração / seriado / organização do curso | `V3004` até 4T2017 | não |
| `V3006`, `V3006A` | Ano/série que frequenta; etapa | 1T2012–atual (`V3006`) | não |
| `V3007` | Concluiu outra graduação | — | não |
| `V3008`–`V3014`, `V3013A/B` | Trajetória passada (frequentou, curso mais elevado, último ano concluído, concluiu) | — | só `V3009A`, `V3014` |
| `VD3004`, `VD3005`, `VD3006` | Nível de instrução; anos de estudo; grupos de anos | — | `VD3006` não |

**Distorção idade-série:** não há variável pronta. Dá para construir com `V3003A`/`V3006` + idade (`V2009`) + data de nascimento (`V2008`, `V20081`, `V20082`, já extraídas). **Quebra de série em 4T2015** (`V3003`→`V3003A`, categorias diferentes): exige compatibilização na Onda 4.
O layout anual (visita 1) também traz `V3002`…`V3014` (a lista exata difere um pouco).

## 5. Renda e população hoje × decisão do plano (item 6)

### 5.1 Variável de renda — confirmado no dicionário

| Variável | Dicionário IBGE (trimestral e anual 2025) |
|---|---|
| **`VD4016`** | Rendimento mensal habitual **do trabalho principal** (14+ anos, quem recebeu em dinheiro/produtos no trabalho principal) |
| **`VD4019`** | Rendimento mensal habitual **de todos os trabalhos** (14+ anos, quem recebeu em dinheiro/produtos em qualquer trabalho) |
| `VD4017` / `VD4020` | Efetivo — trabalho principal / todos os trabalhos |
| `VD4031` | Horas habituais em **todos** os trabalhos (`V4039` = horas habituais **no trabalho principal**, **não extraída**) |

**O Hub usa `VD4019` (todos os trabalhos)**, decisão explícita e documentada:
- `src/processing/agregacoes_pnadc.py:17-19` (docstring: "mais completo que só o trabalho principal");
- `agregacoes_pnadc.py:127` `m.VD4019 AS renda_habitual_nominal` e `:131` `m.VD4019 * d.deflator_habitual AS renda_habitual_real` (efetiva: `VD4020`, `:128`, `:132`).

### 5.2 População — o que o código faz

| Onde | Filtro | Arquivo:linha |
|---|---|---|
| `CRIAR_BASE` | `V2009 >= 14` (sem limite superior; sem filtro de ocupação) | `agregacoes_pnadc.py:211` |
| `hiato_racial` | Branca/Preta/Parda, `renda_habitual_real IS NOT NULL` (**sem** `> 0`) | `:1975-1976` |
| `checagem_robustez_hiato` | idem | `checagem_robustez_hiato.py:42-43` |
| `gini_por_raca`, `theil_racial` | Branca/Preta/Parda/Indígena, `renda > 0` | `:2345-2346`, `:2382-2383` |
| Oaxaca-Blinder | Branca/Preta/Parda, ocupação não nula, `renda > 0`, últimos 8 trimestres | `:478-480` |
| Desenho B (cotas, renda) | coortes de nascimento 1983–2001, `renda > 0` | `analise_causal_cotas.py:213-216` |

**Medido nos microdados (2012T1–2026T2, pessoas ≥ 14):**
- `VD4019` não nulo ⟹ **sempre ocupado** (`VD4002='1'`) e **nunca zero** (0 casos de `VD4019 = 0`). Desocupados e fora da força têm `VD4019` nulo.
- Logo, a população efetiva do Hub hoje é **ocupados ≥ 14 anos com renda habitual de algum trabalho > 0**. O `> 0` que falta em `hiato_racial` não muda nada na prática.
- Ocupados com `VD4019` nulo (sem rendimento): 497.468 registros, ≈ 2,15 mi pessoas/trimestre em média; inclui 458.346 dos 461.836 trabalhadores familiares auxiliares (`VD4009='10'`).
- **Join do deflator:** 0 linhas com renda e sem deflator (não há perda silenciosa ali).
- `V2010 = 9` (Ignorado) com renda: 2.576 registros, fora das tabelas raciais.

### 5.3 Divergências em relação ao plano v1.0

| # | Plano | Hub hoje | Tamanho medido | Impacto esperado |
|---|---|---|---|---|
| D1 | Renda = `VD4016` (trabalho principal) | `VD4019` (todos) | `VD4016 ≠ VD4019` em **3,15%** da população ponderada; média nominal agregada R$ 2.396,7 (`VD4019`) × R$ 2.326,3 (`VD4016`), −2,9% | Todo nível de renda cai um pouco; o hiato pode mudar se o segundo trabalho for mais comum em um grupo (**não medido por raça ainda**: é o F2 da Onda 1) |
| D2 | Pessoa entra se renda do **trabalho principal** > 0 | Entra se renda de **qualquer** trabalho > 0 | 4.217 registros têm `VD4019` e não têm `VD4016` (renda só no trabalho secundário; 3.490 deles são familiares auxiliares no principal) | Pequeno; saem da população |
| D3 | 25–64 anos ("a confirmar contra o uso atual") | **14+, sem teto** | Entre quem tem renda: 14–24 = **14,83%**, 25–64 = 82,17%, 65+ = 2,99% (ponderado) | **Grande**: restringir a 25–64 tira ~18% da população; muda médias, hiato, Gini, Theil e todas as séries. É decisão sua (§8) |
| D4 | Gini e Theil na mesma população | **Já estão** na mesma (ver §7) | — | Só falta incluir Amarela (hoje fora de ambos) |
| D5 | Horas para renda por hora | `VD4031` = horas de **todos** os trabalhos | — | Coerente com `VD4019`, **incoerente** com `VD4016`: com a renda do trabalho principal, a hora certa é `V4039` (não extraída) |

Nada foi alterado. A mudança de definição só acontece na Fase 2 (item 7, `populacao.py`) e a regeneração com o antes × depois e a ficha do Bloco F.

## 6. Dados externos e módulos (item 7)

| Fonte | O que encontrei | Acesso | Tamanho | Estado |
|---|---|---|---|---|
| **Módulo de mobilidade** | Existe o **suplemento de Mobilidade Sócio-ocupacional da PNAD 2014** (PNAD antiga, anual, não a Contínua), publicado pelo IBGE em 2016 ([liv98815](https://biblioteca.ibge.gov.br/visualizacao/livros/liv98815.pdf)). Na PNADC **não encontrei** módulo de mobilidade | Microdados da PNAD 2014: FTP do IBGE (público) | NÃO VERIFICADO | Busca não exaustiva; **NÃO VERIFICADO** que a PNADC nunca teve um |
| **Parentesco** `V2005` | **Já extraída.** 01 responsável, 02/03 cônjuge, 04 filho do responsável e do cônjuge, 05 só do responsável, 06 enteado, 07 genro/nora, 08 pai/mãe/padrasto/madrasta, 09 sogro, 10 neto, 11 bisneto, 12 irmão, 13 avô/avó, 14 outro parente, (15+ não parentes: não listados aqui) | — | — | Permite ligar filhos (04/05/06) ao responsável e cônjuge (01/02/03). Pais na posição 08 também ligam ao responsável |
| **Condição do domicílio** | `S01017` (próprio pago / pagando / alugado / cedido…), `S01018/S01019` (prestação/aluguel), `S01020/S01020A` (terreno; documento de propriedade). **Só no arquivo anual de visita 1**, já extraído em `data/raw/pnadc_anual_visita1` (2016–2019, 2022–2025: **faltam 2020–2021**) | — | — | Disponível para H3.1 |
| **Renda domiciliar per capita** (P5, Bloco T) | **Não existe no trimestral.** No anual (visita 1): `VD5008`/`VD5011` (habitual de todos os trabalhos + efetivo de outras fontes, per capita; `VD5011` inclui tíquete transporte/alimentação), fontes `V5001A…V5008A`, pesos `V1032` + 200 réplicas. **Não extraídas** no extrato anual atual | FTP IBGE | NÃO VERIFICADO | Blocos S (P5) e T dependem de nova extração anual |
| **RAIS pública** (sem identificação) | Disponível sem restrição pelo MTE | Livre | NÃO VERIFICADO | — |
| **RAIS identificada** | Acesso só por **acordo de cooperação** com o MTE: formulário no gov.br + CPF, CNPJ da entidade, ofício e plano de trabalho ([modelo do MTE](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho/minutas/ac-modelo-de-documento-para-solicitao-de-acesso-base-de-dados.docx)) | **Exige vínculo institucional** (pessoa física sozinha provavelmente não consegue; a confirmar) | — | Bloqueante para D3.5/D8.2 sem instituição |
| **Painel Estatístico de Pessoal** | [pep.paineis.gov.br](https://pep.paineis.gov.br/extensions/pep/index.html): servidores desde 1999, ingressos/saídas desde 1995, exportação para Excel/CSV. **Raça/cor no PEP: NÃO VERIFICADO** (a página não menciona). A ENAP publica sumários de servidores por raça/cor (Siape; autodeclaração **facultativa**) ([ENAP](https://repositorio.enap.gov.br/handle/1/3259)) | Painel aberto | — | Para G3: provavelmente agregado, não microdado; preenchimento de raça/cor incompleto |
| **Censo da Educação Superior** | [INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior), 1995–2024, download direto. **Atenção:** desde 31/03/2022 o INEP publica "microdados simplificados" (LGPD), **sem dado por aluno nem raça**; o dado por aluno fica no **SEDAP** (Serviço de Acesso a Dados Protegidos), por solicitação ([UERJ](https://www.e-publicacoes.uerj.br/re-doc/article/view/83226)) | Público (simplificado); SEDAP (restrito) | 2012: **10 MB** (`HEAD`); 2024: sem resposta | **G1/E6 com raça por aluno exige SEDAP** |
| **Censo Escolar** | [INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar), 1995–2025. Mesma restrição de 2022 (por aluno/raça suprimidos; edições antigas republicadas) ([Folha PE](https://www.folhape.com.br/noticias/mec-retem-informacoes-detalhadas-do-censo-escolar-2021-e-apaga-edicoes/216660/)) | Público (simplificado); SEDAP | NÃO VERIFICADO (URL padrão deu 404) | E2/E4 com raça por aluno exige SEDAP |
| **SAEB** | [INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/saeb), 1995–2023 (bienal) | Download direto | 2023: **694 MB** (`HEAD`) | Raça/cor no SAEB público: **NÃO VERIFICADO** |

## 7. Diferenças em relação à Rodada 1

| Afirmação da Rodada 1 | Resultado com os dados |
|---|---|
| E5 / Registro de incertezas: "se `V1028001…V1028200` existem nos microdados públicos: não verificado" | **Existem**, no mesmo arquivo de dados (§3). Não estão extraídos |
| E3/R1: "Gini mantém zeros, Theil não" | **Vale para a função** `calcular_gini_ponderado`, **não para a produção**: `gerar_gini_por_raca` já filtra `renda > 0` (`:2346`), igual ao Theil. Além disso, não existe `VD4019 = 0` no extrato. Em produção, Gini e Theil já usam a mesma população (Branca/Negra/Indígena, ocupados ≥ 14, renda > 0). Resta: docstring do Theil e Amarela fora |
| Achado de cobertura: "não há variáveis de frequência escolar" | Correto para o **extrato**; todas existem no **layout** (§4) |
| N7: renda domiciliar per capita (`VD5*`, "confirmar") | Confirmado que **só existe no arquivo anual** (visita 1), não no trimestral |
| Plano: "o Hub hoje usa `VD4019`, que é o habitual de todos os trabalhos" | **Confirmado** no dicionário e no código |
| Rodada 1: "98 parquets" | 98 versionados; há **101** na pasta (3 `habitacao_*` novos, não versionados) |

## 8. Riscos remanescentes

- O layout trimestral local é de **31/10/2022**. Se o IBGE reponderou a série após o Censo 2022 e mudou o layout, o extrato pode estar misturando versões de peso. **NÃO VERIFICADO**: é o item 3 da Fase 3.
- Sem as réplicas, a validação do B1 depende do bootstrap Estrato/UPA (checagem independente, mas não o método oficial do IBGE).
- Python local 3.12 × CI 3.11 pedido: um lockfile gerado em 3.12 pode não instalar em 3.11.

## 9. Decisões que dependem do Felipe

1. **Faixa etária da população de referência:** 25–64 (plano) × 14+ (Hub hoje). A mudança tira ~18% da população com renda. Recomendo **25–64** para os Blocos A–D (evita estudantes e aposentados) e manter 14+ como sensibilidade F3.
2. **Pesos replicados:** reextrair (~13 GB de download, dezenas de GB em disco) ou ficar com linearização Estrato/UPA + bootstrap? Recomendo **linearização agora** e decidir a reextração depois do B1, se a razão linearização/bootstrap não ficar próxima de 1.
3. **Horas do trabalho principal (`V4039`)** e **variáveis escolares**: autorizar a inclusão em `VARIAVEIS_DESEJADAS` para a próxima extração. Isso exige rebaixar os trimestres; dá para combinar com o item 2 numa única reextração.
4. **Extração anual (visita 1):** incluir `VD5008`/`VD5011`, `V5001A…V5008A`, `V1032001…200` e cobrir 2020–2021 (hoje faltam), necessário para P5 e o Bloco T.
5. **SEDAP/INEP e RAIS identificada:** exigem pedido formal e, para a RAIS, entidade conveniada. Você tem vínculo institucional que possa assinar?
6. **`habitacao_*`** (3 parquets e 2 scripts não versionados): entram na Fase 1 (eles têm colunas de EP/IC) ou ficam fora até a temporada de habitação?
7. **Versão do Python no CI:** 3.11 (como pedido) ou 3.12 (o que roda aqui)?
