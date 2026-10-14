# Ficha de pesquisa — `D1` · Quanto do hiato está associado a diferenças observáveis? (decomposição)

| Campo | Valor |
|---|---|
| ID no plano | `D1.1`–`D1.4`; contribuições de `D2.1`, `D3.1`, `D3.4`, `D5.1`, `D5.2`; `D8.1` (`docs/PLANO_DE_ANALISE.md`, Bloco D) |
| Onda | 3 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-14 / 2026-10-14 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
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

## 10. Resultados

Tabelas: `d1_aninhada`, `d1_contribuicao_blocos`, `d1_mudanca_janelas`, `d1_ob_reimers`, `d1_rif_ob`,
`d1_sensibilidade_omitidas`, `d1_extensiva_p1` (`src/processing/bloco_d.py`). Log-pontos (lp) de ln renda; IC 95%.

**Correção feita antes de ler os resultados.** Na primeira rodada, Gelbach e Shapley de vínculo e atividade
explodiram (±2,5 lp, com sinais opostos): a dummy "serviços domésticos" da atividade (`VD4010` = 11) é idêntica a
"doméstico" da posição (`VD4009` 03/04). O coeficiente total não muda, mas a divisão entre os dois blocos fica
indeterminada. `montar_x` passou a retirar toda coluna que é combinação linear das anteriores (na ordem dos blocos);
em todas as amostras só saiu `atividade:11` — o trabalho doméstico fica no bloco vínculo.

**D1.1 — especificações aninhadas, Branca × Negra**

| Especificação | 2012 | 2025T3–2026T2 |
|---|---|---|
| E0 hiato bruto | 0,464 (0,450–0,478) | 0,427 (0,415–0,439) |
| E3 + idade, sexo, instrução | 0,242 | 0,237 |
| E4 + território | 0,133 | 0,133 |
| E6 + horas, vínculo | 0,114 | 0,113 |
| **E8 completa** | **0,101 (0,096–0,106)** | **0,094 (0,089–0,100)** |
| Parte associada às covariáveis (E8) | 78,2% | 77,9% |

Branca × Indígena (n = 4.299 indígenas na janela recente): bruto 0,481 (0,403–0,559) → E8 0,125 (0,077–0,174).

**D1.2 — contribuição de cada bloco (Gelbach; Shapley entre colchetes), Branca × Negra, 2025T3–2026T2**

| Bloco | lp (IC 95%) | % do bruto | Shapley | 2012 (Gelbach) |
|---|---|---|---|---|
| Instrução | 0,089 (0,086–0,093) | 20,9% | [0,090] | 0,129 (27,7%) |
| Território | 0,084 (0,080–0,087) | 19,6% | [0,087] | 0,100 (21,5%) |
| Ocupação (grupamento) | 0,082 (0,078–0,085) | 19,1% | [0,076] | 0,063 (13,6%) |
| Vínculo (posição, previdência) | 0,059 (0,057–0,062) | 13,8% | [0,052] | 0,061 (13,1%) |
| Horas | 0,020 (0,018–0,022) | 4,6% | [0,011] | 0,014 |
| Idade | 0,008 | 1,8% | [0,005] | 0,008 |
| Sexo | −0,008 | −1,9% | [−0,003] | −0,011 |
| Atividade | −0,000 | 0,0% | [0,015] | 0,001 |
| **Parte não associada (E8)** | **0,094** | **22,1%** | | 0,101 |

Gelbach e Shapley dão a mesma ordem; somam exatamente bruto − E8. Indígena, janela recente (Gelbach): território
0,087, vínculo 0,081, instrução 0,079, ocupação 0,066, horas 0,036 (IC de ±0,02 a 0,03).

**Mudança 2012 → 2025T3–2026T2** (EP com a covariância das UPAs comuns às duas janelas): hiato bruto −0,037
(−0,056 a −0,017); contribuição da instrução **−0,039 (−0,046 a −0,032)**; território −0,016 (−0,022 a −0,009);
ocupação **+0,019 (+0,014 a +0,024)**; horas +0,006; vínculo −0,002 (n.s.); **E8 −0,007 (−0,015 a +0,001)**.
Na série anual (2º trimestres), a contribuição da instrução cai de forma contínua (0,130 em 2012 → 0,090 em 2021 e
estável depois), enquanto o hiato bruto fica parado até 2021 (0,46–0,47) e cai em degrau em 2022 (0,446 → 0,423,
como no B1); a E8 oscila entre 0,089 e 0,103 sem tendência.

**D1.4 / D8.1 — sensibilidade a variáveis omitidas** (Branca × Negra, E8; janela recente, 2012 entre parênteses)

| Medida | Valor |
|---|---|
| Oster: δ que zeraria o coeficiente (R²max = 1,3 R̃ = 0,74) | **0,85** (0,82) |
| Oster: δ que zeraria (R²max = 1) | 0,33 (0,34) |
| Cinelli-Hazlett: RV (q = 1) | 7,0% (7,3%) |
| Omitida 1× tão forte quanto instrução → coeficiente | 0,058 (0,046) |
| Omitida 2× instrução | 0,022 (−0,011) |
| Omitida 3× instrução | −0,015 (−0,069) |
| Omitida 1× tão forte quanto território | −0,051 (cruza zero) |

(Coeficiente expresso como hiato Branca − Negra; negativo = o hiato condicional desaparece.)

**Lado P4 — diferença de Pr(estar em P1) entre adultos 18+, Branca − Negra (p.p.), janela recente:** bruta 2,1
(1,7–2,5); com idade e sexo 5,7; + instrução 1,5 (1,2–1,8); + território **−1,1 (−1,4 a −0,8)**. Gelbach: instrução
+3,3, território +3,0, idade −2,7 (pessoas negras são mais jovens, idades de maior ocupação), sexo −0,4. Em 2012:
bruta 2,5; completa −1,1.

