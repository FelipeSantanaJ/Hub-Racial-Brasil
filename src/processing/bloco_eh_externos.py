"""Onda 4, parte 2 — fontes externas (INEP e POF; fichas `docs/studies/{E3,E6,E7,H3.2}`). Lê os parquets extraídos por
`src.ingestion.externos_educacao`.

- **E3** — SAEB 2023: proficiência por raça, bruta, com o INSE, com rede/lugar e dentro da escola.
- **E6** — Censo da Educação Superior 2014 e 2023: composição racial de ingressantes, matriculados e concluintes;
  reserva de vagas; razão concluintes ÷ ingressantes.
- **E7** — Censo Escolar 2024: segregação Branca × Negra entre escolas e exposição à infraestrutura.
- **H3.2** — POF 2017–2018: bens duráveis por raça, bruto e no mesmo décimo de renda disponível per capita.

Uso:
    python -m src.processing.bloco_eh_externos [--so e3 e6 e7 h32]
"""
from __future__ import annotations

import argparse

import duckdb
import numpy as np
import pandas as pd
from scipy import stats

from src.inference import multiplicidade, variancia
from src.inference.saida import salvar_tabela
from src.ingestion.externos_educacao import DESTINO as PQ
from src.processing.agregacoes_pnadc import OUTPUT_DIR
from src.processing.bloco_d import Sistema, _dummies, ep_de
from src.processing.sensibilidade_populacao import Z95

SAEB_RACA = {"A": "Branca", "B": "Preta", "C": "Parda", "D": "Amarela", "E": "Indígena"}
SERIES = {"5EF": "5º ano EF", "9EF": "9º ano EF", "34EM": "3ª/4ª série EM"}
INFRA = {"IN_INTERNET_ALUNOS": "Internet para alunos", "IN_BANDA_LARGA": "Banda larga",
         "IN_BIBLIOTECA_SALA_LEITURA": "Biblioteca ou sala de leitura", "IN_LABORATORIO_CIENCIAS": "Laboratório de ciências",
         "IN_LABORATORIO_INFORMATICA": "Laboratório de informática", "IN_QUADRA_ESPORTES": "Quadra de esportes",
         "IN_ESGOTO_REDE_PUBLICA": "Esgoto pela rede pública"}
BENS = {"1403001": "Automóvel", "1403101": "Motocicleta", "1401901": "Microcomputador ou notebook",
        "1401201": "Máquina de lavar roupa", "1402101": "Ar-condicionado", "1400401": "Geladeira de 2 portas",
        "1401401": "TV de LED, plasma ou LCD"}


def _ic(df: pd.DataFrame, col: str = "estimativa") -> pd.DataFrame:
    df["ic_inferior"] = df[col] - Z95 * df["ep"]
    df["ic_superior"] = df[col] + Z95 * df["ep"]
    return df


def _coefs(y, X, w, upa, est, nomes_raca: list[str], primeiro: int = 1) -> dict[str, tuple[float, np.ndarray]]:
    """Coeficientes das colunas primeiro..primeiro+k−1 (dummies de raça) e ψ."""
    s = Sistema(X, y, w)
    cols = np.arange(X.shape[1])
    b = s.beta(cols)
    out = {}
    for j, r in enumerate(nomes_raca, start=primeiro):
        c = np.zeros(len(cols))
        c[j] = 1.0
        out[r] = (float(b[j]), s.influencia(cols, c, b))
    return out


def _desviar(v: np.ndarray, grupo: np.ndarray, w: np.ndarray, sw: np.ndarray) -> np.ndarray:
    return v - (np.bincount(grupo, weights=w * v) / sw)[grupo]


