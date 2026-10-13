# Árvore de Conteúdo — Instagram / TikTok

Segunda árvore do projeto, separada da [árvore de análises](../docs/PLANO.md). Ela traduz os
achados do datahub em posts curtos para redes sociais. **Status: não iniciada — planejada
para 2027**, com lançamento em **21/03/2027** (Dia Internacional pela Eliminação da
Discriminação Racial).

```
conteudo/
├── README.md            este plano: objetivo, princípios, formatos, etapas C1-C5
├── PAUTAS.md            banco de pautas, cada uma ligada a um achado e a um gráfico do projeto
├── CALENDARIO_2027.md   planejamento de postagens mês a mês
├── templates/           (C1) modelos de carrossel, capa de vídeo e legenda
└── posts/               (C3-C4) uma pasta por post: AAAA-MM-DD_slug/
    ├── roteiro.md
    ├── legenda.txt
    └── arte/
```

## Objetivo

Levar os números do datahub a quem não vai abrir um PPT de 650 slides: uma pergunta, um
número, uma leitura honesta e a fonte. Cada post aponta para o dado completo (README, deck
e, a partir do fim de 2027, o dashboard da Etapa 6).

**Público**: pessoas interessadas em desigualdade racial no Brasil — estudantes,
jornalistas, educadores, ativistas e profissionais de dados.

## Princípios editoriais

1. **Nenhum número novo nasce aqui.** Todo número vem de um achado já publicado na árvore de
   análises e é conferido contra o parquet ou doc de origem antes de ir ao ar.
2. **Fonte sempre visível**: "PNAD Contínua/IBGE, 2026 T2" (ou o período certo) em todo card.
3. **Contexto antes do choque**: o que o número mede, para quem e em que período.
4. **Ressalvas viram conteúdo**: amostra pequena de Indígena, correlação × causalidade e
   resultados nulos são explicados, não escondidos.
5. **Linguagem**: "Negra" = Preta + Parda (definição dita uma vez por post); Indígena e
   Amarela nunca somem do recorte sem explicação.
6. **Sem números soltos de projeção**: extrapolações ("quanto tempo até fechar o hiato")
   sempre com a palavra "ilustrativo" e a hipótese por trás.

## Formatos

| Formato | Rede | Especificação | Uso |
|---|---|---|---|
| Carrossel | Instagram | 1080×1350, 6-8 cards | Achado com contexto: pergunta → número → gráfico → leitura → ressalva → fonte |
| Vídeo curto | Reels + TikTok | 9:16, 30-60 s, legenda embutida | Um número, narrado, com o gráfico animado em 2-3 passos |
| Card único | Instagram | 1080×1350 | Datas âncora e atualizações trimestrais |
| Stories | Instagram | 9:16 | Enquete "o que você acha que o dado mostra?" antes do post do achado |

**Identidade visual**: a mesma paleta terrosa dos gráficos do projeto (cores por raça
consistentes entre deck, dashboard e redes), tipografia sans-serif de alta legibilidade e
gráficos redesenhados para leitura vertical a partir das versões cruas (sem título
rasterizado) da árvore.

## Fluxo de produção de um post

1. Escolher a pauta em [PAUTAS.md](PAUTAS.md) e abrir o achado de origem.
2. Roteiro (`roteiro.md`): gancho, número, leitura, ressalva, chamada para o dado completo.
3. Arte a partir dos templates de C1.
4. **Checagem do número** contra o parquet/doc de origem (e do período/trimestre citado).
5. Legenda com fonte, definição de "Negra" e link.
6. Publicação conforme o [calendário](CALENDARIO_2027.md).

## Etapas

| Etapa | Entregável | Período planejado | Status |
|---|---|---|---|
| **C1** — Linha editorial e identidade | Guia de estilo de 1 página; templates de carrossel (capa, card de número, card de gráfico, card de ressalva, card de fonte), capa de vídeo e modelo de legenda; perfis criados | jan/2027 | ⏳ não iniciada |
| **C2** — Banco de pautas | [PAUTAS.md](PAUTAS.md) revisado, com roteiro curto para as 8 primeiras pautas | jan-fev/2027 | ⏳ não iniciada |
| **C3** — Produção piloto | 4 carrosséis + 4 vídeos prontos antes do lançamento (o primeiro mês inteiro em estoque) | fev-mar/2027 | ⏳ não iniciada |
| **C4** — Calendário de postagens | Execução do [CALENDARIO_2027.md](CALENDARIO_2027.md): 2 posts/semana + datas âncora | 21/03 a dez/2027 | ⏳ não iniciada |
| **C5** — Métricas e revisão | Revisão trimestral (jun, set, dez): o que manter, cortar ou aprofundar; plano 2028 | jun, set e dez/2027 | ⏳ não iniciada |

## Cadência e esforço

Dentro do ritmo do projeto (3-5h/semana), com a árvore de análises dividindo o tempo:

- **2 posts por semana**: 1 carrossel (terça) + 1 vídeo curto (sexta), o vídeo publicado
  igual no Reels e no TikTok.
- **Estoque mínimo de 2 semanas** produzido à frente.
- Cada pauta rende um carrossel e um vídeo; o carrossel sai primeiro.

## Métricas (C5)

| Métrica | Por quê |
|---|---|
| Salvamentos e compartilhamentos | Melhor sinal de conteúdo útil para esse tipo de dado |
| Retenção média do vídeo | Mostra se o gancho e o ritmo funcionam |
| Cliques no link (README / dashboard) | Ponte de volta para a árvore de análises |
| Comentários com dúvida de método | Viram pautas da série "Como ler este dado" |

## Ligação com a árvore de análises

| Etapa de análise | Conteúdo que alimenta | Quando |
|---|---|---|
| Etapa 1 — PNAD Contínua | Todo o banco de pautas inicial | mar-dez/2027 |
| Extensão — atualização trimestral | Card de atualização após cada divulgação do IBGE | mai, ago, nov/2027 |
| Etapa 2 — Censo 2022 | Recorte ABC Paulista e recorte indígena | a partir do 2º semestre de 2027, se a etapa fechar |
| Etapa 3 — Habitação | Saneamento e moradia por raça | 2º semestre de 2027, se a etapa fechar |
| Etapa 6 — Dashboard | Link fixo da bio e chamada dos posts | dez/2027 |
