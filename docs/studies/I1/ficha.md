# Ficha de pesquisa — `I1` · Censo 2022 × PNAD Contínua: o hiato de renda e a composição racial batem?

| Campo | Valor |
|---|---|
| ID no plano | `I1` (novo, Onda 6 "Integração"; responde também F1 e a parte "indígenas em amostra grande" do mapa de fontes) |
| Onda | 6 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
| PR | `onda6/integracao` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026). Os microdados de acesso público do Censo 2022 (amostra) só
> identificam a UF; município e área de ponderação ficam no acesso controlado.

## 1. Pergunta

Medidos da mesma forma, o hiato de renda do trabalho Branca × Negra (e × Indígena) e a composição racial dos adultos
no Censo 2022 coincidem com os da PNAD Contínua do 3º trimestre de 2022 — no Brasil e por UF?

## 2. Tipo

`D` (validação externa da fonte principal do Hub). **Não permite concluir** qual das duas fontes está "certa": são
instrumentos diferentes (questionário, informante, período de referência, peso).

## 3. Estimando

- **Composição:** % de pessoas de 18+ que se declaram Branca, Preta, Parda, Indígena — Censo × PNADC 2022T3.
- **Hiato de renda:** entre ocupados de 18+ com rendimento habitual de **todos os trabalhos** > 0 (Censo: P1080;
  PNADC: VD4019, o mesmo conceito — o Censo não separa o trabalho principal): (a) razão das médias Branca ÷ Negra − 1
  (%); (b) diferença das médias de ln renda (lp); também Branca × Indígena, Preta e Parda. Brasil e 27 UFs.
- **Concordância:** diferença Censo − PNADC em cada medida, Brasil e UF; correlação entre UFs dos hiatos das duas
  fontes.

## 4. População

Pessoas de 18+ em domicílios particulares (Censo: espécie 01/05; PNADC: domicílios particulares); ocupados com renda
> 0 para o hiato. Ignorado sempre fora. **Sensibilidade:** renda até o P99,9 de cada fonte (valores extremos do Censo
sem a crítica da PNADC); Censo só com rendimento não imputado (se houver marca de imputação na P1080).

## 5. Método

- **Censo:** médias ponderadas por P0110 (peso público). EP **aproximado** por linearização com o domicílio (P0100)
  como conglomerado e a UF como estrato — o desenho real (áreas de ponderação, setores) não está no arquivo público;
  com milhões de pessoas o erro amostral é pequeno perto das diferenças de medição.
- **PNADC 2022T3:** linearização Estrato/UPA do Hub (`variancia`).
- **Regra de concordância (pré-registrada):** diferença Brasil no hiato (razão) ≤ 5 p.p. = "concordam"; 5–10 =
  "concordam com ressalva"; > 10 = "discordam" e a ficha investiga a fonte da diferença (renda extrema, composição).
- **Família FDR:** diferenças Censo − PNADC por UF × medida (BH).

## 6. Dados

| Fonte | Variáveis | Período | Arquivo | Acesso |
|---|---|---|---|---|
| IBGE, Censo 2022, microdados da amostra (acesso público) | P0020 (UF), P0100, P0110, P0130, P0180 (idade), P0210 (cor), P0950 (ocupada), P1080 (renda de todos os trabalhos) | jul/2022 | `data/raw/externos/censo_2022/microdados/*.zip` | público (FTP IBGE), baixado em 20/10/2026 |
| PNAD Contínua trimestral | V2010, V2009, VD4002, VD4019, V1028, Estrato, UPA | 2022T3 | `data/raw/pnadc_extraido_v2` | público |

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **As fontes concordam** | diferença no hiato (razão) ≤ 5 p.p. no Brasil; correlação entre UFs ≥ 0,8 |
| H2 | **O Censo capta mais renda no topo** (sem teto de crítica) | hiato maior no Censo, e a diferença some ao cortar no P99,9 |
| H3 | **A PNADC 2022 tem a composição antiga** (pesos calibrados em projeções anteriores ao Censo 2022) | % parda maior e % branca menor no Censo que na PNADC 2022T3 em ≥ 2 p.p. |
| H4 | **Indígenas diferentes** (o Censo 2022 ampliou a captação de indígenas) | % indígena maior no Censo; hiato Branca × Indígena difere > 10 p.p. |

## 8. O que refutaria

H1 é refutada se a diferença Brasil no hiato (razão) for > 10 p.p. ou a correlação entre UFs < 0,6. As demais, pelo
critério de cada uma.

## 9. Armadilhas

- Período: Censo = mês de referência julho/2022; PNADC 2022T3 = jul–set; inflação pequena entre os dois.
- Renda: no Censo é de todos os trabalhos (P1080) e pode ter valores declarados sem crítica; a PNADC também tem
  imputação. O Hub usa VD4016 (trabalho principal) como referência: aqui se usa VD4019 só para comparar com o Censo.
- Quem responde: no Censo, um morador responde por todos com mais frequência (informante proxy).
- Peso do arquivo público do Censo é próprio da versão pública (P0110).
- Composição racial: diferença pode refletir pesos da PNADC (reponderação, F6) e não a autodeclaração.

## 10. Resultados

<Preenchido depois de rodar.>

## 11. Afirmações permitidas

<Depois de rodar.>

## 12. Afirmações proibidas

- "O Censo prova que a PNADC está errada" (ou o contrário).

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-20 | Claude Code | criação (seções 1–9 antes de rodar) |
