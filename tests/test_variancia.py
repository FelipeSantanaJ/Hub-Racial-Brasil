"""Testes de aceitação do estimador de variância design-based (B1 da auditoria).

Monte Carlo: população sintética estratificada com efeito de conglomerado conhecido;
a média dos EPs estimados tem de bater com o desvio-padrão Monte Carlo do estimador.
"""
import numpy as np
import pytest

from src.inference import variancia as v


PESOS_ESTRATO = np.random.default_rng(1234).uniform(100, 900, size=100)


def _amostra_conglomerada(rng, n_estratos=20, upas_por_estrato=6, pessoas_por_upa=25,
                          efeito_upa=1.0, ruido=2.0):
    """Uma amostra de um desenho estratificado por conglomerados: cada estrato tem
    média própria; cada UPA soma um efeito aleatório (correlação intraclasse); pesos
    desiguais por estrato. Grupo binário com proporção que varia entre UPAs."""
    linhas = []
    for h in range(n_estratos):
        mu_h = 10 + h * 0.5
        w_h = PESOS_ESTRATO[h]  # desenho fixo entre réplicas Monte Carlo
        for j in range(upas_por_estrato):
            u = rng.normal(0, efeito_upa)
            p_grupo = rng.uniform(0.2, 0.8)
            for _ in range(pessoas_por_upa):
                g = rng.random() < p_grupo
                y = mu_h + u + (1.5 if g else 0.0) + rng.normal(0, ruido)
                linhas.append((y, w_h, f"{h}-{j}", h, g))
    y, w, upa, est, g = map(np.array, zip(*linhas))
    return y, w, upa, est, g


def test_invariancia_escala_linearizacao():
    rng = np.random.default_rng(1)
    y, w, upa, est, _ = _amostra_conglomerada(rng)
    eps = [v.erro_padrao_media_design(y, c * w, upa, est) for c in (1, 10, 500)]
    assert np.allclose(eps, eps[0], rtol=1e-10)


def test_invariancia_escala_bootstrap_e_replicados():
    rng = np.random.default_rng(2)
    y, w, upa, est, _ = _amostra_conglomerada(rng)
    eps = [v.erro_padrao_bootstrap_estrato_upa(y, c * w, upa, est, n_boot=100, seed=3) for c in (1, 10, 500)]
    assert np.allclose(eps, eps[0], rtol=1e-10)
    W = w[:, None] * rng.uniform(0.5, 1.5, size=(len(w), 20))
    eps_r = [v.erro_padrao_media_replicados(y, c * w, c * W, fator_escala=1 / 20) for c in (1, 10, 500)]
    assert np.allclose(eps_r, eps_r[0], rtol=1e-10)


def test_pesos_iguais_aas_igual_s_sobre_raiz_n():
    rng = np.random.default_rng(3)
    y = rng.normal(50, 7, size=1000)
    w = np.full(1000, 37.0)
    upa = np.arange(1000)
    est = np.zeros(1000)
    esperado = np.std(y, ddof=1) / np.sqrt(1000)
    assert v.erro_padrao_media_design(y, w, upa, est) == pytest.approx(esperado, rel=1e-12)


def test_monte_carlo_media_e_dominio_e_diferenca():
    rng = np.random.default_rng(4)
    medias, dom, dif = [], [], []
    ep_m, ep_d, ep_dif = [], [], []
    for _ in range(400):
        y, w, upa, est, g = _amostra_conglomerada(rng)
        medias.append(np.average(y, weights=w))
        ep_m.append(v.erro_padrao_media_design(y, w, upa, est))
        dom.append(np.average(y[g], weights=w[g]))
        ep_d.append(v.erro_padrao_media_design(y, w, upa, est, dominio=g))
        r = v.diferenca_medias_design(y, w, upa, est, g, ~g)
        dif.append(r["diferenca"])
        ep_dif.append(r["ep_diferenca"])
    # tolerância de 12%: com 400 réplicas o erro Monte Carlo do DP é ~3,5%, e a
    # linearização com 6 UPAs/estrato tem viés pequeno (seleção com reposição).
    assert np.mean(ep_m) == pytest.approx(np.std(medias, ddof=1), rel=0.12)
    assert np.mean(ep_d) == pytest.approx(np.std(dom, ddof=1), rel=0.12)
    assert np.mean(ep_dif) == pytest.approx(np.std(dif, ddof=1), rel=0.12)


