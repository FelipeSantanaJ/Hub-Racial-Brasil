# Ficha de pesquisa — `D4.4` · Segregação residencial Branca × Negra e a renda do bairro (Censo 2022)

| Campo | Valor |
|---|---|
| ID no plano | `D4.4` (`docs/PLANO_DE_ANALISE.md`, Bloco D; antes "Bloqueado: exige Censo 2022") |
| Onda | 6 (integração) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 20/10/2026) |
| PR | `onda6/integracao` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026). O plano marcava o D4.4 como `M` bloqueado por dado; com os
> agregados por setor do Censo 2022 (públicos no FTP do IBGE desde 2025–2026), a parte **descritiva** fica possível.
> O mecanismo (acesso a emprego, efeito de vizinhança) continua fora do alcance.

## 1. Pergunta

Quão separadas, entre setores censitários, moram as pessoas brancas e negras — no país e dentro do mesmo município —
e quanto mais pobre, em média, é o setor em que mora uma pessoa negra em comparação com uma pessoa branca?

## 2. Tipo

`D`. Contagens do universo do Censo (sem erro amostral). **Não permite concluir** por que a segregação existe
(preferência, preço da terra, discriminação no mercado imobiliário, história) nem efeito do bairro sobre renda.

## 3. Estimando

- **Dissimilaridade de Duncan** D = ½ Σ_s |b_s/B − n_s/N| (b = pessoas brancas, n = pretas + pardas, s = setor):
  (i) nacional, setores juntos; (ii) **dentro do município**: D de cada município, média ponderada pela população
  Branca + Negra; por porte (capitais, municípios ≥ 500 mil, 100–500 mil, < 100 mil).
- **Theil H** (entropia, dois grupos) decomposto em entre municípios e dentro de municípios (como no E7).
- **Isolamento** ₙP*ₙ: % de negros no setor da pessoa negra média, e ₙP*_b (exposição a brancos).
- **Renda do bairro:** renda média do responsável pelo domicílio no setor (agregado "Rendimento do Responsável"),
  média experimentada por cada grupo: R_g = Σ_s g_s·r_s / Σ_s g_s. Razão R_Branca / R_Negra − 1 (%), bruta e dentro do
  município (comparando grupos no mesmo município: média ponderada das razões municipais).
- **Linha de base aleatória:** D e H esperados se cada setor tivesse a composição do município, com o mesmo tamanho
  (simulação binomial, 200 réplicas) — o "D por acaso" de setores pequenos. Reporta-se D observado e D − D aleatório.

## 4. População

Todas as pessoas recenseadas em domicílios (universo), Branca e Negra (preta + parda), por setor censitário 2022.
Setores com valores suprimidos pelo IBGE por sigilo (se houver) saem e são contados. **Sensibilidade:** Branca ×
Preta; Branca × Parda; só setores urbanos; municípios com ≥ 20 setores.

## 5. Método

Somas e fórmulas fechadas; sem inferência (censo). FDR: não se aplica.

## 6. Dados

| Fonte | Variáveis | Período | Arquivo | Acesso |
|---|---|---|---|---|
| IBGE, Censo 2022 — Agregados por setores, Cor ou raça | V01317 (branca), V01318 (preta), V01320 (parda), V01321 (indígena) | 2022 | `Agregados_por_setores_cor_ou_raca_BR.zip` | público (FTP IBGE) |
| idem — Básico | código do setor, município, situação | 2022 | `Agregados_por_setores_basico_BR_20260520.zip` | público |
| idem — Rendimento do Responsável | renda média do responsável no setor | 2022 | `Agregados_por_setores_renda_responsavel_BR_20260508_csv.zip` | público |

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Segregação moderada, sobretudo entre regiões** | D nacional ≥ 0,35, mas D dentro do município ≤ 0,30; a maior parte do H vem de entre municípios |
| H2 | **Segregação urbana nas metrópoles** | D dentro do município maior nas capitais e municípios ≥ 500 mil que nos < 100 mil (diferença ≥ 0,05) |
| H3 | **Bairros mais pobres** | R_Branca / R_Negra − 1 ≥ 20% no país e ≥ 10% dentro do mesmo município |
| H4 | **Escola reflete moradia** | D dentro do município residencial (setor) próximo do D entre escolas dentro do município do E7 (0,26) |

## 8. O que refutaria

