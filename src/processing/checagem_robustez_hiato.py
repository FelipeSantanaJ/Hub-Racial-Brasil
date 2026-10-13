"""Checagem do erro-padrão do hiato racial histórico (série completa, Brasil, Branca vs.
Negra): teste de aceitação do B1 da auditoria (docs/auditoria/rodada1.md, E1).

Compara, trimestre a trimestre, três erros-padrão do hiato absoluto (média Branca −
média Negra, renda habitual real, mesmo universo de `gerar_hiato_racial`: população de referência,
`src/utils/populacao.py`):

- `ep_linearizacao`: o de produção desde 12/10/2026 — linearização de Taylor com
  Estrato/UPA, incluindo a covariância entre as duas médias
  (`src.inference.variancia.diferenca_medias_design`);
- `ep_bootstrap_estrato_upa`: checagem independente, bootstrap de Rao-Wu que reamostra
  UPAs dentro de cada estrato (`erro_padrao_bootstrap_estrato_upa`);
- `ep_bootstrap_upa_legado`: o bootstrap antigo, só por UPA e tratando as duas médias
  como independentes (`pnadc_core.erro_padrao_cluster_bootstrap`), para continuidade com
  a checagem histórica.

Critério de aceitação do B1: razão `ep_linearizacao / ep_bootstrap_estrato_upa` próxima
de 1 nos 58 trimestres.

Uso:
    python -m src.processing.checagem_robustez_hiato
"""
import duckdb
import numpy as np
import pandas as pd
from scipy import stats

from src.inference import variancia
from src.inference.variancia import SE_METODO as SE_METODO_DESENHO
from src.inference.saida import salvar_tabela
from src.processing.agregacoes_pnadc import CRIAR_BASE, OUTPUT_DIR
from src.utils import pnadc_core
from src.utils import populacao as pop

N_BOOT = 1000
N_BOOT_LEGADO = 200


def main() -> None:
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    print("Materializando base...", flush=True)
    con.execute(CRIAR_BASE)

    trimestres = con.execute("SELECT DISTINCT ano, trimestre FROM base ORDER BY ano, trimestre").df()

    resultados = []
    for _, row in trimestres.iterrows():
        ano, trimestre = int(row["ano"]), int(row["trimestre"])
        micro = con.execute(f"""
            SELECT raca_cor, renda_referencia_real, peso, upa, estrato
            FROM base
            WHERE ano = {ano} AND trimestre = {trimestre}
              AND raca_cor IN ('Branca', 'Preta', 'Parda')
              AND {pop.filtro_sql()}
        """).df()
        if micro.empty:
            continue
        micro["raca_cor"] = micro["raca_cor"].replace({"Preta": "Negra", "Parda": "Negra"})
        y = micro["renda_referencia_real"].to_numpy(float)
        w = micro["peso"].to_numpy(float)
        u = micro["upa"].to_numpy(object)
        e = micro["estrato"].to_numpy(object)
        em_b = (micro["raca_cor"] == "Branca").to_numpy()
        em_n = ~em_b

        r = variancia.diferenca_medias_design(y, w, u, e, em_b, em_n)
        ep_boot = variancia.erro_padrao_bootstrap_estrato_upa(y, w, u, e, em_b, em_n, n_boot=N_BOOT, seed=42)
        df_b, df_n = micro[em_b], micro[em_n]
        ep_legado = float(np.sqrt(
            pnadc_core.erro_padrao_cluster_bootstrap(df_b, "renda_referencia_real", "peso", "upa", N_BOOT_LEGADO, 42) ** 2
            + pnadc_core.erro_padrao_cluster_bootstrap(df_n, "renda_referencia_real", "peso", "upa", N_BOOT_LEGADO, 42) ** 2
        ))

        hiato = r["diferenca"]
        diag = r["diagnostico"]
        resultados.append({
            "ano": ano, "trimestre": trimestre,
            "hiato_absoluto": hiato,
            "ep_linearizacao": r["ep_diferenca"],
            "ep_linearizacao_sem_covariancia": float(np.sqrt(r["ep_a"] ** 2 + r["ep_b"] ** 2)),
            "correlacao_medias": r["cov_ab"] / (r["ep_a"] * r["ep_b"]),
            "ep_bootstrap_estrato_upa": ep_boot,
            "ep_bootstrap_upa_legado": ep_legado,
            "z_linearizacao": hiato / r["ep_diferenca"],
            "z_bootstrap_estrato_upa": hiato / ep_boot,
            "p_valor_linearizacao": float(2 * stats.norm.sf(abs(hiato / r["ep_diferenca"]))),
            "n_upas": diag.n_upas, "n_estratos": diag.n_estratos,
            "n_estratos_upa_unica": diag.n_estratos_upa_unica,
            "n_branca": r["n_a"], "n_negra": r["n_b"],
        })
        print(f"{ano}T{trimestre}: razão lin/boot = {r['ep_diferenca'] / ep_boot:.3f}", flush=True)

    df = pd.DataFrame(resultados)
    df["razao_linearizacao_sobre_bootstrap"] = df["ep_linearizacao"] / df["ep_bootstrap_estrato_upa"]
    df["se_metodo"] = variancia.SE_METODO

    destino = OUTPUT_DIR / "checagem_robustez_hiato_racial.parquet"
    salvar_tabela(df, destino, se_metodo=SE_METODO_DESENHO, n_boot=N_BOOT, bootstrap="rao_wu_estrato_upa")

    razao = df["razao_linearizacao_sobre_bootstrap"]
    print(f"checagem_robustez_hiato_racial.parquet: {len(df)} trimestres", flush=True)
    print(f"razão EP linearização / bootstrap Estrato-UPA: mediana {razao.median():.3f} "
          f"(mín {razao.min():.3f}, máx {razao.max():.3f})", flush=True)
    print(f"z mínimo (linearização) na série: {df['z_linearizacao'].min():.1f}", flush=True)
    print(f"estratos com UPA única (máx por trimestre): {df['n_estratos_upa_unica'].max()}", flush=True)


if __name__ == "__main__":
    main()
