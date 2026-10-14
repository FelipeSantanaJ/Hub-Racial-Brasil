"""Aprofundamentos da Etapa 1.

Gráficos CRUS (título/subtítulo/legenda/fonte viram caixa de texto no PPT, como no
resto do deck) para as análises do bloco de aprofundamentos:

  #1  Renda efetiva vs. habitual — instabilidade de renda por raça
  #2  Prêmio da escolaridade por raça (retorno à educação)
  #3  Hiato Branca vs. Negra — Capital vs. Interior
  #4  Taxa de desocupação por raça × escolaridade
  #5  Hiato Branca vs. Negra — setor formal vs. informal
  #6  % ganhando até 1 / até 2 / acima de 3 salários mínimos, por raça
  #7  Oaxaca-Blinder / RIF ao longo do tempo (parcela explicada vs. não-explicada)
  #8  Dupla desvantagem: decomposição Homem Branco ↔ Mulher Negra
  #11 "Quanto tempo até fechar o hiato?" — extrapolação de tendência

Grava a seção `aprofundamentos` em `docs/arvore_manifest.json`.

Uso:
    python -m src.processing.graficos_aprofundamentos
"""
from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.processing import graficos_fase1 as g
from src.processing.graficos_arvore import (
    _salvar, _placeholder, _estilo, _fmt_reais, _fig_serie, MANIFESTO, PROCESSED, FONTE, so_folhas_com_imagem,
)

CORES_RACA = g.CORES_RACA
NIV = g.NIVEIS_INSTRUCAO_ORDEM
ROT_NIV = g.NIVEIS_INSTRUCAO_ROTULO_CURTO
NEG = {"Preta": "Negra", "Parda": "Negra"}


def _mp(sub, val, w=None):
    """Média ponderada de células; sem `w`, usa o peso do denominador (`graficos_fase1.peso_para`)."""
    if sub.empty:
        return np.nan
    if w is None:
        return g.media_ponderada_celulas(sub, val)
    return float((sub[val] * sub[w]).sum() / sub[w].sum()) if sub[w].sum() else np.nan


def _data(df):
    return pd.to_datetime(df["ano"].astype(str) + "-" + ((df["trimestre"] - 1) * 3 + 1).astype(str) + "-01")


def _serie_por_raca_col(df, valcol, w=None, brasil=True):
    d = df.copy()
    if brasil and "nivel_geografico" in d.columns:
        d = d[d["nivel_geografico"] == "brasil"]
    d["raca"] = d["raca_cor"].map(lambda x: NEG.get(x, x))
    d["data"] = _data(d)
    out = {}
    for raca in ("Branca", "Negra", "Indígena"):
        g_ = d[d["raca"] == raca]
        out[raca] = g_.groupby("data").apply(lambda s: _mp(s, valcol, w))
    s = pd.DataFrame(out).sort_index()
    s["Indígena"] = s["Indígena"].rolling(4, center=True, min_periods=2).mean()
    return s


def _folha(tipo, titulo, subtitulo, arquivo, legenda):
    return {"tipo": tipo, "ramo": "—", "sub": titulo, "titulo": titulo,
            "subtitulo": subtitulo, "arquivo": arquivo, "legenda": legenda}


