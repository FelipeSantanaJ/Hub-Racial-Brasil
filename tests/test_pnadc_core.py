"""Testes de regressão para src/utils/pnadc_core.py.

Cobre as validações descritas em docs/PLANO.md (round-trip de
quantil, casos sintéticos de Theil, guarda contra o erro padrão inflado em ~sqrt(n) e contra
o peso tratado como frequência — E1 da auditoria) —
automatizadas para não serem silenciosamente reintroduzidas numa mudança futura.
"""
import numpy as np
import pandas as pd
import pytest

from src.utils import pnadc_core


class TestQuantilRoundTrip:
    """quantil_ponderado e sua inversa, percentil_ponderado_de_valor, precisam se
    cancelar: o valor no percentil P, jogado de volta, precisa devolver P."""

    @pytest.mark.parametrize("percentil", [10, 25, 50, 75, 90])
    def test_round_trip_pesos_iguais(self, percentil):
        valores = np.arange(1, 1001, dtype=float)  # 1..1000
        pesos = np.ones_like(valores)

        valor = pnadc_core.quantil_ponderado(valores, pesos, percentil / 100)
        percentil_recuperado = pnadc_core.percentil_ponderado_de_valor(valores, pesos, valor)

        assert percentil_recuperado == pytest.approx(percentil, abs=1e-9)


def _aas(n):
    """Desenho de amostragem aleatória simples: cada observação é a sua UPA, estrato único."""
    return np.arange(n), np.zeros(n)


def _formula_antiga_peso_frequencia(valores, pesos):
    """Fórmula removida em 12/10/2026 (E1), mantida AQUI só como referência negativa."""
    n = len(valores)
    m = np.average(valores, weights=pesos)
    return np.sqrt((n / (n - 1)) * np.sum(pesos * (valores - m) ** 2) / np.sum(pesos) ** 2)


class TestErroPadraoMediaPonderada:
    """EP design-based (src/inference/variancia.py). Com pesos iguais e AAS, o EP precisa
    bater EXATAMENTE com a fórmula clássica s/sqrt(n)."""

    def test_bate_com_formula_classica_pesos_iguais(self):
        valores = np.array([10.0, 20.0, 30.0])
        pesos = np.array([1.0, 1.0, 1.0])

        ep = pnadc_core.erro_padrao_media_ponderada(valores, pesos, *_aas(3))

        n = len(valores)
        s = valores.std(ddof=1)  # desvio padrão amostral (denominador n-1)
        ep_classico = s / np.sqrt(n)

        assert ep == pytest.approx(ep_classico, rel=1e-9)

    def test_nao_reintroduz_fator_sqrt_n(self):
        """Guarda explícita contra o bug corrigido em 2026-09-04: erro padrão não pode
        escalar linearmente com o tamanho da amostra quando os dados são só replicados
        (mesma variância, n maior deveria ESTREITAR o IC, não alargar)."""
        rng = np.random.default_rng(0)
        valores_base = rng.normal(100, 15, size=50)
        pesos_base = np.ones(50)

        ep_50 = pnadc_core.erro_padrao_media_ponderada(valores_base, pesos_base, *_aas(50))

        valores_5000 = np.tile(valores_base, 100)
        pesos_5000 = np.tile(pesos_base, 100)
        ep_5000 = pnadc_core.erro_padrao_media_ponderada(valores_5000, pesos_5000, *_aas(5000))

        # replicar a amostra 100x deveria dividir o erro padrão por ~sqrt(100)=10,
        # não multiplicar por ~sqrt(100) (o sentido do bug antigo). Tolerância de 2%
        # cobre a correção de população finita (n/(n-1)), que difere um pouco entre
        # n=50 e n=5000 mas não chega perto da ordem de grandeza do bug antigo.
        assert ep_5000 == pytest.approx(ep_50 / 10, rel=0.02)

    def test_exige_upa_e_estrato(self):
        with pytest.raises(ValueError, match="upa"):
            pnadc_core.erro_padrao_media_ponderada([1.0, 2.0, 3.0], [1.0, 1.0, 1.0])

    def test_guarda_peso_na_primeira_potencia(self):
        """FALHA se a fórmula antiga (peso tratado como frequência) voltar: o EP de
        produção tem de ser o mesmo nas escalas 1x e 500x, igual à referência AAS em
        escala 1x, e diferente da fórmula antiga em escala 500x (que daria EP ÷ ~22)."""
        rng = np.random.default_rng(42)
        y = rng.lognormal(7.5, 0.8, size=20_000)
        w = rng.uniform(0.5, 1.5, size=20_000)
        upa, est = _aas(20_000)
        ep_1 = pnadc_core.erro_padrao_media_ponderada(y, w, upa, est)
        ep_500 = pnadc_core.erro_padrao_media_ponderada(y, 500 * w, upa, est)
        assert ep_500 == pytest.approx(ep_1, rel=1e-10)
        antiga_500 = _formula_antiga_peso_frequencia(y, 500 * w)
        assert ep_500 / antiga_500 > 15

    def test_tabela_hiatos_invariante_a_escala(self):
        rng = np.random.default_rng(3)
        n = 4000
        df = pd.DataFrame({
            "y": rng.lognormal(7, 0.7, n), "g": rng.choice(["A", "B"], n),
            "w": rng.uniform(100, 900, n), "upa": rng.integers(0, 400, n),
        })
        df["est"] = df["upa"] // 10
        t1 = pnadc_core.tabela_hiatos_significancia(df, "y", "g", "B", peso="w", upa="upa", estrato="est")
        df["w"] *= 500
        t2 = pnadc_core.tabela_hiatos_significancia(df, "y", "g", "B", peso="w", upa="upa", estrato="est")
        pd.testing.assert_frame_equal(t1, t2, rtol=1e-9)

    def test_tabela_hiatos_exige_desenho(self):
        df = pd.DataFrame({"y": [1.0, 2.0, 3.0, 4.0], "g": ["A", "A", "B", "B"], "w": 1.0})
        with pytest.raises(ValueError, match="upa"):
            pnadc_core.tabela_hiatos_significancia(df, "y", "g", "B", peso="w")


