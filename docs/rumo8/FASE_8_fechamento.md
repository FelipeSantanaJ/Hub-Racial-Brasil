# Fase 8 — Fechamento dos textos públicos (esforço médio)

```text
FASE 8 — Fechamento. Branch: rumo8/fase8. Agora SIM os textos públicos podem mudar. Ponto de partida: docs/auditoria/pendencias_textuais.md.

TAREFAS
8.1 Aplicar as frases aprovadas em: README.md, docs/ANALISE_RACA_GENERO.md, docs/CHANGELOG_METODOLOGICO.md, docs/LIMITACOES_E_METODOLOGIA.md, docs/studies/INDICE.md, fichas e curadoria. Substituir "degrau de 2022" pela forma estimada na Fase 1; a manchete pelo resultado do critério C1; "78% associado" pelas duas escalas; G1 pelos três números e os dois limites.
8.2 Regenerar os gráficos e o deck afetados (liste os arquivos de docs/auditoria/graficos_a_regenerar.md); o deck deve refletir a versão final. Gere tudo de árvore limpa.
8.3 Atualizar STATUS dos estudos no INDICE.md ("Aprovado com ressalvas" só quando o Felipe aprovou).
8.4 Lint de frases proibidas como TESTE de CI (tests/test_frases_proibidas.py): falha se o texto público contiver, por exemplo, "degrau" aplicado a 2022 quando o modelo escolhido não for degrau; "+9,0" sem a base e sem os dois limites; "78% do hiato é explicado"; "validado" para I1 se o critério falhou; "explicado por" sobre escolaridade; "discriminação" como rótulo do resíduo; qualquer "cotas aumentaram/não aumentaram" sem os dois limites. Mantenha a lista em arquivo versionado.
8.5 Gerar o TEXTO para atualizar o documento estado-atual do projeto de conteúdo (ele fica no Project, não no repositório): entregue um bloco pronto para o Felipe colar, com o que mudou e o que ainda não pode ser dito.
8.6 CHANGELOG_METODOLOGICO.md: entrada datada "Rumo ao 8" com antes/depois dos números principais e dos defeitos corrigidos.
8.7 CI completo verde; tag v-rumo8.

ACEITE
- grep por frases proibidas em README.md, docs/ e conteudo/ vazio.
- Todos os parquets em escopo com _meta.json limpo.
- Teste de frases proibidas no CI e passando.

GATE: aprovação final do Felipe antes de qualquer publicação.
```

---
