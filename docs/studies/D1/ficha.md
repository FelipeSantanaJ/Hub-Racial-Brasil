# Ficha de pesquisa — `D1` · Quanto do hiato está associado a diferenças observáveis? (decomposição)

| Campo | Valor |
|---|---|
| ID no plano | `D1.1`–`D1.4`; contribuições de `D2.1`, `D3.1`, `D3.4`, `D5.1`, `D5.2`; `D8.1` (`docs/PLANO_DE_ANALISE.md`, Bloco D) |
| Onda | 3 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-14 / 2026-10-14 |
| Estado de publicação | **Proposto** |
| PR | `onda3/d` |

> Seções 1–9 escritas **antes** de rodar (14/10/2026). Substitui, como referência do Hub, as tabelas
> `decomposicao_oaxaca_blinder*` e `decomposicao_hiato_ocupacional` (3 especificações, sem região, sexo, horas nem
> vínculo; R5 da auditoria), que continuam publicadas para comparação.

## 1. Pergunta

Quanto do hiato racial de renda do trabalho (Branca × Negra; Branca × Indígena) está associado a diferenças de
idade, sexo, instrução, território, horas, vínculo, ocupação e atividade — cada bloco sem depender da ordem em que
entra —, em que pontos da distribuição, e quão forte teria de ser uma variável omitida para anular a parte que sobra?

## 2. Tipo

`C` (contabilidade). Nenhum bloco é "causa" do hiato: instrução, ocupação, vínculo e horas são em parte **resultado**
das mesmas desigualdades (mediadores; D3.4). A parte que sobra é a **parte do hiato não associada às covariáveis
incluídas** — nunca "discriminação" (regra R5; D8.3).

## 3. Estimando

- **Hiato bruto:** diferença de médias de ln(renda) Branca − grupo (log-pontos; 0,40 lp ≈ 49%).
- **D1.1 — especificações aninhadas** (coeficiente da raça em ln renda, WLS, Branca = referência; Amarela fora):
  E0 nada → E1 + idade (faixas de 5 anos) → E2 + sexo → E3 + instrução (`VD3004`) → E4 + território (UF, urbano
  `V1022`, tipo de área `V1023`) → E5 + horas (ln das horas habituais do trabalho principal, `V4039`) → E6 + vínculo
  (posição `VD4009` e contribuição à previdência `VD4012`) → E7 + ocupação (grupamento `VD4011`) → E8 + atividade
  (grupamento `VD4010`). "Parte associada" em E_k = hiato bruto − coeficiente em E_k.
- **D1.2 — contribuição de cada bloco sem depender da ordem:** (a) **Gelbach (2016)** *(a confirmar)*: a queda do
  coeficiente de E0 para E8 repartida em Σ_k Γ_k β_k (identidade exata); (b) **Shapley-Shorrocks** sobre os 8 blocos
  (256 regressões), como checagem.
- **OB de dois termos (Reimers, pesos ½–½)** na especificação completa, por comparação com as tabelas antigas.
- **D1.3 — quantis:** RIF-OB (Firpo-Fortin-Lemieux, 2009 *(a confirmar)*) em P10, P25, P50, P75, P90 de ln renda,
  Reimers, especificação completa; banda do kernel × 0,5, × 1 e × 2 (R4: heaping).
- **D1.4 / D8.1 — sensibilidade a omitidas:** (a) Oster (2019) *(a confirmar)*: β* com δ = 1 e R²max = min(1,3 R̃, 1)
  (fórmula aproximada) e o δ que zeraria o coeficiente; (b) Cinelli-Hazlett (2020) *(a confirmar)*: valor de robustez
  RV (q = 1) e limites para uma omitida "k vezes tão forte quanto" instrução e quanto território (k = 1, 2, 3).
- **Lado do Bloco T (P4):** a diferença de Pr(estar em P1) entre adultos 18+ Brancos e Negros repartida por Gelbach com
  os blocos que existem para quem não trabalha (idade, sexo, instrução, território). A renda de quem está em P1 é a
  margem intensiva (acima); esta é a extensiva.
- **Períodos:** janelas 2012 (4 trimestres) e 2025T3–2026T2 (4 trimestres); série anual com os 2º trimestres de 2012
  a 2026 para E0–E8 e Gelbach.

## 4. População

- **Universo:** P1 = ocupados 18+ com renda habitual do trabalho principal > 0 (`populacao.REFERENCIA`); Branca, Negra
  (Preta + Parda), Indígena. Observações com covariável faltante (horas) ficam fora; o número é reportado.
- **Renda:** `VD4016` real (deflator habitual do IBGE), em log.
- **Lado P4:** pessoas 18+ (Branca, Negra, Indígena); desfecho = estar em P1 (0/1).
- **Sensibilidade:** Branca × Indígena (amostra pequena; IC largos).

