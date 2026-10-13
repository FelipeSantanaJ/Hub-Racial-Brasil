"""Deck final da Etapa 1 — junta:
  0. Leitura principal das Ondas 1 e 2 (estudos com ficha em docs/studies) — `ONDAS`
  1. Árvore cruzada de renda por raça (itens 1-10) — `manifesto['arvore']`
  2. Topo 10% / base 10% / quartis com limiares Brasil / gênero / raça×gênero — `manifesto['extremos']`
  3. Ponteiro pra tabela de crescimento (arquivo à parte)
  4. "Outras análises" — análises complementares NÃO cobertas pela árvore (sem Preta/Parda)

Nos blocos 1-2 o texto (título/subtítulo/legenda/fonte) é CAIXA DE TEXTO e a imagem é
crua. No bloco 4 as imagens trazem o título rasterizado (regerar as ~35
como figura crua fica pra uma passada futura) — o slide só acrescenta legenda + fonte.

Uso:
    python -m src.processing.apresentacao_final
"""
from __future__ import annotations

import json

from pptx import Presentation
from pptx.util import Inches
from pptx.enum.text import PP_ALIGN

from src.processing import apresentacao_arvore as A

REPO_ROOT = A.REPO_ROOT
MANIFESTO = A.MANIFESTO
# Cada revisão gera um arquivo versionado — não sobrescreve o
# Datahub_Racial_Brasil_Fase1.pptx publicado.
VERSAO = "v7"
DESTINO = REPO_ROOT / "docs" / f"Datahub_Racial_Brasil_Fase1_{VERSAO}.pptx"

