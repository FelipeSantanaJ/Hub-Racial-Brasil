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

# Identidade visual em tons terrosos (2026-09-04) — paleta re-validada do zero com
# `validate_palette.js` (ALL CHECKS PASS, all-pairs, modo claro): banda de luminosidade,
# piso de croma, separação CVD (deutan/protan/tritan) e piso de visão normal. Escolhida
# de propósito espalhada pelo círculo cromático (verde-azulado, vermelho-terracota,
# ocre-amarelo, ameixa-roxo) para NÃO formar um gradiente claro→escuro que lembre tom de
# pele — é uma paleta categórica arbitrária, igual à anterior (azul/laranja/aqua/violeta),
# só que reformulada em tons terrosos.
COR_BRANCA = "#0d9086"    # verde-azulado profundo (pinho/petróleo)
COR_NEGRA = "#c8541f"     # terracota — usada também para "Preta" nos gráficos detalhados
COR_INDIGENA = "#853359"  # ameixa/vinho
CORES_RACA = {"Branca": COR_BRANCA, "Negra": COR_NEGRA, "Indígena": COR_INDIGENA}

# Cor do gráfico Preta vs. Parda (validada junto com Branca/Negra/Indígena acima,
# all-pairs PASS, ainda que este gráfico não mostre as quatro ao mesmo tempo).
COR_PRETA = COR_NEGRA
COR_PARDA = "#d19a12"     # ocre/mostarda

SUPERFICIE = "#f7f2ea"
TINTA_PRIMARIA = "#2b2018"
TINTA_SECUNDARIA = "#5c4f3f"
TINTA_MUTED = "#8f8271"
GRADE = "#e6ddd0"
EIXO = "#c9bda8"


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
    rotulos: dict[str, str] | None = None, formato_eixo_y=None, teto_pct: bool = False,
) -> Path:
    """Plota uma série temporal (colunas = raças, ou qualquer outra categoria — ex.:
    região) no estilo padrão do projeto — linhas, rótulos diretos sem colisão, faixa da
    pandemia, grade horizontal. `formato_eixo_y` (opcional) troca o formato padrão em
    R$ por outro (ex.: `lambda v, _: f"{v:.0f}%"` pra séries em percentual). `teto_pct`
    limita o topo do eixo a 100% — usar em séries percentuais cujo máximo já está perto
    de 100 (sem isso, o `* 1.22` padrão criaria uma grade acima de 100%, sem sentido
    pra uma métrica limitada a esse teto)."""
    rotulos = rotulos or {c: c for c in serie.columns}
    formato_eixo_y = formato_eixo_y or (lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    fig, ax = _novo_eixo(figsize=(11, 5.5))
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=GRADE, alpha=0.6, zorder=0)

    topo = serie.max().max() * 1.22
    if teto_pct:
        topo = min(topo, 100)
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
    ax.yaxis.set_major_formatter(formato_eixo_y)
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


def grafico_escolaridade_por_raca_genero(esc: pd.DataFrame, nivel: str = "Superior completo") -> Path:
    """% que atingiu um nível de instrução (`nivel`, default Superior completo), por
    raça x gênero, Brasil, trimestre mais recente. `nivel=None` cobria só Superior
    completo antes — chamado agora pros 7 níveis (ver `main()`), mesmo padrão
    "combinado + um por categoria" já usado em raça×escolaridade (renda)."""
    ultimo_ano, ultimo_trimestre = _trimestre_mais_recente(esc)
    e = esc[
        (esc["nivel_geografico"] == "brasil")
        & (esc["ano"] == ultimo_ano)
        & (esc["trimestre"] == ultimo_trimestre)
    ].copy()

    combinado = _combinar_negra_multi(e, "populacao_estimada", by=["sexo", "nivel_instrucao"])
    total = combinado.groupby(["raca_cor", "sexo"])["populacao_estimada"].sum().rename("total")
    no_nivel = (
        combinado[combinado["nivel_instrucao"] == nivel]
        .groupby(["raca_cor", "sexo"])["populacao_estimada"].sum().rename("no_nivel")
    )
    pct = (no_nivel / total * 100).rename("pct_nivel").reset_index()

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
        valores = [pct[(pct["raca_cor"] == r) & (pct["sexo"] == sexo)]["pct_nivel"].sum() for r in ordem_raca]
        cores = [CORES_RACA[r] for r in ordem_raca]
        deslocamento = (i - 0.5) * largura
        barras = ax.bar(
            x + deslocamento, valores, largura, color=cores, alpha=alpha_por_sexo[sexo],
            edgecolor=SUPERFICIE, linewidth=1.5, zorder=3,
        )
        for barra, v in zip(barras, valores):
            ax.text(
                barra.get_x() + barra.get_width() / 2, v + max(valores) * 0.02, f"{v:.0f}%",
                ha="center", fontsize=9, color=TINTA_SECUNDARIA,
            )

    legenda = [
        Patch(facecolor=TINTA_MUTED, alpha=alpha_por_sexo["Homem"], label="Homens"),
        Patch(facecolor=TINTA_MUTED, alpha=alpha_por_sexo["Mulher"], label="Mulheres"),
    ]
    ax.legend(handles=legenda, loc="upper right", frameon=False, fontsize=9.5)

    ax.set_xticks(x)
    ax.set_xticklabels([r.split(" ")[0] for r in ordem_raca], fontsize=10.5, color=TINTA_PRIMARIA)
    ax.set_ylim(0, pct["pct_nivel"].max() * 1.35)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")

    rotulo_nivel = NIVEIS_INSTRUCAO_ROTULO_CURTO[nivel]
    _titulo(
        ax,
        f"{rotulo_nivel}, por raça e gênero — Brasil",
        f"% da população 14+ anos · {ultimo_trimestre}º trimestre de {ultimo_ano} · PNAD Contínua Trimestral",
    )
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)

    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    sufixo = "" if nivel == "Superior completo" else f"_{_slug(rotulo_nivel)}"
    return _salvar(fig, f"escolaridade_por_raca_genero{sufixo}.png")


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

GRUPAMENTOS_OCUPACIONAIS_ORDEM = [
    "Diretores e gerentes",
    "Profissionais das ciências e intelectuais",
    "Técnicos e profissionais de nível médio",
    "Trabalhadores de apoio administrativo",
    "Trabalhadores dos serviços, vendedores do comércio",
    "Trabalhadores agropecuários, florestais, da caça e pesca",
    "Trabalhadores da construção, artes mecânicas e ofícios",
    "Operadores de instalações e máquinas e montadores",
    "Ocupações elementares",
    "Forças armadas, policiais e bombeiros militares",
    "Ocupações maldefinidas",
]
ROTULOS_OCUPACAO_CURTO = {
    "Diretores e gerentes": "Diretores/gerentes",
    "Profissionais das ciências e intelectuais": "Profissionais",
    "Técnicos e profissionais de nível médio": "Técnicos",
    "Trabalhadores de apoio administrativo": "Apoio administrativo",
    "Trabalhadores dos serviços, vendedores do comércio": "Serviços/comércio",
    "Trabalhadores agropecuários, florestais, da caça e pesca": "Agropecuária",
    "Trabalhadores da construção, artes mecânicas e ofícios": "Construção/ofícios",
    "Operadores de instalações e máquinas e montadores": "Operadores de máquinas",
    "Ocupações elementares": "Ocupações elementares",
    "Forças armadas, policiais e bombeiros militares": "Forças armadas/policiais",
    "Ocupações maldefinidas": "Maldefinidas",
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

# Gerações com amostra ao longo de toda a janela 2012-2026 (Geração Silenciosa e Alpha
# ficam de fora dos gráficos — amostra residual/inexistente, ver agregacoes_pnadc.py).
GERACOES_ORDEM_GRAFICO = [
    "Baby Boomer (1946-1964)", "Geração X (1965-1980)",
    "Millennial (1981-1996)", "Geração Z (1997-2012)",
]
ROTULOS_GERACAO_CURTO = {
    "Baby Boomer (1946-1964)": "Baby Boomer", "Geração X (1965-1980)": "Geração X",
    "Millennial (1981-1996)": "Millennial", "Geração Z (1997-2012)": "Geração Z",
}
# Reaproveita os tons da identidade visual (mesma paleta validada de CORES_REGIAO) —
# dimensão diferente de raça e de região, mas nunca aparece no mesmo gráfico que elas.
CORES_GERACAO = {
    "Baby Boomer (1946-1964)": "#3a5a9a", "Geração X (1965-1980)": "#c8541f",
    "Millennial (1981-1996)": "#0d9086", "Geração Z (1997-2012)": "#853359",
}


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


CMAP_SEQUENCIAL = LinearSegmentedColormap.from_list(
    "terroso_sequencial", ["#f6e8cf", "#d19a12", "#8a3d17", "#2b1509"]
)


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
    "grupamento_ocupacional": "Só ocupação\n(isolado)",
}


