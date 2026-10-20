"""Onda 6 — integração (fichas `docs/studies/{D4.4,I1,H3.4,H4.2}`).

- **D4.4** — segregação residencial Branca × Negra entre setores censitários (Censo 2022, universo): Duncan nacional e
  dentro do município, Theil H entre/dentro de municípios, isolamento, renda média do responsável no setor
  experimentada por cada grupo, e linha de base aleatória (composição do município nos mesmos setores).
- **I1** — Censo 2022 (amostra, acesso público) × PNADC 2022T3: composição racial de 20+ e hiato de renda de todos os
  trabalhos entre ocupados de 20+, Brasil e UF (o arquivo público do Censo só traz a idade em faixas de 5 anos).
- **H3.4** — riqueza imobiliária (moradia própria) pela POF 2017–2018: aluguel estimado × 12 ÷ *cap rate*, por pessoa.
- **H4.2** — transições trimestrais no painel de 5 visitas da PNADC (ligação por UPA, domicílio, grupo de rotação,
  ordem, sexo e data de nascimento).

Uso:
    python -m src.processing.bloco_integracao [--so d44 i1 h34 h42]
"""
from __future__ import annotations

import argparse
import zipfile

import duckdb
import numpy as np
import pandas as pd
from scipy import stats

from src.inference import multiplicidade, tendencia, variancia
from src.inference.saida import salvar_tabela
from src.ingestion.censo_2022 import PESSOAS, SETORES
from src.ingestion.externos_educacao import DESTINO as PQ
from src.ingestion.externos_educacao import EXT
from src.processing.agregacoes_pnadc import OUTPUT_DIR, PARQUET_GLOB
from src.processing.bloco_d import Sistema, _dummies, ep_de
from src.processing.bloco_eh_externos import _theil_entre_dentro

Z95 = 1.959963984540054
SEMENTE = 20261020

# ========================================================================================================= #
# comum
# ========================================================================================================= #
def var_conglomerados(z: np.ndarray, cl: np.ndarray, est: np.ndarray) -> float:
    """Variância linearizada de Σz com conglomerados `cl` (inteiros) aninhados em estratos `est` (inteiros)."""
    cl_cod, cl_uni = pd.factorize(cl)
    tot = np.bincount(cl_cod, weights=z)
    est_cl = np.zeros(len(cl_uni), dtype=np.int64)
    est_cl[cl_cod] = est
    h_cod, _ = pd.factorize(est_cl)
    n_h = np.bincount(h_cod)
    med = np.bincount(h_cod, weights=tot) / n_h
    dev = tot - med[h_cod]
    fator = np.where(n_h[h_cod] > 1, n_h[h_cod] / np.maximum(n_h[h_cod] - 1, 1), 1.0)
    return float(np.sum(fator * dev ** 2))


def _media_z(y: np.ndarray, w: np.ndarray, d: np.ndarray) -> tuple[np.ndarray, float]:
    return variancia.influencia_media(np.where(d, y, 0.0), w, d)


# ========================================================================================================= #
# D4.4 — segregação residencial
# ========================================================================================================= #
CAPITAIS = {11: "Porto Velho", 12: "Rio Branco", 13: "Manaus", 14: "Boa Vista", 15: "Belém", 16: "Macapá",
            17: "Palmas", 21: "São Luís", 22: "Teresina", 23: "Fortaleza", 24: "Natal", 25: "João Pessoa",
            26: "Recife", 27: "Maceió", 28: "Aracaju", 29: "Salvador", 31: "Belo Horizonte", 32: "Vitória",
            33: "Rio de Janeiro", 35: "São Paulo", 41: "Curitiba", 42: "Florianópolis", 43: "Porto Alegre",
            50: "Campo Grande", 51: "Cuiabá", 52: "Goiânia", 53: "Brasília"}
N_ALEATORIO = 200


def duncan(b: np.ndarray, n: np.ndarray) -> float:
    return float(0.5 * np.abs(b / b.sum() - n / n.sum()).sum())


