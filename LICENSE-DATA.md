# Licença dos dados derivados e dos textos

**Copyright (c) 2026 Felipe Santana**

## O que esta licença cobre

Salvo indicação em contrário, os seguintes conteúdos deste repositório estão licenciados sob a
**Creative Commons Atribuição 4.0 Internacional (CC BY 4.0)**
(<https://creativecommons.org/licenses/by/4.0/deed.pt-br>):

- as tabelas agregadas em `data/processed/` (arquivos `.parquet`, `.csv` e seus `_meta.json`);
- os gráficos em `docs/img/` e as apresentações em `docs/`;
- os textos em `docs/` e `conteudo/` (documentação, análises, notas metodológicas).

O **código-fonte** (`src/`, `tests/`, `notebooks/` e arquivos de configuração) é licenciado
separadamente sob a licença MIT (arquivo `LICENSE`).

Você pode copiar, redistribuir, adaptar e usar para qualquer fim, inclusive comercial, desde que
dê o crédito apropriado. Sugestão de atribuição:

> Fonte: Hub-Racial-Brasil (Felipe Santana), a partir dos microdados da PNAD Contínua/IBGE.
> https://github.com/FelipeSantanaJ/Hub-Racial-Brasil

## O que esta licença NÃO cobre: os microdados do IBGE

Os **microdados originais** (PNAD Contínua trimestral e anual, dicionários, deflatores) são
produzidos e publicados pelo **Instituto Brasileiro de Geografia e Estatística (IBGE)** e seguem
os termos de uso do IBGE. Este repositório **não os redistribui**: `data/raw/` é ignorado pelo git
e os extratores (`src/ingestion/`) baixam os arquivos diretamente do servidor público do IBGE
(`https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/`).

As tabelas derivadas são **estimativas calculadas por este projeto**, não estatísticas oficiais
do IBGE. O IBGE não revisou nem endossa os resultados aqui publicados. Os métodos e as
limitações estão em `docs/LIMITACOES_E_METODOLOGIA.md` e `docs/CHANGELOG_METODOLOGICO.md`.
