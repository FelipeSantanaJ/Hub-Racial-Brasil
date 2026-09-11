"""Fase D — gráficos de topo 10% / base 10% / quartis com os LIMIARES NOVOS
(Brasil / dentro de gênero / dentro de raça×gênero), a partir dos parquets de
`agregacoes_pnadc.gerar_extremos_racial` e `gerar_quartis_multi_racial`.

Figuras "cruas" (sem título/subtítulo/rodapé — isso vira caixa de texto no PPT),
mesma convenção de `graficos_arvore.py`. Grava a seção `extremos` em
`docs/arvore_manifest.json`.

Uso:
    python -m src.processing.graficos_extremos
"""
from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from src.processing import graficos_fase1 as g
from src.processing.graficos_arvore import _salvar_bare, _placeholder, MANIFESTO, PROCESSED, FONTE

Q_ORDEM = ["Q1 (25% que menos ganham)", "Q2", "Q3", "Q4 (25% que mais ganham)"]
Q_CURTO = {"Q1 (25% que menos ganham)": "Q1", "Q2": "Q2", "Q3": "Q3", "Q4 (25% que mais ganham)": "Q4"}
DIM_ORDEM = {
    "nivel_instrucao": g.NIVEIS_INSTRUCAO_ORDEM,
    "faixa_etaria": g.FAIXAS_ETARIAS_ORDEM,
    "geracao": g.GERACOES_ORDEM_GRAFICO,
    "sexo": ["Mulher", "Homem"],
}
DIM_ROT = {
    "nivel_instrucao": g.NIVEIS_INSTRUCAO_ROTULO_CURTO,
    "faixa_etaria": {f: f for f in g.FAIXAS_ETARIAS_ORDEM},
    "geracao": g.ROTULOS_GERACAO_CURTO,
    "sexo": {"Mulher": "Mulher", "Homem": "Homem"},
}
DIM_NOME = {"nivel_instrucao": "escolaridade", "faixa_etaria": "faixa etária",
            "geracao": "geração", "sexo": "gênero"}
CORES_GRUPO = {
    "Branca": g.COR_BRANCA, "Negra": g.COR_NEGRA, "Indígena": g.COR_INDIGENA,
    "Branca · Homem": g.COR_BRANCA, "Branca · Mulher": "#5bbfb5",
    "Negra · Homem": g.COR_NEGRA, "Negra · Mulher": "#e08a5a",
}
HATCH_GRUPO = {"Branca · Homem": "//", "Negra · Homem": "//"}


def _eixo(figsize):
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    ax.set_facecolor(g.SUPERFICIE)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(g.EIXO)
    ax.tick_params(axis="both", colors=g.TINTA_MUTED, labelsize=9.5, length=0)
    return fig, ax


def _fmt_reais(v):
    return f"R$ {v:,.0f}".replace(",", ".")


def _recente(df):
    ano, tri = g._trimestre_mais_recente(df)
    return df[(df["ano"] == ano) & (df["trimestre"] == tri)].copy(), f"{tri}º tri. {ano}"


# --------------------------------------------------------------------------- #
def _fig_barras_grupo(cats, rotulos, series_por_grupo, nome_arquivo, *, pct=True, ndigits=0):
    """Barras agrupadas: x = categoria, uma barra por grupo. `series_por_grupo` =
    dict {grupo: [valores alinhados a cats]}."""
    grupos = list(series_por_grupo)
    x = np.arange(len(cats))
    n = len(grupos)
    largura = min(0.8 / n, 0.28)
    fig, ax = _eixo((max(8, 1.4 * len(cats) + 2), 4.7))
    for i, grp in enumerate(grupos):
        vals = series_por_grupo[grp]
        ax.bar(x + (i - (n - 1) / 2) * largura, [v if pd.notna(v) else 0 for v in vals], largura,
               color=CORES_GRUPO.get(grp, g.TINTA_MUTED), hatch=HATCH_GRUPO.get(grp),
               edgecolor=g.SUPERFICIE, linewidth=0.4, zorder=3, label=grp)
    ax.set_xticks(x)
    ax.set_xticklabels(rotulos, fontsize=9.5, rotation=20 if len(cats) > 4 else 0,
                       ha="right" if len(cats) > 4 else "center")
    ax.yaxis.set_major_formatter((lambda v, _: f"{v:.0f}%") if pct else (lambda v, _: _fmt_reais(v)))
    ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
    ax.legend(loc="upper left" if pct else "upper right", frameon=False, fontsize=9)
    fig.tight_layout()
    return _salvar_bare(fig, nome_arquivo)


