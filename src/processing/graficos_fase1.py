"""Gera as visualizações exploratórias da Fase 1 (Etapa 6).

Lê data/processed/{renda,escolaridade}.parquet e produz os gráficos comparativos
Branca vs. Negra (Preta+Parda) vs. Indígena — geral, por gênero, e cruzando com
faixa etária — salvos em docs/img/ para uso no README.

Uso:
    python -m src.processing.graficos_fase1
"""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "docs" / "img"

# Paleta categórica validada (ver skill de dataviz) — ordem fixa, não trocar por raça.
COR_BRANCA = "#2a78d6"    # slot 1 (azul)
COR_NEGRA = "#eb6834"     # slot 2 (laranja) — usada também para "Preta" nos gráficos detalhados
COR_INDIGENA = "#1baf7a"  # slot 3 (aqua)
CORES_RACA = {"Branca": COR_BRANCA, "Negra (Preta+Parda)": COR_NEGRA, "Indígena": COR_INDIGENA}

# Paleta dos gráficos "detalhados" que separam Preta de Parda (validada à parte,
# all-pairs PASS — ver skill de dataviz): Branca=azul, Preta=laranja, Parda=violeta,
# Indígena=aqua (mesmas cores de Branca/Indígena que o resto do projeto).
COR_PRETA = COR_NEGRA
COR_PARDA = "#4a3aa7"     # slot 7 (violeta)
CORES_RACA_DETALHADA = {"Branca": COR_BRANCA, "Preta": COR_PRETA, "Parda": COR_PARDA, "Indígena": COR_INDIGENA}

SUPERFICIE = "#fcfcfb"
TINTA_PRIMARIA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_MUTED = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"


def _novo_eixo(figsize=(10, 5.5)):
    """Cria fig/ax com o estilo padrão do projeto (superfície, spines, cor de fundo)."""
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    fig.patch.set_facecolor(SUPERFICIE)
    ax.set_facecolor(SUPERFICIE)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(EIXO)
    ax.tick_params(axis="both", colors=TINTA_MUTED, labelsize=9.5, length=0)
    return fig, ax


def _titulo(ax, titulo: str, subtitulo: str) -> None:
    ax.set_title(titulo, fontsize=14, fontweight="bold", color=TINTA_PRIMARIA, loc="left", pad=32)
    ax.text(0, 1.03, subtitulo, transform=ax.transAxes, fontsize=9.5, color=TINTA_SECUNDARIA, ha="left")


def _rodape(fig, nota: str = "Fonte: IBGE, PNAD Contínua Trimestral (microdados). Elaboração própria.") -> None:
    fig.text(0.01, 0.01, nota, fontsize=8, color=TINTA_MUTED)


def _trimestre_mais_recente(df: pd.DataFrame) -> tuple[int, int]:
    """(ano, trimestre) do trimestre mais recente presente no df.

    NÃO usar df[["ano","trimestre"]].max() — isso pega o máximo de cada coluna
    independentemente e pode devolver uma combinação (ano, trimestre) que não existe
    (ex.: (2026, 4) quando 2026 só tem T1/T2 e T4=4 veio de outro ano).
    """
    ultima_linha = df.sort_values(["ano", "trimestre"]).iloc[-1]
    return int(ultima_linha["ano"]), int(ultima_linha["trimestre"])


