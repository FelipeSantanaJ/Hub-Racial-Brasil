"""Onda 3 — Bloco D, partes estruturais (fichas `docs/studies/D2`…`D6`); a decomposição geral está em `bloco_d.py`.

- **D2** — educação: hiato por nível de instrução (bruto e condicional), quantis dentro do nível (bootstrap Rao-Wu),
  sobrequalificação de diplomados (três definições) e Gelbach do hiato entre diplomados.
- **D3** — ocupação: segregação (Duncan e Theil H; grupamento e CBO de 4 dígitos) com benchmark de alocação
  aleatória; hiato dentro da mesma CBO de 4 dígitos (efeitos fixos absorvidos).
- **D4** — território: Kitagawa entre/dentro de UF; hiato por UF (BH entre as 27); por tipo de área e urbano/rural.
- **D5** — posição na ocupação e previdência: diferenças brutas e condicionais (MQO linear).
- **D6** — hiato por faixa etária e perfil idade-renda.

Uso:
    python -m src.processing.bloco_d_estrutura [--so d2 d3 d4 d5 d6 segregacao]
"""
from __future__ import annotations

import argparse

import duckdb
import numpy as np
import pandas as pd
from scipy import stats

from src.inference import multiplicidade
from src.inference.saida import salvar_tabela
from src.processing.agregacoes_pnadc import OUTPUT_DIR
from src.processing.bloco_a import _quantis, multiplicadores_rao_wu
from src.processing.bloco_d import (BLOCOS, JANELAS, RACAS_D, ROTULO, Sistema, _amostra_p1, ep_de, gelbach,
                                    micro_d, montar_x)
from src.processing.sensibilidade_populacao import Z95
from src.inference import variancia

SE = "wls_influencia_linearizacao_estrato_upa"
NIVEIS = {"1": "Sem instrução", "2": "Fundamental incompleto", "3": "Fundamental completo", "4": "Médio incompleto",
          "5": "Médio completo", "6": "Superior incompleto", "7": "Superior completo"}
SOBREQUAL = {"principal: grupos 04–09": ["04", "05", "06", "07", "08", "09"],
             "antiga: só grupo 09": ["09"], "estrita: grupos 03–09": ["03", "04", "05", "06", "07", "08", "09"]}
POSICOES = {"Empregado privado com carteira": ["01"], "Empregado privado sem carteira": ["02"],
            "Trabalhador doméstico": ["03", "04"], "Setor público (inclui militar e estatutário)": ["05", "06", "07"],
            "Empregador": ["08"], "Conta própria": ["09"]}


# ----------------------------------------------------------------------------------------- #
# ferramenta comum: coeficiente de raça num domínio
# ----------------------------------------------------------------------------------------- #
def coef_raca(m: pd.DataFrame, y: np.ndarray, dom: np.ndarray, blocos: list[str], min_n: int = 30) -> dict:
    """{raça: (coeficiente raça − Branca, ψ de tamanho len(m), n do grupo no domínio)} de y ~ raça + blocos no domínio."""
    raca = m["raca"].to_numpy(object)
    racas = [r for r in RACAS_D if (dom & (raca == r)).sum() >= min_n]
    if not racas or (dom & (raca == "Branca")).sum() < min_n:
        return {}
    sub = m[dom]
    X, idx = montar_x(sub, blocos, racas)
    s = Sistema(X, y[dom], m["peso"].to_numpy(float)[dom])
    cols = np.arange(X.shape[1])
    b = s.beta(cols)
    out = {}
    for j, r in enumerate(racas, start=1):
        c = np.zeros(len(cols))
        c[j] = 1.0
        psi = np.zeros(len(m))
        psi[dom] = s.influencia(cols, c, b)
        out[r] = (float(b[j]), psi, int((dom & (raca == r)).sum()))
    return out


def _ic(df: pd.DataFrame, col: str = "estimativa") -> pd.DataFrame:
    df["ic_inferior"] = df[col] - Z95 * df["ep"]
    df["ic_superior"] = df[col] + Z95 * df["ep"]
    return df


