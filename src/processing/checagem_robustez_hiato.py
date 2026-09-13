"""Checagem de robustez do erro padrão do hiato racial histórico (série completa,
Brasil, Branca vs. Negra) via bootstrap por cluster (UPA), comparando com o método em
produção (`pnadc_core.tabela_hiatos_significancia`, que usa só o peso analítico V1028).

Não substitui o método em produção — roda como validação pontual (ver docs/PLANO.md,
seção de hardening, e docs/LIMITACOES_E_METODOLOGIA.md) que confirma se os 58 trimestres
de `hiato_racial.parquet` continuam significativos sob um erro padrão mais conservador
(que soma o efeito de conglomerado por UPA ao peso analítico).

Uso:
    python -m src.processing.checagem_robustez_hiato
"""
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from scipy import stats

from src.processing.agregacoes_pnadc import CRIAR_BASE, OUTPUT_DIR
from src.utils import pnadc_core

N_BOOT = 200


def main() -> None:
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    print("Materializando base...", flush=True)
    con.execute(CRIAR_BASE)

    original = pd.read_parquet(OUTPUT_DIR / "hiato_racial.parquet")
    trimestres = con.execute("SELECT DISTINCT ano, trimestre FROM base ORDER BY ano, trimestre").df()

    resultados = []
    for _, row in trimestres.iterrows():
        ano, trimestre = int(row["ano"]), int(row["trimestre"])
        micro = con.execute(f"""
            SELECT raca_cor, renda_habitual_real, peso, upa
            FROM base
            WHERE ano = {ano} AND trimestre = {trimestre}
              AND raca_cor IN ('Branca', 'Preta', 'Parda')
              AND renda_habitual_real IS NOT NULL
        """).df()
        if micro.empty:
            continue
        micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})

        df_b = micro[micro["raca_cor"] == "Branca"]
        df_n = micro[micro["raca_cor"] == "Negra"]
        if df_b.empty or df_n.empty:
            continue

        media_b = pnadc_core.media_ponderada(df_b["renda_habitual_real"], df_b["peso"])
        media_n = pnadc_core.media_ponderada(df_n["renda_habitual_real"], df_n["peso"])
        ep_b = pnadc_core.erro_padrao_cluster_bootstrap(
            df_b, "renda_habitual_real", "peso", cluster_col="upa", n_boot=N_BOOT, seed=42)
        ep_n = pnadc_core.erro_padrao_cluster_bootstrap(
            df_n, "renda_habitual_real", "peso", cluster_col="upa", n_boot=N_BOOT, seed=42)

        hiato = media_b - media_n
        ep_cluster = float(np.sqrt(ep_b**2 + ep_n**2))
        if ep_cluster > 0:
            z = hiato / ep_cluster
            p_valor_cluster = float(2 * (1 - stats.norm.cdf(abs(z))))
        else:
            p_valor_cluster = np.nan

        resultados.append({
            "ano": ano, "trimestre": trimestre,
            "hiato_absoluto": hiato,
            "ep_peso_apenas": float(np.sqrt(
                pnadc_core.erro_padrao_media_ponderada(df_b["renda_habitual_real"], df_b["peso"])**2
                + pnadc_core.erro_padrao_media_ponderada(df_n["renda_habitual_real"], df_n["peso"])**2
            )),
            "ep_cluster_bootstrap": ep_cluster,
            "p_valor_cluster_bootstrap": p_valor_cluster,
            "significativo_cluster_bootstrap": bool(p_valor_cluster < 0.05) if not np.isnan(p_valor_cluster) else False,
        })

    df = pd.DataFrame(resultados)
    df = df.merge(
        original[["ano", "trimestre", "p_valor", "significativo"]].rename(
            columns={"p_valor": "p_valor_peso_apenas", "significativo": "significativo_peso_apenas"}
        ),
        on=["ano", "trimestre"], how="left",
    )
    df["razao_ep_cluster_sobre_peso"] = df["ep_cluster_bootstrap"] / df["ep_peso_apenas"]

    destino = OUTPUT_DIR / "checagem_robustez_hiato_racial.parquet"
    df.to_parquet(destino, index=False)

    n_diff = int((df["significativo_cluster_bootstrap"] != df["significativo_peso_apenas"]).sum())
    print(f"checagem_robustez_hiato_racial.parquet: {len(df)} trimestres", flush=True)
    print(f"trimestres com significância divergente (peso vs. cluster bootstrap): {n_diff}", flush=True)
    print(f"razão média EP cluster / EP peso apenas: {df['razao_ep_cluster_sobre_peso'].mean():.2f}x "
          f"(min {df['razao_ep_cluster_sobre_peso'].min():.2f}x, max {df['razao_ep_cluster_sobre_peso'].max():.2f}x)",
          flush=True)
    print(f"p-valor máximo (cluster bootstrap) na série: {df['p_valor_cluster_bootstrap'].max():.2e}", flush=True)


if __name__ == "__main__":
    main()