def _salvar(fig, nome_arquivo: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destino = OUTPUT_DIR / nome_arquivo
    fig.savefig(destino, facecolor=SUPERFICIE)
    plt.close(fig)
    return destino


def _media_ponderada_por_grupo(df: pd.DataFrame, col_valor: str, by: list[str]) -> pd.DataFrame:
    """Média de col_valor ponderada por populacao_estimada, colapsando tudo que não está em `by`."""
    if df.empty:
        return pd.DataFrame(columns=by + [col_valor])
    return (
        df.groupby(by)
        .apply(lambda g: (g[col_valor] * g["populacao_estimada"]).sum() / g["populacao_estimada"].sum())
        .rename(col_valor)
        .reset_index()
    )


def _combinar_negra(df: pd.DataFrame, col_valor: str, by: list[str]) -> pd.DataFrame:
    """Combina Preta+Parda em 'Negra (Preta+Parda)'; Branca/Indígena passam pela mesma
    média ponderada (colapsando qualquer dimensão fora de `by`, ex.: faixa_etaria) —
    todas as raças precisam do mesmo tratamento, senão o pivot_table do gráfico faria
    média NÃO ponderada por engano para quem não passasse por aqui.
    """
    negra = _media_ponderada_por_grupo(df[df["raca_cor"].isin(["Preta", "Parda"])], col_valor, by)
    negra["raca_cor"] = "Negra (Preta+Parda)"

    partes = [negra]
    for raca in ("Branca", "Indígena"):
        parte = _media_ponderada_por_grupo(df[df["raca_cor"] == raca], col_valor, by)
        parte["raca_cor"] = raca
        partes.append(parte)

    return pd.concat([p[by + ["raca_cor", col_valor]] for p in partes], ignore_index=True)


def _media_ponderada_por_data(df: pd.DataFrame) -> pd.Series:
    """Colapsa sexo x faixa_etaria numa média ponderada por data (populacao_estimada)."""
    return df.groupby("data").apply(
        lambda g: (g["renda_habitual_real_media"] * g["populacao_estimada"]).sum() / g["populacao_estimada"].sum()
    )


def _preparar_serie_brasil(renda: pd.DataFrame) -> pd.DataFrame:
    """Monta a série Branca / Negra (Preta+Parda) / Indígena, renda habitual real, Brasil.

    O nível 'brasil' de renda.parquet ainda tem uma linha por sexo x faixa_etaria —
    aqui colapsamos isso numa única média ponderada por trimestre e raça.
    """
    r = renda[renda["nivel_geografico"] == "brasil"].copy()
    r["data"] = pd.to_datetime(
        r["ano"].astype(str) + "-" + ((r["trimestre"] - 1) * 3 + 1).astype(str) + "-01"
    )

    branca = _media_ponderada_por_data(r[r["raca_cor"] == "Branca"])
    indigena = _media_ponderada_por_data(r[r["raca_cor"] == "Indígena"])
    negra = _media_ponderada_por_data(r[r["raca_cor"].isin(["Preta", "Parda"])])

    serie = pd.DataFrame({"Branca": branca, "Negra (Preta+Parda)": negra, "Indígena": indigena}).sort_index()

    # Indígena tem amostra pequena por trimestre (~0,6% da amostra nacional) e a série
    # trimestral bruta é muito ruidosa para mostrar tendência — suaviza com média móvel
    # de 4 trimestres (ver docs/LIMITACOES_E_METODOLOGIA.md).
    serie["Indígena"] = serie["Indígena"].rolling(4, center=True, min_periods=2).mean()

    return serie


def grafico_renda_por_raca(renda: pd.DataFrame) -> Path:
    serie = _preparar_serie_brasil(renda)

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)
    fig.patch.set_facecolor(SUPERFICIE)
    ax.set_facecolor(SUPERFICIE)

    # faixa sombreada: período de coleta por telefone durante a pandemia (queda de amostra)
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=GRADE, alpha=0.6, zorder=0)

    topo = serie.max().max() * 1.22
    base = serie.min().min() * 0.92
    ax.set_ylim(base, topo)

    linhas = [
        ("Branca", COR_BRANCA),
        ("Negra (Preta+Parda)", COR_NEGRA),
        ("Indígena (média móvel 4 trim.)", COR_INDIGENA),
    ]
    colunas_serie = ["Branca", "Negra (Preta+Parda)", "Indígena"]
    for coluna, (_, cor) in zip(colunas_serie, linhas):
        ax.plot(serie.index, serie[coluna], color=cor, linewidth=2, solid_capstyle="round", zorder=3)

    # Rótulos no fim de cada linha, com separação mínima entre eles pra não colidir
    # quando duas séries terminam com valores próximos (caso de Negra/Indígena aqui).
    ultimo_x = serie.index[-1]
    valores_finais = sorted(
        ((serie[coluna].iloc[-1], rotulo, cor) for coluna, (rotulo, cor) in zip(colunas_serie, linhas))
    )
    espaco_minimo = (topo - base) * 0.045
    for i in range(1, len(valores_finais)):
        anterior_y = valores_finais[i - 1][0]
        if valores_finais[i][0] - anterior_y < espaco_minimo:
            valores_finais[i] = (anterior_y + espaco_minimo, *valores_finais[i][1:])

    for y_rotulo, rotulo, cor in valores_finais:
        ax.annotate(
            rotulo,
            xy=(ultimo_x, y_rotulo),
            xytext=(8, 0),
            textcoords="offset points",
            color=cor,
            fontsize=10,
            fontweight="bold",
            va="center",
        )

    ax.text(
        pd.Timestamp("2020-06-15"), topo * 0.93,
        "pandemia\n(coleta por telefone)",
        fontsize=8, color=TINTA_MUTED, ha="center", va="top",
    )

    ax.set_title(
        "Renda habitual do trabalho, por raça — Brasil (2012–2026)",
        fontsize=14, fontweight="bold", color=TINTA_PRIMARIA, loc="left", pad=32,
    )
    ax.text(
        0, 1.03,
        "R$ reais, a preços do trimestre mais recente (deflator oficial IBGE) · PNAD Contínua Trimestral",
        transform=ax.transAxes, fontsize=9.5, color=TINTA_SECUNDARIA, ha="left",
    )

    ax.yaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(EIXO)
    ax.tick_params(axis="both", colors=TINTA_MUTED, labelsize=9.5, length=0)
    ax.set_xlim(serie.index.min(), serie.index.max() + pd.Timedelta(days=270))

    fonte = "Fonte: IBGE, PNAD Contínua Trimestral (microdados). Elaboração própria."
    fig.text(0.01, 0.01, fonte, fontsize=8, color=TINTA_MUTED)

    fig.tight_layout(rect=(0, 0.03, 1, 1))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destino = OUTPUT_DIR / "renda_por_raca.png"
    fig.savefig(destino, facecolor=SUPERFICIE)
    plt.close(fig)
    return destino


