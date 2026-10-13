"""Microdado SINTÉTICO (sem nenhum dado real) no formato do extrato bruto da PNAD Contínua,
para o teste golden-file da pipeline `CRIAR_BASE` → agregação → saída (B5 da auditoria).

Determinístico (seed fixa): ~5.000 pessoas em 2 trimestres, 4 UFs, 20 estratos, 100 UPAs,
com efeito de UPA, pesos desiguais, hiato racial embutido, desocupados e pessoas fora da
força de trabalho (renda nula), para exercitar filtros e o EP design-based.

Uso (regerar os arquivos esperados — só quando uma mudança de resultado for INTENCIONAL e
documentada no CHANGELOG_METODOLOGICO):
    python -m tests.golden.microdado_sintetico --regerar-esperado
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20261012
PASTA_GOLDEN = Path(__file__).resolve().parent
TRIMESTRES = [(2025, 4), (2026, 1)]
UFS = ["29", "33", "35", "43"]


def gerar_microdado(n_por_trimestre: int = 2500) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    partes = []
    for ano, tri in TRIMESTRES:
        upa_idx = rng.integers(0, 100, size=n_por_trimestre)
        estrato = upa_idx // 5
        uf = np.array(UFS)[estrato % 4]
        efeito_upa = np.random.default_rng(SEED + 1).normal(0, 0.25, size=100)[upa_idx]
        raca = rng.choice(["1", "2", "3", "4", "5", "9"], p=[0.43, 0.10, 0.01, 0.44, 0.01, 0.01], size=n_por_trimestre)
        sexo = rng.choice(["1", "2"], size=n_por_trimestre)
        idade = rng.integers(14, 80, size=n_por_trimestre).astype(float)
        instr = rng.choice(list("1234567"), size=n_por_trimestre)
        forca = rng.choice(["1", "2"], p=[0.65, 0.35], size=n_por_trimestre)
        ocup = np.where(forca == "1", rng.choice(["1", "2"], p=[0.9, 0.1], size=n_por_trimestre), None)
        log_renda = (7.3 + 0.12 * instr.astype(int) + 0.25 * (raca == "1") + 0.15 * (sexo == "1")
                     + efeito_upa + rng.normal(0, 0.6, size=n_por_trimestre))
        renda = np.where(ocup == "1", np.round(np.exp(log_renda), 0), np.nan)
        peso = np.round(np.random.default_rng(SEED + 2).uniform(150, 900, size=20)[estrato]
                        * rng.uniform(0.8, 1.2, size=n_por_trimestre), 4)
        partes.append(pd.DataFrame({
            "UF": uf, "Capital": np.where(rng.random(n_por_trimestre) < 0.3, uf, None),
            "RM_RIDE": None, "UPA": [f"{u}{i:07d}" for u, i in zip(uf, upa_idx)],
            "Estrato": [f"{u}{e:05d}" for u, e in zip(uf, estrato)],
            "V1008": rng.integers(1, 15, size=n_por_trimestre).astype(str),
            "V1016": rng.integers(1, 6, size=n_por_trimestre).astype(str),
            "V1022": rng.choice(["1", "2"], p=[0.85, 0.15], size=n_por_trimestre),
            "V1023": rng.choice(list("1234"), size=n_por_trimestre),
            "V1028": peso, "V2003": rng.integers(1, 6, size=n_por_trimestre).astype(str),
            "V2007": sexo, "V2009": idade, "V2010": raca, "V3001": "1",
            "VD3004": instr, "VD4001": forca, "VD4002": ocup,
            "VD4003": np.where(forca == "2", "2", None), "VD4005": None,
            "VD4009": np.where(ocup == "1", rng.choice(["01", "02", "05", "07", "09"], size=n_por_trimestre), None),
            "VD4010": np.where(ocup == "1", rng.choice([f"{i:02d}" for i in range(1, 13)], size=n_por_trimestre), None),
            "VD4011": np.where(ocup == "1", rng.choice([f"{i:02d}" for i in range(1, 12)], size=n_por_trimestre), None),
            "VD4012": np.where(ocup == "1", rng.choice(["1", "2"], size=n_por_trimestre), None),
            "VD4016": renda, "VD4017": renda, "VD4019": renda, "VD4020": renda,
            "VD4031": np.where(ocup == "1", 40.0, np.nan), "VD4035": np.where(ocup == "1", 40.0, np.nan),
            "V4039": np.where(ocup == "1", 40.0, np.nan),
            "ano": ano, "trimestre": tri,
        }))
    return pd.concat(partes, ignore_index=True)


def gerar_deflator() -> pd.DataFrame:
    linhas = [{"ano": a, "trimestre": t, "UF": uf, "deflator_habitual": 1.0 + 0.01 * i,
               "deflator_efetivo": 1.0 + 0.01 * i}
              for i, (a, t) in enumerate(TRIMESTRES) for uf in UFS]
    return pd.DataFrame(linhas)


def gravar_extrato(df: pd.DataFrame, raiz: Path) -> str:
    """Grava no mesmo layout hive do extrator (ano=/trimestre=/parte_0000.parquet)."""
    for (ano, tri), sub in df.groupby(["ano", "trimestre"]):
        pasta = raiz / f"ano={ano}" / f"trimestre={tri}"
        pasta.mkdir(parents=True, exist_ok=True)
        sub.drop(columns=["ano", "trimestre"]).to_parquet(pasta / "parte_0000.parquet", index=False)
    return str(raiz / "ano=*" / "trimestre=*" / "*.parquet")


def rodar_pipeline(tmp: Path) -> dict[str, pd.DataFrame]:
    """CRIAR_BASE sobre o sintético + duas agregações (uma de pontos, uma de inferência)."""
    import duckdb

    from src.processing import agregacoes_pnadc as ag

    glob = gravar_extrato(gerar_microdado(), tmp / "raw")
    deflator = tmp / "deflator.parquet"
    gerar_deflator().to_parquet(deflator, index=False)
    sql = ag.CRIAR_BASE.replace(ag.PARQUET_GLOB, glob.replace("\\", "/")).replace(ag.DEFLATOR_PATH, str(deflator).replace("\\", "/"))
    assert sql != ag.CRIAR_BASE
    saida = tmp / "processed"
    saida.mkdir()
    original = ag.OUTPUT_DIR
    ag.OUTPUT_DIR = saida
    try:
        con = duckdb.connect()
        con.execute(sql)
        ag.gerar_renda(con)
        ag.gerar_hiato_racial(con)
    finally:
        ag.OUTPUT_DIR = original
    return {nome: pd.read_parquet(saida / f"{nome}.parquet") for nome in ("renda", "hiato_racial")}


def ordenar(nome: str, df: pd.DataFrame) -> pd.DataFrame:
    chaves = [c for c in ("nivel_geografico", "geografia", "ano", "trimestre", "raca_cor", "sexo", "faixa_etaria") if c in df.columns]
    return df.sort_values(chaves).reset_index(drop=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regerar-esperado", action="store_true")
    args = parser.parse_args()
    if args.regerar_esperado:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for nome, df in rodar_pipeline(Path(d)).items():
                ordenar(nome, df).to_parquet(PASTA_GOLDEN / f"esperado_{nome}.parquet", index=False)
                print(f"esperado_{nome}.parquet: {len(df)} linhas")
