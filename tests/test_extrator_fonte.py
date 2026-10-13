"""Registro da publicação extraída (nome do zip e Last-Modified; R15 da auditoria Rodada 2).
Sem rede: o HEAD é simulado."""
from src.ingestion import extrator_pnadc as ex


class _Resposta:
    headers = {"Last-Modified": "Fri, 15 Aug 2025 12:00:00 GMT", "Content-Length": "123456"}

    def raise_for_status(self):
        pass


def test_info_remota_e_ida_e_volta(monkeypatch, tmp_path):
    monkeypatch.setattr(ex.requests, "head", lambda *a, **k: _Resposta())
    info = ex.info_remota("https://ftp.ibge.gov.br/x/2026/PNADC_022026_20260815.zip")
    assert info["arquivo_zip"] == "PNADC_022026_20260815.zip"
    assert info["last_modified_servidor"] == "Fri, 15 Aug 2025 12:00:00 GMT"
    assert info["tamanho_bytes"] == 123456
    ex.gravar_fonte(tmp_path, info)
    assert ex.ler_fonte(tmp_path) == {c: info[c] for c in ex.COLUNAS_FONTE}


def test_head_falho_nao_interrompe(monkeypatch):
    def falha(*a, **k):
        raise ConnectionError("sem rede")
    monkeypatch.setattr(ex.requests, "head", falha)
    info = ex.info_remota("https://ftp.ibge.gov.br/x/PNADC_012012.zip")
    assert info["arquivo_zip"] == "PNADC_012012.zip" and info["last_modified_servidor"] is None


def test_particao_antiga_sem_fonte(tmp_path):
    assert ex.ler_fonte(tmp_path) == {c: None for c in ex.COLUNAS_FONTE}