def _p(df: pd.DataFrame, col: str = "estimativa") -> pd.DataFrame:
    df["p_valor"] = 2 * stats.norm.sf(np.abs(df[col] / df["ep"]))
    return df


# ----------------------------------------------------------------------------------------- #
# D2 — educação
# ----------------------------------------------------------------------------------------- #
def d2(m: pd.DataFrame, janela: str, n_boot: int = 200) -> tuple[list[dict], list[dict], list[dict]]:
    upa, est = m["upa"].to_numpy(), m["estrato"].to_numpy()
    y = np.log(m["renda"].to_numpy(float))
    niv = m["instrucao"].astype(str).to_numpy()
    niveis, guard = [], {}
    for cod, rot in NIVEIS.items():
        dom = niv == cod
        for esp, blocos in (("bruto", []), ("condicional (idade, sexo, território)", ["idade", "sexo", "territorio"])):
            for r, (c, psi, n) in coef_raca(m, y, dom, blocos).items():
                niveis.append({"periodo": janela, "nivel": rot, "codigo": cod, "raca": r, "especificacao": esp,
                               "estimativa": -c, "ep": ep_de(psi, upa, est), "n_grupo": n})
                guard[(cod, r, esp)] = (-c, -psi)
    for r in RACAS_D:
        for esp in ("bruto", "condicional (idade, sexo, território)"):
            if ("7", r, esp) in guard and ("2", r, esp) in guard:
                v = guard[("7", r, esp)][0] - guard[("2", r, esp)][0]
                e = ep_de(guard[("7", r, esp)][1] - guard[("2", r, esp)][1], upa, est)
                niveis.append({"periodo": janela, "nivel": "Superior completo − Fundamental incompleto", "codigo": "7−2",
                               "raca": r, "especificacao": esp, "estimativa": v, "ep": e, "emd_80pct": 2.8 * e})
    # quantis dentro do nível (Branca × Negra)
    qs = [0.10, 0.50, 0.90]
    quant = []
    for rot, cods in (("Superior completo", ["7"]), ("Médio completo ou superior incompleto", ["5", "6"])):
        sel = np.isin(niv, cods) & m["raca"].isin(["Branca", "Negra"]).to_numpy()
        mm = m[sel].reset_index(drop=True)
        yy, ww = y[sel], mm["peso"].to_numpy(float)
        cod_u, mult = multiplicadores_rao_wu(mm["upa"].to_numpy(), mm["estrato"].to_numpy(), n_boot, seed=17)
        estq, rep = {}, {}
        for g in ("Branca", "Negra"):
            ix = np.flatnonzero(mm["raca"].to_numpy(object) == g)
            o = ix[np.argsort(yy[ix], kind="stable")]
            estq[g] = _quantis(yy[o], ww[o], qs)
            rep[g] = _quantis(yy[o], ww[o][:, None] * mult[cod_u[o]], qs)
        for i, q in enumerate(qs):
            dif = rep["Branca"][i] - rep["Negra"][i]
            quant.append({"periodo": janela, "nivel": rot, "quantil": f"P{int(round(q * 100))}",
                          "ln_branca": float(estq["Branca"][i]), "ln_negra": float(estq["Negra"][i]),
                          "estimativa": float(estq["Branca"][i] - estq["Negra"][i]), "ep_bootstrap": float(dif.std(ddof=1)),
                          "ic_inferior": float(np.percentile(dif, 2.5)), "ic_superior": float(np.percentile(dif, 97.5))})
    # sobrequalificação entre diplomados
    sob = []
    dipl = niv == "7"
    ocup = m["ocupacao"].astype(str).to_numpy()
    for nome, grupos in SOBREQUAL.items():
        ind = 100 * np.isin(ocup, grupos).astype(float)
        for r in ["Branca", *RACAS_D]:
            d = dipl & (m["raca"] == r).to_numpy()
            z, mu = variancia.influencia_media(np.where(d, ind, 0.0), m["peso"].to_numpy(float), d)
            sob.append({"periodo": janela, "definicao": nome, "raca": r, "medida": "% sobrequalificado",
                        "estimativa": mu, "ep": ep_de(z, upa, est), "n": int(d.sum())})
        for esp, blocos in (("diferença bruta (p.p.)", []), ("diferença condicional (p.p.)", ["idade", "sexo", "territorio"])):
            for r, (c, psi, n) in coef_raca(m, ind, dipl, blocos).items():
                sob.append({"periodo": janela, "definicao": nome, "raca": f"{r} − Branca", "medida": esp,
                            "estimativa": c, "ep": ep_de(psi, upa, est), "n": n})
    # Gelbach do hiato entre diplomados, com o bloco 'sobrequalificado' (definição principal)
    md = m[dipl].reset_index(drop=True).assign(sobreq=lambda d: np.isin(d["ocupacao"].astype(str), SOBREQUAL["principal: grupos 04–09"]))
    X, idx = montar_x(md, ["idade", "sexo", "territorio"])
    X = np.column_stack([X, md["sobreq"].to_numpy(float)])
    idx["sobrequalificacao"] = np.array([X.shape[1] - 1])
    s = Sistema(X, np.log(md["renda"].to_numpy(float)), md["peso"].to_numpy(float))
    blocos_g = ["idade", "sexo", "territorio", "sobrequalificacao"]
    for j, r in enumerate(RACAS_D, start=1):
        b0 = s.beta(idx["base"])
        bruto = -b0[j]
        for blk, (dlt, psi) in gelbach(s, idx, blocos_g, j).items():
            sob.append({"periodo": janela, "definicao": "principal: grupos 04–09", "raca": f"{r} − Branca",
                        "medida": f"Gelbach entre diplomados (lp): {ROTULO.get(blk, 'Sobrequalificação')}",
                        "estimativa": -dlt, "ep": ep_de(psi, md["upa"].to_numpy(), md["estrato"].to_numpy()),
                        "pct_do_bruto": 100 * -dlt / bruto, "n": int((md["raca"] == r).sum())})
        sob.append({"periodo": janela, "definicao": "principal: grupos 04–09", "raca": f"{r} − Branca",
                    "medida": "hiato bruto entre diplomados (lp)", "estimativa": bruto, "ep": np.nan,
                    "n": int((md["raca"] == r).sum())})
    return niveis, quant, sob