class TestDecomposicaoTheilEntreDentro:
    """Os 3 casos sintéticos usados pra validar a função quando foi escrita (ver
    docs/PLANO.md), como teste de regressão automatizado."""

    def test_grupos_identicos_theil_entre_zero(self):
        valores = np.tile([10.0, 20.0, 30.0, 40.0], 2)
        grupos = ["A"] * 4 + ["B"] * 4
        df = pd.DataFrame({"valor": valores, "grupo": grupos, "peso": 1.0})

        resumo, _ = pnadc_core.decomposicao_theil_entre_dentro(df, "valor", "grupo", peso="peso")

        assert resumo["theil_entre_grupos"] == pytest.approx(0.0, abs=1e-9)

    def test_medias_diferentes_variancia_zero_theil_entre_e_100_por_cento(self):
        df = pd.DataFrame({
            "valor": [10.0] * 50 + [30.0] * 50,
            "grupo": ["A"] * 50 + ["B"] * 50,
            "peso": 1.0,
        })

        resumo, _ = pnadc_core.decomposicao_theil_entre_dentro(df, "valor", "grupo", peso="peso")

        assert resumo["theil_dentro_grupos"] == pytest.approx(0.0, abs=1e-9)
        assert resumo["pct_entre_grupos"] == pytest.approx(100.0, abs=1e-6)

    def test_grupo_unico_bate_com_theil_t_direto(self):
        rng = np.random.default_rng(1)
        valores = rng.lognormal(mean=8, sigma=0.6, size=200)
        df = pd.DataFrame({"valor": valores, "grupo": "único", "peso": 1.0})

        resumo, _ = pnadc_core.decomposicao_theil_entre_dentro(df, "valor", "grupo", peso="peso")
        theil_direto = pnadc_core.theil_t(valores, np.ones_like(valores))

        assert resumo["theil_total"] == pytest.approx(theil_direto, rel=1e-9)
        assert resumo["theil_entre_grupos"] == pytest.approx(0.0, abs=1e-9)


