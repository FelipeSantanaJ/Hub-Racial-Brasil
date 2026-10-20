# Ficha de pesquisa — `H3` · Patrimônio por proxy: casa própria e rendas de capital, por raça

| Campo | Valor |
|---|---|
| ID no plano | `H3.1`, `H3.3` (`H3.2` exige POF; `H3.4` bloqueado) (`docs/PLANO_DE_ANALISE.md`, Bloco H) |
| Onda | 4 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Proposto** |
| PR | `onda4/e-h` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026).

## 1. Pergunta

Com a mesma renda domiciliar por pessoa, pessoas negras moram menos em casa própria quitada e recebem menos aluguel e
rendimentos de aplicações do que pessoas brancas? (Se sim, a desigualdade de patrimônio é maior do que a de renda
deixa ver.)

## 2. Tipo

`D`/`C`. Proxies fracas de riqueza (o Hub não mede patrimônio; `H3.4`).

## 3. Estimando

- **H3.1:** % de pessoas (todas as idades) em domicílio próprio já pago (`S01017` = 1), próprio pagando (= 2), alugado
  (= 3), cedido (4–6), por raça da pessoa; bruta e **dentro do mesmo décimo nacional** de renda domiciliar per capita
  (`VD5008`), com o UF e a situação (urbano/rural) como controles (MQO linear).
- **H3.3:** % de adultos 18+ que recebem aluguel/arrendamento (`V5007A` = 1) ou rendimentos de aplicações, poupança e
  outros (`V5008A` = 1), por raça; bruta e no mesmo décimo de `VD5008`.
- **Período:** PNAD Contínua anual, Visita 1: 2016–2019 e 2022–2025 (`S01017`); H3.3 também 2020–21 (Visita 5).
  Destaque: 2016 e 2025.

## 4. População

Moradores (H3.1) e adultos 18+ (H3.3) da PNADC anual, exceto pensionistas/domésticos e parentes (`V2005` 17–19);
Branca, Negra, Indígena.

## 5. Método

Proporções e MQO linear (`bloco_d.Sistema`); influência linearizada por Estrato/UPA (`V1032`); décimos de `VD5008`
com o peso empatado repartido (R9). FDR entre os indicadores de um ano.

## 6. Dados

PNAD Contínua anual v2: `S01017`, `V5007A`, `V5008A`, `VD5008`, `V2005`, `V2010`, `V2009`, `UF`, `V1022`.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Desvantagem de patrimônio além da renda** | Com o mesmo décimo de renda, UF e situação, pessoas negras têm menos casa própria quitada **e** menos renda de aluguel/aplicações (IC excluindo zero) |
| H2 | **Casa própria não discrimina** (programas habitacionais, autoconstrução) | Diferença condicional em casa própria ≈ 0 ou favorável a negros |

## 8. O que refutaria

H1 refutada se alguma das duas diferenças condicionais tiver IC incluindo zero. H2 refutada se a diferença
condicional em casa própria quitada for negativa para negros com IC excluindo zero.

## 9. Armadilhas

- "Próprio" não diz valor do imóvel, regularidade fundiária nem localização (autoconstrução em área irregular conta
  como própria): a proxy pode até favorecer quem tem menos patrimônio de fato.
- Renda de aluguel e de aplicações é muito subdeclarada nas pesquisas domiciliares (a confirmar).
- `S01017` só na Visita 1 (sem 2020–21).
- A unidade é a pessoa (cada morador herda a condição do domicílio).
