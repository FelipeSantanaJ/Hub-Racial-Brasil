# Ficha de pesquisa — `G4` · Salário mínimo e hiato racial: UFs mais expostas viram o hiato cair mais quando o mínimo subiu?

| Campo | Valor |
|---|---|
| ID no plano | `G4` (`docs/PLANO_DE_ANALISE.md`, Bloco G) |
| Onda | 5 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Bloqueado** (por poder estatístico; aprovado pelo Felipe em 20/10/2026) |
| PR | `onda5/g` |

> Seções 1–9 escritas **antes** de rodar (20/10/2026). O plano manda apresentar como `C`: a identificação por
> exposição regional é fraca.

## 1. Pergunta

Nos trimestres em que o salário mínimo real subiu, o hiato de renda Branca × Negra caiu mais nas UFs em que, em 2012,
a parcela de trabalhadores negros ganhando até um salário mínimo era maior que a de brancos?

## 2. Tipo

`C` (apresentado como contabilidade/associação), embora o desenho seja de exposição diferencial (*bite*, tipo
Lee 1999; para o Brasil, Engbom & Moser 2022, *AER* *(a confirmar)*). **Não permite concluir** que o mínimo "causou"
a queda do hiato: a variação do mínimo real é nacional e coincide com o ciclo econômico, que também afeta mais as UFs
de renda baixa.

## 3. Estimando

- **Hiato:** `hiato_ut` = média de ln(renda real do trabalho principal) Branca − média Negra, na UF u e trimestre t,
  população P1 (ocupados 18+ com VD4016 > 0), pesos V1028. Em log-pontos.
- **Exposição:** `E_u = s_Negra,u − s_Branca,u`, com `s_g,u` = % dos trabalhadores do grupo g na UF u com VD4016
  nominal ≤ 1,05 × salário mínimo, nos 4 trimestres de 2012.
- **Regressor:** `X_ut = E_u × ln(SM real_ut)`; SM real = SM nominal do mês de referência × deflator habitual da UF
  (`deflator_ibge`). SM nominal: tabela `SALARIO_MINIMO_NOMINAL` do Hub, com 2023 = R$ 1.302 em 2023T1 e R$ 1.320 de
  2023T2 em diante (mudança em maio de 2023; a confirmar contra o microdado).
- **Parâmetro:** β em `hiato_ut = α_u + γ_t + β·X_ut + ε_ut`. **Interpretação pré-registrada:** se o aumento do mínimo
  passasse integralmente para quem ganha até 1 SM e para mais ninguém, a média de ln renda do grupo g subiria s_g·Δln SM
  e o hiato mudaria −E_u·Δln SM, isto é, **β = −1**. β = 0: nenhuma compressão diferencial. β < −1: transbordamento
  para quem ganha um pouco mais que o mínimo.

## 4. População

- Ocupados 18+ com renda habitual do trabalho principal > 0 (P1), Branca e Negra; 27 UFs × 58 trimestres (2012T1–2026T2).
- **Sensibilidade obrigatória:** (a) exposição com limiar de 1,5 SM; (b) sem pesos; (c) 2012–2019 (sem pandemia);
  (d) sem 2020–2021; (e) exposição de 2012T1 só.

## 5. Método

- **Estimador:** MQO com efeitos fixos de UF e de trimestre, ponderado pela população P1 da UF em 2012.
- **Incerteza:** 27 conglomerados (UF) → *wild cluster bootstrap* com pesos de Webb (9.999 reamostragens, hipótese nula
  imposta) para o p-valor e IC por inversão; EP CR1 só para registro. O erro amostral do `hiato_ut` está no resíduo.
- **EMD:** ficha G6. **Efeitos plausíveis:** β entre −1,5 e 0. **Regra:** EMD(β) ≤ 1 → roda; > 1 → não roda.
- **Família de testes (FDR):** β principal e as 5 sensibilidades (6 testes), BH.
- **Regra de amostra:** UF × trimestre com < 100 trabalhadores negros ou brancos na amostra sai (a medir; esperado: só
  algumas UFs pequenas do Norte para brancos).

## 6. Dados

| Fonte | Variáveis | Período | Extrato / arquivo | Acesso |
|---|---|---|---|---|
| PNAD Contínua trimestral | V2010, V2009, VD4016, UF, V1028, Estrato, UPA | 2012T1–2026T2 | `data/raw/pnadc_extraido_v2` | público |
| Deflator IBGE | deflator habitual por UF × trimestre | idem | `data/processed/deflator_ibge.parquet` | público |
| Salário mínimo | valor nominal por ano | 2012–2026 | `agregacoes_pnadc.SALARIO_MINIMO_NOMINAL` | lei (público) |

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Compressão pelo mínimo** | β < 0, próximo de −1 |
| H2 | **Ciclo, não o mínimo** | β ≈ 0 com controle de desocupação da UF × E_u; ou β some sem 2015–2017 |
| H3 | **Informalidade bloqueia o repasse** (quem ganha ≤ 1 SM é muitas vezes informal) | −1 < β < 0 |

## 8. O que refutaria

- H1 é refutada se o IC 95% de β contiver 0 **e** excluir −1 (detectaria repasse total, e não o vê).
- Se o IC contiver 0 e −1 ao mesmo tempo, o resultado é "inconclusivo" — não "sem efeito".

## 9. Armadilhas

- **Identificação fraca:** uma série nacional do mínimo × exposição fixa; tendências próprias de UFs pobres
  (Nordeste) confundem → sensibilidade com tendência linear por região (registrada como desvio se acrescentada).
- **Heaping** no valor do mínimo (F4): o limiar 1,05 × SM captura quem declara exatamente o mínimo.
- **Quebras de série:** 2020–2021 (coleta por telefone), reponderação; sensibilidades (c) e (d).
- **27 conglomerados:** EP CR1 subestima; por isso o *wild bootstrap*.
- O hiato por UF tem erro amostral grande em UFs pequenas → pesos e regra de amostra.

## 10. Resultados

**Não estimado (regra pré-registrada; ficha G6).** EMD de β = 1,45 (ρ = 0) a 3,4 (ρ = 0,8; ρ estimado 0,51 → 2,3):
maior que 1, ou seja, o desenho não detectaria nem o repasse integral do mínimo a quem ganha até 1 SM. A exposição
diferencial E_u varia pouco entre UFs (DP 0,033) e o hiato por UF × trimestre é ruidoso. O código do estimador
(`bloco_g.g4_estimar`, *wild cluster bootstrap* de Webb) fica pronto e testado com dado simulado, mas não foi aplicado
ao dado real. Estado: **Bloqueado por poder** (proposto).

Caminhos que poderiam dar poder (decisão do Felipe, não feitos): exposição por microrregião/estrato (mais unidades,
mais ruído); período 2002–2015 com a PNAD anual (valorização forte do mínimo; outra pesquisa, fora do escopo atual).

## 11. Afirmações permitidas

- "O Hub não consegue medir, com a PNAD Contínua por UF, se a valorização do salário mínimo reduziu o hiato racial:
  o desenho não tem poder estatístico para isso (ficha G6)."

## 12. Afirmações proibidas

- "O salário mínimo reduziu o hiato racial em X" (é `C`, não `Q`).
- "O salário mínimo não afeta o hiato" a partir de IC que contém zero e −1.

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-20 | Claude Code | criação (seções 1–9 antes de rodar) |
