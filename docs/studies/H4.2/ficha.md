# Ficha de pesquisa — `H4.2` · Entrar e sair da formalidade e do emprego: transições trimestrais por raça (painel da PNADC)

| Campo | Valor |
|---|---|
| ID no plano | `H4.2` (`docs/PLANO_DE_ANALISE.md`, Bloco H) |
| Onda | 6 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
| PR | `onda6/integracao` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026). Refaz `transicao_desemprego_emprego` e
> `transicao_informal_formal` (mapa de cobertura: `esp` — atrito não medido, sem série, sem EP design-based).

## 1. Pergunta

De um trimestre para o seguinte, pessoas negras saem do desemprego e entram no emprego com carteira com a mesma
frequência que pessoas brancas — e perdem a carteira com a mesma frequência? A diferença persiste com as mesmas
características, e mudou entre 2012 e 2026?

## 2. Tipo

`C`. Probabilidades de transição e diferenças condicionais. **Não permite concluir** discriminação na contratação
(as características não observadas diferem).

## 3. Estimando

Para pessoas de 18+ observadas em dois trimestres consecutivos (visitas *k* e *k*+1):

- **T1 desocupado → ocupado:** entre desocupados em *t*, % ocupados em *t*+1.
- **T2 sem carteira → com carteira:** entre empregados do setor privado sem carteira (VD4009 = 02) em *t*, % empregados
  com carteira (VD4009 = 01) em *t*+1.
- **T3 com carteira → perda:** entre empregados com carteira em *t*, % sem carteira, conta própria ou desocupados em *t*+1.
- Por raça (Branca, Negra, Indígena), **por ano** (pares de trimestres agregados no ano de *t*) e no período inteiro;
  diferença Negra − Branca em p.p., bruta e com idade (faixas de 5 anos), sexo, instrução (VD3004), UF e ano.

## 4. População

Pessoas de 18+ (P1 não se aplica: a transição é sobre a situação de trabalho). Ignorado fora.

- **Ligação da mesma pessoa (mais estrita que a da tabela antiga):** UPA, V1008 (domicílio), V1014 (grupo de
  rotação), V2003 (ordem), V2007 (sexo) e data de nascimento (V2008, V20081, V20082) iguais; V1016 (visita) avançando
  exatamente 1; quando a data de nascimento é ignorada (99/9999), exige idade consistente (diferença 0 ou 1).
- **Atrito:** % de pessoas da visita *k* (≤ 4) encontradas na *k*+1, por raça e ano; **sensibilidade:** reponderação
  pelo inverso da probabilidade de ser encontrado (logit em idade, sexo, instrução, UF, raça, situação de trabalho).

## 5. Método

- Taxas ponderadas por V1028 de *t*; EP por linearização Estrato/UPA de *t* (`variancia`).
- Condicional: MQO linear (modelo de probabilidade) com `bloco_d.Sistema` e EP por `ep_de`.
- **Tendência** na série anual da diferença: EWC (`src/inference/tendencia.py`), como no Bloco B; e teste de degrau em
  2015–16 e 2020–21.
- **Família FDR:** {T1, T2, T3} × {bruta, condicional} × {Negra, Indígena} no período inteiro; a série anual à parte.
- Regra de amostra: célula com n < 30 transições na origem não publica (`precisao`).

## 6. Dados

PNAD Contínua trimestral 2012T1–2026T2, extrato v2 (`data/raw/pnadc_extraido_v2`): UPA, V1008, V1014, V1016, V2003,
V2007, V2008, V20081, V20082, V2009, V2010, VD3004, VD4002, VD4009, V1028, Estrato, UF.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Formalização mais difícil** | T2 menor e T3 maior para negros, também condicional |
| H2 | **Só composição** | diferenças condicionais com IC contendo zero |
| H3 | **Mais sensível ao ciclo** | a diferença em T3 (perda) aumenta em 2015–16 e 2020 |
| H4 | **Atrito seletivo** | encontrados na visita seguinte ≠ por raça em ≥ 3 p.p., e a reponderação muda a diferença em ≥ 1 p.p. |

## 8. O que refutaria

H1 é refutada se as diferenças condicionais de T2 e T3 tiverem IC contendo zero, ou sinais contrários aos previstos.
H3, se a série não tiver degrau significante (EWC) nos anos de crise.

## 9. Armadilhas

- **Erro de classificação** gera transições espúrias (alguém classificado errado num trimestre "transita"); pode
  diferir por raça se a qualidade da resposta diferir (informante proxy).