**Leitura das hipóteses**

- **H1 (instrução é o maior bloco):** confirmada para Branca × Negra nas duas janelas, mas na recente por margem
  pequena — instrução − território 0,006 (0,001–0,010); instrução − ocupação 0,008 (0,004–0,011). Na prática,
  instrução, território e ocupação pesam quase igual (≈ 20% do hiato cada). Para Branca × Indígena: **não
  distinguível** (instrução − território −0,008; −0,037 a 0,020).
- **H2 (alocação no mercado ≥ instrução):** refutada em 2012 (vínculo + ocupação + atividade − instrução = −0,005;
  −0,009 a −0,000) e **confirmada em 2025–26** (+0,051; 0,047 a 0,055): o peso relativo passou da instrução para a
  ocupação.
- **H3 (território ≥ 15%):** confirmada (19,6%; 21,5% em 2012).
- **H4 (a queda veio das características, não da parte não associada):** confirmada pelo critério pré-registrado (E8
  não muda; a contribuição da instrução cai). Mas a série mostra um descompasso: a convergência educacional foi
  gradual desde 2012 e não reduziu o hiato bruto até 2021; o degrau de 2022 aparece sobretudo em vínculo, ocupação e
  horas (recomposição do mercado depois da pandemia) — leitura descritiva, sem IC ano a ano.
- **H6 (fragilidade a omitidas):** **confirmada** pelo critério fixado: δ de Oster < 1. Uma variável omitida tão
  forte quanto o território eliminaria a parte não associada; uma tão forte quanto a instrução a reduziria de 0,094
  para 0,058. Ou seja: a parte não associada (~9 lp, ~10% de renda) **não é robusta** a omitidas da mesma ordem das
  observadas — nem para concluir que existe, nem que é zero.
- **H5 (teto de vidro × piso pegajoso):** **nenhuma das duas é afirmada** — a ordem entre P90 e P10 da parte não
  associada inverte com a banda do kernel (critério pré-registrado: estável nas três bandas). O que é estável: a parte
  não associada no P90 é maior que na mediana nas duas janelas; na janela recente também no P10 (forma de "U").

**OB de dois termos (Reimers, E8)** — Branca × Negra: parte não associada 0,096 (0,090–0,102) na janela recente e
0,106 (0,100–0,111) em 2012, coerente com o coeficiente da E8 (0,094 e 0,101). Branca × Indígena: 0,148
(0,084–0,212) e 0,098 (0,026–0,169).

**D1.3 — RIF-OB por quantil, Branca × Negra** (lp; banda de Silverman × 0,5 / × 1 / × 2; IC do bootstrap só na
banda × 1)

| Quantil | Hiato bruto | Parte não associada 2025T3–2026T2 | Parte não associada 2012 |
|---|---|---|---|
| P10 | 0,724 (2012: 0,642) | 0,45 / **0,41** / 0,40 | −0,39 / −0,14 / 0,21 (instável) |
| P25 | 0,135 (2012: 0,147) | −0,07 / **−0,05** / −0,02 | −0,05 / −0,04 / −0,04 |
| P50 | 0,376 (2012: 0,333) | 0,11 / **0,14** / 0,11 | −0,03 / 0,01 / 0,03 |
| P75 | 0,496 (2012: 0,511) | 0,37 / **0,30** / 0,22 | 0,28 / 0,24 / 0,16 |
| P90 | 0,669 (2012: 0,671) | 0,51 / **0,44** / 0,34 | 0,28 / 0,29 / 0,24 |

**Ressalva forte (R4):** o P25 dos dois grupos cai no salário mínimo — o hiato bruto ali é pequeno porque o piso legal
comprime a distribuição, não porque haja igualdade. Em massas de probabilidade a densidade estimada depende da banda
e o bootstrap de quantis fica preso aos valores redondos: os IC da banda × 1 (ex.: P90 0,436–0,467) **subestimam** a
incerteza e não devem ser citados sozinhos. A conclusão por quantil é só a que sobrevive às três bandas.

## 11. Afirmações permitidas

- "Entre ocupados com renda, cerca de 78% da diferença de renda (em log) entre pessoas brancas e negras está associada
  a diferenças de instrução, território, ocupação, vínculo e horas (2025–26). Instrução, território e ocupação pesam
  cerca de um quinto cada."
- "Desde 2012, a diferença de instrução passou a responder por menos do hiato (de 28% para 21%) e a de ocupação por
  mais (de 14% para 19%)."
- "Sobra uma parte de cerca de 9 log-pontos (≈ 10% de renda) não associada às covariáveis incluídas. Ela não é
  robusta: uma variável omitida tão associada à raça e à renda quanto o território a eliminaria."
- "Entre todos os adultos, a menor ocupação de pessoas negras (2 p.p.) desaparece — e se inverte — quando se comparam
  pessoas com a mesma idade, sexo, instrução e lugar."

## 12. Afirmações proibidas

- "X% do hiato é discriminação" ou "os 9 log-pontos restantes são discriminação" (R5; D8.3).
- "A educação explica o hiato" no sentido causal; "a ocupação explica" sem dizer que é mediadora (D3.4).
- "A desigualdade racial é maior no topo" (teto de vidro) ou "na base" (piso pegajoso) como resultado do D1.3.
- Citar os IC do RIF-OB sem as três bandas e a ressalva de heaping.
- Comparar o tamanho da parte não associada entre Negra e Indígena (IC do Indígena ≈ ±0,06).
