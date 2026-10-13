"""Extrai a série anual da PNAD Contínua - Visita 1 (IBGE) direto do FTP público.

Ao contrário da Trimestral (mesmo layout reaproveitado para toda a série), cada ano da
Visita 1 tem seu PRÓPRIO dicionário/input SAS — o conjunto de temas suplementares varia
ano a ano (ver `docs/PLANO.md`, quadro oficial "PNAD Contínua – Pesquisas Suplementares
Anuais"). Por isso o layout é baixado e reinterpretado ano a ano, não uma vez só.

Recorte atual: tema Habitação (variáveis S01xxx), disponível nos anos 2016-2019 e
2022-2025 (2020/2021 não têm Visita 1 publicada; tema não pesquisado antes de 2016).

Uso:
    python -m src.ingestion.extrator_pnadc_visita_anual                 # todos os anos com Habitação
    python -m src.ingestion.extrator_pnadc_visita_anual --anos 2025
"""
import argparse
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
    "Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Visita/Visita_1"
)
DADOS_URL = f"{BASE_URL}/Dados/"
DOC_URL = f"{BASE_URL}/Documentacao/"

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "data" / "raw" / "pnadc_anual_visita1" / "parquet"
RAW_TMP_DIR = REPO_ROOT / "data" / "raw" / "pnadc_anual_visita1" / "_tmp"

CHUNKSIZE = 200_000
HEADERS = {"User-Agent": "Mozilla/5.0 (datahub-racial-brasil)"}

# Anos em que o tema Habitação foi investigado na Visita 1 (quadro oficial do IBGE:
# PNAD Contínua – Pesquisas Suplementares Anuais 2012-2025). 2020/2021 não têm
# microdados de Visita 1 publicados; 2026 ainda não saiu.
ANOS_HABITACAO = [2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025]