def grafico_renda_por_raca_detalhada(renda: pd.DataFrame) -> Path:
    """Igual ao gráfico de renda por raça, mas SEM combinar Preta+Parda em 'Negra' —
    pra ver se as duas populações se movem juntas ou têm trajetórias diferentes."""
    r = renda[renda["nivel_geografico"] == "brasil"].copy()
    r["data"] = pd.to_datetime(
        r["ano"].astype(str) + "-" + ((r["trimestre"] - 1) * 3 + 1).astype(str) + "-01"
    )
    racas = ["Branca", "Preta", "Parda", "Indígena"]
    serie = pd.DataFrame({raca: _media_ponderada_por_data(r[r["raca_cor"] == raca]) for raca in racas}).sort_index()
    # Indígena tem amostra pequena — mesma suavização dos outros gráficos
    serie["Indígena"] = serie["Indígena"].rolling(4, center=True, min_periods=2).mean()

    fig, ax = _novo_eixo()
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=GRADE, alpha=0.6, zorder=0)

    topo = serie.max().max() * 1.22
    base = serie.min().min() * 0.92
    ax.set_ylim(base, topo)

    for raca in racas:
        ax.plot(
            serie.index, serie[raca], color=CORES_RACA_DETALHADA[raca], linewidth=2,
            solid_capstyle="round", zorder=3,
        )

    ultimo_x = serie.index[-1]
    valores_finais = sorted((serie[raca].iloc[-1], raca, CORES_RACA_DETALHADA[raca]) for raca in racas)
    espaco_minimo = (topo - base) * 0.045
    for i in range(1, len(valores_finais)):
        anterior_y = valores_finais[i - 1][0]
        if valores_finais[i][0] - anterior_y < espaco_minimo:
            valores_finais[i] = (anterior_y + espaco_minimo, *valores_finais[i][1:])
    for y_rotulo, rotulo, cor in valores_finais:
        ax.annotate(
            rotulo, xy=(ultimo_x, y_rotulo), xytext=(8, 0), textcoords="offset points",
            color=cor, fontsize=10, fontweight="bold", va="center",
        )

    ax.text(
        pd.Timestamp("2020-06-15"), topo * 0.93, "pandemia\n(coleta por telefone)",
        fontsize=8, color=TINTA_MUTED, ha="center", va="top",
    )

    _titulo(
        ax,
        "Renda habitual do trabalho, Preta e Parda separadas — Brasil (2012–2026)",
        "R$ reais, a preços do trimestre mais recente (deflator oficial IBGE) · PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    ax.set_xlim(serie.index.min(), serie.index.max() + pd.Timedelta(days=270))

    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "renda_por_raca_detalhada.png")


