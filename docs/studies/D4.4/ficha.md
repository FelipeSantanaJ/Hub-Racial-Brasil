# Ficha de pesquisa — `D4.4` · Segregação residencial Branca × Negra e a renda do bairro (Censo 2022)

| Campo | Valor |
|---|---|
| ID no plano | `D4.4` (`docs/PLANO_DE_ANALISE.md`, Bloco D; antes "Bloqueado: exige Censo 2022") |
| Onda | 6 (integração) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
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

<Preenchido depois de rodar.>

## 11. Afirmações permitidas

<Depois de rodar.>

## 12. Afirmações proibidas

- "A segregação residencial causa o hiato de renda" (é `D`; mecanismo `M` fora de alcance).
- Chamar o setor censitário de "bairro" sem ressalva.

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-20 | Claude Code | criação (seções 1–9 antes de rodar) |