# ------------------------------------------------------------------ #
def construir() -> list[dict]:
    P = PROCESSED
    f = []

    # ---- #1 Renda efetiva vs. habitual ------------------------------- #
    renda = pd.read_parquet(P / "renda.parquet")
    d = renda[renda["nivel_geografico"] == "brasil"].copy()
    d["raca"] = d["raca_cor"].map(lambda x: NEG.get(x, x))
    d["data"] = _data(d)
    razao = {}
    for raca in ("Branca", "Negra", "Indígena"):
        gg = d[d["raca"] == raca]
        ef = gg.groupby("data").apply(lambda s: _mp(s, "renda_efetiva_real_media"))
        hb = gg.groupby("data").apply(lambda s: _mp(s, "renda_habitual_real_media"))
        razao[raca] = (100 * ef / hb)
    sr = pd.DataFrame(razao).sort_index()
    sr["Indígena"] = sr["Indígena"].rolling(4, center=True, min_periods=2).mean()
    _fig_serie(sr, CORES_RACA, "apr_efetiva_habitual.png", pct=True)
    f.append(_folha("grafico", "Renda efetiva ÷ habitual, por raça — Brasil",
                    "% · 100% = recebeu tudo que costuma receber no mês · abaixo de 100% = perda por falta/interrupção · série 2012–2026",
                    "apr_efetiva_habitual.png",
                    "Quanto menor, mais a renda do mês fica abaixo da 'habitual' — instabilidade de renda."))

    # ---- #2 Prêmio da escolaridade por raça ------------------------- #
    rpe = pd.read_parquet(P / "renda_por_escolaridade.parquet")
    rr = rpe[rpe["nivel_geografico"] == "brasil"].copy()
    ano, tri = g._trimestre_mais_recente(rr)
    rr = rr[(rr["ano"] == ano) & (rr["trimestre"] == tri)]
    rr["raca"] = rr["raca_cor"].map(lambda x: NEG.get(x, x))
    base_niv = "Médio completo ou equivalente"
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    _estilo(ax)
    x = np.arange(len(NIV))
    for raca in ("Branca", "Negra", "Indígena"):
        gg = rr[rr["raca"] == raca]
        base = _mp(gg[gg["nivel_instrucao"] == base_niv], "renda_habitual_real_media")
        vals = [100 * _mp(gg[gg["nivel_instrucao"] == n], "renda_habitual_real_media") / base
                if base and not np.isnan(base) else np.nan for n in NIV]
        ax.plot(x, vals, marker="o", color=CORES_RACA[raca], linewidth=2, zorder=3)
        if pd.notna(vals[-1]):
            ax.annotate(raca, xy=(x[-1], vals[-1]), xytext=(8, 0), textcoords="offset points",
                        color=CORES_RACA[raca], fontsize=9.5, fontweight="bold", va="center")
    ax.axhline(100, color=g.EIXO, linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels([ROT_NIV[n] for n in NIV], fontsize=9, rotation=20, ha="right")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}")
    ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
    _salvar(fig, "apr_premio_escolaridade.png")
    f.append(_folha("grafico", "Retorno da escolaridade, por raça — Brasil",
                    f"índice: renda média em cada nível ÷ renda no Médio completo (=100), dentro de cada raça · {tri}º tri. {ano}",
                    "apr_premio_escolaridade.png",
                    "Se a curva de uma raça é mais inclinada, cada degrau de escolaridade 'vale' mais R$ pra ela."))

    # ---- #11 Quanto tempo até fechar o hiato? --------------------- #
    # Desde a Onda 2 (13/10/2026, estudo B6): projeção CONDICIONAL com IC do ritmo (EWC) e duas premissas; a
    # extrapolação simples sem incerteza que estava aqui saiu (contradizia o B1: a queda foi um degrau em 2022).
    b6p = P / "b6_projecao_condicional.parquet"
    if b6p.exists() and (g.OUTPUT_DIR / "onda2_b6_projecao_condicional.png").exists():
        b6 = pd.read_parquet(b6p)
        b6 = b6[b6["serie"] == "P1 · Branca × Negra"].set_index("premissa")
        pa, pb = b6.loc["P-a ritmo linear de todo o período"], b6.loc["P-b ritmo linear desde 2022"]
        fmt = lambda v: f"{v:+.2f}".replace(".", ",")  # noqa: E731
        f.append(_folha("grafico", "Hiato Branca vs. Negra — projeção condicional (não é previsão)",
                        f"se o ritmo de 2012–2026 ({fmt(pa['ritmo_pp_ano'])} p.p./ano) continuar: zero por volta de "
                        f"{pa['ano_central']:.0f} ({pa['ano_mais_cedo']:.0f}–{pa['ano_mais_tarde']:.0f}); no ritmo desde "
                        f"2022 ({fmt(pb['ritmo_pp_ano'])} p.p./ano): sem data",
                        "onda2_b6_projecao_condicional.png",
                        "A queda de 2012–2026 veio de um degrau em 2022 (B1); desde então a série está plana. "
                        "Ficha: docs/studies/B6."))
    (g.OUTPUT_DIR / "apr_convergencia.png").unlink(missing_ok=True)

    # ---- #3 Capital vs. Interior --------------------------------- #
    p = P / "hiato_capital_interior.parquet"
    if p.exists():
        hci = pd.read_parquet(p)
        hci["data"] = _data(hci)
        piv = hci.pivot_table(index="data", columns="localizacao", values="hiato_percentual").sort_index()
        _fig_serie(piv, {"Capital": g.COR_NEGRA, "Interior": "#3a5a9a"},
                   "apr_capital_interior.png", pct=True)
        f.append(_folha("grafico", "Hiato de renda Branca vs. Negra — Capital vs. Interior — Brasil",
                        "% de diferença · Welch trimestre a trimestre · série 2012–2026",
                        "apr_capital_interior.png",
                        "O hiato racial de renda é maior nas capitais ou no interior?"))

    # ---- #4 Desocupação por raça × escolaridade ----------------- #
    p = P / "desocupacao_por_escolaridade.parquet"
    if p.exists():
        de = pd.read_parquet(p)
        ano, tri = g._trimestre_mais_recente(de)
        d = de[(de["ano"] == ano) & (de["trimestre"] == tri)]
        fig, ax = plt.subplots(figsize=(10, 4.8), dpi=150)
        fig.patch.set_facecolor(g.SUPERFICIE)
        _estilo(ax)
        x = np.arange(len(NIV))
        lw = 0.26
        for i, raca in enumerate(("Branca", "Negra", "Indígena")):
            vals = [float(d[(d["raca_cor"] == raca) & (d["nivel_instrucao"] == n)]["taxa_desocupacao_pct"].iloc[0])
                    if len(d[(d["raca_cor"] == raca) & (d["nivel_instrucao"] == n)]) else np.nan for n in NIV]
            ax.bar(x + (i - 1) * lw, [v if pd.notna(v) else 0 for v in vals], lw,
                   color=CORES_RACA[raca], zorder=3, label=raca)
        ax.set_xticks(x)
        ax.set_xticklabels([ROT_NIV[n] for n in NIV], fontsize=9, rotation=20, ha="right")
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
        ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
        ax.legend(loc="upper right", frameon=False, fontsize=9.5)
        _salvar(fig, "apr_desocupacao_escolaridade.png")
        f.append(_folha("grafico", "Taxa de desocupação por raça e escolaridade — Brasil",
                        f"% da força de trabalho desocupada · {tri}º tri. {ano}",
                        "apr_desocupacao_escolaridade.png",
                        "Mais diploma fecha o gap de emprego como (em parte) fecha o de salário?"))

    # ---- #5 Formal vs. informal -------------------------------- #
    p = P / "hiato_formal_informal.parquet"
    if p.exists():
        hf = pd.read_parquet(p)
        hf["data"] = _data(hf)
        piv = hf.pivot_table(index="data", columns="setor", values="hiato_percentual").sort_index()
        _fig_serie(piv, {"Formal": "#3a5a9a", "Informal": g.COR_NEGRA},
                   "apr_formal_informal.png", pct=True)
        f.append(_folha("grafico", "Hiato de renda Branca vs. Negra — setor formal vs. informal — Brasil",
                        "formal = contribui para a previdência · % de diferença · Welch · série 2012–2026",
                        "apr_formal_informal.png",
                        "A informalidade explica parte do hiato, ou ele sobrevive dentro do emprego protegido?"))

    # ---- #6 Salários mínimos ---------------------------------- #
    p = P / "faixas_salario_minimo.parquet"
    if p.exists():
        sm = pd.read_parquet(p)
        sm["data"] = pd.to_datetime(sm["ano"].astype(str) + "-" + ((sm["trimestre"] - 1) * 3 + 1).astype(str) + "-01")
        for col, nome, titulo, leg in [
            ("pct_ate_1sm", "apr_sm_ate1", "% ganhando até 1 salário mínimo, por raça — Brasil",
             "Concentração perto do piso salarial."),
            ("pct_acima_3sm", "apr_sm_acima3", "% ganhando acima de 3 salários mínimos, por raça — Brasil",
             "Presença no topo da distribuição de renda do trabalho."),
        ]:
            piv = sm.pivot_table(index="data", columns="raca_cor", values=col).sort_index()
            piv = piv.reindex(columns=[c for c in ("Branca", "Negra", "Indígena") if c in piv.columns])
            if "Indígena" in piv.columns:
                piv["Indígena"] = piv["Indígena"].rolling(4, center=True, min_periods=2).mean()
            _fig_serie(piv, CORES_RACA, f"{nome}.png", pct=True)
            f.append(_folha("grafico", titulo,
                            "renda habitual nominal ÷ salário mínimo nominal do ano · série 2012–2026", f"{nome}.png", leg))

    # ---- #7 Oaxaca-Blinder / RIF ao longo do tempo ------------ #
    p = P / "oaxaca_blinder_temporal.parquet"
    if p.exists():
        ob = pd.read_parquet(p)
        med = ob[ob["ponto"] == "média"].sort_values("ano")
        fig, ax = plt.subplots(figsize=(11, 4.8), dpi=150)
        fig.patch.set_facecolor(g.SUPERFICIE)
        _estilo(ax)
        ax.stackplot(med["ano"], med["pct_explicada"], med["pct_nao_explicada"],
                     colors=["#3a5a9a", g.COR_NEGRA], alpha=0.85)
        ax.set_ylim(0, 100)
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
        ax.annotate("explicada\n(composição)", xy=(med["ano"].iloc[-1], med["pct_explicada"].iloc[-1] / 2),
                    color=g.SUPERFICIE, fontsize=9, fontweight="bold", ha="right")
        ax.annotate("NÃO-explicada\n(retorno diferente)", xy=(med["ano"].iloc[-1], 100 - med["pct_nao_explicada"].iloc[-1] / 2),
                    color=g.SUPERFICIE, fontsize=9, fontweight="bold", ha="right", va="center")
        ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
        _salvar(fig, "apr_oaxaca_temporal.png")
        f.append(_folha("grafico", "Decomposição de Oaxaca-Blinder do hiato Branca vs. Negra — ano a ano",
                        "controles: faixa etária + escolaridade + ocupação · parcela explicada por composição vs. não-explicada (não explicada = parte não associada às covariáveis incluídas)",
                        "apr_oaxaca_temporal.png",
                        "A parte não-explicada está caindo conforme a escolaridade de negros sobe, ou fica travada?"))

        rif = ob[ob["ponto"].isin(["p10", "p50", "p90"])].copy()
        rif["hiato_resid_pct"] = 100 * (np.exp(rif["residuo_restrito_coef"]) - 1)
        piv = rif.pivot_table(index="ano", columns="ponto", values="hiato_resid_pct")
        piv = piv.reindex(columns=["p10", "p50", "p90"])
        piv.index = pd.to_datetime(piv.index.astype(str) + "-07-01")
        _fig_serie(piv, {"p10": "#3a5a9a", "p50": g.TINTA_MUTED, "p90": g.COR_NEGRA},
                   "apr_rif_temporal.png", pct=True)
        f.append(_folha("grafico", "Hiato residual (não-explicado) por ponto da distribuição — ano a ano",
                        "RIF de P10/P50/P90, mesmos controles · o resíduo em forma de U ('piso pegajoso' na base, 'teto de vidro' no topo) é estável?",
                        "apr_rif_temporal.png",
                        "P10 = base, P50 = mediana, P90 = topo. Cada linha é o hiato que sobra depois dos controles."))

    # ---- #8 Dupla desvantagem -------------------------------- #
    p = P / "dupla_desvantagem.parquet"
    if p.exists():
        dd = pd.read_parquet(p).sort_values(["ano", "trimestre"])
        dd["data"] = _data(dd)
        fig, ax = plt.subplots(figsize=(11, 4.8), dpi=150)
        fig.patch.set_facecolor(g.SUPERFICIE)
        _estilo(ax)
        ax.stackplot(dd["data"], dd["efeito_raca"], dd["efeito_genero"], dd["interacao"],
                     labels=["efeito raça (entre homens)", "efeito gênero (entre brancos)", "interação"],
                     colors=[g.COR_NEGRA, "#3a5a9a", g.COR_INDIGENA], alpha=0.85)
        ax.plot(dd["data"], dd["gap_total"], color=g.TINTA_PRIMARIA, linewidth=1.5, zorder=4)
        ax.yaxis.set_major_formatter(lambda v, _: _fmt_reais(v))
        ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
        ax.legend(loc="upper left", frameon=False, fontsize=8.5)
        _salvar(fig, "apr_dupla_desvantagem.png")
        f.append(_folha("grafico", "Gap de renda Homem Branco ↔ Mulher Negra — decomposição — Brasil",
                        "R$ reais · gap total (linha) = efeito raça + efeito gênero + interação (o 'extra' de ser as duas coisas) · série 2012–2026",
                        "apr_dupla_desvantagem.png",
                        "Do abismo entre o grupo mais e o menos favorecido, quanto é raça, quanto é gênero, quanto é a soma dos dois."))

    # ---- #12 Validação cruzada com o IBGE "Desigualdades" ---------- #
    # Ref.: IBGE, "Desigualdades Sociais por Cor ou Raça no Brasil", 2ª ed. (nov/2022),
    # dados de 2021. Nosso número = média dos 4 trimestres de 2021 do nosso pipeline.
    oc = pd.read_parquet(P / "ocupacao.parquet")
    o = oc[(oc["nivel_geografico"] == "brasil") & (oc["ano"] == 2021)]
    inf = pd.read_parquet(P / "informalidade.parquet")
    iv = inf[(inf["nivel_geografico"] == "brasil") & (inf["ano"] == 2021)]

    def _desoc(r):
        gg = o[o["raca_cor"] == r]
        return 100 * gg["pop_desocupados"].sum() / gg["pop_forca_trabalho"].sum()

    def _informal(r):
        gg = iv[iv["raca_cor"] == r]
        return 100 - g.media_ponderada_celulas(gg, "pct_contribui_previdencia")

    indic = [
        ("Desoc. Branca", 11.3, _desoc("Branca")),
        ("Desoc. Preta", 16.5, _desoc("Preta")),
        ("Desoc. Parda", 16.2, _desoc("Parda")),
        ("Informal. Branca", 32.7, _informal("Branca")),
        ("Informal. Preta", 43.4, _informal("Preta")),
        ("Informal. Parda", 47.0, _informal("Parda")),
    ]
    fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=150)
    fig.patch.set_facecolor(g.SUPERFICIE)
    _estilo(ax)
    x = np.arange(len(indic))
    ax.bar(x - 0.2, [v for _, v, _n in indic], 0.4, color=g.TINTA_MUTED, zorder=3, label="IBGE (Desigualdades, 2021)")
    ax.bar(x + 0.2, [n for _, _v, n in indic], 0.4, color=g.COR_BRANCA, zorder=3, label="Nosso pipeline (média 2021)")
    for xi, (_, v, n) in zip(x, indic):
        ax.text(xi - 0.2, v, f"{v:.0f}", ha="center", va="bottom", fontsize=8, color=g.TINTA_SECUNDARIA)
        ax.text(xi + 0.2, n, f"{n:.0f}", ha="center", va="bottom", fontsize=8, color=g.TINTA_SECUNDARIA)
    ax.set_xticks(x)
    ax.set_xticklabels([r for r, _v, _n in indic], fontsize=9)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.grid(axis="y", color=g.GRADE, linewidth=0.8, zorder=0)
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    _salvar(fig, "apr_validacao_ibge.png")
    f.append(_folha("grafico", "Validação cruzada — nosso pipeline vs. IBGE 'Desigualdades Sociais por Cor ou Raça' (2021)",
                    "taxa de desocupação e informalidade (% sem contribuição previdenciária), Brasil, 2021 · fontes independentes",
                    "apr_validacao_ibge.png",
                    "Reproduzimos os números oficiais dentro de ~1-3 p.p. — diferenças cabem em universo/definição (a 'informalidade' do IBGE é um composto mais amplo). O hiato de renda Branca vs. Preta em 2021 dá ~70% no nosso pipeline (Branca vs. Negra combinada) vs. 76% do IBGE (Branca vs. Preta só) — Preta ganha menos que Parda, daí a diferença."))

    return so_folhas_com_imagem([{"item": "APR", "titulo": "Aprofundamentos", "folhas": f}])


def main():
    secoes = construir()
    manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    manifesto["aprofundamentos"] = secoes
    manifesto.setdefault("_meta", {})["fonte"] = FONTE
    MANIFESTO.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
    n = sum(len(s["folhas"]) for s in secoes)
    print(f"Aprofundamentos: {n} gráficos.")
    for x in secoes[0]["folhas"]:
        print(f"  {x['arquivo']}")


if __name__ == "__main__":
    main()