# ----------------------------------------------------------------------------------------- #
# E3 — SAEB
# ----------------------------------------------------------------------------------------- #
def e3() -> list[dict]:
    linhas = []
    con = duckdb.connect()
    for serie, rot in SERIES.items():
        for disc in ("LP", "MT"):
            m = con.execute(f"""
                SELECT ID_ESCOLA AS escola, ESTRATO AS estrato, ID_UF AS uf, IN_PUBLICA AS publica,
                       ID_LOCALIZACAO AS localizacao, TX_RESP_Q04 AS q04,
                       CAST(PESO_ALUNO_{disc} AS DOUBLE) AS peso, CAST(PROFICIENCIA_{disc}_SAEB AS DOUBLE) AS prof,
                       TRY_CAST(INSE_ALUNO AS DOUBLE) AS inse
                FROM '{(PQ / f"saeb_2023_{serie}.parquet").as_posix()}' WHERE IN_PROFICIENCIA_{disc} = '1'""").df()
            n_lido = len(m)
            m = m[m["prof"].notna() & m["peso"].notna() & (m["peso"] > 0)].reset_index(drop=True)
            m["raca"] = m["q04"].map(SAEB_RACA).fillna("Não declarada")
            w, y = m["peso"].to_numpy(float), m["prof"].to_numpy(float)
            upa, est = m["escola"].to_numpy(), m["estrato"].to_numpy()
            mu = np.average(y, weights=w)
            dp = float(np.sqrt(np.average((y - mu) ** 2, weights=w)))
            raca = m["raca"].to_numpy(object)
            base = {"serie": rot, "disciplina": disc, "dp_serie": dp, "n_sem_proficiencia_ou_peso": n_lido - len(m)}
            for r in ["Branca", "Preta", "Parda", "Indígena", "Amarela", "Não declarada"]:
                d = raca == r
                z, mr = variancia.influencia_media(np.where(d, y, 0.0), w, d)
                linhas.append({**base, "raca": r, "especificacao": "média", "estimativa": float(mr),
                               "ep": ep_de(z, upa, est), "n": int(d.sum()),
                               "pct_alunos": float(100 * w[d].sum() / w.sum())})
            # regressões: Branca, Preta, Parda, Indígena com INSE válido (mesma amostra em todas as especificações)
            ok = np.isin(raca, ["Branca", "Preta", "Parda", "Indígena"]) & np.isfinite(m["inse"].to_numpy())
            sub = m[ok].reset_index(drop=True)
            ws, ys = sub["peso"].to_numpy(float), sub["prof"].to_numpy(float)
            us, es = sub["escola"].to_numpy(), sub["estrato"].to_numpy()
            rr = sub["raca"].to_numpy(object)
            inse = sub["inse"].to_numpy(float)
            for agrup, dums in (("Negra", {"Negra": np.isin(rr, ["Preta", "Parda"]), "Indígena": rr == "Indígena"}),
                                ("Preta/Parda", {"Preta": rr == "Preta", "Parda": rr == "Parda", "Indígena": rr == "Indígena"})):
                R = np.column_stack([v.astype(float) for v in dums.values()])
                nomes = list(dums)
                lugar = np.column_stack([sub["publica"].astype(str).eq("1").to_numpy(float),
                                         sub["localizacao"].astype(str).eq("1").to_numpy(float),
                                         _dummies(sub["uf"].astype(str))[0]])
                specs = {"bruto (amostra com INSE)": np.column_stack([np.ones(len(sub)), R]),
                         "+ INSE": np.column_stack([np.ones(len(sub)), R, inse, inse ** 2]),
                         "+ INSE, rede, localização, UF": np.column_stack([np.ones(len(sub)), R, inse, inse ** 2, lugar])}
                res = {k: _coefs(ys, X, ws, us, es, nomes) for k, X in specs.items()}
                # dentro da escola (efeitos fixos por desvio da média ponderada da escola)
                g = pd.factorize(sub["escola"])[0]
                sw = np.bincount(g, weights=ws)
                Xd = np.column_stack([_desviar(c, g, ws, sw) for c in np.column_stack([R, inse, inse ** 2]).T])
                res["+ INSE, dentro da escola"] = _coefs(_desviar(ys, g, ws, sw), Xd, ws, us, es, nomes, primeiro=0)
                for esp, coefs in res.items():
                    for r, (c, psi) in coefs.items():
                        linhas.append({**base, "raca": f"Branca − {r}", "agrupamento": agrup, "especificacao": esp,
                                       "estimativa": -c, "ep": ep_de(psi, us, es), "estimativa_dp": -c / dp,
                                       "ep_dp": ep_de(psi, us, es) / dp, "n": int(dums[r].sum())})
                if agrup == "Negra":
                    for num, den, nome in (("+ INSE", "bruto (amostra com INSE)", "razão + INSE ÷ bruto"),
                                           ("+ INSE, dentro da escola", "+ INSE", "razão dentro da escola ÷ + INSE")):
                        a, pa = res[num]["Negra"]
                        b, pb = res[den]["Negra"]
                        psi = pa / b - a * pb / b ** 2
                        linhas.append({**base, "raca": "Branca − Negra", "agrupamento": agrup, "especificacao": nome,
                                       "estimativa": a / b, "ep": ep_de(psi, us, es)})
                else:
                    for esp in ("bruto (amostra com INSE)", "+ INSE"):
                        a, pa = res[esp]["Preta"]
                        b, pb = res[esp]["Parda"]
                        linhas.append({**base, "raca": "Preta − Parda (desvantagem adicional de pretos)",
                                       "agrupamento": agrup, "especificacao": esp, "estimativa": -(a - b),
                                       "ep": ep_de(pa - pb, us, es), "estimativa_dp": -(a - b) / dp})
            print(f"E3 {serie} {disc}: {len(m):,} alunos, {len(sub):,} com INSE".replace(",", "."), flush=True)
    df = _ic(pd.DataFrame(linhas))
    # crescimento entre etapas (diferença em DP; EP somando as variâncias — conservador)
    cres = []
    for disc in ("LP", "MT"):
        for esp in ("bruto (amostra com INSE)", "+ INSE", "+ INSE, dentro da escola"):
            x = df[(df["disciplina"] == disc) & (df["raca"] == "Branca − Negra") & (df["especificacao"] == esp)].set_index("serie")
            for a, b in (("9º ano EF", "5º ano EF"), ("3ª/4ª série EM", "9º ano EF")):
                cres.append({"serie": f"{a} − {b}", "disciplina": disc, "raca": "Branca − Negra", "especificacao": esp,
                             "estimativa": x.loc[a, "estimativa_dp"] - x.loc[b, "estimativa_dp"],
                             "ep": float(np.hypot(x.loc[a, "ep_dp"], x.loc[b, "ep_dp"])), "unidade": "DP"})
    return pd.concat([df, _ic(pd.DataFrame(cres))], ignore_index=True)


