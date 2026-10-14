# Ficha de pesquisa — `B4` · Coortes: os jovens de hoje têm hiato menor que a geração anterior na mesma idade?

| Campo | Valor |
|---|---|
| ID no plano | `B4` (`docs/PLANO_DE_ANALISE.md`, Bloco B) |
| Onda | 2 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-13 / 2026-10-13 |
| Estado de publicação | **Aprovado com ressalvas** (aprovado pelo Felipe em 13/10/2026) |
| PR | `onda2/b-c` |

> Seções 1–9 escritas **antes** de rodar (13/10/2026).

## 1. Pergunta

Na mesma idade, o hiato de renda Branca × Negra é menor para quem nasceu mais tarde? E, separando idade, período e
coorte sob uma restrição declarada, há efeito de coorte?

## 2. Tipo

`D` (comparação na mesma idade) e `C` (modelo idade-período-coorte, identificado só sob restrição).

## 3. Estimando

1. **Mesma idade, coortes diferentes (D):** hiato em log-pontos (ln média Branca − ln média Negra) aos 25–34 e aos
   35–44 anos, em 2012 (nascidos em 1978–87 e 1968–77) × 2025T3–2026T2 (nascidos em 1991–2001 e 1981–91).
2. **APC (C):** células ano (2012–2025) × idade simples (25–59) → coorte = ano − idade. Modelo para o hiato em
   log-pontos da célula: g = idade (7 grupos de 5 anos) + coorte (grupos de 5 anos de nascimento) + período.
   **Restrição que identifica o modelo (declarada):** normalização de Deaton-Paxson *(a confirmar: Deaton & Paxson
   1994; Deaton 1997)* — os efeitos de período somam zero e são ortogonais a uma tendência linear; **todo movimento
   linear no tempo é atribuído a idade e coorte**, e o período só capta ciclo. Sensibilidade: modelo sem período (AC).

## 4. População

P1, 25–59 anos (idades em que a escolaridade está quase completa e antes da aposentadoria), Branca × Negra.

## 5. Método

- **Estimador:** (1) razão de médias ponderadas por janela; (2) WLS das células com peso = 1/variância da célula.
- **Incerteza:** (1) linearização Estrato/UPA (método delta do log da razão) com a diferença entre janelas tratada
  como independente (amostras de anos distantes); (2) EP de modelo (WLS com variâncias conhecidas). As células
  compartilham UPAs (idades diferentes, mesmos domicílios): a covariância ignorada é um **risco declarado**.
- **FDR:** família = os efeitos de coorte do modelo (BH).

## 6. Dados

PNAD Contínua trimestral v2, 2012T1–2026T2 (`V2009`, `V2010`, `VD4016`, deflator).

## 7. Hipóteses concorrentes

| # | Hipótese | O que ela prevê nos dados |
|---|---|---|
| H1 | **Coortes novas convergem** (expansão escolar e cotas atingiram os nascidos depois de 1990) | Hiato aos 25–34 menor em 2025 que em 2012; efeitos de coorte decrescentes |
| H2 | **Acúmulo com a idade:** o hiato cresce ao longo da vida dentro da coorte | Efeitos de idade crescentes (25–29 < 50–59) |
| H3 | **Tudo é período** (o mercado como um todo mudou) | Efeitos de coorte planos no modelo APC; diferença aos 25–34 igual à aos 35–44 |

## 8. O que refutaria

- H1 é refutada se a diferença 2025 − 2012 aos 25–34 tiver IC incluindo zero ou for positiva.
- O efeito de coorte do APC **não pode refutar nada sozinho**: é condicional à restrição. Se o resultado mudar de
  sinal entre a restrição DP e o modelo AC, o texto fica "não identificável com estes dados".

## 9. Armadilhas

- **APC:** idade + coorte = período; sem restrição não há solução única. Qualquer "efeito de coorte" é efeito sob
  uma restrição. Declarar sempre.
- Composição: quem tem 25–34 em 2025 tem mais escolaridade (o efeito de coorte inclui isso, por construção).
- Reclassificação racial atinge coortes de forma diferente (B2).
- Sobrevivência e migração por raça.

## 10. Resultados

`b4_mesma_idade_coortes.parquet`, `b4_celulas_idade_ano.parquet` (490 células), `b4_apc.parquet`. Hiato em
log-pontos (ln média Branca − ln média Negra), P1:

| Idade | 2012 (nascidos) | 2025T3–2026T2 (nascidos) | Diferença (IC 95%) |
|---|---|---|---|
| 25–34 | 0,479 (1978–87) | 0,438 (1991–2000) | **−0,041 (−0,078 a −0,004)** |
| 35–44 | 0,552 (1968–77) | 0,528 (1981–90) | −0,024 (−0,066 a 0,018) |
| 45–54 | 0,603 (1958–67) | 0,553 (1971–80) | −0,050 (−0,097 a −0,004) |

**APC** (células ano 2012–2025 × idade 25–59; referência: idade 25–29 e coorte 1950–54; restrição de Deaton-Paxson).
Efeitos de coorte (log-pontos): 1955 −0,01 · 1960 −0,05 · **1965 −0,12** · 1970 −0,13 · 1975 −0,14 · 1980 −0,15 ·
**1985 −0,19** · 1990 −0,22 · 1995 −0,23 · 2000 −0,25 (IC ≈ ±0,065; todos a partir de 1965 com p ajustado < 0,001).
Efeitos de idade: o hiato sobe +0,09 de 25–29 para 30–34 e +0,11 para 35–39, e depois fica entre +0,08 e +0,10.
Sem período (AC), os números quase não mudam (coorte 2000: −0,22); qui²/g.l. = 1,26 (APC) e 1,30 (AC).

**O que a restrição decide.** A parte **linear** da queda entre coortes é indistinguível de uma tendência de período:
sob a restrição alternativa "sem efeito de coorte" ela seria atribuída ao tempo. O que é identificado sem restrição é a
**curvatura**: um degrau entre as coortes de 1960 e 1965, estabilidade de 1965 a 1980 e nova queda a partir de 1985.

**Leitura das hipóteses.** H1 confirmada na comparação na mesma idade (25–34: −0,04 lp) e, sob a restrição declarada,
no APC. H2 parcialmente: o hiato cresce no início da carreira (25–29 → 35–39), não ao longo de toda a vida. H3
refutada como explicação única (a curvatura entre coortes não é período).

## 11. Afirmações permitidas

- "Aos 25–34 anos, o hiato de renda entre pessoas brancas e negras é menor para quem nasceu em 1991–2000 do que era
  para quem nasceu em 1978–87 na mesma idade (0,44 contra 0,48 log-pontos)."
- "O hiato racial cresce nos primeiros anos de carreira (dos 25 aos 39 anos) e depois se estabiliza." (com a
  restrição APC na mesma tela)

## 12. Afirmações proibidas

- "A geração X é menos desigual por causa de Y."
- Efeito de coorte do APC sem a restrição na mesma tela.

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-13 | Claude Code | criação (seções 1–9 antes de rodar) |
| 2026-10-13 | Felipe Santana | aprovada com ressalvas |
