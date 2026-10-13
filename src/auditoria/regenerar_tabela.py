"""Regenera tabelas avulsas de `agregacoes_pnadc` sem rodar o pipeline inteiro.

Materializa a `CRIAR_BASE` uma vez e chama só os geradores pedidos. Serve para correções
pontuais entre regenerações completas (ex.: E6, 13/10/2026), quando rodar `main()` trocaria
a população de tabelas que ainda não devem mudar. Antes de usar, copie as tabelas atuais
para `data/processed/_legado/<rotulo>/` e depois rode `src.auditoria.antes_depois`.

Uso:
    python -m src.auditoria.regenerar_tabela gerar_decomposicao_raca_genero
"""
import argparse
import time

import duckdb

from src.processing import agregacoes_pnadc as ag


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("geradores", nargs="+", help="nomes de funções gerar_* de agregacoes_pnadc")
    args = parser.parse_args()
    funcoes = []
    for nome in args.geradores:
        f = getattr(ag, nome, None)
        if not (callable(f) and nome.startswith("gerar_")):
            raise SystemExit(f"gerador desconhecido: {nome}")
        funcoes.append(f)
    con = duckdb.connect()
    con.execute("PRAGMA disable_progress_bar")
    t0 = time.time()
    con.execute(ag.CRIAR_BASE)
    print(f"base materializada em {time.time() - t0:.0f}s", flush=True)
    for f in funcoes:
        f(con)


if __name__ == "__main__":
    main()