def grafico_renda_por_raca_genero(renda: pd.DataFrame) -> Path:
    r = renda[renda["nivel_geografico"] == "brasil"].copy()
    r["data"] = pd.to_datetime(
        r["ano"].astype(str) + "-" + ((r["trimestre"] - 1) * 3 + 1).astype(str) + "-01"
    )
    combinado = _combinar_negra(r, "renda_habitual_real_media", by=["data", "sexo"])
    # já vem uma linha por (data, sexo, raca_cor) — Negra combinada, Branca/Indígena originais
    pivot = combinado.pivot_table(
        index="data", columns=["raca_cor", "sexo"], values="renda_habitual_real_media"
    ).sort_index()
    # Indígena separado por gênero fica com amostra bem pequena — suaviza mais
    for sexo in ("Homem", "Mulher"):
        if ("Indígena", sexo) in pivot.columns:
            pivot[("Indígena", sexo)] = pivot[("Indígena", sexo)].rolling(4, center=True, min_periods=2).mean()

    fig, ax = _novo_eixo(figsize=(12, 5.5))
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=GRADE, alpha=0.6, zorder=0)

    topo = pivot.max().max() * 1.28
    base = pivot.min().min() * 0.9
    ax.set_ylim(base, topo)

    ordem_raca = ["Branca", "Negra (Preta+Parda)", "Indígena"]
    estilos = {"Homem": "--", "Mulher": "-"}
    rotulo_sexo = {"Homem": "Homens", "Mulher": "Mulheres"}
    rotulos_finais = []
    for raca in ordem_raca:
        for sexo, tracejado in estilos.items():
            if (raca, sexo) not in pivot.columns:
                continue
            cor = CORES_RACA[raca]
            ax.plot(
                pivot.index, pivot[(raca, sexo)], color=cor, linewidth=2,
                linestyle=tracejado, solid_capstyle="round", dash_capstyle="round", zorder=3,
            )
            rotulos_finais.append(
                (pivot[(raca, sexo)].iloc[-1], f"{raca.split(' ')[0]} · {rotulo_sexo[sexo]}", cor)
            )

    ultimo_x = pivot.index[-1]
    rotulos_finais.sort()
    espaco_minimo = (topo - base) * 0.05
    for i in range(1, len(rotulos_finais)):
        anterior_y = rotulos_finais[i - 1][0]
        if rotulos_finais[i][0] - anterior_y < espaco_minimo:
            rotulos_finais[i] = (anterior_y + espaco_minimo, *rotulos_finais[i][1:])
    for y_rotulo, rotulo, cor in rotulos_finais:
        ax.annotate(
            rotulo, xy=(ultimo_x, y_rotulo), xytext=(8, 0), textcoords="offset points",
            color=cor, fontsize=9, fontweight="bold", va="center",
        )

    ax.text(
        pd.Timestamp("2020-06-15"), topo * 0.95, "pandemia\n(coleta por telefone)",
        fontsize=8, color=TINTA_MUTED, ha="center", va="top",
    )

    _titulo(
        ax,
        "Renda habitual do trabalho, por raça e gênero — Brasil (2012–2026)",
        "R$ reais, a preços do trimestre mais recente (deflator oficial IBGE) · linha cheia "
        "= mulheres, tracejada = homens · PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    ax.set_xlim(pivot.index.min(), pivot.index.max() + pd.Timedelta(days=320))

    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "renda_por_raca_genero.png")


