"""Deck final da reconstrução — junta:
  1. Árvore cruzada de renda por raça (itens 1-10) — `manifesto['arvore']`
  2. Topo 10% / base 10% / quartis com limiares novos — `manifesto['extremos']`
  3. Ponteiro pra tabela de crescimento (arquivo à parte)
  4. "Outras análises" — o que já existia e NÃO é coberto pela árvore (sem Preta/Parda)

Nos blocos 1-2 o texto (título/subtítulo/legenda/fonte) é CAIXA DE TEXTO e a imagem é
crua. No bloco 4 as imagens antigas ainda trazem o título rasterizado (regerar as ~35
como figura crua fica pra uma passada futura) — o slide só acrescenta legenda + fonte.

Substitui `docs/Datahub_Racial_Brasil_Fase1.pptx`.

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
# Cada mudança pedida gera uma versão nova (decisão do usuário) — não sobrescreve o
# Datahub_Racial_Brasil_Fase1.pptx original.
VERSAO = "v7"
DESTINO = REPO_ROOT / "docs" / f"Datahub_Racial_Brasil_Fase1_{VERSAO}.pptx"

# ---- "Outras análises": curadoria do que continua (sem Preta/Parda, sem o que a
# árvore já cobre). (título da seção, nota, [(arquivo, legenda), ...]) ---------- #
OUTRAS = [
    # (a "Hiato Branca vs. Negra — série histórica" saiu daqui: a árvore agora traz a
    #  série de hiato — com Indígena — nos itens 1-8.)
    ("É ocupação, ou é cor da pele? — decomposição do hiato",
     "Quanto idade, escolaridade e ocupação explicam do hiato Branca vs. Negra.", [
        ("decomposicao_hiato_ocupacional.png", "Padronização direta: 67% bruto → 30% (+escolaridade) → 24% (+ocupação, residual). Ocupação sozinha: 33%."),
        ("oaxaca_blinder_decomposicao.png", "Regressão (Oaxaca-Blinder) com teste de significância: resíduo +22% (p<0,001)."),
        ("oaxaca_blinder_quantis.png", "O resíduo não é uniforme: ~15% na mediana, ~31% na base (piso pegajoso), ~36% no topo (teto de vidro)."),
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
        ("hiato_racial_por_regiao.png", "O hiato varia MUITO por região: ~65-85% no Sudeste vs. ~45-55% no Sul."),
        ("segregacao_ocupacional.png", "Duncan: ~17% de um grupo precisaria trocar de categoria ocupacional pra igualar o outro."),
        ("hiato_quebra_estrutural.png", "Teste tipo Chow: mudança de patamar/inclinação significativa nos 3 eventos testados."),
    ]),
    ("Novas variáveis da PNAD", "Informalidade, jornada, alfabetização, desalento.", [
        ("informalidade_carteira_assinada.png", "% com carteira: Branca 72%, Negra 63%, Indígena 52% (2026 T2)."),
        ("renda_por_hora.png", "O hiato sobrevive quase intacto na renda POR HORA — não é jornada, é remuneração."),
        ("alfabetizacao_60mais.png", "60+ anos: Branca 93%, Negra 80%, Indígena 72% alfabetizados."),
        ("desalento.png", "Fora da força de trabalho, Negra e Indígena desistem de procurar emprego a taxas 2-4x a de Branca."),
    ]),
    ("Topo 10% — limiar DENTRO de cada raça (série histórica)",
     "Complementa a Fase D (limiares Brasil / gênero / raça×gênero): aqui o P90 é calculado dentro de cada raça, 2012–2026.", [
        ("topo10_genero.png", "% de mulheres no topo 10% de cada raça."),
        ("topo10_escolaridade.png", "% com Superior completo no topo 10% — negros 38%→58%, brancos ~83%."),
        ("topo10_escolaridade_composicao.png", "Distribuição pelos 7 níveis — o topo negro tem mais Médio completo (23%) que o branco (10%)."),
        ("topo10_faixa_etaria.png", "Composição por faixa etária do topo 10%."),
        ("topo10_geracao.png", "Composição por geração — topo negro pende a Millennial/Z; branco a Boomer/X."),
    ]),
    ("4 quartis — limiar DENTRO de cada raça (série histórica)",
     "Complementa a Fase D: P25/P50/P75 dentro de cada raça, 2012–2026.", [
        ("quartis_genero.png", "% de mulheres por quartil — maioria entre as mais pobres nas duas raças."),
        ("quartis_escolaridade.png", "% com Superior completo cresce em todo quartil, mas o hiato se abre no Q4 (~72% vs. ~40%)."),
        ("quartis_escolaridade_composicao.png", "Distribuição pelos 7 níveis, um painel por quartil."),
        ("quartis_faixa_etaria.png", "Composição por faixa etária, um painel por quartil."),
        ("quartis_geracao.png", "Composição por geração, um painel por quartil."),
    ]),
    ("Desigualdade interna, setor público/privado, sobre-qualificação", None, [
        ("gini_por_raca.png", "Gini DENTRO de cada raça — Branca tem mais desigualdade interna (distribuição mais comprimida na base)."),
        ("theil_decomposicao.png", "Só ~7% da desigualdade total do Brasil vem de diferença ENTRE raças — 93% é dentro de cada uma."),
        ("hiato_setor_publico_privado.png", "Hiato menor no Público (~45-50%) que no Privado (~58-65%)."),
        ("segregacao_setorial.png", "Segregação por setor (10%) < por ocupação (17%)."),
        ("sobrequalificacao.png", "Negros com Superior completo em ocupação elementar: quase o dobro da taxa de brancos."),
    ]),
    ("A função quantil da renda em R$, e sua inversa", None, [
        ("funcao_quantil_racial.png", "Em R$: P10 R$1.500 vs R$720; P50 R$3.000 vs R$2.000; P90 R$10.000 vs R$5.000."),
        ("hiato_por_percentil.png", "O hiato bruto por percentil não é uniforme — maior na base (108% no P10) e no topo (100% no P90)."),
        ("percentil_de_valor_racial.png", "R$3.000 = P57 entre brancos (meio), mas P76 entre negros (quase o topo)."),
    ]),
]


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
                        "Rodada 'sugestões novas': instabilidade de renda, retorno da escolaridade, "
                        "Capital×Interior, desocupação×escolaridade, formal×informal, salários mínimos, "
                        "Oaxaca-Blinder ano a ano, dupla desvantagem, projeção de convergência.")
        n += 1
        for folha in sec["folhas"]:
            A.slide_grafico(prs, folha)
            n += 1
    return n


def secao_outras(prs, n):
    A.slide_divisor(prs, "Outras análises",
                    "O que já existia e não é coberto pela árvore. Nesta seção o título fica na própria "
                    "imagem (gráficos de rodadas anteriores).")
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
    A._txt(s, Inches(0.55), Inches(7.16), Inches(9.0), Inches(0.3), A.FONTE_PADRAO, 8, A.TINTA_MUTED)


def main():
    manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    arvore = manifesto["arvore"]

    prs = Presentation()
    prs.slide_width, prs.slide_height = A.LARGURA, A.ALTURA
    A.slide_titulo(prs)
    A.slide_indice(prs, arvore)

    n = 2
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
