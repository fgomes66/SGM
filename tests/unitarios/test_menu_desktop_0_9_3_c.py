import inspect

from sgm.desktop.apresentacao.janela_principal import JanelaPrincipal


def test_01_janela_define_novo_processo():
    assert callable(getattr(JanelaPrincipal, "_novo_processo", None))


def test_02_janela_define_abrir_processo():
    assert callable(getattr(JanelaPrincipal, "_abrir_processo", None))


def test_03_comandos_usam_operacoes_corretas_do_controlador():
    fonte_novo = inspect.getsource(JanelaPrincipal._novo_processo)
    fonte_abrir = inspect.getsource(JanelaPrincipal._abrir_processo)
    assert "controlador.novo_processo" in fonte_novo
    assert "controlador.listar_processos" in fonte_abrir
    assert "controlador.abrir" in fonte_abrir