# ----------------------------------------------------------------------------------------- #
# D3 — segregação e hiato dentro da CBO
# ----------------------------------------------------------------------------------------- #
def indices_segregacao(cat: np.ndarray, negra: np.ndarray, w: np.ndarray) -> tuple[float, float]:
    """Duncan D e Theil H (informação) entre dois grupos ao longo das categorias `cat` (códigos inteiros)."""
    k = int(cat.max()) + 1
    n_o = np.bincount(cat, weights=w * negra, minlength=k)
    b_o = np.bincount(cat, weights=w * (1 - negra), minlength=k)
    N, B = n_o.sum(), b_o.sum()
    D = 0.5 * np.abs(b_o / B - n_o / N).sum()
    t_o, T = n_o + b_o, N + B

    def ent(p):
        p = np.clip(p, 1e-15, 1 - 1e-15)
        return -(p * np.log(p) + (1 - p) * np.log(1 - p))
    E = ent(N / T)
    ok = t_o > 0
    H = float(np.sum(t_o[ok] / T * (E - ent(n_o[ok] / t_o[ok]))) / E)
    return float(D), H


def segregacao(m: pd.DataFrame, chaves: dict, n_perm: int = 20, n_boot: int = 0) -> list[dict]:
    sel = m["raca"].isin(["Branca", "Negra"]).to_numpy()
    mm = m[sel]
    negra = (mm["raca"] == "Negra").to_numpy(float)
    w = mm["peso"].to_numpy(float)
    rng = np.random.default_rng(7)
    linhas = []
    for nivel, col in (("grupamento VD4011", "ocupacao"), ("CBO 4 dígitos (V4010)", "cbo")):
        v = mm[col].astype(str)
        ok = (mm[col].notna() & ~v.isin(["0000", "nan", "None", "0"])).to_numpy()
        cat = pd.factorize(v[ok])[0]
        D, H = indices_segregacao(cat, negra[ok], w[ok])
        perm = [indices_segregacao(cat, rng.permutation(negra[ok]), w[ok]) for _ in range(n_perm)]
        Dr, Hr = np.mean([p[0] for p in perm]), np.mean([p[1] for p in perm])
        linha = {**chaves, "nivel": nivel, "n_categorias": int(cat.max()) + 1, "duncan_D": D, "theil_H": H,
                 "duncan_D_aleatorio": Dr, "theil_H_aleatorio": Hr, "duncan_D_excesso": D - Dr, "theil_H_excesso": H - Hr}
        if n_boot:
            cod, mult = multiplicadores_rao_wu(mm["upa"].to_numpy()[ok], mm["estrato"].to_numpy()[ok], n_boot, seed=23)
            reps = np.array([indices_segregacao(cat, negra[ok], w[ok] * mult[cod, b]) for b in range(n_boot)])
            linha.update({"duncan_D_ep": float(reps[:, 0].std(ddof=1)), "theil_H_ep": float(reps[:, 1].std(ddof=1))})
        linhas.append(linha)
    return linhas


