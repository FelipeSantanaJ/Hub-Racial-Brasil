"""Catálogo de populações e insumos das tabelas de data/processed (proveniência, Fase 2).

Cada tabela declara no `_meta.json` QUEM está no cálculo e DE ONDE vêm os dados. A população
é descrita a partir dos filtros do gerador (levantados em 13/10/2026 sobre o código de
`agregacoes_pnadc.py`, `analise_causal_cotas.py` e `agregacoes_habitacao.py`). Tabela sem
entrada aqui sai com população "NÃO DOCUMENTADA" — o teste `test_catalogo_cobre_tabelas`
avisa quando isso acontece.

Desde a Onda 1 (13/10/2026) todas as tabelas de renda estão na população de referência
(ocupados 18+, renda do trabalho principal > 0; `src/utils/populacao.py`) e todas as
trimestrais vêm do extrato v2.
"""
from __future__ import annotations

import re

from src.utils import populacao as pop


# --- descrições reutilizadas -------------------------------------------------------------
# Desde a Onda 1 (13/10/2026) TODA tabela de renda usa a população e a renda de referência
# (decisão do Ponto de parada 2: o Hub não fica com duas populações). Tabelas cujo indicador
# não é renda (escolaridade, ocupação, desalento…) mantêm o universo do próprio indicador (14+).
P1 = pop.DESCRICAO_POPULACAO_REFERENCIA + "; renda: " + pop.DESCRICAO_RENDA_REFERENCIA
PESSOAS_14_RENDA = ("Pessoas de 14+ anos (contagens e população); médias de renda dos ocupados com renda do "
                    "trabalho principal (VD4016) > 0. Tabelas COM faixa etária (renda, renda_completa, "
                    "renda_multidimensional_faixa) trazem também a faixa 14–17, que fica fora das análises; "
                    "tabelas SEM faixa etária usam só 18+ (" + pop.DESCRICAO_POPULACAO_REFERENCIA + ")")
PESSOAS_14 = "Todas as pessoas de 14+ anos"
FORCA_14 = "Pessoas de 14+ anos na força de trabalho (ocupados + desocupados)"
HEAPING = "; fatias com o peso empatado no limiar repartido (R9)"

INSUMO_TRIMESTRAL_V1 = "trimestral_v1"
INSUMO_TRIMESTRAL_V2 = "trimestral_v2"  # produção desde a Onda 1 (idêntico ao v1 nas colunas comuns)
INSUMO_ANUAL_VISITA1_V1 = "anual_visita1_v1"
INSUMO_DERIVADO = "derivado"  # lido de outro parquet de data/processed
T = INSUMO_TRIMESTRAL_V2

