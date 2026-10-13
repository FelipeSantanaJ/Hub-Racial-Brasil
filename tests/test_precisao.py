"""CV a partir de totais por UPA (src/inference/precisao.py) contra a linearização de
src/inference/variancia.py, e a regra de supressão (R8, Ponto de parada 3)."""
import numpy as np
import pandas as pd
import pytest

from src.inference import precisao, variancia


def _amostra(seed=0, n=6000, upa_unica=True):
    rng = np.random.default_rng(seed)
    estrato = rng.integers(0, 40, size=n)
    upa = estrato * 10 + rng.integers(0, 6, size=n)
    if upa_unica:  # estrato 39 com uma só UPA
        upa = np.where(estrato == 39, 390, upa)
    efeito = rng.normal(0, 0.3, size=400)[upa]
    df = pd.DataFrame({
        "estrato": estrato, "upa": upa,
        "w": rng.uniform(100, 900, size=n),
        "raca": rng.choice(["Branca", "Negra", "Indígena"], p=[0.45, 0.53, 0.02], size=n),
        "sexo": rng.choice(["H", "M"], size=n),
        "y": np.exp(7.5 + efeito + rng.normal(0, 0.7, size=n)),
        "tem_y": rng.random(n) < 0.6,
    })
    return df


def _totais(df, chaves, dominio, y):
    d = df[dominio].assign(wy=lambda x: x["w"] * x[y])
    return (d.groupby([*chaves, "estrato", "upa"]).agg(A=("wy", "sum"), B=("w", "sum"), n=("w", "size"))
            .reset_index())


def _n_h(df):
    return df.groupby("estrato")["upa"].nunique().rename("n_h").reset_index()


def test_media_bate_com_linearizacao():
    df = _amostra()
    dom = df["tem_y"].to_numpy()
    res = precisao.cv_de_totais_upa(_totais(df, ["raca", "sexo"], dom, "y"), ["raca", "sexo"], _n_h(df))
    assert len(res) == 6
    for _, r in res.iterrows():
        cel = (df["raca"] == r["raca"]).to_numpy() & (df["sexo"] == r["sexo"]).to_numpy() & dom
        # universo = todas as linhas (y zerado fora do domínio para não sair do universo)
        ep = variancia.erro_padrao_media_design(np.where(cel, df["y"], 0.0), df["w"], df["upa"], df["estrato"],
                                                dominio=cel)
        media = np.average(df["y"][cel], weights=df["w"][cel])
        assert r["estimativa"] == pytest.approx(media, rel=1e-12)
        assert r["ep"] == pytest.approx(ep, rel=1e-6)
        assert r["n"] == cel.sum()


def test_proporcao_bate_com_linearizacao():
    df = _amostra(seed=1)
    df["ind"] = (df["y"] > 2500).astype(float)
    dom = df["tem_y"].to_numpy()
    res = precisao.cv_de_totais_upa(_totais(df, ["raca"], dom, "ind"), ["raca"], _n_h(df))
    for _, r in res.iterrows():
        cel = (df["raca"] == r["raca"]).to_numpy() & dom
        ep = variancia.erro_padrao_media_design(np.where(cel, df["ind"], 0.0), df["w"], df["upa"], df["estrato"],
                                                dominio=cel)
        assert r["ep"] == pytest.approx(ep, rel=1e-6)


def test_total_bate_com_linearizacao_sem_upa_unica():
    df = _amostra(seed=2, upa_unica=False)
    dom = np.ones(len(df), bool)
    res = precisao.cv_de_totais_upa(_totais(df, ["raca"], dom, "y"), ["raca"], _n_h(df), tipo="total")
    for _, r in res.iterrows():
        cel = (df["raca"] == r["raca"]).to_numpy()
        var, _ = variancia.variancia_linearizada(np.where(cel, df["w"], 0.0), df["upa"], df["estrato"])
        assert r["estimativa"] == pytest.approx(df["w"][cel].sum())
        assert r["ep"] == pytest.approx(np.sqrt(var), rel=1e-6)


def test_universo_por_trimestre():
    """Chaves de universo (ex.: ano/trimestre): cada trimestre usa os seus n_h."""
    a, b = _amostra(seed=3), _amostra(seed=4)
    a["tri"], b["tri"] = 1, 2
    df = pd.concat([a, b], ignore_index=True)
    dom = df["tem_y"].to_numpy()
    n_h = df.groupby(["tri", "estrato"])["upa"].nunique().rename("n_h").reset_index()
    res = precisao.cv_de_totais_upa(_totais(df, ["tri", "raca"], dom, "y"), ["tri", "raca"], n_h,
                                    chaves_universo=["tri"])
    sozinho = precisao.cv_de_totais_upa(_totais(a, ["raca"], a["tem_y"].to_numpy(), "y"), ["raca"], _n_h(a))
    junto = res[res["tri"] == 1].set_index("raca")["ep"]
    assert np.allclose(junto.loc[sozinho["raca"]].to_numpy(), sozinho["ep"].to_numpy(), rtol=1e-12)


def test_regra_supressao():
    n = np.array([29, 30, 500, 500, 500, np.nan])
    cv = np.array([0.1, 0.1, 0.30, 0.3001, np.nan, 0.1])
    assert precisao.publicavel(n, cv).tolist() == [False, True, True, False, False, False]
