# Ficha de pesquisa — `H1` · Transmissão educacional pais → filhos, por raça (com o viés de corresidência medido)

| Campo | Valor |
|---|---|
| ID no plano | `H1.1`–`H1.4`, `E5` (`docs/PLANO_DE_ANALISE.md`, Blocos H e E) |
| Onda | 4 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 20/10/2026) |
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

## 10. Resultados

Tabelas: `h1_corresidencia`, `h1_transmissao_educacional`. p.p.; IC 95%; janela 2025T3–2026T2 salvo indicação.

**Viés de corresidência**

| Medida | 2012 | 2025–26 |
|---|---|---|
| Moram com pai/mãe, 18–24: Branca / Negra / Indígena | 64,5% / 58,4% / 48,8% | 60,1% / 54,4% / 46,3% |
| Moram com pai/mãe, 25–29: Branca / Negra / Indígena | 35,7% / 31,4% / 20,0% | 31,3% / 26,5% / 22,0% |
| Superior completo 25–29, dif. Branca − Negra: todos / corresidentes | 15,4 / 19,1 | 18,5 / 18,1 |
| **Viés (corresidentes − todos)**: superior 25–29 | **+3,6 (2,5–4,7)** | −0,4 (−2,0 a 1,3) |
| Viés: médio completo 19–24 | −0,4 | −2,3 (−3,1 a −1,5) |
| Viés: frequenta ou concluiu superior 18–24 | +2,4 (1,9–2,9) | +0,3 (n.s.) |

**Mesma origem, destinos diferentes — superior completo aos 25–29 (corresidentes)**

| Escolaridade dos pais | Branca | Negra | Branca − Negra |
|---|---|---|---|
| G1 até fundamental incompleto | 15,3% | 8,4% | 6,9 (4,1–9,7) |
| G2 fundamental completo a médio incompleto | 22,1% | 15,9% | 6,3 (1,9–10,7) |
| G3 médio completo a superior incompleto | 34,1% | 24,3% | 9,8 (6,3–13,3) |
| **G4 superior completo** | 64,9% | 49,0% | **15,9 (11,7–20,2)** |
| Bruta (corresidentes) | | | 18,1 (16,1–20,2) |
| **Padronizada pela origem dos negros** | | | **9,2 (7,3–11,1)** — razão 0,51 (0,44–0,57) |

O mesmo para "frequenta ou concluiu superior" aos 18–24 (razão 0,52) e médio completo aos 19–24 (0,50). Em 2012,
razões de 0,51 a 0,61.

**Gradiente de origem (G4 − G1) e mudança desde 2012** (Branca + Negra): superior 25–29 53,6 → 48,4 (**−5,2; −8,5 a
−1,8**); médio 19–24 46,8 → 32,0 (−14,8; −16,7 a −13,0). O gradiente é **menor para negros** (superior: 40,6 × 49,6
para brancos): pais negros com diploma "transmitem" menos o diploma aos filhos.

**Mobilidade (25–29, corresidentes):** ascendente 38,1% (brancos) × 48,0% (negros) — negros partem de mais baixo; dentro
da mesma origem, brancos sobem mais (G1: +3,8; G3: +9,8 p.p.). Descendente: 15,1% × 12,9%; dentro de G3, negros descem
mais (+4,6 p.p.).

**Leitura das hipóteses**

- **H1 (a origem explica a maior parte):** **refutada pelo critério** — a diferença padronizada é 51% da bruta (IC
  44–57%, inclui a metade): a escolaridade dos pais responde por cerca de **metade**, não mais.
- **H2 (mesma origem, destinos diferentes):** **confirmada** nos 4 grupos de origem, e a diferença **cresce** com a
  origem: entre filhos de pais com diploma, 65% dos brancos e 49% dos negros têm diploma.
- **H3 (transmissão enfraquecendo):** **confirmada** (gradiente −5,2 p.p. no superior; −14,8 no médio).
- **H4 (a corresidência seleciona por raça):** **confirmada só em 2012** para o superior (+3,6 p.p.); em 2025–26 o viés
  fica abaixo de 3 p.p. em todos os desfechos (maior: −2,3 no médio). A subamostra corresidente, hoje, reproduz bem a
  diferença racial da população de 18–29.

## 11. Afirmações permitidas

- "Entre jovens que moram com os pais, cerca de metade da diferença racial em ter diploma superior está associada à
  escolaridade dos pais; a outra metade aparece mesmo entre filhos de pais com a mesma escolaridade."
- "Entre filhos de pais com diploma superior, 65% dos jovens brancos de 25 a 29 anos que moram com os pais têm diploma,
  contra 49% dos negros."

## 12. Afirmações proibidas

- Generalizar para quem não mora com os pais sem a ressalva (declaração obrigatória do bloco).
- "A origem familiar causa X% da desigualdade educacional."