def test_conglomeracao_aumenta_ep_frente_a_formula_iid():
    """Com efeito de UPA forte, o EP de desenho tem de ser bem maior que o EP i.i.d."""
    rng = np.random.default_rng(5)
    y, w, upa, est, _ = _amostra_conglomerada(rng, efeito_upa=3.0, ruido=1.0)
    ep_iid = v.erro_padrao_media_design(y, w, np.arange(len(y)), np.zeros(len(y)))
    assert v.erro_padrao_media_design(y, w, upa, est) > 2 * ep_iid


def test_bootstrap_estrato_upa_concorda_com_linearizacao():
    rng = np.random.default_rng(6)
    y, w, upa, est, g = _amostra_conglomerada(rng, n_estratos=40)
    lin = v.erro_padrao_media_design(y, w, upa, est)
    boot = v.erro_padrao_bootstrap_estrato_upa(y, w, upa, est, n_boot=2000, seed=1)
    assert boot == pytest.approx(lin, rel=0.10)
    lin_d = v.diferenca_medias_design(y, w, upa, est, g, ~g)["ep_diferenca"]
    boot_d = v.erro_padrao_bootstrap_estrato_upa(y, w, upa, est, g, ~g, n_boot=2000, seed=1)
    assert boot_d == pytest.approx(lin_d, rel=0.10)


def test_upa_unica_politica_explicita():
    rng = np.random.default_rng(7)
    y, w, upa, est, _ = _amostra_conglomerada(rng)
    # força o estrato 0 a ter uma única UPA
    so_uma = (est != 0) | (upa == "0-0")
    y, w, upa, est = y[so_uma], w[so_uma], upa[so_uma], est[so_uma]
    ep, diag = v.erro_padrao_media_design(y, w, upa, est, diagnostico=True)
    assert diag.n_estratos_upa_unica == 1
    assert np.isfinite(ep) and ep > 0
    with pytest.raises(ValueError, match="única UPA"):
        v.erro_padrao_media_design(y, w, upa, est, politica_upa_unica="erro")


def test_dominio_nao_recorta_amostra():
    """A média do domínio é a mesma de recortar; o EP usa todas as UPAs (z=0 fora)."""
    rng = np.random.default_rng(8)
    y, w, upa, est, g = _amostra_conglomerada(rng)
    _, media = v.influencia_media(y, w, g)
    assert media == pytest.approx(np.average(y[g], weights=w[g]))
    ep, diag = v.erro_padrao_media_design(y, w, upa, est, dominio=g, diagnostico=True)
    assert diag.n_upas == len(np.unique(upa))


def test_welch_df_caso_conhecido():
    # ep1 = ep2 e n1 = n2 = n  =>  df = 2(n − 1)
    assert v.graus_liberdade_welch(0.3, 0.3, 51, 51) == pytest.approx(100.0)
    # variância concentrada num grupo => df → n desse grupo − 1
    assert v.graus_liberdade_welch(1.0, 1e-6, 21, 1000) == pytest.approx(20.0, rel=1e-6)


def test_n_efetivo_aas():
    rng = np.random.default_rng(9)
    y = rng.normal(size=2000)
    w = np.ones(2000)
    ep = v.erro_padrao_media_design(y, w, np.arange(2000), np.zeros(2000))
    assert v.n_efetivo_desenho(y, w, ep) == pytest.approx(1999, rel=1e-6)
