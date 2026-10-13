"""Extrai a série histórica da PNAD Contínua Trimestral (IBGE) direto do FTP público.

Baixa cada trimestre (zip de microdados de largura fixa), interpreta o layout SAS
oficial, seleciona as colunas de interesse do projeto e grava em Parquet particionado
por ano/trimestre (data/raw/pnadc_extraido/parquet/ano=AAAA/trimestre=T/parte_NNNN.parquet).

Idempotente: um trimestre já processado (marcador _SUCCESS) é pulado. Pode ser
reexecutado a qualquer momento para só buscar trimestres novos.

Uso:
    python -m src.ingestion.extrator_pnadc                  # série completa 2012-atual
    python -m src.ingestion.extrator_pnadc --ano-inicial 2026 --ano-final 2026
"""
import argparse
import os
import re
import time
import zipfile
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

BASE_URL = (
    "https://ftp.ibge.gov.br/Trabalho_e_Rendimento/"
    "Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados"
)
DOC_URL = f"{BASE_URL}/Documentacao/"

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "data" / "raw" / "pnadc_extraido" / "parquet"
RAW_TMP_DIR = REPO_ROOT / "data" / "raw" / "pnadc_extraido" / "_tmp"

CHUNKSIZE = 200_000
HEADERS = {"User-Agent": "Mozilla/5.0 (datahub-racial-brasil)"}

# Colunas mantidas na base final: identificação/desenho amostral, geografia (incl.
# RM_RIDE para Região Metropolitana), demografia, educação, mercado de trabalho e
# rendimento. "ano"/"trimestre" não entram aqui: viram colunas de partição via
# hive partitioning (ano=/trimestre=) ao ler com DuckDB.
VARIAVEIS_DESEJADAS = [
    # identificação / desenho amostral
    "UF", "Capital", "RM_RIDE", "UPA", "Estrato",
    "V1008", "V1014", "V1016", "V1022", "V1023", "V1028",
    # domicílio / pessoa
    "V2001", "V2003", "V2005", "V2007", "V2008", "V20081", "V20082",
    "V2009", "V2010",
    # educação
    "VD3004", "VD3005",
    # mercado de trabalho (condição, ocupação, posição, rendimento)
    "VD4001", "VD4002", "VD4003", "VD4004A", "VD4005", "VD4008",
    "VD4009", "VD4010", "VD4011", "VD4012", "VD4016", "VD4017",
    "VD4019", "VD4020",
    # outras
    "V3001", "V3009A", "V3014", "VD4031", "VD4035",
]


def listar_diretorio(url: str, tentativas: int = 4) -> list[str]:
    """Retorna a lista de nomes de arquivos/pastas de um índice do FTP HTTP do IBGE."""
    for i in range(tentativas):
        try:
            r = requests.get(url, headers=HEADERS, timeout=60)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            nomes = []
            for a in soup.find_all("a"):
                href = a.get("href", "")
                if href in ("../", "/") or href.startswith("?"):
                    continue
                nomes.append(href)
            return nomes
        except Exception as e:
            print(f"  tentativa {i + 1} falhou para {url}: {e}")
            time.sleep(3)
    raise RuntimeError(f"Não foi possível listar {url}")


def baixar_arquivo(url: str, destino: Path, tentativas: int = 4) -> Path:
    """Baixa um arquivo com streaming, pulando se já existir (retomada simples)."""
    if destino.exists() and destino.stat().st_size > 0:
        return destino
    for i in range(tentativas):
        try:
            with requests.get(url, headers=HEADERS, stream=True, timeout=120) as r:
                r.raise_for_status()
                tmp = destino.with_suffix(destino.suffix + ".part")
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                tmp.rename(destino)
            return destino
        except Exception as e:
            print(f"  tentativa {i + 1} falhou para {url}: {e}")
            time.sleep(5)
    raise RuntimeError(f"Não foi possível baixar {url}")


