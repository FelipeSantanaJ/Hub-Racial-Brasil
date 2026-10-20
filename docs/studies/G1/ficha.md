# Ficha de pesquisa — `G1` · Lei 12.711/2012 (cotas): a presença de estudantes negros entre os ingressantes das federais aumentou?

| Campo | Valor |
|---|---|
| ID no plano | `G1` (`docs/PLANO_DE_ANALISE.md`, Bloco G) |
| Onda | 5 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
| PR | `onda5/g` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026). Antes desta ficha foram olhados só: os totais de ingressantes por
> ano (conferência contra os números oficiais) e a variável de **tratamento** (ingressantes por reserva étnica,
> `QT_ING_RVETNICO`), para contar instituições e coortes — **nenhuma** proporção de negros por instituição × ano. Os
> **níveis** de 2014 e 2023 das federais presenciais já tinham sido vistos no E6 (51,2% e 49,9% de negros entre os
> declarados); nem a tendência antes da lei nem o grupo de comparação foram vistos.
> Substitui o desenho antigo com coortes da PNADC (`did_cotas_universitarias*`, R2 da auditoria).

## 1. Pergunta

A Lei 12.711/2012 — reserva, a partir de 2013 e completa em 2016, de metade das vagas das instituições federais para
egressos de escola pública, com subcota para pretos, pardos e indígenas — aumentou a proporção de pessoas negras
entre os ingressantes dos cursos presenciais de graduação das federais que não tinham reserva étnica própria?

## 2. Tipo

`Q`. Diferença em diferenças com dado administrativo (censo das instituições), data de tratamento fixada em lei.
**Não permite concluir:** efeito sobre conclusão, renda ou mobilidade (G2); efeito sobre o sistema inteiro (pode haver
deslocamento de estudantes negros de estaduais/privadas para federais); efeito em federais que já tinham reserva.

## 3. Estimando

- **Y1 (principal):** % de ingressantes negros (pretos + pardos) entre os ingressantes com cor/raça declarada, por
  instituição × ano (cursos presenciais de graduação).
- **Y1b (conservador contra o artefato de declaração):** não declarados contados como negros. Como a lei exige
  autodeclaração dos cotistas, a declaração sobe nas tratadas; com esta definição, isso empurra o efeito **para baixo**.
- **Y1c:** não declarados contados como não negros (empurra para cima; só como limite).
- **Y2 (primeiro estágio):** % de ingressantes vindos de escola pública, entre os de procedência informada.
- **Y3 (mecanismo do artefato):** % de ingressantes sem cor/raça declarada.
- **Parâmetro:** ATT pós-implantação = média dos coeficientes do event study em **2016–2019** (lei completa, antes da
  pandemia), em p.p.; também 2013–2015 (implantação gradual) e 2020–2023, e cada ano.

## 4. População

- **Unidades:** instituições públicas (`TP_CATEGORIA_ADMINISTRATIVA` 1 federal, 2 estadual, 3 municipal), soma dos
  cursos presenciais de graduação (`TP_NIVEL_ACADEMICO` = 1, `TP_MODALIDADE_ENSINO` = 1).
- **Painel balanceado:** instituições com ≥ 30 ingressantes em todos os anos 2009–2023 (157: 92 federais, 59 estaduais,
  6 municipais).
- **Tratadas:** federais **sem** reserva étnica antes da lei — `QT_ING_RVETNICO` < 5% dos ingressantes em todos os anos
  2009–2012 (73 federais). Data de tratamento: 2013, para todas (a lei).
- **Controles:** estaduais e municipais sem reserva étnica em 2009–2012 (mesmo critério; 40: 34 estaduais e 6 municipais). Estaduais que adotaram
  reserva depois por lei estadual continuam no controle (definição só com dado antes da lei) — isso puxa o efeito para
  zero (conservador).
- **Fora:** federais com reserva própria antes de 2013 (19) e estaduais com reserva antes de 2013 (análise à parte, só
  descritiva).
- **Sensibilidade obrigatória:** (a) controle só com quem nunca adotou até 2023 (condiciona em dado posterior —
  declarado); (b) painel não balanceado; (c) sem pesos; (d) limiar de 1% e 10% na definição de "sem reserva";
  (e) **versão escalonada** (Callaway–Sant'Anna com coorte = primeiro ano com reserva étnica ≥ 5%, controle "nunca
  tratado" e "ainda não tratado"), que usa todas as instituições — com a ressalva de que a reserva informada oscila
  (71 instituições ficam abaixo do limiar depois de adotar: tratamento medido com erro).

## 5. Método

- **Estimador principal:** event study `Y_it = α_i + γ_t + Σ_{k≠2012} δ_k·1[t = k]·Tratada_i + ε_it`, 2009–2023,
  ano-base 2012, ponderado pelos ingressantes da instituição em 2012 (pergunta sobre estudantes, não sobre
  instituições). Com uma única data de tratamento, Callaway–Sant'Anna e Sun–Abraham coincidem com este estimador (o
  viés do TWFE com adoção escalonada não ocorre); a versão escalonada da seção 4(e) usa Callaway–Sant'Anna.
