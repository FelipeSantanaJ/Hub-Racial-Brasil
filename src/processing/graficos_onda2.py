"""Gráficos dos estudos da Onda 2 (Blocos B e C), no estilo do Hub (`graficos_fase1`). Cada gráfico
corresponde a uma afirmação permitida nas fichas `docs/studies/{B1…B6,C1…C5}`.

Uso:
    python -m src.processing.graficos_onda2
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
import pandas as pd

from src.inference import tendencia
from src.processing import graficos_fase1 as g

P = g.REPO_ROOT / "data" / "processed"
COR_P4 = "#8f8271"
CORES_CEL = {"HB": g.COR_BRANCA, "MB": "#5fb3ab", "HN": g.COR_NEGRA, "MN": "#e39a74", "HI": g.COR_INDIGENA, "MI": "#b97a98"}
ROT_CEL = {"HB": "Homens brancos", "MB": "Mulheres brancas", "HN": "Homens negros", "MN": "Mulheres negras",
           "HI": "Homens indígenas", "MI": "Mulheres indígenas"}


def _data(df):
    return pd.to_datetime(df["ano"].astype(str) + "-" + ((df["trimestre"] - 1) * 3 + 1).astype(str) + "-01")


def _limpar(ax):
    ax.set_facecolor(g.SUPERFICIE)
    ax.grid(axis="y", color=g.GRADE, lw=0.8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)


def grafico_b1_degraus() -> None:
    """B1: série do hiato P1 e P4 (Branca × Negra) com a reta simples e o ajuste com degraus."""
    s = pd.read_parquet(P / "sensibilidade_hiato_populacao.parquet")
    deg = pd.read_parquet(P / "b1_degraus_hiato.parquet")
    fig, ax = g._novo_eixo(figsize=(11, 5.6))
    g.marcar_quebras(ax)
    for popn, cor, rot in (("P1", g.COR_BRANCA, "Ocupados com renda (P1)"), ("P4", COR_P4, "Todos os adultos (P4)")):
        x = s[(s["populacao"] == popn) & (s["comparacao"] == "Branca × Negra")].sort_values(["ano", "trimestre"])
        d = _data(x)
        ax.plot(d, x["hiato_percentual"], color=cor, lw=1.6, alpha=0.9, label=rot)
        # ajuste com tendência + degraus (coeficientes do b1_degraus_hiato)
        serie = f"{popn} · Branca × Negra"
        c = deg[(deg["serie"] == serie) & (deg["metrica"] == "hiato_pct")].set_index("termo")["estimativa"]
        t = tendencia.tempo_anos(x["ano"], x["trimestre"])
        y = x["hiato_percentual"].to_numpy()
        base = y.mean() - c["inclinacao_por_ano"] * (t - t.mean()).mean()
        ajuste = base + c["inclinacao_por_ano"] * (t - t.mean())
        for k, (a, q) in {"2015T1": (2015, 1), "2020T1": (2020, 1), "2022T1": (2022, 1)}.items():
            ajuste = ajuste + c[f"degrau_{k}"] * ((x["ano"] * 10 + x["trimestre"]) >= a * 10 + q).to_numpy()
        ajuste = ajuste + (y - ajuste).mean()
        ax.step(d, ajuste, where="post", color=cor, lw=2.4, ls="--")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.legend(loc="lower left", frameon=False, fontsize=9.5)
    g._titulo(ax, "O hiato caiu em degrau depois da pandemia, não em tendência contínua",
              "Hiato % Branca × Negra · tracejado = tendência comum + degraus em 2015, 2020 e 2022 (EP EWC) · 18+")
    g._rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda2_b1_degraus_hiato.png")


def grafico_b3_quantis() -> None:
    j = pd.read_parquet(P / "b3_quantis_janelas.parquet")
    fig, ax = g._novo_eixo(figsize=(10, 5.5))
    x = np.arange(len(j))
    for i, (col, cor, rot) in enumerate([("log_pontos_2012", "#8f8271", "2012"),
                                         ("log_pontos_2025T3-2026T2", g.COR_NEGRA, "2025T3–2026T2")]):
        ax.bar(x + (i - 0.5) * 0.36, j[col], 0.36, color=cor, label=rot, zorder=3)
    for k, r in j.iterrows():
        dif = 0.0 if abs(r["diferenca"]) < 0.005 else r["diferenca"]
        ax.text(k + 0.18, r["log_pontos_2025T3-2026T2"] + 0.02, f"{dif:+.2f}".replace(".", ",").replace("+0,00", "0,00"),
                ha="center", fontsize=8.5, color=g.TINTA_SECUNDARIA)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.1f}".replace(".", ","))
    ax.set_xticks(x)
    ax.set_xticklabels(j["quantil"])
    ax.legend(loc="upper center", frameon=False, fontsize=9.5)
    _limpar(ax)
    g._titulo(ax, "Hiato Branca × Negra em cada ponto da distribuição: a base se afastou, o topo parou",
              "Log-pontos (ln quantil Branca − ln quantil Negra) · número = mudança · P25 ≈ salário mínimo (valores redondos)")
    g._rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda2_b3_hiato_quantis_janelas.png")


def grafico_b4_coortes() -> None:
    a = pd.read_parquet(P / "b4_apc.parquet")
    a = a[a["termo"].str.startswith("coorte")]
    fig, ax = g._novo_eixo(figsize=(10, 5.5))
    for mod, cor in (("APC (Deaton-Paxson)", g.COR_NEGRA), ("AC (sem período)", "#8f8271")):
        x = a[a["modelo"] == mod]
        anos = x["termo"].str[-4:].astype(int) + 2
        ax.errorbar(anos + (0.6 if mod.startswith("AC") else 0), x["estimativa"],
                    yerr=[x["estimativa"] - x["ic_inferior"], x["ic_superior"] - x["estimativa"]],
                    fmt="o-", color=cor, ms=4, lw=1.6, capsize=2, label=mod)
    ax.axhline(0, color=g.EIXO, lw=1)
    ax.legend(loc="lower left", frameon=False, fontsize=9)
    _limpar(ax)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.1f}".replace(".", ",").replace("-", "−"))
    ax.set_xlabel("Coorte de nascimento (meio do grupo de 5 anos)", color=g.TINTA_SECUNDARIA)
    g._titulo(ax, "Coortes mais novas têm hiato menor na mesma idade (sob restrição declarada)",
              "Efeito de coorte em log-pontos vs. nascidos em 1950–54 · Deaton-Paxson: período sem tendência · IC 95%")
    g._rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda2_b4_efeitos_coorte.png")


def grafico_b6_projecao() -> None:
    s = pd.read_parquet(P / "hiato_racial.parquet").sort_values(["ano", "trimestre"])
    b6 = pd.read_parquet(P / "b6_projecao_condicional.parquet")
    b6 = b6[b6["serie"] == "P1 · Branca × Negra"].set_index("premissa")
    fig, ax = g._novo_eixo(figsize=(11, 5.6))
    t = tendencia.tempo_anos(s["ano"], s["trimestre"])
    ax.plot(t, s["hiato_percentual"], color=g.COR_BRANCA, lw=2, label="Observado (P1)")
    t0, h0 = t[-1], s["hiato_percentual"].iloc[-1]
    fut = np.linspace(t0, 2125, 200)
    pa = b6.loc["P-a ritmo linear de todo o período"]
    for rit, ls in ((pa["ritmo_pp_ano"], "-"), (pa["ritmo_ic_inferior"], ":"), (pa["ritmo_ic_superior"], ":")):
        ax.plot(fut, np.maximum(h0 + rit * (fut - t0), 0), color=g.COR_NEGRA, ls=ls, lw=1.4)
    pb = b6.loc["P-b ritmo linear desde 2022"]
    # o ritmo pós-2022 não é distinguível de zero: desenhado plano, com o número no rótulo
    ax.plot(fut, np.full_like(fut, h0), color="#8f8271", lw=1.4)
    f1 = lambda v: f"{v:+.1f}".replace(".", ",")  # noqa: E731
    ax.text(2040, h0 + 2, f"ritmo desde 2022: {f1(pb['ritmo_pp_ano'])} p.p./ano (IC {f1(pb['ritmo_ic_inferior'])} a "
            f"{f1(pb['ritmo_ic_superior'])}) — não cai", fontsize=8.5, color=g.TINTA_SECUNDARIA)
    ax.text(2080, max(h0 + pa["ritmo_pp_ano"] * (2080 - t0), 0) + 2, "se continuar o ritmo de 2012–26 (−0,8 p.p./ano)",
            fontsize=8.5, color=g.COR_NEGRA)
    ax.set_ylim(0, 110)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    _limpar(ax)
    g._titulo(ax, "Projeção condicional: se o ritmo for X, o hiato zera quando? (não é previsão)",
              "Hiato % Branca × Negra, P1 · pontilhado = IC 95% do ritmo (EWC) · sem modelo de choques nem de composição")
    g._rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda2_b6_projecao_condicional.png")


def grafico_c1_celulas() -> None:
    c = pd.read_parquet(P / "c123_racaxsexo_celulas.parquet")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), dpi=150, sharey=True)
    fig.patch.set_facecolor(g.SUPERFICIE)
    for ax, conc, tit in zip(axes, ["P1", "P4 (todos os adultos, fora de P1 = 0)"],
                             ["Ocupados com renda (P1)", "Todos os adultos (P4)"]):
        x = c[(c["conceito"] == conc) & c["metrica"].str.startswith("C1 log HB/")]
        for sig in ["MB", "HN", "MN"]:
            y = x[x["metrica"] == f"C1 log HB/{sig}"].sort_values(["ano", "trimestre"])
            ax.plot(_data(y), 100 * np.exp(-y["estimativa"]), color=CORES_CEL[sig], lw=2, label=ROT_CEL[sig])
        g.marcar_quebras(ax)
        ax.set_title(tit, loc="left", fontsize=11, color=g.TINTA_PRIMARIA)
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
        _limpar(ax)
    axes[0].legend(loc="lower left", frameon=False, fontsize=9)
    fig.suptitle("Quanto cada grupo ganha, em % da renda média dos homens brancos", x=0.01, ha="left", fontsize=14,
                 fontweight="bold", color=g.TINTA_PRIMARIA)
    fig.text(0.01, 0.905, "Renda do trabalho principal · pessoas de 18+ · P4: quem está fora de P1 entra com zero",
             fontsize=9.5, color=g.TINTA_SECUNDARIA)
    g._rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 0.9))
    g._salvar(fig, "onda2_c1_celulas_pct_homem_branco.png")


def grafico_c3_shapley() -> None:
    c = pd.read_parquet(P / "c123_racaxsexo_celulas.parquet")
    u = c[(c["ano"] == c["ano"].max())]
    u = u[(u["trimestre"] == u["trimestre"].max()) & (u["escala"] == "log-pontos")]
    an = pd.read_parquet(P / "c123_racaxsexo_domiciliar_anual.parquet")
    an = an[(an["ano"] == an["ano"].max()) & (an["escala"] == "log-pontos")]
    fig, ax = g._novo_eixo(figsize=(10, 5.2))
    linhas = [("P1", u[u["conceito"] == "P1"]), ("P4 (todos os adultos)", u[u["conceito"].str.startswith("P4")]),
              ("Renda domiciliar per capita", an)]
    for i, (rot, x) in enumerate(linhas):
        v = x.set_index("metrica")["estimativa"]
        r_, gn = v["C3 Shapley raça·Negra"], v["C3 Shapley gênero·Negra"]
        ax.barh(i, r_, color=g.COR_NEGRA, label="raça" if i == 0 else None)
        ax.barh(i, gn, left=r_, color="#d19a12", label="gênero" if i == 0 else None)
        ax.text(r_ + gn + 0.01, i, f"total {r_ + gn:.2f} · raça {100 * r_ / (r_ + gn):.0f}%".replace(".", ","), va="center",
                fontsize=9, color=g.TINTA_SECUNDARIA)
    ax.set_yticks(range(len(linhas)))
    quebra = {"P4 (todos os adultos)": "P4\n(todos os adultos)", "Renda domiciliar per capita": "Renda domiciliar\nper capita"}
    ax.set_yticklabels([quebra.get(r, r) for r, _ in linhas])
    ax.set_xlim(0, 1.45)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.1f}".replace(".", ","))
    ax.invert_yaxis()
    ax.legend(loc="lower right", frameon=False, fontsize=9.5)
    ax.grid(axis="x", color=g.GRADE, lw=0.8)
    g._titulo(ax, "Homens brancos × mulheres negras: quanto é raça, quanto é gênero",
              "Log-pontos das médias · repartição de Shapley (independe da ordem; a interação é dividida meio a meio)")
    g._rodape(fig, "Fonte: IBGE, PNAD Contínua Trimestral (P1, P4: último trimestre) e anual (renda domiciliar). "
                   "Elaboração própria.")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda2_c3_shapley_raca_genero.png")


def grafico_c4_maternidade() -> None:
    c = pd.read_parquet(P / "c4_penalidade_maternidade.parquet")
    c = c[(c["faixa_etaria"] == "25–44") & c["definicao"].str.startswith("principal") & (c["desfecho"] == "pr_p1_pp")
          & c["raca"].isin(["Branca", "Negra"])]
    fig, ax = g._novo_eixo(figsize=(10, 5.2))
    rotulos, i = [], 0
    for jan in ["2012", "2025T3-2026T2"]:
        for sexo in ["Mulher", "Homem"]:
            for raca, cor in (("Branca", g.COR_BRANCA), ("Negra", g.COR_NEGRA)):
                r = c[(c["janela"] == jan) & (c["sexo"] == sexo) & (c["raca"] == raca)]
                if r.empty:
                    continue
                r = r.iloc[0]
                ax.barh(i, r["estimativa"], color=cor, zorder=3)
                ax.errorbar(r["estimativa"], i, xerr=[[r["estimativa"] - r["ic_inferior"]], [r["ic_superior"] - r["estimativa"]]],
                            fmt="none", ecolor=g.TINTA_SECUNDARIA, capsize=2, zorder=4)
                adj = {"Branca": "brancas", "Negra": "negras"}[raca] if sexo == "Mulher" else {"Branca": "brancos", "Negra": "negros"}[raca]
                rotulos.append(f"{jan.replace('T3-', 'T3–')} · {'mulheres' if sexo == 'Mulher' else 'homens'} {adj}")
                i += 1
    ax.set_yticks(range(len(rotulos)))
    ax.set_yticklabels(rotulos, fontsize=8.5)
    ax.invert_yaxis()
    ax.axvline(0, color=g.EIXO, lw=1)
    ax.grid(axis="x", color=g.GRADE, lw=0.8)
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}".replace("-", "−"))
    g._titulo(ax, "Filho de 0 a 5 anos e ocupação com renda (25–44 anos)",
              "Diferença em p.p. de Pr(P1) com mesma idade, instrução e região · responsáveis e cônjuges · IC 95%")
    g._rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda2_c4_penalidade_maternidade.png")


def grafico_c5_domestico() -> None:
    c = pd.read_parquet(P / "c5_trabalho_domestico.parquet")
    fig, ax = g._novo_eixo(figsize=(10, 5.5))
    for raca in ["Branca", "Negra"]:
        x = c[(c["indicador"] == "pct_domesticas_entre_ocupadas_p1") & (c["raca"] == raca)].sort_values(["ano", "trimestre"])
        d = _data(x)
        ax.plot(d, x["estimativa"], color=g.CORES_RACA[raca], lw=2, label=f"Mulheres {raca.lower()}s")
        ax.fill_between(d, x["ic_inferior"], x["ic_superior"], color=g.CORES_RACA[raca], alpha=0.12, lw=0)
    g.marcar_quebras(ax)
    ax.set_ylim(0, None)
    ax.yaxis.set_major_locator(MultipleLocator(4))
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.legend(loc="upper right", frameon=False, fontsize=9.5)
    g._titulo(ax, "Trabalho doméstico remunerado entre as mulheres ocupadas com renda",
              "% das ocupadas de 18+ com renda que são trabalhadoras domésticas (VD4009 03/04) · faixa = IC 95%")
    g._rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    g._salvar(fig, "onda2_c5_trabalho_domestico.png")


def main() -> None:
    for f in (grafico_b1_degraus, grafico_b3_quantis, grafico_b4_coortes, grafico_b6_projecao, grafico_c1_celulas,
              grafico_c3_shapley, grafico_c4_maternidade, grafico_c5_domestico):
        try:
            f()
        except FileNotFoundError as e:
            print(f"pulado {f.__name__}: {e}")


if __name__ == "__main__":
    main()