def _fig_quartis_stack(dq, dim, grupos, nome_arquivo):
    """100% empilhado: x = grupo×quartil, empilhado pelas categorias ordinais da
    dimensão. Uma cor sequencial por categoria."""
    cats = [c for c in DIM_ORDEM[dim] if c in set(dq["categoria"])]
    if not cats:
        return _placeholder(nome_arquivo)
    cores = g.CMAP_SEQUENCIAL(np.linspace(0.15, 0.95, len(cats)))
    rot_grp = {"Branca": "Branca", "Negra": "Negra", "Branca · Homem": "Br·H",
               "Branca · Mulher": "Br·M", "Negra · Homem": "Ne·H", "Negra · Mulher": "Ne·M"}
    barras = [(grp, q) for grp in grupos for q in Q_ORDEM]
    x = np.arange(len(barras))
    fig, ax = _eixo((max(9, 0.7 * len(barras) + 2), 5.0))
    base = np.zeros(len(barras))
    for ci, cat in enumerate(cats):
        alturas = []
        for grp, q in barras:
            row = dq[(dq["grupo"] == grp) & (dq["quartil"] == q) & (dq["categoria"] == cat)]
            alturas.append(float(row["pct_do_quartil"].iloc[0]) if len(row) else 0.0)
        ax.bar(x, alturas, 0.8, bottom=base, color=cores[ci], zorder=3,
               label=DIM_ROT[dim].get(cat, cat))
        base += np.array(alturas)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{rot_grp.get(grp, grp)}\n{Q_CURTO[q]}" for grp, q in barras], fontsize=8)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False, fontsize=8)
    fig.tight_layout()
    return _salvar_bare(fig, nome_arquivo)


