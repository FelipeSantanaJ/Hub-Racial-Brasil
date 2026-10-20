# Ficha de pesquisa — `H3.2` · Bens duráveis por raça com a mesma renda (POF 2017–2018)

| Campo | Valor |
|---|---|
| ID no plano | `H3.2` (`docs/PLANO_DE_ANALISE.md`, Bloco H) |
| Onda | 4 (parte 2, POF) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Proposto** |
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
