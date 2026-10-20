# Ficha de pesquisa — `H2` · Mesma origem, mesma renda? O resíduo do D1 com e sem origem

| Campo | Valor |
|---|---|
| ID no plano | `H2.1`–`H2.4` (`docs/PLANO_DE_ANALISE.md`, Bloco H) |
| Onda | 4 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 20/10/2026) |
| PR | `onda4/e-h` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026).
> **Declaração obrigatória:** associação entre origem observada e destino; não efeito causal da origem; amostra
> restrita a quem mora com os pais.

## 1. Pergunta

Entre jovens ocupados que moram com pai ou mãe, o hiato racial de renda persiste quando se comparam filhos de pais com
a mesma escolaridade e renda? Quanto da parte não associada às covariáveis do D1 diminui ao incluir a origem? E pessoas
negras e brancas que partem da base têm a mesma chance de chegar ao topo?

## 2. Tipo

`C`. Subamostra selecionada (corresidência; H1); renda dos pais medida hoje, não na infância.

## 3. Estimando

- **Amostra:** filhos(as) (`V2005` 04/05/06) de 18 a 29 anos em P1 (ocupados com renda do trabalho principal > 0),
  Branca × Negra; janelas 2012 e 2025T3–2026T2.
- **H2.1 / H2.2:** coeficiente de Negra em ln renda com os controles da E8 do D1, na subamostra, e depois com o bloco
  **origem**: escolaridade máxima dos pais (4 grupos, H1), renda do trabalho dos pais (soma de `VD4019` real de
  responsável e cônjuge; ln(1 + x) e indicador de zero) e se algum dos pais é empregador ou servidor público. Mudança
  do coeficiente (com ψ combinados) e Gelbach do bloco origem ao lado dos blocos do D1. Comparação com a E8 do D1 na
  população inteira de 18–29 (mesma faixa etária).
- **H2.3:** elasticidade *proxy* da renda do filho em relação à renda do trabalho dos pais (ln–ln, pais com renda > 0),
  por raça.
- **H2.4:** matriz de transição por quintil da renda dos pais (quintis nacionais entre os domicílios da subamostra) ×
  quintil da renda do filho (quintis da subamostra): Pr(filho no quintil de cima | pais no quintil de baixo), por raça.

## 4. População

Ver acima. Sensibilidade: 22–29 anos (menos estudantes); Indígena fora (n).

## 5. Método

WLS (`bloco_d.Sistema`, `gelbach`); influência linearizada por Estrato/UPA; para H2.4, proporções por domínio.

## 6. Dados

PNAD Contínua trimestral v2: chave de domicílio, `V2005`, `VD4019`, `VD4009`, `VD3004` dos pais; variáveis do D1 do
filho; deflator do IBGE.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Parte do resíduo é herança** | Incluir a origem reduz o coeficiente de Negra (E8) em ≥ 25%, com IC da mudança excluindo zero |
| H2 | **O resíduo não é origem observada** | Redução < 10% |
| H3 | **Mobilidade do topo desigual** | Pr(quintil de cima \| pais no quintil de baixo) menor para negros (IC da diferença exclui zero) |

## 8. O que refutaria

- H1 refutada se a redução for < 25% ou o IC da mudança incluir zero; H2 refutada se ≥ 10%. Entre 10% e 25%: "redução
  modesta", nenhuma das duas.
- H3 refutada se o IC da diferença incluir zero.

## 9. Armadilhas

- **Corresidência** (H1): jovens ocupados que moram com os pais são selecionados (mais jovens, mais solteiros, renda
  menor); o resíduo na subamostra pode ser diferente do da população — por isso a comparação com a E8 de toda a faixa
  18–29.
- **Renda dos pais contemporânea** (e só do trabalho): não é a renda da infância; viés de atenuação na elasticidade.
- Pais aposentados ou fora do mercado têm renda do trabalho zero (indicador separado).
- Controlar origem é controlar um mediador anterior; não é "eliminar a discriminação".

## 10. Resultados

Tabelas: `h2_origem_renda`, `h2_mobilidade_quintis`. ln renda (log-pontos), IC 95%.

**H2.1 / H2.2 — hiato condicional (Branca × Negra), 18–29 anos em P1**

| Especificação | 2012 | 2025T3–2026T2 |
|---|---|---|
| E8 (controles do D1), todos de 18–29 | 0,069 (0,062–0,076) | 0,047 (0,038–0,056) |
| E8, só corresidentes | 0,067 | 0,048 (0,036–0,060) |
| **E8 + origem, corresidentes** | 0,045 | **0,028 (0,017–0,040)** |
| Mudança ao incluir a origem | −0,022 (−0,024 a −0,019); **−32%** | −0,020 (−0,024 a −0,016); **−42% (−53% a −30%)** |

Gelbach com o bloco origem (corresidentes, janela recente; hiato bruto 0,232): território 0,053 (23%), **origem 0,051
(22%; 0,046–0,056)**, vínculo 0,034, instrução 0,030, ocupação 0,029. A E8 da subamostra corresidente (0,048) é
praticamente igual à de todos os jovens (0,047): a seleção por corresidência quase não muda a parte não associada.

**H2.3 — elasticidade *proxy*** (ln renda do filho × ln renda do trabalho dos pais): Branca 0,219 (0,203–0,235), Negra
0,281 (0,266–0,296); diferença +0,062 (0,040–0,083). Em 2012: 0,242 × 0,283.

**H2.4 — quintis** (renda do trabalho dos pais × renda do filho, corresidentes, janela recente)

| Pais no quintil | Filho no quintil | Branca | Negra | Negra − Branca |
|---|---|---|---|---|
| 1 (base) | 5 (topo) | 8,2% | 5,5% | **−2,7 (−4,3 a −1,2)** |
| 1 | 1 | 30,4% | 40,9% | +10,5 (7,5–13,5) |
| 5 (topo) | 5 | 43,3% | 34,3% | −9,0 (−12,4 a −5,6) |
| 3 | 5 | 22,1% | 14,1% | −8,0 |

**Leitura das hipóteses**

- **H1 (parte do resíduo é herança):** **confirmada** — incluir a origem reduz a parte não associada do D1 em 42%
  (IC 30% a 53%) entre jovens que moram com os pais (32% em 2012).
- **H2 (o resíduo não é origem):** **refutada.**
- **H3 (mobilidade do topo desigual):** **confirmada** — partindo dos 20% de baixo, 5,5% dos jovens negros chegam aos
  20% de cima, contra 8,2% dos brancos; e no topo, a permanência é menor para negros (34% × 43%).
- **Critério de saída da Onda 4 (H2.2):** o resíduo do D1, para jovens de 18–29, cai de 0,048 para 0,028 lp ao incluir
  escolaridade e renda dos pais — parte do que o D1 chama de "não associado" era origem não observada. Para adultos
  mais velhos (fora de casa) não é possível repetir.

## 11. Afirmações permitidas

- "Entre jovens que moram com os pais, comparar filhos de pais com a mesma escolaridade e renda reduz em cerca de 40% a
  parte do hiato de renda que não está associada às características observáveis; ainda sobra ≈ 3%."
- "Entre filhos de famílias dos 20% de menor renda, 5,5% dos jovens negros chegam aos 20% de maior renda, contra 8,2%
  dos brancos."

## 12. Afirmações proibidas

- "A herança familiar explica 40% da discriminação" (o resíduo não é discriminação; a origem é associação).
- Extrapolar para adultos acima de 29 anos ou para quem não mora com os pais.
- Ler a elasticidade como mobilidade intergeracional "verdadeira" (renda dos pais contemporânea, só do trabalho).