# ----------------------------------------------------------------------------------------- #
# E6 — Censo da Educação Superior
# ----------------------------------------------------------------------------------------- #
def _composicao(g: pd.DataFrame, chaves: dict) -> list[dict]:
    out = []
    for k, rot in (("ING", "ingressantes"), ("MAT", "matriculados"), ("CONC", "concluintes")):
        tot = g[f"QT_{k}"].sum()
        nd = g[f"QT_{k}_CORND"].sum()
        dec = tot - nd
        neg = g[f"QT_{k}_PRETA"].sum() + g[f"QT_{k}_PARDA"].sum()
        bra = g[f"QT_{k}_BRANCA"].sum()
        ind = g[f"QT_{k}_INDIGENA"].sum()
        out.append({**chaves, "fluxo": rot, "total": int(tot), "pct_nao_declarada": 100 * nd / tot if tot else np.nan,
                    "pct_negra_entre_declarados": 100 * neg / dec if dec else np.nan,
                    "pct_branca_entre_declarados": 100 * bra / dec if dec else np.nan,
                    "pct_indigena_entre_declarados": 100 * ind / dec if dec else np.nan,
                    "pct_negra_limite_inferior": 100 * neg / tot if tot else np.nan,
                    "pct_negra_limite_superior": 100 * (neg + nd) / tot if tot else np.nan})
    return out


