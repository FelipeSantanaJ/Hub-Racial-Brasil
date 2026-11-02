# Fase 3 — Decomposição, mediadoras e escala (esforço médio)

```text
FASE 3 — Decomposição, mediadoras e escala. Branch: rumo8/fase3. Corrige os problemas 3, 7 e 9 do anexo A e as fragilidades de I1, E3, H4.2, H3.4 e D4.4.

PERGUNTAS DO MEIO DO CAMINHO
- Quanto do hiato está associado a diferenças PRÉ-determinadas (idade, coorte, região de nascimento, educação dos pais) e quanto a variáveis que são consequência (instrução própria, ocupação, vínculo, território)?
- O "78% associado" e o "~9 lp" sobrevivem quando a escala é a da manchete (razão de médias)?
- O que a sensibilidade de Oster e o valor de Cinelli-Hazlett significam quando o controle é um mediador?

TAREFAS
3.1 D1 em PPML (e log-OLS), lado a lado, mesmas covariáveis. O E0 do modelo de decomposição tem de fechar com ln(razão de médias) da manchete (ex.: 0,505 = ln 1,66 em 2026T2). Reescreva a ficha com a escala dita.
3.2 Oster e Cinelli-Hazlett: aplique apenas a um modelo com variáveis pré-tratamento (idade, região de nascimento, coorte; educação dos pais quando disponível e declarando o viés de corresidência do H1). Para o restante, use "decomposição descritiva". D8 passa a ter uma tabela que separa "mediadoras" de "pré-tratamento".
3.3 E3 (SAEB): acrescente a especificação com INSE médio da escola (sem efeito fixo) e a com efeito fixo; reporte a sequência de razões como LIMITES e não como partição. Reescreva "H2/H3 refutadas" se a especificação com contexto mudar a leitura (a Passada B: 0,2857 -> 0,207 DP).
3.4 I1: reescreva como "H1 refutada pelo critério" quando a correlação por UF (0,586) ficar abaixo do limiar pré-registrado (0,6); reporte a correlação disatenuada (0,78) como ressalva. Ancore a validação no gráfico por cortes de renda (R$10 mil: 39,1/40,2; 20 mil: 53,4/53,8; 30 mil: 60,3/59,4; 50 mil: 64,8/64,0 [VERIFICADO pela Passada B]) e não no limiar. Se o critério falhou, escreva "refutado".
3.5 H4.2: refaça T2 e T3 com (i) origem "empregado privado + doméstico" e (ii) incluindo público como destino alternativo, usando pnadc_extraido_v2; adicione limites de Manski para o atrito (MNAR). Tabela: diferença de T2 em 3 definições.
3.6 H3.4: validação com a tabela INVENTARIO da POF (pof_inventario.parquet). Regra pré-fixada: razão de riqueza por raça fora de 2,0 ± 0,3 refuta. Reporte 2,03x (cap fixo) e 2,20x (cap variável, suposição).
3.7 D4.4: tabela principal com três escalas (setor, subdistrito, distrito: 0,24; 0,18; 0,08 [VERIFICADO pela Passada B]). Frase permitida sempre cita o setor (~460 pessoas) e a queda com unidades maiores.
3.8 Supressão: troque o critério por n efetivo de Kish >= 30 e CV do ESTIMANDO publicado (hiato ou razão). Hoje 9 das 24 células aprovadas de Indígena/Amarela x UF têm n_kish < 30 [VERIFICADO pela Passada A]. Regenere.

ACEITE
- E0 do D1 fecha com ln(razão de médias) da manchete (tolerância 1e-6).
- D8 separa mediadoras de pré-tratamento; nenhuma ficha usa "controle de confusão" para mediadora.
- Nenhuma célula publicada com n_kish < 30.
- I1 diz "refutada" quando o critério falha.
- Ficha do E3 contém a especificação com contexto da escola.

GATE: relatório e aprovação das fichas.
```

---
