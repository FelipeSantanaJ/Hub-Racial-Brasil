# Fase 4 — Desenho causal (G1) (esforço médio)

```text
FASE 4 — Desenho causal (G1, Lei 12.711). Branch: rumo8/fase4. Corrige os problemas do G1 (anexo A, itens 2 e 3) e prepara o segundo desenho (G3).

PERGUNTAS DO MEIO DO CAMINHO
- Se o efeito verdadeiro fosse 0, 5 ou 9 p.p., qual a probabilidade de a regra de decisão do projeto concluir "efeito", "artefato" ou "indeterminado"? (Hoje a regra não podia afirmar efeito.)
- O efeito contra a média pré-lei (2009–11) é +4,9 (IC -1,4 a 11,1) contra +9,0 contra 2012 [VERIFICADO pela Passada B]. Qual é o número principal?
- O ΔY1 das 73 instituições tratadas acompanha a queda de "não declarados" (ΔY3) ou a parcela de reserva étnica?
- O que o HonestDiD exato diz que o Rambachan-Roth conservador não dizia?

TAREFAS
4.1 Reescreva a ficha do G1 (commit separado, antes de rodar): a regra de decisão passa a ser por IDENTIFICAÇÃO PARCIAL. Conclusões possíveis: "aumentaram" (Y1b > 0 com IC), "não aumentaram de forma relevante" (Y1c com limite superior < 2 p.p.), ou "não identificado: o conjunto identificado inclui 0 e +X". As três têm de poder ocorrer. Critério C3 do anexo C.
4.2 Estimativa principal contra a média pré-lei, com EP (CR1 completo da Fase 1). Mantenha base-2012 e base-2011 como alternativas. Reporte as três.
4.3 EMD pelo EP realizado (não 8,5 por simulação com 4 anos). Inclua retrodesign: para efeitos verdadeiros em {0, 2, 5, 9}, poder, exagero esperado (fator M) e erro de sinal.
4.4 Callaway-Sant'Anna como estimativa co-principal, com a distribuição de coortes de adoção (primeiro ano com reserva étnica >= 5%: 2013 (30), 2014 (16), 2015 (12), 2016–2020 (13), nunca (2) entre as tratadas; 15 dos 40 controles adotam depois de 2012 [VERIFICADO pela Passada B]). Documente a implantação gradual da Lei 12.711 [a confirmar no texto da lei].
4.5 Não publique M̄ (Rambachan-Roth conservador): ele é função mecânica do horizonte. Substitua por HonestDiD (R) com restrição de suavidade e magnitudes relativas, se o ambiente da Fase 0 permitir; senão, registre como bloqueado por ambiente.
4.6 Dose-resposta: regresse ΔY1 em ΔY3 e na parcela QT_ING_RVETNICO/QT_ING entre as 73 tratadas. Reporte o IC e o que cada hipótese (artefato x efeito real) prevê.
4.7 Sensibilidade: leave-one-out dos 5 maiores controles e das 5 maiores tratadas; limiar de 5% e 10%; com e sem pesos.
4.8 G3 (Lei 12.990): escreva e commite AGORA a ficha pré-registrada do desenho (evento ou DiD sobre ingressos com reserva; hipóteses; critério; poder esperado), antes de receber qualquer dado. Marque "Bloqueado (por dado)". Quando o dado chegar, a Fase 7 só roda.
4.9 G4: avalie se a PNAD anual 2002–2015 (valorização forte do salário mínimo) dá poder; se sim, escreva a ficha e a viabilidade; se não, mantenha "Bloqueado (por poder)" com o MDE calculado.

ACEITE
- A tabela g1_cotas_federais traz as três bases e os dois limites (Y1b, Y1c) juntos.
- A ficha contém a curva de poder da regra: nas três hipóteses (0, 5, 9) as três conclusões têm probabilidade calculada.
- Retrodesign na ficha, com "exagero esperado se significativo" para 2–10 p.p.
- Nenhum texto proposto diz "cotas aumentaram" nem "cotas não aumentaram" sem os dois limites; nenhum depende de M̄.
- Ficha do G3 commitada antes de qualquer dado.

GATE: relatório e aprovação.
```

---
