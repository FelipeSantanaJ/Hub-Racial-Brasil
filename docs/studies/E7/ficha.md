# Ficha de pesquisa — `E7` · A escola de cada um: segregação racial entre escolas e infraestrutura (Censo Escolar)

| Campo | Valor |
|---|---|
| ID no plano | `E7` (e partes INEP de `E2`/`E4`) (`docs/PLANO_DE_ANALISE.md`, Bloco E) |
| Onda | 4 (parte 2, fontes do INEP) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Proposto** |
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