Cada hipótese é refutada se o número indicado não se verificar. Se D − D aleatório for menor que 0,05 dentro dos
municípios, a "segregação" dentro do município é atribuída ao tamanho dos setores e não é afirmada.

## 9. Armadilhas

- **Problema da unidade de área (MAUP):** setor (~200–400 domicílios) não é bairro; D depende do recorte.
- **Viés de unidades pequenas:** setores pequenos inflam D por acaso → linha de base aleatória.
- **Renda do responsável** ≠ renda domiciliar per capita; mede o bairro, não a pessoa.
- **Composição regional:** o país tem regiões majoritariamente negras e outras brancas; o D nacional mistura
  geografia ampla com segregação local → sempre separar entre/dentro de municípios.
- Cor/raça do Censo 2022 tem autodeclaração com mais pardos que 2010 (reclassificação, B2/F1).

## 10. Resultados

Tabela: `d44_segregacao_residencial` (`src/processing/bloco_integracao.py`, `--so d44`). **Conferência:** 203,08 milhões
de pessoas nos setores (oficial: 203,1 mi); 43,4% brancas, 10,1% pretas, 45,2% pardas (oficial: 43,5 / 10,2 / 45,3).
41.288 setores (8,8%; 4,05 milhões de pessoas) têm contagem por cor suprimida por sigilo e ficam fora.

| Branca × Negra (todos os setores) | Observado | Esperado por acaso | Observado − acaso |
|---|---|---|---|
| Duncan D, setores do país | **0,39** | 0,33 (composição de cada município) | 0,06 |
| Duncan D dentro do município (média ponderada) | **0,21** | 0,04 | **0,17** |
| Theil H total · entre municípios · dentro | 0,165 · 0,116 · 0,049 (**70% entre municípios**) | — | — |
| Isolamento: % de negros no setor da pessoa negra média | 65,5% | — | — |
| Renda média do responsável no setor: pessoa branca × negra | R$ 3.531 × R$ 2.282 → **+55%** | — | — |
| Mesma razão, dentro do mesmo município | **+30%** | — | — |

**Por porte (dentro do município):** capitais D 0,28 (renda do setor +70%); ≥ 500 mil não capitais 0,24 (+36%);
100–500 mil 0,20 (+24%); < 100 mil 0,18 (+10%). Entre as cidades com ≥ 1 milhão de brancos + negros, Salvador tem o
maior D (0,40), seguida de Porto Alegre (0,37), Campinas (0,35), Belo Horizonte (0,34), Rio (0,32) e São Paulo (0,32);
Manaus o menor (0,18).

**Sensibilidades:** Branca × Preta D dentro 0,27 (renda +36% dentro do município), Branca × Parda 0,21 (+28%); só
setores urbanos 0,21; municípios com ≥ 20 setores 0,22 — a leitura não muda.

**Leitura das hipóteses**

- **H1 (moderada, sobretudo entre regiões): confirmada** — D nacional 0,39, dentro do município 0,21, 70% do Theil
  entre municípios.
- **H2 (mais nas metrópoles): confirmada** — capitais 0,28 × municípios < 100 mil 0,18 (diferença 0,10).
- **H3 (bairros mais pobres): confirmada** — +55% no país, +30% dentro do mesmo município (+70% nas capitais).
- **H4 (escola reflete moradia):** D residencial dentro do município 0,21 × D entre escolas dentro do município 0,26
  (E7) — próximos, com a escola um pouco mais segregada; unidades diferentes (setor × escola), comparação indicativa.
- A segregação dentro dos municípios **não é efeito do tamanho dos setores**: D − acaso = 0,17 (regra da seção 8:
  > 0,05).

## 11. Afirmações permitidas

- "Dentro da mesma cidade, a renda média dos responsáveis pelos domicílios nos setores censitários onde moram pessoas
  brancas é 30% maior que nos setores onde moram pessoas negras; nas capitais, 70% maior (Censo 2022)."
- "A separação residencial entre brancos e negros é moderada (índice de dissimilaridade 0,21 dentro dos municípios),
  maior nas capitais (0,28) e máxima em Salvador (0,40) entre as grandes cidades."

## 12. Afirmações proibidas

- "A segregação residencial causa o hiato de renda" (é `D`; mecanismo `M` fora de alcance).
- Chamar o setor censitário de "bairro" sem ressalva.

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-20 | Claude Code | criação (seções 1–9 antes de rodar) |
| 2026-10-20 | Claude Code | resultados (seções 10–11) |
