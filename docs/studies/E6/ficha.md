# Ficha de pesquisa — `E6` · Ensino superior: quem entra, onde, por cota, e quem conclui (Censo da Educação Superior)

| Campo | Valor |
|---|---|
| ID no plano | `E6` (descritivo; o desenho causal das cotas é o G1, Onda 5) (`docs/PLANO_DE_ANALISE.md`, Bloco E) |
| Onda | 4 (parte 2, fontes do INEP) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Proposto** |
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