# ---- "Outras análises": curadoria do que continua (sem Preta/Parda, sem o que a
# árvore já cobre). (título da seção, nota, [(arquivo, legenda), ...]) ---------- #
OUTRAS = [
    # (a "Hiato Branca vs. Negra — série histórica" saiu daqui: a árvore agora traz a
    #  série de hiato — com Indígena — nos itens 1-8.)
    ("É ocupação, ou é cor da pele? — decomposição do hiato",
     "Quanto idade, escolaridade e ocupação explicam do hiato Branca vs. Negra.", [
        ("decomposicao_hiato_ocupacional.png", "Padronização direta: 66% bruto → 31% (+escolaridade) → 25% (+ocupação, residual). Ocupação sozinha: 34%."),
        ("oaxaca_blinder_decomposicao.png", "Regressão (Oaxaca-Blinder) com teste de significância: resíduo +23% (p<0,001; parte não associada às covariáveis, não é medida de discriminação)."),
        ("oaxaca_blinder_quantis.png", "O resíduo não é uniforme: ~15% na mediana, ~35% na base (piso pegajoso), ~34% no topo (teto de vidro)."),
        ("renda_por_raca_ocupacao.png", "Dentro de CADA categoria ocupacional, Branca ganha mais que Negra."),
     ]),
    ("Raça × A × B — combinações com ocupação (pooled 8 trimestres)",
     "Heatmaps raça × 2 dimensões. Ocupação (11 categorias) só no snapshot pooled — célula por trimestre isolado fica fina demais.", [
        ("raca_genero_geracao.png", "Renda por raça, gênero e geração."),
        ("raca_genero_ocupacao.png", "Renda por raça, gênero e ocupação."),
        ("raca_faixa_etaria_escolaridade.png", "Renda por raça, faixa etária e escolaridade."),
        ("raca_faixa_etaria_ocupacao.png", "Renda por raça, faixa etária e ocupação."),
        ("raca_geracao_escolaridade.png", "Renda por raça, geração e escolaridade."),
        ("raca_geracao_ocupacao.png", "Renda por raça, geração e ocupação."),
        ("raca_escolaridade_ocupacao.png", "Mesmo nível de instrução E mesma ocupação — o hiato ainda aparece na maioria das células."),
     ]),
    ("Região, segregação e quebras estruturais", None, [
        ("hiato_racial_por_regiao.png", "O hiato varia MUITO por região: 60–83% no Sudeste vs. 39–52% no Sul (2012–2026)."),
        ("segregacao_ocupacional.png", "Duncan: ~17% de um grupo precisaria trocar de categoria ocupacional pra igualar o outro."),
        ("hiato_quebra_estrutural.png", "Teste tipo Chow com EP robusto (EWC): mudança significativa em 2 dos 3 eventos (a reforma da previdência não)."),
    ]),
    ("Novas variáveis da PNAD", "Informalidade, jornada, alfabetização, desalento.", [
        ("informalidade_carteira_assinada.png", "% com carteira (só CLT, entre empregados): Branca 72%, Negra 63%, Indígena 48% (2026 T2)."),
        ("renda_por_hora.png", "O hiato sobrevive quase intacto na renda POR HORA — não é jornada, é remuneração."),
        ("alfabetizacao_60mais.png", "60+ anos: Branca 93%, Negra 80%, Indígena 72% alfabetizados."),
        ("desalento.png", "Fora da força de trabalho, Negra e Indígena desistem de procurar emprego a taxas 2-4x a de Branca."),
    ]),
    ("Topo 10% — limiar DENTRO de cada raça (série histórica)",
     "Complementa a seção de topo 10% / base 10% / quartis (limiares Brasil / gênero / raça×gênero): aqui o P90 é calculado dentro de cada raça, 2012–2026.", [
        ("topo10_genero.png", "% de mulheres no topo 10% de cada raça."),
        ("topo10_escolaridade.png", "% com Superior completo no topo 10% — negros 37%→61%, brancos 84% (2012→2026)."),
        ("topo10_escolaridade_composicao.png", "Distribuição pelos 7 níveis — o topo negro tem mais Médio completo (22%) que o branco (9%)."),
        ("topo10_faixa_etaria.png", "Composição por faixa etária do topo 10%."),
        ("topo10_geracao.png", "Composição por geração — topo negro pende a Millennial/Z; branco a Boomer/X."),
    ]),
    ("4 quartis — limiar DENTRO de cada raça (série histórica)",
     "Complementa a seção de topo 10% / base 10% / quartis: P25/P50/P75 dentro de cada raça, 2012–2026.", [
        ("quartis_genero.png", "% de mulheres por quartil — maioria entre as mais pobres nas duas raças."),
        ("quartis_escolaridade.png", "% com Superior completo cresce em todo quartil, mas o hiato se abre no Q4 (73% vs. 43%)."),
        ("quartis_escolaridade_composicao.png", "Distribuição pelos 7 níveis, um painel por quartil."),
        ("quartis_faixa_etaria.png", "Composição por faixa etária, um painel por quartil."),
        ("quartis_geracao.png", "Composição por geração, um painel por quartil."),
    ]),
    ("Desigualdade interna, setor público/privado, sobre-qualificação", None, [
        ("gini_por_raca.png", "Gini DENTRO de cada raça — Branca tem mais desigualdade interna (distribuição mais comprimida na base)."),
        ("theil_decomposicao.png", "Só ~7% da desigualdade total do Brasil vem de diferença ENTRE raças — 93% é dentro de cada uma."),
        ("hiato_setor_publico_privado.png", "Hiato menor no Público (mediana 48%) que no Privado (mediana 60%) em todos os trimestres."),
        ("segregacao_setorial.png", "Segregação por setor (10%) < por ocupação (17%)."),
        ("sobrequalificacao.png", "Negros com Superior completo em ocupação elementar: quase o dobro da taxa de brancos."),
    ]),
    ("A função quantil da renda em R$, e sua inversa", None, [
        ("funcao_quantil_racial.png", "Em R$: P10 R$1.500 vs R$766; P50 R$3.000 vs R$2.000; P90 R$10.000 vs R$5.000."),
        ("hiato_por_percentil.png", "O hiato bruto por percentil não é uniforme — maior na base (96% no P10) e no topo (100% no P90)."),
        ("percentil_de_valor_racial.png", "R$3.000 = P58 entre brancos (meio), mas P77 entre negros (quase o topo)."),
    ]),
]