def d3_dentro_cbo(m: pd.DataFrame, janela: str) -> list[dict]:
    """Coeficiente de raça em ln renda: E8 sem ocupação, E8 (grupamento) e E8 com efeitos fixos de CBO-4."""
    upa, est = m["upa"].to_numpy(), m["estrato"].to_numpy()
    y = np.log(m["renda"].to_numpy(float))
    w = m["peso"].to_numpy(float)
    sem_ocup = [b for b in BLOCOS if b != "ocupacao"]
    res = {"E8 sem ocupação": coef_raca(m, y, np.ones(len(m), bool), sem_ocup),
           "E8 (grupamento VD4011)": coef_raca(m, y, np.ones(len(m), bool), BLOCOS)}
    # efeitos fixos de CBO-4: desvio da média ponderada dentro da ocupação (Frisch-Waugh-Lovell)
    cbo = pd.factorize(m["cbo"].astype(str))[0]
    X, idx = montar_x(m, sem_ocup)
    X = X[:, 1:]  # a constante some no desvio
    sw = np.bincount(cbo, weights=w)

    def desviar(v):
        return v - (np.bincount(cbo, weights=w * v) / sw)[cbo]
    Xd = np.column_stack([desviar(X[:, j]) for j in range(X.shape[1])])
    del X
    s = Sistema(Xd, desviar(y), w)
    cols = np.arange(Xd.shape[1])
    b = s.beta(cols)
    fe = {}
    for j, r in enumerate(RACAS_D):
        c = np.zeros(len(cols))
        c[j] = 1.0
        fe[r] = (float(b[j]), s.influencia(cols, c, b), int((m["raca"] == r).sum()))
    res["E8 com efeitos fixos de CBO 4 dígitos"] = fe
    linhas = []
    for esp, rr in res.items():
        for r, (c, psi, n) in rr.items():
            linhas.append({"periodo": janela, "raca": r, "especificacao": esp, "estimativa": -c, "ep": ep_de(psi, upa, est),
                           "n_grupo": n})
    for r in RACAS_D:
        a, pa, _ = res["E8 com efeitos fixos de CBO 4 dígitos"][r]
        bb, pb, _ = res["E8 (grupamento VD4011)"][r]
        razao, psi = a / bb, pa / bb - a * pb / bb ** 2
        linhas.append({"periodo": janela, "raca": r, "especificacao": "razão CBO-4 ÷ grupamento", "estimativa": razao,
                       "ep": ep_de(psi, upa, est), "n_cbo": int(cbo.max()) + 1})
    return linhas