def duncan_dentro(b: np.ndarray, n: np.ndarray, mun: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    """D de cada município (só os que têm os dois grupos) e a média ponderada pela população dos dois grupos."""
    bm, nm = np.bincount(mun, weights=b), np.bincount(mun, weights=n)
    ok_m = (bm > 0) & (nm > 0)
    ok = ok_m[mun]
    parc = np.where(ok, 0.5 * np.abs(b / np.where(ok, bm[mun], 1) - n / np.where(ok, nm[mun], 1)), 0.0)
    dm = np.bincount(mun, weights=parc)
    peso = np.where(ok_m, bm + nm, 0.0)
    return float(np.sum(dm * peso) / peso.sum()), dm, peso


def isolamento(b: np.ndarray, n: np.ndarray) -> tuple[float, float]:
    t = b + n
    ok = t > 0
    nn = float(np.sum(n[ok] / n.sum() * n[ok] / t[ok]))
    nb = float(np.sum(n[ok] / n.sum() * b[ok] / t[ok]))
    return nn, nb


def renda_bairro(b: np.ndarray, n: np.ndarray, r: np.ndarray, mun: np.ndarray) -> tuple[float, float, float, float]:
    """(R_b, R_n, R_b/R_n − 1 em %, média ponderada das razões municipais − 1 em %)."""
    ok = np.isfinite(r) & (r > 0)
    b, n, r, mun = b[ok], n[ok], r[ok], mun[ok]
    rb, rn = np.sum(b * r) / b.sum(), np.sum(n * r) / n.sum()
    sb, sn = np.bincount(mun, weights=b * r), np.bincount(mun, weights=n * r)
    bm, nm = np.bincount(mun, weights=b), np.bincount(mun, weights=n)
    okm = (bm > 0) & (nm > 0)
    razao_m = np.where(okm, (sb / np.where(okm, bm, 1)) / np.where(okm & (sn > 0), sn / np.where(okm, nm, 1), np.nan), np.nan)
    peso = np.where(okm & np.isfinite(razao_m), bm + nm, 0.0)
    dentro = float(np.nansum(np.where(peso > 0, razao_m, 0) * peso) / peso.sum())
    return float(rb), float(rn), float(100 * (rb / rn - 1)), float(100 * (dentro - 1))


def linha_base(b: np.ndarray, n: np.ndarray, mun: np.ndarray, reps: int = N_ALEATORIO, semente: int = SEMENTE
               ) -> tuple[float, float]:
    """D nacional e D dentro do município esperados se cada setor tivesse a composição do seu município."""
    rng = np.random.default_rng(semente)
    t = (b + n).astype(np.int64)
    p = np.bincount(mun, weights=n) / np.maximum(np.bincount(mun, weights=b + n), 1)
    dn, dd = [], []
    for _ in range(reps):
        ns = rng.binomial(t, p[mun]).astype(float)
        bs = t - ns
        dn.append(duncan(bs, ns))
        dd.append(duncan_dentro(bs, ns, mun)[0])
    return float(np.mean(dn)), float(np.mean(dd))


def d44() -> pd.DataFrame:
    s = pd.read_parquet(SETORES)
    s["cd_uf"] = s["CD_UF"].astype(int)
    pop_mun = s.groupby("CD_MUN")["pessoas"].transform("sum")
    cap = s.apply(lambda r: CAPITAIS.get(r["cd_uf"]) == r["NM_MUN"], axis=1)
    if cap.groupby(s["CD_MUN"]).any().sum() != 27:
        raise ValueError("capitais não identificadas pelas 27 UFs")
    s["porte"] = np.select([cap, pop_mun >= 500_000, pop_mun >= 100_000], ["capitais", "≥ 500 mil (não capital)",
                                                                           "100–500 mil"], "< 100 mil")
    s["n_setores_mun"] = s.groupby("CD_MUN")["CD_SETOR"].transform("count")
    valido = s[["branca", "preta", "parda"]].notna().all(axis=1)
    linhas = [{"amostra": "todos os setores", "comparacao": "—", "recorte": "Brasil", "medida": "setores com contagem suprimida (sigilo)",
               "valor": float((~valido).sum()), "pessoas_nos_suprimidos": float(s.loc[~valido, "pessoas"].sum())}]
    s = s[valido].copy()
    s["negra"] = s["preta"] + s["parda"]
    amostras = {"todos os setores": s, "só setores urbanos": s[s["SITUACAO"].str.startswith("Urb")],
                "municípios com ≥ 20 setores": s[s["n_setores_mun"] >= 20]}
    for nome_a, a in amostras.items():
        comps = [("Branca × Negra", "negra")] + ([("Branca × Preta", "preta"), ("Branca × Parda", "parda")]
                                                 if nome_a == "todos os setores" else [])
        for nome_c, col in comps:
            b, n = a["branca"].to_numpy(float), a[col].to_numpy(float)
            mun = pd.factorize(a["CD_MUN"])[0]
            base = {"amostra": nome_a, "comparacao": nome_c, "n_setores": len(a), "n_municipios": int(mun.max()) + 1}
            dn = duncan(b, n)
            dd, dm, peso = duncan_dentro(b, n, mun)
            al_n, al_d = linha_base(b, n, mun)
            th = _theil_entre_dentro(b, n, mun)
            nn, nb = isolamento(b, n)
            rb, rn, razao, razao_d = renda_bairro(b, n, a["renda_media_resp"].to_numpy(float), mun)
            for rec, med, v, al in (("Brasil", "Duncan D (setores)", dn, al_n),
                                    ("Brasil", "Duncan D dentro do município (média ponderada)", dd, al_d),
                                    ("Brasil", "Theil H total", th["H_total"], np.nan),
                                    ("Brasil", "Theil H entre municípios", th["H_entre_municipios"], np.nan),
                                    ("Brasil", "Theil H dentro dos municípios", th["H_dentro_municipios"], np.nan),
                                    ("Brasil", "% do H entre municípios", th["pct_entre"], np.nan),
                                    ("Brasil", "isolamento: % do grupo 2 no setor da pessoa média do grupo 2", 100 * nn, np.nan),
                                    ("Brasil", "exposição: % de brancos no setor da pessoa média do grupo 2", 100 * nb, np.nan),
                                    ("Brasil", "renda média do responsável no setor — pessoa branca (R$)", rb, np.nan),
                                    ("Brasil", "renda média do responsável no setor — pessoa do grupo 2 (R$)", rn, np.nan),
                                    ("Brasil", "renda do setor: branca ÷ grupo 2 − 1 (%)", razao, np.nan),
                                    ("Brasil", "renda do setor: branca ÷ grupo 2 − 1, dentro do município (%)", razao_d, np.nan)):
                linhas.append({**base, "recorte": rec, "medida": med, "valor": v, "valor_aleatorio": al,
                               "valor_menos_aleatorio": v - al if np.isfinite(al) else np.nan})
            if nome_a == "todos os setores" and nome_c == "Branca × Negra":
                porte_m = a.groupby("CD_MUN", sort=False)["porte"].first().reindex(pd.factorize(a["CD_MUN"])[1]).to_numpy()
                for p in ["capitais", "≥ 500 mil (não capital)", "100–500 mil", "< 100 mil"]:
                    m = porte_m == p
                    dmp = float(np.sum(dm[m] * peso[m]) / peso[m].sum())
                    sel = (a["porte"] == p).to_numpy()
                    _, _, rz, rzd = renda_bairro(b[sel], n[sel], a["renda_media_resp"].to_numpy(float)[sel],
                                                 pd.factorize(a["CD_MUN"][sel])[0])
                    _, ald = linha_base(b[sel], n[sel], pd.factorize(a["CD_MUN"][sel])[0], reps=50)
                    linhas += [{**base, "recorte": p, "medida": "Duncan D dentro do município (média ponderada)", "valor": dmp,
                                "valor_aleatorio": ald, "valor_menos_aleatorio": dmp - ald, "n_municipios": int(m.sum())},
                               {**base, "recorte": p, "medida": "renda do setor: branca ÷ grupo 2 − 1, dentro do município (%)",
                                "valor": rzd, "n_municipios": int(m.sum())}]
                top = (pd.DataFrame({"mun": pd.factorize(a["CD_MUN"])[1], "D": dm, "peso": peso})
                       .merge(a.groupby("CD_MUN")[["NM_MUN", "NM_UF"]].first(), left_on="mun", right_index=True)
                       .query("peso >= 1e6").sort_values("D", ascending=False))
                for _, r in top.iterrows():
                    linhas.append({**base, "recorte": f"{r['NM_MUN']} ({r['NM_UF']})", "medida": "Duncan D do município (≥ 1 mi de brancos + negros)",
                                   "valor": float(r["D"]), "n_municipios": 1})
            print(f"D4.4 {nome_a} {nome_c}: D = {dn:.3f}, dentro = {dd:.3f}", flush=True)
    return pd.DataFrame(linhas)


# ========================================================================================================= #
# I1 — Censo 2022 × PNADC 2022T3
# ========================================================================================================= #
RACAS_COD = {"Branca": [1], "Preta": [2], "Parda": [4], "Negra": [2, 4], "Indígena": [5], "Amarela": [3]}
COMPARA = [("Negra", "Branca × Negra"), ("Indígena", "Branca × Indígena"), ("Preta", "Branca × Preta"),
           ("Parda", "Branca × Parda")]


def _estatisticas(raca: np.ndarray, w: np.ndarray, renda: np.ndarray, na_renda: np.ndarray, cl: np.ndarray,
                  est: np.ndarray) -> list[dict]:
    """Composição de 20+ (todas as linhas) e hiato entre `na_renda`; EP linearizado por conglomerado/estrato."""
    out = []
    for g, cods in RACAS_COD.items():
        z, m = _media_z(np.isin(raca, cods).astype(float) * 100, w, np.ones(len(w), bool))
        out.append({"bloco": "composição 20+", "medida": f"% {g}", "estimativa": m, "ep": np.sqrt(var_conglomerados(z, cl, est))})
    y, ly = renda, np.log(np.where(renda > 0, renda, 1.0))
    zs, ms, zl, ml = {}, {}, {}, {}
    for g, cods in RACAS_COD.items():
        d = na_renda & np.isin(raca, cods)
        zs[g], ms[g] = _media_z(y, w, d)
        zl[g], ml[g] = _media_z(ly, w, d)
        out.append({"bloco": "renda", "medida": f"renda média — {g} (R$)", "estimativa": ms[g],
                    "ep": np.sqrt(var_conglomerados(zs[g], cl, est)), "n": int(d.sum())})
    for g, rot in COMPARA:
        r = ms["Branca"] / ms[g]
        z = (zs["Branca"] - r * zs[g]) / ms[g]
        out.append({"bloco": "hiato", "medida": f"{rot}: razão das médias − 1 (%)", "estimativa": 100 * (r - 1),
                    "ep": 100 * np.sqrt(var_conglomerados(z, cl, est))})
        out.append({"bloco": "hiato", "medida": f"{rot}: diferença de médias de ln (lp)", "estimativa": ml["Branca"] - ml[g],
                    "ep": np.sqrt(var_conglomerados(zl["Branca"] - zl[g], cl, est))})
    return out


def _censo_i1() -> pd.DataFrame:
    con = duckdb.connect()
    return con.execute(f"""
        SELECT CAST(P0020 AS TINYINT) AS uf, CAST(P0100 AS BIGINT) AS dom, CAST(P0110 AS DOUBLE) AS w,
               CAST(P0210 AS TINYINT) AS raca, (P0950 = '1' AND TRY_CAST(P1080 AS DOUBLE) > 0) AS ocup_renda,
               CAST(TRY_CAST(P1080 AS DOUBLE) AS FLOAT) AS renda, (MP1080 = '0') AS nao_imputado
        FROM read_parquet('{(PESSOAS / '*.parquet').as_posix()}')
        WHERE P0130 IN ('01', '05') AND P0180 BETWEEN '05' AND '17' AND P0210 IN ('1','2','3','4','5')""").df()


def _pnadc_i1() -> pd.DataFrame:
    con = duckdb.connect()
    return con.execute(f"""
        SELECT CAST(UF AS INTEGER) AS uf, CAST(UPA AS BIGINT) AS dom, CAST(Estrato AS BIGINT) AS estrato,
               CAST(V1028 AS DOUBLE) AS w, CAST(V2010 AS TINYINT) AS raca, (VD4002 = '1' AND VD4019 > 0) AS ocup_renda,
               CAST(VD4019 AS DOUBLE) AS renda
        FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1)
        WHERE ano = 2022 AND trimestre = 3 AND V2009 >= 20 AND V2010 IN ('1','2','3','4','5')""").df()


def _p999(renda: np.ndarray, w: np.ndarray, m: np.ndarray) -> float:
    return float(np.quantile(renda[m], 0.999, method="inverted_cdf", weights=w[m]))


def i1() -> pd.DataFrame:
    fontes = {"Censo 2022": _censo_i1(), "PNADC 2022T3": _pnadc_i1()}
    linhas = []
    for fonte, df in fontes.items():
        cl = (df["uf"].to_numpy(np.int64) * 10_000_000_000 + df["dom"].to_numpy(np.int64)) if fonte.startswith("Censo") \
            else df["dom"].to_numpy(np.int64)
        est = df["uf"].to_numpy(np.int64) if fonte.startswith("Censo") else df["estrato"].to_numpy(np.int64)
        raca, w = df["raca"].to_numpy(np.int8), df["w"].to_numpy(float)
        renda = np.nan_to_num(df["renda"].to_numpy(float))
        ok = df["ocup_renda"].fillna(False).to_numpy(bool)
        especs = {"principal": ok, "renda até o P99,9": ok & (renda <= _p999(renda, w, ok))}
        if fonte.startswith("Censo"):
            especs["só renda não imputada"] = ok & df["nao_imputado"].fillna(False).to_numpy(bool)
        for esp, m in especs.items():
            for uf in [0] + sorted(df["uf"].unique()):
                s = np.ones(len(df), bool) if uf == 0 else (df["uf"].to_numpy() == uf)
                if esp != "principal" and uf != 0:
                    continue
                for r in _estatisticas(raca[s], w[s], renda[s], m[s], cl[s], est[s]):
                    if esp != "principal" and r["bloco"] == "composição 20+":
                        continue
                    linhas.append({"fonte": fonte, "especificacao": esp, "uf": int(uf) if uf else "Brasil", **r})
            print(f"I1 {fonte} {esp}: ok", flush=True)
    df = pd.DataFrame(linhas)
    df["ic_inferior"], df["ic_superior"] = df["estimativa"] - Z95 * df["ep"], df["estimativa"] + Z95 * df["ep"]
    c = df[df["fonte"] == "Censo 2022"].set_index(["especificacao", "uf", "bloco", "medida"])
    p = df[(df["fonte"] == "PNADC 2022T3")].set_index(["especificacao", "uf", "bloco", "medida"])
    comuns = c.index.intersection(p.index)
    dif = pd.DataFrame({"estimativa": c.loc[comuns, "estimativa"] - p.loc[comuns, "estimativa"],
                        "ep": np.sqrt(c.loc[comuns, "ep"] ** 2 + p.loc[comuns, "ep"] ** 2)}).reset_index()
    dif["fonte"] = "Censo − PNADC"
    dif["ic_inferior"], dif["ic_superior"] = dif["estimativa"] - Z95 * dif["ep"], dif["estimativa"] + Z95 * dif["ep"]
    dif["p_valor"] = 2 * stats.norm.sf(np.abs(dif["estimativa"] / dif["ep"]))
    dif.loc[dif["especificacao"] != "principal", "p_valor"] = np.nan
    dif = multiplicidade.adicionar_fdr(dif, None)
    out = pd.concat([df, dif], ignore_index=True)
    for g, rot in COMPARA[:2]:
        med = f"{rot}: razão das médias − 1 (%)"
        x = out[(out["especificacao"] == "principal") & (out["medida"] == med) & (out["uf"] != "Brasil")]
        piv = x.pivot_table(index="uf", columns="fonte", values="estimativa")
        out = pd.concat([out, pd.DataFrame([{"fonte": "Censo × PNADC", "especificacao": "principal", "uf": "27 UFs",
                                             "bloco": "concordância", "medida": f"correlação entre UFs — {med}",
                                             "estimativa": float(piv["Censo 2022"].corr(piv["PNADC 2022T3"]))}])],
                        ignore_index=True)
    out["uf"] = out["uf"].astype(str)
    return out


# ========================================================================================================= #
# H3.4 — riqueza imobiliária (POF)
# ========================================================================================================= #
POF_ZIP = EXT / "pof_2017_18" / "Dados_20230713.zip"
DOM_W = [2, 4, 1, 9, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 14, 14, 1]
DOM_N = ["UF", "ESTRATO_POF", "TIPO_SITUACAO_REG", "COD_UPA", "NUM_DOM", "V0201", "V0202", "V0203", "V0204", "V0205",
         "V0206", "V0207", "V0208", "V0209", "V02101", "V02102", "V02103", "V02104", "V02105", "V02111", "V02112",
         "V02113", "V0212", "V0213", "V02141", "V02142", "V0215", "V02161", "V02162", "V02163", "V02164", "V0217",
         "V0219", "V0220", "V0221", "PESO", "PESO_FINAL", "V6199"]
ALU_W = [2, 4, 1, 9, 2, 1, 2, 7, 2, 10, 2, 2, 12, 10, 1, 2, 14, 14, 10]
ALU_N = ["UF", "ESTRATO_POF", "TIPO_SITUACAO_REG", "COD_UPA", "NUM_DOM", "NUM_UC", "QUADRO", "V9001", "V9002", "V8000",
         "V9010", "V9011", "DEFLATOR", "V8000_DEFLA", "COD_IMPUT_VALOR", "FATOR_ANUALIZACAO", "PESO", "PESO_FINAL",
         "RENDA_TOTAL"]
CAPS = {"4% a.a.": 0.04, "5% a.a.": 0.05, "6% a.a.": 0.06}


def _fwf(membro: str, larg: list[int], nomes: list[str]) -> pd.DataFrame:
    with zipfile.ZipFile(POF_ZIP) as z, z.open(membro) as fh:
        return pd.read_fwf(fh, widths=larg, names=nomes, dtype=str, encoding="latin-1")


def base_h34() -> pd.DataFrame:
    m = pd.read_parquet(PQ / "pof_morador.parquet")
    dom = _fwf("DOMICILIO.txt", DOM_W, DOM_N)[["COD_UPA", "NUM_DOM", "V0217"]]
    alu = _fwf("ALUGUEL_ESTIMADO.txt", ALU_W, ALU_N)
    alu["aluguel_mensal"] = pd.to_numeric(alu["V8000_DEFLA"], errors="coerce")
    alu = alu.groupby(["COD_UPA", "NUM_DOM"], as_index=False)["aluguel_mensal"].sum()
    chave = ["COD_UPA", "NUM_DOM"]
    m = m.merge(dom, on=chave, how="left").merge(alu, on=chave, how="left")
    m["moradores"] = m.groupby(chave)["COD_UPA"].transform("size")
    m["raca"] = m["V0405"].map({"1": "Branca", "2": "Negra", "4": "Negra", "5": "Indígena"})
    m["w"] = pd.to_numeric(m["PESO_FINAL"])
    m["renda_pc"] = pd.to_numeric(m["RENDA_DISP_PC"], errors="coerce").fillna(0)
    return m


def _cap_variavel(m: pd.DataFrame, propria: np.ndarray) -> np.ndarray:
    """6% no décimo inferior do aluguel estimado (entre domicílios próprios, pesos de domicílio) → 4% no superior."""
    d = m[propria].drop_duplicates(["COD_UPA", "NUM_DOM"])
    cortes = np.quantile(d["aluguel_mensal"], np.arange(1, 10) / 10, method="inverted_cdf", weights=d["w"])
    dec = np.searchsorted(cortes, m["aluguel_mensal"].fillna(0).to_numpy(), side="left")
    return 0.06 - 0.02 * dec / 9


def h34() -> pd.DataFrame:
    m0 = base_h34()
    linhas = []
    for esp, codigos in (("principal: própria já paga", ["1"]), ("própria, paga ou pagando (sem descontar dívida)", ["1", "2"])):
        m = m0[m0["raca"].notna()].reset_index(drop=True)
        propria = (m["V0217"].isin(codigos) & m["aluguel_mensal"].notna()).to_numpy()
        w, upa, est = m["w"].to_numpy(float), m["COD_UPA"].to_numpy(), m["ESTRATO_POF"].to_numpy()
        raca = m["raca"].to_numpy(object)
        anual = np.where(propria, 12 * m["aluguel_mensal"].fillna(0).to_numpy(float), 0.0) / m["moradores"].to_numpy(float)
        caps = {**{k: np.full(len(m), v) for k, v in CAPS.items()}, "variável (6% → 4%)": _cap_variavel(m, propria)}
        cortes = np.quantile(m["renda_pc"], np.arange(1, 10) / 10, method="inverted_cdf", weights=w)
        decimo = np.searchsorted(cortes, m["renda_pc"].to_numpy(), side="left").astype(str)
        R = np.column_stack([(raca == r).astype(float) for r in ("Negra", "Indígena")])
        ctrl = np.column_stack([_dummies(pd.Series(decimo))[0], _dummies(m["UF"])[0],
                                (m["TIPO_SITUACAO_REG"] == "2").to_numpy(float)])
        for nome_cap, cap in caps.items():
            y = anual / cap
            zs, ms = {}, {}
            for r in ("Branca", "Negra", "Indígena"):
                d = raca == r
                zs[r], ms[r] = _media_z(y, w, d)
                linhas.append({"especificacao": esp, "cap_rate": nome_cap, "raca": r, "medida": "riqueza imobiliária média por pessoa (R$ jan/2018)",
                               "estimativa": ms[r], "ep": ep_de(zs[r], upa, est), "n": int(d.sum())})
                if nome_cap == "5% a.a.":
                    med = float(np.quantile(y[d], 0.5, method="inverted_cdf", weights=w[d]))
                    linhas.append({"especificacao": esp, "cap_rate": nome_cap, "raca": r, "medida": "mediana por pessoa (R$ jan/2018)",
                                   "estimativa": med, "n": int(d.sum())})
                    zp, mp = _media_z(100 * propria.astype(float), w, d)
                    linhas.append({"especificacao": esp, "cap_rate": "—", "raca": r, "medida": "% em moradia própria (condição da especificação)",
                                   "estimativa": mp, "ep": ep_de(zp, upa, est), "n": int(d.sum())})
                    zr, mr = _media_z(m["renda_pc"].to_numpy(float), w, d)
                    linhas.append({"especificacao": esp, "cap_rate": "—", "raca": r, "medida": "renda disponível per capita média (R$ jan/2018)",
                                   "estimativa": mr, "ep": ep_de(zr, upa, est), "n": int(d.sum())})
                    if r != "Branca":
                        zb, mb = _media_z(m["renda_pc"].to_numpy(float), w, raca == "Branca")
                        linhas.append({"especificacao": esp, "cap_rate": "—", "raca": f"Branca ÷ {r}", "medida": "razão das rendas disponíveis per capita",
                                       "estimativa": mb / mr, "ep": variancia.razao_delta_design(zb, zr, mb, mr, upa, est)})
            for r in ("Negra", "Indígena"):
                razao = ms["Branca"] / ms[r]
                linhas.append({"especificacao": esp, "cap_rate": nome_cap, "raca": f"Branca ÷ {r}", "medida": "razão das riquezas imobiliárias médias",
                               "estimativa": razao, "ep": variancia.razao_delta_design(zs["Branca"], zs[r], ms["Branca"], ms[r], upa, est),
                               "p_valor": np.nan})
            for nome_x, X in (("diferença bruta (R$)", np.column_stack([np.ones(len(m)), R])),
                              ("diferença no mesmo décimo de renda disponível per capita, UF e situação (R$)",
                               np.column_stack([np.ones(len(m)), R, ctrl]))):
                s = Sistema(X, y, w)
                cols = np.arange(X.shape[1])
                b = s.beta(cols)
                e = s.residuo(b)
                Ginv = np.linalg.pinv(s.G)
                for j, r in ((1, "Negra"), (2, "Indígena")):
                    c = np.zeros(X.shape[1])
                    c[j] = 1
                    psi = (X @ (Ginv @ c)) * w * e
                    ep = ep_de(psi, upa, est)
                    linhas.append({"especificacao": esp, "cap_rate": nome_cap, "raca": f"{r} − Branca", "medida": nome_x,
                                   "estimativa": float(b[j]), "ep": ep, "p_valor": float(2 * stats.norm.sf(abs(b[j] / ep))),
                                   "pct_da_media_branca": float(100 * b[j] / ms["Branca"])})
    df = pd.DataFrame(linhas)
    df["ic_inferior"], df["ic_superior"] = df["estimativa"] - Z95 * df["ep"], df["estimativa"] + Z95 * df["ep"]
    fam = df["p_valor"].notna() & df["especificacao"].str.startswith("principal")
    df.loc[~fam, "p_valor"] = np.nan
    return multiplicidade.adicionar_fdr(df, ["cap_rate"])


# ========================================================================================================= #
# H4.2 — transições no painel
# ========================================================================================================= #
PARES = EXT.parent / "pnadc_pares_h42"
FAIXAS = [18, 25, 30, 35, 40, 45, 50, 55, 60, 65]
TRANS = {"T1 desocupado → ocupado": ("desocupado", ["com_carteira", "sem_carteira", "conta_propria", "outro_ocupado"]),
         "T2 sem carteira → com carteira": ("sem_carteira", ["com_carteira"]),
         "T3 com carteira → perda (sem carteira, conta própria ou desocupado)": ("com_carteira",
                                                                                ["sem_carteira", "conta_propria", "desocupado"])}

ESTADO_SQL = """CASE WHEN {a}.VD4002 = '2' THEN 'desocupado'
                     WHEN {a}.VD4009 = '01' THEN 'com_carteira'
                     WHEN {a}.VD4009 = '02' THEN 'sem_carteira'
                     WHEN {a}.VD4009 = '09' THEN 'conta_propria'
                     WHEN {a}.VD4002 = '1' THEN 'outro_ocupado' ELSE 'fora' END"""


def _sql_trimestre(a: int, tr: int) -> str:
    return f"""SELECT UF, Estrato, UPA, V1008, V1014, CAST(V1016 AS INTEGER) AS visita, V2003, V2007, V2008, V20081, V20082,
        V2009 AS idade, CASE V2010 WHEN '1' THEN 'Branca' WHEN '2' THEN 'Negra' WHEN '4' THEN 'Negra' WHEN '5' THEN 'Indígena'
        END AS raca, VD3004, V1028, {ESTADO_SQL.format(a='m')} AS estado
        FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1) m
        WHERE ano = {a} AND trimestre = {tr} AND V2010 IN ('1','2','4','5')"""


CEL_SQL = """CASE WHEN {i} < 30 THEN 1 WHEN {i} < 45 THEN 2 WHEN {i} < 60 THEN 3 ELSE 4 END AS fx,
             CASE WHEN {e} IN ('1','2','3') THEN 1 WHEN {e} IN ('4','5') THEN 2 ELSE 3 END AS ins,
             substr(CAST({u} AS VARCHAR), 1, 1) AS reg"""


def gerar_pares() -> pd.DataFrame:
    """Pares de trimestres consecutivos da mesma pessoa (18+ em t), um par de trimestres por vez (memória), gravados em
    `PARES/`; devolve o atrito por raça × ano e grava as células do ajuste de atrito."""
    con = duckdb.connect()
    con.execute("SET memory_limit = '3GB'")
    tri = con.execute(f"SELECT DISTINCT ano, trimestre FROM read_parquet('{PARQUET_GLOB}', hive_partitioning = 1) "
                      "ORDER BY ano, trimestre").fetchall()
    PARES.mkdir(parents=True, exist_ok=True)
    atr, cel, dups = [], [], 0
    for (a0, t0), (a1, t1) in zip(tri[:-1], tri[1:]):
        con.execute(f"CREATE OR REPLACE TABLE b0 AS {_sql_trimestre(a0, t0)}")
        con.execute(f"CREATE OR REPLACE TABLE b1 AS {_sql_trimestre(a1, t1)}")
        con.execute(f"""CREATE OR REPLACE TABLE p AS
            SELECT {a0} AS ano, {t0} AS trimestre, b0.UF AS uf, b0.Estrato AS estrato, b0.UPA AS upa, b0.V1028 AS w,
                   b0.raca, b0.V2007 AS sexo, b0.idade, b0.VD3004 AS instr, b0.estado AS estado0, b1.estado AS estado1,
                   b0.V1008, b0.V2003
            FROM b0 JOIN b1
              ON b0.UPA = b1.UPA AND b0.V1008 = b1.V1008 AND b0.V1014 = b1.V1014 AND b0.V2003 = b1.V2003
             AND b0.V2007 = b1.V2007 AND b1.visita = b0.visita + 1
             AND ((b0.V20082 <> '9999' AND b0.V2008 = b1.V2008 AND b0.V20081 = b1.V20081 AND b0.V20082 = b1.V20082)
                  OR (b0.V20082 = '9999' AND b1.idade - b0.idade BETWEEN 0 AND 1))
            WHERE b0.idade >= 18""")
        dups += con.execute("SELECT count(*) FROM (SELECT upa, V1008, V2003 FROM p GROUP BY ALL HAVING count(*) > 1)").fetchone()[0]
        con.execute("""CREATE OR REPLACE TABLE pu AS SELECT * EXCLUDE (V1008, V2003) FROM p
                       QUALIFY count(*) OVER (PARTITION BY upa, V1008, V2003) = 1""")
        con.execute(f"COPY pu TO '{(PARES / f'{a0}_{t0}.parquet').as_posix()}' (FORMAT parquet)")
        atr.append(con.execute(f"""
            SELECT {a0} AS ano, e.raca, e.w_eleg, e.n_eleg, a.w_ach, a.n_ach FROM
            (SELECT raca, sum(V1028) AS w_eleg, count(*) AS n_eleg FROM b0 WHERE idade >= 18 AND visita <= 4 GROUP BY ALL) e
            LEFT JOIN (SELECT raca, sum(w) AS w_ach, count(*) AS n_ach FROM pu GROUP BY ALL) a USING (raca)""").df())
        cel.append(con.execute(f"""
            SELECT {a0} AS ano, e.*, a.w_ach FROM
            (SELECT raca, V2007 AS sexo, {CEL_SQL.format(i='idade', e='VD3004', u='UF')}, estado, sum(V1028) AS w_eleg
             FROM b0 WHERE idade >= 18 AND visita <= 4 GROUP BY ALL) e
            LEFT JOIN (SELECT raca, sexo, {CEL_SQL.format(i='idade', e='instr', u='uf')}, estado0 AS estado, sum(w) AS w_ach
                       FROM pu GROUP BY ALL) a USING (raca, sexo, fx, ins, reg, estado)""").df())
        print(f"pares {a0}T{t0}→{a1}T{t1}: ok", flush=True)
    atr = pd.concat(atr).groupby(["ano", "raca"], as_index=False)[["w_eleg", "n_eleg", "w_ach", "n_ach"]].sum()
    atr["pct_encontrados"] = 100 * atr["w_ach"] / atr["w_eleg"]
    atr["pares_duplicados_descartados"] = int(dups)
    cel = pd.concat(cel).groupby(["ano", "raca", "sexo", "fx", "ins", "reg", "estado"], as_index=False)[["w_eleg", "w_ach"]].sum()
    cel.to_parquet(PARES / "_celulas.parquet", index=False)
    return atr


def _x_h42(d: pd.DataFrame, anos: list[int], ufs: list[str]) -> np.ndarray:
    idade = d["idade"].to_numpy()
    fx = np.searchsorted(FAIXAS, idade, side="right") - 1
    cols = [np.ones(len(d)), (d["raca"] == "Negra").to_numpy(float), (d["raca"] == "Indígena").to_numpy(float),
            (d["sexo"] == "2").to_numpy(float)]
    cols += [(fx == k).astype(float) for k in range(1, len(FAIXAS))]
    cols += [(d["instr"] == str(k)).to_numpy(float) for k in range(2, 8)]
    cols += [(d["uf"].astype(str) == u).to_numpy(float) for u in ufs[1:]]
    cols += [(d["ano"] == a).to_numpy(float) for a in anos[1:]]
    return np.column_stack(cols)


def h42() -> tuple[pd.DataFrame, pd.DataFrame]:
    atr = gerar_pares()
    con = duckdb.connect()
    cel = pd.read_parquet(PARES / "_celulas.parquet")
    cel["fator"] = cel["w_eleg"] / cel["w_ach"]
    con.register("cel", cel[["ano", "raca", "sexo", "fx", "ins", "reg", "estado", "fator"]])
    linhas = []
    for nome, (origem, destinos) in TRANS.items():
        d = con.execute(f"""
            SELECT p.*, c.fator FROM read_parquet('{(PARES / '[0-9]*.parquet').as_posix()}') p
            LEFT JOIN cel c ON c.ano = p.ano AND c.raca = p.raca AND c.sexo = p.sexo
              AND c.fx = CASE WHEN p.idade < 30 THEN 1 WHEN p.idade < 45 THEN 2 WHEN p.idade < 60 THEN 3 ELSE 4 END
              AND c.ins = CASE WHEN p.instr IN ('1','2','3') THEN 1 WHEN p.instr IN ('4','5') THEN 2 ELSE 3 END
              AND c.reg = substr(CAST(p.uf AS VARCHAR), 1, 1) AND c.estado = p.estado0
            WHERE p.estado0 = '{origem}'""").df()
        d["y"] = 100 * d["estado1"].isin(destinos).astype(float)
        upa = d["upa"].astype(str).to_numpy()
        est = d["estrato"].astype(str).to_numpy()
        raca = d["raca"].to_numpy(object)
        y = d["y"].to_numpy(float)
        for pesos in ("V1028 de t", "ajustado por atrito (células)"):
            w = d["w"].to_numpy(float) * (d["fator"].fillna(1.0).to_numpy(float) if pesos.startswith("ajust") else 1.0)
            for periodo, sel in [("2012–2026", np.ones(len(d), bool))] + (
                    [(str(a), (d["ano"] == a).to_numpy()) for a in sorted(d["ano"].unique())] if pesos == "V1028 de t" else []):
                zs, ms = {}, {}
                for r in ("Branca", "Negra", "Indígena"):
                    dm = sel & (raca == r)
                    zs[r], ms[r] = _media_z(y, w, dm)
                    linhas.append({"transicao": nome, "pesos": pesos, "periodo": periodo, "raca": r, "medida": "% que transita",
                                   "estimativa": ms[r], "ep": ep_de(zs[r], upa, est), "n": int(dm.sum())})
                for r in ("Negra", "Indígena"):
                    linhas.append({"transicao": nome, "pesos": pesos, "periodo": periodo, "raca": f"{r} − Branca",
                                   "medida": "diferença bruta (p.p.)", "estimativa": ms[r] - ms["Branca"],
                                   "ep": ep_de(zs[r] - zs["Branca"], upa, est)})
        # condicional (2012–2026), X'WX acumulado por ano
        anos = sorted(d["ano"].unique())
        ufs = sorted(d["uf"].astype(str).unique())
        w = d["w"].to_numpy(float)
        G, g = None, None
        for a in anos:
            m = (d["ano"] == a).to_numpy()
            X = _x_h42(d[m], anos, ufs)
            Xw = X * w[m][:, None]
            G = Xw.T @ X if G is None else G + Xw.T @ X
            g = Xw.T @ y[m] if g is None else g + Xw.T @ y[m]
        Ginv = np.linalg.pinv(G)
        b = Ginv @ g
        for j, r in ((1, "Negra"), (2, "Indígena")):
            c = np.zeros(len(b))
            c[j] = 1
            a_vec = Ginv @ c
            psi = np.empty(len(d))
            for a in anos:
                m = (d["ano"] == a).to_numpy()
                X = _x_h42(d[m], anos, ufs)
                psi[m] = (X @ a_vec) * w[m] * (y[m] - X @ b)
            linhas.append({"transicao": nome, "pesos": "V1028 de t", "periodo": "2012–2026", "raca": f"{r} − Branca",
                           "medida": "diferença com idade, sexo, instrução, UF e ano (p.p.)", "estimativa": float(b[j]),
                           "ep": ep_de(psi, upa, est)})
        print(f"H4.2 {nome}: {len(d):,} pares".replace(",", "."), flush=True)
    df = pd.DataFrame(linhas)
    df["ic_inferior"], df["ic_superior"] = df["estimativa"] - Z95 * df["ep"], df["estimativa"] + Z95 * df["ep"]
    fam = (df["periodo"] == "2012–2026") & (df["pesos"] == "V1028 de t") & df["raca"].str.contains("−")
    df["p_valor"] = np.where(fam, 2 * stats.norm.sf(np.abs(df["estimativa"] / df["ep"])), np.nan)
    df = multiplicidade.adicionar_fdr(df, None)
    # tendência e degraus da diferença anual Negra − Branca (EWC)
    tend = []
    for nome in TRANS:
        s = df[(df["transicao"] == nome) & (df["raca"] == "Negra − Branca") & (df["medida"] == "diferença bruta (p.p.)")
               & (df["pesos"] == "V1028 de t") & (df["periodo"] != "2012–2026")]
        anos = s["periodo"].astype(int).to_numpy()
        th = tendencia.tendencia_hac(anos.astype(float), s["estimativa"].to_numpy())
        tend.append({"transicao": nome, "medida": "tendência da diferença Negra − Branca (p.p. por ano)", **th})
        dg = tendencia.degraus_ewc(anos, np.ones(len(anos), int), s["estimativa"].to_numpy(),
                                   {"2015": (2015, 1), "2020": (2020, 1)})
        for _, r in dg.iterrows():
            tend.append({"transicao": nome, "medida": "degrau da diferença Negra − Branca (p.p.)", **r.to_dict()})
    tend = pd.DataFrame(tend)
    return df, pd.concat([atr.assign(tipo="atrito"), tend.assign(tipo="tendencia")], ignore_index=True)


# ========================================================================================================= #
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--so", nargs="*", default=None, help="d44 i1 h34 h42")
    fazer = set(parser.parse_args().so or ["d44", "i1", "h34", "h42"])
    if "d44" in fazer:
        salvar_tabela(d44(), OUTPUT_DIR / "d44_segregacao_residencial.parquet", se_metodo="sem_inferencia",
                      nota="Universo do Censo 2022 por setor; Negra = preta + parda; linha de base = composição do município")
    if "h34" in fazer:
        salvar_tabela(h34(), OUTPUT_DIR / "h34_riqueza_imobiliaria.parquet", se_metodo="wls_influencia_linearizacao_estrato_upa",
                      familia_fdr=["cap_rate"], nota="Aluguel estimado mensal (V8000_DEFLA, R$ jan/2018) × 12 ÷ cap rate; por pessoa do domicílio")
    if "i1" in fazer:
        salvar_tabela(i1(), OUTPUT_DIR / "i1_censo_pnadc.parquet", se_metodo="linearizacao_domicilio_uf_censo_e_estrato_upa_pnadc",
                      familia_fdr=None, nota="Censo: EP aproximado (domicílio como conglomerado, UF como estrato); renda de todos os trabalhos")
    if "h42" in fazer:
        df, extra = h42()
        salvar_tabela(df, OUTPUT_DIR / "h42_transicoes.parquet", se_metodo="linearizacao_estrato_upa",
                      familia_fdr=None, nota="Pares de trimestres consecutivos; ligação UPA+V1008+V1014+V2003+sexo+nascimento")
        salvar_tabela(extra, OUTPUT_DIR / "h42_atrito_tendencia.parquet", se_metodo="ewc_e_sem_inferencia",
                      nota="Atrito = % dos elegíveis (visita ≤ 4) encontrados na visita seguinte; tendência EWC da diferença anual")


if __name__ == "__main__":
    main()
