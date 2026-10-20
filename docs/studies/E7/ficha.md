# Ficha de pesquisa — `E7` · A escola de cada um: segregação racial entre escolas e infraestrutura (Censo Escolar)

| Campo | Valor |
|---|---|
| ID no plano | `E7` (e partes INEP de `E2`/`E4`) (`docs/PLANO_DE_ANALISE.md`, Bloco E) |
| Onda | 4 (parte 2, fontes do INEP) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
| PR | `onda4/inep-pof` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026).

## 1. Pergunta

Quão separados estudantes brancos e negros estão entre escolas, e as escolas onde estudam estudantes negros têm a mesma
infraestrutura — no país e dentro do mesmo município?

## 2. Tipo

`D`. Descrição administrativa; a segregação resulta de moradia, renda, rede e escolha.

## 3. Estimando

- **Segregação** Branca × Negra (preta + parda) das matrículas da educação básica (`QT_MAT_BAS_*`) entre escolas:
  Duncan D e Theil H, nacional e média dos municípios (ponderada por matrículas); decomposição do H nacional em entre
  municípios e dentro dos municípios. Também público × privado.
- **Exposição à infraestrutura:** para cada indicador da escola (internet para alunos, banda larga, biblioteca ou sala
  de leitura, laboratório de ciências, laboratório de informática, quadra, esgoto pela rede pública), % das matrículas
  brancas e % das negras em escolas que o têm; diferença Branca − Negra bruta e **dentro do município** (média das
  diferenças municipais ponderada pelas matrículas negras).
- **Não declarada:** % das matrículas sem cor/raça, por rede.
- Ano: 2024.

## 4. População

Escolas em atividade com matrícula na educação básica no Censo Escolar 2024.

## 5. Método

Somas ponderadas por matrícula. Sem IC (censo; a incerteza é de declaração e cobertura). Sensibilidade à não
declaração: excluir escolas com > 50% de matrículas sem cor/raça.

## 6. Dados

INEP, Microdados do Censo Escolar 2024 (`microdados_ed_basica_2024.csv`), baixados em 20/10/2026.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Segregação é sobretudo entre lugares** | Componente entre municípios ≥ metade do H nacional |
| H2 | **Escolas de negros têm menos infraestrutura, mesmo no mesmo município** | Diferença Branca − Negra > 0 em ≥ 5 dos 7 indicadores, dentro do município |
| H3 | **A rede pública iguala** | Dentro da rede pública, diferenças dentro do município < 2 p.p. |

## 8. O que refutaria

H1 refutada se o componente entre municípios for < metade. H2 refutada se a diferença dentro do município for ≤ 0 em 3
ou mais indicadores. H3 refutada se alguma diferença dentro do município na rede pública for ≥ 2 p.p.

## 9. Armadilhas

- **Cor/raça não declarada** nas matrículas (alta em algumas redes); se a não declaração se concentra em certas escolas,
  vicia segregação e exposição.
- Uma escola com muitas etapas mistura públicos; a infraestrutura é da escola, não da turma.
- Segregação medida com unidades pequenas tem viés para cima (escolas pequenas).
- Indicadores binários de infraestrutura não medem qualidade nem uso.

## 10. Resultados

Tabela: `e7_escolas_segregacao`. 176.336 escolas em atividade com matrícula de brancos ou negros; 46,9 milhões de
matrículas, 19,0% sem cor/raça declarada (16,5% na pública, 29,0% na privada).

**Segregação Branca × Negra entre escolas (2024)**

| Amostra | Duncan D nacional | Duncan D médio dentro dos municípios | Theil H | % do H entre municípios |
|---|---|---|---|---|
| Todas as escolas | 0,514 | 0,264 | 0,282 | **77,6%** |
| Escolas com ≤ 50% sem cor/raça | 0,515 | 0,258 | 0,282 | 78,3% |
| Rede pública | 0,499 | 0,205 | 0,258 | 88,3% |
| Rede privada | 0,528 | 0,321 | 0,292 | 64,1% |

**Exposição à infraestrutura** (% das matrículas em escolas com o item; diferença Branca − Negra em p.p.)

| Item | Brancos | Negros | Bruta | Dentro do município | Dentro do município, só rede pública | Dentro do município, só privada |
|---|---|---|---|---|---|---|
| Internet para alunos | 65,8 | 54,4 | 11,4 | 1,7 | −0,3 | 7,5 |
| Banda larga | 91,9 | 90,3 | 1,6 | 0,5 | 0,1 | 1,3 |
| Biblioteca ou sala de leitura | 78,0 | 72,6 | 5,4 | 1,8 | −0,1 | 5,8 |
| Laboratório de ciências | 31,8 | 23,3 | 8,5 | **4,8** | 0,5 | 11,3 |
| Laboratório de informática | 56,6 | 46,5 | 10,0 | 0,4 | 0,1 | 4,0 |
| Quadra de esportes | 69,9 | 59,0 | 10,8 | 2,1 | −0,6 | **14,1** |
| Esgoto pela rede pública | 81,8 | 63,8 | **18,0** | 2,5 | 0,8 | 0,9 |

A sensibilidade sem escolas com mais de 50% de matrículas sem cor/raça muda pouco (≤ 0,4 p.p.).

**Leitura das hipóteses**

- **H1 (segregação sobretudo entre lugares):** **confirmada** — 78% do Theil H está entre municípios. Dentro do município
  o Duncan cai de 0,51 para 0,26.
- **H2 (escolas de negros têm menos infraestrutura no mesmo município):** **confirmada pelo critério** (diferença > 0
  nos 7 itens), mas pequena (0,4 a 4,8 p.p.): a maior parte da diferença bruta (até 18 p.p. em esgoto) é de lugar.
- **H3 (a rede pública iguala):** **confirmada** — dentro do município, na rede pública, todas as diferenças ficam abaixo
  de 1 p.p. A diferença dentro do município vem da rede **privada** (quadra +14 p.p., laboratório de ciências +11):
  alunos negros na privada estão em escolas privadas mais simples.

## 11. Afirmações permitidas

- "Metade das matrículas de alunos negros teria de mudar de escola para que brancos e negros se distribuíssem igual
  entre as escolas do país; dentro de cada município, um quarto."
- "Na rede pública, alunos brancos e negros do mesmo município estudam em escolas com a mesma infraestrutura; a
  diferença nacional vem de onde moram."

## 12. Afirmações proibidas

- "Escolas de alunos negros são piores" sem separar lugar e rede.
- Tratar os indicadores de infraestrutura como medida de qualidade do ensino.
