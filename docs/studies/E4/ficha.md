# Ficha de pesquisa — `E4` · Escola pública ou privada: quem acessa cada rede, por raça

| Campo | Valor |
|---|---|
| ID no plano | `E4` (parte PNADC; tipo de escola fino exige Censo Escolar) (`docs/PLANO_DE_ANALISE.md`, Bloco E) |
| Onda | 4 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Proposto** |
| PR | `onda4/e-h` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026).

## 1. Pergunta

Entre estudantes da mesma etapa, quanto mais pessoas brancas do que negras e indígenas estudam na rede privada — e
quanto disso some quando se comparam estudantes de famílias com a mesma escolaridade e no mesmo lugar? No superior,
a rede pública ficou mais negra desde 2016?

## 2. Tipo

`D`/`C`. Associação; a rede privada é proxy grosseira de qualidade e de renda familiar (a PNADC não traz a escola).

## 3. Estimando

- % na rede privada (`V3002A` = 1) entre quem frequenta, por etapa (pré-escola, fundamental, médio, graduação) e raça;
  diferença Branca − Negra (p.p.), bruta e condicional (UF, urbano, tipo de área; e, para quem mora com pai/mãe,
  escolaridade máxima do responsável ou cônjuge — ver H1).
- Composição racial da graduação por rede: % de estudantes negros na graduação pública e na privada.
- **Períodos:** janelas 2016 (4 trimestres; `V3002A` só existe desde 2016) e 2025T3–2026T2.

## 4. População

Pessoas que frequentam escola ou curso (`V3002` = 1) em etapa regular ou graduação; Branca, Negra, Indígena.

## 5. Método

Proporções e MQO linear (`bloco_d.Sistema`); influência linearizada por Estrato/UPA; FDR entre etapas de uma janela.

## 6. Dados

PNAD Contínua trimestral v2: `V3002`, `V3002A`, `V3003A`, `V2005`, `VD3004` dos moradores, `UF`, `V1022`, `V1023`.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **A rede é sobretudo renda/escolaridade da família** | Diferença condicional à escolaridade dos pais e ao lugar < metade da bruta no fundamental e no médio |
| H2 | **Inversão no superior:** a graduação pública ficou mais negra que a privada desde as cotas (2012) | % negra na graduação pública ≥ % negra na privada na janela recente |

## 8. O que refutaria

- H1 refutada se a diferença condicional for ≥ metade da bruta (IC da razão acima de 0,5).
- H2 refutada se a % negra na pública for menor que na privada com IC da diferença excluindo zero.

## 9. Armadilhas

- `V3002A` só desde 2016: não há 2012.
- A escolaridade dos pais só existe para quem mora com eles (corresidência; ver H1) — no superior a corresidência é
  seletiva.
- Pública mistura municipal, estadual e federal (qualidades muito diferentes); a PNADC não separa.