def grafico_decomposicao_hiato(decomp: pd.DataFrame) -> Path:
    """Quanto do hiato Branca vs. Negra sobra depois de controlar por idade, depois +
    escolaridade, depois + ocupação — padronização direta (ver
    agregacoes_pnadc.gerar_decomposicao_hiato_ocupacional). A 5ª barra ("só ocupação")
    é uma comparação ISOLADA — ocupação sozinha, sem idade/escolaridade já controladas
    — por isso vem separada visualmente (espaço + cor diferente + linha pontilhada),
    não é mais um passo acumulado da cadeia."""
    ordem_cadeia = [
        "nenhum (hiato bruto)", "faixa_etaria", "faixa_etaria + nivel_instrucao",
        "faixa_etaria + nivel_instrucao + grupamento_ocupacional",
    ]
    cadeia = decomp[decomp["controles"].isin(ordem_cadeia)].set_index("controles").loc[ordem_cadeia].reset_index()
    isolado = decomp[decomp["controles"] == "grupamento_ocupacional"].iloc[0]

    cadeia["rotulo"] = cadeia["controles"].map(ROTULOS_DECOMPOSICAO)
    x_cadeia = np.arange(len(cadeia))
    x_isolado = len(cadeia) + 0.6

    fig, ax = _novo_eixo(figsize=(11.5, 5.5))
    cores_cadeia = [COR_BRANCA] * (len(cadeia) - 1) + [COR_NEGRA]
    barras = ax.bar(x_cadeia, cadeia["hiato_percentual"], color=cores_cadeia, width=0.55, zorder=3)
    for barra, v in zip(barras, cadeia["hiato_percentual"]):
        ax.text(barra.get_x() + barra.get_width() / 2, v + 1.5, f"{v:.0f}%",
                ha="center", fontsize=12, fontweight="bold", color=TINTA_PRIMARIA)

    for i in range(len(cadeia) - 1):
        ax.annotate(
            "", xy=(x_cadeia[i + 1] - 0.3, cadeia["hiato_percentual"].iloc[i + 1] + 3),
            xytext=(x_cadeia[i] + 0.3, cadeia["hiato_percentual"].iloc[i] + 3),
            arrowprops=dict(arrowstyle="->", color=TINTA_MUTED, lw=1.2),
        )

    ax.axvline(x_isolado - 0.6, color=EIXO, linewidth=1, linestyle=":", zorder=1)
    ax.bar([x_isolado], [isolado["hiato_percentual"]], color=COR_PARDA, width=0.55, zorder=3)
    ax.text(x_isolado, isolado["hiato_percentual"] + 1.5, f"{isolado['hiato_percentual']:.0f}%",
            ha="center", fontsize=12, fontweight="bold", color=TINTA_PRIMARIA)

    ax.set_xticks(list(x_cadeia) + [x_isolado])
    ax.set_xticklabels(list(cadeia["rotulo"]) + [ROTULOS_DECOMPOSICAO["grupamento_ocupacional"]], fontsize=10)
    ax.set_ylim(0, max(cadeia["hiato_percentual"].max(), isolado["hiato_percentual"]) * 1.25)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")

    _titulo(
        ax, "Quanto do hiato Branca vs. Negra idade/escolaridade/ocupação explicam?",
        "Últimos 8 trimestres agrupados, pessoas ocupadas · padronização direta · PNAD Contínua Trimestral",
    )
    hiato_bruto = cadeia.loc[cadeia["controles"] == "nenhum (hiato bruto)", "hiato_percentual"].iloc[0]
    hiato_residual = cadeia["hiato_percentual"].iloc[-1]
    ax.text(
        0.5, -0.20,
        f"Ocupação sozinha: hiato cai de {hiato_bruto:.0f}% pra {isolado['hiato_percentual']:.0f}%. "
        f"Idade+escolaridade+ocupação juntas: cai pra {hiato_residual:.0f}%.",
        transform=ax.transAxes, ha="center", fontsize=10, color=TINTA_SECUNDARIA, style="italic",
    )
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
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


ROTULOS_OB_CONTROLES = {
    "faixa_etaria": "+ faixa\netária",
    "faixa_etaria + nivel_instrucao": "+ escolaridade",
    "faixa_etaria + nivel_instrucao + grupamento_ocupacional": "+ ocupação",
    "grupamento_ocupacional": "Só ocupação\n(isolado)",
}


def grafico_oaxaca_blinder_decomposicao(ob: pd.DataFrame) -> Path:
    """Decomposição de Oaxaca-Blinder do hiato Branca-Negra (log-renda) em parcela
    explicada (composição — idade/escolaridade/ocupação) vs. não-explicada (mesmas
    características, retorno diferente) — ver `pnadc_core.decomposicao_oaxaca_blinder`.
    Complementa `decomposicao_hiato_ocupacional.png` (padronização direta, mais fácil
    de ler em R$) com o teste de significância formal da parte residual."""
    d = ob[ob["ponto"] == "média"].copy()
    ordem_cadeia = [
        "faixa_etaria", "faixa_etaria + nivel_instrucao",
        "faixa_etaria + nivel_instrucao + grupamento_ocupacional",
    ]
    cadeia = d[d["controles"].isin(ordem_cadeia)].set_index("controles").loc[ordem_cadeia].reset_index()
    isolado = d[d["controles"] == "grupamento_ocupacional"].iloc[0]
    cadeia["rotulo"] = cadeia["controles"].map(ROTULOS_OB_CONTROLES)

    x_cadeia = np.arange(len(cadeia))
    x_isolado = len(cadeia) + 0.6

    fig, ax = _novo_eixo(figsize=(11, 6.8))

    def _desenhar_barra(x, exp_, nexp, label_exp=None, label_nexp=None):
        ax.bar([x], [exp_], width=0.5, color=COR_BRANCA, alpha=0.55, zorder=3, label=label_exp)
        ax.bar([x], [nexp], width=0.5, bottom=[exp_], color=COR_NEGRA, zorder=3, label=label_nexp)
        # fatia fina (< 8pp, caso da barra "+ faixa etária") recebe rótulo ACIMA da
        # própria fatia, não centralizado dentro dela — texto não cabe numa fatia de
        # poucos pixels de altura (bug visto no primeiro render: rótulo vazava pro
        # eixo x e colidia com o tick label).
        if exp_ < 8:
            ax.text(x, exp_ + 2, f"{exp_:.0f}%", ha="center", va="bottom", fontsize=9,
                    color=TINTA_PRIMARIA, fontweight="bold")
        else:
            ax.text(x, exp_ / 2, f"{exp_:.0f}%", ha="center", va="center", fontsize=10,
                    color=SUPERFICIE, fontweight="bold")
        ax.text(x, exp_ + nexp / 2, f"{nexp:.0f}%", ha="center", va="center", fontsize=10,
                color=SUPERFICIE, fontweight="bold")

    for i, row in cadeia.iterrows():
        _desenhar_barra(
            x_cadeia[i], row["pct_explicada"], row["pct_nao_explicada"],
            label_exp="Explicada (composição)" if i == 0 else None,
            label_nexp="Não-explicada (retorno)" if i == 0 else None,
        )
    # barra isolada ("só ocupação", sem idade/escolaridade já controladas) — separada
    # visualmente (espaço + linha pontilhada), não é mais um passo acumulado da cadeia.
    ax.axvline(x_isolado - 0.6, color=EIXO, linewidth=1, linestyle=":", zorder=1)
    _desenhar_barra(x_isolado, isolado["pct_explicada"], isolado["pct_nao_explicada"])

    ax.set_xticks(list(x_cadeia) + [x_isolado])
    ax.set_xticklabels(list(cadeia["rotulo"]) + [ROTULOS_OB_CONTROLES["grupamento_ocupacional"]], fontsize=10)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, frameon=False, fontsize=9.5)

    p_valor_final = cadeia["residuo_restrito_p_valor"].iloc[-1]
    coef_final = cadeia["residuo_restrito_coef"].iloc[-1]
    hiato_residual_pct = (np.exp(coef_final) - 1) * 100
    p_txt = "p < 0,001" if p_valor_final < 0.001 else f"p = {p_valor_final:.3f}"
    _titulo(
        ax, "Decomposição de Oaxaca-Blinder do hiato Branca vs. Negra",
        "% do hiato de log-renda por composição vs. por retorno às mesmas características · "
        f"resíduo final de +{hiato_residual_pct:.0f}% ({p_txt})",
    )
    p_isolado_txt = "p < 0,001" if isolado["residuo_restrito_p_valor"] < 0.001 else f"p = {isolado['residuo_restrito_p_valor']:.3f}"
    ax.text(
        0.5, -0.34,
        f"Ocupação sozinha explica {isolado['pct_explicada']:.0f}% do hiato ({p_isolado_txt}) — "
        "menos que idade+escolaridade+ocupação juntas.",
        transform=ax.transAxes, ha="center", fontsize=9.5, color=TINTA_SECUNDARIA, style="italic",
    )
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.28, 1, 1))
    return _salvar(fig, "oaxaca_blinder_decomposicao.png")


def grafico_oaxaca_blinder_quantis(ob: pd.DataFrame) -> Path:
    """Decomposição de Oaxaca-Blinder via RIF (Firpo-Fortin-Lemieux 2009) em três
    pontos da distribuição de renda — base (P10), mediana (P50) e topo (P90) — com os
    mesmos controles (idade+escolaridade+ocupação). Responde: o hiato residual entre
    Branca e Negra é maior no topo ou na base da distribuição de renda?"""
    d = ob[ob["ponto"].isin(["p10", "p50", "p90"])].copy()
    ordem = {"p10": 0, "p50": 1, "p90": 2}
    d = d.assign(ordem=d["ponto"].map(ordem)).sort_values("ordem")
    d["hiato_residual_pct"] = (np.exp(d["residuo_restrito_coef"]) - 1) * 100
    rotulos_ponto = {"p10": "P10\n(base)", "p50": "P50\n(mediana)", "p90": "P90\n(topo)"}

    fig, ax = _novo_eixo(figsize=(8.5, 5.5))
    x = np.arange(len(d))
    barras = ax.bar(x, d["hiato_residual_pct"], width=0.5, color=COR_NEGRA, zorder=3)
    for barra, v, p in zip(barras, d["hiato_residual_pct"], d["residuo_restrito_p_valor"]):
        marca = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "n.s."))
        ax.text(barra.get_x() + barra.get_width() / 2, v + d["hiato_residual_pct"].max() * 0.02,
                f"{v:.0f}%\n{marca}", ha="center", fontsize=10.5, fontweight="bold", color=TINTA_PRIMARIA)

    ax.set_xticks(x)
    ax.set_xticklabels([rotulos_ponto[p] for p in d["ponto"]], fontsize=10.5)
    ax.set_ylim(0, d["hiato_residual_pct"].max() * 1.3)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    _titulo(
        ax, "Hiato residual Branca vs. Negra, por ponto da distribuição de renda",
        "Regressão RIF com idade+escolaridade+ocupação controladas · *** p<0,001 · "
        "últimos 8 trimestres, ocupados",
    )
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "oaxaca_blinder_quantis.png")


REGIOES_ORDEM = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
# Paleta terrosa de 5 cores, validada all-pairs PASS (reaproveita os 3 tons de raça +
# ocre da Parda, já validados juntos, mais um 5º — índigo terroso — validado contra os
# outros 4). Dimensão diferente de raça (região) nunca aparece no mesmo gráfico, mas os
# tons se sobrepõem por serem a mesma identidade visual, não por acidente.
CORES_REGIAO = {
    "Norte": "#3a5a9a", "Nordeste": "#c8541f", "Sudeste": "#0d9086",
    "Sul": "#853359", "Centro-Oeste": "#d19a12",
}