# ----------------------------------------------------------------------------------------- #
# D4 — território
# ----------------------------------------------------------------------------------------- #
def d4(m: pd.DataFrame, janela: str) -> tuple[list[dict], list[dict]]:
    upa, est = m["upa"].to_numpy(), m["estrato"].to_numpy()
    w = m["peso"].to_numpy(float)
    y = np.log(m["renda"].to_numpy(float))
    raca, uf = m["raca"].to_numpy(object), m["uf"].to_numpy(object)
    domB, domN = raca == "Branca", raca == "Negra"
    entre = dentro = 0.0
    psi_e, psi_d = np.zeros(len(m)), np.zeros(len(m))
    kit = []
    for u in sorted(set(uf)):
        iu = (uf == u).astype(float)
        zsB, sB = variancia.influencia_media(np.where(domB, iu, 0.0), w, domB)
        zsN, sN = variancia.influencia_media(np.where(domN, iu, 0.0), w, domN)
        dB, dN = domB & (uf == u), domN & (uf == u)
        zyB, yB = variancia.influencia_media(np.where(dB, y, 0.0), w, dB)
        zyN, yN = variancia.influencia_media(np.where(dN, y, 0.0), w, dN)
        entre += (sB - sN) * (yB + yN) / 2
        dentro += (yB - yN) * (sB + sN) / 2
        psi_e += (zsB - zsN) * (yB + yN) / 2 + (sB - sN) * (zyB + zyN) / 2
        psi_d += (zyB - zyN) * (sB + sN) / 2 + (yB - yN) * (zsB + zsN) / 2
    for comp, v, psi in (("hiato total (lp)", entre + dentro, psi_e + psi_d), ("entre UFs (composição)", entre, psi_e),
                         ("dentro das UFs", dentro, psi_d)):
        kit.append({"periodo": janela, "recorte": "Kitagawa por UF", "grupo": comp, "raca": "Negra",
                    "especificacao": "Kitagawa", "estimativa": float(v), "ep": ep_de(psi, upa, est),
                    "pct_do_total": 100 * v / (entre + dentro)})
    # por UF, tipo de área e urbano/rural
    por = []
    guard = {}
    rot_area = {"1": "Capital", "2": "Resto da RM (exclui capital)", "3": "Resto da RIDE (exclui capital)", "4": "Resto da UF"}
    recortes = [("UF", u, uf == u) for u in sorted(set(uf))]
    recortes += [("tipo de área (V1023)", rot_area.get(a, a), m["area"].astype(str).to_numpy() == a) for a in rot_area]
    recortes += [("situação (V1022)", rot, m["urbano"].astype(str).to_numpy() == c) for c, rot in (("1", "Urbana"), ("2", "Rural"))]
    for recorte, grupo, dom in recortes:
        pct_negra = 100 * w[dom & domN].sum() / w[dom & (domN | domB)].sum() if dom.any() else np.nan
        esps = [("bruto", []), ("condicional (idade, sexo, instrução)", ["idade", "sexo", "instrucao"])]
        if recorte != "UF":  # tipo de área e situação misturam UFs: também com território (UF, urbano, tipo de área)
            esps.append(("condicional (idade, sexo, instrução, território)", ["idade", "sexo", "instrucao", "territorio"]))
        for esp, blocos in esps:
            for r, (c, psi, n) in coef_raca(m, y, dom, blocos).items():
                if r != "Negra":
                    continue
                por.append({"periodo": janela, "recorte": recorte, "grupo": grupo, "raca": r, "especificacao": esp,
                            "estimativa": -c, "ep": ep_de(psi, upa, est), "n_grupo": n, "pct_negra_em_p1": pct_negra})
                guard[(recorte, grupo, esp)] = (-c, -psi)
    for esp in ("bruto", "condicional (idade, sexo, instrução)", "condicional (idade, sexo, instrução, território)"):
        a, b_ = guard.get(("tipo de área (V1023)", "Capital", esp)), guard.get(("tipo de área (V1023)", "Resto da UF", esp))
        if a and b_:
            por.append({"periodo": janela, "recorte": "tipo de área (V1023)", "grupo": "Capital − Resto da UF", "raca": "Negra",
                        "especificacao": esp, "estimativa": a[0] - b_[0], "ep": ep_de(a[1] - b_[1], upa, est)})
    return kit, por


