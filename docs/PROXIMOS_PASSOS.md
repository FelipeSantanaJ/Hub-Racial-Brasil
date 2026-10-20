# Próximos passos depois do plano de análise (Ondas 0–6)

O [plano de análise](PLANO_DE_ANALISE.md) foi executado até a Onda 6 (20/10/2026). Este arquivo lista o que ficou de
fora e depende de uma **decisão ou de um pedido do Felipe** — nada aqui foi enviado a ninguém.

## 1. Pedido via Lei de Acesso à Informação — G3 (Lei 12.990) · PENDENTE, não enviar ainda

Decisão do Felipe (20/10/2026): não pedir agora; verificar em outro momento. Antes de pedir, conferir se o Painel
Estatístico de Pessoal passou a trazer cor/raça (NÃO VERIFICADO desde a nota do IPEA de 2021). Rascunho pronto:

> **Órgão:** Ministério da Gestão e da Inovação em Serviços Públicos (MGI) — via Fala.BR.
>
> **Pedido:** Com base na Lei nº 12.527/2011, solicito tabela agregada (sem dados pessoais) com o número de
> **ingressantes** no Poder Executivo federal civil, por **ano de ingresso** (2008 a 2025), **cor ou raça** declarada
> (branca, preta, parda, amarela, indígena, não informada), **órgão** e **cargo/carreira**, e, quando disponível, se o
> ingresso se deu por **vaga reservada** nos termos da Lei nº 12.990/2014. Peço os dados em formato aberto (CSV).
> Caso alguma célula precise ser suprimida por sigilo, solicito que seja indicada e que as demais sejam mantidas. A
> finalidade é pesquisa sobre a composição racial do serviço público federal.

Ficha: [`studies/G3`](studies/G3/ficha.md).

## 2. Censo 2022 com acesso controlado (município, área de ponderação)

Os microdados públicos só identificam a UF e trazem a idade em faixas de 5 anos (ficha I1). O hiato de renda por
município, a segregação combinada com renda individual e indígenas por território exigem o arquivo de **acesso
controlado** do IBGE (o layout "acesso Controlado" está publicado no FTP do IBGE, em
`Microdados_e_Areas_de_Ponderacao/Documentacao/Layout e dicionário/`; não foi baixado). O acesso é por
pedido ao IBGE em ambiente restrito (Sala de Acesso a Dados Restritos, *a confirmar* o procedimento atual). Decisão:
pedir ou não.

## 3. Feito depois do plano (20/10/2026)

- **G1 — Rambachan–Roth (magnitudes relativas):** feito como análise posterior, não pré-registrada (ficha G1, 10b). O
  efeito de 2016–2019 não resiste a violações de tendência maiores que 0,19 × a maior variação pré-lei.
- **Gráficos da Onda 6** no deck publicado (650 slides).

## 4. Ideias que ficaram fora do plano (sem decisão)

- **G1 com o FLCI exato** de Rambachan–Roth (pacote `HonestDiD`, em R) — mais estreito que a versão conservadora.
- **POF 2024–2025** quando o IBGE publicar (*a confirmar* data): refazer H3.2 e H3.4 e ter série de riqueza.
- **G4 com mais unidades** (microrregiões) ou com a PNAD anual 2002–2015 (valorização forte do mínimo), para ter poder.
- **Hiato indígena:** usar o Censo 2022 (I1) como referência em vez da PNADC em todas as peças públicas.