# (regex do nome do arquivo, população, insumo). Primeiro padrão que casar vale.
CATALOGO: list[tuple[str, str, str]] = [
    (r"^(hiato_racial|checagem_robustez_hiato_racial|hiato_regional|hiato_setor_publico_privado|hiato_capital_interior"
     r"|hiato_formal_informal|hiato_por_geracao)$", P1 + "; Branca × Negra (Preta+Parda)", T),
    (r"^(hiato_branca_indigena|hiato_regional_indigena)$", P1 + "; Branca × Indígena", T),
    (r"^(hiato_preta_parda|hiato_regional_pretaparda)$", P1 + "; Preta × Parda", T),
    (r"^hiato_arvore$", P1 + " e sexo informado; Branca × Negra e Branca × Indígena; células com n ≥ 30", T),
    (r"^hiato_.*_todas$", P1 + "; Branca × Negra", T),
    (r"^hiato_.*_pretaparda$", P1 + "; Preta × Parda", T),
    (r"^(dupla_desvantagem|decomposicao_raca_genero)$", P1 + " e sexo informado; células raça × sexo", T),
    (r"^decomposicao_hiato_ocupacional$", P1 + "; Branca × Negra; padronização direta, últimos 8 trimestres", T),
    (r"^(decomposicao_oaxaca_blinder.*|oaxaca_blinder_temporal)$", P1 + " e ocupação informada; log da renda", T),
    (r"^(gini_por_raca|theil_racial)$", P1 + "; Branca, Negra, Indígena e Amarela (Amarela desde a Onda 1; Ignorado fora)", T),
    (r"^extremos_distribuicao_racial$",
     P1 + "; escopos 'brasil' e 'genero' com Branca, Negra, Indígena e Amarela; Ignorado sempre fora" + HEAPING, T),
    (r"^(perfil_topo10.*|perfil_quartis.*|extremos_.*|quartis_multi_racial)$", P1 + HEAPING, T),
    (r"^(funcao_quantil_racial|percentil_de_valor_racial)$", P1, T),
    (r"^faixas_salario_minimo$", P1 + " (renda NOMINAL do trabalho principal × salário mínimo do ano)", T),
    (r"^horas_trabalhadas$", "Ocupados de 14+ com renda do trabalho principal > 0 (a faixa 14–17 fica fora das "
     "análises); horas habituais do trabalho principal (V4039)", T),
    (r"^(renda|renda_.*)$", PESSOAS_14_RENDA, T),
    (r"^(escolaridade|alfabetizacao)$", PESSOAS_14, T),
    (r"^(ocupacao|desocupacao_por_escolaridade)$", FORCA_14, T),
    (r"^desalento_subutilizacao$", "Pessoas de 14+ anos fora da força de trabalho", T),
    (r"^informalidade$", "Ocupados de 14+ anos. Carteira: só CLT entre empregados privados/domésticos/públicos "
     "(VD4009 01–06); estatutário/militar entre empregados 01–07; previdência: todos (R19, Onda 1)", T),
    (r"^sobrequalificacao$", "Ocupados de 14+ anos com Superior completo e ocupação informada", T),
    (r"^segregacao_.*$", "Ocupados de 14+ anos com ocupação (VD4011) ou setor (VD4010) informado", T),
    (r"^transicao_desemprego_emprego$", "Pessoas pareadas em trimestres consecutivos (painel de 5 visitas), desocupadas em t0", T),
    (r"^transicao_informal_formal$", "Pessoas pareadas em trimestres consecutivos, empregadas sem carteira em t0", T),
    (r"^(quebra_estrutural|ritmo_convergencia_hiatos)$", "Série trimestral de hiato_racial / hiato_branca_indigena / hiato_preta_parda",
     INSUMO_DERIVADO),
    (r"^(painel_cohortes_superior_completo.*|did_cotas_universitarias.*)$",
     "Pessoas de 25–29 anos, agregadas por coorte de nascimento × raça (Desenho A)", T),
    (r"^mecanismo_renda_cohortes_cotas$", P1 + "; coortes de nascimento 1983–2001 (Desenho A)", T),
    (r"^did_cotas_servico_publico.*$",
     "Participação: ocupados de 14+ anos com setor público/privado classificável (empregados e militares/estatutários); "
     "hiato de renda: " + P1 + "; janela de −10 a +12 trimestres em torno de 2014T2 (Desenho B)", T),
    # --- Onda 1: Blocos F e S (src/processing/sensibilidade_populacao.py) ---
    (r"^sensibilidade_hiato_populacao$", "Pessoas 18+; hiato em P1–P4 (ver coluna descricao_populacao); "
     "P1 = " + pop.DESCRICAO_POPULACAO_REFERENCIA, T),
    (r"^sensibilidade_hiato_p5_anual$", "Pessoas 18+ da PNAD Contínua anual (Visita 1; Visita 5 em 2020–2021); "
     "P1 vs. P5 (renda domiciliar per capita VD5008), valores nominais do ano", "anual_v2"),
    (r"^composicao_populacao_referencia$", "Pessoas 18+ por condição (população de referência, ocupado sem renda "
     "do trabalho principal, desocupado, fora da força)", T),
    (r"^selecao_entrada_populacao_referencia$", "Pessoas 18+ Brancas, Negras e Indígenas; Pr(estar na população "
     "de referência)", T),
    (r"^composicao_racial_declarada$", "Pessoas 14+, 18+ e população de referência; cor/raça declarada (V2010)", T),
    (r"^heaping_renda$", P1 + "; % com renda nominal múltipla de R$ 100/500/1.000", T),
    (r"^heaping_renda_faixas$", P1 + "; 2º trimestres; % múltiplo de R$ 1.000/100 e arredondamento a 1–2 algarismos "
     "significativos dentro de faixas NOMINAIS fixas (F4)", T),
    # --- Onda 1: Bloco A (src/processing/bloco_a.py) ---
    (r"^a2_metricas_hiato_preta_parda$", P1 + "; Preta × Parda (hiato % = Preta ÷ Parda − 1; R11)", T),
    (r"^(a2_metricas_hiato|a3_hiato_quantis|a4_desigualdade_decomposicao|a5_representacao_decimos|a6_dominancia)$",
     P1 + "; Branca, Negra (Preta+Parda), Indígena e Amarela; Ignorado fora", T),
    # --- Onda 1: Bloco T (src/processing/bloco_t.py) ---
    (r"^(t1_renda_domiciliar_per_capita|t2_pobreza|t3_fontes_de_renda|t4_decimos_renda_domiciliar)$",
     "Todas as pessoas (todas as idades) da PNAD Contínua anual (Visita 1; Visita 5 em 2020–2021), exceto "
     "pensionistas/empregados domésticos e parentes (V2005 17–19); renda domiciliar per capita habitual (VD5008), "
     "valores nominais do ano", "anual_v2"),
    # --- Onda 1, pendências: Bloco S (src/processing/bloco_s.py) ---
    (r"^s03_perfil_fora_populacao_referencia$", "Pessoas 18+ (Ignorado fora), por condição (P1, ocupado sem renda, "
     "desocupado, fora da força); 4 trimestres empilhados por janela (2012; 2025T3–2026T2)", T),
    (r"^s13_limites_hiato$", "Pessoas 18+ (Ignorado fora); renda potencial de quem está fora de P1 limitada por "
     "suposições explícitas; renda observada = " + pop.DESCRICAO_RENDA_REFERENCIA, T),
    (r"^s14_margens_intensiva_extensiva$", "Pessoas 18+ (Ignorado fora); renda do trabalho principal por adulto "
     "(fora de P1 = 0) = Pr(P1) × horas habituais (V4039) × renda por hora", T),
    (r"^(s15_selecao_no_tempo|s15_selecao_episodios)$", "Séries do S0.1, S0.2 (refeito por ano) e S1.1; pessoas 18+", T),
    # --- Onda 2: Bloco B (src/processing/bloco_b.py) ---
    (r"^(b1_tendencia_hiato|b1_degraus_hiato)$", "Séries publicadas do hiato: P1 (hiato_racial, hiato_branca_indigena, "
     "hiato_preta_parda, a2_*), P4 (sensibilidade_hiato_populacao) e renda domiciliar per capita (t1)", INSUMO_DERIVADO),
    (r"^b6_projecao_condicional$", "Saída do B1 (tendência do hiato); projeção condicional", INSUMO_DERIVADO),
    (r"^b5_ciclo_tendencia$", "Séries do S1 (P1 e P4, Branca × Negra) + taxa de desocupação (14+, IBGE)", T),
    (r"^b5_taxa_desocupacao$", "Pessoas de 14+ na força de trabalho; desocupados ÷ força", T),
    (r"^(b3_hiato_quantis_serie|b3_quantis_janelas)$", P1 + "; Branca × Negra; quantis incondicionais", T),
    (r"^b3_tendencia_quantis$", P1 + " (trimestral) e renda domiciliar per capita (t1, anual); tendência por quantil", T),
    (r"^b2_decomposicao_tempo$", P1 + " e P4 (pessoas 18+, fora de P1 = 0); Branca × Negra (Preta/Parda); janelas "
     "2012 e 2025T3–2026T2", T),
    (r"^b2_composicao_racial_coortes$", "Pessoas 18+ dos 2º trimestres, coortes de nascimento 1950–1994", T),
    (r"^(b4_mesma_idade_coortes|b4_celulas_idade_ano|b4_apc)$", P1 + "; 25–59 anos; Branca × Negra; células ano × idade", T),
    # --- Onda 2: Bloco C (src/processing/bloco_c.py) ---
    (r"^(c123_racaxsexo_celulas|c2_interacao_regressao|c1_theil_celulas|c1_quantis_celulas|c2_interacao_tendencia)$",
     P1 + " e P4 (pessoas 18+, fora de P1 = 0); células Branca/Negra/Indígena × sexo", T),
    (r"^c123_racaxsexo_domiciliar_anual$", "Pessoas 18+ da PNAD Contínua anual (Visita 1; Visita 5 em 2020–2021), exceto "
     "V2005 17–19; renda domiciliar per capita (VD5008) por raça × sexo da pessoa", "anual_v2"),
    (r"^c4_penalidade_maternidade$", "Pessoas de 25–44 anos (responsáveis ou cônjuges na definição principal); filho(a) "
     "de 0–5 no domicílio (UPA + V1008 + V1014); janelas 2012 e 2025T3–2026T2", T),
    (r"^(c6_conjugal_chefia|c6_hiato_condicional)$", "Pessoas de 25–59 anos (Branca, Negra); chefia (V2005 = 01) e "
     "casal (cônjuge no domicílio); janelas 2012 e 2025T3–2026T2", T),
    (r"^(c5_trabalho_domestico|c5_tendencia)$", "Mulheres 18+ (P1 e todas); trabalho doméstico = VD4009 03/04", T),
    # --- Onda 3: Bloco D (src/processing/bloco_d.py) ---
    (r"^(d1_aninhada|d1_contribuicao_blocos|d1_mudanca_janelas|d1_ob_reimers|d1_rif_ob)$",
     P1 + "; Branca, Negra (Preta+Parda) e Indígena; com horas habituais (V4039) > 0; ln da renda real", T),
    (r"^d1_sensibilidade_omitidas$", P1 + "; Branca e Negra; especificação completa (E8)", T),
    (r"^d1_extensiva_p1$", "Pessoas 18+ (Branca, Negra, Indígena); desfecho = estar em P1 (" + pop.DESCRICAO_POPULACAO_REFERENCIA + ")", T),
    (r"^(d2_hiato_por_nivel|d2_quantis_nivel|d2_sobrequalificacao)$",
     P1 + "; Branca, Negra e Indígena (quantis: Branca × Negra); sobrequalificação = Superior completo (VD3004 = 7)", T),
    (r"^d3_segregacao$", P1 + "; Branca × Negra; ocupação por grupamento (VD4011) e CBO 4 dígitos (V4010, sem ignorados)", T),
    (r"^d3_hiato_dentro_ocupacao$", P1 + "; Branca, Negra e Indígena; controles da E8 do D1 e efeitos fixos de CBO 4 dígitos", T),
    (r"^d4_territorio$", P1 + "; Branca × Negra; por UF, tipo de área (V1023) e situação (V1022)", T),
    (r"^d5_posicao_ocupacao$", P1 + "; Branca, Negra e Indígena; posição (VD4009) e previdência (VD4012)", T),
    (r"^d6_hiato_idade$", P1 + "; Branca, Negra e Indígena; faixas etárias de 5 anos", T),
    # --- Onda 4: Blocos E e H, parte PNADC (src/processing/bloco_eh.py) ---
    (r"^e1_escolarizacao_idade$", "Pessoas de 5 a 29 anos (Branca, Negra, Indígena; todas, não só P1); frequência, etapa "
     "adequada (V3003 até 2015, V3003A desde 2016, harmonizados) e conclusão (VD3004)", T),
    (r"^e4_rede_escola$", "Pessoas que frequentam pré-escola, fundamental, médio regular ou graduação (V3002 = 1), "
     "Branca, Negra, Indígena; rede (V3002A, desde 2016)", T),
    (r"^(h1_transmissao_educacional|h1_corresidencia)$", "Pessoas de 18 a 29 anos (Branca, Negra, Indígena); origem = "
     "maior VD3004 do responsável/cônjuge para filhos(as) e enteados(as) corresidentes (V2005 04/05/06)", T),
    (r"^(h2_origem_renda|h2_mobilidade_quintis)$", "Filhos(as) e enteados(as) corresidentes de 18 a 29 anos em P1 (" +
     pop.DESCRICAO_POPULACAO_REFERENCIA + "), Branca × Negra; origem = escolaridade e renda do trabalho dos pais", T),
    (r"^h3_patrimonio_proxy$", "PNAD Contínua anual (Visita 1; Visita 5 em 2020–2021 só para rendas de capital), exceto "
     "V2005 17–19; condição do domicílio (S01017) por pessoa e rendas de aluguel/aplicações (V5007A/V5008A) de adultos 18+",
     "anual_v2"),
    # --- Onda 4, parte 2: INEP e POF (src/processing/bloco_eh_externos.py) ---
    (r"^e3_saeb_proficiencia$", "Estudantes do 5º e 9º anos do fundamental e da 3ª/4ª série do médio com proficiência "
     "válida no SAEB 2023; cor/raça autodeclarada no questionário (TX_RESP_Q04)", "inep_saeb_2023"),
    (r"^e6_superior_composicao$", "Cursos de graduação do Censo da Educação Superior 2014 e 2023: ingressantes, "
     "matriculados e concluintes por cor/raça (não declarada à parte)", "inep_censo_superior"),
    (r"^e7_escolas_segregacao$", "Escolas em atividade com matrícula na educação básica, Censo Escolar 2024; matrículas "
     "por cor/raça (não declarada à parte)", "inep_censo_escolar_2024"),
    (r"^h32_pof_bens$", "Moradores da POF 2017–2018 (Branca, Negra, Indígena); bens duráveis da unidade de consumo",
     "ibge_pof_2017_18"),
    # --- Onda 5: Bloco G (src/processing/bloco_g.py) ---
    (r"^g1_cotas_federais$", "Instituições públicas (federais, estaduais, municipais) com ≥ 30 ingressantes em cursos "
     "presenciais de graduação em todos os anos 2009–2023 (Censo da Educação Superior); tratadas = federais sem reserva "
     "étnica antes de 2013; controles = estaduais e municipais sem reserva étnica antes de 2013", "inep_censo_superior_2009_2023"),
    (r"^g1_series_grupos$", "Mesmas instituições do g1_cotas_federais; médias anuais por grupo (ponderadas pelos "
     "ingressantes de 2012)", "inep_censo_superior_2009_2023"),
    (r"^g4_salario_minimo$", P1 + "; Branca × Negra; painel UF × trimestre 2012T1–2026T2", T),
    (r"^g6_emd$", "Não se aplica (efeito mínimo detectável por simulação; insumos do G1 e do G4)", "g_misto"),
    (r"^habitacao_.*$", "Moradores (pessoas) da PNAD Contínua anual, Visita 1, tema Habitação: 2016–2019 e 2022–2025",
     INSUMO_ANUAL_VISITA1_V1),
    (r"^deflator_ibge$", "Não se aplica (deflatores oficiais do IBGE por UF × trimestre)", "ibge_deflator"),
    (r"^linhas_pobreza_ppc$", "Não se aplica (linhas internacionais de pobreza do Banco Mundial, PPC 2021, convertidas "
     "para R$ nominais por pessoa por mês, por ano)", "wb_ppc_ipc"),
]

NAO_DOCUMENTADA = "NÃO DOCUMENTADA (conferir o gerador e acrescentar ao catálogo)"


def entrada(nome_arquivo: str) -> tuple[str, str]:
    """(população, chave de insumo) da tabela; nome com ou sem `.parquet`."""
    base = re.sub(r"\.parquet$", "", nome_arquivo)
    for padrao, populacao, insumo in CATALOGO:
        if re.match(padrao, base):
            return populacao, insumo
    return NAO_DOCUMENTADA, INSUMO_TRIMESTRAL_V2
