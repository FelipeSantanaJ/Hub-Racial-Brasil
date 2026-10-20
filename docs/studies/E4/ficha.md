# Ficha de pesquisa — `E4` · Escola pública ou privada: quem acessa cada rede, por raça

| Campo | Valor |
|---|---|
| ID no plano | `E4` (parte PNADC; tipo de escola fino exige Censo Escolar) (`docs/PLANO_DE_ANALISE.md`, Bloco E) |
| Onda | 4 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
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

## 10. Resultados

Tabela: `e4_rede_escola`. % na rede privada entre quem frequenta; diferenças Branca − Negra em p.p.

| Etapa (2025T3–2026T2) | Branca | Negra | Bruta | + território | Corresidentes: + território + escolaridade dos pais | Razão ÷ bruta (corresidentes) | + renda dos pais (sensib.) |
|---|---|---|---|---|---|---|---|
| Pré-escola | 29,1% | 14,6% | 14,5 | 15,5 | 8,6 (6,9–10,4) | 0,55 (0,48–0,63) | 0,44 (0,36–0,52) |
| Fundamental | 27,4% | 12,6% | 14,8 | 15,8 | 8,7 (7,9–9,4) | **0,56 (0,52–0,59)** | 0,45 (0,41–0,48) |
| Médio | 24,6% | 8,3% | 16,3 | 15,7 | 10,9 (9,5–12,2) | **0,63 (0,59–0,68)** | 0,55 (0,50–0,60) |
| Graduação | 75,9% | 73,0% | 2,9 | 0,6 (n.s.) | 2,5 | 0,51 (0,28–0,74) | 0,43 |

Em 2016 o padrão é o mesmo (fundamental: bruta 13,4; razão 0,56). **Composição da graduação:** pessoas negras são
52,8% (51,3–54,4) dos estudantes da graduação pública e 49,1% da privada — diferença +3,7 (2,0–5,4); em 2016, 49,2% ×
43,0% (+6,2).

**Desvio declarado:** a coluna "+ renda dos pais" (renda do trabalho de responsável e cônjuge) foi acrescentada
depois da primeira rodada, como sensibilidade; a hipótese é julgada pela especificação pré-registrada.

**Leitura das hipóteses**

- **H1 (a rede é sobretudo renda/escolaridade da família):** **refutada** na especificação pré-registrada — com a mesma
  escolaridade dos pais e o mesmo lugar, sobram 56% (fundamental) e 63% (médio) da diferença bruta. Com a renda dos
  pais, sobram 45% e 55%: cerca de metade da diferença de acesso à escola privada não está associada a escolaridade,
  renda dos pais e lugar.
- **H2 (graduação pública mais negra que a privada):** **confirmada** (+3,7 p.p.), mas a distância **diminuiu** desde
  2016 (+6,2): a privada ficou mais negra mais depressa (ProUni/FIES/EAD, a confirmar).

## 11. Afirmações permitidas

- "Na educação básica, crianças brancas estão duas vezes mais na escola privada que crianças negras (27% × 13% no
  fundamental); metade dessa diferença persiste entre famílias com a mesma escolaridade, renda e lugar."
- "Na graduação pública, 53% dos estudantes são negros; na privada, 49%."

## 12. Afirmações proibidas

- "Escola privada é melhor" (a PNADC não mede qualidade; a pública inclui as federais).
- Atribuir a mudança da composição da graduação às cotas (descrição, sem desenho causal; Bloco G).
