"""Gráfico da Onda 5 (Bloco G), no estilo do Hub (`graficos_fase1`): event study do G1 (ficha `docs/studies/G1`).

Uso:
    python -m src.processing.graficos_onda5
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from src.processing import graficos_fase1 as g

P = g.REPO_ROOT / "data" / "processed"
RODAPE = ("Fonte: INEP, Censo da Educação Superior 2009–2023. 73 federais sem reserva própria × 40 estaduais/municipais. "
          "Elaboração própria.")


def _estilo(ax) -> None:
    ax.set_facecolor(g.SUPERFICIE)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(g.EIXO)
    ax.tick_params(axis="both", colors=g.TINTA_MUTED, labelsize=9.5, length=0)


def _paineis(n: int, figsize):
    fig, axs = plt.subplots(1, n, figsize=figsize, dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    return fig, axs


def _titulo_fig(fig, titulo: str, subtitulo: str) -> None:
    fig.text(0.01, 0.965, titulo, fontsize=14, fontweight="bold", color=g.TINTA_PRIMARIA, ha="left", va="top")
    fig.text(0.01, 0.905, subtitulo, fontsize=9.5, color=g.TINTA_SECUNDARIA, ha="left", va="top")


def grafico_g1_event_study() -> None:
    d = pd.read_parquet(P / "g1_cotas_federais.parquet")
    d = d[(d["especificacao"] == "principal") & d["periodo"].str.fullmatch(r"\d{4}")]
    fig, axs = _paineis(2, (11, 5.2))
    paineis = [(axs[0], [("Y1", "Entre quem declarou cor", g.COR_NEGRA),
                         ("Y1b", "Não declarados contados como negros", g.TINTA_MUTED)],
                "% de negros entre ingressantes"),
               (axs[1], [("Y3", "Sem cor/raça declarada", "#2f6f9f")], "% sem cor/raça declarada")]
    for ax, series, tit in paineis:
        _estilo(ax)
        ax.axvspan(2012.5, 2016.5, color=g.GRADE, alpha=0.5, lw=0)
        ax.axhline(0, color=g.EIXO, lw=1)
        for k, (y, rot, cor) in enumerate(series):
            s = d[d["desfecho"] == y].assign(ano=lambda x: x["periodo"].astype(int))
            s = pd.concat([s, pd.DataFrame({"ano": [2012], "estimativa": [0.0], "ic_inferior": [0.0],
                                            "ic_superior": [0.0]})]).sort_values("ano")
            desl = (k - (len(series) - 1) / 2) * 0.18
            ax.errorbar(s["ano"] + desl, s["estimativa"],
                        yerr=[s["estimativa"] - s["ic_inferior"], s["ic_superior"] - s["estimativa"]],
                        fmt="o-", color=cor, ms=4, lw=1.6, elinewidth=1, capsize=0, label=rot)
        ax.set_title(tit, fontsize=11, color=g.TINTA_PRIMARIA, loc="left")
        ax.set_xticks(range(2009, 2024, 2))
        ax.grid(axis="y", color=g.GRADE, lw=0.8)
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:+.0f}".replace("-", "−"))
        ax.text(2014.5, 0.98, "implantação\nda lei", transform=ax.get_xaxis_transform(), ha="center", va="top",
                fontsize=8, color=g.TINTA_MUTED)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.5, 0.035), ncol=2, frameon=False, fontsize=9)
    _titulo_fig(fig, "A proporção de negros sobe junto com o registro de cor — não dá para separar os dois",
                "Federais tratadas menos controles, em p.p., relativo a 2012 · IC 95% (CR1 por instituição)")
    g._rodape(fig, RODAPE)
    fig.tight_layout(rect=(0, 0.08, 1, 0.87))
    g._salvar(fig, "onda5_g1_event_study.png")


def main() -> None:
    grafico_g1_event_study()


if __name__ == "__main__":
    main()
