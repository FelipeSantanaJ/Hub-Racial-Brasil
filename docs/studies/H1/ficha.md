# Ficha de pesquisa — `H1` · Transmissão educacional pais → filhos, por raça (com o viés de corresidência medido)

| Campo | Valor |
|---|---|
| ID no plano | `H1.1`–`H1.4`, `E5` (`docs/PLANO_DE_ANALISE.md`, Blocos H e E) |
| Onda | 4 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Proposto** |
| PR | `onda4/e-h` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026).
> **Declaração obrigatória:** associação entre origem observada e destino; não efeito causal da origem; amostra
> restrita a quem mora com os pais.

## 1. Pergunta

Entre jovens que moram com pai ou mãe, quanto a escolaridade dos pais prediz a deles, essa associação é igual para
brancos e negros com a **mesma** origem, mudou entre 2012 e 2025–26 — e quanto a restrição a quem mora com os pais
distorce essas respostas?

## 2. Tipo

`C`. Associação condicional; a PNADC não pergunta a escolaridade dos pais — só é observada quando moram juntos.

## 3. Estimando

- **Ligação:** filho(a) = `V2005` 04 (filho do responsável e do cônjuge), 05 (só do responsável) ou 06 (enteado); pais =
  responsável (01) e cônjuge (02/03) do mesmo domicílio (UPA + V1008 + V1014). **Escolaridade de origem** = maior
  `VD3004` entre responsável e cônjuge, em 4 grupos: até fundamental incompleto; fundamental completo a médio
  incompleto; médio completo a superior incompleto; superior completo.
- **Desfechos do filho:** médio completo aos 19–24; superior completo aos 25–29; frequenta ou concluiu superior aos 18–24.
- **H1.1 / H1.3:** Pr(desfecho | origem, raça) — matriz por grupo de origem; diferença Branca − Negra **dentro** de cada
  origem (p.p.) e a média ponderada dessas diferenças (padronizada pela distribuição de origem dos negros).
- **H1.2:** mobilidade ascendente = filho de 25–29 com grupo de escolaridade acima do dos pais; descendente; imóvel.
- **H1.4:** as mesmas medidas nas janelas 2012 e 2025T3–2026T2.
- **Viés de corresidência (quantificado):** (a) % dos jovens de cada idade (18–29) que moram com pai/mãe, por raça;
  (b) desfecho do jovem (observável para **todos**) entre corresidentes × não corresidentes, por raça; (c) a diferença
  racial do desfecho na população inteira × na subamostra corresidente — quanto da diferença a subamostra
  super/subestima.

## 4. População

Pessoas de 18 a 29 anos (Branca, Negra; Indígena com ressalva), PNAD Contínua trimestral; subamostra corresidente para
as medidas de origem.

## 5. Método

Proporções por domínio e MQO linear (`bloco_d.Sistema`); influência linearizada por Estrato/UPA; janelas de 4
trimestres empilhados (a mesma pessoa pode aparecer em mais de um trimestre: linearização por UPA). FDR entre os 4
grupos de origem de um desfecho × janela.

## 6. Dados

PNAD Contínua trimestral v2: `V2005`, `V2009`, `V2007`, `V2010`, `VD3004`, `V3002`, `V3003A`/`V3003`, chave de domicílio.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **A origem explica a maior parte da diferença educacional** | Diferença Branca − Negra padronizada pela origem < metade da bruta (superior aos 25–29, corresidentes) |
| H2 | **Mesma origem, destinos diferentes** (desvantagem que não vem da família) | Diferença Branca − Negra > 0 com IC excluindo zero **dentro** de pelo menos 3 dos 4 grupos de origem |
| H3 | **Transmissão enfraquecendo** | Diferença no desfecho entre filhos de pais com superior e filhos de pais com até fundamental incompleto menor em 2025–26 que em 2012 |
| H4 | **A corresidência seleciona por raça** | Diferença racial no desfecho entre corresidentes difere da diferença na população inteira em mais de 3 p.p. |

## 8. O que refutaria

- H1 refutada se a diferença padronizada for ≥ metade da bruta.
- H2 refutada se em 2 ou mais grupos de origem o IC incluir zero.
- H3 refutada se o IC da mudança no gradiente de origem incluir zero ou for positivo.
- H4 refutada se as duas diferenças raciais ficarem a menos de 3 p.p. (então o viés de corresidência, nessa medida, é
  pequeno).

## 9. Armadilhas

- **Corresidência:** aos 25–29 a maioria já saiu de casa, e quem fica é selecionado (renda, casamento, estudo).
- **Jovens ainda estudando:** aos 18–24, superior incompleto pode virar completo; por isso "frequenta ou concluiu".
- **Escolaridade dos pais** medida hoje (pais que voltaram a estudar).
- **Pais e mães diferentes de pai e mãe biológicos** (enteados; famílias recompostas); responsável pode ser avó/avô
  (aí o jovem é neto — `V2005` 10 — e fica fora).
- Teto: filhos de pais com superior não podem "subir".