def correlacao_uf(por: pd.DataFrame, n_sim: int = 2000) -> list[dict]:
    """Spearman entre hiato condicional por UF e % negra em P1; IC por simulação paramétrica (estimativa ± EP) e por
    reamostragem das UFs."""
    rng = np.random.default_rng(13)
    linhas = []
    for janela, x in por[(por["recorte"] == "UF") & (por["especificacao"].str.startswith("condicional"))].groupby("periodo"):
        rho = stats.spearmanr(x["estimativa"], x["pct_negra_em_p1"]).statistic
        par = [stats.spearmanr(x["estimativa"] + rng.normal(0, 1, len(x)) * x["ep"], x["pct_negra_em_p1"]).statistic
               for _ in range(n_sim)]
        ix = [rng.integers(0, len(x), len(x)) for _ in range(n_sim)]
        boot = [stats.spearmanr(x["estimativa"].to_numpy()[i], x["pct_negra_em_p1"].to_numpy()[i]).statistic for i in ix]
        linhas.append({"periodo": janela, "recorte": "UF", "grupo": "Spearman(hiato condicional, % negra)", "raca": "Negra",
                       "especificacao": "correlação entre UFs", "estimativa": float(rho),
                       "ic_inferior": float(np.percentile(par, 2.5)), "ic_superior": float(np.percentile(par, 97.5)),
                       "ic_inferior_reamostrando_ufs": float(np.nanpercentile(boot, 2.5)),
                       "ic_superior_reamostrando_ufs": float(np.nanpercentile(boot, 97.5))})
    return linhas


# ----------------------------------------------------------------------------------------- #
# D5 — posição na ocupação
# ----------------------------------------------------------------------------------------- #
def d5(m: pd.DataFrame, janela: str) -> tuple[list[dict], dict]:
    upa, est = m["upa"].to_numpy(), m["estrato"].to_numpy()
    pos = m["posicao"].astype(str).to_numpy()
    tudo = np.ones(len(m), bool)
    linhas, guard = [], {}
    desfechos = {k: 100 * np.isin(pos, v).astype(float) for k, v in POSICOES.items()}
    desfechos["Contribui para a previdência"] = 100 * (m["previdencia"].astype(str) == "1").to_numpy(float)
    for nome, yy in desfechos.items():
        for r in ["Branca", *RACAS_D]:
            d = (m["raca"] == r).to_numpy()
            z, mu = variancia.influencia_media(np.where(d, yy, 0.0), m["peso"].to_numpy(float), d)
            linhas.append({"periodo": janela, "desfecho": nome, "nivel": "todos", "raca": r, "medida": "% do grupo",
                           "estimativa": mu, "ep": ep_de(z, upa, est)})
        for esp, blocos in (("diferença bruta (p.p.)", []),
                            ("diferença condicional (p.p.)", ["idade", "sexo", "instrucao", "territorio"])):
            for r, (c, psi, n) in coef_raca(m, yy, tudo, blocos).items():
                linhas.append({"periodo": janela, "desfecho": nome, "nivel": "todos", "raca": f"{r} − Branca",
                               "medida": esp, "estimativa": c, "ep": ep_de(psi, upa, est), "n_grupo": n})
                guard[(nome, r, esp)] = (c, psi)
    niv = m["instrucao"].astype(str).to_numpy()
    for nome in ("Empregado privado com carteira", "Contribui para a previdência"):
        for cod, rot in NIVEIS.items():
            for r, (c, psi, n) in coef_raca(m, desfechos[nome], niv == cod, ["idade", "sexo", "territorio"]).items():
                linhas.append({"periodo": janela, "desfecho": nome, "nivel": rot, "raca": f"{r} − Branca",
                               "medida": "diferença condicional (p.p.)", "estimativa": c, "ep": ep_de(psi, upa, est),
                               "n_grupo": n})
    guard["upa"], guard["est"] = upa, est
    return linhas, guard


# ----------------------------------------------------------------------------------------- #
# D6 — idade
# ----------------------------------------------------------------------------------------- #
FAIXAS_D6 = [(18, 24), (25, 29), (30, 34), (35, 39), (40, 44), (45, 49), (50, 54), (55, 59), (60, 64), (65, 200)]


