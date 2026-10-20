# Ficha de pesquisa — `H2` · Mesma origem, mesma renda? O resíduo do D1 com e sem origem

| Campo | Valor |
|---|---|
| ID no plano | `H2.1`–`H2.4` (`docs/PLANO_DE_ANALISE.md`, Bloco H) |
| Onda | 4 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Proposto** |
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