- **Atrito** não aleatório (mudança de domicílio) → medido e reponderado.
- Viés de grupo de rotação; 2020–21 (telefone) com mais atrito.
- VD4009 muda com a reforma do questionário? (a confirmar no dicionário; o Hub usa VD4009 desde 2012).

## 10. Resultados

Tabelas: `h42_transicoes` e `h42_atrito_tendencia` (`src/processing/bloco_integracao.py`, `--so h42`). 57 pares de
trimestres consecutivos (2012T1→T2 … 2026T1→T2); nenhum par duplicado na ligação estrita. Pares: 745.827 (T1),
998.797 (T2), 2.703.631 (T3).

**Desvio do registro prévio (declarado):** a sensibilidade ao atrito usou **ajuste por células** (raça × sexo × 4
faixas de idade × 3 de instrução × região × situação de trabalho × ano: peso × elegíveis ÷ encontrados), e não um
logit, por memória (dezenas de milhões de pessoas-trimestre).

| 2012–2026 (p.p.) | Branca | Negra | Negra − Branca bruta | **Negra − Branca com idade, sexo, instrução, UF, ano** |
|---|---|---|---|---|
| T1 desocupado → ocupado | 29,9% | 30,9% | +1,0 (0,7 a 1,4) | **+1,1** (0,7 a 1,5) |
| T2 sem carteira → com carteira | 15,1% | 12,3% | −2,8 (−3,0 a −2,6) | **+0,5** (0,2 a 0,7) |
| T3 com carteira → perda | 6,6% | 8,0% | +1,3 (1,2 a 1,4) | **+0,18** (0,08 a 0,28) |

Indígenas: T2 10,5% (−4,6 p.p. bruta; −1,0 condicional, IC −2,4 a 0,5); T3 7,9% (+1,3 bruta; +0,3 condicional, IC
contém zero). Todas as diferenças Negra − Branca têm p-BH < 0,01.

**Atrito:** % dos elegíveis (visita ≤ 4) encontrados na visita seguinte — brancos 80–91%, negros 78–89%, indígenas
70–88%; a diferença Branca − Negra fica entre 1,6 e 3,6 p.p. (maior em 2014 e 2020). O ajuste por células muda as diferenças
brutas em no máximo 0,05 p.p.

**Série anual da diferença Negra − Branca (bruta):** T2 foi de −3,8 (2012) a −1,2/−2,4 (2025–26): a desvantagem na
formalização encolheu (+0,22 p.p. por ano, IC EWC −0,02 a 0,45 — não confiável); degrau de +2,5 p.p. em 2020 (IC 1,5
a 3,5), na pandemia. T1: tendência −0,13 p.p./ano (−0,20 a −0,06). T3: sem degrau em 2015 (+0,15; −1,4 a 1,8) nem em
2020 (0,00). Com 15 pontos anuais o EWC tem só 2 g.l.: os IC da série são largos.

**Leitura das hipóteses**

- **H1 (formalização mais difícil): refutada para T2, fraca para T3** — com as mesmas características, negros sem
  carteira passam para o emprego com carteira um pouco **mais** (+0,5 p.p.) que brancos; na perda da carteira resta
  +0,18 p.p. (2,4% da taxa branca).
- **H2 (só composição): quase confirmada** — a desvantagem bruta de −2,8 p.p. em T2 e cerca de 86% da de T3 somem com
  idade, sexo, instrução, UF e ano.
- **H3 (mais sensível ao ciclo): refutada** — sem degrau em T3 em 2015–16 nem em 2020.
- **H4 (atrito seletivo): refutada como fonte de viés** — o atrito difere por raça em 1,6–3,6 p.p., mas o ajuste não muda
  as diferenças.

## 11. Afirmações permitidas

- "De um trimestre para o outro, trabalhadores negros sem carteira conseguem carteira assinada menos vezes que brancos
  (12% × 15%) e perdem a carteira um pouco mais (8,0% × 6,6%); com a mesma idade, sexo, escolaridade e estado, essas
  diferenças quase desaparecem." Ressalva: associação, não discriminação; erro de classificação entre trimestres.

## 12. Afirmações proibidas

- "Empregadores discriminam negros na formalização" (é `C`).

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-20 | Claude Code | criação (seções 1–9 antes de rodar) |
| 2026-10-20 | Claude Code | resultados; desvio: atrito por células em vez de logit |
