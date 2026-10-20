"""Gráficos dos estudos da Onda 4 (Blocos E e H), no estilo do Hub (`graficos_fase1`). Cada gráfico corresponde a uma
afirmação permitida nas fichas `docs/studies/{E1,E3,E7,H1,H2,H3,H3.2}`.

Uso:
    python -m src.processing.graficos_onda4
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.processing import graficos_fase1 as g

P = g.REPO_ROOT / "data" / "processed"
RECENTE = "2025T3-2026T2"
ROT_RECENTE = "2025T3–2026T2"
FONTES = {
    "e1": "Fonte: IBGE, PNAD Contínua Trimestral (2012 e 2025T3–2026T2). Elaboração própria.",
    "h1": "Fonte: IBGE, PNAD Contínua Trimestral. Jovens de 25–29 que moram com pai ou mãe. Elaboração própria.",
    "h2": "Fonte: IBGE, PNAD Contínua Trimestral. Ocupados de 18–29 com renda > 0; ln da renda do trabalho. Elaboração própria.",
    "e3": "Fonte: INEP, microdados do SAEB 2023 (pesos amostrais do aluno). Elaboração própria.",
    "e7": "Fonte: INEP, Censo Escolar 2024 (censo: sem erro amostral). Elaboração própria.",
    "h3": "Fonte: IBGE, POF 2017–2018 (bens) e PNAD Contínua anual 2025, Visita 1 (moradia e renda). Elaboração própria.",
}
COR_CONDICIONAL = "#2f6f9f"
COR_BRUTO = g.TINTA_MUTED


def _fmt(v: float, casas: int = 0) -> str:
    return f"{v:.{casas}f}".replace(".", ",").replace("-", "−")


def _estilo(ax) -> None:
    ax.set_facecolor(g.SUPERFICIE)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(g.EIXO)
    ax.tick_params(axis="both", colors=g.TINTA_MUTED, labelsize=9.5, length=0)


def _paineis(n: int, figsize):
    fig, axs = plt.subplots(1, n, figsize=figsize, dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    for ax in axs:
        _estilo(ax)
    return fig, axs


def _titulo_fig(fig, titulo: str, subtitulo: str) -> None:
    fig.text(0.01, 0.965, titulo, fontsize=14, fontweight="bold", color=g.TINTA_PRIMARIA, ha="left", va="top")
    fig.text(0.01, 0.905, subtitulo, fontsize=9.5, color=g.TINTA_SECUNDARIA, ha="left", va="top")


def grafico_e1_conclusao_idade() -> None:
    """E1: % com médio completo (17–29) e com superior completo (22–29), Branca × Negra, 2012 × janela recente."""
    e1 = pd.read_parquet(P / "e1_escolarizacao_idade.parquet")
    e1 = e1[e1["idade"].str.fullmatch(r"\d+")].assign(idade_n=lambda d: d["idade"].astype(int))
    fig, axs = _paineis(2, (11, 5.2))
    paineis = [("medio_completo", range(17, 30), "Ensino médio completo"),
               ("superior_completo", range(22, 30), "Ensino superior completo")]
    for ax, (ind, idades, nome) in zip(axs, paineis):
        for raca in ("Branca", "Negra"):
            cor = g.CORES_RACA[raca]
            for per, estilo, lw in (("2012", "--", 1.3), (RECENTE, "-", 2.2)):
                s = e1[(e1["indicador"] == ind) & (e1["raca"] == raca) & (e1["periodo"] == per)
                       & e1["idade_n"].isin(idades)].sort_values("idade_n")
                rot = f"{raca}, {'2012' if per == '2012' else ROT_RECENTE}"
                ax.plot(s["idade_n"], s["estimativa"], ls=estilo, lw=lw, color=cor, marker="o" if per != "2012" else None,
                        ms=3, label=rot, alpha=1 if per != "2012" else 0.75)
                if per == RECENTE:
                    ax.fill_between(s["idade_n"], s["ic_inferior"], s["ic_superior"], color=cor, alpha=0.18, lw=0)
        ax.set_title(nome, fontsize=11, color=g.TINTA_PRIMARIA, loc="left")
        ax.set_ylim(0, 100)
        ax.set_xticks(list(idades))
        ax.set_xlabel("idade", fontsize=9, color=g.TINTA_MUTED)
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
        ax.grid(axis="y", color=g.GRADE, lw=0.8)
    axs[0].legend(loc="lower right", frameon=False, fontsize=8.5)
    _titulo_fig(fig, "A distância no ensino médio caiu desde 2012; no diploma superior, aumentou",
                "% com a etapa concluída por idade · linha tracejada = 2012; contínua = janela recente com IC 95%")
    g._rodape(fig, FONTES["e1"])
    fig.tight_layout(rect=(0, 0.03, 1, 0.87))
    g._salvar(fig, "onda4_e1_conclusao_por_idade.png")


def grafico_h1_superior_origem() -> None:
    """H1: % com superior completo aos 25–29, por escolaridade dos pais, Branca × Negra (janela recente)."""
    h1 = pd.read_parquet(P / "h1_transmissao_educacional.parquet")
    x = h1[(h1["periodo"] == RECENTE) & (h1["desfecho"] == "superior completo (25–29)")
           & (h1["medida"] == "% com o desfecho") & h1["raca"].isin(["Branca", "Negra"])]
    origens = sorted(o for o in x["origem"].unique() if o.startswith("G"))
    rotulos = ["Pais até fund.\nincompleto", "Pais com fund.\ncompleto", "Pais com médio\ncompleto", "Pais com\nsuperior"]
    fig, ax = g._novo_eixo(figsize=(11, 5.2))
    larg = 0.36
    for k, raca in enumerate(("Branca", "Negra")):
        s = x[x["raca"] == raca].set_index("origem").loc[origens]
        pos = np.arange(len(origens)) + (k - 0.5) * larg
        ax.bar(pos, s["estimativa"], larg, color=g.CORES_RACA[raca], label=raca)
        ax.errorbar(pos, s["estimativa"], yerr=[s["estimativa"] - s["ic_inferior"], s["ic_superior"] - s["estimativa"]],
                    fmt="none", ecolor=g.TINTA_SECUNDARIA, elinewidth=1, capsize=3)
        for p, v, sup in zip(pos, s["estimativa"], s["ic_superior"]):
            ax.text(p, sup + 1.2, f"{_fmt(v)}%", ha="center", fontsize=9, color=g.TINTA_SECUNDARIA)
    ax.set_xticks(range(len(origens)))
    ax.set_xticklabels(rotulos, fontsize=9.5)
    ax.set_ylim(0, 80)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="y", color=g.GRADE, lw=0.8)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    g._titulo(ax, "Mesmo com pais de igual escolaridade, jovens negros têm menos diploma superior",
              f"% com superior completo aos 25–29 anos, pela maior escolaridade do pai ou da mãe · {ROT_RECENTE} · IC 95%")
    g._rodape(fig, FONTES["h1"])
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda4_h1_superior_por_origem.png")


def grafico_h2_residuo_origem() -> None:
    """H2: hiato condicional (E8) Branca × Negra entre jovens 18–29, sem e com a origem social, nas duas janelas."""
    h2 = pd.read_parquet(P / "h2_origem_renda.parquet")
    especs = [("E8, todos de 18–29", "E8, todos de 18–29", "#c4b8a4"),
              ("E8, corresidentes", "E8, quem mora com os pais", COR_BRUTO),
              ("E8 + origem, corresidentes", "E8 + origem (escolaridade e renda dos pais)", COR_CONDICIONAL)]
    fig, ax = g._novo_eixo(figsize=(11, 4.6))
    janelas = [("2012", "2012"), (RECENTE, ROT_RECENTE)]
    for j, (per, rot) in enumerate(janelas):
        for k, (esp, nome, cor) in enumerate(especs):
            r = h2[(h2["periodo"] == per) & (h2["especificacao"] == esp)].iloc[0]
            y = j * 4 + k
            ax.errorbar(r["estimativa"], y, xerr=[[r["estimativa"] - r["ic_inferior"]], [r["ic_superior"] - r["estimativa"]]],
                        fmt="o", color=cor, ms=7, elinewidth=2, capsize=0, label=nome if j == 0 else None)
            ax.text(r["ic_superior"] + 0.002, y, _fmt(r["estimativa"], 3), va="center", fontsize=9, color=g.TINTA_SECUNDARIA)
        m = h2[(h2["periodo"] == per) & (h2["especificacao"] == "mudança ao incluir a origem")
               & (h2["medida"] == "% do E8 dos corresidentes")].iloc[0]
        ax.text(0.092, j * 4 + 1.5, f"origem reduz {_fmt(-m['estimativa'])}%\n(IC {_fmt(-m['ic_superior'])}–{_fmt(-m['ic_inferior'])}%)",
                va="center", fontsize=9, color=COR_CONDICIONAL)
    ax.set_yticks([1, 5])
    ax.set_yticklabels([r for _, r in janelas])
    ax.invert_yaxis()
    ax.set_xlim(0, 0.11)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.2f}".replace(".", ","))
    ax.grid(axis="x", color=g.GRADE, lw=0.8)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False, fontsize=9)
    g._titulo(ax, "Entre jovens, a origem social responde por ~40% da parte não associada",
              "Hiato Branca × Negra condicional às características do D1 (E8), em log-pontos de renda · IC 95%")
    g._rodape(fig, FONTES["h2"])
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    g._salvar(fig, "onda4_h2_residuo_com_origem.png")


def grafico_e3_saeb() -> None:
    """E3: diferença Branca − Negra de proficiência (DP da série): bruta, + INSE, + INSE dentro da escola."""
    e3 = pd.read_parquet(P / "e3_saeb_proficiencia.parquet")
    x = e3[(e3["raca"] == "Branca − Negra") & (e3["agrupamento"] == "Negra")]
    series = ["5º ano EF", "9º ano EF", "3ª/4ª série EM"]
    especs = [("bruto (amostra com INSE)", "Bruta", COR_BRUTO),
              ("+ INSE", "Mesmo nível socioeconômico (INSE)", "#5fb3ab"),
              ("+ INSE, dentro da escola", "Mesmo INSE, na mesma escola", COR_CONDICIONAL)]
    fig, axs = _paineis(2, (11, 5.2))
    larg = 0.26
    for ax, (disc, nome) in zip(axs, (("LP", "Língua portuguesa"), ("MT", "Matemática"))):
        for k, (esp, rot, cor) in enumerate(especs):
            s = x[(x["disciplina"] == disc) & (x["especificacao"] == esp)].set_index("serie").loc[series]
            pos = np.arange(len(series)) + (k - 1) * larg
            ax.bar(pos, s["estimativa_dp"], larg, color=cor, label=rot)
            ax.errorbar(pos, s["estimativa_dp"], yerr=1.96 * s["ep_dp"], fmt="none", ecolor=g.TINTA_SECUNDARIA,
                        elinewidth=1, capsize=2)
            for p, v in zip(pos, s["estimativa_dp"]):
                ax.text(p, v + 0.012, _fmt(v, 2), ha="center", fontsize=8, color=g.TINTA_SECUNDARIA)
        ax.set_title(nome, fontsize=11, color=g.TINTA_PRIMARIA, loc="left")
        ax.set_xticks(range(len(series)))
        ax.set_xticklabels(["5º ano", "9º ano", "3ª/4ª série\ndo médio"])
        ax.set_ylim(0, 0.5)
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:.1f}".replace(".", ","))
        ax.grid(axis="y", color=g.GRADE, lw=0.8)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.5, 0.035), ncol=3, frameon=False, fontsize=9)
    _titulo_fig(fig, "A diferença de aprendizado cresce até o 9º ano e não some com o mesmo INSE",
                "Proficiência de estudantes brancos menos a de negros (pretos e pardos), em desvios-padrão da série · IC 95%")
    g._rodape(fig, FONTES["e3"])
    fig.tight_layout(rect=(0, 0.08, 1, 0.87))
    g._salvar(fig, "onda4_e3_saeb_inse_escola.png")


def grafico_e7_infraestrutura() -> None:
    """E7: diferença (p.p.) entre as escolas de alunos brancos e de negros, bruta e dentro do mesmo município, por rede."""
    e7 = pd.read_parquet(P / "e7_escolas_segregacao.parquet")
    e7 = e7[e7["indicador"] != "segregação entre escolas"]
    fig, axs = _paineis(2, (11, 5.4))
    ordem = (e7[e7["amostra"] == "rede pública"].sort_values("diferenca_bruta_pp")["indicador"].tolist())
    for ax, rede in zip(axs, ("rede pública", "rede privada")):
        s = e7[e7["amostra"] == rede].set_index("indicador").loc[ordem]
        y = np.arange(len(ordem))
        ax.barh(y + 0.19, s["diferenca_bruta_pp"], 0.36, color=COR_BRUTO, label="Bruta (Brasil)")
        ax.barh(y - 0.19, s["diferenca_dentro_do_municipio_pp"], 0.36, color=COR_CONDICIONAL,
                label="Dentro do mesmo município")
        for yy, v in zip(y, s["diferenca_bruta_pp"]):
            ax.text(v + 0.3, yy + 0.19, _fmt(v, 1), va="center", fontsize=8, color=g.TINTA_SECUNDARIA)
        for yy, v in zip(y, s["diferenca_dentro_do_municipio_pp"]):
            ax.text(max(v, 0) + 0.3, yy - 0.19, _fmt(v, 1), va="center", fontsize=8, color=COR_CONDICIONAL)
        ax.axvline(0, color=g.EIXO, lw=1)
        ax.set_yticks(y)
        ax.set_yticklabels(ordem if rede == "rede pública" else [])
        ax.set_xlim(-2, 20)
        ax.set_xticks(range(0, 21, 5))
        ax.xaxis.set_major_formatter(lambda v, _: _fmt(v))
        ax.set_title(rede.capitalize(), fontsize=11, color=g.TINTA_PRIMARIA, loc="left")
        ax.grid(axis="x", color=g.GRADE, lw=0.8)
    axs[1].legend(loc="lower right", frameon=False, fontsize=9)
    _titulo_fig(fig, "Na rede pública do mesmo município, escolas de alunos brancos e negros têm a mesma estrutura",
                "% das matrículas brancas em escolas com o item menos % das matrículas negras (p.p.)")
    g._rodape(fig, FONTES["e7"])
    fig.tight_layout(rect=(0, 0.03, 1, 0.88))
    g._salvar(fig, "onda4_e7_infraestrutura_municipio.png")


def grafico_h3_patrimonio() -> None:
    """H3/H3.2: Negra − Branca (p.p.) em bens e moradia, bruta e com o mesmo décimo de renda, UF e situação."""
    h32 = pd.read_parquet(P / "h32_pof_bens.parquet")
    h3 = pd.read_parquet(P / "h3_patrimonio_proxy.parquet")
    bens = [i for i in h32["indicador"].unique() if not i.startswith("Número")]
    pof = h32[(h32["raca"] == "Negra − Branca") & h32["indicador"].isin(bens)].copy()
    pof["tipo"] = np.where(pof["medida"] == "diferença bruta", "bruta", "condicional")
    moradia = ["casa própria quitada", "alugada", "recebe aluguel ou aplicações (18+)"]
    pn = h3[(h3["ano"] == h3["ano"].max()) & (h3["visita"] == 1) & (h3["raca"] == "Negra − Branca")
            & h3["indicador"].isin(moradia)].copy()
    pn["tipo"] = np.where(pn["medida"].str.startswith("diferença bruta"), "bruta", "condicional")
    nomes_pn = {"casa própria quitada": "Mora em casa própria quitada", "alugada": "Mora em casa alugada",
                "recebe aluguel ou aplicações (18+)": "Recebe aluguel ou aplicações (18+)"}
    fig, axs = plt.subplots(1, 2, figsize=(11, 5.4), dpi=150, gridspec_kw={"width_ratios": [1.6, 1]})
    fig.patch.set_facecolor(g.SUPERFICIE)
    for ax, df, ordem, nomes, tit in (
            (axs[0], pof, sorted(bens, key=lambda b: pof[(pof["indicador"] == b) & (pof["tipo"] == "condicional")]["estimativa"].iloc[0], reverse=True),
             {b: b for b in bens}, "Bens duráveis no domicílio (POF 2017–18)"),
            (axs[1], pn, moradia, nomes_pn, f"Moradia e renda (PNADC {int(h3['ano'].max())})")):
        _estilo(ax)
        y = np.arange(len(ordem))
        for desl, tipo, cor, rot in ((0.19, "bruta", COR_BRUTO, "Bruta"),
                                     (-0.19, "condicional", COR_CONDICIONAL, "Mesmo décimo de renda, UF e situação")):
            s = df[df["tipo"] == tipo].set_index("indicador").loc[ordem]
            ax.barh(y + desl, s["estimativa"], 0.36, color=cor, label=rot)
            ax.errorbar(s["estimativa"], y + desl, xerr=[s["estimativa"] - s["ic_inferior"], s["ic_superior"] - s["estimativa"]],
                        fmt="none", ecolor=g.TINTA_SECUNDARIA, elinewidth=0.9, capsize=2)
            if tipo == "condicional":
                for yy, v, lo in zip(y, s["estimativa"], s["ic_inferior"]):
                    ax.text(min(lo, 0) - 0.25, yy + desl, _fmt(v, 1), va="center", ha="right", fontsize=8, color=cor)
        ax.axvline(0, color=g.EIXO, lw=1)
        ax.set_yticks(y)
        ax.set_yticklabels([nomes[o] for o in ordem], fontsize=9)
        ax.invert_yaxis()
        ax.set_title(tit, fontsize=10.5, color=g.TINTA_PRIMARIA, loc="left")
        ax.grid(axis="x", color=g.GRADE, lw=0.8)
        ax.xaxis.set_major_formatter(lambda v, _: _fmt(v))
    axs[0].set_xlim(-32, 8)
    axs[1].set_xlim(-9, 6)
    axs[1].set_xticks(range(-8, 7, 2))
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.5, 0.035), ncol=2, frameon=False, fontsize=9)
    _titulo_fig(fig, "Com a mesma renda e o mesmo lugar, pessoas negras têm menos patrimônio",
                "Diferença Negra − Branca em pontos percentuais · IC 95% design-based")
    g._rodape(fig, FONTES["h3"])
    fig.tight_layout(rect=(0, 0.08, 1, 0.88))
    g._salvar(fig, "onda4_h3_patrimonio_condicional.png")


def main() -> None:
    grafico_e1_conclusao_idade()
    grafico_h1_superior_origem()
    grafico_h2_residuo_origem()
    grafico_e3_saeb()
    grafico_e7_infraestrutura()
    grafico_h3_patrimonio()


if __name__ == "__main__":
    main()
