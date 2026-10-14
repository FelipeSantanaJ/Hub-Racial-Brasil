"""Gráficos dos estudos da Onda 1 (Blocos S, T e A), no estilo do Hub (`graficos_fase1`).
Cada gráfico corresponde a uma afirmação permitida nas fichas `docs/studies/{S1,T,A}`.

Uso:
    python -m src.processing.graficos_onda1
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator, NullFormatter
import pandas as pd

from src.processing import graficos_fase1 as g

P = g.REPO_ROOT / "data" / "processed"
FONTE_ANUAL = ("Fonte: IBGE, PNAD Contínua anual (Visita 1; Visita 5 em 2020–21). Renda domiciliar per capita "
               "(VD5008), nominal do ano. Elaboração própria.")
CORES_POP = {"P1": g.TINTA_PRIMARIA, "P2": "#8f8271", "P3": "#d19a12", "P4": g.COR_NEGRA}
ROT_POP = {"P1": "P1 · ocupados com renda (referência)", "P2": "P2 · + ocupados sem rendimento",
           "P3": "P3 · renda de todos os trabalhos", "P4": "P4 · todos os adultos (não ocupados = 0)"}


def _data(df):
    return pd.to_datetime(df["ano"].astype(str) + "-" + ((df["trimestre"] - 1) * 3 + 1).astype(str) + "-01")


def grafico_s1_populacoes() -> None:
    s = pd.read_parquet(P / "sensibilidade_hiato_populacao.parquet")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), dpi=150, sharey=True)
    fig.patch.set_facecolor(g.SUPERFICIE)
    for ax, comp, tit in zip(axes, ["Branca × Negra, homens", "Branca × Negra, mulheres"], ["Homens", "Mulheres"]):
        ax.set_facecolor(g.SUPERFICIE)
        c = s[s["comparacao"] == comp].assign(data=lambda d: _data(d))
        for pop_ in ["P1", "P2", "P3", "P4"]:
            x = c[c["populacao"] == pop_].sort_values("data")
            ax.plot(x["data"], x["hiato_percentual"], color=CORES_POP[pop_], lw=2 if pop_ in ("P1", "P4") else 1.2,
                    label=ROT_POP[pop_])
            if pop_ in ("P1", "P4"):
                ax.fill_between(x["data"], x["ic_inferior"], x["ic_superior"], color=CORES_POP[pop_], alpha=0.12, lw=0)
        g.marcar_quebras(ax)
        ax.set_title(tit, loc="left", fontsize=11, color=g.TINTA_PRIMARIA)
        ax.grid(axis="y", color=g.GRADE, lw=0.8)
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    axes[0].legend(loc="lower left", frameon=False, fontsize=8.5)
    fig.suptitle("Hiato de renda Branca × Negra muda com a população — sobretudo entre mulheres",
                 x=0.01, ha="left", fontsize=14, fontweight="bold", color=g.TINTA_PRIMARIA)
    fig.text(0.01, 0.905, "Hiato % = renda média Branca ÷ Negra − 1 · faixa = IC 95% design-based · pessoas de 18+ · "
             "PNAD Contínua Trimestral, 2012–2026", fontsize=9.5, color=g.TINTA_SECUNDARIA)
    g._rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 0.9))
    g._salvar(fig, "onda1_s1_hiato_por_populacao.png")


def grafico_t1_hiato_domiciliar() -> None:
    t = pd.read_parquet(P / "t1_renda_domiciliar_per_capita.parquet")
    t = t[t["recorte"] == "raca_pessoa"].sort_values("ano")
    fig, ax = g._novo_eixo(figsize=(10, 5.5))
    for gr in ["Negra", "Indígena"]:
        x = t[t["grupo"] == gr]
        ax.plot(x["ano"], x["hiato_percentual"], marker="o", ms=4, color=g.CORES_RACA[gr], lw=2, label=f"Branca × {gr}")
        ax.fill_between(x["ano"], x["ic_inferior"], x["ic_superior"], color=g.CORES_RACA[gr], alpha=0.12, lw=0)
    g.marcar_quebras(ax, eixo="ano")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="y", color=g.GRADE, lw=0.8)
    ax.legend(loc="lower left", frameon=False, fontsize=9.5)
    g._titulo(ax, "Hiato de renda domiciliar per capita, por raça — Brasil (2012–2025)",
              "Hiato % = média Branca ÷ média do grupo − 1 · todas as pessoas, todas as idades · faixa = IC 95%")
    g._rodape(fig, FONTE_ANUAL)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda1_t1_hiato_domiciliar_per_capita.png")


def grafico_t2_pobreza() -> None:
    t = pd.read_parquet(P / "t2_pobreza.parquet")
    t = t[(t["recorte"] == "raca_pessoa") & (t["linha"] == "1/2 salário mínimo (CadÚnico)")].sort_values("ano")
    fig, ax = g._novo_eixo(figsize=(10, 5.5))
    for gr in ["Branca", "Negra", "Indígena"]:
        x = t[t["grupo"] == gr]
        ax.plot(x["ano"], x["fgt0_pct"], marker="o", ms=4, color=g.CORES_RACA[gr], lw=2, label=gr)
        ax.fill_between(x["ano"], x["fgt0_ic_inferior"], x["fgt0_ic_superior"], color=g.CORES_RACA[gr], alpha=0.12, lw=0)
    g.marcar_quebras(ax, eixo="ano")
    ax.set_ylim(0, None)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="y", color=g.GRADE, lw=0.8)
    ax.legend(loc="upper right", frameon=False, fontsize=9.5)
    g._titulo(ax, "Pessoas abaixo de ½ salário mínimo per capita, por raça (2012–2025)",
              "% das pessoas (todas as idades) · linha de baixa renda do CadÚnico · faixa = IC 95% · 2020–21: Visita 5")
    g._rodape(fig, FONTE_ANUAL)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda1_t2_pobreza_meio_sm.png")


def grafico_a3_hiato_quantis() -> None:
    a = pd.read_parquet(P / "a3_hiato_quantis.parquet")
    a = a[a["raca"] == "hiato Branca × Negra"]
    ordem = ["P10", "P25", "P50", "P75", "P90", "P95", "P99"]
    fig, ax = g._novo_eixo(figsize=(10, 5.5))
    x = np.arange(len(ordem))
    for i, (ano, cor) in enumerate([(2012, "#8f8271"), (2026, g.COR_NEGRA)]):
        d = a[a["ano"] == ano].set_index("medida").loc[ordem]
        ax.bar(x + (i - 0.5) * 0.36, d["valor"], 0.36, color=cor, label=str(ano), zorder=3)
        ax.errorbar(x + (i - 0.5) * 0.36, d["valor"], yerr=[d["valor"] - d["ic_inferior"], d["ic_superior"] - d["valor"]],
                    fmt="none", ecolor=g.TINTA_SECUNDARIA, elinewidth=0.8, capsize=2, zorder=4)
    ax.set_xticks(x)
    ax.set_xticklabels(ordem)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="y", color=g.GRADE, lw=0.8, zorder=0)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    g._titulo(ax, "Hiato de renda Branca × Negra em cada ponto da distribuição (2º trimestre)",
              "Hiato % = quantil Branca ÷ quantil Negra − 1 · IC 95%: bootstrap Rao-Wu · P25 ≈ salário mínimo")
    g._rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda1_a3_hiato_por_quantil.png")


def grafico_a5_decimos() -> None:
    a = pd.read_parquet(P / "a5_representacao_decimos.parquet")
    u = a[(a["ano"] == a["ano"].max())]
    u = u[(u["trimestre"] == u["trimestre"].max()) & u["decimo"].str.startswith("D")]
    fig, ax = g._novo_eixo(figsize=(10, 5.5))
    for gr in ["Branca", "Negra", "Indígena"]:
        d = u[u["raca"] == gr].sort_values("decimo")
        ax.plot(range(1, 11), d["indice_representacao"], marker="o", color=g.CORES_RACA[gr], lw=2, label=gr)
    ax.axhline(1, color=g.TINTA_MUTED, lw=1, ls="--")
    ax.set_xticks(range(1, 11))
    ax.set_xticklabels([f"D{i}" for i in range(1, 11)])
    ax.grid(axis="y", color=g.GRADE, lw=0.8)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    g._titulo(ax, f"Quem está em cada décimo de renda do Brasil, {int(u['ano'].iloc[0])} T{int(u['trimestre'].iloc[0])}",
              "Participação no décimo ÷ participação na população (1 = proporcional) · D1 = 10% que menos ganham")
    g._rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda1_a5_representacao_decimos.png")


CORES_TERMOS = {"ln_pr_p1": g.COR_NEGRA, "ln_horas": g.COR_PARDA, "ln_renda_hora": g.COR_BRANCA}
ROT_TERMOS = {"ln_pr_p1": "estar ocupado com renda (Pr(P1))", "ln_horas": "horas trabalhadas",
              "ln_renda_hora": "renda por hora"}


def grafico_s14_margens() -> None:
    """S1.4: hiato da renda do trabalho por adulto em log-pontos = soma de três termos."""
    s = pd.read_parquet(P / "s14_margens_intensiva_extensiva.parquet")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), dpi=150, sharey=True)
    fig.patch.set_facecolor(g.SUPERFICIE)
    for ax, comp, tit in zip(axes, ["Branca × Negra, homens", "Branca × Negra, mulheres"], ["Homens", "Mulheres"]):
        ax.set_facecolor(g.SUPERFICIE)
        c = s[s["comparacao"] == comp].assign(data=lambda d: _data(d)).sort_values("data")
        base = np.zeros(len(c))
        for k in ["ln_renda_hora", "ln_horas", "ln_pr_p1"]:
            ax.fill_between(c["data"], base, base + c[k], color=CORES_TERMOS[k], alpha=0.85, lw=0, label=ROT_TERMOS[k])
            base = base + c[k].to_numpy()
        ax.plot(c["data"], c["ln_renda_por_adulto"], color=g.TINTA_PRIMARIA, lw=1.2)
        g.marcar_quebras(ax)
        ax.set_title(tit, loc="left", fontsize=11, color=g.TINTA_PRIMARIA)
        ax.grid(axis="y", color=g.GRADE, lw=0.8)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    axes[0].set_ylabel("log-pontos (Branca − Negra)", color=g.TINTA_SECUNDARIA)
    axes[0].legend(loc="lower left", frameon=False, fontsize=8.5)
    fig.suptitle("De onde vem o hiato de renda do trabalho por adulto: renda por hora, horas ou estar ocupado",
                 x=0.01, ha="left", fontsize=14, fontweight="bold", color=g.TINTA_PRIMARIA)
    fig.text(0.01, 0.905, "Renda por adulto = Pr(ocupado com renda) × horas × renda por hora · pessoas de 18+ · "
             "soma das áreas = hiato em log-pontos (linha)", fontsize=9.5, color=g.TINTA_SECUNDARIA)
    g._rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 0.9))
    g._salvar(fig, "onda1_s14_margens_hiato.png")


def grafico_s15_selecao() -> None:
    """S1.5: diferença de participação em P1 e quanto incluir os de fora aumenta o hiato."""
    s = pd.read_parquet(P / "s15_selecao_no_tempo.parquet")
    s = s[s["comparacao"] == "Branca × Negra"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    paineis = [("a_dif_participacao_p1_pp", "Participação em P1: Branca − Negra (p.p.)"),
               ("b_delta_hiato_P4_menos_P1_pp", "Quanto o hiato cresce ao incluir quem está fora de P1 (p.p.)")]
    cores = {"Total": g.TINTA_PRIMARIA, "Homem": g.COR_BRANCA, "Mulher": g.COR_NEGRA}
    for ax, (serie, tit) in zip(axes, paineis):
        ax.set_facecolor(g.SUPERFICIE)
        x = s[s["serie"] == serie].assign(data=lambda d: _data(d))
        for sexo, rot in (("Total", "Total"), ("Homem", "Homens"), ("Mulher", "Mulheres")):
            y = x[x["sexo"] == sexo].sort_values("data")
            ax.plot(y["data"], y["valor"], color=cores[sexo], lw=2 if sexo == "Total" else 1.3, label=rot)
        g.marcar_quebras(ax)
        ax.axhline(0, color=g.EIXO, lw=1)
        ax.set_title(tit, loc="left", fontsize=11, color=g.TINTA_PRIMARIA)
        ax.grid(axis="y", color=g.GRADE, lw=0.8)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    axes[0].legend(loc="upper left", frameon=False, fontsize=8.5)
    fig.suptitle("A desvantagem negra em estar ocupado com renda cresceu na crise e voltou ao nível de 2012",
                 x=0.01, ha="left", fontsize=14, fontweight="bold", color=g.TINTA_PRIMARIA)
    fig.text(0.01, 0.905, "Pessoas de 18+ · P1 = ocupados com renda do trabalho principal > 0 · hiato P4: todos os "
             "adultos, quem está fora de P1 com renda zero", fontsize=9.5, color=g.TINTA_SECUNDARIA)
    g._rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 0.9))
    g._salvar(fig, "onda1_s15_selecao_no_tempo.png")


def grafico_t4_topo_base() -> None:
    """T4: razão de chances de estar no topo e na base 10% da renda domiciliar per capita."""
    t = pd.read_parquet(P / "t4_decimos_renda_domiciliar.parquet")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    for ax, dec, tit in zip(axes, ["topo10", "base10"], ["Chance de estar entre os 10% mais ricos",
                                                         "Chance de estar entre os 10% mais pobres"]):
        ax.set_facecolor(g.SUPERFICIE)
        for gr in ["Negra", "Indígena"]:
            x = t[(t["decimo"] == dec) & (t["raca"] == gr)].sort_values("ano")
            ax.plot(x["ano"], x["razao_de_chances"], marker="o", ms=4, color=g.CORES_RACA[gr], lw=2, label=gr)
            ax.fill_between(x["ano"], x["rc_ic_inferior"], x["rc_ic_superior"], color=g.CORES_RACA[gr], alpha=0.12, lw=0)
        g.marcar_quebras(ax, eixo="ano")
        ax.axhline(1, color=g.TINTA_MUTED, lw=1, ls="--")
        ax.set_yscale("log")
        ax.yaxis.set_major_locator(FixedLocator([0.1, 0.2, 0.3, 0.5, 1] if dec == "topo10" else [1, 2, 3, 4, 6]))
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:g}".replace(".", ","))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_title(tit, loc="left", fontsize=11, color=g.TINTA_PRIMARIA)
        ax.grid(axis="y", color=g.GRADE, lw=0.8)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    axes[0].legend(loc="upper left", frameon=False, fontsize=9)
    fig.suptitle("Renda domiciliar per capita: razão de chances em relação a pessoas brancas (2012–2025)",
                 x=0.01, ha="left", fontsize=14, fontweight="bold", color=g.TINTA_PRIMARIA)
    fig.text(0.01, 0.905, "1 = mesma chance que pessoas brancas · escala log · faixa = IC 95% · todas as pessoas, "
             "todas as idades · décimos nacionais do ano", fontsize=9.5, color=g.TINTA_SECUNDARIA)
    g._rodape(fig, FONTE_ANUAL)
    fig.tight_layout(rect=(0, 0.03, 1, 0.9))
    g._salvar(fig, "onda1_t4_topo_base_domiciliar.png")


def main() -> None:
    grafico_s1_populacoes()
    grafico_t1_hiato_domiciliar()
    grafico_t2_pobreza()
    grafico_a3_hiato_quantis()
    grafico_a5_decimos()
    grafico_s14_margens()
    grafico_s15_selecao()
    grafico_t4_topo_base()


if __name__ == "__main__":
    main()