def grafico_escolaridade_por_raca_genero(esc: pd.DataFrame) -> Path:
    """% com superior completo, por raça x gênero, Brasil, trimestre mais recente."""
    ultimo_ano, ultimo_trimestre = _trimestre_mais_recente(esc)
    e = esc[
        (esc["nivel_geografico"] == "brasil")
        & (esc["ano"] == ultimo_ano)
        & (esc["trimestre"] == ultimo_trimestre)
    ].copy()

    combinado = _combinar_negra_multi(e, "populacao_estimada", by=["sexo", "nivel_instrucao"])
    total = combinado.groupby(["raca_cor", "sexo"])["populacao_estimada"].sum().rename("total")
    superior = (
        combinado[combinado["nivel_instrucao"] == "Superior completo"]
        .groupby(["raca_cor", "sexo"])["populacao_estimada"].sum().rename("superior")
    )
    pct = (superior / total * 100).rename("pct_superior").reset_index()

    ordem_raca = ["Branca", "Negra (Preta+Parda)", "Indígena"]
    pct["raca_cor"] = pd.Categorical(pct["raca_cor"], categories=ordem_raca, ordered=True)
    pct = pct.sort_values(["raca_cor", "sexo"])

    fig, ax = _novo_eixo(figsize=(9, 5.5))
    largura = 0.35
    x = np.arange(len(ordem_raca))
    # alpha diferencia gênero dentro de cada cor de raça: homens = tom mais claro (0.55),
    # mulheres = cor cheia (1.0) — mesma convenção em todo o gráfico.
    alpha_por_sexo = {"Homem": 0.55, "Mulher": 1.0}
    for i, sexo in enumerate(["Homem", "Mulher"]):
        valores = [pct[(pct["raca_cor"] == r) & (pct["sexo"] == sexo)]["pct_superior"].sum() for r in ordem_raca]
        cores = [CORES_RACA[r] for r in ordem_raca]
        deslocamento = (i - 0.5) * largura
        barras = ax.bar(
            x + deslocamento, valores, largura, color=cores, alpha=alpha_por_sexo[sexo],
            edgecolor=SUPERFICIE, linewidth=1.5, zorder=3,
        )
        for barra, v in zip(barras, valores):
            ax.text(
                barra.get_x() + barra.get_width() / 2, v + 0.6, f"{v:.0f}%",
                ha="center", fontsize=9, color=TINTA_SECUNDARIA,
            )

    legenda = [
        Patch(facecolor=TINTA_MUTED, alpha=alpha_por_sexo["Homem"], label="Homens"),
        Patch(facecolor=TINTA_MUTED, alpha=alpha_por_sexo["Mulher"], label="Mulheres"),
    ]
    ax.legend(handles=legenda, loc="upper right", frameon=False, fontsize=9.5)

    ax.set_xticks(x)
    ax.set_xticklabels([r.split(" ")[0] for r in ordem_raca], fontsize=10.5, color=TINTA_PRIMARIA)
    ax.set_ylim(0, pct["pct_superior"].max() * 1.35)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")

    _titulo(
        ax,
        "Superior completo, por raça e gênero — Brasil",
        f"% da população 14+ anos · {ultimo_trimestre}º trimestre de {ultimo_ano} · PNAD Contínua Trimestral",
    )
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)

    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "escolaridade_por_raca_genero.png")


def _combinar_negra_multi(df: pd.DataFrame, col_valor: str, by: list[str]) -> pd.DataFrame:
    """Como _combinar_negra, mas soma (não pondera) — usado para contagens/população."""
    negra = (
        df[df["raca_cor"].isin(["Preta", "Parda"])]
        .groupby(by)[col_valor].sum().reset_index()
    )
    negra["raca_cor"] = "Negra (Preta+Parda)"
    outras = df[df["raca_cor"].isin(["Branca", "Indígena"])][by + ["raca_cor", col_valor]].copy()
    return pd.concat([outras, negra[by + ["raca_cor", col_valor]]], ignore_index=True)