def d6(m: pd.DataFrame, janela: str) -> list[dict]:
    upa, est = m["upa"].to_numpy(), m["estrato"].to_numpy()
    y = np.log(m["renda"].to_numpy(float))
    w = m["peso"].to_numpy(float)
    idade = m["idade"].to_numpy()
    linhas, guard = [], {}
    for lo, hi in FAIXAS_D6:
        rot = f"{lo}–{hi}" if hi < 200 else f"{lo}+"
        dom = (idade >= lo) & (idade <= hi)
        for r in ["Branca", *RACAS_D]:
            d = dom & (m["raca"] == r).to_numpy()
            z, mu = variancia.influencia_media(np.where(d, y, 0.0), w, d)
            linhas.append({"periodo": janela, "faixa_etaria": rot, "raca": r, "medida": "média de ln renda",
                           "estimativa": mu, "ep": ep_de(z, upa, est), "n": int(d.sum())})
        for esp, blocos in (("hiato bruto (lp)", []), ("hiato condicional (lp; sexo, instrução, território)",
                                                       ["sexo", "instrucao", "territorio"])):
            for r, (c, psi, n) in coef_raca(m, y, dom, blocos).items():
                linhas.append({"periodo": janela, "faixa_etaria": rot, "raca": r, "medida": esp, "estimativa": -c,
                               "ep": ep_de(psi, upa, est), "n": n})
                guard[(rot, r, esp)] = (-c, -psi)
    for r in RACAS_D:
        for esp, blocos in (("hiato condicional (lp; sexo, instrução, território)", ["sexo", "instrucao", "territorio"]),
                            ("hiato bruto (lp)", [])):
            a = coef_raca(m, y, (idade >= 50) & (idade <= 59), blocos).get(r)
            b = coef_raca(m, y, (idade >= 25) & (idade <= 29), blocos).get(r)
            if a and b:
                linhas.append({"periodo": janela, "faixa_etaria": "50–59 − 25–29", "raca": r, "medida": esp,
                               "estimativa": -a[0] + b[0], "ep": ep_de(-a[1] + b[1], upa, est)})
    return linhas


