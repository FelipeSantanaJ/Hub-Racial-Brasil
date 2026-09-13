"""Gráficos do desenho causal preliminar (Leis de Cotas) — ver
`src/processing/analise_causal_cotas.py` pro método e `docs/ANALISE_CAUSAL_COTAS.md`
pro texto completo. Dois tipos de gráfico:

- Event-study (Desenho B): coeficiente por trimestre relativo à Lei 12.990/2014, com
  banda de IC 95% e linha vertical marcando a lei.
- Coorte de exposição (Desenho A): % Superior completo por coorte de nascimento, com
  linha vertical no limiar de exposição à Lei 12.711/2012.

Uso:
    python -m src.processing.graficos_causal_cotas
"""
from pathlib import Path

import pandas as pd

from src.processing.graficos_fase1 import (
    COR_BRANCA, COR_NEGRA, COR_INDIGENA, COR_PRETA, COR_PARDA,
    SUPERFICIE, TINTA_PRIMARIA, TINTA_SECUNDARIA, TINTA_MUTED, GRADE, EIXO,
    _novo_eixo, _titulo, _rodape, _salvar, _slug, OUTPUT_DIR,
)
from src.processing.agregacoes_pnadc import OUTPUT_DIR as DADOS_DIR
from src.processing.analise_causal_cotas import _limiar_nascimento, ANO_LEI_UNIVERSITARIA

CORES_RACA_TRATADO = {"Negra": COR_NEGRA, "Indígena": COR_INDIGENA, "Preta": COR_PRETA, "Parda": COR_PARDA}


def grafico_event_study(curva: pd.DataFrame, titulo: str, subtitulo: str, nome_arquivo: str, cor: str) -> Path:
    """Coeficiente do event-study (diferença-em-diferenças, público vs. privado, cada
    trimestre relativo contra o trimestre -1) com banda de IC 95% e linha vertical
    marcando o início da vigência da lei (entre os trimestres -1 e 0)."""
    fig, ax = _novo_eixo(figsize=(10, 5.5))
    ax.axhline(0, color=EIXO, linewidth=1, zorder=1)
    ax.axvline(-0.5, color=TINTA_MUTED, linewidth=1.3, linestyle="--", zorder=2)

    ax.fill_between(curva["relative_quarter"], curva["ic_inferior"], curva["ic_superior"],
                     color=cor, alpha=0.18, zorder=2)
    ax.plot(curva["relative_quarter"], curva["coef"], color=cor, linewidth=2,
            marker="o", markersize=4.5, zorder=3)

    ymin, ymax = ax.get_ylim()
    ax.text(-0.5, ymax, " Lei entra em vigor", color=TINTA_SECUNDARIA, fontsize=8.5,
            ha="left", va="top", rotation=90, alpha=0.85)

    ax.set_xlabel("Trimestres em relação à lei (0 = 1º trimestre pós-lei)", fontsize=9.5, color=TINTA_SECUNDARIA)
    ax.yaxis.grid(True, color=GRADE, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    _titulo(ax, titulo, subtitulo)
    _rodape(fig)
    return _salvar(fig, nome_arquivo)


def grafico_cohortes_did(
    painel: pd.DataFrame, raca_tratado: str, ano_lei: int, titulo: str, subtitulo: str, nome_arquivo: str,
) -> Path:
    """% Superior completo por coorte de nascimento (medido sempre aos 25-29 anos),
    Branca vs. `raca_tratado`, com linha vertical no limiar de nascimento equivalente à
    exposição à lei (quem nasceu depois tinha <=18 anos quando a cota passou a valer)."""
    limiar = _limiar_nascimento(ano_lei)
    d = painel[painel["raca_cor"].isin(["Branca", raca_tratado])].sort_values("ano_nascimento")
    cor_tratado = CORES_RACA_TRATADO.get(raca_tratado, COR_NEGRA)

    fig, ax = _novo_eixo(figsize=(10, 5.5))
    ax.axvspan(limiar, limiar + 4, color=GRADE, alpha=0.6, zorder=0)
    ax.axvline(limiar, color=TINTA_MUTED, linewidth=1.3, linestyle="--", zorder=2)

    for raca, cor in [("Branca", COR_BRANCA), (raca_tratado, cor_tratado)]:
        sub = d[d["raca_cor"] == raca]
        ax.plot(sub["ano_nascimento"], sub["pct_superior"], color=cor, linewidth=2.2,
                marker="o", markersize=4, zorder=3, label=raca)

    ymax = ax.get_ylim()[1]
    ax.text(limiar, ymax, f" nasceu em {limiar}+: acesso à cota desde a entrada na universidade  ",
            color=TINTA_SECUNDARIA, fontsize=8, ha="left", va="top", rotation=90, alpha=0.85)

    ax.set_xlabel("Ano de nascimento (coorte)", fontsize=9.5, color=TINTA_SECUNDARIA)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.yaxis.grid(True, color=GRADE, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5, labelcolor=TINTA_PRIMARIA)
    _titulo(ax, titulo, subtitulo)
    _rodape(fig)
    return _salvar(fig, nome_arquivo)


def main() -> None:
    painel = pd.read_parquet(DADOS_DIR / "painel_cohortes_superior_completo.parquet")
    grafico_cohortes_did(
        painel, "Negra", ANO_LEI_UNIVERSITARIA,
        "Lei de Cotas Universitárias: % Superior completo por coorte",
        "Branca vs. Negra, medido aos 25-29 anos · linha tracejada = 1º ano de nascimento exposto à lei",
        "causal_cohortes_universitaria_negra.png",
    )
    grafico_cohortes_did(
        painel, "Indígena", ANO_LEI_UNIVERSITARIA,
        "Lei de Cotas Universitárias: % Superior completo por coorte",
        "Branca vs. Indígena, medido aos 25-29 anos · linha tracejada = 1º ano de nascimento exposto à lei",
        "causal_cohortes_universitaria_indigena.png",
    )

    curvas = pd.read_parquet(DADOS_DIR / "did_cotas_servico_publico_curvas.parquet")
    for raca in ["Negra", "Indígena", "Preta", "Parda"]:
        curva = curvas[(curvas["raca_cor"] == raca) & (curvas["outcome"] == "participacao")]
        grafico_event_study(
            curva,
            f"Lei de Cotas no Serviço Público: participação de {raca} no setor público",
            "Diferença-em-diferenças vs. setor privado (controle) · pontos percentuais em relação ao trimestre anterior à lei",
            f"causal_eventstudy_participacao_{_slug(raca)}.png",
            CORES_RACA_TRATADO.get(raca, COR_NEGRA),
        )

    curva_renda = curvas[(curvas["raca_cor"] == "Negra") & (curvas["outcome"] == "hiato_renda_pct")]
    grafico_event_study(
        curva_renda,
        "Lei de Cotas no Serviço Público: hiato de renda Branca-Negra",
        "Diferença-em-diferenças vs. setor privado (controle) · pontos percentuais em relação ao trimestre anterior à lei",
        "causal_eventstudy_hiato_renda.png",
        COR_NEGRA,
    )


if __name__ == "__main__":
    main()