## 5. Método

- **Estimador:** WLS (`V1028`). Todas as regressões de uma janela saem de uma única matriz X'WX (as aninhadas, Gelbach
  e Shapley são sub-blocos dela).
- **Incerteza:** função de influência de cada coeficiente (e das contribuições de Gelbach, incluindo a incerteza de
  β), linearizada por Estrato/UPA. Shapley: a influência é a combinação linear das 256 influências. RIF-OB:
  bootstrap de Rao-Wu (100 réplicas, banda × 1); as outras bandas sem IC.
- **FDR:** não há bateria de testes de "zero": as contribuições são estimativas com IC. A comparação entre o maior e o
  segundo maior bloco (H1) é um teste único, declarado aqui.
- **EMD:** não se aplica (não há afirmação de "não há diferença", salvo H4, que usa o IC da mudança).
- **Supressão:** Indígena com n e CV reportados; não publica componente com CV > 30%.

## 6. Dados

PNAD Contínua trimestral v2 (`data/raw/pnadc_extraido_v2`): `V2009`, `V2007`, `V2010`, `VD3004`, `UF`, `V1022`,
`V1023`, `V4039`, `VD4009`, `VD4012`, `VD4011`, `VD4010`, `VD4016`, `V1028`, `UPA`, `Estrato`; deflator do IBGE.

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Capital humano:** a instrução é o maior bloco associado ao hiato | Contribuição de Gelbach de instrução maior que a de qualquer outro bloco, com IC da diferença para o segundo excluindo zero |
| H2 | **Alocação no mercado (segregação):** onde se trabalha pesa tanto quanto a instrução | Vínculo + ocupação + atividade somados ≥ instrução (Gelbach) |
| H3 | **Composição territorial:** parte relevante do hiato nacional é morar em regiões mais pobres | Território ≥ 15% do hiato bruto |
| H4 | **A queda do hiato veio das características, não do "resíduo":** o degrau de 2022 (B1) foi de composição (instrução) | Entre 2012 e 2025–26, a parte associada a instrução cai e o coeficiente em E8 não muda (IC da mudança inclui zero) |
| H5a | **Teto de vidro:** a parte não associada cresce no topo | Parte não associada (RIF-OB) em P90 > P50 > P10 |
| H5b | **Piso pegajoso:** a parte não associada é maior na base | P10 > P50 |
| H6 | **A parte não associada é frágil a omitidas** | Oster δ < 1 (uma omitida tão forte quanto as observadas zeraria o coeficiente) ou RV < força de "1× instrução" |

## 8. O que refutaria

- **H1** refutada se outro bloco tiver contribuição maior que a instrução, ou se o IC da diferença entre instrução e o
  segundo maior incluir zero (então "não distinguível").
- **H3** refutada se território < 15% do hiato bruto na janela recente.
- **H4** refutada se o coeficiente em E8 cair entre as janelas com IC da mudança excluindo zero.
- **H5a/H5b**: decide-se pela ordem das estimativas pontuais em P10/P50/P90 com IC (bootstrap) que não se sobrepõem;
  se se sobrepõem, "não distinguível" e nenhuma das duas é afirmada. Precisa ser estável nas três bandas.
- **H6** confirmada (fragilidade) se Oster δ < 1 ou se o limite com "1× instrução" levar o coeficiente a zero.

## 9. Armadilhas

- **Mediação (D3.4):** ocupação, vínculo, horas e atividade são em parte efeito de discriminação e de desigualdade
  anterior; "explicar" por elas não é absolver o mercado. Por isso a ordem E0→E8 vai do mais "pré-mercado" ao mais
  "dentro do mercado", e Gelbach/Shapley são reportados ao lado.
- **Escala:** decomposições em log-pontos; não converter parcelas em % do hiato em R$.
- **Categoria de referência:** a divisão da parte não associada entre covariáveis depende da categoria omitida
  (Oaxaca-Ransom) — por isso só o total da parte não associada é reportado, nunca "efeito do retorno da instrução".
- **RIF e heaping:** rendas redondas viram massas de probabilidade; a densidade no quantil depende da banda (R4). A
  conclusão de quantil só vale se estável nas três bandas.
- **Oster/Cinelli-Hazlett** são para inferir robustez do coeficiente; não dão a "parte da discriminação".
- **Quebras:** 2020–21 (pandemia, coleta por telefone) fora das janelas; 4T2015 (questionário de educação) não afeta
  `VD3004` de forma conhecida (a confirmar).
- **Reclassificação racial** (B2): as janelas comparam composições raciais diferentes; o B2 mostrou efeito pequeno na
  média.