# Núcleo (identificação/desenho amostral + raça/sexo/idade, presentes em toda Visita 1)
# + bloco Habitação (S01xxx). V1016 não existe na Visita 1 (é específico do painel
# trimestral). Peso: V1032 é o peso calibrado da divulgação anual (distinto do V1028
# trimestral) — confirmado no layout 2025; se não existir num ano específico, o aviso
# de "variáveis não encontradas" do parser avisa, não quebra a extração.
VARIAVEIS_DESEJADAS = [
    # identificação / desenho amostral
    "UF", "Capital", "RM_RIDE", "UPA", "Estrato",
    "V1008", "V1014", "V1022", "V1023", "V1032",
    # domicílio / pessoa
    "V2001", "V2003", "V2005", "V2007", "V2009", "V2010",
    # Habitação (tema suplementar da Visita 1). S01011/S01012 (nomes usados em
    # 2016-2019, antes do desmembramento em S01011A/B/C e S01012A a partir de 2022)
    # E as variantes novas ficam AMBAS na lista — cada ano só tem uma das duas, a
    # outra é ignorada silenciosamente pelo `montar_colspecs` (esperado).
    "S01001", "S01002", "S01003", "S01004", "S01005", "S01006",
    "S01007", "S01007A", "S01008", "S01009", "S01010",
    "S01011", "S01011A", "S01011B", "S01011C", "S01012", "S01012A", "S01013",
    "S01014", "S010141", "S010142", "S01015",
    "S01016", "S01016A", "S01016A1", "S01016A2", "S01016A3", "S01016A4", "S01016A5", "S01016B",
    "S01017", "S01018", "S01019", "S01020", "S01020A", "S01021",
    "S01022", "S01023", "S01024", "S01025", "S01026", "S01028", "S01029",
    "S01031", "S010311", "S010312",
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


def encontrar_arquivo_ano(pasta_url: str, arquivos: list[str], prefixo: str, ano: int, sufixo: str) -> str | None:
    """Encontra, numa listagem de diretório já obtida, o arquivo do ano pedido."""
    padrao = re.compile(rf"^{prefixo}{ano}_visita1_\d+\.{sufixo}$", re.IGNORECASE)
    candidatos = sorted(a for a in arquivos if padrao.match(a))
    return pasta_url + candidatos[-1] if candidatos else None


def obter_layout_ano(ano: int) -> pd.DataFrame:
    """Baixa e interpreta o dicionário/input (layout de largura fixa) específico do ano."""
    arquivos_doc = listar_diretorio(DOC_URL)
    url_input = encontrar_arquivo_ano(DOC_URL, arquivos_doc, "input_PNADC_", ano, "txt")
    if url_input is None:
        raise RuntimeError(f"Não encontrei o input_PNADC_{ano}_visita1_*.txt em {DOC_URL}")

    nome_input = url_input.split("/")[-1]
    destino_input = RAW_TMP_DIR / nome_input
    baixar_arquivo(url_input, destino_input)
    return parse_layout_sas(destino_input)


def montar_colspecs(layout: pd.DataFrame, variaveis_desejadas: list[str], ano: int):
    """Monta colspecs/nomes/dtypes a partir do layout do ano e da seleção de variáveis.

    Variáveis pedidas que não existem no layout daquele ano específico são avisadas e
    ignoradas (esperado: temas/campos entram e saem de um ano para outro).
    """
    faltando = [v for v in variaveis_desejadas if v not in set(layout["nome"])]
    if faltando:
        print(f"  {ano}: variáveis não encontradas no layout deste ano: {faltando}")
    layout_sel = layout[layout["nome"].isin(variaveis_desejadas)].copy()
    layout_sel = layout_sel.sort_values("inicio")
    colspecs = [(int(r.inicio) - 1, int(r.fim)) for r in layout_sel.itertuples()]
    nomes = list(layout_sel["nome"])
    dtypes = {n: (str if t else "float64") for n, t in zip(layout_sel["nome"], layout_sel["texto"])}
    return colspecs, nomes, dtypes


def processar_ano(ano: int, variaveis_desejadas: list[str]) -> str:
    """Baixa e converte um ano (Visita 1) para Parquet. Idempotente via marcador _SUCCESS."""
    particao_dir = OUTPUT_DIR / f"ano={ano}"
    marcador = particao_dir / "_SUCCESS"
    if marcador.exists():
        return "já processado"

    layout = obter_layout_ano(ano)
    colspecs, nomes_colunas, dtypes = montar_colspecs(layout, variaveis_desejadas, ano)

    arquivos_dados = listar_diretorio(DADOS_URL)
    url_zip = encontrar_arquivo_ano(DADOS_URL, arquivos_dados, "PNADC_", ano, "zip")
    if url_zip is None:
        return "indisponível no servidor"

    nome_zip = url_zip.split("/")[-1]
    destino_zip = RAW_TMP_DIR / nome_zip
    baixar_arquivo(url_zip, destino_zip)

    pasta_extraida = RAW_TMP_DIR / f"extraido_{ano}"
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

    # limpeza dos arquivos brutos do ano para economizar espaço em disco
    destino_zip.unlink()
    for f in pasta_extraida.iterdir():
        f.unlink()
    pasta_extraida.rmdir()

    return f"ok ({total_linhas:,} linhas)".replace(",", ".")


def main(anos: list[int]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_TMP_DIR.mkdir(parents=True, exist_ok=True)

    resultados = []
    for ano in tqdm(anos, desc="PNAD Contínua Anual - Visita 1 (Habitação)"):
        try:
            status = processar_ano(ano, VARIAVEIS_DESEJADAS)
        except Exception as e:
            status = f"ERRO: {e}"
        resultados.append({"ano": ano, "status": status})
        print(f"{ano}: {status}")

    resumo_novo = pd.DataFrame(resultados)
    resumo_path = OUTPUT_DIR / "_resumo_extracao.csv"
    if resumo_path.exists():
        resumo_anterior = pd.read_csv(resumo_path)
        anos_novos = set(resumo_novo["ano"])
        resumo_anterior = resumo_anterior[~resumo_anterior["ano"].isin(anos_novos)]
        resumo = pd.concat([resumo_anterior, resumo_novo], ignore_index=True)
        resumo = resumo.sort_values("ano").reset_index(drop=True)
    else:
        resumo = resumo_novo
    resumo.to_csv(resumo_path, index=False)
    print(resumo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anos", type=int, nargs="+", default=ANOS_HABITACAO)
    args = parser.parse_args()
    main(args.anos)
