import inspect

from sgm.desktop.apresentacao.janela_principal import JanelaPrincipal


def test_01_menu_guarda_barra_como_atributo():
    fonte = inspect.getsource(JanelaPrincipal._criar_menu)
    assert "self._barra_menu" in fonte


def test_02_menu_guarda_arquivo_como_atributo():
    fonte = inspect.getsource(JanelaPrincipal._criar_menu)
    assert "self._menu_arquivo" in fonte


def test_03_menu_guarda_ajuda_como_atributo():
    fonte = inspect.getsource(JanelaPrincipal._criar_menu)
    assert "self._menu_ajuda" in fonte


def test_04_menu_e_associado_a_janela():
    fonte = inspect.getsource(JanelaPrincipal._criar_menu)
    assert "self.configure(menu=self._barra_menu)" in fonte


def test_05_menu_forca_atualizacao_tcl():
    fonte = inspect.getsource(JanelaPrincipal._criar_menu)
    assert "self.update_idletasks()" in fonte


def test_06_barra_acoes_existe():
    fonte = inspect.getsource(JanelaPrincipal._criar_layout)
    assert "self._barra_acoes" in fonte


def test_07_barra_tem_novo_processo():
    fonte = inspect.getsource(JanelaPrincipal._criar_layout)
    assert 'text="Novo processo..."' in fonte


def test_08_barra_tem_abrir_processo():
    fonte = inspect.getsource(JanelaPrincipal._criar_layout)
    assert 'text="Abrir processo..."' in fonte


def test_09_barra_tem_salvar():
    fonte = inspect.getsource(JanelaPrincipal._criar_layout)
    assert 'text="Salvar"' in fonte


def test_10_barra_tem_fechar():
    fonte = inspect.getsource(JanelaPrincipal._criar_layout)
    assert 'text="Fechar processo"' in fonte


def test_11_atalho_novo_permanece():
    assert callable(getattr(JanelaPrincipal, "_atalho_novo", None))


def test_12_atalho_abrir_permanece():
    assert callable(getattr(JanelaPrincipal, "_atalho_abrir", None))


def test_13_atalho_salvar_permanece():
    assert callable(getattr(JanelaPrincipal, "_atalho_salvar", None))


def test_14_acao_novo_ligada_ao_metodo():
    fonte = inspect.getsource(JanelaPrincipal._criar_layout)
    assert "command=self._novo_processo" in fonte


def test_15_acao_abrir_ligada_ao_metodo():
    fonte = inspect.getsource(JanelaPrincipal._criar_layout)
    assert "command=self._abrir_processo" in fonte
