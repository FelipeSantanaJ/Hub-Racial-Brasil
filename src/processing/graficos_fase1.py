"""Gera as visualizações exploratórias da Fase 1 (Etapa 6).

Lê data/processed/{renda,escolaridade}.parquet e produz os gráficos comparativos
Branca vs. Negra vs. Indígena — geral, por gênero, e cruzando com
faixa etária — salvos em docs/img/ para uso no README.

Uso:
    python -m src.processing.graficos_fase1
"""
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "docs" / "img"

# Paleta categórica validada (ver skill de dataviz) — ordem fixa, não trocar por raça.
COR_BRANCA = "#2a78d6"    # slot 1 (azul)
COR_NEGRA = "#eb6834"     # slot 2 (laranja) — usada também para "Preta" nos gráficos detalhados
COR_INDIGENA = "#1baf7a"  # slot 3 (aqua)
CORES_RACA = {"Branca": COR_BRANCA, "Negra": COR_NEGRA, "Indígena": COR_INDIGENA}

# Cores do gráfico Preta vs. Parda (validadas à parte, all-pairs PASS junto com
# Branca/Indígena — ver skill de dataviz, ainda que este gráfico não mostre as duas).
COR_PRETA = COR_NEGRA
COR_PARDA = "#4a3aa7"     # slot 7 (violeta)

SUPERFICIE = "#fcfcfb"
TINTA_PRIMARIA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_MUTED = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"


def _slug(texto: str) -> str:
    """ASCII puro pra nome de arquivo (sem acento) — evita problemas de link/URL
    quando o gráfico é embutido no README/GitHub."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sem_acento.lower().replace(" ", "_").replace(".", "").replace("-", "_")


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
    """Combina Preta+Parda em 'Negra'; Branca/Indígena passam pela mesma
    média ponderada (colapsando qualquer dimensão fora de `by`, ex.: faixa_etaria) —
    todas as raças precisam do mesmo tratamento, senão o pivot_table do gráfico faria
    média NÃO ponderada por engano para quem não passasse por aqui.
    """
    negra = _media_ponderada_por_grupo(df[df["raca_cor"].isin(["Preta", "Parda"])], col_valor, by)
    negra["raca_cor"] = "Negra"

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
    """Monta a série Branca / Negra / Indígena, renda habitual real, Brasil.

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

    serie = pd.DataFrame({"Branca": branca, "Negra": negra, "Indígena": indigena}).sort_index()

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
        ("Negra", COR_NEGRA),
        ("Indígena (média móvel 4 trim.)", COR_INDIGENA),
    ]
    colunas_serie = ["Branca", "Negra", "Indígena"]
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


def _media_ponderada_por_data_generico(df: pd.DataFrame, coluna_valor: str) -> pd.Series:
    """Como _media_ponderada_por_data, mas com a coluna de valor parametrizada."""
    if df.empty:
        return pd.Series(dtype=float)
    return df.groupby("data").apply(
        lambda g: (g[coluna_valor] * g["populacao_estimada"]).sum() / g["populacao_estimada"].sum()
    )


def _serie_por_raca(
    df: pd.DataFrame, racas: list[str], coluna_valor: str = "renda_habitual_real_media",
    filtro_extra: dict | None = None, sexo: str | None = None, suavizar: set[str] | None = None,
) -> pd.DataFrame:
    """Série temporal (index=data) com uma coluna por raça em `racas`.

    'Negra' em `racas` soma Preta+Parda (ponderado). Filtra
    nivel_geografico='brasil' (se a coluna existir), qualquer `filtro_extra`
    ({coluna: valor}, ex.: {'faixa_etaria': '25-39'}) e `sexo` se informados.
    `suavizar` é o conjunto de nomes de raça que recebem média móvel de 4
    trimestres (tipicamente Indígena, por causa da amostra pequena).
    """
    r = df.copy()
    if "nivel_geografico" in r.columns:
        r = r[r["nivel_geografico"] == "brasil"]
    if filtro_extra:
        for col, val in filtro_extra.items():
            r = r[r[col] == val]
    if sexo is not None:
        r = r[r["sexo"] == sexo]
    r["data"] = pd.to_datetime(
        r["ano"].astype(str) + "-" + ((r["trimestre"] - 1) * 3 + 1).astype(str) + "-01"
    )

    colunas = {}
    for raca in racas:
        sub = r[r["raca_cor"].isin(["Preta", "Parda"])] if raca == "Negra" else r[r["raca_cor"] == raca]
        colunas[raca] = _media_ponderada_por_data_generico(sub, coluna_valor)
    serie = pd.DataFrame(colunas).sort_index()

    for raca in suavizar or set():
        if raca in serie.columns:
            serie[raca] = serie[raca].rolling(4, center=True, min_periods=2).mean()
    return serie


