# Ficha de pesquisa — `S0.3` · Quem está fora de P1 é diferente entre os grupos?

| Campo | Valor |
|---|---|
| ID no plano | `S0.3` (`docs/PLANO_DE_ANALISE.md`, Bloco S) |
| Onda | 1 (pendências) |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (proposto) |
| PR | `onda1/pendencias` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

Entre as pessoas de 18+ que estão fora da população de referência (ocupados sem renda do trabalho principal,
desocupados, fora da força), as características (escolaridade, idade, criança pequena no domicílio, chefia,
região, frequência escolar) diferem entre pessoas brancas, negras e indígenas, e entre as células raça × sexo?

## 2. Tipo

`D`. Perfis comparados, sem ajuste: descreve **quem** fica de fora, não **por que**. O S0.2 já faz a comparação
ajustada (Pr(P1) condicional); aqui o objetivo é saber se "estar fora" significa coisas diferentes para cada grupo.

## 3. Estimando

Para cada condição c ∈ {P1 (referência), ocupado sem renda, desocupado, fora da força — desalentado, fora da
força — outros} e cada grupo g (raça; raça × sexo), a média ponderada (proporção, em %, ou idade em anos) de:

| Indicador | Definição |
|---|---|
| `pct_ate_fundamental_incompleto` | `VD3004` ∈ {1, 2} (sem instrução ou fundamental incompleto) |
| `pct_superior_completo` | `VD3004` = 7 |
| `idade_media` | `V2009` |
| `pct_crianca_0a5_no_domicilio` | há ao menos uma pessoa de 0–5 anos no domicílio (chave `UPA`+`V1008`+`V1014` no trimestre) |
| `pct_responsavel_domicilio` | `V2005` = 01 |
| `pct_frequenta_escola` | `V3002` = 1 |
| `pct_nordeste` | primeiro dígito de `UF` = 2 |

E a diferença Negra − Branca (e Indígena − Branca) dentro de cada condição, em p.p. (ou anos), com IC 95%.

Janelas: 2025T3–2026T2 (4 trimestres) e 2012T1–2012T4, as mesmas do S0.2.

## 4. População

- **Universo:** pessoas de 18+ (Ignorado fora), todas as condições. Não há renda envolvida além da definição de P1.
- **Exclusões:** Amarela entra só no universo (variância), não nas comparações (n pequeno nas condições raras).
- **Sensibilidade:** não se aplica (perfil descritivo; a janela 2012 serve de comparação no tempo).

## 5. Método

- **Estimador:** média ponderada (`V1028`) no domínio grupo × condição, com as 4 visitas trimestrais empilhadas.
- **Incerteza:** linearização Estrato/UPA (`variancia.variancia_linearizada`) com estimação de domínio sobre o universo
  da janela (todas as pessoas 18+ dos 4 trimestres). Como a mesma UPA aparece em vários trimestres (rotação), as
  4 visitas ficam no mesmo conglomerado: a covariância entre trimestres entra no EP. Diferença entre grupos com a
  covariância entre domínios (`variancia.diferenca_medias_design`).
- **Família de testes (FDR):** não há p-valor publicado; leitura por IC. Se algum texto afirmar "difere", a família é
  "os 7 indicadores × 4 condições de uma comparação numa janela" (28 testes) e vale BH.
- **EMD:** não se aplica (sem afirmação de "não há diferença"; onde o IC cruza zero, o texto diz "não distinguível").
- **Supressão:** n < 30 ou CV > 30% ⇒ `publicavel = False` (`src/inference/precisao.py`). Para proporções, o CV é
  sobre a proporção estimada (proporções pequenas tendem a ser suprimidas — o que é desejado).

## 6. Dados

| Fonte | Variáveis | Período | Extrato / arquivo | Acesso |
|---|---|---|---|---|
| PNAD Contínua trimestral | `V2007`, `V2009`, `V2010`, `V2005`, `V3002`, `VD3004`, `VD4001`, `VD4002`, `VD4005`, `VD4016`, `UF`, `UPA`, `V1008`, `V1014`, `Estrato`, `V1028` | 2012; 2025T3–2026T2 | `data/raw/pnadc_extraido_v2` | público |

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Fora de P1 = desvantagem acumulada para negros.** As pessoas negras fora de P1 têm menos escolaridade e mais responsabilidades de cuidado que as brancas fora de P1 | Diferença Negra − Branca positiva em `pct_ate_fundamental_incompleto` e `pct_crianca_0a5` em quase todas as condições |
| H2 | **Mesma composição.** Fora de P1, os grupos são parecidos; a diferença racial está em quem entra, não em quem fica de fora | Diferenças dentro de cada condição pequenas (≤ 3 p.p.) e menores que as diferenças entre P1 e as demais condições |
| H3 | **"Fora da força" significa coisas diferentes.** Para brancos, mais estudo ou aposentadoria (mais velhos, mais superior); para negras, cuidado | Entre mulheres fora da força: Branca com idade média e `pct_superior` maiores; Negra com `pct_crianca_0a5` maior |

## 8. O que refutaria

- H1 é refutada se, entre os desocupados e os fora da força, a diferença Negra − Branca em `pct_ate_fundamental_incompleto`
  tiver IC que inclui zero ou for negativa.
- H3 é refutada se, entre mulheres fora da força, `pct_crianca_0a5` Negra − Branca tiver IC que inclui zero **e** a
  diferença de idade média for menor que 2 anos.