def grafico_hiato_regional(hr: pd.DataFrame) -> Path:
    """Hiato de renda Branca vs. Negra, em %, por Região — mesmo teste de Welch de
    `grafico_hiato_percentual`, quebrado por região pra ver se a desigualdade regional
    do Brasil (Norte/Nordeste vs. Sul/Sudeste) também aparece especificamente no hiato
    racial, ou se é uniforme pelo país."""
    h = hr.copy()
    h["data"] = pd.to_datetime(h["ano"].astype(str) + "-" + ((h["trimestre"] - 1) * 3 + 1).astype(str) + "-01")
    pivot = h.pivot_table(index="data", columns="regiao", values="hiato_percentual").sort_index()
    pivot = pivot[REGIOES_ORDEM]
    return _grafico_serie_temporal(
        pivot, CORES_REGIAO,
        "Hiato de renda Branca vs. Negra, por Região — Brasil (2012–2026)",
        "Quanto a mais Branca ganha que Negra, em % · teste de Welch por trimestre e região · "
        "PNAD Contínua Trimestral",
        "hiato_racial_por_regiao.png",
        formato_eixo_y=lambda v, _: f"{v:.0f}%",
    )


def grafico_segregacao_ocupacional(seg: pd.DataFrame) -> Path:
    """Índice de dissimilaridade de Duncan entre a distribuição ocupacional de Branca e
    de Negra — % de um dos grupos que precisaria trocar de categoria ocupacional pra
    igualar a distribuição do outro. Mede segregação ocupacional em si, à parte do seu
    efeito na renda (já coberto pela decomposição do hiato)."""
    s = seg.copy()
    s["data"] = pd.to_datetime(s["ano"].astype(str) + "-" + ((s["trimestre"] - 1) * 3 + 1).astype(str) + "-01")
    s = s.sort_values("data")
    s["indice_pct"] = s["indice_duncan_branca_negra"] * 100

    fig, ax = _novo_eixo(figsize=(11, 5.5))
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=GRADE, alpha=0.6, zorder=0)
    ax.plot(s["data"], s["indice_pct"], color=COR_NEGRA, linewidth=2.2, solid_capstyle="round", zorder=3)
    ax.annotate(
        f"{s['indice_pct'].iloc[-1]:.0f}%", xy=(s["data"].iloc[-1], s["indice_pct"].iloc[-1]),
        xytext=(8, 0), textcoords="offset points", color=COR_NEGRA, fontsize=11, fontweight="bold", va="center",
    )
    _titulo(
        ax, "Índice de segregação ocupacional, Branca vs. Negra — Brasil (2012–2026)",
        "Índice de dissimilaridade de Duncan · % que precisaria trocar de categoria ocupacional "
        "pra igualar a distribuição do outro grupo · PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    ax.set_xlim(s["data"].min(), s["data"].max() + pd.Timedelta(days=280))
    ax.set_ylim(0, s["indice_pct"].max() * 1.25)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "segregacao_ocupacional.png")


ROTULOS_EVENTO_ESTRUTURAL = {
    "reforma_trabalhista_2017": "Reforma\ntrabalhista",
    "reforma_previdencia_2019": "Reforma da\nprevidência",
    "recessao_2015": "Recessão\n2015-16",
}


def grafico_quebra_estrutural(hiato: pd.DataFrame, quebra: pd.DataFrame) -> Path:
    """Mesma série do hiato % (`grafico_hiato_percentual`), com os 3 eventos testados
    em `agregacoes_pnadc.gerar_quebra_estrutural` marcados — teste simplificado tipo
    Chow (mudança de patamar e/ou inclinação), não busca por múltiplas quebras."""
    h = _preparar_hiato(hiato)
    topo = h["hiato_percentual"].max() * 1.28

    fig, ax = _novo_eixo(figsize=(11.5, 5.8))
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=GRADE, alpha=0.6, zorder=0)
    ax.plot(h["data"], h["hiato_percentual"], color=COR_BRANCA, linewidth=2.2, solid_capstyle="round", zorder=3)

    for _, linha in quebra.iterrows():
        data_evento = pd.Timestamp(f"{int(linha['ano_evento'])}-{(int(linha['trimestre_evento']) - 1) * 3 + 1:02d}-01")
        ax.axvline(data_evento, color=TINTA_MUTED, linewidth=1, linestyle=":", zorder=2)
        marca = "significativo" if linha["significativo_a_5pct"] else "não-significativo"
        ax.text(
            data_evento, topo * 0.98, f"{ROTULOS_EVENTO_ESTRUTURAL[linha['evento']]}\n({marca})",
            fontsize=7.5, color=TINTA_SECUNDARIA, ha="center", va="top",
        )

    ax.set_ylim(0, topo * 1.05)
    _titulo(
        ax, "Hiato racial e possíveis pontos de inflexão — Brasil (2012–2026)",
        "Teste de quebra estrutural simplificado (nível + inclinação, tipo Chow) em cada evento · "
        "PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    ax.set_xlim(h["data"].min(), h["data"].max() + pd.Timedelta(days=280))
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "hiato_quebra_estrutural.png")


ROTULOS_RACA_SUAVIZADA = {"Branca": "Branca", "Negra": "Negra", "Indígena": "Indígena (média móvel 4 trim.)"}


def grafico_informalidade(inf: pd.DataFrame) -> Path:
    """% de empregados com carteira de trabalho assinada (entre privado/doméstico/
    público — ver decodificação de VD4009 em docs/LIMITACOES_E_METODOLOGIA.md), por
    raça, Brasil. Indígena suavizado (amostra pequena)."""
    serie = _serie_por_raca(inf, ["Branca", "Negra", "Indígena"], coluna_valor="pct_com_carteira",
                             suavizar={"Indígena"})
    return _grafico_serie_temporal(
        serie, CORES_RACA,
        "% de empregados com carteira assinada, por raça — Brasil (2012–2026)",
        "Entre empregados no setor privado, doméstico ou público (VD4009) · PNAD Contínua Trimestral",
        "informalidade_carteira_assinada.png",
        rotulos=ROTULOS_RACA_SUAVIZADA,
        formato_eixo_y=lambda v, _: f"{v:.0f}%",
    )


def grafico_renda_por_hora(horas: pd.DataFrame) -> Path:
    """Renda real por hora trabalhada (aproximada: renda habitual mensal / (horas
    semanais x 4,345)), por raça — testa se o hiato de renda vem de jornada diferente
    ou de remuneração por hora efetivamente menor."""
    serie = _serie_por_raca(horas, ["Branca", "Negra", "Indígena"], coluna_valor="renda_por_hora_real_media",
                             suavizar={"Indígena"})
    return _grafico_serie_temporal(
        serie, CORES_RACA,
        "Renda real por hora trabalhada, por raça — Brasil (2012–2026)",
        "Renda habitual mensal ÷ (horas semanais x 4,345) · a preços do trimestre mais recente · "
        "PNAD Contínua Trimestral",
        "renda_por_hora.png",
        rotulos=ROTULOS_RACA_SUAVIZADA,
    )


def grafico_alfabetizacao(alf: pd.DataFrame) -> Path:
    """% alfabetizado (V3001), por raça, população 60+ anos — cohort onde o
    analfabetismo residual ainda é mensurável no Brasil (nas faixas mais jovens já está
    perto de 100% pros três grupos)."""
    serie = _serie_por_raca(alf, ["Branca", "Negra", "Indígena"], coluna_valor="pct_alfabetizado",
                             filtro_extra={"faixa_etaria": "60+"}, suavizar={"Indígena"})
    return _grafico_serie_temporal(
        serie, CORES_RACA,
        "% alfabetizado, população 60+ anos, por raça — Brasil (2012–2026)",
        "Sabe ler e escrever (V3001) · Indígena com amostra pequena nessa faixa etária, suavizado · "
        "PNAD Contínua Trimestral",
        "alfabetizacao_60mais.png",
        rotulos=ROTULOS_RACA_SUAVIZADA,
        formato_eixo_y=lambda v, _: f"{v:.0f}%",
        teto_pct=True,
    )


def grafico_desalento(des: pd.DataFrame) -> Path:
    """% da população fora da força de trabalho que está desalentada (desistiu de
    procurar emprego, VD4005), por raça — vai além da taxa de desocupação simples
    (ocupacao.parquet)."""
    serie = _serie_por_raca(des, ["Branca", "Negra", "Indígena"], coluna_valor="pct_desalento",
                             suavizar={"Indígena"})
    return _grafico_serie_temporal(
        serie, CORES_RACA,
        "% de desalento entre quem está fora da força de trabalho, por raça — Brasil (2012–2026)",
        "Desistiu de procurar emprego (VD4005), entre quem está fora da força de trabalho · "
        "PNAD Contínua Trimestral",
        "desalento.png",
        rotulos=ROTULOS_RACA_SUAVIZADA,
        formato_eixo_y=lambda v, _: f"{v:.0f}%",
    )


def grafico_gini_por_raca(gini: pd.DataFrame) -> Path:
    """Coeficiente de Gini da renda habitual real, calculado DENTRO de cada raça —
    desigualdade INTERNA a cada grupo, não o hiato ENTRE eles. Leitura que pede cuidado:
    Branca tem Gini mais alto (mais desigualdade interna) que Negra — não significa que
    a população negra está "melhor", só que sua distribuição de renda é mais comprimida
    perto da base (todo mundo mais pobre = menos variação a medir)."""
    g = gini.copy()
    g["data"] = pd.to_datetime(g["ano"].astype(str) + "-" + ((g["trimestre"] - 1) * 3 + 1).astype(str) + "-01")
    pivot = g.pivot_table(index="data", columns="raca_cor", values="gini").sort_index()
    pivot = pivot[["Branca", "Negra", "Indígena"]]
    pivot["Indígena"] = pivot["Indígena"].rolling(4, center=True, min_periods=2).mean()
    return _grafico_serie_temporal(
        pivot, CORES_RACA,
        "Coeficiente de Gini da renda, dentro de cada raça — Brasil (2012–2026)",
        "Desigualdade DENTRO de cada grupo racial (0 = igualdade perfeita, 1 = desigualdade máxima) — "
        "não é o hiato ENTRE eles · PNAD Contínua Trimestral",
        "gini_por_raca.png",
        rotulos=ROTULOS_RACA_SUAVIZADA,
        formato_eixo_y=lambda v, _: f"{v:.2f}",
    )


