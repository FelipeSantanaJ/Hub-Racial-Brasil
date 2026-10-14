"""Bloco D (Onda 3): decomposições com respostas conhecidas."""
import numpy as np
import pandas as pd
import pytest

from src.inference import variancia
from src.processing import bloco_d as D


def _sim(n=4000, seed=0):
    rng = np.random.default_rng(seed)
    neg = rng.random(n) < 0.5
    ind = (~neg) & (rng.random(n) < 0.1)
    educ = rng.normal(0, 1, n) - 0.6 * neg - 0.4 * ind
    terr = rng.normal(0, 1, n) - 0.3 * neg + 0.3 * educ
    horas = rng.normal(0, 1, n) + 0.2 * educ
    y = 0.5 * educ + 0.2 * terr + 0.1 * horas - 0.15 * neg - 0.1 * ind + rng.normal(0, 0.5, n)
    w = rng.uniform(1, 3, n)
    X = np.column_stack([np.ones(n), neg, ind, educ, terr, horas])
    idx = {"base": np.array([0, 1, 2]), "educ": np.array([3]), "terr": np.array([4]), "horas": np.array([5])}
    return X, y, w, idx, neg, ind


def test_sistema_igual_a_wls_direto():
    X, y, w, *_ = _sim()
    s = D.Sistema(X, y, w, bloco=777)
    sw = np.sqrt(w)
    direto = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
    assert s.beta(np.arange(X.shape[1])) == pytest.approx(direto)


def test_gelbach_soma_a_queda_do_coeficiente_e_das_influencias():
    X, y, w, idx, *_ = _sim()
    s = D.Sistema(X, y, w)
    blocos = ["educ", "terr", "horas"]
    g = D.gelbach(s, idx, blocos, j_raca=1)
    seq = D.aninhadas(s, idx, blocos, j_raca=1)
    base, cheio = seq[0], seq[-1]
    assert sum(d for d, _ in g.values()) == pytest.approx(base[1] - cheio[1], abs=1e-10)
    soma_psi = sum(p for _, p in g.values())
    assert soma_psi == pytest.approx(base[2] - cheio[2], abs=1e-9)
    # a instrução (educ) é o bloco que mais reduz o hiato simulado
    assert min(g, key=lambda k: g[k][0]) == "educ"


def test_shapley_soma_o_total():
    X, y, w, idx, *_ = _sim(seed=1)
    s = D.Sistema(X, y, w)
    blocos = ["educ", "terr", "horas"]
    sh = D.shapley(s, idx, blocos, j_raca=1)
    seq = D.aninhadas(s, idx, blocos, j_raca=1)
    assert sum(v for v, _ in sh.values()) == pytest.approx(seq[0][1] - seq[-1][1], abs=1e-10)
    assert sum(p for _, p in sh.values()) == pytest.approx(seq[0][2] - seq[-1][2], abs=1e-9)


def test_ep_igual_ao_sanduiche_hc0_quando_cada_observacao_e_uma_upa():
    X, y, w, idx, *_ = _sim(seed=2)
    n = len(y)
    s = D.Sistema(X, y, w)
    cols = np.arange(X.shape[1])
    c = np.zeros(len(cols))
    c[1] = 1.0
    psi = s.influencia(cols, c)
    ep = D.ep_de(psi, np.arange(n), np.zeros(n))
    b = s.beta(cols)
    e = y - X @ b
    A_inv = np.linalg.inv((X * w[:, None]).T @ X)
    meat = (X * (w * e)[:, None]).T @ (X * (w * e)[:, None])
    hc0 = np.sqrt((A_inv @ meat @ A_inv)[1, 1])
    assert ep == pytest.approx(hc0 * np.sqrt(n / (n - 1)), rel=1e-8)


def test_reimers_soma_e_sem_diferenca_de_retorno_nao_sobra_parte():
    rng = np.random.default_rng(3)
    n = 6000
    grupo = rng.random(n) < 0.5
    x = rng.normal(0, 1, n) + 1.0 * grupo
    y = 1 + 0.8 * x + rng.normal(0, 0.1, n)  # mesmo retorno nos dois grupos
    w = np.ones(n)
    X = np.column_stack([np.ones(n), x])
    r = D.reimers(X, y, w, grupo, ~grupo)
    assert r["bruto"][0] == pytest.approx(r["explicada"][0] + r[D.NAO_ASSOCIADA][0])
    assert abs(r[D.NAO_ASSOCIADA][0]) < 0.02 and r["explicada"][0] == pytest.approx(0.8 * (x[grupo].mean() - x[~grupo].mean()), rel=0.03)
    # ψ do bruto é a diferença das influências das médias
    zA, _ = variancia.influencia_media(np.where(grupo, y, 0.0), w, grupo)
    zB, _ = variancia.influencia_media(np.where(~grupo, y, 0.0), w, ~grupo)
    assert r["bruto"][1] == pytest.approx(zA - zB)


def test_reimers_com_categoria_ausente_num_grupo_usa_o_coeficiente_do_outro():
    rng = np.random.default_rng(5)
    n = 8000
    grupo = rng.random(n) < 0.3
    cat = (~grupo) & (rng.random(n) < 0.2)          # categoria que só existe no grupo B
    x = rng.normal(0, 1, n)
    y = 1 + 0.5 * x + 0.7 * cat + rng.normal(0, 0.1, n)
    w = np.ones(n)
    X = np.column_stack([np.ones(n), x, cat.astype(float)])
    r = D.reimers(X, y, w, grupo, ~grupo)           # não pode ser singular
    assert r["bruto"][0] == pytest.approx(r["explicada"][0] + r[D.NAO_ASSOCIADA][0])
    # a diferença de composição da categoria entra pela via do coeficiente de B (0,7)
    esperado = 0.5 * (x[grupo].mean() - x[~grupo].mean()) + 0.7 * (0 - cat[~grupo].mean())
    assert r["explicada"][0] == pytest.approx(esperado, abs=0.01)
    assert abs(r[D.NAO_ASSOCIADA][0]) < 0.01


