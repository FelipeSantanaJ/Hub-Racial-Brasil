"""Reconstrução do deck — ÁRVORE cruzada de renda por raça (itens 1-10).

Estrutura v3 (2026-09-06):
- **valor_serie**: série histórica de renda (linha, 2012-2026). Sem snapshot de renda.
- **hiato_serie**: série histórica do hiato de renda, com Welch. UM GRÁFICO POR
  COMPARAÇÃO — "Branca vs. Negra" e "Branca vs. Indígena" em slides SEPARADOS (a série
  de Indígena tem muitos picos por causa da amostra pequena; sobrepor as duas atrapalha
  a leitura). A série de Indígena é suavizada (média móvel de 4 trimestres). "Combinada"
  (todos os recortes num painel) também vira 2 slides, um por comparação.
- **hiato_snapshot**: hiato do trimestre mais recente, também 1 gráfico por comparação
  (barras vs. Negra num slide, vs. Indígena noutro), com asteriscos de Welch.
- Itens 9-10: a série de hiato por célula fica só em Branca vs. Negra (Indígena por
  célula gênero×faixa/geração×escolaridade quase nunca tem amostra ≥ 30); a visão de
  Indígena para esses itens está nos 2 heatmaps por gênero (vs. Negra / vs. Indígena).

Raças nos valores: Branca / Negra (Preta+Parda, ponderado) / Indígena — Indígena nunca
descartado (linha some onde a amostra < 30).

Figuras "cruas" — sem título/subtítulo/rodapé (isso vira caixa de texto no PPT). O
manifesto (`docs/arvore_manifest.json`, chave `arvore`) grava titulo/subtitulo/legenda.

Uso:
    python -m src.processing.graficos_arvore            # itens 1-10
    python -m src.processing.graficos_arvore 1 2 6      # só alguns
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from src.processing import graficos_fase1 as g

REPO_ROOT = g.REPO_ROOT
OUTPUT_DIR = g.OUTPUT_DIR
PROCESSED = REPO_ROOT / "data" / "processed"
MANIFESTO = REPO_ROOT / "docs" / "arvore_manifest.json"

FONTE = "Fonte: IBGE, PNAD Contínua Trimestral (microdados). Elaboração própria."
RACAS_VALOR = ["Branca", "Negra", "Indígena"]
CMP = [("Negra", "ne", g.COR_NEGRA), ("Indígena", "in", g.COR_INDIGENA)]
NOTA_SERIE = "R$ reais, a preços do trimestre mais recente (deflator IBGE) · série 2012–2026"
SUB_HS = "hiato = renda média Branca − renda média do grupo, % relativo ao grupo · Welch trimestre a trimestre"
SUB_HS_IND = SUB_HS + " · série de Indígena suavizada (média móvel 4 trim., amostra pequena)"
SUB_HSNAP = "% de diferença de renda · Welch: *** p<0,001  ** p<0,01  * p<0,05  ·  n.s. = não signif."


# ======================================================================= #
# Renderizadores crus
# ======================================================================= #
def _salvar(fig, nome) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = OUTPUT_DIR / nome
    fig.savefig(dest, facecolor=g.SUPERFICIE, bbox_inches="tight", dpi=82)
    plt.close(fig)
    return dest


_salvar_bare = _salvar  # compat: graficos_extremos.py importa este nome


def _placeholder(nome, msg="Amostra insuficiente para este corte") -> Path:
    fig, ax = plt.subplots(figsize=(8, 4.0), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    ax.set_facecolor(g.SUPERFICIE)
    ax.axis("off")
    ax.text(0.5, 0.5, msg, ha="center", va="center", fontsize=13, color=g.TINTA_MUTED)
    return _salvar(fig, nome)


def _estilo(ax):
    ax.set_facecolor(g.SUPERFICIE)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(g.EIXO)
    ax.tick_params(axis="both", colors=g.TINTA_MUTED, labelsize=9.5, length=0)


def _fmt_reais(v):
    return f"R$ {v:,.0f}".replace(",", ".")


def _fig_serie(serie: pd.DataFrame, cores: dict, nome, pct=False, cruza_zero=False) -> Path:
    serie = serie.dropna(how="all")
    if serie.empty or not np.isfinite(serie.to_numpy(dtype=float)).any():
        return _placeholder(nome)
    fig, ax = plt.subplots(figsize=(11, 4.7), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    _estilo(ax)
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=g.GRADE, alpha=0.6, zorder=0)
    vmax = np.nanmax(serie.to_numpy(dtype=float))
    vmin = np.nanmin(serie.to_numpy(dtype=float))
    span = (vmax - vmin) or 1
    if cruza_zero or vmin < 0:
        ax.set_ylim(vmin - span * 0.12, vmax + span * 0.12)
        ax.axhline(0, color=g.EIXO, linewidth=1)
    else:
        ax.set_ylim(vmin * 0.9 if vmin > 0 else 0,
                    (min(vmax * 1.2, 100) if pct and vmax <= 100 else vmax * 1.2))
    for c in serie.columns:
        ls = "--" if any(t in str(c) for t in ("Homem", "Homens")) else "-"
        ax.plot(serie.index, serie[c], color=cores.get(c, g.TINTA_MUTED), linewidth=2,
                linestyle=ls, solid_capstyle="round", dash_capstyle="round", zorder=3)
    fin = sorted((serie[c].iloc[-1], c, cores.get(c, g.TINTA_MUTED))
                 for c in serie.columns if pd.notna(serie[c].iloc[-1]))
    for i in range(1, len(fin)):
        if fin[i][0] - fin[i - 1][0] < span * 0.07:
            fin[i] = (fin[i - 1][0] + span * 0.07, *fin[i][1:])
    for y, rot, cor in fin:
        ax.annotate(rot, xy=(serie.index[-1], y), xytext=(8, 0), textcoords="offset points",
                    color=cor, fontsize=9.5, fontweight="bold", va="center")
    ax.set_xlim(serie.index.min(), serie.index.max() + pd.Timedelta(days=330))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
    ax.yaxis.set_major_formatter((lambda v, _: f"{v:.0f}%") if pct else (lambda v, _: _fmt_reais(v)))
    fig.tight_layout()
    return _salvar(fig, nome)


def _fig_serie_multipanel(paineis: dict[str, pd.DataFrame], cores: dict, nome, pct=False) -> Path:
    paineis = {k: v.dropna(how="all") for k, v in paineis.items()}
    paineis = {k: v for k, v in paineis.items() if not v.empty and np.isfinite(v.to_numpy(dtype=float)).any()}
    if not paineis:
        return _placeholder(nome)
    n = len(paineis)
    fig, axes = plt.subplots(1, n, figsize=(4.7 * n, 4.6), dpi=150, sharey=True)
    fig.patch.set_facecolor(g.SUPERFICIE)
    if n == 1:
        axes = [axes]
    todos = pd.concat(paineis.values())
    vmax, vmin = np.nanmax(todos.to_numpy(dtype=float)), np.nanmin(todos.to_numpy(dtype=float))
    for ax, (tp, serie) in zip(axes, paineis.items()):
        _estilo(ax)
        ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=g.GRADE, alpha=0.6, zorder=0)
        if vmin < 0:
            ax.axhline(0, color=g.EIXO, linewidth=1)
        for c in serie.columns:
            ax.plot(serie.index, serie[c], color=cores.get(c, g.TINTA_MUTED), linewidth=1.8, zorder=3)
            if pd.notna(serie[c].iloc[-1]):
                ax.annotate(c, xy=(serie.index[-1], serie[c].iloc[-1]), xytext=(4, 0),
                            textcoords="offset points", color=cores.get(c, g.TINTA_MUTED),
                            fontsize=7.5, fontweight="bold", va="center")
        ax.set_title(tp, fontsize=11, color=g.TINTA_SECUNDARIA)
        ax.set_xlim(serie.index.min(), serie.index.max() + pd.Timedelta(days=520))
        ax.xaxis.set_major_locator(mdates.YearLocator(4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
    axes[0].yaxis.set_major_formatter((lambda v, _: f"{v:.0f}%") if pct else (lambda v, _: _fmt_reais(v)))
    if vmin >= 0:
        axes[0].set_ylim(0, (min(vmax * 1.2, 100) if pct and vmax <= 100 else vmax * 1.2))
    fig.tight_layout()
    return _salvar(fig, nome)


def _fig_serie_categorias(serie: pd.DataFrame, cores: dict, nome, pct=True) -> Path:
    """Série com N linhas (categorias de uma dimensão) — painel único, rótulos ao fim
    com anti-colisão. Usado nos gráficos combinados de hiato (uma comparação por vez)."""
    return _fig_serie(serie, cores, nome, pct=pct, cruza_zero=True)


def _fig_hiato_bar(cats, rotulos, por_cat: dict, cor, nome) -> Path:
    """por_cat[cat] = (hiato_pct, p_valor). Uma barra por categoria, asterisco de Welch."""
    vals = [por_cat.get(c, (np.nan, np.nan)) for c in cats]
    validos = [v for v, _ in vals if pd.notna(v)]
    if not validos:
        return _placeholder(nome)
    x = np.arange(len(cats))
    fig, ax = plt.subplots(figsize=(max(7, 1.3 * len(cats) + 2.5), 4.6), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    _estilo(ax)
    lo, hi = min(0, min(validos)), max(0, max(validos))
    m = (hi - lo) * 0.22 or 1
    ax.set_ylim(lo - m * (1.1 if lo < 0 else 0), hi + m)
    ax.bar(x, [v if pd.notna(v) else 0 for v, _ in vals], 0.55, color=cor, zorder=3)
    for xi, (v, p) in zip(x, vals):
        if pd.isna(v):
            continue
        ax.text(xi, v + m * (0.10 if v >= 0 else -0.20), f"{v:.0f}%\n{g._marca_significancia(p)}",
                ha="center", va="bottom" if v >= 0 else "top", fontsize=9.5, fontweight="bold",
                color=g.TINTA_PRIMARIA)
    ax.axhline(0, color=g.EIXO, linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(rotulos, fontsize=10, rotation=18 if len(cats) > 4 else 0,
                       ha="right" if len(cats) > 4 else "center")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
    fig.tight_layout()
    return _salvar(fig, nome)


def _fig_hiato_bar_2cmp(por_cmp: dict, nome) -> Path:
    """Um gráfico com 2 barras: hiato Branca vs. Negra e Branca vs. Indígena (usado só
    na análise de Raça sozinha, onde o snapshot é só 2 números)."""
    itens = [(f"Branca vs. {c}", *por_cmp.get(c, (np.nan, np.nan)), cor) for c, _sl, cor in CMP]
    validos = [v for _, v, _p, _c in itens if pd.notna(v)]
    if not validos:
        return _placeholder(nome)
    x = np.arange(len(itens))
    fig, ax = plt.subplots(figsize=(6.5, 4.6), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    _estilo(ax)
    hi = max(validos)
    ax.set_ylim(0, hi * 1.25)
    for xi, (rot, v, p, cor) in zip(x, itens):
        if pd.isna(v):
            continue
        ax.bar(xi, v, 0.5, color=cor, zorder=3)
        ax.text(xi, v + hi * 0.03, f"{v:.0f}%\n{g._marca_significancia(p)}", ha="center",
                va="bottom", fontsize=10.5, fontweight="bold", color=g.TINTA_PRIMARIA)
    ax.set_xticks(x)
    ax.set_xticklabels([rot for rot, *_ in itens], fontsize=10.5)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
    fig.tight_layout()
    return _salvar(fig, nome)


def _fig_hiato_heatmap(dados, dim_l, dim_c, nome) -> Path:
    ml, mc = g.METADADOS_DIM_HIATO[dim_l], g.METADADOS_DIM_HIATO[dim_c]
    ol, oc = ml["ordem"], mc["ordem"]
    d = dados[dados[dim_l].isin(ol) & dados[dim_c].isin(oc)]
    m = d.pivot_table(index=dim_l, columns=dim_c, values="hiato_percentual").reindex(index=ol, columns=oc)
    mp = d.pivot_table(index=dim_l, columns=dim_c, values="p_valor").reindex(index=ol, columns=oc)
    arr = m.to_numpy(dtype=float)
    fin = arr[np.isfinite(arr)]
    if not len(fin):
        return _placeholder(nome)
    lim = np.abs(fin).max() or 1
    fig, ax = plt.subplots(figsize=(1.15 * len(oc) + 3.5, 0.7 * len(ol) + 2.6), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    ax.set_facecolor(g.SUPERFICIE)
    im = ax.imshow(arr, cmap=g.CMAP_DIVERGENTE_HIATO, vmin=-lim, vmax=lim, aspect="auto")
    ax.set_xticks(range(len(oc)))
    ax.set_xticklabels([mc["rotulos"].get(c, c) for c in oc], fontsize=8.5, color=g.TINTA_MUTED, rotation=35, ha="right")
    ax.set_yticks(range(len(ol)))
    ax.set_yticklabels([ml["rotulos"].get(r, r) for r in ol], fontsize=8.5, color=g.TINTA_MUTED)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    for yi in range(m.shape[0]):
        for xi in range(m.shape[1]):
            v = arr[yi, xi]
            if pd.notna(v):
                cor = g.TINTA_PRIMARIA if abs(v) < lim * 0.55 else g.SUPERFICIE
                ax.text(xi, yi, f"{v:.0f}%\n{g._marca_significancia(mp.to_numpy(dtype=float)[yi, xi])}",
                        ha="center", va="center", fontsize=7.5, color=cor)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03).ax.tick_params(labelsize=8, colors=g.TINTA_MUTED)
    fig.tight_layout()
    return _salvar(fig, nome)


# ======================================================================= #
# Dados
# ======================================================================= #
def _serie_valor(df, filtro=None, sexo=None) -> pd.DataFrame:
    return g._serie_por_raca(df, RACAS_VALOR, filtro_extra=filtro, sexo=sexo, suavizar={"Indígena"})


def _serie_valor_rg(renda) -> pd.DataFrame:
    cols = {}
    for raca in RACAS_VALOR:
        for sexo, rs in [("Mulher", "Mulheres"), ("Homem", "Homens")]:
            s = g._serie_por_raca(renda, [raca], sexo=sexo,
                                  suavizar={"Indígena"} if raca == "Indígena" else None)
            cols[f"{raca} · {rs}"] = s[raca]
    return pd.DataFrame(cols).sort_index()


def _hia_filtra(hia, combo, **kw):
    d = hia[hia["combo"] == combo]
    for k, v in kw.items():
        d = d[d[k] == v]
    return d


def _hiato_serie_1(hia, combo, comparacao, suavizar, **kw) -> pd.DataFrame:
    """Série (1 coluna, index=data) do hiato % de uma comparação."""
    d = _hia_filtra(hia, combo, comparacao=comparacao, **kw).copy()
    if d.empty:
        return pd.DataFrame()
    d["data"] = pd.to_datetime(d["ano"].astype(str) + "-" + ((d["trimestre"] - 1) * 3 + 1).astype(str) + "-01")
    s = d.set_index("data")["hiato_percentual"].sort_index()
    if suavizar:
        s = s.rolling(4, center=True, min_periods=2).mean()
    return s.to_frame(f"Branca vs. {comparacao}")


def _hiato_serie_cat(hia, combo, dim, cats, comparacao, suavizar, **kw) -> pd.DataFrame:
    """Série com uma coluna por categoria de `dim` (para o gráfico combinado)."""
    d = _hia_filtra(hia, combo, comparacao=comparacao, **kw).copy()
    if d.empty:
        return pd.DataFrame()
    d["data"] = pd.to_datetime(d["ano"].astype(str) + "-" + ((d["trimestre"] - 1) * 3 + 1).astype(str) + "-01")
    piv = d.pivot_table(index="data", columns=dim, values="hiato_percentual")
    piv = piv.reindex(columns=[c for c, _, _ in cats]).rename(columns={c: r for c, r, _ in cats}).sort_index()
    return piv.rolling(4, center=True, min_periods=2).mean() if suavizar else piv


def _hiato_snap_1(hia, combo, comparacao, **kw):
    d = _hia_filtra(hia, combo, comparacao=comparacao, **kw)
    if d.empty:
        return (np.nan, np.nan)
    r = d.sort_values(["ano", "trimestre"]).iloc[-1]
    return (r["hiato_percentual"], r["p_valor"])


# ======================================================================= #
_SLUG_FX = {f: f.replace("+", "mais").replace("-", "_") for f in g.FAIXAS_ETARIAS_ORDEM}
_GER = g.GERACOES_ORDEM_GRAFICO
_ROT_GER = g.ROTULOS_GERACAO_CURTO
_NIV = g.NIVEIS_INSTRUCAO_ORDEM
_ROT_NIV = g.NIVEIS_INSTRUCAO_ROTULO_CURTO


def _folha(tipo, ramo, sub, titulo, subtitulo, arquivo, legenda):
    return {"tipo": tipo, "ramo": ramo, "sub": sub, "titulo": titulo,
            "subtitulo": subtitulo, "arquivo": arquivo, "legenda": legenda}


def _tit(*partes):
    return " — ".join(p for p in partes if p)


def _emit_hs_recorte(f, hia, combo, ramo, rot, titulo_base, arq_base, rot_titulo=None, **cell):
    """2 folhas: série do hiato vs. Negra e vs. Indígena, em slides separados. O recorte
    (`rot_titulo`, default = `rot`) entra EXPLÍCITO no título."""
    rt = rot if rot_titulo is None else rot_titulo
    for cmp_, sl, cor in CMP:
        piv = _hiato_serie_1(hia, combo, cmp_, suavizar=(cmp_ == "Indígena"), **cell)
        nome = f"{arq_base}_{sl}.png"
        _fig_serie(piv, {f"Branca vs. {cmp_}": cor}, nome, pct=True, cruza_zero=True)
        f.append(_folha("hiato_serie", ramo, f"{rot} · hiato vs. {cmp_}",
                        _tit(titulo_base, rt, f"Branca vs. {cmp_}", "Brasil"),
                        SUB_HS_IND if cmp_ == "Indígena" else SUB_HS, nome,
                        f"Hiato de renda Branca vs. {cmp_} — {rot} — 2012–2026 (Welch)."))


def _emit_hs_comb(f, hia, combo, dim, cats, cores_cat, ramo, titulo_base, arq_base, **cell):
    """2 folhas: série combinada (uma linha por categoria) vs. Negra e vs. Indígena."""
    dnome = dim.replace("_", " ")
    for cmp_, sl, _cor in CMP:
        piv = _hiato_serie_cat(hia, combo, dim, cats, cmp_, suavizar=(cmp_ == "Indígena"), **cell)
        nome = f"{arq_base}_{sl}.png"
        _fig_serie_categorias(piv, cores_cat, nome)
        f.append(_folha("hiato_serie", ramo, f"{ramo if ramo != '—' else 'Combinada'} · hiato por {dnome} · vs. {cmp_}",
                        f"{titulo_base} — Branca vs. {cmp_} — Brasil",
                        SUB_HS_IND if cmp_ == "Indígena" else SUB_HS, nome,
                        f"Hiato de renda Branca vs. {cmp_} por {dnome} — 2012–2026 (Welch)."))


def _emit_hsnap(f, hia, combo, dim, cats, ramo, titulo_base, arq_base, qq, **cell):
    """2 folhas: snapshot do hiato (barras por categoria) vs. Negra e vs. Indígena."""
    dnome = dim.replace("_", " ") if dim else ""
    for cmp_, sl, cor in CMP:
        por_cat = {rot: _hiato_snap_1(hia, combo, cmp_, **({dim: c} if dim else {}), **cell)
                   for c, rot, _ in cats}
        nome = f"{arq_base}_{sl}.png"
        _fig_hiato_bar([rot for _, rot, _ in cats], [rot for _, rot, _ in cats], por_cat, cor, nome)
        sufixo = f" por {dnome}" if dnome else ""
        f.append(_folha("hiato_snapshot", ramo, f"{ramo if ramo != '—' else 'Snapshot'} · hiato{sufixo} · vs. {cmp_}",
                        f"{titulo_base} — Branca vs. {cmp_} — Brasil",
                        f"{SUB_HSNAP} · {qq}" + (f" · só {ramo.lower()}" if ramo != "—" else ""), nome,
                        f"Hiato Branca vs. {cmp_}{sufixo} — {qq}."))


def _emit_valor_comb_split(f, df, dim, cats, cores_cat, ramo, titulo_base, arq_base, sexo=None):
    """N folhas (uma por raça): série de renda com uma linha por categoria de `dim`,
    dentro de cada raça. Substitui o gráfico de 3 painéis (Branca|Negra|Indígena) por
    3 slides — um por raça — pra dar espaço a cada painel."""
    dnome = dim.replace("_", " ")
    for raca in RACAS_VALOR:
        cols = {rot: g._serie_por_raca(df, [raca], filtro_extra={dim: c}, sexo=sexo,
                                       suavizar={"Indígena"} if raca == "Indígena" else None)[raca]
                for c, rot, _ in cats}
        piv = pd.DataFrame(cols).sort_index()
        nome = f"{arq_base}_{g._slug(raca)}.png"
        _fig_serie(piv, cores_cat, nome)
        rs = ramo if ramo != "—" else ""
        f.append(_folha("valor_serie", ramo, _tit(rs, raca, "Combinado"),
                        _tit(titulo_base, rs, raca, "Brasil"), NOTA_SERIE, nome,
                        _tit(f"Renda média real por {dnome}", raca, rs) + " — série histórica."))


def construir(itens: set, dados: dict) -> list[dict]:
    renda, rpe, rg = dados["renda"], dados["renda_por_escolaridade"], dados["renda_por_geracao"]
    rc, rcg, hia = dados["renda_completa"], dados["renda_completa_geracao"], dados["hiato_arvore"]
    ano, tri = g._trimestre_mais_recente(renda)
    qq = f"{tri}º tri. {ano}"
    secoes = []

    def cores_de(cats):
        return {rot: c for (_, rot, _), c in zip(cats, plt.cm.viridis(np.linspace(0.12, 0.9, len(cats))))}

    # -------------------------------------------------------------- 1. Raça
    if 1 in itens:
        f = []
        _fig_serie(_serie_valor(renda), g.CORES_RACA, "arv_raca_serie.png")
        f.append(_folha("valor_serie", "—", "Raça", "Renda média real por raça — Brasil",
                        NOTA_SERIE, "arv_raca_serie.png", "Renda média real por raça — série histórica."))
        _emit_hs_recorte(f, hia, "", "—", "Raça (Brasil)", "Hiato de renda", "arv_raca_hiato_serie", rot_titulo="")
        # análise de Raça sozinha: o snapshot é só 2 números — 1 gráfico com as 2 barras.
        _fig_hiato_bar_2cmp({c: _hiato_snap_1(hia, "", c) for c, _s, _co in CMP}, "arv_raca_hiato_snapshot.png")
        f.append(_folha("hiato_snapshot", "—", "Hiato — snapshot",
                        "Hiato de renda — Branca vs. Negra e vs. Indígena — Brasil",
                        f"{SUB_HSNAP} · {qq}", "arv_raca_hiato_snapshot.png",
                        f"Hiato Branca vs. Negra e Branca vs. Indígena — {qq}."))
        secoes.append({"item": 1, "titulo": "Raça", "folhas": f})

    # ---------------------------------------------------- 2. Raça × Gênero
    if 2 in itens:
        f = []
        _fig_serie(_serie_valor_rg(renda),
                   {f"{r} · {s}": g.CORES_RACA[r] for r in RACAS_VALOR for s in ("Mulheres", "Homens")},
                   "arv_rg_comb_serie.png")
        f.append(_folha("valor_serie", "Combinado", "Combinado", "Renda média real por raça e gênero — Brasil",
                        NOTA_SERIE, "arv_rg_comb_serie.png", "Renda média real por raça e gênero — série (6 linhas)."))
        for sexo, rs in [("Mulher", "Mulheres"), ("Homem", "Homens")]:
            _fig_serie(_serie_valor(renda, sexo=sexo), g.CORES_RACA, f"arv_rg_{rs.lower()}_serie.png")
            f.append(_folha("valor_serie", rs, rs, f"Renda média real por raça — {rs} — Brasil",
                            NOTA_SERIE, f"arv_rg_{rs.lower()}_serie.png",
                            f"Renda média real por raça — {rs} — série histórica."))
        cc = cores_de([("Homem", "Homens", 0), ("Mulher", "Mulheres", 0)])
        _emit_hs_comb(f, hia, "sexo", "sexo", [("Homem", "Homens", "h"), ("Mulher", "Mulheres", "m")],
                      cc, "—", "Hiato de renda por gênero", "arv_rg_hiato_comb_serie")
        for sexo, rs in [("Mulher", "Mulheres"), ("Homem", "Homens")]:
            _emit_hs_recorte(f, hia, "sexo", rs, rs, "Hiato de renda", f"arv_rg_hiato_{rs.lower()}_serie", sexo=sexo)
        _emit_hsnap(f, hia, "sexo", "sexo",
                    [("Homem", "Homens", "h"), ("Mulher", "Mulheres", "m")],
                    "—", "Hiato de renda por gênero", "arv_rg_hiato_snapshot", qq)
        secoes.append({"item": 2, "titulo": "Raça × Gênero", "folhas": f})

    # -------------------------------- 3/4/5. Raça × {Faixa|Geração|Escol}
    e345 = []
    if 3 in itens:
        e345.append((3, "Raça × Faixa Etária", renda, "faixa_etaria",
                     [(fx, f"{fx} anos", _SLUG_FX[fx]) for fx in g.FAIXAS_ETARIAS_ORDEM], "faixa"))
    if 4 in itens:
        e345.append((4, "Raça × Geração", rg, "geracao",
                     [(ge, _ROT_GER[ge], g._slug(_ROT_GER[ge])) for ge in _GER], "geracao"))
    if 5 in itens:
        e345.append((5, "Raça × Escolaridade", rpe, "nivel_instrucao",
                     [(ni, _ROT_NIV[ni], g._slug(_ROT_NIV[ni])) for ni in _NIV], "escol"))
    for item, titulo, df, dim, cats, pref in e345:
        f = []
        cc = cores_de(cats)
        _emit_valor_comb_split(f, df, dim, cats, cc, "—", "Renda média real", f"arv_{pref}_comb_serie")
        for c, rot, slug in cats:
            _fig_serie(_serie_valor(df, {dim: c}), g.CORES_RACA, f"arv_{pref}_{slug}_serie.png")
            f.append(_folha("valor_serie", "—", rot, f"Renda média real por raça — {rot} — Brasil",
                            NOTA_SERIE, f"arv_{pref}_{slug}_serie.png",
                            f"Renda média real por raça — {rot} — série histórica."))
        _emit_hs_comb(f, hia, dim, dim, cats, cc, "—", f"Hiato de renda por {dim.replace('_', ' ')}",
                      f"arv_{pref}_hiato_comb_serie")
        for c, rot, slug in cats:
            _emit_hs_recorte(f, hia, dim, "—", rot, "Hiato de renda",
                             f"arv_{pref}_{slug}_hiato_serie", **{dim: c})
        _emit_hsnap(f, hia, dim, dim, cats, "—", f"Hiato de renda por {dim.replace('_', ' ')}",
                    f"arv_{pref}_hiato_snapshot", qq)
        secoes.append({"item": item, "titulo": titulo, "folhas": f})

    # ---------------------- 6/7/8. Raça × Gênero × {Faixa|Geração|Escol}
    e678 = []
    if 6 in itens:
        e678.append((6, "Raça × Gênero × Faixa Etária", renda, "faixa_etaria",
                     [(fx, f"{fx} anos", _SLUG_FX[fx]) for fx in g.FAIXAS_ETARIAS_ORDEM], "gfx", "sexo|faixa_etaria"))
    if 7 in itens:
        e678.append((7, "Raça × Gênero × Geração", rg, "geracao",
                     [(ge, _ROT_GER[ge], g._slug(_ROT_GER[ge])) for ge in _GER], "gge", "sexo|geracao"))
    if 8 in itens:
        e678.append((8, "Raça × Gênero × Escolaridade", rpe, "nivel_instrucao",
                     [(ni, _ROT_NIV[ni], g._slug(_ROT_NIV[ni])) for ni in _NIV], "ges", "sexo|nivel_instrucao"))
    for item, titulo, df, dim, cats, pref, combo in e678:
        f = []
        cc = cores_de(cats)
        for sexo, rs in [("Mulher", "Mulheres"), ("Homem", "Homens")]:
            _emit_valor_comb_split(f, df, dim, cats, cc, rs, "Renda média real",
                                   f"arv_{pref}_{rs.lower()}_comb_serie", sexo=sexo)
            for c, rot, slug in cats:
                _fig_serie(_serie_valor(df, {dim: c}, sexo=sexo), g.CORES_RACA,
                           f"arv_{pref}_{rs.lower()}_{slug}_serie.png")
                f.append(_folha("valor_serie", rs, f"{rs} · {rot}",
                                f"Renda média real por raça — {rs}, {rot} — Brasil",
                                NOTA_SERIE, f"arv_{pref}_{rs.lower()}_{slug}_serie.png",
                                f"Renda média real por raça — {rs}, {rot} — série histórica."))
            _emit_hs_comb(f, hia, combo, dim, cats, cc, rs, f"Hiato por {dim.replace('_', ' ')} — {rs}",
                          f"arv_{pref}_{rs.lower()}_hiato_comb_serie", sexo=sexo)
            for c, rot, slug in cats:
                _emit_hs_recorte(f, hia, combo, rs, f"{rs} · {rot}", "Hiato de renda",
                                 f"arv_{pref}_{rs.lower()}_{slug}_hiato_serie", sexo=sexo, **{dim: c})
            _emit_hsnap(f, hia, combo, dim, cats, rs, f"Hiato por {dim.replace('_', ' ')} — {rs}",
                        f"arv_{pref}_{rs.lower()}_hiato_snapshot", qq, sexo=sexo)
        secoes.append({"item": item, "titulo": titulo, "folhas": f})

    # ------------- 9/10. Raça × Gênero × {Faixa|Geração} × Escolaridade
    e910 = []
    if 9 in itens:
        e910.append((9, "Raça × Gênero × Faixa Etária × Escolaridade", rc, "faixa_etaria",
                     [(fx, f"{fx} anos", _SLUG_FX[fx]) for fx in g.FAIXAS_ETARIAS_ORDEM],
                     "gfe", "sexo|faixa_etaria|nivel_instrucao"))
    if 10 in itens:
        e910.append((10, "Raça × Gênero × Geração × Escolaridade", rcg, "geracao",
                     [(ge, _ROT_GER[ge], g._slug(_ROT_GER[ge])) for ge in _GER],
                     "gge2", "sexo|geracao|nivel_instrucao"))
    for item, titulo, df, dim2, cats2, pref, combo in e910:
        f = []
        for sexo, rs in [("Mulher", "Mulheres"), ("Homem", "Homens")]:
            for c, rot2, slug2 in cats2:
                for ni in _NIV:
                    rotn = _ROT_NIV[ni]
                    sl = f"{pref}_{rs.lower()}_{slug2}_{g._slug(rotn)}"
                    _fig_serie(_serie_valor(df, {dim2: c, "nivel_instrucao": ni}, sexo=sexo),
                               g.CORES_RACA, f"arv_{sl}_serie.png")
                    f.append(_folha("valor_serie", f"{rs} · {rot2}", f"{rs} · {rot2} · {rotn}",
                                    f"Renda média real por raça — {rs}, {rot2}, {rotn} — Brasil",
                                    NOTA_SERIE, f"arv_{sl}_serie.png",
                                    f"Renda média real por raça — {rs}, {rot2}, {rotn} — série histórica."))
                    piv = _hiato_serie_1(hia, combo, "Negra", suavizar=False,
                                         sexo=sexo, **{dim2: c, "nivel_instrucao": ni})
                    _fig_serie(piv, {"Branca vs. Negra": g.COR_NEGRA}, f"arv_{sl}_hiato_serie.png",
                               pct=True, cruza_zero=True)
                    f.append(_folha("hiato_serie", f"{rs} · {rot2}", f"{rs} · {rot2} · {rotn} · hiato",
                                    f"Hiato de renda — {rs}, {rot2}, {rotn} — Branca vs. Negra — Brasil",
                                    SUB_HS + " · (Indígena por célula sem amostra — ver heatmaps do item)",
                                    f"arv_{sl}_hiato_serie.png",
                                    f"Hiato Branca vs. Negra — {rs}, {rot2}, {rotn} — 2012–2026 (Welch)."))
        for sexo, rs in [("Mulher", "Mulheres"), ("Homem", "Homens")]:
            for cmp_, slc, _cor in CMP:
                sub = _hia_filtra(hia, combo, comparacao=cmp_, sexo=sexo)
                if not sub.empty:
                    sub = sub[(sub["ano"] == sub["ano"].max())]
                    sub = sub[sub["trimestre"] == sub["trimestre"].max()]
                _fig_hiato_heatmap(sub, dim2, "nivel_instrucao", f"arv_{pref}_{rs.lower()}_hiato_{slc}.png")
                f.append(_folha("hiato_snapshot", rs,
                                f"{rs} · hiato vs. {cmp_} · {dim2.replace('_', ' ')} × escolaridade",
                                f"Hiato Branca vs. {cmp_} — {rs}: {dim2.replace('_', ' ')} × escolaridade — Brasil",
                                f"{SUB_HSNAP} · {qq} · só {rs.lower()}",
                                f"arv_{pref}_{rs.lower()}_hiato_{slc}.png",
                                f"Hiato Branca vs. {cmp_} por {dim2.replace('_', ' ')} e escolaridade, só {rs.lower()} — {qq}."))
        secoes.append({"item": item, "titulo": titulo, "folhas": f})

    # ------- 11. Raça × Geração × Escolaridade (AMBOS os gêneros) ---------
    # Fecha a única combinação que faltava pra um dashboard geração×escolaridade×
    # gênero: gênero = "ambos" com geração E escolaridade específicas ao mesmo tempo
    # (itens 9-10 só têm as células quebradas por gênero). Mesma lógica do item 10,
    # sem a dimensão de gênero.
    if 11 in itens:
        f = []
        combo = "geracao|nivel_instrucao"
        for ge in _GER:
            rotg = _ROT_GER[ge]
            for ni in _NIV:
                rotn = _ROT_NIV[ni]
                sl = f"ge_{g._slug(rotg)}_{g._slug(rotn)}"
                _fig_serie(_serie_valor(rcg, {"geracao": ge, "nivel_instrucao": ni}),
                           g.CORES_RACA, f"arv_{sl}_serie.png")
                f.append(_folha("valor_serie", "—", f"{rotg} · {rotn}",
                                _tit("Renda média real por raça", rotg, rotn, "ambos os gêneros — Brasil"),
                                NOTA_SERIE, f"arv_{sl}_serie.png",
                                f"Renda média real por raça — {rotg}, {rotn}, ambos os gêneros — série histórica."))
                piv = _hiato_serie_1(hia, combo, "Negra", suavizar=False, geracao=ge, nivel_instrucao=ni)
                _fig_serie(piv, {"Branca vs. Negra": g.COR_NEGRA}, f"arv_{sl}_hiato_serie.png",
                           pct=True, cruza_zero=True)
                f.append(_folha("hiato_serie", "—", f"{rotg} · {rotn} · hiato",
                                _tit("Hiato de renda", rotg, rotn, "Branca vs. Negra — Brasil"),
                                SUB_HS + " · ambos os gêneros · (Indígena por célula: ver heatmaps do item)",
                                f"arv_{sl}_hiato_serie.png",
                                f"Hiato Branca vs. Negra — {rotg}, {rotn}, ambos os gêneros — 2012–2026 (Welch)."))
        for cmp_, slc, _cor in CMP:
            sub = _hia_filtra(hia, combo, comparacao=cmp_)
            if not sub.empty:
                sub = sub[sub["ano"] == sub["ano"].max()]
                sub = sub[sub["trimestre"] == sub["trimestre"].max()]
            _fig_hiato_heatmap(sub, "geracao", "nivel_instrucao", f"arv_ge_hiato_{slc}.png")
            f.append(_folha("hiato_snapshot", "—", f"hiato vs. {cmp_} · geração × escolaridade",
                            f"Hiato Branca vs. {cmp_} — geração × escolaridade (ambos os gêneros) — Brasil",
                            f"{SUB_HSNAP} · {qq}", f"arv_ge_hiato_{slc}.png",
                            f"Hiato Branca vs. {cmp_} por geração e escolaridade, ambos os gêneros — {qq}."))
        secoes.append({"item": 11, "titulo": "Raça × Geração × Escolaridade (ambos os gêneros)", "folhas": f})

    return secoes


def _carregar():
    return {
        "renda": pd.read_parquet(PROCESSED / "renda.parquet"),
        "renda_por_escolaridade": pd.read_parquet(PROCESSED / "renda_por_escolaridade.parquet"),
        "renda_por_geracao": pd.read_parquet(PROCESSED / "renda_por_geracao.parquet"),
        "renda_completa": pd.read_parquet(PROCESSED / "renda_completa.parquet"),
        "renda_completa_geracao": pd.read_parquet(PROCESSED / "renda_completa_geracao.parquet"),
        "hiato_arvore": pd.read_parquet(PROCESSED / "hiato_arvore.parquet"),
    }


def main():
    itens = {int(a) for a in sys.argv[1:]} or set(range(1, 12))
    dados = _carregar()
    secoes = construir(itens, dados)
    manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8")) if MANIFESTO.exists() else {}
    manifesto.setdefault("_meta", {})["fonte"] = FONTE
    ex = {s["item"]: s for s in manifesto.get("arvore", [])}
    ex.update({s["item"]: s for s in secoes})
    manifesto["arvore"] = [ex[k] for k in sorted(ex, key=lambda x: (isinstance(x, str), x))]
    MANIFESTO.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
    for s in secoes:
        print(f"  item {s['item']:>2} · {s['titulo']:<44} · {len(s['folhas'])} folhas")
    print(f"Total desta rodada: {sum(len(s['folhas']) for s in secoes)} folhas.")


if __name__ == "__main__":
    main()
