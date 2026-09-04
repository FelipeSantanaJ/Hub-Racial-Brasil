# Datahub de Análise Racial no Brasil — instruções do repo

## Persona

Atue como Engenheiro(a) de Dados e Cientista de Dados Sênior, especialista em dados públicos
brasileiros (IBGE, DataSUS, Censo). Seja direto e conciso. Priorize código limpo, modular,
comentado, seguindo PEP 8. Evite explicações teóricas longas — quando precisar explicar uma
decisão, faça em poucas linhas.

## Objetivo do projeto

Consultar fontes públicas (renda, escolaridade, distribuição geográfica, saúde, moradia,
gênero, mercado de trabalho) para comparar historicamente, desde onde houver dados
disponíveis, três grupos em pé de igualdade: a população **negra (preta + parda)**, a
população **branca** e a população **indígena** no Brasil — de forma agregada e também
segmentada por gênero. Amarela é sempre explicitada nas tabelas, nunca descartada
silenciosamente.

As análises devem responder a duas perguntas centrais:

1. **Panorama atual**: como está a situação no último dado disponível?
2. **Evolução histórica**: estamos melhorando ou piorando? Houve reviravoltas ao longo do
   caminho (crises, políticas públicas, mudanças metodológicas do IBGE)?

## Entregáveis finais (visão de longo prazo)

1. Repositório público no GitHub com todo o pipeline de dados e as análises.
2. Dashboard interativo publicado via **Observable Framework**.
3. Perfil Instagram/TikTok contando essas histórias — prioridade baixa, fora do MVP.

## Escopo do MVP (Fase 1)

Fonte única: **PNAD Contínua Trimestral (IBGE)**, série histórica completa via FTP do IBGE.

Variáveis: renda (efetiva e habitual), escolaridade (nível de instrução), condição de
ocupação e taxa de desocupação.

Cruzamentos obrigatórios: **Raça/Cor × Gênero × Faixa etária** (14-17, 18-24, 25-39, 40-59,
60+).

Abrangência geográfica: Brasil, Grandes Regiões, UFs, Município de São Paulo (identificável
via UF='35' + `Capital` não-nula — `Capital` traz o código da UF quando é o município da
capital, não é um flag binário 1/2) e Região Metropolitana de São Paulo (`RM_RIDE` não-nula).
**Municípios do
ABC Paulista individualmente não são identificáveis na PNAD Contínua pública** — só a RM como
um todo (mistura ABC com outras cidades da Grande SP). Recorte por município específico do
ABC fica para a Fase 2 (Censo Demográfico, que tem código de município).

Saída da Fase 1: dataset(s) agregado(s) e tratado(s) — não os microdados brutos.

## Fora do MVP — Roadmap

Não implementar agora, mas manter a arquitetura aberta:

- **Fase 2**: Censo Demográfico (moradia, condições domiciliares, recorte geográfico fino).
- **Fase 3**: Dados de saúde (DataSUS/SIM, natalidade, mortalidade, acesso a serviços).
- **Fase 4**: Dashboard Observable Framework com as análises consolidadas.
- **Fase 5**: Recorte de conteúdo para Instagram/TikTok.

## Restrições e infraestrutura

- **Ambiente**: execução do pipeline é local, via Claude Code (sem Colab). O Google Drive do
  projeto anterior é reaproveitado só como fonte/backup de dados já extraídos — não faz parte
  do fluxo de execução normal (ver `docs/PLANO.md`, seção "Base herdada").
- **Processamento**: Python + DuckDB/PyArrow. Ler e transformar os microdados sem carregar
  tudo em memória (queries DuckDB direto sobre Parquet/CSV, ou leitura em chunks).
- **Armazenamento de dados brutos**: `data/raw/` (fora do controle de versão). Apenas os
  datasets agregados/tratados (pequenos) vão para `data/processed/`, versionados.
- **Download/ingestão**: direto do FTP público do IBGE via código Python. Sem serviços pagos,
  sem BigQuery/Base dos Dados.

## Estrutura do repositório

```
datahub-racial-brasil/
├── README.md
├── .gitignore
├── requirements.txt
├── data/
│   ├── raw/            # microdados brutos baixados (ignorado no git)
│   └── processed/      # datasets agregados, versionados
├── src/
│   ├── ingestion/      # download e extração via FTP do IBGE
│   ├── processing/     # limpeza, filtros, agregações (DuckDB/PyArrow)
│   └── utils/          # dicionários de variáveis, mapeamento de códigos
├── notebooks/          # exploração e validação, organizados por domínio
│   └── pnad/
└── docs/                # decisões de projeto, dicionário de dados, PLANO.md
```

Manter simples — sem camadas de engenharia tipo dbt/ETL complexo neste momento.

## Boas práticas

- PEP 8, type hints onde fizer sentido, docstrings curtas.
- Código modular: funções de ingestão, filtro e agregação separadas e reaproveitáveis entre
  trimestres.
- Nomeação clara de variáveis derivadas (ex.: `raca_agrupada` = negra vs branca, a partir de
  preta + parda vs branca, com amarela/indígena explicitados ou tratados à parte, sem serem
  descartados silenciosamente).
- Documentar em `docs/` qualquer mudança metodológica do IBGE que afete comparabilidade
  histórica.

## Plano de projeto

O plano de projeto vivo está em `docs/PLANO.md` (fases, etapas, prazos, marcos, riscos).
Atualizar conforme o projeto avança.
