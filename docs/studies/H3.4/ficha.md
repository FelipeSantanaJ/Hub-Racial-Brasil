# Ficha de pesquisa — `H3.4` · Riqueza imobiliária por raça (proxy pela POF), com intervalo

| Campo | Valor |
|---|---|
| ID no plano | `H3.4` (`docs/PLANO_DE_ANALISE.md`, Bloco H) |
| Onda | 6 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
| PR | `onda6/integracao` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026). O plano assume o limite: com dado público só há **proxy** de
> riqueza. Esta ficha mede o maior componente da riqueza das famílias brasileiras que a POF permite ver — a casa
> própria — e não a riqueza total.

## 1. Pergunta

Quanto vale, em média, o patrimônio imobiliário (a moradia própria) das pessoas brancas, negras e indígenas, qual é a
razão entre os grupos, e quanto dela persiste com a mesma renda e o mesmo lugar?

## 2. Tipo

`D/C`. **Não permite concluir** a lacuna de riqueza total (faltam ativos financeiros, outros imóveis, empresas,
dívidas) nem por que ela existe.

## 3. Estimando

- **Valor da moradia própria** da unidade de consumo (UC) = aluguel estimado mensal declarado pelo morador
  (`ALUGUEL_ESTIMADO`, V8000 deflacionado para 15/01/2018, `V8000_DEFLA`) × 12 ÷ taxa bruta de rentabilidade do
  aluguel (*cap rate*). UC sem moradia própria = 0.
- **Por pessoa:** valor da UC ÷ número de moradores da UC, atribuído a cada morador (a pessoa herda a riqueza
  domiciliar per capita), por raça da pessoa (V0405).
- **Medidas:** média e mediana; % com moradia própria quitada; razão das médias Branca ÷ Negra (e ÷ Indígena);
  diferença Negra − Branca no mesmo décimo de renda disponível per capita, UF e situação (como no H3.2), em R$ e em %
  da média Branca.
- **Intervalo:** (i) IC 95% design-based; (ii) *cap rate* uniforme de 4%, 5% e 6% ao ano (muda o nível, não a
  razão); (iii) *cap rate* variando com o valor (6% no décimo inferior de aluguel estimado → 4% no superior, linear),
  porque imóveis baratos rendem mais — muda a razão. O "intervalo da lacuna" = envelope de (i)–(iii).

## 4. População

Moradores da POF 2017–2018, Branca, Negra (preta + parda), Indígena. **Principal:** moradia própria já paga
(condição de ocupação do domicílio, V0217); **sensibilidade:** incluindo "própria, ainda pagando" (valor sem
descontar a dívida — superestima).

## 5. Método

- Médias e razões com influência linearizada por estrato/UPA (`variancia.influencia_media`, como no H3.2); razão de
  médias pelo método delta. Mediana por quantil ponderado (sem EP; descrita).
- Condicional: MQO com décimo de renda, UF e situação (`bloco_d.Sistema`, `_coefs` do H3.2).
- **Família FDR:** {Negra, Indígena} × {bruta, condicional} × medidas (BH).

## 6. Dados

| Fonte | Variáveis | Período | Arquivo | Acesso |
|---|---|---|---|---|
| IBGE, POF 2017–2018 | `ALUGUEL_ESTIMADO` (V9001, V8000_DEFLA, fator de anualização), `DOMICILIO` (V0217), `MORADOR` (V0405, PESO_FINAL, RENDA_DISP_PC) | 2017–18 | `data/raw/externos/pof_2017_18/Dados_20230713.zip` | público; baixado em 20/10/2026 (Onda 4) |

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **A lacuna de riqueza é maior que a de renda** | razão das médias de riqueza imobiliária Branca ÷ Negra maior que a razão das rendas disponíveis per capita (POF) |
| H2 | **Com a mesma renda, some** | diferença condicional (mesmo décimo, UF, situação) com IC contendo zero |
| H3 | **Casa própria é comum, valor não** | % com casa própria parecido entre grupos (H3 da PNADC), mas valor médio bem menor para negros |

## 8. O que refutaria

H1 é refutada se a razão de riqueza for menor ou igual à de renda em todo o envelope do intervalo. H2, se a diferença
condicional excluir zero.

## 9. Armadilhas

- **Aluguel estimado é declarado pelo morador** (pergunta: "quanto pagaria de aluguel"), sujeito a erro e a viés de
  quem mora em áreas sem mercado de aluguel (rural, periferias).
- *Cap rate* desconhecido e heterogêneo → intervalo, não ponto.
- Riqueza domiciliar atribuída por pessoa supõe partilha igual no domicílio.
- POF 2017–18 é antiga (a POF 2024–25 ainda não saiu, *a confirmar*); não há série.
- Não inclui outros imóveis, terra, veículos, aplicações, empresas, dívidas (financiamento imobiliário).

## 10. Resultados

<Preenchido depois de rodar.>

## 11. Afirmações permitidas

<Depois de rodar.>

## 12. Afirmações proibidas

- "A lacuna de riqueza racial no Brasil é de X" (o Hub mede só a moradia própria, por proxy).
- Citar números de riqueza total de estudos externos sem conferi-los (*a confirmar*).

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-20 | Claude Code | criação (seções 1–9 antes de rodar) |
