"""Golden-file da pipeline CRIAR_BASE → agregação → saída sobre microdado SINTÉTICO (B5).

Falha se qualquer mudança de código alterar estimativas pontuais, erros-padrão, IC ou
p-valores dessas saídas. Mudança intencional: regerar com
`python -m tests.golden.microdado_sintetico --regerar-esperado` e registrar no
docs/CHANGELOG_METODOLOGICO.md.
"""
import pandas as pd
import pytest

from tests.golden.microdado_sintetico import PASTA_GOLDEN, gerar_microdado, ordenar, rodar_pipeline


def test_microdado_sintetico_deterministico():
    a, b = gerar_microdado(), gerar_microdado()
    pd.testing.assert_frame_equal(a, b)
    assert 4500 <= len(a) <= 5500


@pytest.mark.parametrize("nome", ["renda", "hiato_racial"])
def test_saida_bate_com_golden(tmp_path, nome):
    obtido = ordenar(nome, rodar_pipeline(tmp_path)[nome])
    esperado = pd.read_parquet(PASTA_GOLDEN / f"esperado_{nome}.parquet")
    pd.testing.assert_frame_equal(obtido, esperado, check_dtype=False, rtol=1e-9, atol=1e-9)


def test_golden_hiato_tem_inferencia_design_based(tmp_path):
    """O hiato sintético tem IC finito e não degenerado (fórmula antiga daria IC ~20x
    mais estreito com esses pesos)."""
    h = rodar_pipeline(tmp_path)["hiato_racial"]
    largura = (h["ic_superior"] - h["ic_inferior"]) / h["hiato_absoluto"].abs()
    assert (largura > 0.05).all()
    assert {"significativo_nominal", "significativo_fdr", "p_valor_bh"} <= set(h.columns)
