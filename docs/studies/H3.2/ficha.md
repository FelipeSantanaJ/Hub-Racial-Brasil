# Ficha de pesquisa — `H3.2` · Bens duráveis por raça com a mesma renda (POF 2017–2018)

| Campo | Valor |
|---|---|
| ID no plano | `H3.2` (`docs/PLANO_DE_ANALISE.md`, Bloco H) |
| Onda | 4 (parte 2, POF) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
| PR | `onda4/inep-pof` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026).

## 1. Pergunta

Com a mesma renda disponível por pessoa e no mesmo lugar, pessoas negras vivem em unidades de consumo com menos bens
duráveis (carro, computador, máquina de lavar, ar-condicionado) que pessoas brancas?

## 2. Tipo

`D`/`C`. Posse de bens é proxy de patrimônio acumulado (H3.4 continua fora de alcance).

## 3. Estimando

- % de pessoas em unidade de consumo (UC) com cada bem (inventário, quadro 14: automóvel 1403001, motocicleta 1403101,
  microcomputador ou notebook 1401901, máquina de lavar 1401201, ar-condicionado 1402101, geladeira de 2 portas
  1400401, TV de tela plana 1401401) e número de bens desses 7 tipos, por cor/raça da pessoa (`V0405`).
- Diferença Negra − Branca bruta e **no mesmo décimo de renda disponível per capita** (`RENDA_DISP_PC`), UF e situação
  urbana/rural (MQO linear).

## 4. População

Moradores da POF 2017–2018 (Branca, Negra = preta + parda, Indígena com ressalva). Peso `PESO_FINAL`.

## 5. Método

Proporções e MQO linear (`bloco_d.Sistema`); linearização com `COD_UPA` como conglomerado e `ESTRATO_POF` como estrato.
FDR entre os 8 indicadores.

## 6. Dados

IBGE, Microdados da POF 2017–2018 (`MORADOR.txt`, `INVENTARIO.txt`; leiaute do programa de leitura do IBGE),
baixados em 20/10/2026.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Menos bens com a mesma renda** | Diferença condicional < 0 (IC excluindo zero) em ≥ 4 dos 7 bens |
| H2 | **Bens de consumo comuns se igualaram; ativos caros não** | Diferença condicional ≈ 0 para geladeira e TV, < 0 para automóvel e computador |

## 8. O que refutaria

H1 refutada se em 4 ou mais bens o IC da diferença condicional incluir zero ou for positivo. H2 refutada se geladeira
e TV tiverem diferença condicional < 0 com IC excluindo zero de mesma ordem que automóvel e computador.

## 9. Armadilhas

- 2017–2018: anterior à pandemia; não há POF mais recente (POF 2024–25 a confirmar).
- O inventário é da UC; atribuir à pessoa repete a informação para todos os moradores.
- Moto e automóvel dependem de território (rural/Norte–Nordeste) — por isso UF e situação.
- A renda disponível da POF inclui renda não monetária (a confirmar a definição exata no tradutor do IBGE).

## 10. Resultados

Tabela: `h32_pof_bens`. POF 2017–2018 (pesos somam 207,1 milhões de pessoas). p.p.; IC 95%; todas as diferenças
Negra − Branca significativas após BH.

| Bem na unidade de consumo | Branca | Negra | Negra − Branca bruta | Mesmo décimo de renda, UF e situação |
|---|---|---|---|---|
| Automóvel | 61,4% | 36,7% | −24,7 | **−8,8 (−9,8 a −7,7)** |
| Motocicleta | 22,6% | 27,1% | +4,5 | −1,3 (−2,2 a −0,4) |
| Microcomputador ou notebook | 54,5% | 35,6% | −18,9 | **−6,6 (−7,6 a −5,6)** |
| Máquina de lavar roupa | 76,8% | 55,6% | −21,1 | −4,9 (−5,8 a −4,0) |
| Ar-condicionado | 26,7% | 14,8% | −11,9 | −5,6 (−6,4 a −4,7) |
| Geladeira de 2 portas | 61,3% | 46,2% | −15,1 | −3,7 (−4,7 a −2,7) |
| TV de LED, plasma ou LCD | 79,2% | 66,0% | −13,2 | −4,3 (−5,1 a −3,4) |
| Número de bens (dos 7) | 3,82 | 2,82 | −1,00 | **−0,35 (−0,38 a −0,32)** |

Indígena − Branca (condicional): automóvel −15,6; computador −11,8; ar-condicionado −13,5; número de bens −0,65.

**Leitura das hipóteses**

- **H1 (menos bens com a mesma renda):** **confirmada** — diferença condicional negativa nos 7 bens (IC excluindo zero).
  Com a mesma renda e no mesmo lugar, a desvantagem de bens é cerca de um terço da bruta.
- **H2 (bens comuns se igualaram, caros não):** **refutada** — geladeira (−3,7) e TV (−4,3) também ficam abaixo, na
  mesma ordem de máquina de lavar e ar-condicionado; automóvel (−8,8) e computador (−6,6) são os maiores.

## 11. Afirmações permitidas

- "Com a mesma renda por pessoa e no mesmo lugar, pessoas negras vivem menos em casas com automóvel (−9 p.p.) e com
  computador (−7 p.p.) que pessoas brancas (POF 2017–2018)."

## 12. Afirmações proibidas

- "A riqueza dos negros é X% menor" (bens duráveis não são patrimônio).
- Usar 2017–2018 como retrato atual sem dizer a data.