def grafico_renda_por_faixa_etaria(renda: pd.DataFrame) -> Path:
    """Renda habitual real por faixa etária, raça (Branca/Negra) e gênero — trimestre mais recente."""
    ultimo_ano, ultimo_trimestre = _trimestre_mais_recente(renda)
    r = renda[
        (renda["nivel_geografico"] == "brasil")
        & (renda["ano"] == ultimo_ano)
        & (renda["trimestre"] == ultimo_trimestre)
        & (renda["raca_cor"].isin(["Branca", "Preta", "Parda"]))
    ].copy()
    combinado = _combinar_negra(r, "renda_habitual_real_media", by=["sexo", "faixa_etaria"])

    faixas = ["14-17", "18-24", "25-39", "40-59", "60+"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5), dpi=150, sharey=True)
    fig.patch.set_facecolor(SUPERFICIE)

    for ax, sexo in zip(axes, ["Homem", "Mulher"]):
        ax.set_facecolor(SUPERFICIE)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color(EIXO)
        ax.tick_params(axis="both", colors=TINTA_MUTED, labelsize=9.5, length=0)

        sub = combinado[combinado["sexo"] == sexo]
        x = np.arange(len(faixas))
        largura = 0.38
        for i, raca in enumerate(["Branca", "Negra (Preta+Parda)"]):
            valores = [
                sub[(sub["raca_cor"] == raca) & (sub["faixa_etaria"] == f)]["renda_habitual_real_media"].sum()
                for f in faixas
            ]
            deslocamento = (i - 0.5) * largura
            ax.bar(x + deslocamento, valores, largura, color=CORES_RACA[raca], zorder=3, label=raca)

        ax.set_xticks(x)
        ax.set_xticklabels(faixas, fontsize=9.5)
        ax.set_title("Homens" if sexo == "Homem" else "Mulheres", fontsize=11, color=TINTA_SECUNDARIA, loc="left")
        ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
        ax.yaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))

    axes[0].legend(
        loc="upper left", frameon=False, fontsize=9.5,
        labelcolor=[CORES_RACA["Branca"], CORES_RACA["Negra (Preta+Parda)"]],
    )

    fig.suptitle(
        "Renda habitual real por faixa etária, raça e gênero — Brasil",
        fontsize=14, fontweight="bold", color=TINTA_PRIMARIA, x=0.01, ha="left",
    )
    fig.text(
        0.01, 0.92,
        f"R$ reais, a preços do trimestre mais recente · {ultimo_trimestre}º trimestre de {ultimo_ano} "
        "· Indígena fora deste corte (amostra insuficiente por faixa etária) · PNAD Contínua Trimestral",
        fontsize=9.5, color=TINTA_SECUNDARIA,
    )

    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 0.88))
    return _salvar(fig, "renda_por_faixa_etaria_raca_genero.png")


NIVEIS_INSTRUCAO_ORDEM = [
    "Sem instrução e menos de 1 ano de estudo",
    "Fundamental incompleto ou equivalente",
    "Fundamental completo ou equivalente",
    "Médio incompleto ou equivalente",
    "Médio completo ou equivalente",
    "Superior incompleto ou equivalente",
    "Superior completo",
]
NIVEIS_INSTRUCAO_ROTULO_CURTO = {
    "Sem instrução e menos de 1 ano de estudo": "Sem instrução",
    "Fundamental incompleto ou equivalente": "Fundamental incompl.",
    "Fundamental completo ou equivalente": "Fundamental compl.",
    "Médio incompleto ou equivalente": "Médio incompl.",
    "Médio completo ou equivalente": "Médio compl.",
    "Superior incompleto ou equivalente": "Superior incompl.",
    "Superior completo": "Superior compl.",
}


