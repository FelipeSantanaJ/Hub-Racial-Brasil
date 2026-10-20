# Ficha de pesquisa — `E6` · Ensino superior: quem entra, onde, por cota, e quem conclui (Censo da Educação Superior)

| Campo | Valor |
|---|---|
| ID no plano | `E6` (descritivo; o desenho causal das cotas é o G1, Onda 5) (`docs/PLANO_DE_ANALISE.md`, Bloco E) |
| Onda | 4 (parte 2, fontes do INEP) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 20/10/2026) |
| PR | `onda4/inep-pof` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026).

## 1. Pergunta

Como a composição racial de ingressantes, matriculados e concluintes da graduação mudou entre 2014 e 2023, por rede
(federal, estadual/municipal, privada), modalidade (presencial, a distância) e área — e qual é o peso da reserva de
vagas étnico-racial no ingresso das federais?

## 2. Tipo

`D`. Contagens administrativas (censo das instituições); sem desenho causal (G1).

## 3. Estimando

- % de pessoas negras (pretas + pardas) e indígenas entre ingressantes, matriculados e concluintes **com cor/raça
  declarada** (excluindo "não declarada"), e a % não declarada, por ano × rede/categoria administrativa × modalidade;
  e por área geral (CINE) e em três cursos de alto retorno (Medicina, Direito, Engenharias — por nome do curso).
- Ingressantes por reserva de vagas (`QT_ING_RESERVA_VAGA`) e por reserva étnica (`QT_ING_RVETNICO`) como % dos
  ingressantes, por categoria administrativa.
- **Razão concluintes ÷ ingressantes** por raça, como fluxo bruto (não é taxa de conclusão de coorte).
- Anos: 2014 e 2023.

## 4. População

Cursos de graduação do Censo da Educação Superior (todos os registros do arquivo de cursos).

## 5. Método

Somas de contagens. **Sem IC**: censo administrativo (erro de cobertura e de declaração não é amostral).

## 6. Dados

INEP, Microdados do Censo da Educação Superior 2014 e 2023 (`MICRODADOS_CADASTRO_CURSOS_*.CSV`), baixados em
20/10/2026. PNADC (E4) para comparar a composição da graduação.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Expansão negra via privada e EAD** | O aumento da % negra entre ingressantes 2014→2023 é maior na privada a distância que na federal presencial |
| H2 | **Federais já mais negras pela reserva** | % negra nos ingressantes federais ≥ % negra na privada presencial em 2023, e reserva étnica ≥ 10% dos ingressantes federais |
| H3 | **Cursos de alto retorno seguem brancos** | % negra em Medicina < % negra no total da graduação em 2023 por mais de 10 p.p. |
| H4 | **Concluir é mais difícil** | Razão concluintes ÷ ingressantes menor para negros que para brancos |

## 8. O que refutaria

Cada hipótese é refutada se a comparação indicada não se verificar (descritivo; sem teste estatístico). H1 também se a
% não declarada mudar tanto entre os anos que inverta a comparação (sensibilidade: atribuir os não declarados na
proporção dos declarados e como todos brancos/todos negros).

## 9. Armadilhas

- **Cor/raça não declarada** é muito alta em 2014 (a medir); comparações no tempo dependem dela.
- Reserva de vagas mistura critérios (escola pública, renda, PPI, PcD); `RVETNICO` é a parcela étnica.
- Matriculados contam a mesma pessoa uma vez por curso; concluintes de 2023 entraram em anos anteriores.
- Nome do curso é texto livre: a classificação de Medicina/Direito/Engenharias é por palavra-chave (a confirmar).

## 10. Resultados

Tabela: `e6_superior_composicao` (`src/processing/bloco_eh_externos.py`). Graduação (`TP_NIVEL_ACADEMICO` = 1). Totais
conferem com os números oficiais (ingressantes 3,11 mi em 2014 e 4,99 mi em 2023; matrículas 7,83 mi e 9,98 mi).
"% negra" = pretos + pardos entre os de cor/raça declarada; entre parênteses, limites com os não declarados todos como
não negros / todos como negros.

| Recorte (ingressantes) | 2014: % não declarada | 2014: % negra | 2023: % não declarada | 2023: % negra | Ingressantes 2023 |
|---|---|---|---|---|---|
| Total | 43,1 | 43,4 (24,7–67,8) | 20,5 | 44,1 (35,0–55,5) | 4,99 mi |
| Federal presencial | 33,2 | 51,2 | 6,9 | **49,9** (46,4–53,4) | 312 mil |
| Federal a distância | 41,5 | 65,7 | 14,9 | 60,9 | 42 mil |
| Estadual presencial | 32,9 | 40,5 | 14,1 | 44,8 | 144 mil |
| Privada presencial | 41,5 | 41,4 | 17,8 | 42,1 | 1,21 mi |
| **Privada a distância** | 53,4 | 44,6 | 23,4 | 43,9 | **3,23 mi** (0,69 mi em 2014) |
| Medicina | 41,0 | 33,9 | 16,6 | **34,9** | 162 mil |
| Direito | 40,3 | 41,0 | 16,7 | 46,7 | 223 mil |
| Engenharias | 38,6 | 39,2 | 19,6 | 43,3 | 324 mil |

Medicina: matriculados 32,5% negros e concluintes 31,6% (total da graduação: 44,8% e 44,4%).

**Reserva de vagas (% dos ingressantes):** federais 24,6% (2014) → **35,6%** (2023), sendo a parcela étnica 11,6% →
**17,9%**; estaduais 23,7% → 13,6% (étnica 7,4% → 4,5%); privadas ≈ 0.

**Razão concluintes ÷ ingressantes (mesmo ano, fluxo bruto):** 2023 — Branca 0,290, Negra 0,297; federais 0,431 ×
0,455; privadas 0,270 × 0,271. Em 2014: 0,329 × 0,243 (com 43% sem cor/raça).

**Leitura das hipóteses**

- **H1 (expansão negra via privada e EAD):** **não confirmada como mudança de composição** — entre os declarados, a % negra
  ficou estável em todas as redes (total 43,4 → 44,1). A expansão foi de **volume**: a privada a distância passou de 0,69
  para 3,23 milhões de ingressantes e hoje recebe 65% de todos os ingressantes, negros e brancos. A comparação no tempo
  é frágil: a não declaração caiu de 43% para 20%.
- **H2 (federais mais negras pela reserva):** **confirmada** — 49,9% de negros entre ingressantes federais presenciais ×
  42,1% na privada presencial; reserva étnica = 17,9% dos ingressos federais.
- **H3 (cursos de alto retorno seguem brancos):** **confirmada para Medicina** em matriculados (−12,3 p.p. em relação ao
  total) e concluintes (−12,8), e **no limite para ingressantes** (−9,2 p.p., abaixo do limiar de 10). Direito e
  Engenharias estão próximos do total.
- **H4 (concluir é mais difícil):** **refutada em 2023** (razões iguais: 0,297 × 0,290); a diferença de 2014 não é
  interpretável com 43% sem cor/raça.

## 11. Afirmações permitidas

- "Metade dos ingressantes das universidades e institutos federais em cursos presenciais é negra (2023); 18% entraram
  pela reserva de vagas étnico-racial."
- "Em Medicina, 32% dos estudantes são negros, contra 45% no conjunto da graduação (2023)."

## 12. Afirmações proibidas

- "As cotas aumentaram a presença negra no ensino superior em X pontos" (descrição; desenho causal é o G1).
- Comparar 2014 e 2023 sem dizer que a cor/raça não declarada caiu de 43% para 20%.