def grafico_theil_decomposicao(theil: pd.DataFrame) -> Path:
    """Decompõe a desigualdade TOTAL de renda (índice de Theil T) em quanto vem de
    diferença ENTRE raças vs. quanto vem de desigualdade DENTRO de cada raça, ao longo
    do tempo — área empilhada até 100%."""
    t = theil.copy()
    t["data"] = pd.to_datetime(t["ano"].astype(str) + "-" + ((t["trimestre"] - 1) * 3 + 1).astype(str) + "-01")
    t = t.sort_values("data")

    fig, ax = _novo_eixo(figsize=(11, 5.5))
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=GRADE, alpha=0.6, zorder=0)
    ax.stackplot(
        t["data"], t["pct_entre_grupos"], t["pct_dentro_grupos"],
        colors=[COR_NEGRA, COR_BRANCA], alpha=[1.0, 0.3], zorder=3,
    )
    # a faixa "entre raças" é sempre fina (~6-8% do total) — rótulo colado LOGO ACIMA da
    # fronteira entre as duas áreas, não centralizado dentro da faixa fina (mesmo bug já
    # visto no gráfico de Oaxaca-Blinder quando um segmento é pequeno demais pro texto).
    y_fronteira = t["pct_entre_grupos"].iloc[-1]
    ax.annotate(
        f"{y_fronteira:.0f}% entre raças", xy=(t["data"].iloc[-1], y_fronteira),
        xytext=(8, -12), textcoords="offset points", color=COR_NEGRA, fontsize=9.5,
        fontweight="bold", va="center",
    )
    ax.annotate(
        f"{100 - y_fronteira:.0f}% dentro de cada raça", xy=(t["data"].iloc[-1], (y_fronteira + 100) / 2),
        xytext=(8, 0), textcoords="offset points", color=TINTA_SECUNDARIA, fontsize=9.5,
        fontweight="bold", va="center",
    )
    ax.set_ylim(0, 100)
    _titulo(
        ax, "De onde vem a desigualdade de renda no Brasil: entre raças ou dentro delas?",
        "Decomposição do índice de Theil T · maior parte vem de DENTRO de cada raça, não entre elas · "
        "PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(t["data"].min(), t["data"].max() + pd.Timedelta(days=280))
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "theil_decomposicao.png")


def grafico_hiato_setor_publico_privado(hsp: pd.DataFrame) -> Path:
    """Hiato Branca vs. Negra DENTRO do setor Público e DENTRO do setor Privado,
    separadamente — testa se salário de concurso público (tabela padronizada) reduz o
    hiato racial em relação ao setor privado (negociação individual)."""
    h = hsp.copy()
    h["data"] = pd.to_datetime(h["ano"].astype(str) + "-" + ((h["trimestre"] - 1) * 3 + 1).astype(str) + "-01")
    pivot = h.pivot_table(index="data", columns="setor_trabalho", values="hiato_percentual").sort_index()
    pivot = pivot[["Público", "Privado"]]
    cores = {"Público": COR_INDIGENA, "Privado": COR_NEGRA}
    return _grafico_serie_temporal(
        pivot, cores,
        "Hiato de renda Branca vs. Negra — setor Público vs. Privado — Brasil (2012–2026)",
        "Quanto a mais Branca ganha que Negra, em % · teste de Welch por trimestre e setor · "
        "PNAD Contínua Trimestral",
        "hiato_setor_publico_privado.png",
        formato_eixo_y=lambda v, _: f"{v:.0f}%",
    )


def grafico_segregacao_setorial(seg: pd.DataFrame) -> Path:
    """Índice de dissimilaridade de Duncan entre a distribuição por setor de atividade
    econômica de Branca e de Negra — paralelo direto de `grafico_segregacao_ocupacional`,
    só que por setor (agropecuária/indústria/comércio/serviços/administração pública)
    em vez de por cargo."""
    s = seg.copy()
    s["data"] = pd.to_datetime(s["ano"].astype(str) + "-" + ((s["trimestre"] - 1) * 3 + 1).astype(str) + "-01")
    s = s.sort_values("data")
    s["indice_pct"] = s["indice_duncan_branca_negra"] * 100

    fig, ax = _novo_eixo(figsize=(11, 5.5))
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=GRADE, alpha=0.6, zorder=0)
    ax.plot(s["data"], s["indice_pct"], color=COR_PARDA, linewidth=2.2, solid_capstyle="round", zorder=3)
    ax.annotate(
        f"{s['indice_pct'].iloc[-1]:.0f}%", xy=(s["data"].iloc[-1], s["indice_pct"].iloc[-1]),
        xytext=(8, 0), textcoords="offset points", color=COR_PARDA, fontsize=11, fontweight="bold", va="center",
    )
    _titulo(
        ax, "Índice de segregação SETORIAL, Branca vs. Negra — Brasil (2012–2026)",
        "Índice de dissimilaridade de Duncan por setor de atividade econômica (não por cargo — "
        "ver segregação ocupacional) · PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    ax.set_xlim(s["data"].min(), s["data"].max() + pd.Timedelta(days=280))
    ax.set_ylim(0, s["indice_pct"].max() * 1.25)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "segregacao_setorial.png")


def grafico_sobrequalificacao(sq: pd.DataFrame) -> Path:
    """% de pessoas com Superior completo que estão em 'Ocupações elementares', por
    raça — mesmo diploma, resultado profissional diferente ("brain waste"/mismatch
    credencial-ocupação)."""
    serie = _serie_por_raca(sq, ["Branca", "Negra", "Indígena"], coluna_valor="pct_sobrequalificado",
                             suavizar={"Indígena"})
    return _grafico_serie_temporal(
        serie, CORES_RACA,
        "% com Superior completo em ocupações elementares, por raça — Brasil (2012–2026)",
        "Entre quem tem Superior completo e está ocupado · 'ocupações elementares' = grupamento "
        "ocupacional 09 (VD4011) · PNAD Contínua Trimestral",
        "sobrequalificacao.png",
        rotulos=ROTULOS_RACA_SUAVIZADA,
        formato_eixo_y=lambda v, _: f"{v:.1f}%",
    )


