# Ficha de pesquisa — `S0` · Quem fica fora da população de referência?

| Campo | Valor |
|---|---|
| ID no plano | `S0.1`, `S0.2` (`docs/PLANO_DE_ANALISE.md`, Bloco S). `S0.3` (perfis de quem está fora): **não feito** nesta rodada |
| Onda | 1 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 13/10/2026) |
| PR | Onda 1 (`onda1/regeneracao`) |

## 1. Pergunta

Que parcela das pessoas de 18+ de cada raça e sexo está em P1 (ocupados com renda do trabalho principal > 0), e
a chance de estar em P1 difere por raça depois de controlar idade, escolaridade, região e sexo?

## 2. Tipo

`D` (S0.1) e `C` (S0.2: diferença ajustada por covariáveis, sem leitura causal).

## 3. Estimando

- S0.1: % das pessoas 18+ em cada condição: (a) P1; (b) ocupado sem renda do trabalho principal; (c) desocupado;
  (d1) fora da força, desalentado; (d2) fora da força, outros. Por raça (Branca, Negra, Indígena, Amarela) × sexo,
  por trimestre.
- S0.2: efeito marginal médio (EMM) de ser Negra ou Indígena (vs. Branca) em Pr(P1), em p.p., de um logit ponderado
  com sexo, 6 faixas de idade, 7 níveis de instrução (`VD3004`) e 5 regiões; janelas 2012 (4 trimestres) e
  2025T3–2026T2; total e por sexo.

## 4. População

Pessoas de 18+ (Ignorado fora). Nenhuma renda envolvida além da definição de P1.

## 5. Método

- **S0.1:** proporções ponderadas (`V1028`); sem EP nesta versão (n por célula reportado).
- **S0.2:** logit ponderado (`statsmodels` GLM, só para os coeficientes); **EP design-based**: a variável
  linearizada do EMM combina o resíduo g_i − EMM com a influência dos coeficientes (sanduíche) e vai para a
  linearização Estrato/UPA (`sensibilidade_populacao.efeitos_marginais_entrada`). Testado contra o delta sobre o
  sanduíche HC0 em amostra aleatória simples.
- **FDR:** não se aplica (2 grupos × 3 recortes × 2 janelas, leitura descritiva com IC).

## 6. Dados

PNAD Contínua trimestral, `data/raw/pnadc_extraido_v2`, 2012T1–2026T2.

## 7. Hipóteses concorrentes

| # | Hipótese | Previsão |
|---|---|---|
| H1 | Negros entram menos em P1 por desvantagem no mercado de trabalho mesmo com as mesmas características | EMM negativo |
| H2 | A diferença bruta vem de composição (idade, escolaridade, região) | EMM ≈ 0 ou de sinal oposto ao bruto |

## 8. O que refutaria

H2 seria refutada por um EMM negativo e significativo para Negra nas duas janelas.

## 9. Armadilhas

- "Controlar escolaridade" absorve desigualdade que já é racial (a escolaridade difere por raça): o EMM não é "o
  efeito da raça", é a diferença entre pessoas com as mesmas características observadas.
- Desalento só é definido para quem está fora da força.

## 10. Resultados

**S0.1, 2026T2** (`composicao_populacao_referencia.parquet`), % das pessoas 18+:

| | P1 | Ocupado sem renda | Desocupado | Fora, desalentado | Fora, outros |
|---|---|---|---|---|---|
| Branca, homens | 73,2 | 0,4 | 2,6 | 0,7 | 23,0 |
| Branca, mulheres | 53,5 | 0,9 | 2,6 | 0,6 | 42,3 |
| Negra, homens | 72,4 | 0,5 | 3,8 | 1,6 | 21,7 |
| Negra, mulheres | 49,1 | 1,0 | 3,9 | 1,8 | 44,2 |
| Indígena, total | 58,5 | 1,4 | 3,1 | 1,6 | 35,5 |

Em 2012T1 estavam em P1: Branca 60,5%, Negra 58,9%, Indígena 54,9% (mulheres: 48,8%, 45,2%, 39,6%).

**S0.2** (`selecao_entrada_populacao_referencia.parquet`), Negra vs. Branca:

| Janela | Recorte | Diferença bruta | EMM ajustado (IC 95%) |
|---|---|---|---|
| 2012 | Total | −2,5 p.p. | **+1,4** (+1,1 a +1,7) |
| 2025T3–2026T2 | Total | −2,1 | **+1,3** (+1,0 a +1,7) |
| 2025T3–2026T2 | Homens | −0,7 | +1,2 (+0,7 a +1,6) |
| 2025T3–2026T2 | Mulheres | −4,1 | +1,5 (+1,1 a +2,0) |

Indígena: EMM sem diferença distinguível de zero em todos os recortes (IC de ±2 a ±4 p.p.).

**Leitura.** A menor presença bruta de pessoas negras (sobretudo mulheres) em P1 desaparece e até se inverte
quando se comparam pessoas da mesma idade, escolaridade, região e sexo: a diferença bruta de acesso é de
composição (H2). Isso **não** diminui o resultado do S1: o hiato de P4 cresce porque quem está fora de P1 entra
com renda zero e a composição educacional é parte da desigualdade racial.

## 11. Afirmações permitidas

- "No 2º trimestre de 2026, 49,1% das mulheres negras de 18+ estavam ocupadas com renda do trabalho, contra 53,5%
  das mulheres brancas."
- "Com a mesma idade, escolaridade, região e sexo, a chance de uma pessoa negra estar ocupada com renda não é
  menor que a de uma pessoa branca (+1,3 p.p.; IC 95% +1,0 a +1,7)."

## 12. Afirmações proibidas

- "Não há discriminação no acesso ao emprego." (o EMM condiciona em escolaridade, que é ela mesma desigual; e
  não mede qualidade do emprego)
- Comparar o EMM com o hiato de renda como se fossem a mesma escala.
