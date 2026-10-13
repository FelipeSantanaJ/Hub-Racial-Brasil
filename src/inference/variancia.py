"""Variância *design-based* para a PNAD Contínua (correção do E1 da auditoria Rodada 1).

Desenho tratado: amostragem estratificada (`Estrato`) de conglomerados (`UPA`), com um
estágio de UPA e seleção tratada como com reposição dentro do estrato — a aproximação
usual de "último estágio" (ultimate cluster) para pesquisas domiciliares complexas.
Referências (de memória, *a confirmar* antes de citar em texto público): Cochran (1977),
cap. 5 e 11; Wolter (2007), *Introduction to Variance Estimation*; Lumley (2010),
*Complex Surveys*.

Estimador de variância por linearização de Taylor da média ponderada (razão de totais):

    ȳ_w  = Σ w_i y_i / Σ w_i
    z_i  = w_i (y_i − ȳ_w) / Σ w_i                       (variável linearizada)
    z_hj = Σ_{i ∈ UPA j do estrato h} z_i                (total por UPA)
    Var  = Σ_h n_h/(n_h−1) Σ_j (z_hj − z̄_h)²             (n_h = nº de UPAs no estrato h)

Propriedades (testadas em tests/test_variancia.py): invariante a w → c·w; igual a s/√n
quando os pesos são iguais e cada observação é a sua própria UPA num estrato único.

**Domínios (subpopulações).** Para a média de um grupo (ex.: Negra), o estimador correto
NÃO recorta a amostra antes de calcular: mantém todas as UPAs do universo passado e zera
z_i fora do domínio (Cochran 1977, §2.13; Lumley 2010, cap. 2 — *a confirmar*). Recortar
antes descarta UPAs sem ninguém do grupo, muda n_h e cria estratos de UPA única
artificiais. Aqui o "universo" é o DataFrame passado (ex.: ocupados com renda do
trimestre); UPAs inteiramente fora dele não entram — aproximação documentada.

**Estratos com uma só UPA (lonely PSU).** Política explícita, nunca descarte silencioso:
`"centrar_media_geral"` (padrão; equivale a `options(survey.lonely.psu = "adjust")` do
pacote `survey` do R — *a confirmar*) centra o total da UPA solitária na média de TODOS os
totais de UPA em vez da média do estrato (que seria ela mesma, variância zero). Como
Σ z_i = 0, essa média geral é ≈ 0 e a contribuição é z_hj². `"erro"` levanta exceção.
O número de estratos afetados é sempre devolvido nos diagnósticos.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

POLITICAS_UPA_UNICA = ("centrar_media_geral", "erro")
SE_METODO = "linearizacao_taylor_estrato_upa"


@dataclass(frozen=True)
class DiagnosticoDesenho:
    """Resumo do desenho efetivamente usado num cálculo de variância."""
    n_obs: int
    n_upas: int
    n_estratos: int
    n_estratos_upa_unica: int

    @property
    def graus_liberdade(self) -> int:
        """Graus de liberdade do desenho: nº de UPAs − nº de estratos (Korn & Graubard,
        1990 — *a confirmar*)."""
        return max(self.n_upas - self.n_estratos, 1)


def _arrays(*cols):
    return [np.asarray(c) for c in cols]


def _mascara_valida(y, w, upa, estrato):
    y = np.asarray(y, dtype=float)
    w = np.asarray(w, dtype=float)
    upa_s = pd.Series(np.asarray(upa, dtype=object))
    est_s = pd.Series(np.asarray(estrato, dtype=object))
    return (~np.isnan(y)) & (~np.isnan(w)) & (w > 0) & upa_s.notna().to_numpy() & est_s.notna().to_numpy()


def _codigos_upa_estrato(upa, estrato):
    """Códigos inteiros 0..J-1 para cada UPA (aninhada no estrato) e 0..H-1 para o estrato
    de cada UPA. A chave da UPA é (estrato, upa) para não supor códigos únicos entre estratos."""
    est_cod, est_uniq = pd.factorize(pd.Series(estrato, dtype=object), sort=True)
    chave = pd.MultiIndex.from_arrays([est_cod, pd.Series(upa, dtype=object)])
    upa_cod, upa_uniq = pd.factorize(chave, sort=True)
    estrato_da_upa = np.asarray(upa_uniq.get_level_values(0))
    return upa_cod, estrato_da_upa, len(est_uniq)


def variancia_linearizada(z, upa, estrato, politica_upa_unica: str = "centrar_media_geral"):
    """Variância *design-based* do total Σ z_i (z já linearizado), estratificado por
    `estrato` e conglomerado por `upa`. Devolve (variância, DiagnosticoDesenho).

    Aceita z matricial (n × k) para estimar a matriz de covariância de k estatísticas de
    uma vez (usado na diferença de médias)."""
    if politica_upa_unica not in POLITICAS_UPA_UNICA:
        raise ValueError(f"politica_upa_unica deve ser uma de {POLITICAS_UPA_UNICA}")
    z = np.asarray(z, dtype=float)
    matricial = z.ndim == 2
    z2 = z if matricial else z[:, None]
    upa_cod, estrato_da_upa, n_estratos = _codigos_upa_estrato(upa, estrato)
    n_upas = len(estrato_da_upa)

    totais = np.zeros((n_upas, z2.shape[1]))
    np.add.at(totais, upa_cod, z2)

    n_h = np.bincount(estrato_da_upa, minlength=n_estratos)
    soma_h = np.zeros((n_estratos, z2.shape[1]))
    np.add.at(soma_h, estrato_da_upa, totais)
    media_h = soma_h / n_h[:, None]

    unica = n_h[estrato_da_upa] == 1
    n_unica = int((n_h == 1).sum())
    if n_unica and politica_upa_unica == "erro":
        raise ValueError(f"{n_unica} estrato(s) com uma única UPA")

    desvio = totais - media_h[estrato_da_upa]
    fator = np.where(unica, 1.0, n_h[estrato_da_upa] / np.maximum(n_h[estrato_da_upa] - 1, 1))
    if n_unica:
        media_geral = totais.mean(axis=0)
        desvio[unica] = totais[unica] - media_geral
    cov = (desvio * fator[:, None]).T @ desvio

    diag = DiagnosticoDesenho(int(len(z)), int(n_upas), int(n_estratos), n_unica)
    return (cov if matricial else float(cov[0, 0])), diag


def influencia_media(y, w, dominio=None):
    """Variável linearizada da média ponderada de `y` no `dominio` (máscara booleana;
    None = todos). Fora do domínio z_i = 0 (estimação de domínio). Devolve (z, média)."""
    y = np.asarray(y, dtype=float)
    w = np.asarray(w, dtype=float)
    d = np.ones(len(y), dtype=bool) if dominio is None else np.asarray(dominio, dtype=bool)
    wd = np.where(d, w, 0.0)
    total_w = wd.sum()
    if total_w <= 0:
        return np.zeros(len(y)), np.nan
    media = float(np.sum(wd * np.where(d, y, 0.0)) / total_w)
    z = np.where(d, wd * (y - media) / total_w, 0.0)
    return z, media


def erro_padrao_media_design(y, w, upa, estrato, dominio=None,
                             politica_upa_unica: str = "centrar_media_geral", diagnostico: bool = False):
    """Erro-padrão da média ponderada de `y` por linearização (Estrato/UPA).

    `dominio` (máscara booleana do mesmo tamanho) estima a média de uma subpopulação sem
    recortar a amostra. Linhas com y/w/upa/estrato ausentes ou peso ≤ 0 são ignoradas.
    `diagnostico=True` devolve (ep, DiagnosticoDesenho)."""
    y, w, upa, estrato = _arrays(y, w, upa, estrato)
    ok = _mascara_valida(y, w, upa, estrato)
    dom = ok if dominio is None else ok & np.asarray(dominio, dtype=bool)
    if dom.sum() < 2:
        return (np.nan, None) if diagnostico else np.nan
    z, _ = influencia_media(y[ok], w[ok], dom[ok])
    var, diag = variancia_linearizada(z, upa[ok], estrato[ok], politica_upa_unica)
    ep = float(np.sqrt(max(var, 0.0)))
    return (ep, diag) if diagnostico else ep


def diferenca_medias_design(y, w, upa, estrato, dominio_a, dominio_b,
                            politica_upa_unica: str = "centrar_media_geral") -> dict:
    """Diferença ȳ_a − ȳ_b entre dois domínios com erro-padrão que INCLUI a covariância
    entre as duas médias (os grupos são pessoas diferentes, mas dividem UPAs: tratar as
    médias como independentes, como fazia `tabela_hiatos_significancia`, ignora isso).

    Devolve dict com media_a, media_b, diferenca, ep_a, ep_b, ep_diferenca, cov_ab e
    o diagnóstico do desenho."""
    y, w, upa, estrato = _arrays(y, w, upa, estrato)
    ok = _mascara_valida(y, w, upa, estrato)
    da = ok & np.asarray(dominio_a, dtype=bool)
    db = ok & np.asarray(dominio_b, dtype=bool)
    za, ma = influencia_media(y[ok], w[ok], da[ok])
    zb, mb = influencia_media(y[ok], w[ok], db[ok])
    cov, diag = variancia_linearizada(np.column_stack([za, zb]), upa[ok], estrato[ok], politica_upa_unica)
    var_dif = cov[0, 0] + cov[1, 1] - 2 * cov[0, 1]
    return {
        "media_a": ma, "media_b": mb, "diferenca": ma - mb,
        "ep_a": float(np.sqrt(max(cov[0, 0], 0.0))), "ep_b": float(np.sqrt(max(cov[1, 1], 0.0))),
        "cov_ab": float(cov[0, 1]), "ep_diferenca": float(np.sqrt(max(var_dif, 0.0))),
        "n_a": int(da.sum()), "n_b": int(db.sum()), "diagnostico": diag,
    }


def razao_delta_design(z_num, z_den, num: float, den: float, upa, estrato,
                       politica_upa_unica: str = "centrar_media_geral") -> float:
    """EP de num/den por método delta, dados os z linearizados de num e de den (mesma
    amostra): z_r = (z_num − (num/den)·z_den)/den."""
    z = (np.asarray(z_num) - (num / den) * np.asarray(z_den)) / den
    var, _ = variancia_linearizada(z, upa, estrato, politica_upa_unica)
    return float(np.sqrt(max(var, 0.0)))


def _agregados_upa(y, w, upa, estrato, dominios):
    """Σ w·y e Σ w por UPA para cada domínio — base do bootstrap (reamostrar UPAs inteiras
    é idêntico a reamostrar esses agregados)."""
    upa_cod, estrato_da_upa, n_estratos = _codigos_upa_estrato(upa, estrato)
    n_upas = len(estrato_da_upa)
    sw, swy = [], []
    for d in dominios:
        wd = np.where(d, w, 0.0)
        sw.append(np.bincount(upa_cod, weights=wd, minlength=n_upas))
        swy.append(np.bincount(upa_cod, weights=wd * np.where(d, y, 0.0), minlength=n_upas))
    return np.array(sw), np.array(swy), estrato_da_upa, n_estratos


def erro_padrao_bootstrap_estrato_upa(y, w, upa, estrato, dominio_a=None, dominio_b=None,
                                      n_boot: int = 500, seed: int = 0) -> float:
    """Erro-padrão por bootstrap de Rao-Wu (1988, *JASA* — *a confirmar*) que reamostra
    UPAs **dentro de cada estrato**: em cada réplica, sorteia n_h − 1 UPAs com reposição
    no estrato h e reescala os pesos por n_h/(n_h − 1) × multiplicidade. Com m_h = n_h − 1
    o estimador de variância do bootstrap é não viesado para o caso linear (o bootstrap
    ingênuo com n_h sorteios subestima por (n_h − 1)/n_h).

    Estatística: média de `dominio_a` (ou de todos), ou a diferença
    média(dominio_a) − média(dominio_b) se `dominio_b` for passado. Estratos com uma única
    UPA ficam fixos (contribuem zero) — política diferente da linearização, de propósito:
    é uma checagem independente, não uma cópia da mesma convenção.

    Substitui, como checagem, `pnadc_core.erro_padrao_cluster_bootstrap` (que reamostra UPA
    ignorando o estrato)."""
    y, w, upa, estrato = _arrays(y, w, upa, estrato)
    ok = _mascara_valida(y, w, upa, estrato)
    y, w, upa, estrato = y[ok], w[ok], upa[ok], estrato[ok]
    da = np.ones(len(y), bool) if dominio_a is None else np.asarray(dominio_a, bool)[ok]
    doms = [da] if dominio_b is None else [da, np.asarray(dominio_b, bool)[ok]]
    sw, swy, estrato_da_upa, n_estratos = _agregados_upa(y, w, upa, estrato, doms)

    ordem = np.argsort(estrato_da_upa, kind="stable")
    n_h = np.bincount(estrato_da_upa, minlength=n_estratos)
    inicio = np.concatenate([[0], np.cumsum(n_h)[:-1]])
    m_h = np.maximum(n_h - 1, 0)
    estr_sorteio = np.repeat(np.arange(n_estratos), m_h)
    fator_upa = np.where(n_h > 1, n_h / np.maximum(n_h - 1, 1), 1.0)[estrato_da_upa]
    fixas = n_h[estrato_da_upa] == 1

    rng = np.random.default_rng(seed)
    n_upas = len(estrato_da_upa)
    reps = np.empty(n_boot)
    for b in range(n_boot):
        pos = inicio[estr_sorteio] + np.floor(rng.random(len(estr_sorteio)) * n_h[estr_sorteio]).astype(int)
        mult = np.bincount(ordem[pos], minlength=n_upas).astype(float)
        a = np.where(fixas, 1.0, mult * fator_upa)
        medias = (swy @ a) / (sw @ a)
        reps[b] = medias[0] if len(medias) == 1 else medias[0] - medias[1]
    return float(np.std(reps, ddof=1))


def erro_padrao_media_replicados(y, w, pesos_replicados, fator_escala: float) -> float:
    """EP da média ponderada a partir de pesos replicados (n × R):
    Var = fator_escala · Σ_r (θ_r − θ)².

    `fator_escala` NÃO tem padrão de propósito: depende de como o IBGE gerou as réplicas
    da PNADC (bootstrap? com que reescala?) — **NÃO VERIFICADO** na documentação. Para um
    bootstrap simples, fator = 1/R; para BRR, 1/R; para jackknife JK1, (R−1)/R. Sem uso em
    produção (decisão de 12/10/2026: réplicas não extraídas)."""
    y = np.asarray(y, dtype=float)
    w = np.asarray(w, dtype=float)
    W = np.asarray(pesos_replicados, dtype=float)
    ok = ~np.isnan(y) & ~np.isnan(w) & (w > 0)
    theta = np.sum(w[ok] * y[ok]) / np.sum(w[ok])
    theta_r = (W[ok] * y[ok, None]).sum(axis=0) / W[ok].sum(axis=0)
    return float(np.sqrt(fator_escala * np.sum((theta_r - theta) ** 2)))


def n_efetivo_desenho(y, w, ep: float) -> float:
    """Tamanho de amostra efetivo do desenho: s²_w / EP², onde s²_w é a variância
    populacional ponderada de y. Incorpora o efeito de desenho (pesos desiguais +
    conglomeração): n_ef = n / deff. Usado nos graus de liberdade de Welch."""
    y = np.asarray(y, dtype=float)
    w = np.asarray(w, dtype=float)
    ok = ~np.isnan(y) & ~np.isnan(w) & (w > 0)
    if ok.sum() < 2 or not ep or np.isnan(ep):
        return np.nan
    m = np.average(y[ok], weights=w[ok])
    s2 = np.average((y[ok] - m) ** 2, weights=w[ok])
    return float(s2 / ep**2)


def graus_liberdade_welch(ep1: float, ep2: float, n1: float, n2: float) -> float:
    """Welch-Satterthwaite com o EP da média já calculado (corrige o E2):
    df = (ep1² + ep2²)² / (ep1⁴/(n1−1) + ep2⁴/(n2−1)).
    A versão antiga dividia ep² por n de novo, como se ep² fosse a variância de y."""
    if n1 <= 1 or n2 <= 1:
        return np.nan
    num = (ep1**2 + ep2**2) ** 2
    den = ep1**4 / (n1 - 1) + ep2**4 / (n2 - 1)
    return float(num / den) if den > 0 else np.nan