def grafico_funcao_quantil_racial(fq: pd.DataFrame) -> Path:
    """Função quantil da renda: quanto ganha quem está em cada percentil, dentro de
    cada raça. Responde diretamente "os 10% mais pobres entre os negros ganham quanto,
    comparado aos 10% mais pobres entre os brancos? E os 20%? E assim por diante" —
    valores reais em R$, não composição demográfica (isso já está nos gráficos de
    quartil acima). Snapshot do trimestre mais recente."""
    ultimo_ano, ultimo_trimestre = _trimestre_mais_recente(fq)
    f = fq[(fq["ano"] == ultimo_ano) & (fq["trimestre"] == ultimo_trimestre)].copy()
    pivot = f.pivot_table(index="percentil", columns="raca_cor", values="renda_no_percentil").sort_index()
    x = pivot.index.to_numpy()

    fig, ax = _novo_eixo(figsize=(11, 6.2))
    for raca, cor, desloc in [("Branca", COR_BRANCA, 10), ("Negra", COR_NEGRA, -14)]:
        ax.plot(x, pivot[raca], color=cor, linewidth=2.2, marker="o", markersize=5, zorder=3)
        for xi, yi in zip(x, pivot[raca]):
            ax.annotate(
                f"R$ {yi:,.0f}".replace(",", "."), xy=(xi, yi), xytext=(0, desloc),
                textcoords="offset points", ha="center", fontsize=7.5, color=cor, fontweight="bold",
            )
        ax.annotate(
            raca, xy=(x[-1], pivot[raca].iloc[-1]), xytext=(12, 0), textcoords="offset points",
            color=cor, fontsize=11, fontweight="bold", va="center",
        )

    ax.set_xticks(x)
    ax.set_xticklabels([f"P{p}" for p in x], fontsize=10)
    ax.set_xlim(x.min() - 5, x.max() + 15)
    ax.set_ylim(0, pivot["Branca"].max() * 1.15)
    _titulo(
        ax, "Quanto ganha quem está em cada percentil de renda, dentro de cada raça",
        f"R$ reais, a preços do trimestre mais recente · {ultimo_trimestre}º tri {ultimo_ano} · "
        "PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "funcao_quantil_racial.png")


def grafico_hiato_por_percentil(fq: pd.DataFrame) -> Path:
    """Hiato BRUTO (sem nenhum controle) entre Branca e Negra em cada percentil de
    renda — versão "crua" do hiato residual por quantil já visto (que controla por
    idade/escolaridade/ocupação); aqui é só a diferença de nível entre as duas
    distribuições, ponto a ponto."""
    ultimo_ano, ultimo_trimestre = _trimestre_mais_recente(fq)
    f = fq[(fq["ano"] == ultimo_ano) & (fq["trimestre"] == ultimo_trimestre)].copy()
    pivot = f.pivot_table(index="percentil", columns="raca_cor", values="renda_no_percentil").sort_index()
    pivot["hiato_pct"] = 100 * (pivot["Branca"] / pivot["Negra"] - 1)

    fig, ax = _novo_eixo(figsize=(10, 5.5))
    x = np.arange(len(pivot))
    barras = ax.bar(x, pivot["hiato_pct"], color=COR_NEGRA, width=0.55, zorder=3)
    for barra, v in zip(barras, pivot["hiato_pct"]):
        ax.text(barra.get_x() + barra.get_width() / 2, v + 2, f"{v:.0f}%", ha="center", fontsize=9.5,
                fontweight="bold", color=TINTA_PRIMARIA)

    ax.set_xticks(x)
    ax.set_xticklabels([f"P{p}" for p in pivot.index], fontsize=10)
    ax.set_ylim(0, pivot["hiato_pct"].max() * 1.2)
    _titulo(
        ax, "Hiato de renda Branca vs. Negra em cada percentil da distribuição",
        f"Sem nenhum controle (idade/escolaridade/ocupação) · {ultimo_trimestre}º tri {ultimo_ano} · "
        "PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "hiato_por_percentil.png")


def grafico_percentil_de_valor_racial(pv: pd.DataFrame) -> Path:
    """Pergunta INVERSA: quem ganha R$X está em que posição da distribuição de CADA
    raça? A mesma quantia pode ser mediana pra uma raça e estar entre os mais ricos da
    outra — ex.: R$3.000 é uma renda "do meio" pra Branca, mas já entra no quarto
    quartil (25% mais ricos) pra Negra, dado o hiato."""
    ultimo_ano, ultimo_trimestre = _trimestre_mais_recente(pv)
    p = pv[(pv["ano"] == ultimo_ano) & (pv["trimestre"] == ultimo_trimestre)].copy()
    valores_ordem = sorted(p["valor_referencia"].unique())
    x = np.arange(len(valores_ordem))
    largura = 0.35

    fig, ax = _novo_eixo(figsize=(11.5, 5.8))
    for i, raca in enumerate(["Branca", "Negra"]):
        valores = [
            p[(p["raca_cor"] == raca) & (p["valor_referencia"] == v)]["percentil_correspondente"].sum()
            for v in valores_ordem
        ]
        deslocamento = (i - 0.5) * largura
        barras = ax.bar(x + deslocamento, valores, largura, color=CORES_RACA[raca], zorder=3, label=raca)
        for barra, v in zip(barras, valores):
            ax.text(barra.get_x() + barra.get_width() / 2, v + 1.5, f"P{v:.0f}", ha="center",
                    fontsize=8, color=TINTA_SECUNDARIA)

    ax.set_xticks(x)
    ax.set_xticklabels([f"R$ {v:,.0f}".replace(",", ".") for v in valores_ordem], fontsize=9)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    ax.set_ylim(0, 112)
    _titulo(
        ax, "Quem ganha essa quantia está em que percentil de renda de cada raça?",
        f"Percentil correspondente a cada valor de renda, dentro de cada raça · {ultimo_trimestre}º "
        f"tri {ultimo_ano} · PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"P{v:.0f}")
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "percentil_de_valor_racial.png")


def grafico_renda_por_raca_ocupacao(rm: pd.DataFrame) -> Path:
    """Renda por raça e grupamento ocupacional (VD4011) — combinação que faltava:
    dentro de CADA categoria ocupacional, Branca ganha mais que Negra, confirmando que
    o hiato não é só "estar em ocupações diferentes" (isso já foi quantificado à parte
    na decomposição do hiato por ocupação)."""
    combinado = _combinar_negra(rm, "renda_habitual_real_media", by=["grupamento_ocupacional"])
    ordem_raca = ["Branca", "Negra", "Indígena"]
    y = np.arange(len(GRUPAMENTOS_OCUPACIONAIS_ORDEM))
    altura = 0.25
    fig, ax = _novo_eixo(figsize=(10.5, 7.5))
    for i, raca in enumerate(ordem_raca):
        valores = [
            combinado[(combinado["raca_cor"] == raca) & (combinado["grupamento_ocupacional"] == o)]["renda_habitual_real_media"].sum()
            for o in GRUPAMENTOS_OCUPACIONAIS_ORDEM
        ]
        deslocamento = (1 - i) * altura
        ax.barh(y + deslocamento, valores, altura, color=CORES_RACA[raca], zorder=3, label=raca)
    ax.set_yticks(y)
    ax.set_yticklabels([ROTULOS_OCUPACAO_CURTO[o] for o in GRUPAMENTOS_OCUPACIONAIS_ORDEM], fontsize=9.5)
    ax.invert_yaxis()
    ax.legend(loc="lower right", frameon=False, fontsize=9.5)
    _titulo(
        ax, "Renda habitual real por raça e categoria ocupacional — Brasil",
        "Últimos 8 trimestres, pessoas ocupadas · PNAD Contínua Trimestral",
    )
    ax.xaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.grid(axis="x", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "renda_por_raca_ocupacao.png")


def _grafico_heatmap_raca(
    dados: pd.DataFrame, dim_linha: str, dim_coluna: str, ordem_linha: list[str], ordem_coluna: list[str],
    rotulos_linha: dict[str, str], rotulos_coluna: dict[str, str], col_valor: str,
    titulo: str, subtitulo: str, nome_arquivo: str, figsize_painel: tuple[float, float] = (4.2, 4.6),
) -> Path:
    """Heatmap com um painel por raça (Branca/Negra/Indígena, sempre os 3, lado a lado)
    — `dim_linha` nas linhas e `dim_coluna` nas colunas de cada painel, cor = valor.
    Generaliza `grafico_renda_completa_heatmap` (um caso particular disto) pra qualquer
    par de dimensões — reaproveitado nas combinações raça×A×B que ainda faltavam."""
    ordem_raca = ["Branca", "Negra", "Indígena"]
    vmin, vmax = dados[col_valor].min(), dados[col_valor].max()

    fig, axes = plt.subplots(1, 3, figsize=(figsize_painel[0] * 3, figsize_painel[1] + 1.3), dpi=150)
    fig.patch.set_facecolor(SUPERFICIE)

    for j, raca in enumerate(ordem_raca):
        ax = axes[j]
        ax.set_facecolor(SUPERFICIE)
        sub = dados[dados["raca_cor"] == raca]
        matriz = sub.pivot_table(index=dim_linha, columns=dim_coluna, values=col_valor)
        matriz = matriz.reindex(index=ordem_linha, columns=ordem_coluna)
        ax.imshow(matriz.values, cmap=CMAP_SEQUENCIAL, vmin=vmin, vmax=vmax, aspect="auto")

        ax.set_xticks(range(len(ordem_coluna)))
        ax.set_xticklabels([rotulos_coluna.get(c, c) for c in ordem_coluna], fontsize=7.5,
                            color=TINTA_MUTED, rotation=35, ha="right")
        if j == 0:
            ax.set_yticks(range(len(ordem_linha)))
            ax.set_yticklabels([rotulos_linha.get(r, r) for r in ordem_linha], fontsize=7.5, color=TINTA_MUTED)
        else:
            ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(length=0)
        ax.set_title(raca, fontsize=11, color=TINTA_SECUNDARIA)

        for yi in range(matriz.shape[0]):
            for xi in range(matriz.shape[1]):
                v = matriz.values[yi, xi]
                if pd.notna(v):
                    cor_txt = SUPERFICIE if v > (vmin + vmax) / 2 else TINTA_PRIMARIA
                    ax.text(xi, yi, f"{v / 1000:.1f}k", ha="center", va="center", fontsize=6.5, color=cor_txt)

    fig.suptitle(titulo, fontsize=13.5, fontweight="bold", color=TINTA_PRIMARIA, x=0.02, ha="left", y=0.99)
    fig.text(0.02, 0.93, subtitulo, fontsize=9, color=TINTA_SECUNDARIA)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 0.88))
    return _salvar(fig, nome_arquivo)


def grafico_raca_genero_geracao(rmg: pd.DataFrame) -> Path:
    combinado = _combinar_negra(rmg, "renda_habitual_real_media", by=["sexo", "geracao"])
    return _grafico_heatmap_raca(
        combinado, dim_linha="geracao", dim_coluna="sexo",
        ordem_linha=GERACOES_ORDEM_GRAFICO, ordem_coluna=["Homem", "Mulher"],
        rotulos_linha=ROTULOS_GERACAO_CURTO, rotulos_coluna={"Homem": "Homens", "Mulher": "Mulheres"},
        col_valor="renda_habitual_real_media",
        titulo="Renda habitual real por raça, gênero e geração — Brasil",
        subtitulo="R$ reais (milhares), a preços do trimestre mais recente · PNAD Contínua Trimestral",
        nome_arquivo="raca_genero_geracao.png",
    )


def grafico_raca_genero_ocupacao(rm: pd.DataFrame) -> Path:
    combinado = _combinar_negra(rm, "renda_habitual_real_media", by=["sexo", "grupamento_ocupacional"])
    return _grafico_heatmap_raca(
        combinado, dim_linha="grupamento_ocupacional", dim_coluna="sexo",
        ordem_linha=GRUPAMENTOS_OCUPACIONAIS_ORDEM, ordem_coluna=["Homem", "Mulher"],
        rotulos_linha=ROTULOS_OCUPACAO_CURTO, rotulos_coluna={"Homem": "Homens", "Mulher": "Mulheres"},
        col_valor="renda_habitual_real_media",
        titulo="Renda habitual real por raça, gênero e ocupação — Brasil",
        subtitulo="R$ reais (milhares), últimos 8 trimestres, ocupados · PNAD Contínua Trimestral",
        nome_arquivo="raca_genero_ocupacao.png",
        figsize_painel=(4.2, 6.5),
    )


def grafico_raca_faixa_etaria_escolaridade(rm: pd.DataFrame) -> Path:
    combinado = _combinar_negra(rm, "renda_habitual_real_media", by=["faixa_etaria", "nivel_instrucao"])
    return _grafico_heatmap_raca(
        combinado, dim_linha="nivel_instrucao", dim_coluna="faixa_etaria",
        ordem_linha=NIVEIS_INSTRUCAO_ORDEM, ordem_coluna=FAIXAS_ETARIAS_ORDEM,
        rotulos_linha=NIVEIS_INSTRUCAO_ROTULO_CURTO, rotulos_coluna={f: f for f in FAIXAS_ETARIAS_ORDEM},
        col_valor="renda_habitual_real_media",
        titulo="Renda habitual real por raça, faixa etária e escolaridade — Brasil",
        subtitulo="R$ reais (milhares), últimos 8 trimestres, ocupados · PNAD Contínua Trimestral",
        nome_arquivo="raca_faixa_etaria_escolaridade.png",
        figsize_painel=(4.2, 5.4),
    )


def grafico_raca_faixa_etaria_ocupacao(rm: pd.DataFrame) -> Path:
    combinado = _combinar_negra(rm, "renda_habitual_real_media", by=["faixa_etaria", "grupamento_ocupacional"])
    return _grafico_heatmap_raca(
        combinado, dim_linha="grupamento_ocupacional", dim_coluna="faixa_etaria",
        ordem_linha=GRUPAMENTOS_OCUPACIONAIS_ORDEM, ordem_coluna=FAIXAS_ETARIAS_ORDEM,
        rotulos_linha=ROTULOS_OCUPACAO_CURTO, rotulos_coluna={f: f for f in FAIXAS_ETARIAS_ORDEM},
        col_valor="renda_habitual_real_media",
        titulo="Renda habitual real por raça, faixa etária e ocupação — Brasil",
        subtitulo="R$ reais (milhares), últimos 8 trimestres, ocupados · PNAD Contínua Trimestral",
        nome_arquivo="raca_faixa_etaria_ocupacao.png",
        figsize_painel=(4.2, 6.5),
    )