- **Incerteza:** EP agrupado por instituição (CR1) e bootstrap por instituição (999 reamostragens, percentil) — o
  reportado é o maior dos dois.
- **Pré-tendência:** δ_2009, δ_2010, δ_2011 conjuntamente iguais a zero (Wald); e o limite de Rambachan–Roth não é
  feito (sem pacote validado; a confirmar se vale implementar).
- **EMD:** ficha G6 (simulação só com 2009–2012). **Efeitos plausíveis (pré-registro):** de **2 a 10 p.p.** em Y1.
  Conta mecânica: com a lei completa, ≈ 50% das vagas para escola pública e, dentro delas, ≈ a proporção de PPI da UF
  (≈ metade ou mais) → ≈ 25% das vagas reservadas para PPI de escola pública; parte deles entraria de qualquer forma
  (deslocamento), o que deixa o efeito líquido plausível entre poucos pontos e ~10 p.p. Literatura com efeitos
  positivos sobre o ingresso de estudantes de escola pública e PPI: Vieira & Arends-Kuenning (2019, *Economics of
  Education Review*) e Mello (2022, *AEJ: Economic Policy*) *(a confirmar)*.
- **Regra de decisão:** a da ficha G6.
- **Família de testes (FDR):** {Y1, Y1b, Y2, Y3} × {2013–15, 2016–19, 2020–23} (12 testes), BH.
- **Regra de amostra:** instituição × ano com < 30 ingressantes declarados sai do Y1 (vira ausente).

## 6. Dados

| Fonte | Variáveis | Período | Extrato / arquivo | Acesso |
|---|---|---|---|---|
| INEP, Censo da Educação Superior (cursos) | `CO_IES`, categoria, modalidade, nível, `QT_ING`, `QT_ING_{BRANCA,PRETA,PARDA,AMARELA,INDIGENA,CORND}`, `QT_ING_RESERVA_VAGA`, `QT_ING_RVETNICO`, `QT_ING_PROCESC*` | 2009–2023 | `data/raw/externos/parquet/censo_superior_ies_2009_2023.parquet` (`src/ingestion/censo_superior_painel.py`) | público; download autorizado em 20/10/2026 |

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **A lei aumentou o ingresso negro** | δ > 0 em Y1 a partir de 2013, crescente até 2016; Y1b também > 0; Y2 > 0 |
| H2 | **Artefato de declaração** (a lei só fez declarar quem antes não declarava) | Y3 cai muito nas tratadas; Y1 sobe, mas Y1b não |
| H3 | **SiSU/REUNI, não a lei** (a nacionalização da seleção e a expansão das federais mudaram a composição) | pré-tendência ≠ 0 em 2009–2011 (expansão e SiSU começam antes de 2013), ou efeito sem degrau em 2013–2016 |
| H4 | **Deslocamento sem efeito líquido no sistema** | δ > 0 nas federais com queda equivalente nas estaduais do controle — não identificável aqui; ressalva obrigatória |

## 8. O que refutaria

- **H1** é refutada se o ATT de 2016–2019 em Y1 tiver IC 95% inteiramente abaixo de 2 p.p. (o limite inferior do
  plausível), com EMD ≤ 2; ou se Y1b (conservador) tiver IC contendo zero **e** Y3 cair mais de 10 p.p. (então o
  aumento de Y1 é compatível com artefato de declaração e a ficha não afirma efeito).
- **Pré-tendência:** Wald de δ_2009–2011 com p < 0,05 → o efeito vira "não identificado" (descrição apenas).

## 9. Armadilhas

- **Declaração:** cor/raça não declarada era ~33% nas federais presenciais em 2014 e ~7% em 2023 (E6); a lei obriga
  declaração dos cotistas → Y1b e Y3 obrigatórios.
- **Reclassificação racial** no país no mesmo período (B2): afeta tratados e controles; o DiD remove o comum.
- **SiSU (2010+) e REUNI (2007–2012)** concentrados nas federais: confundidores com momento parecido.
- **Reserva informada oscila** (tratamento medido com erro) → o desenho principal usa a data legal, não o dado.
- **Controles diferentes** (estaduais e municipais, menores, outras leis estaduais de cotas); 40 controles, quase todos
  estaduais.
- **Novas instituições e desmembramentos** (ex.: campi que viram universidades) somem do painel balanceado ou mudam o
  tamanho da original; sensibilidade com painel não balanceado.
- 2020–2021: pandemia (ingresso e registro atípicos) — fora do parâmetro principal.

## 10. Resultados

<Preenchido depois de rodar (só se o G6 indicar poder).>

## 11. Afirmações permitidas

<Depois de rodar.>

## 12. Afirmações proibidas

- "As cotas não funcionam" a partir de um efeito não detectado.
- "As cotas aumentaram a presença negra no ensino superior brasileiro" (o desenho vê as federais tratadas, não o
  sistema; deslocamento não identificado).
- Atribuir o efeito à subcota racial separada da reserva por escola pública (as duas vêm juntas na lei).

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-20 | Claude Code | criação (seções 1–9 antes de rodar) |
