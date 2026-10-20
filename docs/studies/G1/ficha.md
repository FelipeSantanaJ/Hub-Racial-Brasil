# Ficha de pesquisa — `G1` · Lei 12.711/2012 (cotas): a presença de estudantes negros entre os ingressantes das federais aumentou?

| Campo | Valor |
|---|---|
| ID no plano | `G1` (`docs/PLANO_DE_ANALISE.md`, Bloco G) |
| Onda | 5 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 20/10/2026) |
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

Tabelas: `g1_cotas_federais` (event study, sensibilidades, Callaway–Sant'Anna) e `g1_series_grupos` (médias por grupo
e ano); `src/processing/bloco_g.py`, `--so g1`. EMD de Y1 = 8,5 p.p. (G6): o desenho só detecta efeitos dessa ordem.
113 instituições (73 federais tratadas, 40 estaduais/municipais de controle), 2009–2023. "ep" = maior entre CR1 e
bootstrap por instituição (999); FDR (BH) na família principal de 12 testes.

**Event study, especificação principal (p.p., relativo a 2012)**

| Desfecho | 2013–2015 | **2016–2019** | 2020–2023 | Pré-tendência (p, 2009–2011) |
|---|---|---|---|---|
| Y1 · % negra entre declarados | +11,4 (5,6 a 17,3) | **+9,0 (3,0 a 15,1)**, p-BH 0,022 | +1,5 (−4,4 a 7,4) | 0,26 |
| Y1b · não declarados como negros (conservador) | −0,2 (−10,2 a 9,7) | **−5,0 (−20,7 a 10,6)** | −10,4 (−23,0 a 2,2) | 0,39 |
| Y1c · não declarados como não negros (limite) | +10,6 (2,5 a 18,8) | +17,5 (9,3 a 25,6) | +6,6 (−4,6 a 17,8) | 0,37 |
| Y2 · % de escola pública (EMD 16 p.p.) | +6,3 (−13,5 a 26,2) | +17,1 (−3,8 a 38,0) | +8,7 (−7,0 a 24,4) | 0,39 |
| Y3 · % sem cor/raça declarada | −10,8 (−25,2 a 3,6) | **−22,5 (−39,9 a −5,1)**, p-BH 0,045 | −17,0 (−35,2 a 1,3) | 0,19 |

**Sensibilidades de Y1 em 2016–2019:** sem pesos +5,8 (0,5 a 11,1); painel não balanceado +8,2 (2,7 a 13,8); limiar
de 1% +8,9 (2,3 a 15,6); limiar de 10% +7,5 (1,9 a 13,1); controle só com quem nunca adotou +8,6 (1,8 a 15,4). Y1b
em todas: IC contém zero, exceto "controle só com quem nunca adotou", em que é **negativo** (−12,0; −22,1 a −1,8).
**Callaway–Sant'Anna** (adoção escalonada pelo dado, todas as 157 públicas): média pós-adoção até 2019 +6,4 (3,1 a
9,7) com controle "nunca tratado" e +8,7 (4,3 a 13,1) com "ainda não tratado"; efeito máximo 1–3 anos depois da
adoção, perto de zero a partir do 6º ano.

**Séries brutas (médias ponderadas):** nas federais tratadas, a % negra entre declarados passou de 42,3 (2012) para
~55 (2014–2019) e 50,3 (2023); no controle, de 37,2 para ~40 e 43,1. Ao mesmo tempo, a % **sem cor declarada** nas
tratadas caiu de 55,5 (2012) para 15,1 (2016) e 6,0 (2023); no controle, de 44,9 para 23,6 e 16,7. Antes da lei,
**mais da metade** dos ingressantes das federais não tinha cor/raça registrada.

**Leitura das hipóteses (regras da seção 8)**

- **H1 (a lei aumentou o ingresso negro): não afirmada.** Y1 sobe 9,0 p.p. (acima do EMD), mas a regra
  pré-registrada se aplica: o IC de Y1b contém zero **e** Y3 cai 22 p.p. (> 10). O aumento de Y1 é compatível com
  artefato de declaração — a lei obrigou cotistas a declarar cor, e a declaração passou de menos da metade para quase
  todos os ingressantes, mais nas tratadas que no controle.