def encontrar_zip_trimestre(ano: int, trimestre: int) -> str | None:
    """Procura, na pasta do ano, o zip de dados do trimestre."""
    url_ano = f"{BASE_URL}/{ano}/"
    try:
        arquivos = listar_diretorio(url_ano)
    except Exception:
        return None
    padrao = re.compile(rf"^PNADC_{trimestre:02d}{ano}.*\.zip$", re.IGNORECASE)
    candidatos = sorted(a for a in arquivos if padrao.match(a))
    return url_ano + candidatos[-1] if candidatos else None


def parse_layout_sas(caminho_txt: Path) -> pd.DataFrame:
    """Interpreta o layout de posição fixa em formato SAS usado pelo IBGE.

    Ex.: "@1  Ano  4."  ->  (nome=Ano, inicio=1, largura=4, texto=False)
    """
    padrao = re.compile(r"@(\d+)\s+(\S+)\s+(\$)?(\d+)\.?")
    registros = []
    with open(caminho_txt, "r", encoding="latin-1") as f:
        for linha in f:
            m = padrao.search(linha)
            if not m:
                continue
            inicio, nome, eh_texto, largura = (
                int(m.group(1)), m.group(2), m.group(3) == "$", int(m.group(4))
            )
            registros.append((nome, inicio, largura, eh_texto))

    layout = pd.DataFrame(registros, columns=["nome", "inicio", "largura", "texto"])
    layout = layout.drop_duplicates(subset="nome").reset_index(drop=True)
    layout["fim"] = layout["inicio"] + layout["largura"] - 1
    return layout


def obter_layout() -> tuple[pd.DataFrame, Path]:
    """Baixa e interpreta o dicionário/input (layout de largura fixa) do trimestre mais recente."""
    arquivos = listar_diretorio(DOC_URL)
    candidatos = sorted(a for a in arquivos if re.match(r"^Dicionario_e_input.*\.zip$", a, re.IGNORECASE))
    if not candidatos:
        raise RuntimeError("Não encontrei o arquivo Dicionario_e_input*.zip na pasta Documentacao.")
    nome_zip = candidatos[-1]
    destino_zip = RAW_TMP_DIR / nome_zip
    baixar_arquivo(DOC_URL + nome_zip, destino_zip)

    pasta_extraida = RAW_TMP_DIR / "dicionario"
    pasta_extraida.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino_zip) as z:
        z.extractall(pasta_extraida)

    input_txt = next(
        (p for p in pasta_extraida.rglob("*.txt")
         if p.name.lower().startswith("input_pnadc_trimestral")),
        None,
    )
    if input_txt is None:
        raise RuntimeError("Não encontrei input_PNADC_trimestral.txt dentro do zip do dicionário.")

    return parse_layout_sas(input_txt), pasta_extraida


def montar_colspecs(layout: pd.DataFrame, variaveis_desejadas: list[str] | None):
    """Monta colspecs/nomes/dtypes para pandas.read_fwf a partir do layout e da seleção de variáveis."""
    if variaveis_desejadas is not None:
        faltando = [v for v in variaveis_desejadas if v not in set(layout["nome"])]
        if faltando:
            print("Aviso: variáveis não encontradas no layout:", faltando)
        layout_sel = layout[layout["nome"].isin(variaveis_desejadas)].copy()
    else:
        layout_sel = layout.copy()

    layout_sel = layout_sel.sort_values("inicio")
    colspecs = [(int(r.inicio) - 1, int(r.fim)) for r in layout_sel.itertuples()]
    nomes = list(layout_sel["nome"])
    dtypes = {n: (str if t else "float64") for n, t in zip(layout_sel["nome"], layout_sel["texto"])}
    return colspecs, nomes, dtypes


