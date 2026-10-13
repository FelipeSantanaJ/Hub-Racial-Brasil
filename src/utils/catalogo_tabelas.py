"""Catálogo de populações e insumos das tabelas de data/processed (proveniência, Fase 2).

Cada tabela declara no `_meta.json` QUEM está no cálculo e DE ONDE vêm os dados. A população
é descrita a partir dos filtros do gerador (levantados em 13/10/2026 sobre o código de
`agregacoes_pnadc.py`, `analise_causal_cotas.py` e `agregacoes_habitacao.py`). Tabela sem
entrada aqui sai com população "NÃO DOCUMENTADA" — o teste `test_catalogo_cobre_tabelas`
avisa quando isso acontece.

Quando a população de referência do plano (ocupados 18+, renda do trabalho principal > 0;
`src/utils/populacao.py`) passar a valer numa tabela, a entrada dela muda junto.
"""
from __future__ import annotations

import re

from src.utils import populacao as pop


# --- descrições reutilizadas -------------------------------------------------------------
RENDA_TODOS_14 = ("Ocupados de 14+ anos com rendimento habitual de qualquer trabalho (VD4019) "
                  "informado; no extrato não há VD4019 = 0, então equivale a renda > 0")
RENDA_TODOS_14_POS = "Ocupados de 14+ anos com rendimento habitual de qualquer trabalho (VD4019) > 0"
PESSOAS_14_RENDA = ("Pessoas de 14+ anos (contagens e população); médias de renda sobre os "
                    "ocupados 14+ com VD4019 informado")
PESSOAS_14 = "Todas as pessoas de 14+ anos"
FORCA_14 = "Pessoas de 14+ anos na força de trabalho (ocupados + desocupados)"

INSUMO_TRIMESTRAL_V1 = "trimestral_v1"
INSUMO_TRIMESTRAL_V2 = "trimestral_v2"
INSUMO_ANUAL_VISITA1_V1 = "anual_visita1_v1"
INSUMO_DERIVADO = "derivado"  # lido de outro parquet de data/processed

