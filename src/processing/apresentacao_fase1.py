"""Gera a apresentação em PowerPoint da Fase 1, com todos os gráficos de
docs/img/ organizados por seção (mesma estrutura de docs/ANALISE_FASE1.md).

Uso:
    python -m src.processing.apresentacao_fase1
"""
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

REPO_ROOT = Path(__file__).resolve().parents[2]
IMG_DIR = REPO_ROOT / "docs" / "img"
DESTINO = REPO_ROOT / "docs" / "Datahub_Racial_Brasil_Fase1.pptx"

LARGURA_SLIDE = Inches(13.333)
ALTURA_SLIDE = Inches(7.5)

SUPERFICIE = RGBColor(0xFC, 0xFC, 0xFB)
TINTA_PRIMARIA = RGBColor(0x0B, 0x0B, 0x0B)
TINTA_SECUNDARIA = RGBColor(0x52, 0x51, 0x4E)
COR_BRANCA = RGBColor(0x2A, 0x78, 0xD6)

# (título da seção, nota de rodapé opcional, [(arquivo, legenda), ...])
SECOES = [
    ("Raça", None, [
        ("renda_por_raca.png", "Hiato grande e persistente entre Branca e Negra/Indígena; estreitamento leve 2012→2026."),
        ("renda_preta_parda.png", "Preta e Parda andam próximas, com Parda ultrapassando levemente nos últimos anos."),
    ]),
    ("Hiato Branca vs. Negra — série histórica", "Com teste de significância (Welch, IC 95%)", [
        ("hiato_racial_percentual.png", "Hiato relativo caiu de ~76% para ~66% — todos os 58 trimestres são estatisticamente significativos."),
        ("hiato_racial_absoluto.png", "Em R$, o hiato disparou na pandemia (pico ~R$2.035) antes de recuar."),
    ]),
    ("É ocupação, ou é cor da pele?", "Decomposição: quanto idade, escolaridade e ocupação explicam do hiato", [
        ("decomposicao_hiato_ocupacional.png", "Hiato bruto 67% → 64% (só idade) → 30% (+escolaridade) → 24% (+ocupação, residual)."),
    ]),
    ("Raça × Gênero", "Combinado + um por gênero", [
        ("renda_por_raca_genero.png", "O hiato de gênero soma ao de raça, não substitui."),
        ("renda_por_raca_homens.png", "Recorte só Homens."),
        ("renda_por_raca_mulheres.png", "Recorte só Mulheres."),
    ]),
    ("Preta × Parda × Gênero", "Combinado + um por gênero", [
        ("renda_preta_parda_genero.png", "Preta e Parda por gênero — quatro linhas, mesmo padrão de proximidade."),
        ("renda_preta_parda_homens.png", "Recorte só Homens."),
        ("renda_preta_parda_mulheres.png", "Recorte só Mulheres."),
    ]),
    ("Raça × Faixa etária", "Combinado + um por faixa etária", [
        ("renda_por_raca_faixa_etaria.png", "Hiato racial se abre na faixa de maior potencial de renda (40-59 anos)."),
        ("renda_por_raca_faixa_14_17.png", "14-17 anos."),
        ("renda_por_raca_faixa_18_24.png", "18-24 anos."),
        ("renda_por_raca_faixa_25_39.png", "25-39 anos."),
        ("renda_por_raca_faixa_40_59.png", "40-59 anos — maior hiato."),
        ("renda_por_raca_faixa_60mais.png", "60+ anos."),
    ]),
    ("Preta × Parda × Faixa etária", "Combinado + uma por faixa etária", [
        ("renda_preta_parda_faixa_etaria.png", "Preta vs. Parda por faixa etária, snapshot mais recente."),
        ("renda_preta_parda_faixa_14_17.png", "14-17 anos."),
        ("renda_preta_parda_faixa_18_24.png", "18-24 anos."),
        ("renda_preta_parda_faixa_25_39.png", "25-39 anos."),
        ("renda_preta_parda_faixa_40_59.png", "40-59 anos."),
        ("renda_preta_parda_faixa_60mais.png", "60+ anos."),
    ]),
    ("Raça × Escolaridade", "O achado central da Fase 1", [
        ("renda_por_raca_escolaridade.png", "O hiato racial SOBREVIVE ao controle por escolaridade — abre no Superior completo."),
        ("renda_por_raca_escolaridade_sem_instrucao.png", "Sem instrução."),
        ("renda_por_raca_escolaridade_fundamental_incompl.png", "Fundamental incompleto."),
        ("renda_por_raca_escolaridade_fundamental_compl.png", "Fundamental completo."),
        ("renda_por_raca_escolaridade_medio_incompl.png", "Médio incompleto."),
        ("renda_por_raca_escolaridade_medio_compl.png", "Médio completo."),
        ("renda_por_raca_escolaridade_superior_incompl.png", "Superior incompleto."),
        ("renda_por_raca_escolaridade_superior_compl.png", "Superior completo — maior hiato de todos."),
    ]),
    ("Preta × Parda × Escolaridade", "Combinado + um por nível", [
        ("renda_preta_parda_escolaridade.png", "Preta vs. Parda por nível de instrução, snapshot mais recente."),
        ("renda_preta_parda_escolaridade_sem_instrucao.png", "Sem instrução."),
        ("renda_preta_parda_escolaridade_fundamental_incompl.png", "Fundamental incompleto."),
        ("renda_preta_parda_escolaridade_fundamental_compl.png", "Fundamental completo."),
        ("renda_preta_parda_escolaridade_medio_incompl.png", "Médio incompleto."),
        ("renda_preta_parda_escolaridade_medio_compl.png", "Médio completo."),
        ("renda_preta_parda_escolaridade_superior_incompl.png", "Superior incompleto."),
        ("renda_preta_parda_escolaridade_superior_compl.png", "Superior completo."),
    ]),
    ("Raça × Gênero × Escolaridade", None, [
        ("renda_por_raca_escolaridade_homens.png", "Hiato no Superior completo é maior entre homens (~46%)."),
        ("renda_por_raca_escolaridade_mulheres.png", "...do que entre mulheres (~36%)."),
    ]),
    ("Raça × Gênero × Faixa etária", None, [
        ("renda_por_faixa_etaria_raca_genero.png", "Mesmo efeito de abertura em 40-59 anos, visível nos dois gêneros."),
    ]),
    ("Escolaridade × Raça × Gênero", None, [
        ("escolaridade_por_raca_genero.png", "Conclusão do superior: hiato racial >2x; mulheres à frente dos homens em todos os grupos."),
    ]),
    ("Todas as dimensões de uma vez", "Raça × Gênero × Faixa etária × Escolaridade", [
        ("renda_completa_heatmap.png", "Seis painéis (raça×gênero), faixa etária × nível de instrução em cada um — o padrão racial se mantém."),
    ]),
]