def processar_trimestre(ano: int, trimestre: int, colspecs, nomes_colunas, dtypes) -> str:
    """Baixa e converte um trimestre para Parquet particionado. Idempotente via marcador _SUCCESS."""
    particao_dir = OUTPUT_DIR / f"ano={ano}" / f"trimestre={trimestre}"
    marcador = particao_dir / "_SUCCESS"
    if marcador.exists():
        return "já processado"

    url_zip = encontrar_zip_trimestre(ano, trimestre)
    if url_zip is None:
        return "indisponível no servidor"

    nome_zip = url_zip.split("/")[-1]
    destino_zip = RAW_TMP_DIR / nome_zip
    baixar_arquivo(url_zip, destino_zip)

    pasta_extraida = RAW_TMP_DIR / f"extraido_{ano}_{trimestre}"
    pasta_extraida.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino_zip) as z:
        z.extractall(pasta_extraida)

    txt_candidatos = list(pasta_extraida.glob("*.txt"))
    if not txt_candidatos:
        return "arquivo .txt de dados não encontrado no zip"
    caminho_txt = txt_candidatos[0]

    particao_dir.mkdir(parents=True, exist_ok=True)
    leitor = pd.read_fwf(
        caminho_txt,
        colspecs=colspecs,
        names=nomes_colunas,
        dtype=dtypes,
        chunksize=CHUNKSIZE,
        encoding="latin-1",
    )

    total_linhas = 0
    for i, bloco in enumerate(leitor):
        for col, tipo in dtypes.items():
            if tipo == "float64":
                bloco[col] = pd.to_numeric(bloco[col], errors="coerce")
        tabela = pa.Table.from_pandas(bloco, preserve_index=False)
        pq.write_table(
            tabela,
            particao_dir / f"parte_{i:04d}.parquet",
            compression="snappy",
        )
        total_linhas += len(bloco)

    marcador.write_text(str(total_linhas))

    # limpeza dos arquivos brutos do trimestre para economizar espaço em disco
    destino_zip.unlink()
    for f in pasta_extraida.iterdir():
        f.unlink()
    pasta_extraida.rmdir()

    return f"ok ({total_linhas:,} linhas)".replace(",", ".")


def main(ano_inicial: int, ano_final: int) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_TMP_DIR.mkdir(parents=True, exist_ok=True)

    print("Baixando e interpretando o dicionário de variáveis (input SAS)...")
    layout, _ = obter_layout()
    print(f"Layout carregado: {len(layout)} variáveis identificadas.")
    colspecs, nomes_colunas, dtypes = montar_colspecs(layout, VARIAVEIS_DESEJADAS)
    print(f"{len(nomes_colunas)} colunas serão extraídas de cada registro.")

    combinacoes = [(a, t) for a in range(ano_inicial, ano_final + 1) for t in (1, 2, 3, 4)]
    resultados = []
    for ano, trimestre in tqdm(combinacoes, desc="Trimestres PNAD Contínua"):
        try:
            status = processar_trimestre(ano, trimestre, colspecs, nomes_colunas, dtypes)
        except Exception as e:
            status = f"ERRO: {e}"
        resultados.append({"ano": ano, "trimestre": trimestre, "status": status})
        print(f"{ano} T{trimestre}: {status}")

    resumo_novo = pd.DataFrame(resultados)
    resumo_path = OUTPUT_DIR / "_resumo_extracao.csv"
    if resumo_path.exists():
        # Mescla com o resumo existente: mantém trimestres fora do intervalo desta
        # execução e substitui só os que acabaram de ser (re)processados.
        resumo_anterior = pd.read_csv(resumo_path)
        chaves_novas = set(zip(resumo_novo["ano"], resumo_novo["trimestre"]))
        resumo_anterior = resumo_anterior[
            ~resumo_anterior.apply(lambda r: (r["ano"], r["trimestre"]) in chaves_novas, axis=1)
        ]
        resumo = pd.concat([resumo_anterior, resumo_novo], ignore_index=True)
        resumo = resumo.sort_values(["ano", "trimestre"]).reset_index(drop=True)
    else:
        resumo = resumo_novo
    resumo.to_csv(resumo_path, index=False)
    print(resumo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ano-inicial", type=int, default=2012)
    parser.add_argument("--ano-final", type=int, default=2026)
    args = parser.parse_args()
    main(args.ano_inicial, args.ano_final)
