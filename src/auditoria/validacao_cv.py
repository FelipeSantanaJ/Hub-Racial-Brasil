"""Valida o CV das tabelas de nível (totais por UPA no DuckDB + NumPy, `precisao.py`) contra a
linearização sobre o microdado (`variancia.erro_padrao_media_design`) numa amostra de células
de um trimestre, e resume quantas células passam na regra de supressão. Não grava parquet.

Uso:
    python -m src.auditoria.validacao_cv --ano 2026 --trimestre 2
"""
import argparse
import json
import time
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from src.inference import precisao, variancia
from src.processing import agregacoes_pnadc as ag

REPO_ROOT = Path(__file__).resolve().parents[2]
CASOS = {
    "renda": (ag.IND_RENDA, ag._chaves("raca_cor", "sexo", "faixa_etaria")),
    "carteira (VD4009 atual)": (ag.IndicadorPrecisao("carteira", ag._bool_sql("tem_carteira_assinada"),
                                                     "tem_carteira_assinada IS NOT NULL"),
                                ag._chaves("raca_cor", "sexo", "faixa_etaria")),
    "populacao (escolaridade)": (ag.IndicadorPrecisao("populacao", None, "TRUE"),
                                 ag._chaves("raca_cor", "sexo", "nivel_instrucao")),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ano", type=int, default=2026)
    parser.add_argument("--trimestre", type=int, default=2)
    parser.add_argument("--n-celulas", type=int, default=40)
    parser.add_argument("--saida", type=Path, default=REPO_ROOT / "docs" / "auditoria" / "validacao_cv.json")
    args = parser.parse_args()
    per = f"ano = {args.ano} AND trimestre = {args.trimestre}"

    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    con.execute(ag.CRIAR_BASE)
    rng = np.random.default_rng(0)
    relatorio = {"trimestre": f"{args.ano}T{args.trimestre}", "casos": {}}
    for rotulo, (ind, chaves) in CASOS.items():
        t0 = time.time()
        prec = ag._precisao_celulas(con, [ind], chaves, trimestres_sql=per)
        seg = time.time() - t0
        cols = list(chaves)
        micro = con.execute(f"""SELECT {', '.join(f'{e} AS {n}' for n, e in chaves.items())}, UF, regiao, localizacao,
                                       Capital, RM_RIDE, peso, upa, estrato,
                                       {ind.y_sql or '1.0'} AS y, COALESCE({ind.dominio_sql}, FALSE) AS dom
                                FROM base WHERE {per}""").df()
        geo = {"brasil": pd.Series("Brasil", index=micro.index), "regiao": micro["regiao"], "uf": micro["UF"],
               "sp_capital_interior": micro["localizacao"].where(micro["UF"] == "35"),
               "rm_sp": np.where(micro["RM_RIDE"] == "35",
                                 np.where(micro["Capital"].notna(), "RM São Paulo - Capital",
                                          "RM São Paulo - Não-capital (proxy ABC Paulista)"), None)}
        amostra = prec[prec[f"n_{ind.nome}"] >= 2].sample(min(args.n_celulas, len(prec)), random_state=1)
        difs, nulas = [], 0
        for _, r in amostra.iterrows():
            cel = (pd.Series(geo[r["nivel_geografico"]], index=micro.index) == r["geografia"]).to_numpy().copy()
            for c in cols:
                cel &= (micro[c] == r[c]).to_numpy()
            cel &= micro["dom"].to_numpy()
            if ind.y_sql:
                y = np.where(cel, micro["y"].astype(float), 0.0)
                ep = variancia.erro_padrao_media_design(y, micro["peso"], micro["upa"], micro["estrato"], dominio=cel)
                est = np.average(micro["y"][cel].astype(float), weights=micro["peso"][cel])
            else:
                var, _ = variancia.variancia_linearizada(np.where(cel, micro["peso"], 0.0), micro["upa"], micro["estrato"])
                ep, est = np.sqrt(var), micro["peso"][cel].sum()
            cv_micro = ep / abs(est) if est else np.nan
            cv_tab = r[f"cv_{ind.nome}"]
            if (np.isnan(cv_micro) and np.isnan(cv_tab)) or (cv_micro < 1e-12 and abs(cv_tab) < 1e-12):
                nulas += 1  # proporção 0% ou 100%: EP = 0 nos dois cálculos
                continue
            difs.append(abs(cv_tab - cv_micro) / cv_micro)
        pub = precisao.publicavel(prec[f"n_{ind.nome}"], prec[f"cv_{ind.nome}"])
        por_nivel = (pd.DataFrame({"nivel": prec["nivel_geografico"], "pub": pub})
                     .groupby("nivel")["pub"].agg(["mean", "size"]))
        relatorio["casos"][rotulo] = {
            "celulas": int(len(prec)), "celulas_validadas": int(len(amostra)), "celulas_ep_zero_nos_dois": nulas,
            "dif_relativa_max": float(np.max(difs)), "dif_relativa_mediana": float(np.median(difs)),
            "segundos_trimestre_5_niveis": round(seg, 1),
            "pct_publicavel_por_nivel": {k: round(100 * v, 1) for k, v in por_nivel["mean"].items()},
            "pct_publicavel_total": round(100 * float(pub.mean()), 1),
        }
        print(rotulo, json.dumps(relatorio["casos"][rotulo], ensure_ascii=False), flush=True)
    args.saida.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