# ---- Leitura principal das Ondas 1 e 2 (decisão do Felipe, 13/10/2026: a queda do hiato é um degrau em 2022,
# não uma tendência contínua). (título, nota, [(arquivo, legenda), ...]); fichas em docs/studies. ------------- #
ONDAS = [
    ("Como o hiato mudou no tempo (Onda 2, Bloco B)",
     "Erro-padrão robusto a autocorrelação (EWC). Fichas B1–B6.", [
        ("onda2_b1_degraus_hiato.png", "A queda de 2012–2026 é um degrau em 2022 (−5,0 p.p.; IC −6,8 a −3,1); sem tendência contínua, e plana desde 2022 (B1)."),
        ("onda2_b6_projecao_condicional.png", "Projeção condicional: no ritmo de 2012–26, zero por volta de 2110 (2079–2231); no ritmo desde 2022, sem data (B6)."),
        ("onda2_b3_hiato_quantis_janelas.png", "Na base (P10) o hiato aumentou (+0,08 lp); no salário mínimo caiu pouco; no topo (P90) não mudou (B3)."),
        ("onda2_b4_efeitos_coorte.png", "Quem nasceu depois de 1990 tem hiato menor na mesma idade (25–34: 0,48 → 0,44 lp), sob restrição declarada (B4)."),
     ]),
    ("Quem fica de fora e a população inteira (Onda 1, Blocos S e T)", "Fichas S0–S1.5, T, T4.", [
        ("onda1_s1_hiato_por_populacao.png", "Contando todos os adultos (quem não tem renda entra com zero), o hiato é maior, sobretudo entre mulheres (S1)."),
        ("onda1_s14_margens_hiato.png", "Cerca de 9 em 10 partes do hiato por adulto vêm da renda por hora; entre mulheres, 15% vêm de estar menos ocupadas (S1.4)."),
        ("onda1_s15_selecao_no_tempo.png", "A desvantagem negra em estar ocupado com renda cresceu na crise de 2015–19 e voltou ao nível de 2012 (S1.5)."),
        ("onda1_t1_hiato_domiciliar_per_capita.png", "Renda domiciliar per capita: hiato de 99% (2012) para 82% (2025), população inteira (T1)."),
        ("onda1_t2_pobreza_meio_sm.png", "Abaixo de ½ salário mínimo per capita: 29% das pessoas negras e 15% das brancas em 2025 (T2)."),
        ("onda1_t4_topo_base_domiciliar.png", "Chance de estar entre os 10% mais ricos: ~1/4 da de pessoas brancas, sem mudança desde 2012 (T4)."),
     ]),
    ("Raça × gênero (Onda 2, Bloco C)", "Fichas C1–C6.", [
        ("onda2_c1_celulas_pct_homem_branco.png", "Entre ocupados, mulheres negras ganham 47% do que ganham homens brancos; entre todos os adultos, 32% (C1)."),
        ("onda2_c3_shapley_raca_genero.png", "Da distância homem branco − mulher negra entre ocupados, ~2/3 se associam a raça e ~1/3 a gênero (Shapley; C3)."),
        ("onda2_c4_penalidade_maternidade.png", "Ter filho de 0–5 anos: −16 p.p. na chance de ocupação com renda para mães negras, −14 para brancas (C4)."),
        ("onda2_c5_trabalho_domestico.png", "Trabalho doméstico: 14% das ocupadas negras, 8% das brancas — razão estável desde 2012 (C5)."),
     ]),
]


FONTE_ANUAL = ("Fonte: IBGE, PNAD Contínua anual (Visita 1; Visita 5 em 2020–21) e trimestral. Renda domiciliar per "
               "capita (VD5008). Elaboração própria.")


def secao_ondas(prs, n):
    A.slide_divisor(prs, "Leitura principal (Ondas 1 e 2)",
                    "Estudos com ficha, hipóteses escritas antes de rodar e IC design-based (docs/studies).")
    n += 1
    for titulo, nota, imgs in ONDAS:
        A.slide_subdivisor(prs, titulo)
        n += 1
        for arq, legenda in imgs:
            if not (A.IMG_DIR / arq).exists():
                continue
            anual = arq.startswith(("onda1_t", "onda2_c3"))
            _slide_outra(prs, {"tipo": "outra", "ramo": "—", "sub": titulo, "titulo": "", "subtitulo": nota or "",
                               "arquivo": arq, "legenda": legenda,
                               **({"fonte": FONTE_ANUAL} if anual else {})})
            n += 1
    return n


def secao_extremos(prs, manifesto, n):
    for sec in manifesto.get("extremos", []):
        A.slide_divisor(prs, sec["titulo"],
                        "Limiares calculados em 3 escopos NOVOS: Brasil inteiro / dentro de cada gênero / "
                        "dentro de cada raça×gênero. Snapshot do trimestre mais recente.")
        n += 1
        for folha in sec["folhas"]:
            A.slide_grafico(prs, folha)
            n += 1
    return n


def slide_tabela_crescimento(prs, n):
    s = A._slide(prs)
    A._txt(s, Inches(0.8), Inches(0.9), Inches(11.7), Inches(1.0),
           "Tabela de crescimento da renda por raça (2012 T1 → 2026 T2)", 26, A.ACENTO, bold=True)
    txt = ("Uma linha por folha de renda da árvore (181 linhas): renda média real Branca, Negra e Indígena "
           "no primeiro e no último trimestre, % de crescimento de cada raça, e os hiatos em R$ "
           "(Branca-Negra e Branca-Indígena) no início vs. no fim.\n\n"
           "Arquivo à parte (não cabe como slide legível):\n"
           "   •  docs/tabela_crescimento_renda.xlsx  (uma aba por item + aba 'Tudo')\n"
           "   •  docs/tabela_crescimento_renda.csv\n\n"
           "Leitura geral: quem cresceu mais (em %) — Negra em 71 folhas, Indígena em 56, Branca em 46 — "
           "mas a diferença Branca-Negra em R$ AUMENTOU em 92 das 181. O hiato relativo cai enquanto a "
           "distância absoluta sobe.")
    A._txt(s, Inches(0.9), Inches(2.1), Inches(11.5), Inches(4.6), txt, 14, A.TINTA_SECUNDARIA)
    A._txt(s, Inches(0.55), Inches(7.16), Inches(9.0), Inches(0.3), A.FONTE_PADRAO, 8, A.TINTA_MUTED)
    return n + 1


