# Ficha de pesquisa — `D6` · Idade: o hiato cresce ao longo da vida?

| Campo | Valor |
|---|---|
| ID no plano | `D6.1`, `D6.2` (coortes: B4) (`docs/PLANO_DE_ANALISE.md`, Bloco D) |
| Onda | 3 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-14 / 2026-10-14 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
| PR | `onda3/d` |

> Seções 1–9 escritas **antes** de rodar (14/10/2026).

## 1. Pergunta

No corte transversal, o hiato racial (bruto e condicional à instrução, sexo e território) é maior entre os mais velhos?
Quanto disso é idade (acúmulo de desvantagem) e quanto é coorte (gerações mais novas com hiato menor, B4)?

## 2. Tipo

`D`/`C`. Em um só corte, idade e coorte são o mesmo eixo; a separação vem do B4 (mesma idade, coortes diferentes) e
fica limitada pela identificação APC (Deaton-Paxson, a confirmar).

## 3. Estimando

- Perfil idade-renda (média de ln renda) por raça, faixas de 5 anos de 18–19 até 65+, nas duas janelas (D6.1).
- Hiato Branca − Negra por faixa etária: bruto e condicional (sexo, instrução, território), IC 95% (D6.2).
- Diferença do hiato condicional 50–59 − 25–29 em cada janela, e a comparação "mesma faixa, janelas diferentes"
  (coorte + período) como ponte para o B4.

## 4. População

P1, Branca × Negra (Indígena com ressalva). Renda `VD4016` real em log.

## 5. Método

WLS por domínio (faixa etária) com `bloco_d.Sistema`; influência linearizada por Estrato/UPA; FDR entre faixas de uma
janela.

## 6. Dados

PNAD Contínua trimestral v2 (`V2009` e variáveis do D1).

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Acúmulo de desvantagem ao longo da vida** | Hiato condicional 50–59 > 25–29 (IC da diferença exclui zero) nas duas janelas |
| H2 | **Coorte, não idade:** o perfil por idade reflete gerações | O hiato da mesma faixa cai entre 2012 e 2025–26 sobretudo nas faixas jovens (coerente com o B4) |

## 8. O que refutaria

H1 refutada se a diferença 50–59 − 25–29 tiver IC incluindo zero em alguma janela. H2 refutada se a queda entre
janelas for igual em todas as faixas (efeito de período, não de coorte).

## 9. Armadilhas

- Idade × coorte × período (APC): nenhum corte separa os três sem restrição.
- Seleção por idade: aposentadoria precoce e saída de P1 diferem por raça (S0/S1).
- Mortalidade diferencial nas idades altas (65+ com n e seleção próprios).

## 10. Resultados

Tabela: `d6_hiato_idade`. Branca × Negra, lp; condicional = sexo, instrução, território.

| Faixa | Condicional 2012 | Condicional 2025T3–2026T2 | Bruto 2025–26 |
|---|---|---|---|
| 18–24 | 0,069 | **0,034 (0,020–0,048)** | 0,186 |
| 25–29 | 0,111 | 0,100 (0,083–0,117) | 0,331 |
| 30–34 | 0,127 | 0,146 | 0,435 |
| 35–39 | 0,155 | 0,151 | 0,464 |
| 40–44 | 0,142 | 0,150 | 0,474 |
| 45–49 | 0,153 | 0,158 | 0,484 |
| 50–54 | 0,161 | 0,159 | 0,475 |
| 55–59 | 0,180 | 0,152 | 0,451 |
| 60–64 | 0,176 | 0,147 | 0,501 |
| 65+ | 0,245 | 0,208 | 0,655 |
| **50–59 − 25–29** | **0,058 (0,039–0,077)** | **0,056 (0,034–0,077)** | 0,134 |

**Leitura das hipóteses**

- **H1 (acúmulo ao longo da vida):** **confirmada** nas duas janelas: o hiato condicional sobe de ~0,03–0,10 antes dos
  30 anos para ~0,15–0,16 a partir dos 35 e fica estável até os 64.
- **H2 (coorte, não idade):** **não refutada, mas o padrão é misto:** a queda entre janelas aparece nas faixas
  extremas (18–24: −0,035; 55–64: −0,03) e não nas intermediárias (30–54 estáveis ou maiores). Não é o padrão "só os
  jovens melhoram" de um efeito de coorte puro; com dois cortes não se separa idade, coorte e período (ver B4).

## 11. Afirmações permitidas

- "Com a mesma instrução, sexo e lugar, o hiato entre jovens de 18 a 24 anos é pequeno (≈ 3%) e chega a ≈ 15% a partir
  dos 35 anos."

## 12. Afirmações proibidas

- "A desigualdade racial vai acabar quando os jovens de hoje envelhecerem" (o perfil por idade é corte transversal;
  B4/B6).
- "A desvantagem cresce com a idade para cada pessoa" (não há painel longo).
