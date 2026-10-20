# Ficha de pesquisa — `G3` · Lei 12.990/2014 (reserva de 20% em concursos federais) e a composição racial do funcionalismo

| Campo | Valor |
|---|---|
| ID no plano | `G3` (`docs/PLANO_DE_ANALISE.md`, Bloco G) |
| Onda | 5 |
| Responsável | Felipe Santana (execução: Claude Code) |
| Criada em / atualizada em | 2026-10-20 / 2026-10-20 |
| Estado de publicação | **Bloqueado** (por dado) |
| PR | `onda5/g` |

## 1. Pergunta

A Lei 12.990/2014 aumentou a proporção de pessoas negras entre os ingressantes do Poder Executivo federal?

## 2. Tipo

`Q` (event study com dado de pessoal). Não executado: falta dado público com raça/cor por servidor.

## 3. Estimando

% de negros entre os ingressantes por ano de ingresso, antes e depois de junho de 2014, por órgão/carreira.

## 4. População

Servidores civis ativos do Executivo federal (SIAPE).

## 5. Método

Não se aplica (sem dado). O desenho do Hub com a PNADC (`did_cotas_servico_publico*`) continua **Bloqueado** desde
13/10/2026 (0 de 40 testes sobrevivem ao FDR; a PNADC não identifica servidor federal).

## 6. Dados — verificação feita em 20/10/2026

| Fonte | Tem raça/cor? | Público? | Situação |
|---|---|---|---|
| Painel Estatístico de Pessoal (PEP, `pep.paineis.gov.br`) | Segundo o IPEA (Silva & Lopez 2021, nota de rodapé 8), o painel "não apresenta informações sobre a cor ou raça dos servidores" | painel e exportação CSV públicos | **sem raça/cor** (fonte: nota do IPEA; o painel atual não foi aberto — NÃO VERIFICADO se mudou depois de 2021) |
| SIAPE (microdados por servidor) | sim (cor/raça obrigatória no SIGEPE) | "os dados relativos à cor e raça dos servidores não estão disponíveis para a consulta pública" (Silva & Lopez 2021, p. 1–2) | **não público** |
| Atlas do Estado Brasileiro (IPEA) | sim, agregado por ano de ingresso entre os **ativos** em 2020 | público (gráficos) | agregado; sofre viés de sobrevivência (quem saiu antes de 2020 não aparece); downloadable? NÃO VERIFICADO |
| Informe de Pessoal (ENAP) | sim, agregado | público (PDF) | agregado; sem série por ano de ingresso verificada |

Fonte da verificação: IPEA, Nota Técnica "Cor ou raça do serviço civil ativo do Executivo federal (1999–2020)",
Tatiana Dias Silva e Felix Garcia Lopez, 2021 (lida em 20/10/2026). A nota descreve: entre os ingressantes de 2013,
32,1% negros; de 2014, 41,8% — e alerta que é "precoce associar" a mudança à lei, porque ela é de junho de 2014 e
parte dos empossados veio de concursos anteriores. Descrição de terceiros; não reproduzida aqui.

## 7. Hipóteses concorrentes

Não se aplica (sem estimação).

## 8. O que refutaria

Não se aplica.

## 9. Armadilhas (para quando houver dado)

Sobrevivência (estoque de ativos ≠ fluxo de ingresso); ingresso por concurso aberto antes da lei; declaração de cor
obrigatória só a partir de certa data (subnotificação de 17% em 1999 → 6% em 2020); um único "tratado" (o Executivo
federal) sem grupo de comparação natural.

## 10. Resultados

Nenhum. **Caminho para destravar (decisão do Felipe):** pedido via Lei de Acesso à Informação ao Ministério da Gestão
de tabela agregada de ingressantes por ano × cor/raça × órgão/carreira (fluxo, não estoque), 2008–2025.

## 11. Afirmações permitidas

- "O Hub não avalia a Lei 12.990: não há dado público com cor/raça por servidor."

## 12. Afirmações proibidas

- Qualquer efeito da Lei 12.990 a partir da PNADC.

## 13. Revisão

| Data | Quem | O que mudou |
|---|---|---|
| 2026-10-20 | Claude Code | criação; verificação de disponibilidade de dado |