# --------------------------------------------------------------------------- #
def construir(dados):
    dist = dados["extremos_distribuicao_racial"]
    renda = dados["extremos_renda_racial"]
    comp = dados["extremos_composicao_racial"]
    quart = dados["quartis_multi_racial"]
    _, qq = _recente(dist)
    folhas = []

    def add(tipo, sub, titulo, subtitulo, arquivo, legenda):
        folhas.append({"tipo": tipo, "ramo": "—", "sub": sub, "titulo": titulo,
                       "subtitulo": subtitulo, "arquivo": arquivo, "legenda": legenda})

    dr, _ = _recente(dist)
    rr, _ = _recente(renda)
    cr, _ = _recente(comp)
    qr, _ = _recente(quart)
    EXTREMOS = [("topo10", "10% que mais ganham"), ("base10", "10% que menos ganham")]

    # 1. Distribuição racial — limiar único do Brasil ---------------------- #
    sub_br = dr[dr["escopo_limiar"] == "brasil"]
    _fig_barras_grupo(
        [rot for _, rot in EXTREMOS], [rot for _, rot in EXTREMOS],
        {raca: [float(sub_br[(sub_br["extremo"] == ex) & (sub_br["raca_cor"] == raca)]["pct_do_extremo"].iloc[0])
                for ex, _ in EXTREMOS] for raca in ["Branca", "Negra", "Indígena"]},
        "ext_dist_brasil.png")
    add("extremo", "Distribuição racial — limiar do Brasil",
        "De quem são os 10% mais ricos e os 10% mais pobres do Brasil?",
        f"% de cada raça dentro do decil · limiar P90/P10 único, todo o Brasil · {qq}",
        "ext_dist_brasil.png",
        "Negra é ~56% da população ocupada, mas só ~33% do topo 10% e ~73% da base 10%.")

    # 2. Distribuição racial — limiar dentro de cada gênero -------------- #
    for ex, rot in EXTREMOS:
        sub_g = dr[(dr["escopo_limiar"] == "genero") & (dr["extremo"] == ex)]
        _fig_barras_grupo(
            ["Homem", "Mulher"], ["Homens", "Mulheres"],
            {raca: [float(sub_g[(sub_g["grupo_limiar"] == s) & (sub_g["raca_cor"] == raca)]["pct_do_extremo"].iloc[0])
                    for s in ["Homem", "Mulher"]] for raca in ["Branca", "Negra", "Indígena"]},
            f"ext_dist_genero_{ex}.png")
        add("extremo", f"Distribuição racial — {rot} de cada gênero",
            f"Dentro dos {rot} de cada gênero, qual a composição racial?",
            f"% de cada raça no decil · limiar P{'90' if ex == 'topo10' else '10'} calculado dentro de cada gênero · {qq}",
            f"ext_dist_genero_{ex}.png",
            f"Limiar por gênero: a sub-representação de Negra no topo (e sobre-representação na base) persiste dentro de cada gênero.")

    # 3. Renda R$ do extremo — por raça e por raça×gênero -------------- #
    for recorte, grupos, slug, rot_rec in [
        ("raca", ["Branca", "Negra"], "raca", "por raça"),
        ("raca_sexo", ["Branca · Homem", "Branca · Mulher", "Negra · Homem", "Negra · Mulher"], "raca_sexo", "por raça × gênero"),
    ]:
        sub_r = rr[rr["recorte"] == recorte]
        # topo 10% e base 10% em slides SEPARADOS — juntos, as barras da base (R$ ~900)
        # somem ao lado das do topo (R$ ~20 mil).
        for ex, rot_ex in EXTREMOS:
            _fig_barras_grupo(
                [rot_ex], [rot_ex],
                {grp: [float(sub_r[(sub_r["extremo"] == ex) & (sub_r["grupo"] == grp)]["renda_media_extremo"].iloc[0])
                       if len(sub_r[(sub_r["extremo"] == ex) & (sub_r["grupo"] == grp)]) else np.nan]
                 for grp in grupos},
                f"ext_renda_{slug}_{ex}.png", pct=False)
            add("extremo", f"Renda em R$ dos {rot_ex} — {rot_rec}",
                f"Quanto ganham (R$) os {rot_ex}, {rot_rec}?",
                f"renda média real no decil · limiar P{'90' if ex == 'topo10' else '10'} dentro de cada grupo ({rot_rec}) · {qq}",
                f"ext_renda_{slug}_{ex}.png",
                f"Os {rot_ex}, {rot_rec}: distância em R$ entre os grupos.")

    # 4. Composição (escolaridade/faixa/geração) dentro do decil ------- #
    for recorte, grupos, rot_rec, slugr in [
        ("raca", ["Branca", "Negra"], "por raça", "raca"),
        ("raca_sexo", ["Branca · Homem", "Branca · Mulher", "Negra · Homem", "Negra · Mulher"], "por raça × gênero", "raca_sexo"),
    ]:
        for ex, rot in EXTREMOS:
            for dim in ["nivel_instrucao", "faixa_etaria", "geracao"]:
                cats = [c for c in DIM_ORDEM[dim]]
                sub_c = cr[(cr["recorte"] == recorte) & (cr["extremo"] == ex) & (cr["dimensao"] == dim)]
                if sub_c.empty:
                    continue
                _fig_barras_grupo(
                    cats, [DIM_ROT[dim].get(c, c) for c in cats],
                    {grp: [float(sub_c[(sub_c["grupo"] == grp) & (sub_c["categoria"] == c)]["pct_no_extremo"].iloc[0])
                           if len(sub_c[(sub_c["grupo"] == grp) & (sub_c["categoria"] == c)]) else 0.0
                           for c in cats] for grp in grupos},
                    f"ext_comp_{slugr}_{ex}_{dim}.png")
                add("extremo", f"{rot} · {DIM_NOME[dim]} · {rot_rec}",
                    f"{DIM_NOME[dim].capitalize()} dentro dos {rot} — {rot_rec}",
                    f"% de cada categoria dentro do decil · limiar P{'90' if ex=='topo10' else '10'} dentro de cada grupo · {qq}",
                    f"ext_comp_{slugr}_{ex}_{dim}.png",
                    f"Composição por {DIM_NOME[dim]} de quem está nos {rot}, {rot_rec}.")

    # 5. Quartis (Q1-Q4) — decomposição generalizada ----------------- #
    for recorte, grupos, rot_rec, slugr in [
        ("raca", ["Branca", "Negra"], "por raça", "raca"),
        ("raca_sexo", ["Branca · Homem", "Branca · Mulher", "Negra · Homem", "Negra · Mulher"], "por raça × gênero", "raca_sexo"),
    ]:
        dims = ["sexo", "nivel_instrucao", "faixa_etaria", "geracao"] if recorte == "raca" \
            else ["nivel_instrucao", "faixa_etaria", "geracao"]
        for dim in dims:
            sub_q = qr[(qr["recorte"] == recorte) & (qr["dimensao"] == dim)]
            if sub_q.empty:
                continue
            arq = f"ext_quartil_{slugr}_{dim}.png"
            if dim == "sexo":
                cats_ok = ["Mulher"]
                _fig_barras_grupo(
                    Q_ORDEM, [Q_CURTO[q] for q in Q_ORDEM],
                    {grp: [float(sub_q[(sub_q["grupo"] == grp) & (sub_q["quartil"] == q) & (sub_q["categoria"] == "Mulher")]["pct_do_quartil"].iloc[0])
                           if len(sub_q[(sub_q["grupo"] == grp) & (sub_q["quartil"] == q) & (sub_q["categoria"] == "Mulher")]) else 0.0
                           for q in Q_ORDEM] for grp in grupos},
                    arq)
                legenda = "% de mulheres em cada quartil de renda, por raça — mais mulheres nos quartis de baixo."
            else:
                _fig_quartis_stack(sub_q, dim, grupos, arq)
                legenda = f"Mix de {DIM_NOME[dim]} em cada quartil (Q1→Q4), {rot_rec} — 100% empilhado."
            add("extremo", f"Quartis Q1–Q4 · {DIM_NOME[dim]} · {rot_rec}",
                f"Decomposição dos 4 quartis de renda por {DIM_NOME[dim]} — {rot_rec}",
                f"limiares P25/P50/P75 dentro de cada grupo ({rot_rec}) · {qq}",
                arq, legenda)

    return [{"item": "D", "titulo": "Topo 10%, base 10% e quartis (limiares novos)", "folhas": folhas}]


def main():
    nomes = ["extremos_distribuicao_racial", "extremos_renda_racial",
             "extremos_composicao_racial", "quartis_multi_racial"]
    dados = {n: pd.read_parquet(PROCESSED / f"{n}.parquet") for n in nomes}
    secoes = construir(dados)
    manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    manifesto["extremos"] = secoes
    manifesto.setdefault("_meta", {})["fonte"] = FONTE
    MANIFESTO.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
    n = sum(len(s["folhas"]) for s in secoes)
    print(f"Fase D: {n} gráficos crus (seção 'extremos' do manifesto).")
    for f in secoes[0]["folhas"]:
        print(f"  {f['arquivo']}")


if __name__ == "__main__":
    main()
