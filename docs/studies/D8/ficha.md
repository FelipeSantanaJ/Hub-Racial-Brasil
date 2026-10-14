# Ficha de pesquisa — `D8` · O resíduo: o que sobra, quão robusto é e o que concluir

| Campo | Valor |
|---|---|
| ID no plano | `D8.1`, `D8.2`, `D8.3` (`docs/PLANO_DE_ANALISE.md`, Bloco D) |
| Onda | 3 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-14 / 2026-10-14 |
| Estado de publicação | **Aprovado com ressalvas** (proposto; aguarda o Felipe) |
| PR | `onda3/d` |

> Ficha de síntese, escrita **depois** dos resultados de D1–D6 (não tem hipóteses próprias; as hipóteses estão nas
> fichas de origem).

## 1. Pergunta

Depois de comparar pessoas com a mesma idade, sexo, instrução, lugar, horas, vínculo, ocupação e atividade, quanto do
hiato sobra, quão robusta é essa sobra a variáveis não observadas e o que ela permite — e não permite — concluir?

## 2. Tipo

`C` (D8.1) e `M` (D8.2–D8.3: organiza evidência externa; o Hub não mede discriminação).

## 3–6. Estimando, população, método, dados

Os de `D1` (E8, Oster, Cinelli-Hazlett), `D2` (hiato condicional por nível), `D3` (efeitos fixos de CBO-4) e `D4`
(por UF). Nenhuma tabela nova.

## 7–9. Hipóteses, refutação, armadilhas

Ver D1 (H6) e D3 (H2'). Armadilha central: tratar o resíduo como medida de discriminação (R5).

## 10. Resultados

**D8.1 — faixa plausível do resíduo (Branca × Negra, ocupados com renda, 2025T3–2026T2, log-pontos)**

| Comparação | Parte não associada |
|---|---|
| E8 (grupamento de ocupação) | 0,094 (0,089–0,100) |
| E8 com CBO de 4 dígitos | 0,078 (0,072–0,083) |
| Omitida 1× tão forte quanto a instrução (Cinelli-Hazlett) | 0,058 |
| Omitida 2× instrução | 0,022 |
| Omitida 3× instrução, ou 1× território | ≤ 0 |
| Oster: δ que zeraria (R²max = 1,3 R̃) | 0,85 |
| Entre diplomados (D2, sem ocupação) | 0,237 |
| Por UF (D4, sem ocupação) | 0,065 (PB) a 0,186 (DF) |

**Leitura:** entre ocupados com renda, a parte do hiato que não está associada às covariáveis observáveis fica entre
**0 e ~9 log-pontos** (até ≈ 10% de renda), conforme o que se supõe sobre variáveis omitidas. Ela **não é robusta** no
sentido de Oster (δ < 1): uma omitida tão relevante quanto as observadas poderia zerá-la. Também não é desprezível: é
estável desde 2012 (0,101 → 0,094; mudança não distinguível de zero), existe nas 27 UFs, dentro da mesma ocupação
detalhada, e é maior entre diplomados.

**D8.2 — outra forma de medir:** sem RAIS identificada (sem vínculo institucional; decisão do Ponto de parada 0), o
Hub não compara pessoas na mesma firma e função. Evidência externa que mede tratamento diferente diretamente
(experimentos de currículo e estudos de auditoria no Brasil) — **NÃO VERIFICADA nesta onda**: levantar e citar só
depois de conferir as referências (a confirmar).

**D8.3 — o que concluímos.** O resíduo é a parte do hiato que as covariáveis incluídas não capturam. Há quatro
explicações concorrentes, que a PNAD Contínua não separa:

1. **discriminação** no salário, na promoção ou na alocação dentro da ocupação;
2. **qualidade diferente** da educação (escola, curso, instituição — Bloco E);
3. **variáveis omitidas** (origem social, redes, riqueza familiar — Bloco H; experiência efetiva);
4. **erro de medida** (renda declarada, heaping, classificação de cor/raça).

O que os dados mostram com segurança é a **estrutura** do hiato: ~78% está associado a diferenças de instrução, lugar,
ocupação e vínculo — diferenças que são elas mesmas resultado de desigualdades anteriores (D3.4) — e essa estrutura
mudou desde 2012 (menos instrução, mais ocupação), enquanto o resíduo ficou parado.

## 11. Afirmações permitidas

- "Comparando pessoas com as mesmas características observáveis, sobra uma diferença de até ≈ 10% que não está
  associada a essas características. Ela pode refletir discriminação, qualidade da educação, origem social ou erro de
  medida; os dados da PNAD não separam essas causas."

## 12. Afirmações proibidas

- "A discriminação responde por 10% (ou 22%) da diferença salarial."
- "O resíduo prova que não há discriminação" (ou que há).
- "Se a educação se igualasse, o hiato cairia 21%" (decomposição não é contrafactual causal).