# ----------------------------------------------------------------------------------------- #
def gerar(con, fazer: set[str]) -> None:
    out = {k: [] for k in ("d2n", "d2q", "d2s", "d3s", "d3c", "d4k", "d4p", "d5", "d6")}
    g5 = {}
    for janela, tris in JANELAS.items():
        if not fazer & {"d2", "d3", "d4", "d5", "d6"}:
            break
        m = _amostra_p1(micro_d(con, tris))
        print(f"D2–D6 {janela}: {len(m):,}".replace(",", "."), flush=True)
        if "d2" in fazer:
            a, b, c = d2(m, janela)
            out["d2n"] += a
            out["d2q"] += b
            out["d2s"] += c
            print("  D2 ok", flush=True)
        if "d4" in fazer:
            k, p = d4(m, janela)
            out["d4k"] += k
            out["d4p"] += p
            print("  D4 ok", flush=True)
        if "d5" in fazer:
            x, g5[janela] = d5(m, janela)
            out["d5"] += x
            print("  D5 ok", flush=True)
        if "d6" in fazer:
            out["d6"] += d6(m, janela)
            print("  D6 ok", flush=True)
        if "d3" in fazer:
            out["d3c"] += d3_dentro_cbo(m, janela)
            out["d3s"] += segregacao(m, {"periodo": janela}, n_boot=100)
            print("  D3 ok", flush=True)
        del m
    if "segregacao" in fazer:
        for a in range(2012, 2027):
            m = _amostra_p1(micro_d(con, [(a, 2)]))
            out["d3s"] += segregacao(m, {"periodo": f"{a}T2"})
            print(f"  segregação {a}T2", flush=True)
    meta = dict(se_metodo=SE, rotulo_residuo="parte não associada às covariáveis incluídas (R5)")
    if out["d2n"]:
        df = _p(_ic(pd.DataFrame(out["d2n"])))
        df.loc[df["codigo"] == "7−2", "p_valor"] = np.nan
        df = multiplicidade.adicionar_fdr(df, ["periodo", "raca", "especificacao"])
        salvar_tabela(df, OUTPUT_DIR / "d2_hiato_por_nivel.parquet", familia_fdr=["periodo", "raca", "especificacao"], **meta,
                      nota="Hiato Branca − grupo em ln renda (lp) dentro de cada nível de VD3004")
        salvar_tabela(pd.DataFrame(out["d2q"]), OUTPUT_DIR / "d2_quantis_nivel.parquet", se_metodo="bootstrap_rao_wu_estrato_upa_200",
                      nota="Hiato Branca − Negra em quantis de ln renda dentro do nível; heaping: IC estreitos não são precisão")
        salvar_tabela(_ic(pd.DataFrame(out["d2s"])), OUTPUT_DIR / "d2_sobrequalificacao.parquet", **meta,
                      nota="Superior completo em ocupação VD4011 abaixo do nível (três definições); Gelbach entre diplomados")
    if out["d3s"]:
        salvar_tabela(pd.DataFrame(out["d3s"]), OUTPUT_DIR / "d3_segregacao.parquet",
                      se_metodo="bootstrap_rao_wu_estrato_upa_100 (só janelas)",
                      nota="Duncan D e Theil H Branca × Negra; '_aleatorio' = média de 20 sorteios da raça (viés de células pequenas)")
    if out["d3c"]:
        salvar_tabela(_ic(pd.DataFrame(out["d3c"])), OUTPUT_DIR / "d3_hiato_dentro_ocupacao.parquet", **meta,
                      nota="Coeficiente de raça (Branca − grupo, lp) com controles da E8; efeitos fixos de CBO-4 por desvio da média")
    if out["d4k"]:
        p = pd.DataFrame(out["d4p"])
        p = _p(_ic(p))
        uf = p["recorte"] == "UF"
        p = pd.concat([multiplicidade.adicionar_fdr(p[uf], ["periodo", "especificacao"]), p[~uf]], ignore_index=True)
        corr = pd.DataFrame(correlacao_uf(p))
        salvar_tabela(pd.concat([_ic(pd.DataFrame(out["d4k"])), p, corr], ignore_index=True), OUTPUT_DIR / "d4_territorio.parquet",
                      familia_fdr=["periodo", "especificacao"], **meta,
                      nota="Kitagawa entre/dentro de UF (lp); hiato Branca − Negra por UF (BH entre as 27), tipo de área e situação")
    if out["d5"]:
        df = _p(_ic(pd.DataFrame(out["d5"])))
        cond = (df["medida"] == "diferença condicional (p.p.)") & (df["nivel"] == "todos")
        df.loc[~cond, "p_valor"] = np.nan
        df = multiplicidade.adicionar_fdr(df, ["periodo", "raca", "medida", "nivel"])
        if len(g5) == 2:
            g0, g1 = g5["2012"], g5["2025T3-2026T2"]
            upa = np.concatenate([g0["upa"], g1["upa"]])
            est = np.concatenate([g0["est"], g1["est"]])
            mud = []
            for ch in g1:
                if ch in ("upa", "est") or ch not in g0:
                    continue
                mud.append({"periodo": "mudança (2025T3-2026T2 − 2012)", "desfecho": ch[0], "nivel": "todos",
                            "raca": f"{ch[1]} − Branca", "medida": ch[2], "estimativa": g1[ch][0] - g0[ch][0],
                            "ep": ep_de(np.concatenate([-g0[ch][1], g1[ch][1]]), upa, est)})
            df = pd.concat([df, _ic(pd.DataFrame(mud))], ignore_index=True)
        salvar_tabela(df, OUTPUT_DIR / "d5_posicao_ocupacao.parquet", familia_fdr=["periodo", "raca", "medida", "nivel"], **meta,
                      nota="MQO linear; p.p.; condicional = idade, sexo, instrução, território")
    if out["d6"]:
        salvar_tabela(_ic(pd.DataFrame(out["d6"])), OUTPUT_DIR / "d6_hiato_idade.parquet", **meta,
                      nota="Corte transversal: idade e coorte confundidas (ver B4)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--so", nargs="*", default=None, help="d2 d3 d4 d5 d6 segregacao")
    fazer = set(parser.parse_args().so or ["d2", "d3", "d4", "d5", "d6", "segregacao"])
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    gerar(con, fazer)


if __name__ == "__main__":
    main()
