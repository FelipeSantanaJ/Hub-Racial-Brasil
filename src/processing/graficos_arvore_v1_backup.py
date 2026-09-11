"""Reconstrução do deck — ÁRVORE cruzada de renda por raça (itens 1-10).

Contexto (2026-09-06): o deck antigo (507 slides) repetia a mesma imagem em vários
lugares porque a seção "Renda média" quebrava cada dimensão ISOLADAMENTE e
reaproveitava as séries por-categoria em toda subseção que tocava aquela dimensão
(434 slides de gráfico / 134 imagens). A estrutura nova é uma ÁRVORE de verdade,
quebra CRUZADA (Mulheres × 14-17 é um gráfico próprio, diferente de Mulheres
sozinho ou de 14-17 sozinho). Regra de ouro: cada PNG aparece em 1 slide só.

Decisões do usuário (ver docs/PLANO.md, seção "Reconstrução do deck"):
- Itens 9-10: gerar TODAS as 126 folhas-célula (70 + 56).
- Cada folha "Valores" = 2 imagens irmãs: série histórica (linha) + snapshot
  (barra). As "Combinado" dos itens 3-5 são só snapshot.
- Cada folha "Hiato" = barra (1 dim) ou heatmap (2 dims) do hiato Branca vs. Negra,
  só trimestre recente, com Welch. Nos itens 6-10 é fatiado por gênero.
- Raças nos "Valores": Branca / Negra (Preta+Parda, média ponderada por
  populacao_estimada) / Indígena — Indígena nunca descartado (cai como barra
  vazada "amostra insuficiente" quando o corte fica sem amostra).
- Família Preta vs. Parda: FORA do deck novo.
- **Texto fora da imagem**: as figuras aqui são "cruas" — só dados, eixos, grade,
  rótulos de eixo, rótulos de valor e legenda de séries. Título, subtítulo, linha
  de fonte e legenda do slide são caixas de texto no PPT (ver
  `apresentacao_arvore.py`), preenchidas a partir dos campos `titulo`/`subtitulo`/
  `legenda` que este módulo grava em `docs/arvore_manifest.json`.

Nenhuma agregação nova é necessária para a árvore: os 5 parquets-base já cobrem
tudo, e os hiatos multidimensionais já têm a coluna `sexo` (é só fatiar).

Uso:
    python -m src.processing.graficos_arvore            # tudo (itens 1-10)
    python -m src.processing.graficos_arvore 1 2 3      # só alguns itens
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
ORDEM_RACAS = ["Branca", "Negra", "Indígena"]
RACAS_VALOR = ["Branca", "Negra", "Indígena"]
NOTA_SERIE = "R$ reais, a preços do trimestre mais recente (deflator IBGE) · série 2012–2026"
SUB_HIATO = ("% de diferença de renda, Branca vs. Negra · teste de Welch: "
             "*** p<0,001  ** p<0,01  * p<0,05  ·  n.s. = não significativo")


# ======================================================================= #
# Renderizadores "crus" — sem título/subtítulo/rodapé (isso vira texto no PPT)
# ======================================================================= #
def _salvar_bare(fig, nome_arquivo: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destino = OUTPUT_DIR / nome_arquivo
    fig.savefig(destino, facecolor=g.SUPERFICIE, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return destino


def _placeholder(nome_arquivo: str, msg: str = "Amostra insuficiente para este corte") -> Path:
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    ax.set_facecolor(g.SUPERFICIE)
    ax.axis("off")
    ax.text(0.5, 0.5, msg, ha="center", va="center", fontsize=13, color=g.TINTA_MUTED)
    return _salvar_bare(fig, nome_arquivo)


def _fig_serie(serie: pd.DataFrame, cores: dict, nome_arquivo: str,
               rotulos: dict | None = None, pct: bool = False) -> Path:
    serie = serie.dropna(how="all")
    if serie.empty or not np.isfinite(serie.to_numpy(dtype=float)).any():
        return _placeholder(nome_arquivo)
    rotulos = rotulos or {c: c for c in serie.columns}
    fig, ax = plt.subplots(figsize=(11, 4.7), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    ax.set_facecolor(g.SUPERFICIE)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(g.EIXO)
    ax.tick_params(axis="both", colors=g.TINTA_MUTED, labelsize=9.5, length=0)
    ax.axvspan(pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"), color=g.GRADE, alpha=0.6, zorder=0)

    vmax = np.nanmax(serie.to_numpy(dtype=float))
    vmin = np.nanmin(serie.to_numpy(dtype=float))
    topo = vmax * 1.20
    base = vmin * 0.9 if vmin > 0 else vmin * 1.1
    if pct:
        topo = min(topo, 100) if vmax <= 100 else topo
    if topo <= base:
        topo = base + 1
    ax.set_ylim(base, topo)

    for coluna in serie.columns:
        ax.plot(serie.index, serie[coluna], color=cores.get(coluna, g.TINTA_MUTED),
                linewidth=2, solid_capstyle="round", zorder=3)

    ultimo_x = serie.index[-1]
    finais = sorted((serie[c].iloc[-1], rotulos[c], cores.get(c, g.TINTA_MUTED))
                    for c in serie.columns if pd.notna(serie[c].iloc[-1]))
    espaco = (topo - base) * 0.06
    for i in range(1, len(finais)):
        if finais[i][0] - finais[i - 1][0] < espaco:
            finais[i] = (finais[i - 1][0] + espaco, *finais[i][1:])
    for y, rot, cor in finais:
        ax.annotate(rot, xy=(ultimo_x, y), xytext=(8, 0), textcoords="offset points",
                    color=cor, fontsize=9.5, fontweight="bold", va="center")

    ax.yaxis.set_major_formatter((lambda v, _: f"{v:.0f}%") if pct
                                 else (lambda v, _: f"R$ {v:,.0f}".replace(",", ".")))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
    ax.set_xlim(serie.index.min(), serie.index.max() + pd.Timedelta(days=300))
    fig.tight_layout()
    return _salvar_bare(fig, nome_arquivo)


def _fig_snapshot(valores: dict, nome_arquivo: str) -> Path:
    if not any(pd.notna(valores.get(r, np.nan)) for r in ORDEM_RACAS):
        return _placeholder(nome_arquivo)
    fig, ax = plt.subplots(figsize=(7.6, 4.7), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    ax.set_facecolor(g.SUPERFICIE)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(g.EIXO)
    ax.tick_params(axis="both", colors=g.TINTA_MUTED, labelsize=10, length=0)

    x = np.arange(len(ORDEM_RACAS))
    alturas = [valores.get(r, np.nan) for r in ORDEM_RACAS]
    validos = [a for a in alturas if pd.notna(a)]
    for xi, raca, altura in zip(x, ORDEM_RACAS, alturas):
        if pd.isna(altura):
            ax.bar(xi, (max(validos) * 0.06 if validos else 1), width=0.6, zorder=3,
                   color="none", edgecolor=g.EIXO, hatch="//")
            ax.text(xi, 0, "amostra\ninsuficiente", ha="center", va="bottom",
                    fontsize=8.5, color=g.TINTA_MUTED)
        else:
            ax.bar(xi, altura, width=0.6, color=g.CORES_RACA[raca], zorder=3)
            ax.text(xi, altura, f"R$ {altura:,.0f}".replace(",", "."), ha="center", va="bottom",
                    fontsize=10.5, fontweight="bold", color=g.TINTA_PRIMARIA)

    ax.set_xticks(x)
    ax.set_xticklabels(ORDEM_RACAS, fontsize=11)
    ax.set_ylim(0, (max(validos) * 1.22) if validos else 1)
    ax.yaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
    fig.tight_layout()
    return _salvar_bare(fig, nome_arquivo)


def _fig_snapshot_agrupado_sexo(df_recente: pd.DataFrame, nome_arquivo: str) -> Path:
    """Barras agrupadas: x = raça, 2 barras por raça (Homens hachurado / Mulheres
    sólido), mesma cor de raça. Legenda em cinza pra não competir com a cor."""
    from matplotlib.patches import Patch
    x = np.arange(len(ORDEM_RACAS))
    largura = 0.38
    fig, ax = plt.subplots(figsize=(9, 4.7), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    ax.set_facecolor(g.SUPERFICIE)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(g.EIXO)
    ax.tick_params(axis="both", colors=g.TINTA_MUTED, labelsize=10, length=0)

    for i, sexo in enumerate(["Homem", "Mulher"]):
        rs = df_recente[df_recente["sexo"] == sexo]
        vals = [
            _wmean(rs[rs["raca_cor"] == "Branca"]),
            _wmean(rs[rs["raca_cor"].isin(["Preta", "Parda"])]),
            _wmean(rs[rs["raca_cor"] == "Indígena"]),
        ]
        desloc = (i - 0.5) * largura
        ax.bar(x + desloc, [v if pd.notna(v) else 0 for v in vals], largura, zorder=3,
               color=[g.CORES_RACA[r] for r in ORDEM_RACAS],
               hatch="//" if sexo == "Homem" else None, edgecolor=g.SUPERFICIE, linewidth=0.4)
        for xi, v in zip(x + desloc, vals):
            if pd.notna(v):
                ax.text(xi, v, f"R$ {v:,.0f}".replace(",", "."), ha="center", va="bottom",
                        fontsize=8, color=g.TINTA_SECUNDARIA)

    ax.set_xticks(x)
    ax.set_xticklabels(ORDEM_RACAS, fontsize=11)
    ax.yaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
    ax.legend(handles=[Patch(facecolor=g.TINTA_MUTED, hatch="//", label="Homens"),
                       Patch(facecolor=g.TINTA_MUTED, label="Mulheres")],
              loc="upper right", frameon=False, fontsize=9.5)
    fig.tight_layout()
    return _salvar_bare(fig, nome_arquivo)


def _fig_hiato_bar(dados: pd.DataFrame, dim: str, nome_arquivo: str) -> Path:
    meta = g.METADADOS_DIM_HIATO[dim]
    ordem, rotulos = meta["ordem"], meta["rotulos"]
    d = dados[dados[dim].isin(ordem)].set_index(dim).reindex(ordem).reset_index()
    if d["hiato_percentual"].isna().all():
        return _placeholder(nome_arquivo)
    fig, ax = plt.subplots(figsize=(max(8, 1.15 * len(ordem) + 3), 4.6), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    ax.set_facecolor(g.SUPERFICIE)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(g.EIXO)
    ax.tick_params(axis="both", colors=g.TINTA_MUTED, labelsize=10, length=0)

    x = np.arange(len(ordem))
    valores = d["hiato_percentual"]
    ax.bar(x, valores.fillna(0), width=0.55, color=g.COR_BRANCA, zorder=3)
    minv, maxv = min(0, valores.min()), max(0, valores.max())
    margem = (maxv - minv) * 0.20 or 1
    ax.set_ylim(minv - margem * (1.1 if minv < 0 else 0), maxv + margem)
    for i, (v, p) in enumerate(zip(valores, d["p_valor"])):
        if pd.isna(v):
            continue
        marca = g._marca_significancia(p)
        desloc = margem * 0.12 if v >= 0 else -margem * 0.22
        ax.text(x[i], v + desloc, f"{v:.0f}%\n{marca}", ha="center",
                va="bottom" if v >= 0 else "top", fontsize=9.5, fontweight="bold",
                color=g.TINTA_PRIMARIA)
    ax.axhline(0, color=g.EIXO, linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels([rotulos.get(c, c) for c in ordem], fontsize=10)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
    fig.tight_layout()
    return _salvar_bare(fig, nome_arquivo)


def _fig_hiato_heatmap(dados: pd.DataFrame, dim_linha: str, dim_coluna: str, nome_arquivo: str) -> Path:
    meta_l, meta_c = g.METADADOS_DIM_HIATO[dim_linha], g.METADADOS_DIM_HIATO[dim_coluna]
    ol, oc = meta_l["ordem"], meta_c["ordem"]
    rl, rc = meta_l["rotulos"], meta_c["rotulos"]
    d = dados[dados[dim_linha].isin(ol) & dados[dim_coluna].isin(oc)]
    matriz = d.pivot_table(index=dim_linha, columns=dim_coluna, values="hiato_percentual").reindex(index=ol, columns=oc)
    matriz_p = d.pivot_table(index=dim_linha, columns=dim_coluna, values="p_valor").reindex(index=ol, columns=oc)
    validos = matriz.to_numpy(dtype=float)
    validos = validos[np.isfinite(validos)]
    if not len(validos):
        return _placeholder(nome_arquivo)
    limite = np.abs(validos).max() or 1

    fig, ax = plt.subplots(figsize=(1.15 * len(oc) + 3.5, 0.7 * len(ol) + 2.6), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    ax.set_facecolor(g.SUPERFICIE)
    im = ax.imshow(matriz.to_numpy(dtype=float), cmap=g.CMAP_DIVERGENTE_HIATO,
                   vmin=-limite, vmax=limite, aspect="auto")
    ax.set_xticks(range(len(oc)))
    ax.set_xticklabels([rc.get(c, c) for c in oc], fontsize=8.5, color=g.TINTA_MUTED, rotation=35, ha="right")
    ax.set_yticks(range(len(ol)))
    ax.set_yticklabels([rl.get(r, r) for r in ol], fontsize=8.5, color=g.TINTA_MUTED)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    for yi in range(matriz.shape[0]):
        for xi in range(matriz.shape[1]):
            v = matriz.to_numpy(dtype=float)[yi, xi]
            if pd.notna(v):
                marca = g._marca_significancia(matriz_p.to_numpy(dtype=float)[yi, xi])
                cor = g.TINTA_PRIMARIA if abs(v) < limite * 0.55 else g.SUPERFICIE
                ax.text(xi, yi, f"{v:.0f}%\n{marca}", ha="center", va="center", fontsize=7.5, color=cor)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03).ax.tick_params(labelsize=8, colors=g.TINTA_MUTED)
    fig.tight_layout()
    return _salvar_bare(fig, nome_arquivo)


# ======================================================================= #
# Dados
# ======================================================================= #
def _wmean(sub: pd.DataFrame, col: str = "renda_habitual_real_media") -> float:
    if sub.empty:
        return np.nan
    w = sub["populacao_estimada"]
    tot = w.sum()
    return float((sub[col] * w).sum() / tot) if tot else np.nan


def _recorte_recente(df: pd.DataFrame, filtro: dict | None = None) -> pd.DataFrame:
    ano, tri = g._trimestre_mais_recente(df)
    r = df[df["nivel_geografico"] == "brasil"] if "nivel_geografico" in df.columns else df
    r = r[(r["ano"] == ano) & (r["trimestre"] == tri)].copy()
    for col, val in (filtro or {}).items():
        r = r[r[col] == val]
    return r


def _valores_por_raca(df: pd.DataFrame, filtro: dict | None = None) -> dict[str, float]:
    r = _recorte_recente(df, filtro)
    return {
        "Branca": _wmean(r[r["raca_cor"] == "Branca"]),
        "Negra": _wmean(r[r["raca_cor"].isin(["Preta", "Parda"])]),
        "Indígena": _wmean(r[r["raca_cor"] == "Indígena"]),
    }


def _serie(df: pd.DataFrame, filtro: dict | None = None, sexo: str | None = None) -> pd.DataFrame:
    return g._serie_por_raca(df, RACAS_VALOR, filtro_extra=filtro, sexo=sexo, suavizar={"Indígena"})


def _sub_snapshot(valores: dict, qq: str) -> str:
    b, n = valores.get("Branca"), valores.get("Negra")
    if b and n and pd.notna(b) and pd.notna(n):
        return (f"R$ reais · {qq} · hiato Branca vs. Negra: R$ {b - n:,.0f}".replace(",", ".")
                + f" ({100 * (b - n) / n:.0f}%)")
    return f"R$ reais · {qq}"


# ======================================================================= #
# Construção da árvore
# ======================================================================= #
_SLUG_FAIXA = {f: f.replace("+", "mais").replace("-", "_") for f in g.FAIXAS_ETARIAS_ORDEM}
_GERACOES = g.GERACOES_ORDEM_GRAFICO
_ROT_GER = g.ROTULOS_GERACAO_CURTO
_NIVEIS = g.NIVEIS_INSTRUCAO_ORDEM
_ROT_NIV = g.NIVEIS_INSTRUCAO_ROTULO_CURTO


def _folha(tipo, ramo, sub, titulo, subtitulo, arquivo, legenda) -> dict:
    return {"tipo": tipo, "ramo": ramo, "sub": sub, "titulo": titulo,
            "subtitulo": subtitulo, "arquivo": arquivo, "legenda": legenda}


def _leaf_valor(df, filtro, sexo, ramo, sub, titulo_base, slug, qq, *, com_serie=True):
    """Gera as 1-2 imagens irmãs de uma folha "Valores" e devolve as folhas do manifesto."""
    folhas = []
    valores = _valores_por_raca(df, {**(filtro or {}), **({"sexo": sexo} if sexo else {})})
    if com_serie:
        arq_s = f"arv_{slug}_serie.png"
        _fig_serie(_serie(df, filtro, sexo), g.CORES_RACA, arq_s)
        folhas.append(_folha("valor_serie", ramo, sub, titulo_base,
                             NOTA_SERIE, arq_s,
                             f"Renda média real por raça — {sub} — série histórica."))
    arq_n = f"arv_{slug}_snapshot.png"
    _fig_snapshot(valores, arq_n)
    folhas.append(_folha("valor_snapshot", ramo, sub, titulo_base,
                         _sub_snapshot(valores, qq), arq_n,
                         f"Renda média real por raça — {sub} — {qq}."))
    return folhas


def construir(itens: set[int], dados: dict) -> list[dict]:
    renda, rpe, rg = dados["renda"], dados["renda_por_escolaridade"], dados["renda_por_geracao"]
    rc, rcg, hr = dados["renda_completa"], dados["renda_completa_geracao"], dados["hiato_racial"]
    hg = dados["hiatos"]  # dict {nome: df}
    ano, tri = g._trimestre_mais_recente(renda)
    qq = f"{tri}º tri. {ano}"
    secoes: list[dict] = []

    # ---- 1. Raça -------------------------------------------------------- #
    if 1 in itens:
        f = []
        _fig_serie(_serie(renda), g.CORES_RACA, "arv_raca_serie.png")
        f.append(_folha("valor_serie", "—", "Raça", "Renda média real por raça — Brasil",
                        NOTA_SERIE, "arv_raca_serie.png", "Renda média real por raça — série histórica."))
        v = _valores_por_raca(renda)
        _fig_snapshot(v, "arv_raca_snapshot.png")
        f.append(_folha("valor_snapshot", "—", "Raça", "Renda média real por raça — Brasil",
                        _sub_snapshot(v, qq), "arv_raca_snapshot.png", f"Renda média real por raça — {qq}."))
        linha = hr.sort_values(["ano", "trimestre"]).iloc[-1]
        _fig_snapshot({"Branca": float(linha["renda_media_branca"]), "Negra": float(linha["renda_media_negra"]),
                       "Indígena": np.nan}, "arv_raca_hiato.png")
        f.append(_folha("hiato", "—", "Hiato Branca vs. Negra", "Hiato de renda Branca vs. Negra — Brasil",
                        f"{SUB_HIATO} · {qq} · Welch {g._marca_significancia(float(linha['p_valor']))} "
                        f"→ R$ {linha['hiato_absoluto']:,.0f}".replace(",", ".")
                        + f" ({linha['hiato_percentual']:.0f}%)",
                        "arv_raca_hiato.png", "Renda média Branca e Negra (microdados) e o hiato entre elas."))
        secoes.append({"item": 1, "titulo": "Raça", "folhas": f})

    # ---- 2. Raça × Gênero -------------------------------------------- #
    if 2 in itens:
        f = []
        _fig_serie(g._serie_por_raca(renda, RACAS_VALOR, suavizar={"Indígena"}), g.CORES_RACA, "arv_rg_comb_serie.png")
        # série combinada raça×gênero: reaproveita a lógica multi-linha só quando faz sentido;
        # aqui a folha "Combinado" traz a série por raça (sem gênero) + o snapshot agrupado.
        f.append(_folha("valor_serie", "Combinado", "Combinado", "Renda média real por raça e gênero — Brasil",
                        NOTA_SERIE, "arv_rg_comb_serie.png",
                        "Renda média real por raça — série histórica (gênero no snapshot ao lado)."))
        _fig_snapshot_agrupado_sexo(_recorte_recente(renda), "arv_rg_comb_snapshot.png")
        f.append(_folha("valor_snapshot", "Combinado", "Combinado", "Renda média real por raça e gênero — Brasil",
                        f"R$ reais · {qq} · barra hachurada = Homens, sólida = Mulheres",
                        "arv_rg_comb_snapshot.png", f"Renda média real por raça e gênero — {qq}."))
        for sexo, rot in [("Mulher", "Mulheres"), ("Homem", "Homens")]:
            f += _leaf_valor(renda, None, sexo, rot, rot,
                             f"Renda média real por raça — {rot} — Brasil",
                             f"rg_{rot.lower()}", qq)
        _fig_hiato_bar(hg["hiato_genero_todas"], "sexo", "arv_rg_hiato.png")
        f.append(_folha("hiato", "—", "Hiato por gênero", "Hiato Branca vs. Negra, por gênero — Brasil",
                        f"{SUB_HIATO} · {qq}", "arv_rg_hiato.png",
                        "Hiato Branca vs. Negra dentro de cada gênero — snapshot, Welch."))
        secoes.append({"item": 2, "titulo": "Raça × Gênero", "folhas": f})

    # ---- 3-5. Raça × {Faixa | Geração | Escolaridade} ------------- #
    especs = []
    if 3 in itens:
        especs.append((3, "Raça × Faixa Etária", renda, "faixa_etaria",
                       [(fx, fx + " anos", _SLUG_FAIXA[fx]) for fx in g.FAIXAS_ETARIAS_ORDEM],
                       "hiato_faixa_etaria_todas"))
    if 4 in itens:
        especs.append((4, "Raça × Geração", rg, "geracao",
                       [(ge, _ROT_GER[ge], g._slug(_ROT_GER[ge])) for ge in _GERACOES],
                       "hiato_geracao_todas"))
    if 5 in itens:
        especs.append((5, "Raça × Escolaridade", rpe, "nivel_instrucao",
                       [(ni, _ROT_NIV[ni], g._slug(_ROT_NIV[ni])) for ni in _NIVEIS],
                       "hiato_escolaridade_todas"))
    for item, titulo, df, dim, cats, hiato_key in especs:
        pref = {3: "faixa", 4: "geracao", 5: "escol"}[item]
        f = []
        vcomb = _combinar_snapshot_dim(df, dim, cats)
        _fig_snapshot_dim(vcomb, cats, f"arv_{pref}_comb_snapshot.png")
        f.append(_folha("valor_snapshot", "Combinado", "Combinado",
                        f"{titulo} — Brasil", f"R$ reais · {qq} · média por raça em cada categoria",
                        f"arv_{pref}_comb_snapshot.png",
                        f"Renda média real por raça e {dim.replace('_', ' ')} — {qq}."))
        for cat, rot, slug in cats:
            f += _leaf_valor(df, {dim: cat}, None, "—", rot,
                             f"Renda média real por raça — {rot} — Brasil", f"{pref}_{slug}", qq)
        _fig_hiato_bar(hg[hiato_key], dim, f"arv_{pref}_hiato.png")
        f.append(_folha("hiato", "—", f"Hiato por {dim.replace('_', ' ')}",
                        f"Hiato Branca vs. Negra, por {dim.replace('_', ' ')} — Brasil",
                        f"{SUB_HIATO} · {qq}", f"arv_{pref}_hiato.png",
                        f"Hiato Branca vs. Negra por {dim.replace('_', ' ')} — snapshot, Welch."))
        secoes.append({"item": item, "titulo": titulo, "folhas": f})

    # ---- 6-8. Raça × Gênero × {Faixa | Geração | Escolaridade} --- #
    especs68 = []
    if 6 in itens:
        especs68.append((6, "Raça × Gênero × Faixa Etária", renda, "faixa_etaria",
                         [(fx, fx + " anos", _SLUG_FAIXA[fx]) for fx in g.FAIXAS_ETARIAS_ORDEM],
                         "hiato_genero_faixa_etaria_todas", "faixa"))
    if 7 in itens:
        especs68.append((7, "Raça × Gênero × Geração", rg, "geracao",
                         [(ge, _ROT_GER[ge], g._slug(_ROT_GER[ge])) for ge in _GERACOES],
                         "hiato_genero_geracao_todas", "geracao"))
    if 8 in itens:
        especs68.append((8, "Raça × Gênero × Escolaridade", rpe, "nivel_instrucao",
                         [(ni, _ROT_NIV[ni], g._slug(_ROT_NIV[ni])) for ni in _NIVEIS],
                         "hiato_genero_escolaridade_todas", "escol"))
    for item, titulo, df, dim, cats, hiato_key, pref in especs68:
        f = []
        for sexo, rot_sexo in [("Mulher", "Mulheres"), ("Homem", "Homens")]:
            for cat, rot, slug in cats:
                f += _leaf_valor(df, {dim: cat}, sexo, rot_sexo, f"{rot_sexo} · {rot}",
                                 f"Renda média real por raça — {rot_sexo}, {rot} — Brasil",
                                 f"{pref}_{sexo.lower()}_{slug}", qq)
        for sexo, rot_sexo in [("Mulher", "Mulheres"), ("Homem", "Homens")]:
            sub = hg[hiato_key][hg[hiato_key]["sexo"] == sexo]
            _fig_hiato_bar(sub, dim, f"arv_{pref}_hiato_{sexo.lower()}.png")
            f.append(_folha("hiato", rot_sexo, f"{rot_sexo} · hiato por {dim.replace('_', ' ')}",
                            f"Hiato Branca vs. Negra — {rot_sexo}, por {dim.replace('_', ' ')} — Brasil",
                            f"{SUB_HIATO} · {qq} · só {rot_sexo.lower()}",
                            f"arv_{pref}_hiato_{sexo.lower()}.png",
                            f"Hiato Branca vs. Negra por {dim.replace('_', ' ')}, só {rot_sexo.lower()} — Welch."))
        secoes.append({"item": item, "titulo": titulo, "folhas": f})

    # ---- 9-10. Raça × Gênero × {Faixa|Geração} × Escolaridade -- #
    especs910 = []
    if 9 in itens:
        especs910.append((9, "Raça × Gênero × Faixa Etária × Escolaridade", rc, "faixa_etaria",
                          [(fx, fx + " anos", _SLUG_FAIXA[fx]) for fx in g.FAIXAS_ETARIAS_ORDEM],
                          "hiato_genero_faixa_etaria_escolaridade_todas", "gfe"))
    if 10 in itens:
        especs910.append((10, "Raça × Gênero × Geração × Escolaridade", rcg, "geracao",
                          [(ge, _ROT_GER[ge], g._slug(_ROT_GER[ge])) for ge in _GERACOES],
                          "hiato_genero_geracao_escolaridade_todas", "gge"))
    for item, titulo, df, dim2, cats2, hiato_key, pref in especs910:
        f = []
        for sexo, rot_sexo in [("Mulher", "Mulheres"), ("Homem", "Homens")]:
            for cat, rot2, slug2 in cats2:
                for ni in _NIVEIS:
                    rotn = _ROT_NIV[ni]
                    f += _leaf_valor(df, {dim2: cat, "nivel_instrucao": ni}, sexo, rot_sexo,
                                     f"{rot_sexo} · {rot2} · {rotn}",
                                     f"Renda média real por raça — {rot_sexo}, {rot2}, {rotn} — Brasil",
                                     f"{pref}_{sexo.lower()}_{slug2}_{g._slug(rotn)}", qq)
        for sexo, rot_sexo in [("Mulher", "Mulheres"), ("Homem", "Homens")]:
            sub = hg[hiato_key][hg[hiato_key]["sexo"] == sexo]
            _fig_hiato_heatmap(sub, dim2, "nivel_instrucao", f"arv_{pref}_hiato_{sexo.lower()}.png")
            f.append(_folha("hiato", rot_sexo, f"{rot_sexo} · hiato {dim2.replace('_', ' ')} × escolaridade",
                            f"Hiato Branca vs. Negra — {rot_sexo}: {dim2.replace('_', ' ')} × escolaridade — Brasil",
                            f"{SUB_HIATO} · {qq} · só {rot_sexo.lower()}",
                            f"arv_{pref}_hiato_{sexo.lower()}.png",
                            f"Hiato Branca vs. Negra por {dim2.replace('_', ' ')} e escolaridade, só {rot_sexo.lower()} — Welch."))
        secoes.append({"item": item, "titulo": titulo, "folhas": f})

    return secoes


def _combinar_snapshot_dim(df, dim, cats):
    r = _recorte_recente(df)
    out = {}
    for cat, _, _ in cats:
        rc_ = r[r[dim] == cat]
        out[cat] = {
            "Branca": _wmean(rc_[rc_["raca_cor"] == "Branca"]),
            "Negra": _wmean(rc_[rc_["raca_cor"].isin(["Preta", "Parda"])]),
            "Indígena": _wmean(rc_[rc_["raca_cor"] == "Indígena"]),
        }
    return out


def _fig_snapshot_dim(valores_por_cat: dict, cats, nome_arquivo: str) -> Path:
    """Barras agrupadas: x = categoria da dimensão, 3 barras (B/N/I) por categoria."""
    rotulos = [rot for _, rot, _ in cats]
    chaves = [c for c, _, _ in cats]
    x = np.arange(len(chaves))
    largura = 0.26
    fig, ax = plt.subplots(figsize=(max(8, 1.5 * len(chaves) + 2), 4.7), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    ax.set_facecolor(g.SUPERFICIE)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(g.EIXO)
    ax.tick_params(axis="both", colors=g.TINTA_MUTED, labelsize=9.5, length=0)
    for i, raca in enumerate(ORDEM_RACAS):
        vals = [valores_por_cat[c].get(raca, np.nan) for c in chaves]
        ax.bar(x + (i - 1) * largura, [v if pd.notna(v) else 0 for v in vals], largura,
               color=g.CORES_RACA[raca], zorder=3, label=raca)
    ax.set_xticks(x)
    ax.set_xticklabels(rotulos, fontsize=9.5, rotation=20 if len(chaves) > 4 else 0, ha="right" if len(chaves) > 4 else "center")
    ax.yaxis.set_major_formatter(lambda v, _: f"R$ {v:,.0f}".replace(",", "."))
    ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    fig.tight_layout()
    return _salvar_bare(fig, nome_arquivo)


# ======================================================================= #
def _carregar() -> dict:
    nomes_hiato = [
        "hiato_genero_todas", "hiato_faixa_etaria_todas", "hiato_geracao_todas",
        "hiato_escolaridade_todas", "hiato_genero_faixa_etaria_todas",
        "hiato_genero_geracao_todas", "hiato_genero_escolaridade_todas",
        "hiato_genero_faixa_etaria_escolaridade_todas", "hiato_genero_geracao_escolaridade_todas",
    ]
    return {
        "renda": pd.read_parquet(PROCESSED / "renda.parquet"),
        "renda_por_escolaridade": pd.read_parquet(PROCESSED / "renda_por_escolaridade.parquet"),
        "renda_por_geracao": pd.read_parquet(PROCESSED / "renda_por_geracao.parquet"),
        "renda_completa": pd.read_parquet(PROCESSED / "renda_completa.parquet"),
        "renda_completa_geracao": pd.read_parquet(PROCESSED / "renda_completa_geracao.parquet"),
        "hiato_racial": pd.read_parquet(PROCESSED / "hiato_racial.parquet"),
        "hiatos": {n: pd.read_parquet(PROCESSED / f"{n}.parquet") for n in nomes_hiato},
    }


def main() -> None:
    itens = {int(a) for a in sys.argv[1:]} or set(range(1, 11))
    dados = _carregar()
    secoes = construir(itens, dados)

    manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8")) if MANIFESTO.exists() else {}
    manifesto.setdefault("_meta", {})["fonte"] = FONTE
    por_item = {s["item"]: s for s in secoes}
    existentes = {s["item"]: s for s in manifesto.get("arvore", [])}
    existentes.update(por_item)
    manifesto["arvore"] = [existentes[k] for k in sorted(existentes)]
    MANIFESTO.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")

    n_img = sum(len(s["folhas"]) for s in secoes)
    print(f"Itens gerados: {sorted(itens)}")
    for s in secoes:
        print(f"  item {s['item']:>2} · {s['titulo']:<42} · {len(s['folhas'])} folhas")
    print(f"Total desta rodada: {n_img} folhas / imagens.")
    print(f"Manifesto: {MANIFESTO.relative_to(REPO_ROOT)} (chave 'arvore', {len(manifesto['arvore'])} itens)")


if __name__ == "__main__":
    main()
