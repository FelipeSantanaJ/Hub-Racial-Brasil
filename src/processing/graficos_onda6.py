"""Gráficos dos estudos da Onda 6 (integração), no estilo do Hub (`graficos_fase1`). Cada gráfico corresponde a uma
afirmação permitida nas fichas `docs/studies/{D4.4,I1,H3.4,H4.2}`.

Uso:
    python -m src.processing.graficos_onda6
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.processing import graficos_fase1 as g
from src.processing.graficos_onda4 import COR_BRUTO, COR_CONDICIONAL, _fmt, _paineis, _titulo_fig

P = g.REPO_ROOT / "data" / "processed"
FONTES = {
    "d44": "Fonte: IBGE, Censo 2022, Agregados por setores censitários (universo). Elaboração própria.",
    "i1": "Fonte: IBGE, Censo 2022 (amostra, acesso público) e PNAD Contínua 2022T3. Ocupados de 20+. Elaboração própria.",
    "h34": "Fonte: IBGE, POF 2017–2018. Moradia própria quitada pelo aluguel estimado. Elaboração própria.",
    "h42": "Fonte: IBGE, PNAD Contínua 2012–2026, pares de trimestres consecutivos (18+). Elaboração própria.",
}
COR_CENSO = "#2f6f9f"
COR_PNADC = g.TINTA_MUTED


def grafico_d44() -> None:
    d = pd.read_parquet(P / "d44_segregacao_residencial.parquet")
    d = d[(d["amostra"] == "todos os setores") & (d["comparacao"] == "Branca × Negra")]
    recortes = ["capitais", "≥ 500 mil (não capital)", "100–500 mil", "< 100 mil", "Brasil"]
    rot = ["Capitais", "≥ 500 mil\n(não capital)", "100–500 mil", "< 100 mil", "Todos os\nmunicípios"]
    med_d = "Duncan D dentro do município (média ponderada)"
    med_r = "renda do setor: branca ÷ grupo 2 − 1, dentro do município (%)"
    fig, axs = _paineis(2, (11, 5.0))
    for ax, med, tit, fmt, alea in ((axs[0], med_d, "Separação entre setores (dissimilaridade, 0 a 1)", lambda v: _fmt(v, 2), True),
                                    (axs[1], med_r, "Renda do setor de brancos sobre a de negros (%)", lambda v: f"+{_fmt(v)}%", False)):
        s = d[d["medida"] == med].set_index("recorte").loc[recortes]
        cores = [COR_CONDICIONAL] * 4 + [g.TINTA_SECUNDARIA]
        ax.bar(range(5), s["valor"], 0.6, color=cores)
        if alea:
            ax.scatter(range(5), s["valor_aleatorio"], marker="_", s=400, color=g.TINTA_PRIMARIA, zorder=3,
                       label="esperado por acaso")
            ax.legend(loc="upper right", frameon=False, fontsize=8.5)
        for x, v in enumerate(s["valor"]):
            ax.text(x, v * 1.02 + (0.004 if alea else 1), fmt(v), ha="center", fontsize=9, color=g.TINTA_SECUNDARIA)
        ax.set_xticks(range(5))
        ax.set_xticklabels(rot, fontsize=9)
        ax.set_title(tit, fontsize=10.5, color=g.TINTA_PRIMARIA, loc="left")
        ax.grid(axis="y", color=g.GRADE, lw=0.8)
        ax.yaxis.set_major_formatter(lambda v, _, a=alea: _fmt(v, 1) if a else f"{v:.0f}%")
    axs[0].set_ylim(0, 0.34)
    axs[0].set_yticks(np.arange(0, 0.31, 0.1))
    axs[1].set_ylim(0, 82)
    _titulo_fig(fig, "Nas capitais, negros moram em setores mais separados e mais pobres que brancos",
                "Branca × Negra (preta + parda), comparando setores censitários dentro do mesmo município")
    g._rodape(fig, FONTES["d44"])
    fig.tight_layout(rect=(0, 0.03, 1, 0.87))
    g._salvar(fig, "onda6_d44_segregacao_renda_setor.png")


def grafico_i1() -> None:
    d = pd.read_parquet(P / "i1_censo_pnadc.parquet")
    d = d[(d["especificacao"] == "principal") & (d["uf"] == "Brasil")]
    comps = ["Branca × Negra", "Branca × Preta", "Branca × Parda", "Branca × Indígena"]
    fig, ax = g._novo_eixo(figsize=(11, 4.8))
    for k, (fonte, cor) in enumerate((("Censo 2022", COR_CENSO), ("PNADC 2022T3", COR_PNADC))):
        s = d[(d["fonte"] == fonte)].set_index("medida").loc[[f"{c}: razão das médias − 1 (%)" for c in comps]]
        y = np.arange(len(comps)) + (k - 0.5) * 0.36
        ax.barh(y, s["estimativa"], 0.34, color=cor, label=fonte)
        ax.errorbar(s["estimativa"], y, xerr=[s["estimativa"] - s["ic_inferior"], s["ic_superior"] - s["estimativa"]],
                    fmt="none", ecolor=g.TINTA_SECUNDARIA, elinewidth=1, capsize=2)
        for yy, v, hi in zip(y, s["estimativa"], s["ic_superior"]):
            ax.text(hi + 1.5, yy, f"+{_fmt(v)}%", va="center", fontsize=9, color=cor)
    ax.set_yticks(range(len(comps)))
    ax.set_yticklabels(comps)
    ax.invert_yaxis()
    ax.set_xlim(0, 135)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="x", color=g.GRADE, lw=0.8)
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    g._titulo(ax, "O Censo confirma o hiato da PNADC e mostra um hiato indígena muito maior",
              "Quanto a renda média de todos os trabalhos de brancos supera a do grupo (%) · Brasil, 2022 · IC 95%")
    g._rodape(fig, FONTES["i1"])
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda6_i1_censo_pnadc.png")


def grafico_h34() -> None:
    d = pd.read_parquet(P / "h34_riqueza_imobiliaria.parquet")
    d = d[d["especificacao"].str.startswith("principal")]
    linhas = []
    for grupo in ("Negra", "Indígena"):
        r = f"Branca ÷ {grupo}"
        linhas += [(r, "Renda disponível per capita", d[(d["raca"] == r) & (d["medida"] == "razão das rendas disponíveis per capita")].iloc[0], COR_BRUTO),
                   (r, "Moradia própria (cap rate uniforme)", d[(d["raca"] == r) & (d["cap_rate"] == "5% a.a.") & (d["medida"] == "razão das riquezas imobiliárias médias")].iloc[0], COR_CONDICIONAL),
                   (r, "Moradia própria (cap rate 6% → 4%)", d[(d["raca"] == r) & (d["cap_rate"] == "variável (6% → 4%)") & (d["medida"] == "razão das riquezas imobiliárias médias")].iloc[0], "#5fb3ab")]
    fig, ax = g._novo_eixo(figsize=(11, 4.8))
    ys, rots = [], []
    for i, (r, nome, s, cor) in enumerate(linhas):
        y = i + (1 if i >= 3 else 0)
        ax.errorbar(s["estimativa"], y, xerr=[[s["estimativa"] - s["ic_inferior"]], [s["ic_superior"] - s["estimativa"]]],
                    fmt="o", color=cor, ms=7, elinewidth=2)
        ax.text(s["ic_superior"] + 0.03, y, _fmt(s["estimativa"], 2) + "×", va="center", fontsize=9, color=cor)
        ys.append(y)
        rots.append(f"{nome}")
    ax.axvline(1, color=g.EIXO, lw=1)
    ax.set_yticks(ys)
    ax.set_yticklabels(rots, fontsize=9)
    ax.text(0.99, 1.0, "Brancos ÷ negros", transform=ax.get_yaxis_transform(), fontsize=9.5, color=g.TINTA_PRIMARIA,
            va="center", ha="left")
    ax.text(0.99, 5.0, "Brancos ÷ indígenas", transform=ax.get_yaxis_transform(), fontsize=9.5, color=g.TINTA_PRIMARIA,
            va="center", ha="left")
    ax.invert_yaxis()
    ax.set_xlim(0.9, 2.9)
    ax.set_xticks(np.arange(1.0, 2.81, 0.2))
    ax.xaxis.set_major_formatter(lambda v, _: _fmt(v, 1) + "×")
    ax.grid(axis="x", color=g.GRADE, lw=0.8)
    g._titulo(ax, "A diferença no valor da moradia própria é maior que a diferença de renda",
              "Razão entre médias por pessoa (brancos ÷ grupo) · moradia própria quitada · IC 95%")
    g._rodape(fig, FONTES["h34"])
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda6_h34_riqueza_imobiliaria.png")


def grafico_h42() -> None:
    d = pd.read_parquet(P / "h42_transicoes.parquet")
    d = d[(d["periodo"] == "2012–2026") & (d["pesos"] == "V1028 de t") & (d["raca"] == "Negra − Branca")]
    trans = list(dict.fromkeys(d["transicao"]))
    rot = ["Desocupado → ocupado", "Sem carteira → com carteira", "Com carteira → perde a carteira\nou o emprego"]
    fig, ax = g._novo_eixo(figsize=(11, 4.6))
    for k, (med, nome, cor) in enumerate((("diferença bruta (p.p.)", "Bruta", COR_BRUTO),
                                          ("diferença com idade, sexo, instrução, UF e ano (p.p.)",
                                           "Mesma idade, sexo, instrução, UF e ano", COR_CONDICIONAL))):
        s = d[d["medida"] == med].set_index("transicao").loc[trans]
        y = np.arange(len(trans)) + (k - 0.5) * 0.36
        ax.barh(y, s["estimativa"], 0.34, color=cor, label=nome)
        ax.errorbar(s["estimativa"], y, xerr=[s["estimativa"] - s["ic_inferior"], s["ic_superior"] - s["estimativa"]],
                    fmt="none", ecolor=g.TINTA_SECUNDARIA, elinewidth=1, capsize=2)
        for yy, v, lo, hi in zip(y, s["estimativa"], s["ic_inferior"], s["ic_superior"]):
            ax.text(hi + 0.08 if v >= 0 else lo - 0.08, yy, _fmt(v, 1), va="center", ha="left" if v >= 0 else "right",
                    fontsize=9, color=cor)
    ax.axvline(0, color=g.EIXO, lw=1)
    ax.set_yticks(range(len(trans)))
    ax.set_yticklabels(rot, fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlim(-3.8, 2.2)
    ax.xaxis.set_major_formatter(lambda v, _: _fmt(v))
    ax.grid(axis="x", color=g.GRADE, lw=0.8)
    ax.legend(loc="lower left", frameon=False, fontsize=9)
    g._titulo(ax, "Com as mesmas características, as diferenças na carteira quase somem",
              "Probabilidade de transição de um trimestre ao seguinte: negros menos brancos (p.p.) · 2012–2026 · IC 95%")
    g._rodape(fig, FONTES["h42"])
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda6_h42_transicoes.png")


def main() -> None:
    grafico_d44()
    grafico_i1()
    grafico_h34()
    grafico_h42()


if __name__ == "__main__":
    main()
