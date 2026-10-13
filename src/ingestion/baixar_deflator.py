"""Baixa o deflator OFICIAL do IBGE para a PNAD Contínua Trimestral.

O IBGE publica, na mesma pasta de documentação dos microdados, uma planilha com o
deflator de rendimentos (habitual e efetivo) por UF e trimestre — pensado
especificamente para converter os valores nominais de renda em valores reais a
preços do trimestre de referência mais recente. É a fonte preferencial (mais
autoritativa e já alinhada à granularidade UF/trimestre da PNAD Contínua) — não
usamos o deflator do IPEA.

Fonte: https://ftp.ibge.gov.br/.../Trabalho_e_Rendimento/.../Microdados/Documentacao/Deflatores.zip
(o nome do .xls dentro do zip muda a cada trimestre — ex.: deflator_PNADC_2026_trimestral_040506.xls
— por isso pegamos dinamicamente o único arquivo .xls presente no zip, em vez de fixar o nome.)

IMPORTANTE sobre a direção da conversão: o deflator do IBGE é o fator pelo qual se
MULTIPLICA o valor nominal para obter o valor real a preços do trimestre de
referência (o trimestre de referência tem deflator = 1.0; trimestres mais antigos
têm deflator > 1, porque R$1 de anos atrás vale mais em termos de hoje).
`renda_real = renda_nominal * deflator` — NÃO divida.

Uso:
    python -m src.ingestion.baixar_deflator
"""
import zipfile
from pathlib import Path

import pandas as pd
import requests

URL_DEFLATORES_ZIP = (
    "https://ftp.ibge.gov.br/Trabalho_e_Rendimento/"
    "Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/"
    "Documentacao/Deflatores.zip"
)
HEADERS = {"User-Agent": "Mozilla/5.0 (datahub-racial-brasil)"}

REPO_ROOT = Path(__file__).resolve().parents[2]
TMP_DIR = REPO_ROOT / "data" / "raw" / "pnadc_extraido" / "_tmp" / "deflatores"
DESTINO = REPO_ROOT / "data" / "processed" / "deflator_ibge.parquet"

# Só os 4 "trim" (janela móvel de meses) que coincidem com os trimestres fixos da
# PNAD Contínua Trimestral. As outras 8 janelas móveis por ano são usadas pela PNAD
# Contínua Mensal, que este projeto não usa.
TRIM_PARA_TRIMESTRE = {"01-02-03": 1, "04-05-06": 2, "07-08-09": 3, "10-11-12": 4}


def baixar_e_processar() -> pd.DataFrame:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    destino_zip = TMP_DIR / "Deflatores.zip"

    r = requests.get(URL_DEFLATORES_ZIP, headers=HEADERS, timeout=60)
    r.raise_for_status()
    destino_zip.write_bytes(r.content)

    with zipfile.ZipFile(destino_zip) as z:
        nomes_xls = [n for n in z.namelist() if n.lower().endswith(".xls")]
        if len(nomes_xls) != 1:
            raise RuntimeError(f"Esperava 1 arquivo .xls no zip, encontrei {len(nomes_xls)}: {nomes_xls}")
        z.extractall(TMP_DIR)
        caminho_xls = TMP_DIR / nomes_xls[0]

    df = pd.read_excel(caminho_xls, sheet_name="deflator", engine="xlrd", header=0)
    df = df[df["trim"].isin(TRIM_PARA_TRIMESTRE)].copy()
    df["trimestre"] = df["trim"].map(TRIM_PARA_TRIMESTRE)
    df["UF"] = df["UF"].astype(str)  # base da PNAD lê UF como texto — precisa bater no join
    df = df.rename(columns={
        "Ano": "ano",
        "Habitual": "deflator_habitual",
        "Efetivo": "deflator_efetivo",
    })[["ano", "trimestre", "UF", "deflator_habitual", "deflator_efetivo"]]

    return df.sort_values(["ano", "trimestre", "UF"]).reset_index(drop=True)


def main() -> None:
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    df = baixar_e_processar()
    df.to_parquet(DESTINO, index=False)
    trimestre_referencia = df[
        (df["deflator_habitual"] == 1.0)
    ][["ano", "trimestre"]].drop_duplicates()
    print(f"deflator_ibge.parquet: {len(df):,} linhas".replace(",", "."))
    print(f"Trimestre de referência (deflator=1.0): {trimestre_referencia.to_dict('records')}")


if __name__ == "__main__":
    main()
