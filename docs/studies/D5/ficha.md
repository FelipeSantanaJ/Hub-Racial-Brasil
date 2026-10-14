# Ficha de pesquisa — `D5` · Posição na ocupação e informalidade: onde cada grupo trabalha, com a mesma instrução

| Campo | Valor |
|---|---|
| ID no plano | `D5.3` (`D5.1` e `D5.2`: contribuições no D1 e S1.4; `D5.4` só literatura) (`docs/PLANO_DE_ANALISE.md`, Bloco D) |
| Onda | 3 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-14 / 2026-10-14 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
| PR | `onda3/d` |

> Seções 1–9 escritas **antes** de rodar (14/10/2026).

## 1. Pergunta

Com a mesma instrução, idade, sexo e lugar, pessoas negras têm probabilidade diferente de estar em cada posição na
ocupação (com carteira, sem carteira, doméstico, setor público, empregador, conta própria) e de contribuir para a
previdência?

## 2. Tipo

`C`. Probabilidades condicionais; a posição é desfecho do mercado de trabalho e de escolhas condicionadas (D5.4 é
`M`: o Hub não separa discriminação na contratação formal de preferências ou restrições).

## 3. Estimando

- Para cada posição k (agrupando `VD4009`: 01 empregado privado com carteira; 02 sem carteira; 03–04 doméstico;
  05–07 setor público, inclusive militar/estatutário; 08 empregador; 09 conta própria) e para "contribui para a
  previdência" (`VD4012` = 1): diferença Negra − Branca em p.p., bruta e condicional (MQO linear com idade em faixas,
  sexo, instrução, território), em P1. Indígena − Branca ao lado.
- Também condicional **dentro de cada nível de instrução** para "com carteira" e "contribui" (o hiato de formalidade é
  maior entre os menos instruídos?).
- **Períodos:** janelas 2012 e 2025T3–2026T2; mudança entre janelas.

## 4. População

P1 (ocupados 18+ com renda > 0). Trabalhador familiar auxiliar (`VD4009` 10) não tem renda: fica fora de P1.

## 5. Método

- **Estimador:** modelo de probabilidade linear por posição (as 6 equações com os mesmos regressores somam 100%);
  `bloco_d.Sistema`.
- **Incerteza:** influência linearizada por Estrato/UPA.
- **FDR:** família = as 7 diferenças condicionais (6 posições + previdência) de uma raça × janela.

## 6. Dados

PNAD Contínua trimestral v2: `VD4009`, `VD4012`, demais variáveis do D1.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Barreira ao emprego formal privado:** com a mesma instrução, negros têm menos carteira e mais conta própria/sem carteira | Diferença condicional em "com carteira" < 0 e em "sem carteira" + "conta própria" > 0 |
| H2 | **Setor público como canal de entrada** (concurso impessoal; cotas desde 2014) | Diferença condicional em "setor público" ≥ 0 na janela recente |
| H3 | **Composição explica a informalidade:** sem diferença depois dos controles | Diferenças condicionais com IC incluindo zero |

## 8. O que refutaria

- H1 refutada se a diferença condicional em "com carteira" tiver IC incluindo zero ou positivo.
- H2 refutada se a diferença condicional em "setor público" for negativa com IC excluindo zero.
- H3 é a alternativa de H1: refutada se H1 for confirmada.

## 9. Armadilhas

- **Escolha × restrição:** conta própria pode ser preferência ou falta de alternativa; o Hub não separa.
- **Previdência** (`VD4012`) mistura formalização e contribuição voluntária (MEI).
- Mudanças legais (reforma trabalhista 2017, MEI) mudam o significado das categorias no tempo.
- LPM pode dar probabilidade fora de [0, 1] para perfis raros; só os efeitos médios são reportados.

## 10. Resultados

Tabela: `d5_posicao_ocupacao`. p.p.; condicional = idade, sexo, instrução, território; IC 95%.

| Posição (2025T3–2026T2) | Branca | Negra | Negra − Branca bruta | condicional | mudança condicional desde 2012 |
|---|---|---|---|---|---|
| Privado com carteira | 39,9% | 38,3% | −1,7 | **+2,3 (1,7–2,8)** | +1,6 (0,9–2,3) |
| Privado sem carteira | 10,9% | 14,3% | +3,4 | −0,2 (−0,5 a 0,1) | −0,6 |
| Doméstico | 3,9% | 6,6% | +2,8 | **+1,3 (1,1–1,5)** | −0,5 |
| Setor público | 13,5% | 12,3% | −1,2 | **+2,0 (1,7–2,3)** | −0,3 (n.s.) |
| Empregador | 5,9% | 2,9% | −3,1 | **−2,4 (−2,6 a −2,2)** | −0,1 (n.s.) |
| Conta própria | 26,0% | 25,7% | −0,3 | **−2,9 (−3,4 a −2,5)** | −0,2 (n.s.) |
| Contribui para a previdência | 74,4% | 62,5% | −11,9 | **−0,6 (−1,1 a −0,2)** | −0,3 (n.s.) |

Indígena − Branca (condicional): com carteira −6,5 (−10,2 a −2,8); previdência −8,0 (−13,1 a −2,9); setor público
+4,4 (1,8–7,1). Por nível (Negra − Branca, condicional): previdência −6,1 (−8,8 a −3,3) entre pessoas sem instrução
e −2,1 no fundamental incompleto; ≈ 0 no superior.

**Leitura das hipóteses**

- **H1 (barreira ao emprego formal privado):** **refutada** para pessoas negras — com a mesma instrução, idade, sexo e
  lugar, elas têm **mais** carteira (+2,3 p.p.) e menos conta própria; o déficit bruto de formalidade (−11,9 p.p. de
  previdência) quase some (−0,6). **Não vale para indígenas:** a barreira à carteira (−6,5) e à previdência (−8,0)
  persiste com os controles.
- **H2 (setor público como canal de entrada):** **confirmada** (+2,0 p.p. condicional; já +2,2 em 2012, antes das cotas
  em concurso de 2014 — a lei de cotas não aparece como mudança).
- **H3 (composição explica a informalidade):** **confirmada** para pessoas negras (a diferença condicional de
  previdência é 5% da bruta), exceto entre os sem instrução.
- **Achado não previsto:** a menor presença como **empregador** é a única diferença de posição que quase não se reduz
  com os controles (−3,1 bruta → −2,4 condicional) e não mudou desde 2012.

## 11. Afirmações permitidas

- "A diferença de informalidade entre pessoas negras e brancas (12 p.p. a menos contribuindo para a previdência) está
  quase toda associada a instrução, idade, sexo e lugar; com essas características iguais, ela cai para menos de 1 p.p."
- "Mesmo com a mesma instrução e o mesmo lugar, pessoas negras são empregadoras 2,4 p.p. menos que pessoas brancas."

## 12. Afirmações proibidas

- "Não há discriminação na contratação formal" — a probabilidade condicional não mede contratação (quem procura,
  quem é recusado).
- "As cotas em concurso aumentaram a presença negra no setor público" (a diferença condicional já existia em 2012).
