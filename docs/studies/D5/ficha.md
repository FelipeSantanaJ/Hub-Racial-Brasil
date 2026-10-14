# Ficha de pesquisa — `D5` · Posição na ocupação e informalidade: onde cada grupo trabalha, com a mesma instrução

| Campo | Valor |
|---|---|
| ID no plano | `D5.3` (`D5.1` e `D5.2`: contribuições no D1 e S1.4; `D5.4` só literatura) (`docs/PLANO_DE_ANALISE.md`, Bloco D) |
| Onda | 3 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-14 / 2026-10-14 |
| Estado de publicação | **Proposto** |
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