def secao_aprofundamentos(prs, manifesto, n):
    for sec in manifesto.get("aprofundamentos", []):
        A.slide_divisor(prs, sec["titulo"],
                        "Instabilidade de renda, retorno da escolaridade, "
                        "Capital×Interior, desocupação×escolaridade, formal×informal, salários mínimos, "
                        "Oaxaca-Blinder ano a ano, dupla desvantagem, projeção condicional (B6).")
        n += 1
        for folha in sec["folhas"]:
            A.slide_grafico(prs, folha)
            n += 1
    return n


def secao_outras(prs, n):
    A.slide_divisor(prs, "Outras análises",
                    "Análises complementares, fora da árvore. Nesta seção o título fica na própria "
                    "imagem.")
    n += 1
    for titulo, nota, imgs in OUTRAS:
        A.slide_subdivisor(prs, titulo)
        n += 1
        for arq, legenda in imgs:
            folha = {"tipo": "outra", "ramo": "—", "sub": titulo, "titulo": "",
                     "subtitulo": nota or "", "arquivo": arq, "legenda": legenda}
            _slide_outra(prs, folha)
            n += 1
    return n


def _slide_outra(prs, folha):
    """Como A.slide_grafico, mas sem caixa de título (a imagem já tem a sua) —
    imagem maior + legenda + fonte."""
    from pptx.util import Emu
    from PIL import Image
    s = A._slide(prs)
    if folha["subtitulo"]:
        A._txt(s, Inches(0.55), Inches(0.3), Inches(12.2), Inches(0.5),
               folha["subtitulo"], 11.5, A.TINTA_SECUNDARIA)
    caminho = A.IMG_DIR / folha["arquivo"]
    if caminho.exists():
        with Image.open(caminho) as im:
            prop = im.size[0] / im.size[1]
        max_w, max_h = Inches(12.4), Inches(5.7)
        if max_w / prop <= max_h:
            w, h = max_w, Emu(int(max_w / prop))
        else:
            h, w = max_h, Emu(int(max_h * prop))
        s.shapes.add_picture(str(caminho), Emu(int((A.LARGURA - w) / 2)), Inches(0.95), width=w, height=h)
    A._txt(s, Inches(0.7), Inches(6.75), Inches(11.9), Inches(0.5),
           folha["legenda"], 11.5, A.TINTA_SECUNDARIA, align=PP_ALIGN.CENTER, italic=True)
    A._txt(s, Inches(0.55), Inches(7.16), Inches(9.0), Inches(0.3), folha.get("fonte", A.FONTE_PADRAO), 8, A.TINTA_MUTED)


def main():
    manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    arvore = manifesto["arvore"]

    prs = Presentation()
    prs.slide_width, prs.slide_height = A.LARGURA, A.ALTURA
    A.slide_titulo(prs)
    A.slide_indice(prs, arvore)

    n = secao_ondas(prs, 2)
    for sec in arvore:
        n_val = sum(1 for f in sec["folhas"] if f["tipo"].startswith("valor"))
        n_hi = sum(1 for f in sec["folhas"] if f["tipo"].startswith("hiato"))
        A.slide_divisor(prs, f"{sec['item']}. {sec['titulo']}",
                        f"{n_val} de renda · {n_hi} de hiato · " + A.NOTA_ITEM.get(sec["item"], ""))
        n += 1
        ramo = None
        for folha in sec["folhas"]:
            br = A.ramo_branch(folha["ramo"])
            if br and br != ramo:
                A.slide_subdivisor(prs, f"{sec['titulo']} — {br}")
                n += 1
            ramo = br
            A.slide_grafico(prs, folha)
            n += 1

    n = secao_extremos(prs, manifesto, n)
    n = slide_tabela_crescimento(prs, n)
    n = secao_aprofundamentos(prs, manifesto, n)
    n = secao_outras(prs, n)

    prs.save(DESTINO)
    print(f"Deck final: {DESTINO.relative_to(REPO_ROOT)}  ·  {n} slides")


if __name__ == "__main__":
    main()
