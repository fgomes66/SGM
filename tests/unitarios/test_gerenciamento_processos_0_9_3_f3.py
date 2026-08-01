import inspect
from unittest.mock import Mock

import pytest

from sgm.desktop.apresentacao import janela_principal as modulo
from sgm.desktop.apresentacao.janela_principal import JanelaPrincipal


class MenuFalso:
    criados = []

    def __init__(self, mestre=None, tearoff=None):
        self.mestre = mestre
        self.tearoff = tearoff
        self.comandos = []
        self.cascatas = []
        MenuFalso.criados.append(self)

    def add_command(self, **kwargs):
        self.comandos.append(kwargs)

    def add_separator(self):
        self.comandos.append({"separator": True})

    def add_cascade(self, **kwargs):
        self.cascatas.append(kwargs)


class JanelaFalsa:
    def __init__(self):
        self.configuracoes = {}
        self.vinculos = []
        self.atualizada = False
        self._novo_processo = Mock()
        self._abrir_processo = Mock()
        self._salvar = Mock()
        self._salvar_como = Mock()
        self._fechar_processo = Mock()
        self._solicitar_saida = Mock()
        self._sobre = Mock()
        self._atalho_novo = Mock()
        self._atalho_abrir = Mock()
        self._atalho_salvar = Mock()
        self._atalho_salvar_como = Mock()
        self._atalho_fechar = Mock()

    def configure(self, **kwargs):
        self.configuracoes.update(kwargs)

    def update_idletasks(self):
        self.atualizada = True

    def bind_all(self, sequencia, callback):
        self.vinculos.append((sequencia, callback))


def executar_menu(monkeypatch):
    MenuFalso.criados.clear()
    monkeypatch.setattr(modulo.tk, "Menu", MenuFalso)
    janela = JanelaFalsa()
    JanelaPrincipal._criar_menu(janela)
    return janela


def test_01_metodo_menu_executa_sem_attribute_error(monkeypatch):
    executar_menu(monkeypatch)


def test_02_nao_existe_referencia_menu_self():
    fonte = inspect.getsource(JanelaPrincipal._criar_menu)
    assert "_menu_self" not in fonte


def test_03_barra_menu_criada(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert isinstance(janela._barra_menu, MenuFalso)


def test_04_menu_arquivo_criado(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert isinstance(janela._menu_arquivo, MenuFalso)


def test_05_menu_ajuda_criado(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert isinstance(janela._menu_ajuda, MenuFalso)


def test_06_menu_associado_a_janela(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert janela.configuracoes["menu"] is janela._barra_menu


def test_07_tcl_atualizado(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert janela.atualizada


def rotulos(menu):
    return [item.get("label") for item in menu.comandos if "label" in item]


def test_08_tem_novo_processo(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert "Novo processo..." in rotulos(janela._menu_arquivo)


def test_09_tem_abrir_processo(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert "Abrir processo..." in rotulos(janela._menu_arquivo)


def test_10_tem_salvar(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert "Salvar" in rotulos(janela._menu_arquivo)


def test_11_tem_salvar_como(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert "Salvar como..." in rotulos(janela._menu_arquivo)


def test_12_tem_fechar_processo(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert "Fechar processo" in rotulos(janela._menu_arquivo)


def test_13_tem_sair(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert "Sair" in rotulos(janela._menu_arquivo)


def test_14_barra_tem_cascata_arquivo(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert any(x.get("label") == "Arquivo" for x in janela._barra_menu.cascatas)


def test_15_barra_tem_cascata_ajuda(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert any(x.get("label") == "Ajuda" for x in janela._barra_menu.cascatas)


def test_16_atalho_ctrl_n(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert any(x[0] == "<Control-n>" for x in janela.vinculos)


def test_17_atalho_ctrl_o(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert any(x[0] == "<Control-o>" for x in janela.vinculos)


def test_18_atalho_ctrl_s(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert any(x[0] == "<Control-s>" for x in janela.vinculos)


def test_19_atalho_salvar_como(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert any(x[0] == "<Control-Shift-S>" for x in janela.vinculos)


def test_20_atalho_ctrl_w(monkeypatch):
    janela = executar_menu(monkeypatch)
    assert any(x[0] == "<Control-w>" for x in janela.vinculos)


def test_21_versao_f3():
    assert JanelaPrincipal.VERSAO == "0.9.3-F3"


def test_22_sobre_identifica_f3():
    fonte = inspect.getsource(JanelaPrincipal._sobre)
    assert "0.9.3-F3" in fonte
