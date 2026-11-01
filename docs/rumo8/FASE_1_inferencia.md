# Fase 1 — Inferência e engenharia (esforço alto)

```text
FASE 1 — Inferência e engenharia. Branch: rumo8/fase1. Corrige os problemas 1 (teste), 6, 8 e 10 do anexo A.

PERGUNTAS DO MEIO DO CAMINHO
- O EP de Taylor (Estrato/UPA) bate com o EP de pesos replicados?
- O teste de quebra/tendência tem o tamanho nominal no modelo exato que o projeto publica?
- Qual é a data estimada da queda do hiato, e a forma dela (degrau ou rampa)?
- Quantas especificações o projeto testou ao todo?
- Todo número publicado reproduz de uma árvore limpa?

TAREFAS
1.1 EP com replicados. Pré-registre a regra: se a razão EP-replicados / EP-Taylor ficar dentro de ±10% nas células principais, o EP de Taylor segue; se sair, o EP oficial passa a ser o replicado (ou Taylor com fator de correção documentado) e todos os ICs são refeitos. Calcule, em >= 2 trimestres (2026T2 e um anterior a 2020, se houver replicados), EP da média por raça, do hiato P1 e P4, e da razão. Se o ambiente permitir, valide também em R com survey::svrepdesign. Tabela: célula, Taylor, replicado, R, razão.
1.2 Fator de pequena amostra. Em src/processing/bloco_g.py (CR1: hoje G/(G-1) sem (n-1)/(n-k)) e em H4.2, aplique o fator completo e regenere. Tabela antes/depois (esperado: EP do G1 3,10 -> ~3,25 [VERIFICADO pela Passada B]). Atualize os testes.
1.3 Teste de quebra. Reproduza o Monte Carlo no MODELO EXATO publicado (3 degraus + tendência, ν=5), com AR(1) ρ em {0; 0,5; 0,8} e >= 2000 réplicas, e meça o tamanho a 5% nominal (a Passada A achou 19,5%, 23,5% e 27% com 400 réplicas). Se ficar fora de 4–7%, adote crítico simulado (sup-Wald) ou bootstrap em blocos e re-estime. Estime a data da quebra (sup-Wald/Andrews e Bai-Perron) em vez de assumi-la. Compare por AIC e SSR: (i) 3 degraus datados, (ii) rampa em 2021, (iii) tendência única, (iv) joinpoint. Reporte: data estimada com IC, forma e estabilidade antes/depois. NÃO use a palavra "degrau" na saída a menos que o modelo escolhido seja degrau.
1.4 Multiplicidade global. Crie docs/auditoria/registro_especificacoes.csv: ficha, família, n de especificações, n de testes, p-valores. Aplique BH-FDR por família E globalmente. Sinalize C2 (interação e escalas), C4, S1.3 (limite superior e piso arbitrários) e a coluna "+ território" do D4 adicionada depois da primeira rodada. Reescreva as fichas afetadas com o n de especificações.
1.5 Reprodutibilidade.
   a) Regenerar d1_aninhada e b1_degraus_hiato de árvore limpa (_meta.json sem "-modificado").
   b) Teste de CI que falha se algum _meta.json tiver "-modificado".
   c) Golden com microdado REAL de 1 trimestre: avalie a licença (LICENSE-DATA.md); se o recorte puder ser versionado, versione; senão, crie job de CI opcional/local que regenera e compara por hash.
   d) Testes para filtros e junções de ingestão sem teste (_censo_i1, base_h34, gerar_pares).
   e) Corrigir a documentação do Theil: 6,67% (definição histórica, 14+, todos os trabalhos) x 6,96% (parquet atual, P1). Escreva as duas definições e qual vale.
1.6 Auditoria do SQL (a maior lacuna: src/processing/agregacoes_pnadc.py, 3.151 linhas, nunca auditada). Como não há segundo revisor humano, faça reimplementação independente das ~15 estatísticas centrais (renda média por raça P1/P4, hiato, Theil, população de referência) em OUTRO motor (Polars ou R) a partir do bruto, SEM ler o SQL. Só depois leia o SQL com este checklist: peso (V1028), deflator (habitual x efetivo), filtros de população (VD4002, VD4016 > 0, idade), recodificação de V2010, política de UPA única, junção de trimestres, tratamento de missing. Compare célula a célula. Divergência = defeito até prova em contrário.

ACEITE (verificados em docs/auditoria/verificacoes_fase1.md)
- Razão EP-replicados / EP-Taylor dentro de ±10% nas células principais, ou EP substituído.
- Monte Carlo no modelo publicado: 4–7% a 5% nominal; data estimada reportada.
- CR1 completo e testes passando.
- registro_especificacoes.csv completo; fichas atualizadas.
- Nenhum _meta.json com "-modificado"; CI falhando se houver.
- Reimplementação independente bate com os parquets em todas as células comparadas, ou cada divergência está explicada.

GATE: relatório + pedido de aprovação das fichas alteradas.
```

---
