"""Extrai a série anual da PNAD Contínua - Visita 1 ou Visita 5 (IBGE) direto do FTP público.

Ao contrário da Trimestral (mesmo layout reaproveitado para toda a série), cada ano da
divulgação anual tem seu PRÓPRIO dicionário/input SAS — o conjunto de temas suplementares
varia ano a ano (ver `docs/PLANO.md`, quadro oficial "PNAD Contínua – Pesquisas
Suplementares Anuais"). Por isso o layout é baixado e reinterpretado ano a ano.

Recorte (extração v2, 12/10/2026): rendimento domiciliar e por fonte (VD5xxx, V500xA —
Blocos S/P5 e T do plano de análise), educação, trabalho e o tema Habitação (S01xxx,
2016-2019 e 2022-2025; H3.1). 2020/2021 não têm Visita 1 publicada: para esses anos usa-se
a Visita 5 (mesma estrutura de renda e peso V1032; confirmado no input de 2021). Variáveis
ausentes num ano são avisadas e ignoradas.

Saída: data/raw/pnadc_anual_v2/visita{N}/parquet/ano=AAAA/ (a extração v1 em
data/raw/pnadc_anual_visita1/, base de `agregacoes_habitacao.py`, é preservada).

Uso:
    python -m src.ingestion.extrator_pnadc_visita_anual                       # Visita 1, 2012-2019 e 2022-2025
    python -m src.ingestion.extrator_pnadc_visita_anual --visita 5 --anos 2020 2021
    python -m src.ingestion.extrator_pnadc_visita_anual --anos 2025 --pesos-replicados
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

from src.ingestion.extrator_pnadc import gravar_fonte, info_remota, ler_fonte

BASE_URL_VISITAS = (
    "https://ftp.ibge.gov.br/Trabalho_e_Rendimento/"
    "Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Anual/Microdados/Visita"
)

REPO_ROOT = Path(__file__).resolve().parents[2]
RAIZ_SAIDA = REPO_ROOT / "data" / "raw" / "pnadc_anual_v2"

CHUNKSIZE = 200_000
HEADERS = {"User-Agent": "Mozilla/5.0 (datahub-racial-brasil)"}

# Anos em que o tema Habitação foi investigado na Visita 1 (quadro oficial do IBGE:
# PNAD Contínua – Pesquisas Suplementares Anuais 2012-2025). 2020/2021 não têm
# microdados de Visita 1 publicados; 2026 ainda não saiu.
ANOS_HABITACAO = [2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025]
# Anos com microdados de Visita 1 no FTP (listagem conferida em 12/10/2026).
ANOS_VISITA1 = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025]

PESOS_REPLICADOS = [f"V1032{i:03d}" for i in range(1, 201)]
CHAVES_LIGACAO = ["UPA", "V1008", "V1014", "V2003"]


def urls_visita(visita: int) -> tuple[str, str]:
    base = f"{BASE_URL_VISITAS}/Visita_{visita}"
    return f"{base}/Dados/", f"{base}/Documentacao/"


def pastas_saida(visita: int) -> tuple[Path, Path, Path]:
    raiz = RAIZ_SAIDA / f"visita{visita}"
    return raiz / "parquet", raiz / "pesos_replicados", raiz / "_tmp"

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
    # --- acrescentadas na extração v2 (12/10/2026) ---
    "V1031", "V1030", "V1034", "posest", "posest_sxi",
    "V2008", "V20081", "V20082", "VD2002", "VD2003", "VD2004",
    # educação (Bloco E; a visita anual tem o mesmo bloco V3 do trimestral)
    "V3001", "V3002", "V3002A", "V3003", "V3003A", "V3006", "V3006A", "V3008", "V3009A",
    "V3013", "V3014", "VD3004", "VD3005", "VD3006",
    # trabalho e renda individual
    "VD4001", "VD4002", "VD4009", "VD4010", "VD4011", "VD4016", "VD4017", "VD4019",
    "VD4020", "VD4031", "V4039",
    # outras fontes (T3) e renda de todas as fontes
    "V5001A", "V5001A2", "V5002A", "V5002A2", "V5003A", "V5003A2", "V5004A", "V5004A2",
    "V5005A", "V5005A2", "V5006A", "V5006A2", "V5007A", "V5007A2", "V5008A", "V5008A2",
    "VD4046", "VD4047", "VD4048", "VD4052",
    # rendimento domiciliar e per capita (P5 / Bloco T): VD5007/VD5008 habitual de todos os
    # trabalhos + efetivo de outras fontes; VD5010/VD5011 idem, inclusive tíquete
    # transporte/alimentação; VD5001-VD5005 efetivos (ver dicionário do ano)
    "VD5001", "VD5002", "VD5003", "VD5004", "VD5005", "VD5006",
    "VD5007", "VD5008", "VD5009", "VD5010", "VD5011", "VD5012",
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


def encontrar_arquivo_ano(pasta_url: str, arquivos: list[str], prefixo: str, ano: int, sufixo: str,
                          visita: int = 1) -> str | None:
    """Encontra, numa listagem de diretório já obtida, o arquivo do ano pedido.

    Aceita os formatos vistos no FTP: `PNADC_2024_visita5.zip` (sem data),
    `PNADC_2025_visita1_20260923.zip` e o input combinado `input_PNADC_2012_a_2014_visita1_*.txt`.
    """
    padrao = re.compile(rf"^{prefixo}(\d{{4}})(?:_a_(\d{{4}}))?_visita{visita}(?:_\d+)?\.{sufixo}$", re.IGNORECASE)
    candidatos = []
    for a in arquivos:
        m = padrao.match(a)
        if m and int(m.group(1)) <= ano <= int(m.group(2) or m.group(1)):
            candidatos.append(a)
    return pasta_url + sorted(candidatos)[-1] if candidatos else None


def obter_layout_ano(ano: int, visita: int, doc_url: str, tmp_dir: Path) -> pd.DataFrame:
    """Baixa e interpreta o dicionário/input (layout de largura fixa) específico do ano."""
    arquivos_doc = listar_diretorio(doc_url)
    url_input = encontrar_arquivo_ano(doc_url, arquivos_doc, "input_PNADC_", ano, "txt", visita)
    if url_input is None:
        raise RuntimeError(f"Não encontrei o input_PNADC_{ano}_visita{visita}*.txt em {doc_url}")

    nome_input = url_input.split("/")[-1]
    destino_input = tmp_dir / nome_input
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


def processar_ano(ano: int, variaveis_desejadas: list[str], visita: int = 1) -> str:
    """Baixa e converte um ano (Visita 1 ou 5) para Parquet. Idempotente via marcador _SUCCESS."""
    dados_url, doc_url = urls_visita(visita)
    output_dir, output_rep, tmp_dir = pastas_saida(visita)
    particao_dir = output_dir / f"ano={ano}"
    marcador = particao_dir / "_SUCCESS"
    if marcador.exists():
        return "já processado"

    layout = obter_layout_ano(ano, visita, doc_url, tmp_dir)
    colspecs, nomes_colunas, dtypes = montar_colspecs(layout, variaveis_desejadas, ano)
    replicados = [c for c in nomes_colunas if c in PESOS_REPLICADOS]

    arquivos_dados = listar_diretorio(dados_url)
    url_zip = encontrar_arquivo_ano(dados_url, arquivos_dados, "PNADC_", ano, "zip", visita)
    if url_zip is None:
        return "indisponível no servidor"

    nome_zip = url_zip.split("/")[-1]
    destino_zip = tmp_dir / nome_zip
    fonte = info_remota(url_zip)
    baixar_arquivo(url_zip, destino_zip)

    pasta_extraida = tmp_dir / f"extraido_{ano}"
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

    if replicados:
        particao_rep = output_rep / f"ano={ano}"
        particao_rep.mkdir(parents=True, exist_ok=True)

    total_linhas = 0
    for i, bloco in enumerate(leitor):
        for col, tipo in dtypes.items():
            if tipo == "float64":
                bloco[col] = pd.to_numeric(bloco[col], errors="coerce")
        if replicados:
            pq.write_table(
                pa.Table.from_pandas(bloco[CHAVES_LIGACAO + replicados], preserve_index=False),
                particao_rep / f"parte_{i:04d}.parquet", compression="zstd",
            )
            bloco = bloco.drop(columns=replicados)
        tabela = pa.Table.from_pandas(bloco, preserve_index=False)
        pq.write_table(
            tabela,
            particao_dir / f"parte_{i:04d}.parquet",
            compression="snappy",
        )
        total_linhas += len(bloco)

    gravar_fonte(particao_dir, fonte)
    marcador.write_text(str(total_linhas))

    # limpeza dos arquivos brutos do ano para economizar espaço em disco
    destino_zip.unlink()
    for f in pasta_extraida.iterdir():
        f.unlink()
    pasta_extraida.rmdir()

    return f"ok ({total_linhas:,} linhas)".replace(",", ".")


def main(anos: list[int], visita: int = 1, pesos_replicados: bool = False) -> None:
    output_dir, _, tmp_dir = pastas_saida(visita)
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    variaveis = VARIAVEIS_DESEJADAS + (PESOS_REPLICADOS if pesos_replicados else [])

    resultados = []
    for ano in tqdm(anos, desc=f"PNAD Contínua Anual - Visita {visita}"):
        try:
            status = processar_ano(ano, variaveis, visita)
        except Exception as e:
            status = f"ERRO: {e}"
        resultados.append({"ano": ano, "status": status, **ler_fonte(output_dir / f"ano={ano}")})
        print(f"{ano}: {status}")

    resumo_novo = pd.DataFrame(resultados)
    resumo_path = output_dir / "_resumo_extracao.csv"
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
    parser.add_argument("--visita", type=int, choices=[1, 5], default=1)
    parser.add_argument("--anos", type=int, nargs="+", default=None,
                        help="padrão: todos os anos de Visita 1 (ou 2020-2021 com --visita 5)")
    parser.add_argument("--pesos-replicados", action="store_true",
                        help="também extrai V1032001..V1032200 (dataset separado)")
    args = parser.parse_args()
    anos = args.anos or (ANOS_VISITA1 if args.visita == 1 else [2020, 2021])
    main(anos, args.visita, args.pesos_replicados)