def _grafico_serie_temporal(
    serie: pd.DataFrame, cores: dict[str, str], titulo: str, subtitulo: str, nome_arquivo: str,
    rotulos: dict[str, str] | None = None,
) -> Path:
    """Plota uma série temporal (colunas = raças) no estilo padrão do projeto —
    linhas, rótulos diretos sem colisão, faixa da pandemia, grade horizontal."""
    rotulos = rotulos or {c: c for c in serie.columns}
    fig, ax = _novo_eixo(figsize=(11, 5.5))
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=GRADE, alpha=0.6, zorder=0)

    topo = serie.max().max() * 1.22
    base = serie.min().min() * 0.9 if serie.min().min() > 0 else 0
    ax.set_ylim(base, topo)

    for coluna in serie.columns:
        ax.plot(serie.index, serie[coluna], color=cores[coluna], linewidth=2, solid_capstyle="round", zorder=3)

    ultimo_x = serie.index[-1]
    valores_finais = sorted(
        (serie[coluna].iloc[-1], rotulos[coluna], cores[coluna])
        for coluna in serie.columns if pd.notna(serie[coluna].iloc[-1])
    )
    espaco_minimo = (topo - base) * 0.05
    for i in range(1, len(valores_finais)):
        anterior_y = valores_finais[i - 1][0]
        if valores_finais[i][0] - anterior_y < espaco_minimo:
            valores_finais[i] = (anterior_y + espaco_minimo, *valores_finais[i][1:])
    for y_rotulo, rotulo, cor in valores_finais:
        ax.annotate(
            rotulo, xy=(ultimo_x, y_rotulo), xytext=(8, 0), textcoords="offset points",
            color=cor, fontsize=9.5, fontweight="bold", va="center",
        )

    ax.text(
        pd.Timestamp("2020-06-15"), topo * 0.95, "pandemia\n(coleta por telefone)",
        fontsize=8, color=TINTA_MUTED, ha="center", va="top",
    )

    _titulo(ax, titulo, subtitulo)
    ax.yaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    ax.set_xlim(serie.index.min(), serie.index.max() + pd.Timedelta(days=280))

    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, nome_arquivo)


def grafico_renda_preta_parda(renda: pd.DataFrame) -> Path:
    """Só a população negra: Preta vs. Parda, sem Branca/Indígena — pra ver se as
    duas populações que compõem 'Negra' se movem juntas ou têm trajetórias diferentes."""
    serie = _serie_por_raca(renda, ["Preta", "Parda"])
    cores = {"Preta": COR_PRETA, "Parda": COR_PARDA}
    return _grafico_serie_temporal(
        serie, cores,
        "Renda habitual do trabalho — Preta vs. Parda — Brasil (2012–2026)",
        "R$ reais, a preços do trimestre mais recente (deflator oficial IBGE) · PNAD Contínua Trimestral",
        "renda_preta_parda.png",
    )


def grafico_preta_parda_sexo(renda: pd.DataFrame, sexo: str) -> Path:
    """Preta vs. Parda, um único gênero."""
    serie = _serie_por_raca(renda, ["Preta", "Parda"], sexo=sexo)
    cores = {"Preta": COR_PRETA, "Parda": COR_PARDA}
    rotulo_sexo = {"Homem": "Homens", "Mulher": "Mulheres"}[sexo]
    sufixo = {"Homem": "homens", "Mulher": "mulheres"}[sexo]
    return _grafico_serie_temporal(
        serie, cores,
        f"Renda habitual do trabalho — Preta vs. Parda — {rotulo_sexo} — Brasil (2012–2026)",
        "R$ reais, a preços do trimestre mais recente (deflator oficial IBGE) · PNAD Contínua Trimestral",
        f"renda_preta_parda_{sufixo}.png",
    )


