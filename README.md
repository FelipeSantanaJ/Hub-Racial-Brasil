# Datahub de Análise Racial no Brasil

Datahub aberto que compara historicamente três grupos — população **negra** (preta + parda),
**branca** e **indígena** no Brasil (Amarela sempre explicitada, nunca descartada) — renda,
escolaridade, mercado de trabalho, saúde e moradia, de forma agregada e segmentada por
gênero — a partir de dados públicos (IBGE, DataSUS e outras fontes, ver roadmap).

Projeto pessoal, em construção. Plano de projeto e status atual em [docs/PLANO.md](docs/PLANO.md).

## Status

✅ Fase 1 (MVP) concluída — pipeline completo (extração da PNAD Contínua, deflator oficial
do IBGE, agregações por raça/gênero/faixa etária/geografia) rodando de ponta a ponta. Ver
[docs/PLANO.md](docs/PLANO.md) para o plano completo, o histórico de como cada etapa foi
validada, e o que vem a seguir (Fase 2 — Censo Demográfico).

### Renda habitual do trabalho, por raça (2012–2026)

![Renda habitual do trabalho por raça, Brasil, 2012-2026](docs/img/renda_por_raca.png)

Valores reais (deflacionados pelo deflator oficial do IBGE, a preços do trimestre mais
recente). A população indígena tem amostra pequena na PNAD Contínua — a linha usa média
móvel de 4 trimestres para reduzir ruído (ver
[docs/LIMITACOES_E_METODOLOGIA.md](docs/LIMITACOES_E_METODOLOGIA.md)).

### O hiato racial sobrevive ao controle por escolaridade

![Renda por raça e nível de instrução, Brasil](docs/img/renda_por_raca_escolaridade.png)

O achado mais forte da Fase 1: o hiato de renda entre Branca e Negra/Indígena não desaparece
entre pessoas com o mesmo nível de instrução — ele se abre dramaticamente justo no topo
(Superior completo). Galeria completa (Preta vs. Parda separadas, cortes por gênero, por
faixa etária, e mais) e a leitura de cada gráfico em
[docs/ANALISE_FASE1.md](docs/ANALISE_FASE1.md).

## Escopo do MVP

Fonte: PNAD Contínua Trimestral (IBGE), série histórica completa via FTP do IBGE.

- Renda, escolaridade, condição de ocupação e taxa de desocupação
- Cruzamento: Raça/Cor × Gênero × Faixa etária
- Geografia: Brasil, Grandes Regiões, UFs, Município de São Paulo, Região Metropolitana de
  São Paulo (municípios individuais do ABC Paulista não são identificáveis na PNAD Contínua
  pública — ver limitação em docs/PLANO.md; fica para a Fase 2/Censo)

## Estrutura

```
data/
├── raw/            # microdados brutos (não versionado)
└── processed/      # datasets agregados e tratados
src/
├── ingestion/       # download e extração via FTP do IBGE
├── processing/      # limpeza, filtros, agregações (DuckDB/PyArrow)
└── utils/           # dicionários de variáveis, mapeamento de códigos
notebooks/pnad/      # exploração e validação
docs/                # plano de projeto, decisões, dicionário de dados
```

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Roadmap

1. **Fase 1 — PNAD Contínua** (MVP): renda, escolaridade, mercado de trabalho
2. **Fase 2 — Censo Demográfico**: moradia, condições domiciliares
3. **Fase 3 — Saúde (DataSUS/SIM/SINASC/PNS)**: natalidade, mortalidade, acesso a serviços
4. **Fase 4 — Dashboard**: publicação via Observable Framework
5. **Fase 5 — Conteúdo**: recorte para redes sociais

Módulos adicionais candidatos (sem ordem fixa, intercalados conforme interesse): violência
(Atlas da Violência), encarceramento (INFOPEN), mercado formal (RAIS/CAGED), educação (INEP),
representação política (TSE). Detalhes, prazos e marcos em [docs/PLANO.md](docs/PLANO.md).
