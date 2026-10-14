"""Gráficos dos estudos da Onda 3 (Bloco D), no estilo do Hub (`graficos_fase1`). Cada gráfico corresponde a uma
afirmação permitida nas fichas `docs/studies/{D1,D8}`.

Uso:
    python -m src.processing.graficos_onda3
"""
from __future__ import annotations

import pandas as pd

from src.processing import graficos_fase1 as g

P = g.REPO_ROOT / "data" / "processed"
RODAPE = ("Fonte: IBGE, PNAD Contínua Trimestral. Ocupados 18+ com renda > 0; ln da renda real do trabalho "
          "principal. Elaboração própria.")
BLOCOS_GRAF = [("Instrução (VD3004)", "Instrução", "#2f6f9f"),
               ("Território (UF, urbano, tipo de área)", "Território", "#5fb3ab"),
               ("Ocupação (grupamento VD4011)", "Ocupação", "#d19a12"),
               ("Vínculo (posição, previdência)", "Vínculo", "#e39a74"),
               ("Horas habituais (ln)", "Horas", "#b97a98")]
COR_RESIDUO = "#8f8271"


def grafico_d1_contribuicoes() -> None:
    """D1: hiato bruto (Branca × Negra) repartido por Gelbach + parte não associada, nas duas janelas."""
    gb = pd.read_parquet(P / "d1_contribuicao_blocos.parquet")
    an = pd.read_parquet(P / "d1_aninhada.parquet")
    fig, ax = g._novo_eixo(figsize=(11, 4.6))
    janelas = [("2012", "2012"), ("2025T3-2026T2", "2025T3–2026T2")]
    for i, (per, rot) in enumerate(janelas):
        x = gb[(gb["periodo"] == per) & (gb["raca"] == "Negra") & (gb["metodo"] == "Gelbach")].set_index("bloco")
        a = an[(an["periodo"] == per) & (an["raca"] == "Negra")].set_index("especificacao")["hiato_condicional_lp"]
        bruto, resto = a["E0"], a["E8 + atividade"]
        esq = 0.0
        for bloco, nome, cor in BLOCOS_GRAF:
            v = x.loc[bloco, "contribuicao_lp"]
            ax.barh(i, v, left=esq, color=cor, label=nome if i == 0 else None)
            if v > 0.03:
                ax.text(esq + v / 2, i, f"{100 * v / bruto:.0f}%", ha="center", va="center", fontsize=9, color="white")
            esq += v
        outros = bruto - resto - esq  # idade, sexo e atividade (≈ 0)
        esq += outros
        ax.barh(i, resto, left=esq, color=COR_RESIDUO, hatch="//", edgecolor="white",
                label="Não associada às covariáveis" if i == 0 else None)
        ax.text(esq + resto / 2, i, f"{100 * resto / bruto:.0f}%", ha="center", va="center", fontsize=9, color="white")
        ax.text(bruto + 0.006, i, f"hiato {bruto:.2f} lp".replace(".", ","), va="center", fontsize=9,
                color=g.TINTA_SECUNDARIA)
    ax.set_yticks(range(len(janelas)))
    ax.set_yticklabels([r for _, r in janelas])
    ax.invert_yaxis()
    ax.set_xlim(0, 0.53)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.1f}".replace(".", ","))
    ax.grid(axis="x", color=g.GRADE, lw=0.8)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=6, frameon=False, fontsize=9)
    g._titulo(ax, "Instrução, lugar e ocupação pesam quase igual; a instrução perdeu peso",
              "Hiato Branca × Negra em log-pontos de renda, repartido por Gelbach (independe da ordem) · % do hiato")
    g._rodape(fig, RODAPE)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    g._salvar(fig, "onda3_d1_contribuicoes.png")


def grafico_d1_serie() -> None:
    """D1: hiato bruto, após idade/sexo/instrução e completo (E8), 2º trimestres 2012–2026, com IC 95%."""
    an = pd.read_parquet(P / "d1_aninhada.parquet")
    x = an[an["periodo"].str.match(r"^\d{4}T2$") & (an["raca"] == "Negra")].copy()
    x["data"] = pd.to_datetime(x["periodo"].str[:4] + "-04-01")
    fig, ax = g._novo_eixo(figsize=(11, 5.4))
    g.marcar_quebras(ax)
    for esp, rot, cor in (("E0", "Bruto", g.COR_NEGRA), ("E3 + instrucao", "Mesma idade, sexo e instrução", "#2f6f9f"),
                          ("E8 + atividade", "Mesmas características observáveis (E8)", COR_RESIDUO)):
        s = x[x["especificacao"] == esp].sort_values("data")
        ax.plot(s["data"], s["hiato_condicional_lp"], color=cor, lw=2, marker="o", ms=3.5, label=rot)
        ax.fill_between(s["data"], s["ic_inferior"], s["ic_superior"], color=cor, alpha=0.18, lw=0)
    ax.set_ylim(0, 0.52)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.1f}".replace(".", ","))
    ax.legend(loc="center", bbox_to_anchor=(0.5, 0.64), ncol=3, frameon=False, fontsize=9.5)
    g._titulo(ax, "O hiato bruto caiu em 2022; a parte não associada às covariáveis ficou parada",
              "Hiato Branca × Negra em log-pontos de renda (2º trimestres) · IC 95% design-based")
    g._rodape(fig, RODAPE)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda3_d1_serie_aninhada.png")


def main() -> None:
    grafico_d1_contribuicoes()
    grafico_d1_serie()


if __name__ == "__main__":
    main()
