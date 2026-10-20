# Ficha de pesquisa — `I1` · Censo 2022 × PNAD Contínua: o hiato de renda e a composição racial batem?

| Campo | Valor |
|---|---|
| ID no plano | `I1` (novo, Onda 6 "Integração"; responde também F1 e a parte "indígenas em amostra grande" do mapa de fontes) |
| Onda | 6 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 20/10/2026) |
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

Tabela: `i1_censo_pnadc` (`src/processing/bloco_integracao.py`, `--so i1`). Censo: 21,5 milhões de pessoas na amostra
pública; pesos somam 203,08 milhões (oficial: 203,1 mi).

**Desvio do registro prévio (declarado):** o arquivo público do Censo traz a idade só em faixas de 5 anos (P0180 é
categoria: 15–19, 20–24…); "18+" não é recortável. As duas fontes passaram para **20+**. Uma primeira rodada tratou
P0180 como idade em anos (erro de leitura do layout, meu) e gerou uma composição impossível (18% brancos, 18%
indígenas); foi descartada antes de qualquer interpretação.

| Brasil, 20+ | Censo 2022 | PNADC 2022T3 | Censo − PNADC (IC 95%) |
|---|---|---|---|
| % Branca | 44,1 | 43,9 | +0,2 (−0,2 a 0,6) |
| % Negra (preta + parda) | 54,9 | 54,8 | +0,1 (−0,3 a 0,5) |
| % Indígena | 0,48 | 0,43 | +0,05 (0,01 a 0,09) |
| Renda média de todos os trabalhos — Branca | R$ 3.751 | R$ 3.559 | +R$ 192 |
| — Negra | R$ 2.211 | R$ 2.139 | +R$ 71 |
| — Indígena | R$ 1.730 | R$ 2.543 (n = 958) | −R$ 813 |
| **Hiato Branca × Negra (razão − 1)** | **69,7%** | **66,4%** | **+3,3 p.p. (−1,2 a 7,9)** |
| Hiato Branca × Negra (ln) | 0,424 | 0,432 | −0,008 (−0,025 a 0,008) |
| Hiato Branca × Preta / × Parda | 78,5% / 67,5% | 69,2% / 65,6% | +9,3 / +1,8 |
| **Hiato Branca × Indígena (razão − 1)** | **116,8%** | **40,0%** | **+76,9 p.p. (43 a 111)** |

Renda até o P99,9: hiato Branca × Negra 64,8% (Censo) × 64,0% (PNADC), diferença +0,8. Só renda não imputada no
Censo: 70,2%. **Correlação entre as 27 UFs** do hiato Branca × Negra: **0,59** (Branca × Indígena: 0,49); nas UFs a
PNADC tem IC largos (amostra estadual pequena).

**Leitura das hipóteses**

- **H1 (as fontes concordam): confirmada no Brasil, refutada nas UFs** — diferença nacional de 3,3 p.p. (≤ 5:
  "concordam"), mas a correlação entre UFs (0,59) fica abaixo do limiar pré-registrado de 0,6. Leitura: o hiato
  nacional da PNADC é validado pelo Censo; hiatos por UF da PNADC num único trimestre não devem ser lidos isoladamente.
- **H2 (Censo capta mais o topo): compatível** — a diferença cai de 3,3 para 0,8 p.p. ao cortar no P99,9.
- **H3 (composição antiga na PNADC): refutada** — composição igual em ±0,2 p.p. (os pesos do extrato v2 já estão
  calibrados após o Censo).
- **H4 (indígenas diferentes): confirmada** — o Censo mostra um hiato Branca × Indígena de 117%, quase o triplo do da
  PNADC (40%, com 958 indígenas na amostra). Os números indígenas de renda da PNADC são frágeis.

## 11. Afirmações permitidas

- "O Censo 2022 confirma o hiato de renda medido pela PNAD Contínua: pessoas brancas ganham cerca de 70% a mais que
  pessoas negras no trabalho (Censo: 69,7%; PNADC: 66,4%, julho–setembro de 2022)."
- "Para indígenas, o Censo 2022 mostra uma diferença muito maior que a PNADC: pessoas brancas ganham mais que o dobro
  (+117%) do que indígenas ganham; a PNADC, com amostra pequena de indígenas, subestima essa diferença."

## 12. Afirmações proibidas

- "O Censo prova que a PNADC está errada" (ou o contrário).
- Citar o hiato Branca × Indígena da PNADC sem a comparação com o Censo 2022.
- Comparar hiatos por UF da PNADC de um único trimestre como se fossem precisos.

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-20 | Claude Code | criação (seções 1–9 antes de rodar) |
| 2026-10-20 | Claude Code | resultados; desvio: 18+ → 20+ (idade em faixas no Censo público) |
