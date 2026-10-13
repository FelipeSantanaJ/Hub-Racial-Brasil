"""Agregações raciais do tema Habitação (PNAD Contínua, Visita 1 anual).

Constrói indicadores binários/contínuos de precariedade habitacional a partir das
variáveis S01xxx extraídas por `src/ingestion/extrator_pnadc_visita_anual.py`, e calcula
o hiato racial (recorte 1: Branca/Preta/Parda/Negra/Indígena) e racial×gênero
(recorte 2: 10 grupos) desses indicadores, ano a ano, com significância Welch — mesma
metodologia já usada em toda a Fase 1 (renda/educação/ocupação).

Uso:
    python -m src.processing.agregacoes_habitacao
"""
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from src.inference.saida import salvar_com_inferencia, salvar_tabela

from src.utils import pnadc_core as core

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "data" / "raw" / "pnadc_anual_visita1" / "parquet"
OUT_DIR = REPO_ROOT / "data" / "processed"

# Peso amostral da divulgação ANUAL (distinto do V1028 trimestral usado no resto do
# projeto) — ver docs/PLANO.md, seção Fase 2.5.
PESO = "V1032"

# Limiar de adensamento excessivo (pessoas por cômodo-dormitório). Convenção usada na
# literatura de déficit habitacional brasileira (FGV/FJP): >2 é o limiar mais comum
# para "adensamento excessivo" em domicílios com dormitório(s) — documentado aqui como
# escolha metodológica explícita, não um padrão único e incontestável do IBGE.
LIMIAR_ADENSAMENTO_EXCESSIVO = 2


def carregar_base() -> pd.DataFrame:
    con = duckdb.connect()
    # union_by_name=True: cada ano tem um subconjunto diferente de colunas S01xxx
    # (ver docs/PLANO.md, Fase 2.5 — nome da variável mudou de ano pra ano); sem essa
    # opção o DuckDB exige exatamente o mesmo schema em todos os arquivos do glob.
    df = con.execute(
        f"SELECT * FROM read_parquet('{RAW_DIR.as_posix()}/ano=*/*.parquet', "
        f"hive_partitioning=1, union_by_name=True)"
    ).df()
    return df


def construir_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    """Cria as colunas de indicador habitacional a partir das variáveis S01xxx cruas.

    S01007/S01002/S01017 são a MESMA variável (mesmo código) em todos os 8 anos —
    nenhuma harmonização necessária. S01011/S01012 mudaram de nome (não de sentido, com
    a única exceção documentada abaixo) entre os anos — usa `combine_first` pra juntar
    nome antigo e novo na mesma coluna lógica.
    """
    df = df.copy()

    # --- Esgotamento sanitário adequado: rede geral/pluvial ou fossa séptica ligada à
    # rede. CUIDADO: S01012 (até 2018) e S01012A (2019+) NÃO têm os mesmos códigos —
    # descoberto por uma quebra de nível suspeita (~95% -> ~60%) bem na fronteira exata
    # da troca de variável, que teria passado batido sem checar o dicionário de cada
    # período. S01012 código 1 = "Rede geral, rede pluvial OU fossa ligada à rede" (já
    # junta as duas categorias que só em S01012A viram códigos separados: 1=rede geral,
    # 2=fossa séptica ligada à rede). Ou seja, "adequado" é código 1 no antigo, mas
    # códigos 1 OU 2 no novo — construir o booleano SEPARADO por variável de origem
    # antes de unificar, nunca aplicar a mesma regra de código às duas.
    col_vazia = pd.Series(np.nan, index=df.index)
    s01012 = df.get("S01012", col_vazia)
    s01012a = df.get("S01012A", col_vazia)
    adequado_antigo = s01012 == "1"
    adequado_novo = s01012a.isin(["1", "2"])
    tem_dado = s01012.notna() | s01012a.notna()
    df["esgoto_adequado"] = np.where(tem_dado, (adequado_antigo | adequado_novo).astype(float), np.nan)

    # --- Água de rede geral de distribuição (idêntico em todos os anos, sem harmonização)
    df["agua_rede_geral"] = np.where(df["S01007"].isna(), np.nan, (df["S01007"] == "1").astype(float))

    # --- Parede de alvenaria (com ou sem revestimento) vs. taipa/madeira/outro
    # (idêntico em todos os anos, sem harmonização)
    df["parede_alvenaria"] = np.where(df["S01002"].isna(), np.nan, df["S01002"].isin(["1", "2"]).astype(float))

    # --- Imóvel próprio (pago ou ainda pagando) vs. alugado/cedido/outra condição
    # (idêntico em todos os anos, sem harmonização)
    df["imovel_proprio"] = np.where(df["S01017"].isna(), np.nan, df["S01017"].isin(["1", "2"]).astype(float))

    # --- Tem banheiro de uso exclusivo dos moradores. S01011 (até 2016) conta
    # "banheiros, sanitários OU buracos para dejeções" numa única pergunta; S01011A
    # (2017+) conta só banheiro de verdade (chuveiro/vaso), com "usa buraco" separado em
    # S01011C. Ou seja: só em 2016 esse indicador pode incluir um domicílio com buraco
    # mas sem banheiro de verdade como "tem banheiro" — diferença pequena (1 de 8 anos),
    # documentada aqui e em LIMITACOES_E_METODOLOGIA.md, não escondida.
    banheiro_antigo = pd.to_numeric(df.get("S01011"), errors="coerce")
    banheiro_novo = pd.to_numeric(df.get("S01011A"), errors="coerce")
    banheiro = banheiro_antigo.combine_first(banheiro_novo) if banheiro_antigo is not None else banheiro_novo
    df["tem_banheiro_exclusivo"] = np.where(banheiro.isna(), np.nan, (banheiro >= 1).astype(float))

    # --- Adensamento: moradores por cômodo-dormitório. V2001 = pessoas no domicílio,
    # S01006 = cômodos servindo de dormitório (0 tratado como NaN pra evitar divisão por
    # zero — domicílio sem cômodo-dormitório dedicado é caso raro/residual, não um "0"
    # informativo pra essa razão).
    moradores = pd.to_numeric(df["V2001"], errors="coerce")
    dormitorios = pd.to_numeric(df["S01006"], errors="coerce").replace(0, np.nan)
    df["adensamento"] = moradores / dormitorios
    df["adensamento_excessivo"] = np.where(
        df["adensamento"].isna(), np.nan,
        (df["adensamento"] > LIMIAR_ADENSAMENTO_EXCESSIVO).astype(float),
    )

    return df