- **H2 (artefato de declaração): não refutada** (é a leitura que os dados não conseguem descartar).
- **H3 (SiSU/REUNI):** pré-tendência não rejeitada (p = 0,26), mas os δ de 2009–2011 são positivos (+5,0, +4,6,
  +2,9): 2012 é um ano atípico no controle (Y1 do controle salta de 34,7 para 37,2). Contra a média de 2009–2011 em
  vez de 2012, o ganho de 2016–2019 seria ~5 p.p. (9,0 − 4,1; conta aritmética, sem IC) — abaixo do EMD. Fragilidade
  declarada; não foi reestimado (seria desvio do registro).
- **H4 (deslocamento):** não identificável aqui (ressalva mantida).
- **Primeiro estágio (Y2) sem poder** (EMD 16 p.p.; procedência escolar mal preenchida, ausente em 2009).

### 10b. Análise posterior (NÃO pré-registrada, 20/10/2026): Rambachan–Roth, magnitudes relativas

Pedida depois dos resultados (decisão do Felipe, 20/10/2026). Tabela `g1_sensibilidade_rr` (`bloco_g --so g1rr`).
Pergunta: quanto as tendências de federais e controles poderiam divergir depois de 2012 — em múltiplos M̄ da maior
variação anual da diferença antes da lei (Δmax = 2,85 p.p. em Y1, entre 2011 e 2012) — antes que o IC inclua zero?
Versão **conservadora e simplificada** de Rambachan & Roth (2023, *Review of Economic Studies*): Δmax tratado como
conhecido e viés acumulado M̄·Δmax·h somado ao IC (o FLCI do artigo é mais estreito; o pacote `HonestDiD` não foi usado).

| Y1 · % negra entre declarados | Estimativa | IC com M̄ = 0,25 | IC com M̄ = 1 | **M̄ de ruptura** |
|---|---|---|---|---|
| 2013–2015 | +11,4 | 4,2 a 18,7 | −0,1 a 23,0 | **0,98** |
| 2016–2019 (parâmetro principal) | +9,0 | −1,0 a 19,0 | −12,7 a 30,8 | **0,19** |
| 2020–2023 | +1,5 | −11,2 a 14,2 | — | 0 (IC já contém zero) |

**Leitura:** o salto de 2013–2015 resiste a violações de tendência do tamanho da maior variação pré-lei; o efeito de
2016–2019 não resiste nem a um quinto dela. Reforça a seção 10: não há efeito afirmável em 2016–2019. Y1b (conservador)
tem IC contendo zero já com M̄ = 0.

## 11. Afirmações permitidas

- "Com dados por instituição do Censo da Educação Superior, não é possível separar o efeito da Lei de Cotas sobre a
  presença de estudantes negros nas federais da melhora no registro de cor/raça que a própria lei provocou: antes de
  2013, mais da metade dos ingressantes das federais não tinha cor registrada."
- "Entre os ingressantes com cor declarada, a proporção de negros nas federais sem cotas próprias subiu ~9 pontos a
  mais que nas estaduais e municipais entre 2012 e 2016–2019; esse número não é robusto à forma de tratar quem não
  declarou."

## 12. Afirmações proibidas

- "As cotas não funcionam" a partir de um efeito não detectado.
- "As cotas aumentaram a presença negra no ensino superior brasileiro" (o desenho vê as federais tratadas, não o
  sistema; deslocamento não identificado).
- Atribuir o efeito à subcota racial separada da reserva por escola pública (as duas vêm juntas na lei).
- "A Lei de Cotas aumentou em 9 pontos a presença negra nas federais" (Y1 sem a ressalva de declaração).
- "A Lei de Cotas não aumentou a presença negra" (o desenho não separa efeito de artefato; EMD de 8,5 p.p.).

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-20 | Claude Code | criação (seções 1–9 antes de rodar) |
| 2026-10-20 | Claude Code | resultados (seções 10–12) depois do G6 |
| 2026-10-20 | Claude Code | 10b: Rambachan–Roth (posterior, não pré-registrada) |