# (regex do nome do arquivo, população, insumo). Primeiro padrão que casar vale.
CATALOGO: list[tuple[str, str, str]] = [
    # --- migradas para a população/renda de referência (Fase 2; valem a partir da próxima regeneração)
    (r"^(hiato_racial|checagem_robustez_hiato_racial)$",
     pop.DESCRICAO_POPULACAO_REFERENCIA + "; renda: " + pop.DESCRICAO_RENDA_REFERENCIA + "; Branca × Negra (Preta+Parda)",
     INSUMO_TRIMESTRAL_V1),
    (r"^(gini_por_raca|theil_racial)$",
     pop.DESCRICAO_POPULACAO_REFERENCIA + "; renda: " + pop.DESCRICAO_RENDA_REFERENCIA
     + "; Branca, Negra e Indígena (Amarela e Ignorado fora)", INSUMO_TRIMESTRAL_V1),
    (r"^decomposicao_oaxaca_blinder.*$",
     pop.DESCRICAO_POPULACAO_REFERENCIA + " e ocupação informada; log de " + pop.DESCRICAO_RENDA_REFERENCIA,
     INSUMO_TRIMESTRAL_V1),
    # --- ainda no recorte histórico (14+, VD4019) ---
    (r"^checagem_robustez_hiato_racial$", RENDA_TODOS_14 + "; Branca × Negra (Preta+Parda)", INSUMO_TRIMESTRAL_V1),
    (r"^(hiato_racial|hiato_regional|hiato_setor_publico_privado|hiato_capital_interior|hiato_formal_informal|hiato_por_geracao)$",
     RENDA_TODOS_14 + "; Branca × Negra (Preta+Parda)", INSUMO_TRIMESTRAL_V1),
    (r"^(hiato_branca_indigena|hiato_regional_indigena)$", RENDA_TODOS_14 + "; Branca × Indígena", INSUMO_TRIMESTRAL_V1),
    (r"^(hiato_preta_parda|hiato_regional_pretaparda)$", RENDA_TODOS_14 + "; Preta × Parda", INSUMO_TRIMESTRAL_V1),
    (r"^hiato_arvore$", RENDA_TODOS_14 + " e sexo informado; Branca × Negra e Branca × Indígena; células com n ≥ 30",
     INSUMO_TRIMESTRAL_V1),
    (r"^hiato_.*_todas$", RENDA_TODOS_14 + "; Branca × Negra", INSUMO_TRIMESTRAL_V1),
    (r"^hiato_.*_pretaparda$", RENDA_TODOS_14 + "; Preta × Parda", INSUMO_TRIMESTRAL_V1),
    (r"^(dupla_desvantagem|decomposicao_raca_genero)$", RENDA_TODOS_14 + " e sexo informado; células raça × sexo",
     INSUMO_TRIMESTRAL_V1),
    (r"^decomposicao_hiato_ocupacional$", RENDA_TODOS_14 + "; Branca × Negra; padronização direta, últimos 8 trimestres",
     INSUMO_TRIMESTRAL_V1),
    (r"^(decomposicao_oaxaca_blinder.*|oaxaca_blinder_temporal)$",
     RENDA_TODOS_14_POS + " e ocupação informada; log da renda", INSUMO_TRIMESTRAL_V1),
    (r"^(gini_por_raca|theil_racial)$", RENDA_TODOS_14_POS + "; Branca, Negra e Indígena (Amarela e Ignorado fora)",
     INSUMO_TRIMESTRAL_V1),
    (r"^(perfil_topo10.*|perfil_quartis.*|funcao_quantil_racial|percentil_de_valor_racial|extremos_.*|quartis_multi_racial)$",
     RENDA_TODOS_14_POS, INSUMO_TRIMESTRAL_V1),
    (r"^faixas_salario_minimo$", "Ocupados de 14+ anos com rendimento habitual nominal de qualquer trabalho > 0",
     INSUMO_TRIMESTRAL_V1),
    (r"^(renda|renda_.*)$", PESSOAS_14_RENDA, INSUMO_TRIMESTRAL_V1),
    (r"^(escolaridade|alfabetizacao)$", PESSOAS_14, INSUMO_TRIMESTRAL_V1),
    (r"^(ocupacao|desocupacao_por_escolaridade)$", FORCA_14, INSUMO_TRIMESTRAL_V1),
    (r"^desalento_subutilizacao$", "Pessoas de 14+ anos fora da força de trabalho", INSUMO_TRIMESTRAL_V1),
    (r"^informalidade$", "Ocupados de 14+ anos (carteira: só empregados e militares/estatutários; previdência: todos)",
     INSUMO_TRIMESTRAL_V1),
    (r"^horas_trabalhadas$", "Ocupados de 14+ anos com horas habituais (VD4031, todos os trabalhos) informadas",
     INSUMO_TRIMESTRAL_V1),
    (r"^sobrequalificacao$", "Ocupados de 14+ anos com Superior completo e ocupação informada", INSUMO_TRIMESTRAL_V1),
    (r"^segregacao_.*$", "Ocupados de 14+ anos com ocupação (VD4011) ou setor (VD4010) informado", INSUMO_TRIMESTRAL_V1),
    (r"^transicao_desemprego_emprego$", "Pessoas pareadas em trimestres consecutivos (painel de 5 visitas), desocupadas em t0",
     INSUMO_TRIMESTRAL_V1),
    (r"^transicao_informal_formal$", "Pessoas pareadas em trimestres consecutivos, empregadas sem carteira em t0",
     INSUMO_TRIMESTRAL_V1),
    (r"^(quebra_estrutural|ritmo_convergencia_hiatos)$", "Série trimestral de hiato_racial / hiato_branca_indigena / hiato_preta_parda",
     INSUMO_DERIVADO),
    (r"^(painel_cohortes_superior_completo.*|did_cotas_universitarias.*)$",
     "Pessoas de 25–29 anos, agregadas por coorte de nascimento × raça (Desenho A)", INSUMO_TRIMESTRAL_V1),
    (r"^mecanismo_renda_cohortes_cotas$", RENDA_TODOS_14_POS + "; coortes de nascimento 1983–2001 (Desenho A)",
     INSUMO_TRIMESTRAL_V1),
    (r"^did_cotas_servico_publico.*$",
     "Ocupados de 14+ anos com setor público/privado classificável (empregados e militares/estatutários), "
     "janela de −10 a +12 trimestres em torno de 2014T2 (Desenho B)", INSUMO_TRIMESTRAL_V1),
    (r"^habitacao_.*$", "Moradores (pessoas) da PNAD Contínua anual, Visita 1, tema Habitação: 2016–2019 e 2022–2025",
     INSUMO_ANUAL_VISITA1_V1),
    (r"^deflator_ibge$", "Não se aplica (deflatores oficiais do IBGE por UF × trimestre)", "ibge_deflator"),
]

NAO_DOCUMENTADA = "NÃO DOCUMENTADA (conferir o gerador e acrescentar ao catálogo)"


def entrada(nome_arquivo: str) -> tuple[str, str]:
    """(população, chave de insumo) da tabela; nome com ou sem `.parquet`."""
    base = re.sub(r"\.parquet$", "", nome_arquivo)
    for padrao, populacao, insumo in CATALOGO:
        if re.match(padrao, base):
            return populacao, insumo
    return NAO_DOCUMENTADA, INSUMO_TRIMESTRAL_V1