def e6() -> pd.DataFrame:
    linhas = []
    for ano in (2014, 2023):
        d = pd.read_parquet(PQ / f"censo_superior_{ano}.parquet")
        d = d[d["TP_NIVEL_ACADEMICO"] == "1"].copy()
        for c in [c for c in d.columns if c.startswith("QT_")]:
            d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
        cat = d["TP_CATEGORIA_ADMINISTRATIVA"].map({"1": "Pública federal", "2": "Pública estadual", "3": "Pública municipal"}).fillna("Privada")
        mod = d["TP_MODALIDADE_ENSINO"].map({"1": "presencial", "2": "a distância"})
        d = d.assign(categoria=cat, modalidade=mod, curso=d["NO_CURSO"].str.upper().fillna(""))
        linhas += _composicao(d, {"ano": ano, "recorte": "Total", "grupo": "Total"})
        for (c_, m_), g in d.groupby(["categoria", "modalidade"]):
            linhas += _composicao(g, {"ano": ano, "recorte": "categoria × modalidade", "grupo": f"{c_} · {m_}"})
        for a, g in d.groupby("NO_CINE_AREA_GERAL"):
            linhas += _composicao(g, {"ano": ano, "recorte": "área geral (CINE)", "grupo": a})
        cursos = {"Medicina": d["curso"].str.contains("MEDICINA") & ~d["curso"].str.contains("VETERIN"),
                  "Direito": d["curso"].str.contains("DIREITO"), "Engenharias": d["curso"].str.contains("ENGENHARIA")}
        for nome, sel in cursos.items():
            linhas += _composicao(d[sel], {"ano": ano, "recorte": "curso (palavra-chave)", "grupo": nome})
        for c_, g in d.groupby("categoria"):
            ing = g["QT_ING"].sum()
            linhas.append({"ano": ano, "recorte": "reserva de vagas", "grupo": c_, "fluxo": "ingressantes", "total": int(ing),
                           "pct_reserva_vagas": 100 * g["QT_ING_RESERVA_VAGA"].sum() / ing,
                           "pct_reserva_etnica": 100 * g["QT_ING_RVETNICO"].sum() / ing})
        for rec, gg in (("Total", d), ("Pública federal", d[d["categoria"] == "Pública federal"]), ("Privada", d[d["categoria"] == "Privada"])):
            for r, cols in (("Branca", ["BRANCA"]), ("Negra", ["PRETA", "PARDA"]), ("Indígena", ["INDIGENA"])):
                ing = sum(gg[f"QT_ING_{c}"].sum() for c in cols)
                conc = sum(gg[f"QT_CONC_{c}"].sum() for c in cols)
                linhas.append({"ano": ano, "recorte": "razão concluintes ÷ ingressantes", "grupo": rec, "fluxo": r,
                               "total": int(ing), "razao_conc_ing": conc / ing if ing else np.nan})
        print(f"E6 {ano}", flush=True)
    return pd.DataFrame(linhas)


# ----------------------------------------------------------------------------------------- #
# E7 — Censo Escolar
# ----------------------------------------------------------------------------------------- #
def _theil_entre_dentro(b: np.ndarray, n: np.ndarray, grupo: np.ndarray) -> dict:
    def ent(p):
        p = np.clip(p, 1e-15, 1 - 1e-15)
        return -(p * np.log(p) + (1 - p) * np.log(1 - p))
    t = b + n
    T, N = t.sum(), n.sum()
    E = ent(N / T)
    H_total = float(np.sum(t / T * (E - ent(n / np.where(t > 0, t, 1)))) / E)
    gb = pd.DataFrame({"g": grupo, "b": b, "n": n}).groupby("g")[["b", "n"]].sum()
    tg = gb["b"] + gb["n"]
    H_entre = float(np.sum(tg / T * (E - ent(gb["n"] / tg))) / E)
    return {"H_total": H_total, "H_entre_municipios": H_entre, "H_dentro_municipios": H_total - H_entre,
            "pct_entre": 100 * H_entre / H_total}


