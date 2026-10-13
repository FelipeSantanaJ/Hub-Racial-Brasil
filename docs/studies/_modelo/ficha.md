# Ficha de pesquisa — `<id>` · <título curto>

> Copiar esta pasta para `docs/studies/<id>/` (id = código do plano, ex.: `S1.1`, `D1`, `H2.2`).
> Toda seção é obrigatória; quando não se aplica, escrever "não se aplica" e por quê.
> Referências citadas de memória ficam marcadas *(a confirmar)* até serem conferidas.

| Campo | Valor |
|---|---|
| ID no plano | `<id>` (`docs/PLANO_DE_ANALISE.md`, Bloco <X>) |
| Onda | <0–6> |
| Responsável | <nome> |
| Criada em / atualizada em | <AAAA-MM-DD> / <AAAA-MM-DD> |
| Estado de publicação | **Bloqueado** / **Aprovado com ressalvas** / **Aprovado** (critérios em `docs/auditoria/rodada1.md`) |
| PR | #<n> |

## 1. Pergunta

<Uma frase, na forma de pergunta respondível com dados.>

## 2. Tipo

`D` (descrição) / `C` (contabilidade/decomposição) / `Q` (quase-experimento) / `M` (mecanismo; só organiza evidência externa).
**Justificativa do tipo:** <por que a pergunta não é de outro tipo; o que este desenho não permite concluir>.

## 3. Estimando

<O que exatamente se mede: estatística, unidade, escala (R$, razão, log-pontos, p.p.), grupo de referência
do hiato % (ex.: "relativo à média Negra"), período.>

## 4. População

- **Universo:** <ex.: ocupados 18+ com renda habitual do trabalho principal > 0 — `populacao.na_populacao_referencia`>
- **Renda:** <variável IBGE e conceito: VD4016 / VD4019 / VD5008…; nominal ou real; deflator>
- **Exclusões e quanto pesam:** <ex.: ocupados sem rendimento = x% da população 18+>
- **Sensibilidade obrigatória:** <ex.: 14+; todos os trabalhos (P3); população inteira (P4/P5)>

## 5. Método

- **Estimador:** <fórmula ou função do código>
- **Incerteza:** <`linearizacao_taylor_estrato_upa` / bootstrap Rao-Wu / regressão com cluster…>
- **Família de testes (FDR):** <quais comparações são corrigidas juntas e por quê; o padrão por tabela é o piso>
- **Efeito mínimo detectável (EMD):** <obrigatório para `Q` e para afirmações de "não há diferença"; calcular ANTES de estimar>
- **Regra de amostra mínima / supressão:** <ex.: célula com n < 30 ou CV > 30% não publica>

## 6. Dados

| Fonte | Variáveis | Período | Extrato / arquivo | Acesso |
|---|---|---|---|---|
| PNAD Contínua trimestral | <…> | <…> | `data/raw/pnadc_extraido_v2` | público |

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | <…> | <…> |
| H2 | <…> | <…> |

## 8. O que refutaria

<Resultado concreto, decidido ANTES de rodar, que faria abandonar ou rever a conclusão principal.>

## 9. Armadilhas

<Composição, reclassificação racial, quebra de série (4T2015, 2020–21, reponderação), seleção, heaping,
APC, corresidência (Bloco H), multiplicidade…>

## 10. Resultados

<Preenchido depois de rodar: números com IC, tabela/parquet de origem com `_meta.json`, gráficos permitidos.>

| Saída | Arquivo | `se_metodo` | Commit |
|---|---|---|---|
| <tabela> | `data/processed/<…>.parquet` | <…> | <…> |

## 11. Afirmações permitidas

- <frase exata que pode ir para texto público, com a ressalva obrigatória na mesma tela>

## 12. Afirmações proibidas

- <o que o resultado NÃO prova; ex.: "o resíduo é discriminação"; "as cotas não funcionam"; "o hiato vai acabar em 20XX">

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| <AAAA-MM-DD> | <nome> | criação |