## 9. Armadilhas

- **Criança no domicílio ≠ filho.** O indicador é "há criança de 0–5 anos no domicílio" (pode ser neta, sobrinha);
  é o mesmo usado no C4. Domicílios multigeracionais (mais comuns entre famílias negras *(a confirmar)*) inflam o
  indicador para avós.
- **Idade confunde tudo:** fora da força inclui aposentados; a diferença de escolaridade entre grupos fora da força
  é em parte diferença de idade (coortes antigas estudaram menos). O perfil é bruto, de propósito; ler junto com o
  S0.2 (ajustado).
- **Desalento** só existe para quem está fora da força e é pequeno: células de Indígena serão suprimidas.
- **4T2015:** a pergunta de frequência escolar mudou no 4º trimestre de 2015 *(ver `extrator_pnadc.py`)*; a janela
  2012 usa `V3002`, que existe nos dois questionários. `VD3004` é derivada e comparável.
- **Pooled 4 trimestres:** a mesma pessoa pode aparecer até 4 vezes; o EP trata isso (mesma UPA), mas "n" conta
  entrevistas, não pessoas.

## 10. Resultados

Janela 2025T3–2026T2 (`s03_perfil_fora_populacao_referencia.parquet`). Níveis por condição (total por raça):

| Indicador | P1 Branca | P1 Negra | Fora de P1 Branca | Fora de P1 Negra | Fora de P1 Indígena |
|---|---|---|---|---|---|
| Até fundamental incompleto (%) | 12,8 | 21,5 | 37,4 | 45,8 | 44,7 |
| Superior completo (%) | 35,5 | 17,7 | 16,1 | 6,1 | 6,6 |
| Idade média (anos) | 41,2 | 39,7 | 55,4 | 49,5 | 49,2 |
| Criança de 0–5 no domicílio (%) | 16,4 | 19,6 | 10,2 | 17,7 | 23,5 |
| Mora no Nordeste (%) | 13,1 | 30,3 | 19,1 | 41,7 | 36,0 |

Diferença Negra − Branca **entre quem está fora de P1** (IC 95%):

| Indicador | Total | Homens | Mulheres | Total em 2012 |
|---|---|---|---|---|
| Até fundamental incompleto (p.p.) | **+8,4** (7,8 a 9,0) | +11,0 (10,0 a 11,9) | +7,1 (6,4 a 7,8) | +10,4 |
| Superior completo (p.p.) | **−10,0** (−10,5 a −9,6) | −10,1 | −10,0 | −6,5 |
| Idade média (anos) | **−5,8** (−6,1 a −5,6) | −5,1 | −6,2 | −5,3 |
| Criança de 0–5 no domicílio (p.p.) | **+7,4** (7,0 a 7,8) | +4,3 (3,9 a 4,7) | **+9,1** (8,6 a 9,6) | +9,3 |
| Responsável pelo domicílio (p.p.) | +1,6 (1,1 a 2,1) | −4,4 (−5,3 a −3,5) | +4,7 (4,0 a 5,4) | — |

Por condição (total, Negra − Branca): desocupados +7,3 p.p. (6,2 a 8,3) com até fundamental incompleto e +5,4 p.p.
(4,1 a 6,7) com criança pequena; fora da força (outros) +9,8 p.p. (9,2 a 10,4) e +7,3 p.p. (6,9 a 7,7). Indígena −
Branca fora de P1: +13,2 p.p. (10,3 a 16,2) com criança pequena, +7,3 p.p. (3,9 a 10,7) com até fundamental incompleto.
45 das 756 estimativas de nível não passam na regra de supressão (todas de Indígena ou desalentados).

**Leitura das hipóteses.** H1 confirmada: em todas as condições fora de P1, pessoas negras têm menos escolaridade e
mais crianças pequenas no domicílio que as brancas na mesma condição. H2 refutada (diferenças de 5 a 10 p.p.). H3
consistente: entre mulheres fora da força, as negras são 6,0 anos mais jovens (−6,3 a −5,7) e vivem mais com criança
pequena (+9,1 p.p.); o "fora da força" branco é mais velho (aposentadoria), o negro mais ligado a cuidado. De 2012
para 2025–26, a diferença em escolaridade baixa caiu (10,4 → 8,4 p.p.), mas a de superior completo **aumentou**
(−6,5 → −10,0 p.p.): a expansão do superior chegou mais aos brancos que estão fora de P1.

| Saída | Arquivo | `se_metodo` | Commit |
|---|---|---|---|
| Perfis e diferenças | `data/processed/s03_perfil_fora_populacao_referencia.parquet` | `linearizacao_taylor_estrato_upa` | este PR |

## 11. Afirmações permitidas

- "Entre as pessoas de 18+ fora da população ocupada com renda (2025T3–2026T2), 45,8% das negras e 37,4% das brancas
  não completaram o ensino fundamental."
- "Entre as mulheres fora da força de trabalho, as negras vivem mais com crianças de 0 a 5 anos no domicílio (+9,1
  p.p.) e são, em média, 6 anos mais jovens que as brancas." (com a ressalva: criança no domicílio ≠ filho)

## 12. Afirmações proibidas

- "Pessoas negras ficam fora do mercado por terem filhos" (associação descritiva, sem causalidade).
- Comparar condições como se fossem escolhas.

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
