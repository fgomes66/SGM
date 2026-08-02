from pathlib import Path

from sgm.desktop.apresentacao.telas.tela_ia import TelaIA


def test_01_tela_ia_expoe_identidade_visual():
    assert TelaIA.TITULO == "SGM AI"
    assert "Assistente inteligente" in TelaIA.SUBTITULO


def test_02_tela_ia_possui_status_inicial():
    assert TelaIA.STATUS_INICIAL == (
        "Nenhum processo analisado pela IA."
    )


def test_03_tela_conteudo_registra_secao_ia():
    caminho = Path(
        "src/sgm/desktop/apresentacao/telas/tela_conteudo.py"
    )
    codigo = caminho.read_text(encoding="utf-8")
    assert "self._ia = TelaIA(self)" in codigo
    assert "if secao == SecaoDesktop.IA:" in codigo
