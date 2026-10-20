# Ficha de pesquisa — `H3` · Patrimônio por proxy: casa própria e rendas de capital, por raça

| Campo | Valor |
|---|---|
| ID no plano | `H3.1`, `H3.3` (`H3.2` exige POF; `H3.4` bloqueado) (`docs/PLANO_DE_ANALISE.md`, Bloco H) |
| Onda | 4 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
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

## 10. Resultados

Tabela: `h3_patrimonio_proxy` (PNADC anual; 2016–2019 e 2022–2025 para casa própria, 2016–2025 para rendas de
capital). p.p.; IC 95%.

| Indicador | Ano | Negra − Branca bruta | Mesmo décimo de renda, UF e situação |
|---|---|---|---|
| Casa própria quitada | 2016 | +0,8 (0,0–1,6) | −2,8 (−3,6 a −2,0) |
| | **2025** | −0,5 (n.s.) | **−4,7 (−5,5 a −4,0)** |
| Casa própria (quitada ou pagando) | 2025 | −3,5 | −4,7 (−5,4 a −4,0) |
| Alugada | 2025 | +1,6 | **+4,2 (3,5–4,8)** |
| Cedida | 2025 | +1,9 | +0,5 |
| Recebe aluguel (18+) | 2025 | −2,2 (Branca 3,7%, Negra 1,5%) | −0,9 (−1,1 a −0,7) |
| Recebe aplicações/outros (18+) | 2025 | −1,6 | −0,4 (−0,6 a −0,2) |
| **Recebe aluguel ou aplicações (18+)** | 2025 | −3,5 (Branca 5,8%, Negra 2,4%) | **−1,2 (−1,4 a −0,9)** |

Indígena − Branca (2025, condicional): casa própria quitada −8,5 (−13,0 a −3,9); alugada +7,2.

**Leitura das hipóteses**

- **H1 (desvantagem de patrimônio além da renda):** **confirmada** — com a mesma renda domiciliar por pessoa, a mesma UF e
  a mesma situação, pessoas negras moram menos em casa própria quitada (−4,7 p.p.) e recebem menos rendas de capital
  (−1,2 p.p., cerca de um quinto da taxa dos brancos, 5,8%). A desvantagem condicional em casa própria **aumentou** desde
  2016 (−2,8 → −4,7).
- **H2 (casa própria não discrimina):** **refutada** na forma condicional. A igualdade **bruta** em casa própria (≈ 0)
  esconde que negros moram mais em UFs e situações (interior, rural) com mais casa própria e renda menor.

## 11. Afirmações permitidas

- "Com a mesma renda por pessoa e no mesmo lugar, pessoas negras moram menos em casa própria quitada (−5 p.p.) e mais
  em casa alugada (+4 p.p.) que pessoas brancas (2025)."
- "Entre adultos, 5,8% das pessoas brancas e 2,4% das negras recebem aluguel ou rendimentos de aplicações."

## 12. Afirmações proibidas

- "A diferença de riqueza é de X%" (o Hub não mede patrimônio; H3.4).
- "Negros têm tanta casa própria quanto brancos" sem a comparação condicional.
