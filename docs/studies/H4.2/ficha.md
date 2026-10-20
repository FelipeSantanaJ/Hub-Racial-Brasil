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

<Preenchido depois de rodar.>

## 11. Afirmações permitidas

<Depois de rodar.>

## 12. Afirmações proibidas

- "Empregadores discriminam negros na formalização" (é `C`).

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-20 | Claude Code | criação (seções 1–9 antes de rodar) |