def e7() -> pd.DataFrame:
    d = pd.read_parquet(PQ / "censo_escolar_2024.parquet")
    d = d[d["TP_SITUACAO_FUNCIONAMENTO"] == "1"].copy()
    for c in [c for c in d.columns if c.startswith("QT_")]:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    d = d[d["QT_MAT_BAS"] > 0].copy()
    d["b"] = d["QT_MAT_BAS_BRANCA"]
    d["n"] = d["QT_MAT_BAS_PRETA"] + d["QT_MAT_BAS_PARDA"]
    d["publica"] = d["TP_DEPENDENCIA"].isin(["1", "2", "3"])
    d["pct_nd"] = d["QT_MAT_BAS_ND"] / d["QT_MAT_BAS"]
    linhas = []
    for amostra, x in (("todas as escolas", d), ("escolas com ≤ 50% sem cor/raça", d[d["pct_nd"] <= 0.5]),
                       ("rede pública", d[d["publica"]]), ("rede privada", d[~d["publica"]])):
        x = x[(x["b"] + x["n"]) > 0]
        bb, nn = x["b"].to_numpy(float), x["n"].to_numpy(float)
        D = 0.5 * np.abs(bb / bb.sum() - nn / nn.sum()).sum()
        th = _theil_entre_dentro(bb, nn, x["CO_MUNICIPIO"].to_numpy())
        # Duncan médio dentro dos municípios (ponderado pelas matrículas negras)
        dm = []
        for _, g in x.groupby("CO_MUNICIPIO"):
            if g["b"].sum() > 0 and g["n"].sum() > 0:
                dm.append((0.5 * np.abs(g["b"] / g["b"].sum() - g["n"] / g["n"].sum()).sum(), g["n"].sum()))
        dm = np.array(dm)
        linhas.append({"amostra": amostra, "indicador": "segregação entre escolas", "escolas": int(len(x)),
                       "matriculas": float(x["QT_MAT_BAS"].sum()), "pct_sem_cor_raca": 100 * x["QT_MAT_BAS_ND"].sum() / x["QT_MAT_BAS"].sum(),
                       "duncan_D_nacional": float(D), "duncan_D_medio_municipios": float(np.average(dm[:, 0], weights=dm[:, 1])), **th})
        for col, rot in INFRA.items():
            v = pd.to_numeric(x[col], errors="coerce")
            ok = v.notna()
            xb, xn, vv = x.loc[ok, "b"], x.loc[ok, "n"], v[ok]
            pb = 100 * (xb * vv).sum() / xb.sum()
            pn = 100 * (xn * vv).sum() / xn.sum()
            dif = []
            for _, g in x[ok].assign(v=vv).groupby("CO_MUNICIPIO"):
                if g["b"].sum() > 0 and g["n"].sum() > 0:
                    dif.append((100 * (g["b"] * g["v"]).sum() / g["b"].sum() - 100 * (g["n"] * g["v"]).sum() / g["n"].sum(), g["n"].sum()))
            dif = np.array(dif)
            linhas.append({"amostra": amostra, "indicador": rot, "pct_matriculas_brancas": float(pb), "pct_matriculas_negras": float(pn),
                           "diferenca_bruta_pp": float(pb - pn),
                           "diferenca_dentro_do_municipio_pp": float(np.average(dif[:, 0], weights=dif[:, 1]))})
        print(f"E7 {amostra}", flush=True)
    return pd.DataFrame(linhas)