def _slide_em_branco(prs: Presentation):
    layout_em_branco = prs.slide_layouts[6]
    return prs.slides.add_slide(layout_em_branco)


def _fundo(slide):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = SUPERFICIE


def slide_titulo(prs: Presentation) -> None:
    slide = _slide_em_branco(prs)
    _fundo(slide)
    caixa = slide.shapes.add_textbox(Inches(0.8), Inches(2.6), Inches(11.7), Inches(2))
    tf = caixa.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Datahub de Análise Racial no Brasil"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = TINTA_PRIMARIA

    p2 = tf.add_paragraph()
    p2.text = "Fase 1 — PNAD Contínua (2012–2026) · Análise exploratória"
    p2.font.size = Pt(20)
    p2.font.color.rgb = TINTA_SECUNDARIA
    p2.space_before = Pt(12)

    p3 = tf.add_paragraph()
    p3.text = "Fonte: IBGE, PNAD Contínua Trimestral (microdados). Elaboração própria."
    p3.font.size = Pt(13)
    p3.font.color.rgb = TINTA_SECUNDARIA
    p3.space_before = Pt(24)


def slide_secao(prs: Presentation, titulo: str, nota: str | None) -> None:
    slide = _slide_em_branco(prs)
    _fundo(slide)
    caixa = slide.shapes.add_textbox(Inches(0.8), Inches(3.1), Inches(11.7), Inches(1.5))
    tf = caixa.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = titulo
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COR_BRANCA
    if nota:
        p2 = tf.add_paragraph()
        p2.text = nota
        p2.font.size = Pt(16)
        p2.font.color.rgb = TINTA_SECUNDARIA
        p2.space_before = Pt(10)


def slide_grafico(prs: Presentation, arquivo: str, legenda: str) -> None:
    caminho = IMG_DIR / arquivo
    if not caminho.exists():
        print(f"  aviso: {arquivo} não encontrado, pulando slide")
        return
    slide = _slide_em_branco(prs)
    _fundo(slide)

    # imagem ocupa a maior parte do slide, centralizada, com margem pra legenda embaixo
    from PIL import Image
    with Image.open(caminho) as im:
        largura_px, altura_px = im.size
    proporcao = largura_px / altura_px

    max_largura = Inches(12.3)
    max_altura = Inches(6.1)
    if max_largura / proporcao <= max_altura:
        largura = max_largura
        altura = Emu(int(max_largura / proporcao))
    else:
        altura = max_altura
        largura = Emu(int(max_altura * proporcao))

    left = Emu(int((LARGURA_SLIDE - largura) / 2))
    top = Inches(0.35)
    slide.shapes.add_picture(str(caminho), left, top, width=largura, height=altura)

    caixa = slide.shapes.add_textbox(Inches(0.6), Inches(6.65), Inches(12.1), Inches(0.7))
    tf = caixa.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = legenda
    p.font.size = Pt(14)
    p.font.color.rgb = TINTA_SECUNDARIA
    p.alignment = PP_ALIGN.CENTER


def main() -> None:
    prs = Presentation()
    prs.slide_width = LARGURA_SLIDE
    prs.slide_height = ALTURA_SLIDE

    slide_titulo(prs)

    total_graficos = 0
    for titulo_secao, nota, graficos in SECOES:
        slide_secao(prs, titulo_secao, nota)
        for arquivo, legenda in graficos:
            slide_grafico(prs, arquivo, legenda)
            total_graficos += 1

    prs.save(DESTINO)
    total_slides = 1 + len(SECOES) + total_graficos
    print(f"Apresentação salva em: {DESTINO.relative_to(REPO_ROOT)}")
    print(f"Slides: {total_slides} ({total_graficos} gráficos + {len(SECOES)} divisores + 1 título)")


if __name__ == "__main__":
    main()
