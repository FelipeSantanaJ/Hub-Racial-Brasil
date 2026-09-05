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
(Superior completo).

### Hiato Branca vs. Negra, com significância estatística

![Hiato percentual Branca vs. Negra](docs/img/hiato_racial_percentual.png)

Testado (Welch, IC 95%) trimestre a trimestre a partir dos microdados: os 58 trimestres da
série são estatisticamente significativos — o hiato caiu de ~76% para ~66% entre 2012 e 2026.

### É ocupação, ou é cor da pele?

![Decomposição do hiato por ocupação](docs/img/decomposicao_hiato_ocupacional.png)

Controlando por idade, escolaridade e ocupação (mesma categoria ocupacional), o hiato bruto
de 67% cai para 24% — mas não desaparece. Boa parte do hiato racial de renda não se explica
por "estar em ocupações diferentes". Confirmado por um segundo método (regressão de
Oaxaca-Blinder, com teste de significância formal — p < 0,001): resíduo de +22%, muito perto
do resultado da padronização direta acima.

### O hiato residual é maior no topo E na base da distribuição de renda

![Hiato residual por quantil](docs/img/oaxaca_blinder_quantis.png)

Decomposição por RIF (Firpo-Fortin-Lemieux): o hiato que sobra depois de controlar
idade/escolaridade/ocupação tem formato em U — menor na mediana (~15%), maior na base
(~31%, "piso pegajoso") e no topo (~36%, "teto de vidro").

### O topo 10% dos negros ficou muito mais escolarizado — mas o hiato lá em cima persiste

![Topo 10% por escolaridade](docs/img/topo10_escolaridade.png)

Olhando só pra quem está no topo 10% de renda DENTRO de cada raça (não um corte único pro
Brasil): a % com Superior completo entre os negros do topo saltou de 38% (2012) para ~58%
hoje — mas ainda fica atrás do topo dos brancos (~83%). E "faixa etária" não acompanha as
mesmas pessoas ao longo do tempo (é um corte transversal repetido) — por isso também
seguimos **gerações** (coortes de nascimento) pra ver o hiato dentro do mesmo grupo
envelhecendo, não misturado entre gerações diferentes.

### O hiato educacional se abre conforme sobe o quartil de renda

![Quartis por escolaridade](docs/img/quartis_escolaridade.png)

Generalizando o topo 10% pra toda a distribuição — os 4 quartis (Q1 = 25% mais pobres, Q4 =
25% mais ricos), cada um calculado DENTRO de cada raça: a diferença de escolaridade entre
Negra e Branca é de só ~6 p.p. no quartil mais pobre, mas chega a ~32 p.p. no mais rico.
Quanto mais alto na distribuição de renda, maior o hiato educacional entre as raças.

### O hiato racial é menor no setor público — mas a desigualdade tem muitas fontes

![Hiato setor público vs. privado](docs/img/hiato_setor_publico_privado.png)

Confirma uma hipótese conhecida: como salário de concurso público segue tabela padronizada,
o hiato racial é menor lá (~45-50%) do que no setor privado (~58-68%). Ao mesmo tempo, uma
decomposição do índice de Theil mostra que só ~7% da desigualdade TOTAL de renda no Brasil
vem de diferença entre raças — os outros 93% são desigualdade dentro de cada raça. Isso não
diminui o hiato racial (que segue grande e estatisticamente significativo), mas mostra que a
desigualdade brasileira tem várias fontes ao mesmo tempo.

**68 gráficos ao todo** — raça × gênero × faixa etária × escolaridade em todas as
combinações (Preta e Parda sempre também separadas), mais aprofundamentos: hiato por região,
segregação ocupacional e setorial (índice de Duncan), teste de quebra estrutural em 3 eventos
históricos, novas variáveis (informalidade, renda por hora, alfabetização, desalento,
sobre-qualificação), hiato/renda por geração, perfil de quem está no topo 10% e em cada um
dos 4 quartis de renda de cada raça, Gini e Theil por raça, e hiato no setor público vs.
privado. Galeria completa, com a leitura de cada gráfico, em
[docs/ANALISE_FASE1.md](docs/ANALISE_FASE1.md), ou como
apresentação em
[docs/Datahub_Racial_Brasil_Fase1.pptx](docs/Datahub_Racial_Brasil_Fase1.pptx).

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