INDICADORES = [
    "esgoto_adequado", "agua_rede_geral", "parede_alvenaria",
    "imovel_proprio", "tem_banheiro_exclusivo", "adensamento_excessivo",
]


def hiato_por_ano(df: pd.DataFrame, col_grupo: str, grupo_referencia: str) -> pd.DataFrame:
    """Roda `tabela_hiatos_significancia` pra cada indicador x ano, empilhando o resultado."""
    linhas = []
    for ano, df_ano in df.groupby("ano"):
        for indicador in INDICADORES:
            sub = df_ano.dropna(subset=[indicador, PESO, col_grupo])
            if sub.empty or grupo_referencia not in sub[col_grupo].unique():
                continue
            tabela = core.tabela_hiatos_significancia(
                sub, coluna_valor=indicador, col_grupo=col_grupo,
                grupo_referencia=grupo_referencia, peso=PESO, upa="UPA", estrato="Estrato",
            ).reset_index()
            tabela["ano"] = ano
            tabela["indicador"] = indicador
            linhas.append(tabela)
    return pd.concat(linhas, ignore_index=True)


def _salvar(tabela: pd.DataFrame, destino, familia: list[str]) -> None:
    """Grava com FDR por família e _meta.json (B2/B3 da auditoria). A linha do grupo de
    referência não é um teste (hiato 0, p = 1 por convenção): o p-valor dela vira NaN para
    não entrar no tamanho da família do Benjamini-Hochberg."""
    tabela = tabela.copy()
    tabela.loc[tabela["hiato_media"] == 0, "p_valor"] = np.nan
    salvar_com_inferencia(tabela, destino, familia=familia)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Carregando base (8 anos, Visita 1)...")
    df = carregar_base()
    print(f"{len(df):,} linhas carregadas.".replace(",", "."))

    df = construir_indicadores(df)
    # ORDEM IMPORTA: aplicar_recorte2 também escreve uma coluna 'raca_cor' interna (sem
    # agregar Preta+Parda em Negra) além de 'grupo' — se rodasse depois de
    # aplicar_recorte1, sobrescreveria o 'raca_cor' já agregado deste. aplicar_recorte1
    # por último garante que 'raca_cor' final fica agregado (Negra), sem afetar 'grupo'.
    df = core.aplicar_recorte2(df)
    df = core.aplicar_recorte1(df)
    df = core.preparar_niveis_geograficos(df)

    print("Calculando hiato racial (recorte 1: Branca/Preta/Parda/Negra/Indígena)...")
    hiato_racial = hiato_por_ano(df, col_grupo="raca_cor", grupo_referencia="Branca")
    _salvar(hiato_racial, OUT_DIR / "habitacao_hiato_racial.parquet", familia=["ano", "indicador"])

    print("Calculando hiato racial x gênero (recorte 2: 10 grupos)...")
    hiato_genero = hiato_por_ano(df, col_grupo="grupo", grupo_referencia="Homens Brancos")
    _salvar(hiato_genero, OUT_DIR / "habitacao_hiato_racial_genero.parquet", familia=["ano", "indicador"])

    print("Calculando hiato racial por região (pooled, todos os 8 anos)...")
    linhas_regiao = []
    for regiao, df_regiao in df.groupby("regiao", observed=True):
        for indicador in INDICADORES:
            sub = df_regiao.dropna(subset=[indicador, PESO, "raca_cor"])
            if sub.empty:
                continue
            tabela = core.tabela_hiatos_significancia(
                sub, coluna_valor=indicador, col_grupo="raca_cor",
                grupo_referencia="Branca", peso=PESO, upa="UPA", estrato="Estrato",
            ).reset_index()
            tabela["regiao"] = regiao
            tabela["indicador"] = indicador
            linhas_regiao.append(tabela)
    hiato_regiao = pd.concat(linhas_regiao, ignore_index=True)
    _salvar(hiato_regiao, OUT_DIR / "habitacao_hiato_regional.parquet", familia=["regiao", "indicador"])

    print("\nResumo 2025, recorte racial (Branca = referência):")
    print(
        hiato_racial[hiato_racial["ano"] == 2025]
        .pivot(index="raca_cor", columns="indicador", values="media")
        .round(3)
    )


if __name__ == "__main__":
    main()