def grafico_raca_geracao_escolaridade(rmg: pd.DataFrame) -> Path:
    combinado = _combinar_negra(rmg, "renda_habitual_real_media", by=["geracao", "nivel_instrucao"])
    return _grafico_heatmap_raca(
        combinado, dim_linha="nivel_instrucao", dim_coluna="geracao",
        ordem_linha=NIVEIS_INSTRUCAO_ORDEM, ordem_coluna=GERACOES_ORDEM_GRAFICO,
        rotulos_linha=NIVEIS_INSTRUCAO_ROTULO_CURTO, rotulos_coluna=ROTULOS_GERACAO_CURTO,
        col_valor="renda_habitual_real_media",
        titulo="Renda habitual real por raça, geração e escolaridade — Brasil",
        subtitulo="R$ reais (milhares), últimos 8 trimestres, ocupados · PNAD Contínua Trimestral",
        nome_arquivo="raca_geracao_escolaridade.png",
        figsize_painel=(4.2, 5.4),
    )


def grafico_raca_geracao_ocupacao(rmg: pd.DataFrame) -> Path:
    combinado = _combinar_negra(rmg, "renda_habitual_real_media", by=["geracao", "grupamento_ocupacional"])
    return _grafico_heatmap_raca(
        combinado, dim_linha="grupamento_ocupacional", dim_coluna="geracao",
        ordem_linha=GRUPAMENTOS_OCUPACIONAIS_ORDEM, ordem_coluna=GERACOES_ORDEM_GRAFICO,
        rotulos_linha=ROTULOS_OCUPACAO_CURTO, rotulos_coluna=ROTULOS_GERACAO_CURTO,
        col_valor="renda_habitual_real_media",
        titulo="Renda habitual real por raça, geração e ocupação — Brasil",
        subtitulo="R$ reais (milhares), últimos 8 trimestres, ocupados · PNAD Contínua Trimestral",
        nome_arquivo="raca_geracao_ocupacao.png",
        figsize_painel=(4.2, 6.5),
    )


def grafico_raca_escolaridade_ocupacao(rm: pd.DataFrame) -> Path:
    combinado = _combinar_negra(rm, "renda_habitual_real_media", by=["nivel_instrucao", "grupamento_ocupacional"])
    return _grafico_heatmap_raca(
        combinado, dim_linha="grupamento_ocupacional", dim_coluna="nivel_instrucao",
        ordem_linha=GRUPAMENTOS_OCUPACIONAIS_ORDEM, ordem_coluna=NIVEIS_INSTRUCAO_ORDEM,
        rotulos_linha=ROTULOS_OCUPACAO_CURTO, rotulos_coluna=NIVEIS_INSTRUCAO_ROTULO_CURTO,
        col_valor="renda_habitual_real_media",
        titulo="Renda habitual real por raça, escolaridade e ocupação — Brasil",
        subtitulo="R$ reais (milhares), últimos 8 trimestres, ocupados · PNAD Contínua Trimestral",
        nome_arquivo="raca_escolaridade_ocupacao.png",
        figsize_painel=(4.6, 6.5),
    )


def grafico_hiato_por_geracao(hg: pd.DataFrame) -> Path:
    """Hiato Branca vs. Negra DENTRO de cada geração (coorte de nascimento sintética),
    ao longo do tempo. Diferença crucial em relação a um gráfico "por faixa etária":
    "pessoas de 25-39 anos" em 2012 e em 2026 são pessoas DIFERENTES (a PNAD Contínua é
    um corte transversal repetido, não um painel de décadas) — aqui cada linha segue
    (aproximadamente) a MESMA coorte de nascimento envelhecendo dentro da janela
    2012-2026."""
    h = hg.copy()
    h["data"] = pd.to_datetime(h["ano"].astype(str) + "-" + ((h["trimestre"] - 1) * 3 + 1).astype(str) + "-01")
    pivot = h.pivot_table(index="data", columns="geracao", values="hiato_percentual").sort_index()
    pivot = pivot[GERACOES_ORDEM_GRAFICO]
    pivot.columns = [ROTULOS_GERACAO_CURTO[c] for c in pivot.columns]
    cores = {ROTULOS_GERACAO_CURTO[k]: v for k, v in CORES_GERACAO.items()}
    return _grafico_serie_temporal(
        pivot, cores,
        "Hiato de renda Branca vs. Negra, por geração — Brasil (2012–2026)",
        "A MESMA coorte de nascimento envelhecendo, não a mesma faixa etária com pessoas "
        "diferentes a cada trimestre · PNAD Contínua Trimestral",
        "hiato_racial_por_geracao.png",
        formato_eixo_y=lambda v, _: f"{v:.0f}%",
    )