def grafico_renda_por_raca_escolaridade(rpe: pd.DataFrame, sexo: str | None = None) -> Path:
    """Renda habitual real por nível de instrução x raça, trimestre mais recente.

    sexo=None junta Homens+Mulheres; sexo='Homem'/'Mulher' filtra só um gênero
    (gera um arquivo .png separado pra cada caso — mais legível que amontoar as
    3 raças x 2 gêneros x 7 níveis num só gráfico).
    """
    ultimo_ano, ultimo_trimestre = _trimestre_mais_recente(rpe)
    r = rpe[
        (rpe["nivel_geografico"] == "brasil") & (rpe["ano"] == ultimo_ano) & (rpe["trimestre"] == ultimo_trimestre)
    ].copy()
    if sexo is not None:
        r = r[r["sexo"] == sexo]

    combinado = _combinar_negra(r, "renda_habitual_real_media", by=["nivel_instrucao"])

    ordem_raca = ["Branca", "Negra (Preta+Parda)", "Indígena"]
    y = np.arange(len(NIVEIS_INSTRUCAO_ORDEM))
    altura = 0.26

    fig, ax = _novo_eixo(figsize=(10, 6.5))
    for i, raca in enumerate(ordem_raca):
        valores = [
            combinado[(combinado["raca_cor"] == raca) & (combinado["nivel_instrucao"] == n)]["renda_habitual_real_media"].sum()
            for n in NIVEIS_INSTRUCAO_ORDEM
        ]
        deslocamento = (1 - i) * altura
        ax.barh(y + deslocamento, valores, altura, color=CORES_RACA[raca], zorder=3, label=raca)
        for yi, v in zip(y + deslocamento, valores):
            if v > 0:
                ax.text(v + max([vv for vv in valores if vv]) * 0.015, yi, f"R$ {v:,.0f}".replace(",", "."),
                        va="center", fontsize=8, color=TINTA_SECUNDARIA)

    ax.set_yticks(y)
    ax.set_yticklabels([NIVEIS_INSTRUCAO_ROTULO_CURTO[n] for n in NIVEIS_INSTRUCAO_ORDEM], fontsize=10)
    ax.invert_yaxis()
    ax.set_xlim(0, combinado["renda_habitual_real_media"].max() * 1.2)
    ax.xaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.legend(loc="upper right", frameon=False, fontsize=9.5)

    sufixo_titulo = {"Homem": " — Homens", "Mulher": " — Mulheres", None: ""}[sexo]
    _titulo(
        ax,
        f"Renda habitual real por nível de instrução e raça{sufixo_titulo} — Brasil",
        f"R$ reais, a preços do trimestre mais recente · {ultimo_trimestre}º trimestre de {ultimo_ano} "
        "· PNAD Contínua Trimestral",
    )
    ax.grid(axis="x", color=GRADE, linewidth=0.8, zorder=0)

    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    sufixo_arquivo = {"Homem": "_homens", "Mulher": "_mulheres", None: ""}[sexo]
    return _salvar(fig, f"renda_por_raca_escolaridade{sufixo_arquivo}.png")


def main() -> None:
    renda = pd.read_parquet(REPO_ROOT / "data" / "processed" / "renda.parquet")
    esc = pd.read_parquet(REPO_ROOT / "data" / "processed" / "escolaridade.parquet")
    rpe = pd.read_parquet(REPO_ROOT / "data" / "processed" / "renda_por_escolaridade.parquet")

    for destino in [
        grafico_renda_por_raca(renda),
        grafico_renda_por_raca_detalhada(renda),
        grafico_renda_por_raca_genero(renda),
        grafico_escolaridade_por_raca_genero(esc),
        grafico_renda_por_faixa_etaria(renda),
        grafico_renda_por_raca_escolaridade(rpe, sexo=None),
        grafico_renda_por_raca_escolaridade(rpe, sexo="Homem"),
        grafico_renda_por_raca_escolaridade(rpe, sexo="Mulher"),
    ]:
        print(f"Gráfico salvo em: {destino.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