# ----------------------------------------------------------------------------------------- #
# H3.2 — POF
# ----------------------------------------------------------------------------------------- #
def h32() -> pd.DataFrame:
    m = pd.read_parquet(PQ / "pof_morador.parquet")
    inv = pd.read_parquet(PQ / "pof_inventario.parquet")
    chave = ["COD_UPA", "NUM_DOM", "NUM_UC"]
    inv = inv[inv["V9001"].isin(BENS) & (pd.to_numeric(inv["V9005"], errors="coerce").fillna(0) > 0)]
    tem = inv.assign(v=1).pivot_table(index=chave, columns="V9001", values="v", aggfunc="max", fill_value=0).reset_index()
    m = m.merge(tem, on=chave, how="left")
    for c in BENS:
        m[c] = m.get(c, 0)
        m[c] = m[c].fillna(0)
    m["raca"] = m["V0405"].map({"1": "Branca", "2": "Negra", "4": "Negra", "5": "Indígena"})
    m = m[m["raca"].notna()].reset_index(drop=True)
    w = pd.to_numeric(m["PESO_FINAL"]).to_numpy(float)
    upa, est = m["COD_UPA"].to_numpy(), m["ESTRATO_POF"].to_numpy()
    renda = pd.to_numeric(m["RENDA_DISP_PC"], errors="coerce").fillna(0).to_numpy(float)
    cortes = np.quantile(renda, np.arange(1, 10) / 10, method="inverted_cdf", weights=w)
    decimo = np.searchsorted(cortes, renda, side="left").astype(str)
    raca = m["raca"].to_numpy(object)
    R = np.column_stack([(raca == r).astype(float) for r in ("Negra", "Indígena")])
    ctrl = np.column_stack([_dummies(pd.Series(decimo))[0], _dummies(m["UF"])[0], (m["TIPO_SITUACAO_REG"] == "2").to_numpy(float)])
    linhas = []
    indicadores = {nome: 100.0 * m[c].to_numpy(float) for c, nome in BENS.items()}
    indicadores["Número de bens (dos 7)"] = sum(m[c].to_numpy(float) for c in BENS)
    for nome, y in indicadores.items():
        for r in ("Branca", "Negra", "Indígena"):
            d = raca == r
            z, mu = variancia.influencia_media(np.where(d, y, 0.0), w, d)
            linhas.append({"indicador": nome, "raca": r, "medida": "% (ou média)", "estimativa": float(mu),
                           "ep": ep_de(z, upa, est), "n": int(d.sum())})
        for esp, X in (("diferença bruta", np.column_stack([np.ones(len(m)), R])),
                       ("diferença no mesmo décimo de renda disponível per capita, UF e situação", np.column_stack([np.ones(len(m)), R, ctrl]))):
            for r, (c, psi) in _coefs(y, X, w, upa, est, ["Negra", "Indígena"]).items():
                linhas.append({"indicador": nome, "raca": f"{r} − Branca", "medida": esp, "estimativa": c, "ep": ep_de(psi, upa, est)})
    df = _ic(pd.DataFrame(linhas))
    df["p_valor"] = np.where(df["medida"].str.startswith("diferença"), 2 * stats.norm.sf(np.abs(df["estimativa"] / df["ep"])), np.nan)
    return multiplicidade.adicionar_fdr(df, ["raca", "medida"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--so", nargs="*", default=None, help="e3 e6 e7 h32")
    fazer = set(parser.parse_args().so or ["e3", "e6", "e7", "h32"])
    if "e6" in fazer:
        salvar_tabela(e6(), OUTPUT_DIR / "e6_superior_composicao.parquet", se_metodo="sem_inferencia",
                      nota="Contagens do censo; % negra entre declarados e limites (não declarados como não negros / negros)")
    if "e7" in fazer:
        salvar_tabela(e7(), OUTPUT_DIR / "e7_escolas_segregacao.parquet", se_metodo="sem_inferencia",
                      nota="Matrículas da educação básica; Negra = preta + parda; diferenças em p.p. de matrículas")
    if "h32" in fazer:
        salvar_tabela(h32(), OUTPUT_DIR / "h32_pof_bens.parquet", se_metodo="wls_influencia_linearizacao_estrato_upa",
                      familia_fdr=["raca", "medida"], nota="% de pessoas em UC com o bem; MQO linear; décimos de RENDA_DISP_PC")
    if "e3" in fazer:
        df = e3()
        df["p_valor"] = np.where(df["raca"].str.startswith("Branca −") & ~df["especificacao"].str.startswith("razão"),
                                 2 * stats.norm.sf(np.abs(df["estimativa"] / df["ep"])), np.nan)
        df = multiplicidade.adicionar_fdr(df, ["serie", "disciplina", "especificacao"])
        salvar_tabela(df, OUTPUT_DIR / "e3_saeb_proficiencia.parquet", se_metodo="wls_influencia_linearizacao_estrato_escola",
                      familia_fdr=["serie", "disciplina", "especificacao"],
                      nota="Proficiência na escala SAEB; diferenças Branca − grupo em pontos e em DP da série; escola = conglomerado")


if __name__ == "__main__":
    main()