def grafico_renda_por_geracao_raca(rg: pd.DataFrame) -> Path:
    """Renda por geração e raça, snapshot do trimestre mais recente — cada geração na
    idade em que está HOJE (Baby Boomer mais velho, Geração Z mais jovem); não controla
    por idade, serve pra ver se o hiato racial varia de geração pra geração."""
    ultimo_ano, ultimo_trimestre = _trimestre_mais_recente(rg)
    r = rg[
        (rg["nivel_geografico"] == "brasil") & (rg["ano"] == ultimo_ano) & (rg["trimestre"] == ultimo_trimestre)
    ].copy()
    combinado = _combinar_negra(r, "renda_habitual_real_media", by=["geracao"])

    ordem_raca = ["Branca", "Negra", "Indígena"]
    x = np.arange(len(GERACOES_ORDEM_GRAFICO))
    largura = 0.25
    fig, ax = _novo_eixo(figsize=(10.5, 5.5))
    maior_valor = 0.0
    for i, raca in enumerate(ordem_raca):
        valores = [
            combinado[(combinado["raca_cor"] == raca) & (combinado["geracao"] == g)]["renda_habitual_real_media"].sum()
            for g in GERACOES_ORDEM_GRAFICO
        ]
        maior_valor = max(maior_valor, max(valores))
        deslocamento = (i - 1) * largura
        ax.bar(x + deslocamento, valores, largura, color=CORES_RACA[raca], zorder=3, label=raca)

    # headroom extra pra legenda não colidir com a barra mais alta (Branca, Baby Boomer)
    ax.set_ylim(0, maior_valor * 1.18)
    ax.set_xticks(x)
    ax.set_xticklabels([ROTULOS_GERACAO_CURTO[g] for g in GERACOES_ORDEM_GRAFICO], fontsize=10)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    _titulo(
        ax, "Renda habitual real por geração e raça — Brasil",
        f"Cada geração na idade em que está hoje (não controla por idade) · {ultimo_trimestre}º "
        f"trimestre de {ultimo_ano} · PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "renda_por_geracao_raca.png")


def _serie_topo10(perfil: pd.DataFrame, dimensao: str, categoria: str) -> pd.DataFrame:
    p = perfil[(perfil["dimensao"] == dimensao) & (perfil["categoria"] == categoria)].copy()
    p["data"] = pd.to_datetime(p["ano"].astype(str) + "-" + ((p["trimestre"] - 1) * 3 + 1).astype(str) + "-01")
    pivot = p.pivot_table(index="data", columns="raca_cor", values="pct_do_topo10").sort_index()
    return pivot[["Branca", "Negra"]]


def grafico_topo10_genero(perfil: pd.DataFrame) -> Path:
    """% de mulheres entre o topo 10% de renda DENTRO de cada raça (limiar/P90 próprio
    de cada grupo, não um corte único pro Brasil todo), ao longo do tempo."""
    pivot = _serie_topo10(perfil, "sexo", "Mulher")
    return _grafico_serie_temporal(
        pivot, {"Branca": COR_BRANCA, "Negra": COR_NEGRA},
        "% de mulheres no topo 10% de renda, dentro de cada raça — Brasil (2012–2026)",
        "Topo 10% com limiar (P90) PRÓPRIO de cada raça, não um corte único pro Brasil · "
        "PNAD Contínua Trimestral",
        "topo10_genero.png",
        formato_eixo_y=lambda v, _: f"{v:.0f}%",
    )


def grafico_topo10_escolaridade(perfil: pd.DataFrame) -> Path:
    """% com Superior completo entre o topo 10% de renda DENTRO de cada raça, ao longo
    do tempo."""
    pivot = _serie_topo10(perfil, "nivel_instrucao", "Superior completo")
    return _grafico_serie_temporal(
        pivot, {"Branca": COR_BRANCA, "Negra": COR_NEGRA},
        "% com Superior completo no topo 10% de renda, dentro de cada raça — Brasil (2012–2026)",
        "Topo 10% com limiar (P90) PRÓPRIO de cada raça · PNAD Contínua Trimestral",
        "topo10_escolaridade.png",
        formato_eixo_y=lambda v, _: f"{v:.0f}%",
    )


def grafico_topo10_escolaridade_composicao(perfil: pd.DataFrame) -> Path:
    """Composição por nível de instrução (todos os 7, não só Superior completo) do
    topo 10% de renda, Negra vs. Branca — complementa `grafico_topo10_escolaridade`
    (que só rastreia UM nível ao longo do tempo) com a distribuição completa, snapshot
    (média dos últimos 8 trimestres)."""
    d = _snapshot_topo10(perfil, "nivel_instrucao")
    x = np.arange(len(NIVEIS_INSTRUCAO_ORDEM))
    largura = 0.35
    fig, ax = _novo_eixo(figsize=(11, 5.8))
    for i, raca in enumerate(["Branca", "Negra"]):
        valores = [
            d[(d["raca_cor"] == raca) & (d["categoria"] == n)]["pct_do_topo10"].sum()
            for n in NIVEIS_INSTRUCAO_ORDEM
        ]
        deslocamento = (i - 0.5) * largura
        ax.bar(x + deslocamento, valores, largura, color=CORES_RACA[raca], zorder=3, label=raca)
    ax.set_xticks(x)
    ax.set_xticklabels([NIVEIS_INSTRUCAO_ROTULO_CURTO[n] for n in NIVEIS_INSTRUCAO_ORDEM], fontsize=9,
                       rotation=25, ha="right")
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    _titulo(
        ax, "Composição por nível de instrução do topo 10% de renda — Negra vs. Branca",
        "Topo 10% dentro de cada raça · média dos últimos 8 trimestres · PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    return _salvar(fig, "topo10_escolaridade_composicao.png")


def _snapshot_topo10(perfil: pd.DataFrame, dimensao: str, n_trimestres: int = 8) -> pd.DataFrame:
    """Média (simples, não ponderada por amostra) dos últimos `n_trimestres` — célula
    mais robusta que um único trimestre isolado pra uma composição já bem repartida."""
    p = perfil[perfil["dimensao"] == dimensao].copy()
    ultimos = p[["ano", "trimestre"]].drop_duplicates().sort_values(["ano", "trimestre"]).tail(n_trimestres)
    p = p.merge(ultimos, on=["ano", "trimestre"])
    return p.groupby(["raca_cor", "categoria"], observed=True)["pct_do_topo10"].mean().reset_index()


def grafico_topo10_faixa_etaria(perfil: pd.DataFrame) -> Path:
    """Composição por faixa etária do topo 10% de renda, Negra vs. Branca — média dos
    últimos 8 trimestres (mais robusto que um trimestre isolado)."""
    d = _snapshot_topo10(perfil, "faixa_etaria")
    x = np.arange(len(FAIXAS_ETARIAS_ORDEM))
    largura = 0.35
    fig, ax = _novo_eixo(figsize=(10, 5.5))
    for i, raca in enumerate(["Branca", "Negra"]):
        valores = [
            d[(d["raca_cor"] == raca) & (d["categoria"] == f)]["pct_do_topo10"].sum()
            for f in FAIXAS_ETARIAS_ORDEM
        ]
        deslocamento = (i - 0.5) * largura
        ax.bar(x + deslocamento, valores, largura, color=CORES_RACA[raca], zorder=3, label=raca)
    ax.set_xticks(x)
    ax.set_xticklabels(FAIXAS_ETARIAS_ORDEM, fontsize=10.5)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    _titulo(
        ax, "Composição por faixa etária do topo 10% de renda — Negra vs. Branca",
        "Topo 10% dentro de cada raça · média dos últimos 8 trimestres · PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "topo10_faixa_etaria.png")


def grafico_topo10_geracao(perfil: pd.DataFrame) -> Path:
    """Composição por geração do topo 10% de renda, Negra vs. Branca — média dos
    últimos 8 trimestres."""
    d = _snapshot_topo10(perfil, "geracao")
    x = np.arange(len(GERACOES_ORDEM_GRAFICO))
    largura = 0.35
    fig, ax = _novo_eixo(figsize=(10, 5.5))
    for i, raca in enumerate(["Branca", "Negra"]):
        valores = [
            d[(d["raca_cor"] == raca) & (d["categoria"] == g)]["pct_do_topo10"].sum()
            for g in GERACOES_ORDEM_GRAFICO
        ]
        deslocamento = (i - 0.5) * largura
        ax.bar(x + deslocamento, valores, largura, color=CORES_RACA[raca], zorder=3, label=raca)
    ax.set_xticks(x)
    ax.set_xticklabels([ROTULOS_GERACAO_CURTO[g] for g in GERACOES_ORDEM_GRAFICO], fontsize=10.5)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    _titulo(
        ax, "Composição por geração do topo 10% de renda — Negra vs. Branca",
        "Topo 10% dentro de cada raça · média dos últimos 8 trimestres · PNAD Contínua Trimestral",
    )
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="y", color=GRADE, linewidth=0.8, zorder=0)
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _salvar(fig, "topo10_geracao.png")


QUARTIS_ORDEM = ["Q1 (25% que menos ganham)", "Q2", "Q3", "Q4 (25% que mais ganham)"]
QUARTIS_ROTULO_CURTO = {
    "Q1 (25% que menos ganham)": "Q1 (mais pobres)", "Q2": "Q2", "Q3": "Q3",
    "Q4 (25% que mais ganham)": "Q4 (mais ricos)",
}


def _grafico_quartis_serie_pequenos_multiplos(
    perfil_q: pd.DataFrame, dimensao: str, categoria: str, titulo: str, subtitulo: str, nome_arquivo: str,
) -> Path:
    """4 painéis pequenos (um por quartil de renda, calculado DENTRO de cada raça), cada
    um com 2 linhas (Branca vs. Negra) da % de `categoria` dentro de `dimensao`, ao
    longo do tempo — generaliza os gráficos de topo 10% pros 4 quartis de uma vez, pra
    poder comparar a composição em QUALQUER fatia da distribuição, não só o topo."""
    p = perfil_q[(perfil_q["dimensao"] == dimensao) & (perfil_q["categoria"] == categoria)].copy()
    p["data"] = pd.to_datetime(p["ano"].astype(str) + "-" + ((p["trimestre"] - 1) * 3 + 1).astype(str) + "-01")

    fig, axes = plt.subplots(1, 4, figsize=(15.5, 4.8), dpi=150, sharey=True)
    fig.patch.set_facecolor(SUPERFICIE)
    for i, (ax, quartil) in enumerate(zip(axes, QUARTIS_ORDEM)):
        ax.set_facecolor(SUPERFICIE)
        sub = p[p["quartil"] == quartil].sort_values("data")
        for raca, cor in [("Branca", COR_BRANCA), ("Negra", COR_NEGRA)]:
            serie = sub[sub["raca_cor"] == raca]
            ax.plot(serie["data"], serie["pct_do_quartil"], color=cor, linewidth=1.8, solid_capstyle="round", zorder=3)
        ax.set_title(QUARTIS_ROTULO_CURTO[quartil], fontsize=11, color=TINTA_SECUNDARIA, loc="left")
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color(EIXO)
        ax.tick_params(axis="both", colors=TINTA_MUTED, labelsize=8, length=0, labelleft=(i == 0))
        ax.xaxis.set_major_locator(mdates.YearLocator(4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.grid(axis="y", color=GRADE, linewidth=0.7, zorder=0)
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")

    legenda = [Patch(facecolor=COR_BRANCA, label="Branca"), Patch(facecolor=COR_NEGRA, label="Negra")]
    fig.legend(handles=legenda, loc="upper right", ncol=2, frameon=False, fontsize=10, bbox_to_anchor=(0.99, 0.99))
    fig.suptitle(titulo, fontsize=14, fontweight="bold", color=TINTA_PRIMARIA, x=0.01, ha="left", y=0.99)
    fig.text(0.01, 0.93, subtitulo, fontsize=9.5, color=TINTA_SECUNDARIA, ha="left")
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.05, 1, 0.85))
    return _salvar(fig, nome_arquivo)


def grafico_quartis_genero(perfil_q: pd.DataFrame) -> Path:
    """% de mulheres em cada quartil de renda, Branca vs. Negra, ao longo do tempo —
    generaliza `grafico_topo10_genero` pros 4 quartis."""
    return _grafico_quartis_serie_pequenos_multiplos(
        perfil_q, "sexo", "Mulher",
        "% de mulheres, por quartil de renda — Branca vs. Negra",
        "Quartis calculados DENTRO de cada raça · Q1 = 25% que menos ganham, Q4 = 25% que mais ganham · "
        "PNAD Contínua Trimestral",
        "quartis_genero.png",
    )


def grafico_quartis_escolaridade(perfil_q: pd.DataFrame) -> Path:
    """% com Superior completo em cada quartil de renda, Branca vs. Negra, ao longo do
    tempo — generaliza `grafico_topo10_escolaridade` pros 4 quartis."""
    return _grafico_quartis_serie_pequenos_multiplos(
        perfil_q, "nivel_instrucao", "Superior completo",
        "% com Superior completo, por quartil de renda — Branca vs. Negra",
        "Quartis calculados DENTRO de cada raça · Q1 = 25% que menos ganham, Q4 = 25% que mais ganham · "
        "PNAD Contínua Trimestral",
        "quartis_escolaridade.png",
    )


def _snapshot_quartis(perfil_q: pd.DataFrame, dimensao: str, n_trimestres: int = 8) -> pd.DataFrame:
    """Média (simples) dos últimos `n_trimestres` — mesma lógica de `_snapshot_topo10`."""
    p = perfil_q[perfil_q["dimensao"] == dimensao].copy()
    ultimos = p[["ano", "trimestre"]].drop_duplicates().sort_values(["ano", "trimestre"]).tail(n_trimestres)
    p = p.merge(ultimos, on=["ano", "trimestre"])
    return p.groupby(["raca_cor", "quartil", "categoria"], observed=True)["pct_do_quartil"].mean().reset_index()


def _grafico_quartis_snapshot_categorico(
    perfil_q: pd.DataFrame, dimensao: str, categorias_ordem: list[str], rotulos_categoria: dict[str, str],
    titulo: str, subtitulo: str, nome_arquivo: str,
) -> Path:
    """4 painéis pequenos (um por quartil), cada um com barras agrupadas (Branca vs.
    Negra) pelas categorias de `dimensao` — composição (snapshot), não série temporal."""
    d = _snapshot_quartis(perfil_q, dimensao)
    x = np.arange(len(categorias_ordem))
    largura = 0.35

    fig, axes = plt.subplots(1, 4, figsize=(16, 4.8), dpi=150, sharey=True)
    fig.patch.set_facecolor(SUPERFICIE)
    for i, (ax, quartil) in enumerate(zip(axes, QUARTIS_ORDEM)):
        ax.set_facecolor(SUPERFICIE)
        for j, raca in enumerate(["Branca", "Negra"]):
            valores = [
                d[(d["raca_cor"] == raca) & (d["quartil"] == quartil) & (d["categoria"] == c)]["pct_do_quartil"].sum()
                for c in categorias_ordem
            ]
            deslocamento = (j - 0.5) * largura
            ax.bar(x + deslocamento, valores, largura, color=CORES_RACA[raca], zorder=3)
        ax.set_title(QUARTIS_ROTULO_CURTO[quartil], fontsize=11, color=TINTA_SECUNDARIA, loc="left")
        ax.set_xticks(x)
        ax.set_xticklabels([rotulos_categoria[c] for c in categorias_ordem], fontsize=7.5, rotation=35, ha="right")
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color(EIXO)
        ax.tick_params(axis="y", colors=TINTA_MUTED, labelsize=8, length=0, labelleft=(i == 0))
        ax.tick_params(axis="x", colors=TINTA_MUTED, length=0)
        ax.grid(axis="y", color=GRADE, linewidth=0.7, zorder=0)
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")

    legenda = [Patch(facecolor=COR_BRANCA, label="Branca"), Patch(facecolor=COR_NEGRA, label="Negra")]
    fig.legend(handles=legenda, loc="upper right", ncol=2, frameon=False, fontsize=10, bbox_to_anchor=(0.99, 0.99))
    fig.suptitle(titulo, fontsize=14, fontweight="bold", color=TINTA_PRIMARIA, x=0.01, ha="left", y=0.99)
    fig.text(0.01, 0.93, subtitulo, fontsize=9.5, color=TINTA_SECUNDARIA, ha="left")
    _rodape(fig)
    fig.tight_layout(rect=(0, 0.16, 1, 0.85))
    return _salvar(fig, nome_arquivo)


def grafico_quartis_faixa_etaria(perfil_q: pd.DataFrame) -> Path:
    """Composição por faixa etária de cada quartil de renda, Branca vs. Negra —
    generaliza `grafico_topo10_faixa_etaria` pros 4 quartis."""
    return _grafico_quartis_snapshot_categorico(
        perfil_q, "faixa_etaria", FAIXAS_ETARIAS_ORDEM, {f: f for f in FAIXAS_ETARIAS_ORDEM},
        "Composição por faixa etária, por quartil de renda — Branca vs. Negra",
        "Quartis calculados DENTRO de cada raça · média dos últimos 8 trimestres · PNAD Contínua Trimestral",
        "quartis_faixa_etaria.png",
    )


def grafico_quartis_geracao(perfil_q: pd.DataFrame) -> Path:
    """Composição por geração de cada quartil de renda, Branca vs. Negra — generaliza
    `grafico_topo10_geracao` pros 4 quartis."""
    return _grafico_quartis_snapshot_categorico(
        perfil_q, "geracao", GERACOES_ORDEM_GRAFICO, ROTULOS_GERACAO_CURTO,
        "Composição por geração, por quartil de renda — Branca vs. Negra",
        "Quartis calculados DENTRO de cada raça · média dos últimos 8 trimestres · PNAD Contínua Trimestral",
        "quartis_geracao.png",
    )


def grafico_quartis_escolaridade_composicao(perfil_q: pd.DataFrame) -> Path:
    """Composição por nível de instrução (todos os 7, não só Superior completo) de
    cada quartil de renda, Branca vs. Negra — complementa `grafico_quartis_escolaridade`
    (que só rastreia UM nível ao longo do tempo) com a distribuição completa."""
    return _grafico_quartis_snapshot_categorico(
        perfil_q, "nivel_instrucao", NIVEIS_INSTRUCAO_ORDEM, NIVEIS_INSTRUCAO_ROTULO_CURTO,
        "Composição por nível de instrução, por quartil de renda — Branca vs. Negra",
        "Quartis calculados DENTRO de cada raça · média dos últimos 8 trimestres · PNAD Contínua Trimestral",
        "quartis_escolaridade_composicao.png",
    )


def main() -> None:
    renda = pd.read_parquet(REPO_ROOT / "data" / "processed" / "renda.parquet")
    esc = pd.read_parquet(REPO_ROOT / "data" / "processed" / "escolaridade.parquet")
    rpe = pd.read_parquet(REPO_ROOT / "data" / "processed" / "renda_por_escolaridade.parquet")
    rc = pd.read_parquet(REPO_ROOT / "data" / "processed" / "renda_completa.parquet")
    hiato = pd.read_parquet(REPO_ROOT / "data" / "processed" / "hiato_racial.parquet")
    decomp = pd.read_parquet(REPO_ROOT / "data" / "processed" / "decomposicao_hiato_ocupacional.parquet")
    ob = pd.read_parquet(REPO_ROOT / "data" / "processed" / "decomposicao_oaxaca_blinder.parquet")
    hiato_regional = pd.read_parquet(REPO_ROOT / "data" / "processed" / "hiato_regional.parquet")
    segregacao = pd.read_parquet(REPO_ROOT / "data" / "processed" / "segregacao_ocupacional.parquet")
    quebra = pd.read_parquet(REPO_ROOT / "data" / "processed" / "quebra_estrutural.parquet")
    informalidade = pd.read_parquet(REPO_ROOT / "data" / "processed" / "informalidade.parquet")
    horas = pd.read_parquet(REPO_ROOT / "data" / "processed" / "horas_trabalhadas.parquet")
    alfabetizacao = pd.read_parquet(REPO_ROOT / "data" / "processed" / "alfabetizacao.parquet")
    desalento = pd.read_parquet(REPO_ROOT / "data" / "processed" / "desalento_subutilizacao.parquet")
    renda_geracao = pd.read_parquet(REPO_ROOT / "data" / "processed" / "renda_por_geracao.parquet")
    hiato_geracao = pd.read_parquet(REPO_ROOT / "data" / "processed" / "hiato_por_geracao.parquet")
    perfil_topo10 = pd.read_parquet(REPO_ROOT / "data" / "processed" / "perfil_topo10_racial.parquet")
    perfil_quartis = pd.read_parquet(REPO_ROOT / "data" / "processed" / "perfil_quartis_racial.parquet")
    gini = pd.read_parquet(REPO_ROOT / "data" / "processed" / "gini_por_raca.parquet")
    theil = pd.read_parquet(REPO_ROOT / "data" / "processed" / "theil_racial.parquet")
    hiato_setor = pd.read_parquet(REPO_ROOT / "data" / "processed" / "hiato_setor_publico_privado.parquet")
    segregacao_setor = pd.read_parquet(REPO_ROOT / "data" / "processed" / "segregacao_setorial.parquet")
    sobrequalificacao = pd.read_parquet(REPO_ROOT / "data" / "processed" / "sobrequalificacao.parquet")
    funcao_quantil = pd.read_parquet(REPO_ROOT / "data" / "processed" / "funcao_quantil_racial.parquet")
    percentil_de_valor = pd.read_parquet(REPO_ROOT / "data" / "processed" / "percentil_de_valor_racial.parquet")
    renda_multi_faixa = pd.read_parquet(REPO_ROOT / "data" / "processed" / "renda_multidimensional_faixa.parquet")
    renda_multi_geracao = pd.read_parquet(REPO_ROOT / "data" / "processed" / "renda_multidimensional_geracao.parquet")

    destinos = [
        # raça
        grafico_renda_por_raca(renda),
        grafico_renda_preta_parda(renda),
        # hiato Branca vs. Negra, série histórica, com significância
        grafico_hiato_percentual(hiato),
        grafico_hiato_absoluto(hiato),
        grafico_decomposicao_hiato(decomp),
        # aprofundamentos: regressão (Oaxaca-Blinder), região, segregação, quebra estrutural
        grafico_oaxaca_blinder_decomposicao(ob),
        grafico_oaxaca_blinder_quantis(ob),
        grafico_hiato_regional(hiato_regional),
        grafico_segregacao_ocupacional(segregacao),
        grafico_quebra_estrutural(hiato, quebra),
        # aprofundamentos: novas variáveis (informalidade, horas, alfabetização, desalento)
        grafico_informalidade(informalidade),
        grafico_renda_por_hora(horas),
        grafico_alfabetizacao(alfabetizacao),
        grafico_desalento(desalento),
        # aprofundamentos: geração (coorte de nascimento, corrige o viés "não são as
        # mesmas pessoas" da faixa etária) e perfil de quem está no topo 10% de renda
        # dentro de cada raça
        grafico_hiato_por_geracao(hiato_geracao),
        grafico_renda_por_geracao_raca(renda_geracao),
        grafico_topo10_genero(perfil_topo10),
        grafico_topo10_escolaridade(perfil_topo10),
        grafico_topo10_escolaridade_composicao(perfil_topo10),
        grafico_topo10_faixa_etaria(perfil_topo10),
        grafico_topo10_geracao(perfil_topo10),
        # decomposição dos 4 quartis (generaliza o topo 10% pra toda a distribuição)
        grafico_quartis_genero(perfil_quartis),
        grafico_quartis_escolaridade(perfil_quartis),
        grafico_quartis_escolaridade_composicao(perfil_quartis),
        grafico_quartis_faixa_etaria(perfil_quartis),
        grafico_quartis_geracao(perfil_quartis),
        # desigualdade dentro de cada raça, setor público x privado, segregação
        # setorial e sobre-qualificação
        grafico_gini_por_raca(gini),
        grafico_theil_decomposicao(theil),
        grafico_hiato_setor_publico_privado(hiato_setor),
        grafico_segregacao_setorial(segregacao_setor),
        grafico_sobrequalificacao(sobrequalificacao),
        # função quantil da renda em R$ (não composição demográfica) e sua inversa
        grafico_funcao_quantil_racial(funcao_quantil),
        grafico_hiato_por_percentil(funcao_quantil),
        grafico_percentil_de_valor_racial(percentil_de_valor),
        # combinações raça×A×B que faltavam pra fechar a matriz completa (ocupação,
        # geração e faixa etária cruzadas entre si e com gênero/escolaridade)
        grafico_renda_por_raca_ocupacao(renda_multi_faixa),
        grafico_raca_genero_geracao(renda_multi_geracao),
        grafico_raca_genero_ocupacao(renda_multi_faixa),
        grafico_raca_faixa_etaria_escolaridade(renda_multi_faixa),
        grafico_raca_faixa_etaria_ocupacao(renda_multi_faixa),
        grafico_raca_geracao_escolaridade(renda_multi_geracao),
        grafico_raca_geracao_ocupacao(renda_multi_geracao),
        grafico_raca_escolaridade_ocupacao(renda_multi_faixa),
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
        # escolaridade x raça x gênero (nível de instrução, não renda) — combinado
        # (Superior completo, já era o destaque) + um por nível (os outros 6 faltavam)
        *[grafico_escolaridade_por_raca_genero(esc, nivel=n) for n in NIVEIS_INSTRUCAO_ORDEM],
        # raça x gênero x faixa etária x escolaridade
        grafico_renda_completa_heatmap(rc),
    ]
    for destino in destinos:
        print(f"Gráfico salvo em: {destino.relative_to(REPO_ROOT)}")
    print(f"\nTotal: {len(destinos)} gráficos.")


if __name__ == "__main__":
    main()