def grafico_preta_parda_genero_combinado(renda: pd.DataFrame) -> Path:
    """Preta vs. Parda, homens e mulheres juntos (4 linhas: cor = Preta/Parda,
    traço = gênero — mesma convenção do gráfico raça x gênero: sólido = mulheres,
    tracejado = homens)."""
    r = renda[renda["nivel_geografico"] == "brasil"].copy()
    r["data"] = pd.to_datetime(
        r["ano"].astype(str) + "-" + ((r["trimestre"] - 1) * 3 + 1).astype(str) + "-01"
    )
    base_cols = {}
    for raca in ("Preta", "Parda"):
        for sexo in ("Homem", "Mulher"):
            sub = r[(r["raca_cor"] == raca) & (r["sexo"] == sexo)]
            base_cols[(raca, sexo)] = _media_ponderada_por_data_generico(sub, "renda_habitual_real_media")
    pivot = pd.DataFrame(base_cols).sort_index()

    cores = {"Preta": COR_PRETA, "Parda": COR_PARDA}
    estilos = {"Homem": "--", "Mulher": "-"}
    rotulo_sexo = {"Homem": "Homens", "Mulher": "Mulheres"}

    fig, ax = _novo_eixo(figsize=(11, 5.5))
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=GRADE, alpha=0.6, zorder=0)
    topo, base = pivot.max().max() * 1.28, pivot.min().min() * 0.9
    ax.set_ylim(base, topo)

    for raca in ("Preta", "Parda"):
        for sexo, tracejado in estilos.items():
            ax.plot(
                pivot.index, pivot[(raca, sexo)], color=cores[raca], linewidth=2,
                linestyle=tracejado, solid_capstyle="round", dash_capstyle="round", zorder=3,
            )

    ultimo_x = pivot.index[-1]
    finais = sorted(
        (pivot[(raca, sexo)].iloc[-1], f"{raca} · {rotulo_sexo[sexo]}", cores[raca])
        for raca in ("Preta", "Parda") for sexo in ("Homem", "Mulher")
    )
    espaco_minimo = (topo - base) * 0.05
    for i in range(1, len(finais)):
        anterior_y = finais[i - 1][0]
        if finais[i][0] - anterior_y < espaco_minimo:
            finais[i] = (anterior_y + espaco_minimo, *finais[i][1:])
    for y_rotulo, rotulo, cor in finais:
        ax.annotate(
            rotulo, xy=(ultimo_x, y_rotulo), xytext=(8, 0), textcoords="offset points",
            color=cor, fontsize=9.5, fontweight="bold", va="center",
        )

    _titulo(
        ax, "Renda habitual do trabalho — Preta vs. Parda, por gênero — Brasil (2012–2026)",
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
    return _salvar(fig, "renda_preta_parda_genero.png")


def grafico_preta_parda_faixa_etaria_combinada(renda: pd.DataFrame) -> Path:
    """Preta vs. Parda por faixa etária, snapshot do trimestre mais recente."""
    ultimo_ano, ultimo_trimestre = _trimestre_mais_recente(renda)
    r = renda[
        (renda["nivel_geografico"] == "brasil") & (renda["ano"] == ultimo_ano) & (renda["trimestre"] == ultimo_trimestre)
        & (renda["raca_cor"].isin(["Preta", "Parda"]))
    ].copy()
    combinado = _media_ponderada_por_grupo(r, "renda_habitual_real_media", by=["raca_cor", "faixa_etaria"])

    x = np.arange(len(FAIXAS_ETARIAS_ORDEM))
    largura = 0.35
    fig, ax = _novo_eixo(figsize=(10, 5.5))
    for i, raca in enumerate(["Preta", "Parda"]):
        valores = [
            combinado[(combinado["raca_cor"] == raca) & (combinado["faixa_etaria"] == f)]["renda_habitual_real_media"].sum()
            for f in FAIXAS_ETARIAS_ORDEM
        ]
        deslocamento = (i - 0.5) * largura
        cor = {"Preta": COR_PRETA, "Parda": COR_PARDA}[raca]
        ax.bar(x + deslocamento, valores, largura, color=cor, zorder=3, label=raca)

    ax.set_xticks(x)
    ax.set_xticklabels(FAIXAS_ETARIAS_ORDEM, fontsize=10.5)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    _titulo(
        ax, "Renda habitual real, Preta vs. Parda, por faixa etária — Brasil",
        f"R$ reais, a preços do trimestre mais recente · {ultimo_trimestre}º trimestre de {ultimo_ano} "
        "· PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "renda_preta_parda_faixa_etaria.png")


def graficos_preta_parda_faixa_etaria_individual(renda: pd.DataFrame) -> list[Path]:
    destinos = []
    for faixa in FAIXAS_ETARIAS_ORDEM:
        serie = _serie_por_raca(renda, ["Preta", "Parda"], filtro_extra={"faixa_etaria": faixa})
        slug = faixa.replace("+", "mais").replace("-", "_")
        destinos.append(_grafico_serie_temporal(
            serie, {"Preta": COR_PRETA, "Parda": COR_PARDA},
            f"Renda habitual, Preta vs. Parda, {faixa} anos — Brasil (2012–2026)",
            "R$ reais, a preços do trimestre mais recente (deflator oficial IBGE) · PNAD Contínua Trimestral",
            f"renda_preta_parda_faixa_{slug}.png",
        ))
    return destinos


def grafico_preta_parda_escolaridade_combinada(rpe: pd.DataFrame) -> Path:
    """Preta vs. Parda por nível de instrução, snapshot do trimestre mais recente."""
    ultimo_ano, ultimo_trimestre = _trimestre_mais_recente(rpe)
    r = rpe[
        (rpe["nivel_geografico"] == "brasil") & (rpe["ano"] == ultimo_ano) & (rpe["trimestre"] == ultimo_trimestre)
        & (rpe["raca_cor"].isin(["Preta", "Parda"]))
    ].copy()

    y = np.arange(len(NIVEIS_INSTRUCAO_ORDEM))
    altura = 0.35
    fig, ax = _novo_eixo(figsize=(10, 6.5))
    for i, raca in enumerate(["Preta", "Parda"]):
        valores = [
            r[(r["raca_cor"] == raca) & (r["nivel_instrucao"] == n)]["renda_habitual_real_media"].sum()
            for n in NIVEIS_INSTRUCAO_ORDEM
        ]
        deslocamento = (0.5 - i) * altura
        cor = {"Preta": COR_PRETA, "Parda": COR_PARDA}[raca]
        ax.barh(y + deslocamento, valores, altura, color=cor, zorder=3, label=raca)
        for yi, v in zip(y + deslocamento, valores):
            if v > 0:
                ax.text(v + max(valores) * 0.015, yi, f"R$ {v:,.0f}".replace(",", "."),
                        va="center", fontsize=8, color=TINTA_SECUNDARIA)

    ax.set_yticks(y)
    ax.set_yticklabels([NIVEIS_INSTRUCAO_ROTULO_CURTO[n] for n in NIVEIS_INSTRUCAO_ORDEM], fontsize=10)
    ax.invert_yaxis()
    ax.legend(loc="upper right", frameon=False, fontsize=9.5)
    _titulo(
        ax, "Renda habitual real, Preta vs. Parda, por nível de instrução — Brasil",
        f"R$ reais, a preços do trimestre mais recente · {ultimo_trimestre}º trimestre de {ultimo_ano} "
        "· PNAD Contínua Trimestral",
    )
    ax.xaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.grid(axis="x", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "renda_preta_parda_escolaridade.png")


def graficos_preta_parda_escolaridade_individual(rpe: pd.DataFrame) -> list[Path]:
    destinos = []
    for nivel in NIVEIS_INSTRUCAO_ORDEM:
        serie = _serie_por_raca(rpe, ["Preta", "Parda"], filtro_extra={"nivel_instrucao": nivel})
        rotulo_curto = NIVEIS_INSTRUCAO_ROTULO_CURTO[nivel]
        slug = _slug(rotulo_curto)
        destinos.append(_grafico_serie_temporal(
            serie, {"Preta": COR_PRETA, "Parda": COR_PARDA},
            f"Renda habitual, Preta vs. Parda — {rotulo_curto} — Brasil (2012–2026)",
            "R$ reais, a preços do trimestre mais recente (deflator oficial IBGE) · PNAD Contínua Trimestral",
            f"renda_preta_parda_escolaridade_{slug}.png",
        ))
    return destinos


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

    ordem_raca = ["Branca", "Negra", "Indígena"]
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

    ordem_raca = ["Branca", "Negra", "Indígena"]
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
    negra["raca_cor"] = "Negra"
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
        for i, raca in enumerate(["Branca", "Negra"]):
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
        labelcolor=[CORES_RACA["Branca"], CORES_RACA["Negra"]],
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

    ordem_raca = ["Branca", "Negra", "Indígena"]
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


FAIXAS_ETARIAS_ORDEM = ["14-17", "18-24", "25-39", "40-59", "60+"]


def grafico_renda_por_raca_sexo(renda: pd.DataFrame, sexo: str) -> Path:
    """Renda por raça ao longo do tempo, um único gênero (recorte raça x gênero,
    'um pra cada gênero')."""
    serie = _serie_por_raca(
        renda, ["Branca", "Negra", "Indígena"], sexo=sexo, suavizar={"Indígena"},
    )
    rotulo_sexo = {"Homem": "Homens", "Mulher": "Mulheres"}[sexo]
    sufixo = {"Homem": "homens", "Mulher": "mulheres"}[sexo]
    return _grafico_serie_temporal(
        serie, CORES_RACA,
        f"Renda habitual do trabalho por raça — {rotulo_sexo} — Brasil (2012–2026)",
        "R$ reais, a preços do trimestre mais recente (deflator oficial IBGE) · PNAD Contínua Trimestral",
        f"renda_por_raca_{sufixo}.png",
    )


def grafico_renda_por_raca_faixa_etaria_combinada(renda: pd.DataFrame) -> Path:
    """Renda por faixa etária x raça, SEM separar por gênero — um único painel
    ('raça x faixa etária, um que mostre tudo')."""
    ultimo_ano, ultimo_trimestre = _trimestre_mais_recente(renda)
    r = renda[
        (renda["nivel_geografico"] == "brasil") & (renda["ano"] == ultimo_ano) & (renda["trimestre"] == ultimo_trimestre)
    ].copy()
    combinado = _combinar_negra(r, "renda_habitual_real_media", by=["faixa_etaria"])

    ordem_raca = ["Branca", "Negra", "Indígena"]
    x = np.arange(len(FAIXAS_ETARIAS_ORDEM))
    largura = 0.26

    fig, ax = _novo_eixo(figsize=(10, 5.5))
    for i, raca in enumerate(ordem_raca):
        valores = [
            combinado[(combinado["raca_cor"] == raca) & (combinado["faixa_etaria"] == f)]["renda_habitual_real_media"].sum()
            for f in FAIXAS_ETARIAS_ORDEM
        ]
        deslocamento = (i - 1) * largura
        ax.bar(x + deslocamento, valores, largura, color=CORES_RACA[raca], zorder=3, label=raca)

    ax.set_xticks(x)
    ax.set_xticklabels(FAIXAS_ETARIAS_ORDEM, fontsize=10.5)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    _titulo(
        ax, "Renda habitual real por faixa etária e raça — Brasil",
        f"R$ reais, a preços do trimestre mais recente · {ultimo_trimestre}º trimestre de {ultimo_ano} "
        "· PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "renda_por_raca_faixa_etaria.png")


def graficos_renda_por_raca_faixa_etaria_individual(renda: pd.DataFrame) -> list[Path]:
    """Um gráfico de série temporal por faixa etária ('um pra cada faixa etária')."""
    destinos = []
    for faixa in FAIXAS_ETARIAS_ORDEM:
        serie = _serie_por_raca(
            renda, ["Branca", "Negra", "Indígena"],
            filtro_extra={"faixa_etaria": faixa}, suavizar={"Indígena"},
        )
        slug = faixa.replace("+", "mais").replace("-", "_")
        destinos.append(_grafico_serie_temporal(
            serie, CORES_RACA,
            f"Renda habitual do trabalho por raça, {faixa} anos — Brasil (2012–2026)",
            "R$ reais, a preços do trimestre mais recente (deflator oficial IBGE) · PNAD Contínua Trimestral",
            f"renda_por_raca_faixa_{slug}.png",
        ))
    return destinos


def graficos_renda_por_raca_nivel_individual(rpe: pd.DataFrame) -> list[Path]:
    """Um gráfico de série temporal por nível de instrução ('um por nível de escolaridade')."""
    destinos = []
    for nivel in NIVEIS_INSTRUCAO_ORDEM:
        serie = _serie_por_raca(
            rpe, ["Branca", "Negra", "Indígena"],
            filtro_extra={"nivel_instrucao": nivel}, suavizar={"Indígena"},
        )
        rotulo_curto = NIVEIS_INSTRUCAO_ROTULO_CURTO[nivel]
        slug = _slug(rotulo_curto)
        destinos.append(_grafico_serie_temporal(
            serie, CORES_RACA,
            f"Renda habitual do trabalho por raça — {rotulo_curto} — Brasil (2012–2026)",
            "R$ reais, a preços do trimestre mais recente (deflator oficial IBGE) · PNAD Contínua Trimestral",
            f"renda_por_raca_escolaridade_{slug}.png",
        ))
    return destinos


CMAP_SEQUENCIAL = LinearSegmentedColormap.from_list("azul_sequencial", ["#cde2fb", "#2a78d6", "#0d366b"])


def _preparar_hiato(hiato: pd.DataFrame) -> pd.DataFrame:
    h = hiato.copy()
    h["data"] = pd.to_datetime(h["ano"].astype(str) + "-" + ((h["trimestre"] - 1) * 3 + 1).astype(str) + "-01")
    return h.sort_values("data")


def grafico_hiato_percentual(hiato: pd.DataFrame) -> Path:
    """Hiato de renda Branca vs. Negra em %, série histórica, com banda de intervalo
    de confiança de 95% (teste de Welch — ver `pnadc_core.tabela_hiatos_significancia`,
    calculado a partir dos microdados de cada trimestre, não das médias já agregadas)."""
    h = _preparar_hiato(hiato)
    h["ic_inferior_pct"] = 100 * h["ic_inferior"] / h["renda_media_negra"]
    h["ic_superior_pct"] = 100 * h["ic_superior"] / h["renda_media_negra"]

    fig, ax = _novo_eixo(figsize=(11, 5.5))
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=GRADE, alpha=0.6, zorder=0)
    ax.fill_between(h["data"], h["ic_inferior_pct"], h["ic_superior_pct"], color=COR_BRANCA, alpha=0.15, zorder=2)
    ax.plot(h["data"], h["hiato_percentual"], color=COR_BRANCA, linewidth=2.2, solid_capstyle="round", zorder=3)
    ax.axhline(0, color=EIXO, linewidth=1)

    ax.annotate(
        f"{h['hiato_percentual'].iloc[-1]:.0f}%", xy=(h["data"].iloc[-1], h["hiato_percentual"].iloc[-1]),
        xytext=(8, 0), textcoords="offset points", color=COR_BRANCA, fontsize=11, fontweight="bold", va="center",
    )

    _titulo(
        ax, "Hiato de renda Branca vs. Negra, em % — Brasil (2012–2026)",
        "Quanto a mais Branca ganha que Negra · faixa = IC 95% (teste de Welch) · PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    ax.set_xlim(h["data"].min(), h["data"].max() + pd.Timedelta(days=280))
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "hiato_racial_percentual.png")


def grafico_hiato_absoluto(hiato: pd.DataFrame) -> Path:
    """Hiato de renda Branca vs. Negra em R$, série histórica, com banda de IC 95%."""
    h = _preparar_hiato(hiato)

    fig, ax = _novo_eixo(figsize=(11, 5.5))
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=GRADE, alpha=0.6, zorder=0)
    ax.fill_between(h["data"], h["ic_inferior"], h["ic_superior"], color=COR_BRANCA, alpha=0.15, zorder=2)
    ax.plot(h["data"], h["hiato_absoluto"], color=COR_BRANCA, linewidth=2.2, solid_capstyle="round", zorder=3)

    ax.annotate(
        f"R$ {h['hiato_absoluto'].iloc[-1]:,.0f}".replace(",", "."),
        xy=(h["data"].iloc[-1], h["hiato_absoluto"].iloc[-1]),
        xytext=(8, 0), textcoords="offset points", color=COR_BRANCA, fontsize=11, fontweight="bold", va="center",
    )

    _titulo(
        ax, "Hiato de renda Branca vs. Negra, em R$ — Brasil (2012–2026)",
        "R$ reais, preço do trimestre mais recente · faixa = IC 95% (Welch) · PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    ax.set_xlim(h["data"].min(), h["data"].max() + pd.Timedelta(days=280))
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "hiato_racial_absoluto.png")


ROTULOS_DECOMPOSICAO = {
    "nenhum (hiato bruto)": "Hiato bruto\n(sem controle)",
    "faixa_etaria": "+ faixa\netária",
    "faixa_etaria + nivel_instrucao": "+ escolaridade",
    "faixa_etaria + nivel_instrucao + grupamento_ocupacional": "+ ocupação\n(residual)",
}


def grafico_decomposicao_hiato(decomp: pd.DataFrame) -> Path:
    """Quanto do hiato Branca vs. Negra sobra depois de controlar por idade, depois +
    escolaridade, depois + ocupação — padronização direta (ver
    agregacoes_pnadc.gerar_decomposicao_hiato_ocupacional)."""
    d = decomp.copy()
    d["rotulo"] = d["controles"].map(ROTULOS_DECOMPOSICAO)

    fig, ax = _novo_eixo(figsize=(10, 5.5))
    x = np.arange(len(d))
    cores = [COR_BRANCA] * (len(d) - 1) + [COR_NEGRA]
    barras = ax.bar(x, d["hiato_percentual"], color=cores, width=0.55, zorder=3)
    for barra, v in zip(barras, d["hiato_percentual"]):
        ax.text(barra.get_x() + barra.get_width() / 2, v + 1.5, f"{v:.0f}%",
                ha="center", fontsize=12, fontweight="bold", color=TINTA_PRIMARIA)

    for i in range(len(d) - 1):
        ax.annotate(
            "", xy=(x[i + 1] - 0.3, d["hiato_percentual"].iloc[i + 1] + 3),
            xytext=(x[i] + 0.3, d["hiato_percentual"].iloc[i] + 3),
            arrowprops=dict(arrowstyle="->", color=TINTA_MUTED, lw=1.2),
        )

    ax.set_xticks(x)
    ax.set_xticklabels(d["rotulo"], fontsize=10.5)
    ax.set_ylim(0, d["hiato_percentual"].max() * 1.25)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")

    _titulo(
        ax, "Quanto do hiato Branca vs. Negra idade/escolaridade/ocupação explicam?",
        "Últimos 8 trimestres agrupados, pessoas ocupadas · padronização direta · PNAD Contínua Trimestral",
    )
    ax.text(
        0.5, -0.20,
        "Mesma idade, escolaridade e ocupação — ainda assim resta um hiato de "
        f"{d['hiato_percentual'].iloc[-1]:.0f}% não explicado por essas três variáveis.",
        transform=ax.transAxes, ha="center", fontsize=10.5, color=TINTA_SECUNDARIA, style="italic",
    )
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    return _salvar(fig, "decomposicao_hiato_ocupacional.png")


def grafico_renda_completa_heatmap(rc: pd.DataFrame) -> Path:
    """Raça x gênero x faixa etária x nível de instrução — tudo de uma vez, como
    grade de heatmaps (um painel por raça x gênero; dentro de cada painel, células
    de faixa etária x nível de instrução, cor = renda real)."""
    ultimo_ano, ultimo_trimestre = _trimestre_mais_recente(rc)
    r = rc[(rc["ano"] == ultimo_ano) & (rc["trimestre"] == ultimo_trimestre)].copy()

    negra = (
        r[r["raca_cor"].isin(["Preta", "Parda"])]
        .groupby(["sexo", "faixa_etaria", "nivel_instrucao"])
        .apply(lambda g: (g["renda_habitual_real_media"] * g["populacao_estimada"]).sum() / g["populacao_estimada"].sum())
        .rename("renda_habitual_real_media")
        .reset_index()
    )
    negra["raca_cor"] = "Negra"
    outras = r[r["raca_cor"].isin(["Branca", "Indígena"])]
    completo = pd.concat([outras, negra], ignore_index=True)

    ordem_raca = ["Branca", "Negra", "Indígena"]
    generos = ["Homem", "Mulher"]
    vmin, vmax = completo["renda_habitual_real_media"].min(), completo["renda_habitual_real_media"].max()

    fig, axes = plt.subplots(len(ordem_raca), len(generos), figsize=(11, 13), dpi=150)
    fig.patch.set_facecolor(SUPERFICIE)

    for i, raca in enumerate(ordem_raca):
        for j, sexo in enumerate(generos):
            ax = axes[i, j]
            ax.set_facecolor(SUPERFICIE)
            sub = completo[(completo["raca_cor"] == raca) & (completo["sexo"] == sexo)]
            matriz = sub.pivot_table(index="nivel_instrucao", columns="faixa_etaria", values="renda_habitual_real_media")
            matriz = matriz.reindex(index=NIVEIS_INSTRUCAO_ORDEM, columns=FAIXAS_ETARIAS_ORDEM)
            ax.imshow(matriz.values, cmap=CMAP_SEQUENCIAL, vmin=vmin, vmax=vmax, aspect="auto")

            ax.set_xticks(range(len(FAIXAS_ETARIAS_ORDEM)))
            ax.set_xticklabels(FAIXAS_ETARIAS_ORDEM, fontsize=7.5, color=TINTA_MUTED)
            if j == 0:
                ax.set_yticks(range(len(NIVEIS_INSTRUCAO_ORDEM)))
                ax.set_yticklabels(
                    [NIVEIS_INSTRUCAO_ROTULO_CURTO[n] for n in NIVEIS_INSTRUCAO_ORDEM], fontsize=7.5, color=TINTA_MUTED
                )
            else:
                ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.tick_params(length=0)
            rotulo_sexo = "Homens" if sexo == "Homem" else "Mulheres"
            ax.set_title(f"{raca.split(' ')[0]} · {rotulo_sexo}", fontsize=10, color=TINTA_SECUNDARIA)

            for yi in range(matriz.shape[0]):
                for xi in range(matriz.shape[1]):
                    v = matriz.values[yi, xi]
                    if pd.notna(v):
                        cor_txt = SUPERFICIE if v > (vmin + vmax) / 2 else TINTA_PRIMARIA
                        ax.text(xi, yi, f"{v / 1000:.1f}k", ha="center", va="center", fontsize=6.5, color=cor_txt)

    fig.suptitle(
        "Renda habitual real por raça, gênero, faixa etária e nível de instrução — Brasil",
        fontsize=13.5, fontweight="bold", color=TINTA_PRIMARIA, x=0.02, ha="left", y=0.99,
    )
    fig.text(
        0.02, 0.965,
        f"R$ reais (milhares), a preços do trimestre mais recente · {ultimo_trimestre}º trimestre de {ultimo_ano} "
        "· células em branco = sem amostra suficiente · PNAD Contínua Trimestral",
        fontsize=9, color=TINTA_SECUNDARIA,
    )
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.02, 1, 0.955))
    return _salvar(fig, "renda_completa_heatmap.png")