class TestGiniPonderado:
    """Dois extremos: igualdade perfeita (Gini=0) e concentração total (Gini -> 1)."""

    def test_igualdade_perfeita_gini_zero(self):
        valores = np.full(20, 50.0)
        pesos = np.ones(20)

        gini = pnadc_core.gini_ponderado(valores, pesos)

        assert gini == pytest.approx(0.0, abs=1e-9)

    def test_uma_pessoa_com_toda_renda_gini_proximo_de_um(self):
        n = 10
        valores = np.zeros(n)
        valores[-1] = 100.0
        pesos = np.ones(n)

        gini = pnadc_core.gini_ponderado(valores, pesos)

        # fórmula fechada pra esse caso: Gini = (n-1)/n
        assert gini == pytest.approx((n - 1) / n, abs=1e-9)

    def test_concentracao_extrema_tende_a_um_com_populacao_grande(self):
        n = 1000
        valores = np.zeros(n)
        valores[-1] = 100.0
        pesos = np.ones(n)

        gini = pnadc_core.gini_ponderado(valores, pesos)

        assert gini > 0.99


class TestZerosGiniTheil:
    """E3: a função de Gini mantém zeros; Theil os exclui. A população tem de ser
    definida antes (renda > 0) para que os dois índices falem da mesma população."""

    def test_theil_ignora_zeros_e_gini_nao(self):
        positivos = np.array([10.0, 20.0, 30.0, 40.0])
        com_zeros = np.r_[positivos, [0.0, 0.0]]
        w4, w6 = np.ones(4), np.ones(6)
        assert pnadc_core.theil_t(com_zeros, w6) == pytest.approx(pnadc_core.theil_t(positivos, w4))
        assert pnadc_core.gini_ponderado(com_zeros, w6) > pnadc_core.gini_ponderado(positivos, w4)

    def test_mesma_populacao_quando_filtrada_antes(self):
        y = np.array([0.0, 5.0, 10.0, 0.0, 50.0])
        w = np.array([2.0, 1.0, 1.0, 3.0, 1.0])
        pos = y > 0
        assert pnadc_core.theil_t(y, w) == pytest.approx(pnadc_core.theil_t(y[pos], w[pos]))
        assert pnadc_core.gini_ponderado(y[pos], w[pos]) < pnadc_core.gini_ponderado(y, w)


class TestOaxacaBlinderSintetico:
    """Decomposição com resposta conhecida: mesmos coeficientes nos dois grupos (resíduo
    não explicado = 0) e diferença só de composição em x."""

    def test_decomposicao_conhecida(self):
        rng = np.random.default_rng(5)
        n = 4000
        grupo = np.repeat(["A", "B"], n // 2)
        # A tem mais x=1 (70%) que B (30%); y = 1 + 0,5·x + ruído pequeno, iguais nos grupos
        x = np.where(grupo == "A", rng.random(n) < 0.7, rng.random(n) < 0.3).astype(int)
        y = 1 + 0.5 * x + rng.normal(0, 0.01, n)
        df = pd.DataFrame({"y": y, "x": x.astype(str), "g": grupo, "w": 1.0, "upa": np.arange(n) // 4})
        r = pnadc_core.decomposicao_oaxaca_blinder(df, "y", ["x"], "w", "g", "A", "B", cluster="upa")
        diferenca_x = x[grupo == "A"].mean() - x[grupo == "B"].mean()
        assert r["hiato_total"] == pytest.approx(0.5 * diferenca_x, abs=2e-3)
        assert r["parcela_explicada"] == pytest.approx(0.5 * diferenca_x, abs=2e-3)
        assert r["parcela_nao_explicada"] == pytest.approx(0.0, abs=2e-3)
        assert r["parcela_explicada"] + r["parcela_nao_explicada"] == pytest.approx(r["hiato_total"])

    def test_residuo_puro(self):
        rng = np.random.default_rng(6)
        n = 4000
        grupo = np.repeat(["A", "B"], n // 2)
        x = (rng.random(n) < 0.5).astype(int)
        y = 1 + 0.3 * (grupo == "A") + 0.5 * x + rng.normal(0, 0.01, n)
        df = pd.DataFrame({"y": y, "x": x.astype(str), "g": grupo, "w": 1.0, "upa": np.arange(n) // 4})
        r = pnadc_core.decomposicao_oaxaca_blinder(df, "y", ["x"], "w", "g", "A", "B", cluster="upa")
        assert r["parcela_nao_explicada"] == pytest.approx(0.3, abs=0.01)
        assert r["residuo_restrito_coef"] == pytest.approx(0.3, abs=0.01)


def test_deflator_ipea_removido():
    """E4: funções de deflator do IPEA (dividiam o nominal) não podem voltar."""
    assert not hasattr(pnadc_core, "aplicar_deflator")
    assert not hasattr(pnadc_core, "carregar_deflator")
