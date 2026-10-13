# Ficha de pesquisa — `B6` · Projeção condicional: se o ritmo for X, a paridade chega quando?

| Campo | Valor |
|---|---|
| ID no plano | `B6` (`docs/PLANO_DE_ANALISE.md`, Bloco B) |
| Onda | 2 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (proposto) |
| PR | `onda2/b-c` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

Sob premissas explícitas sobre o ritmo de queda do hiato, em que ano o hiato Branca × Negra chegaria a zero — e
quão incerta é essa conta?

## 2. Tipo

`D` (aritmética condicional). **Não é previsão.** A resposta é sempre "se o ritmo for X, então Y", com X na tela.

## 3. Estimando

Ano de paridade = último ano + hiato atual / |ritmo|, para três premissas de ritmo:

| Premissa | Ritmo |
|---|---|
| P-a | Inclinação linear 2012–2026 (B1, p.p./ano), com o IC EWC |
| P-b | Inclinação linear 2022–2026 (pós-pandemia) |
| P-c | Queda **proporcional** constante (inclinação em log do hiato %, B1): o hiato nunca chega a zero; reporta-se o ano em que cai à metade |

Se o IC do ritmo inclui zero ou ritmo ≥ 0, o ano de paridade é **"sem data finita"**. Séries: P1 (B×N), P4 (B×N) e
renda domiciliar per capita (T1).

## 4. População

A das séries do B1.

## 5. Método

- Ano central e intervalo: obtidos invertendo os extremos do IC do ritmo (IC EWC do B1).
- Nenhuma incerteza do nível futuro, da composição ou de choques é modelada: a faixa é **só** a incerteza do ritmo
  passado, condicional a ele continuar.

## 6. Dados

Saída do B1 (`b1_tendencia_hiato`).

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê |
|---|---|---|
| H1 | O ritmo de 2012–26 dá uma data finita mas distante (OLS ingênuo: ~84 anos) | Ano de paridade P-a depois de 2080 |
| H2 | O ritmo não é distinguível de zero | "Sem data finita" em P-a |

## 8. O que refutaria

Não há refutação empírica de uma projeção condicional; o critério de publicação é: se o IC do ritmo inclui zero, não
se publica ano nenhum, só "sem data finita".

## 9. Armadilhas

- Extrapolação linear de 14 anos para 50+ anos.
- Ritmo em p.p. (linear) e em % (proporcional) dão respostas qualitativamente diferentes (a proporcional nunca zera).
- Mudança de composição racial (B2) pode mexer no hiato sem mudar a renda de ninguém.

## 10. Resultados

`b6_projecao_condicional.parquet`. Ano em que o hiato chegaria a zero **se** o ritmo indicado continuar (intervalo
pelos extremos do IC 95% do ritmo; "sem data" quando o IC alcança zero):

| Série (hiato atual) | Premissa | Ritmo | Ano (intervalo) |
|---|---|---|---|
| P1 · Branca × Negra (65,7%) | P-a linear 2012–2026 | −0,78 p.p./ano (−1,25 a −0,32) | **2110** (2079 a 2231) |
| | P-b linear desde 2022 | +0,55 p.p./ano (−0,14 a 1,24) | **sem data finita** |
| | P-c proporcional (meia-vida) | −0,91% ao ano (−1,45 a −0,37) | metade do hiato em 2102 (2074 a 2212) |
| P4 · Branca × Negra (71,8%) | P-a | −0,91 (−1,88 a 0,05) | sem data finita (central 2105) |
| T1 · domiciliar per capita (81,7%) | P-a | −1,24 (−3,13 a 0,66) | sem data finita (central 2091) |

**Leitura.** H1 confirmada só sob a premissa de ritmo de todo o período (data central 2110). H2 confirmada para o
ritmo pós-2022 e para P4 e T1: o ritmo não é distinguível de zero e não há data. Junto com o B1 (a queda foi um degrau,
não uma tendência), **a premissa P-a é a menos defensável das três**.

## 11. Afirmações permitidas

- "Se o hiato continuasse caindo no ritmo médio de 2012 a 2026 (0,8 ponto por ano), chegaria a zero por volta de 2110
  — mas desde 2022 ele não cai, e nesse ritmo não chega." (sempre com as duas premissas)

## 12. Afirmações proibidas

- **"Em 20XX haverá igualdade"** ou qualquer data sem a premissa na mesma frase.
- Usar o ano central sem o intervalo.

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