def main() -> None:
    renda = pd.read_parquet(REPO_ROOT / "data" / "processed" / "renda.parquet")
    esc = pd.read_parquet(REPO_ROOT / "data" / "processed" / "escolaridade.parquet")
    rpe = pd.read_parquet(REPO_ROOT / "data" / "processed" / "renda_por_escolaridade.parquet")
    rc = pd.read_parquet(REPO_ROOT / "data" / "processed" / "renda_completa.parquet")
    hiato = pd.read_parquet(REPO_ROOT / "data" / "processed" / "hiato_racial.parquet")
    decomp = pd.read_parquet(REPO_ROOT / "data" / "processed" / "decomposicao_hiato_ocupacional.parquet")

    destinos = [
        # raça
        grafico_renda_por_raca(renda),
        grafico_renda_preta_parda(renda),
        # hiato Branca vs. Negra, série histórica, com significância
        grafico_hiato_percentual(hiato),
        grafico_hiato_absoluto(hiato),
        grafico_decomposicao_hiato(decomp),
        # raça x gênero: combinado + um por gênero
        grafico_renda_por_raca_genero(renda),
        grafico_renda_por_raca_sexo(renda, "Homem"),
        grafico_renda_por_raca_sexo(renda, "Mulher"),
        # preta x parda x gênero: combinado + um por gênero
        grafico_preta_parda_genero_combinado(renda),
        grafico_preta_parda_sexo(renda, "Homem"),
        grafico_preta_parda_sexo(renda, "Mulher"),
        # raça x faixa etária: combinado + um por faixa
        grafico_renda_por_raca_faixa_etaria_combinada(renda),
        *graficos_renda_por_raca_faixa_etaria_individual(renda),
        # preta x parda x faixa etária: combinado + uma por faixa
        grafico_preta_parda_faixa_etaria_combinada(renda),
        *graficos_preta_parda_faixa_etaria_individual(renda),
        # raça x escolaridade: combinado + um por nível
        grafico_renda_por_raca_escolaridade(rpe, sexo=None),
        *graficos_renda_por_raca_nivel_individual(rpe),
        # preta x parda x escolaridade: combinado + um por nível
        grafico_preta_parda_escolaridade_combinada(rpe),
        *graficos_preta_parda_escolaridade_individual(rpe),
        # raça x gênero x escolaridade
        grafico_renda_por_raca_escolaridade(rpe, sexo="Homem"),
        grafico_renda_por_raca_escolaridade(rpe, sexo="Mulher"),
        # raça x gênero x faixa etária
        grafico_renda_por_faixa_etaria(renda),
        # escolaridade x raça x gênero (nível de instrução, não renda)
        grafico_escolaridade_por_raca_genero(esc),
        # raça x gênero x faixa etária x escolaridade
        grafico_renda_completa_heatmap(rc),
    ]
    for destino in destinos:
        print(f"Gráfico salvo em: {destino.relative_to(REPO_ROOT)}")
    print(f"\nTotal: {len(destinos)} gráficos.")


if __name__ == "__main__":
    main()