def test_rif_tem_media_igual_ao_quantil_e_rif_ob_soma():
    rng = np.random.default_rng(4)
    n = 20000
    y = rng.normal(0, 1, n)
    w = rng.uniform(1, 2, n)
    r = D.rif(y, w, 0.5)
    assert np.average(r, weights=w) == pytest.approx(D.pnadc_core.quantil_ponderado(y, w, 0.5), abs=0.01)
    grupo = rng.random(n) < 0.5
    y2 = y + 0.5 * grupo
    X = np.column_stack([np.ones(n), rng.normal(size=n)])
    GA, GB = D._g_dominio(X, w, grupo), D._g_dominio(X, w, ~grupo)
    d = D.rif_ob(X, y2, w, grupo, ~grupo, 0.9, 1.0, GA, GB)
    assert d["bruto"] == pytest.approx(d["explicada"] + d[D.NAO_ASSOCIADA])
    assert d["bruto"] == pytest.approx(0.5, abs=0.06) and abs(d["explicada"]) < 0.03


def test_valor_de_robustez_do_exemplo_publicado():
    # Exemplo de Darfur do sensemakr (Cinelli e Hazlett, 2020 — a confirmar): t = 4,18 com 783 g.l. → RV ≈ 13,9%
    t, gl = 4.18, 783
    assert D.valor_robustez(t * t / (t * t + gl)) == pytest.approx(0.139, abs=0.001)


def test_limites_de_sensibilidade_casos_triviais():
    assert D.limite_ch(0.01, 0.1, 0.0, -0.3, 2.0)["vies"] == pytest.approx(0.0)
    assert D.limite_ch(0.0091, 0.1, 1.0, -0.3, 2.0)["r2dz_x"] == pytest.approx(0.0092, abs=1e-4)
    o = D.oster(-0.3, 0.1, -0.3, 0.4, 0.52)
    assert o["beta_ajustado_delta1"] == pytest.approx(-0.3)
    # coeficiente que cai à metade de R̊ = 0,1 para R̃ = 0,4: com R²max = 0,7, δ = 1 leva-o a zero
    assert D.oster(-0.4, 0.1, -0.2, 0.4, 0.7)["beta_ajustado_delta1"] == pytest.approx(0.0)


def test_montar_x_blocos_tem_referencia_omitida():
    m = pd.DataFrame({"raca": ["Branca", "Negra", "Indígena", "Negra"], "sexo": ["1", "2", "2", "1"],
                      "idade": [20, 35, 50, 70], "instrucao": ["1", "2", "2", None], "uf": ["11", "35", "35", "35"],
                      "urbano": ["1", "1", "2", "1"], "area": ["1", "4", "4", "4"], "horas": [40, 20, 44, 40],
                      "posicao": ["01", "01", "09", "01"], "previdencia": ["1", "2", "2", "1"],
                      "ocupacao": ["05", "05", "09", "05"], "atividade": ["01", "02", "02", "02"]})
    X, idx = D.montar_x(m, D.BLOCOS, remover=False)
    assert X.shape[0] == 4 and list(idx["base"]) == [0, 1, 2]
    assert X[:, idx["sexo"]].ravel().tolist() == [0, 1, 1, 0]
    # instrução: faltante vira categoria própria; a mais frequente ('2') é a referência
    assert len(idx["instrucao"]) == 2


def test_indices_de_segregacao_extremos():
    from src.processing.bloco_d_estrutura import indices_segregacao
    w = np.ones(4)
    # segregação completa: cada grupo numa ocupação
    D_, H_ = indices_segregacao(np.array([0, 0, 1, 1]), np.array([0.0, 0.0, 1.0, 1.0]), w)
    assert D_ == pytest.approx(1.0) and H_ == pytest.approx(1.0)
    # mesma distribuição nas ocupações
    D_, H_ = indices_segregacao(np.array([0, 1, 0, 1]), np.array([0.0, 0.0, 1.0, 1.0]), w)
    assert D_ == pytest.approx(0.0) and H_ == pytest.approx(0.0, abs=1e-12)


def test_colunas_colineares_saem_e_ficam_registradas():
    rng = np.random.default_rng(6)
    n = 3000
    pos = rng.choice(["01", "03", "04", "09"], n)
    ativ = np.where(np.isin(pos, ["03", "04"]), "11", rng.choice(["01", "07"], n))  # doméstico ≡ serviços domésticos
    m = pd.DataFrame({"raca": rng.choice(["Branca", "Negra", "Indígena"], n), "posicao": pos, "previdencia": "1",
                      "atividade": ativ, "peso": rng.uniform(1, 2, n)})
    X, idx = D.montar_x(m, ["vinculo", "atividade"])
    assert len(idx["_removidas"]) == 1 and idx["_removidas"][0].startswith("atividade:")
    assert np.linalg.matrix_rank(X) == X.shape[1]
    # a dummy de previdência constante (só '1') vira coluna sem categoria; nada vazio fica em X
    assert (np.abs(X).sum(axis=0) > 0).all()
