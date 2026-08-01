import inspect
from dataclasses import replace

import pytest

from sgm.desktop import ControladorDesktop, EstadoDesktop, RepositorioProcessosJSON
from sgm.desktop.apresentacao.janela_principal import JanelaPrincipal
from tests.unitarios.test_cadastro_processo_desktop_0_9_3_b import formulario_valido


def ctrl(tmp_path):
    return ControladorDesktop(
        repositorio=RepositorioProcessosJSON(tmp_path),
        exigir_fluxo=True,
    )


def preparar(c, referencia="CASO-F2"):
    c.novo_processo(referencia)
    assert c.registrar_identificacao(formulario_valido()) == ()


def test_01_estado_fecha_processo():
    estado = EstadoDesktop().iniciar_novo("CASO")
    fechado = estado.fechar_processo()
    assert fechado.referencia_processo is None


def test_02_fechar_limpa_identificacao():
    estado = EstadoDesktop().iniciar_novo("CASO")
    fechado = estado.fechar_processo()
    assert fechado.identificacao_processo is None


def test_03_fechar_limpa_contrato():
    fechado = EstadoDesktop().iniciar_novo("CASO").fechar_processo()
    assert fechado.contrato_trabalho is None


def test_04_fechar_limpa_eventos():
    fechado = EstadoDesktop().iniciar_novo("CASO").fechar_processo()
    assert fechado.eventos_contratuais == ()


def test_05_fechar_limpa_calculos():
    fechado = EstadoDesktop().iniciar_novo("CASO").fechar_processo()
    assert fechado.resultados_calculo == ()


def test_06_fechar_remove_pendencia():
    fechado = EstadoDesktop().iniciar_novo("CASO").fechar_processo()
    assert not fechado.alteracoes_pendentes


def test_07_repositorio_existe_falso(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    assert not repo.existe("CASO")


def test_08_repositorio_existe_verdadeiro(tmp_path):
    c = ctrl(tmp_path); preparar(c)
    assert c.repositorio.existe("CASO-F2")


def test_09_salvar_como_exige_identificacao(tmp_path):
    c = ctrl(tmp_path)
    with pytest.raises(ValueError): c.salvar_como("COPIA")


def test_10_salvar_como_exige_referencia(tmp_path):
    c = ctrl(tmp_path); preparar(c)
    with pytest.raises(ValueError): c.salvar_como(" ")


def test_11_salvar_como_cria_arquivo(tmp_path):
    c = ctrl(tmp_path); preparar(c)
    caminho = c.salvar_como("COPIA")
    assert caminho.exists()


def test_12_salvar_como_troca_referencia(tmp_path):
    c = ctrl(tmp_path); preparar(c)
    c.salvar_como("COPIA")
    assert c.estado.referencia_processo == "COPIA"


def test_13_salvar_como_preserva_original(tmp_path):
    c = ctrl(tmp_path); preparar(c)
    c.salvar_como("COPIA")
    assert c.repositorio.existe("CASO-F2")
    assert c.repositorio.existe("COPIA")


def test_14_salvar_como_rejeita_duplicado(tmp_path):
    c = ctrl(tmp_path); preparar(c)
    c.salvar_como("COPIA")
    c.abrir("CASO-F2")
    with pytest.raises(FileExistsError): c.salvar_como("COPIA")


def test_15_salvar_como_sobrescreve(tmp_path):
    c = ctrl(tmp_path); preparar(c)
    c.salvar_como("COPIA")
    c.abrir("CASO-F2")
    assert c.salvar_como("COPIA", sobrescrever=True).exists()


def test_16_salvar_como_publica(tmp_path):
    c = ctrl(tmp_path); preparar(c)
    recebidos=[]; c.observar(recebidos.append)
    c.salvar_como("COPIA")
    assert recebidos[-1].referencia_processo == "COPIA"


def test_17_controlador_fecha(tmp_path):
    c = ctrl(tmp_path); preparar(c); c.fechar_processo()
    assert c.estado.referencia_processo is None


def test_18_controlador_fecha_publica(tmp_path):
    c = ctrl(tmp_path); preparar(c)
    recebidos=[]; c.observar(recebidos.append); c.fechar_processo()
    assert recebidos[-1].mensagem_status == "Processo fechado."


def test_19_titulo_sem_processo():
    assert JanelaPrincipal._titulo_para(EstadoDesktop()) == JanelaPrincipal.TITULO_BASE


def test_20_titulo_com_processo():
    estado = replace(EstadoDesktop(), referencia_processo="CASO")
    assert "CASO" in JanelaPrincipal._titulo_para(estado)


def test_21_titulo_com_pendencia():
    estado = replace(EstadoDesktop(), referencia_processo="CASO", alteracoes_pendentes=True)
    assert JanelaPrincipal._titulo_para(estado).endswith("*")


def test_22_status_sem_processo():
    assert "nenhum" in JanelaPrincipal._status_para(EstadoDesktop())


def test_23_status_com_processo():
    estado = replace(EstadoDesktop(), referencia_processo="CASO")
    assert "Processo ativo: CASO" in JanelaPrincipal._status_para(estado)


def test_24_status_pendencia():
    estado = replace(EstadoDesktop(), alteracoes_pendentes=True)
    assert "alterações pendentes" in JanelaPrincipal._status_para(estado)


def test_25_menu_tem_salvar_como():
    assert callable(getattr(JanelaPrincipal, "_salvar_como", None))


def test_26_menu_tem_fechar():
    assert callable(getattr(JanelaPrincipal, "_fechar_processo", None))


def test_27_atalho_novo():
    assert callable(getattr(JanelaPrincipal, "_atalho_novo", None))


def test_28_atalho_abrir():
    assert callable(getattr(JanelaPrincipal, "_atalho_abrir", None))


def test_29_atalho_salvar():
    assert callable(getattr(JanelaPrincipal, "_atalho_salvar", None))


def test_30_atalho_salvar_como():
    assert callable(getattr(JanelaPrincipal, "_atalho_salvar_como", None))


def test_31_atalho_fechar():
    assert callable(getattr(JanelaPrincipal, "_atalho_fechar", None))


def test_32_fonte_menu_novo():
    fonte = inspect.getsource(JanelaPrincipal._criar_menu)
    assert "Novo processo..." in fonte


def test_33_fonte_menu_abrir():
    fonte = inspect.getsource(JanelaPrincipal._criar_menu)
    assert "Abrir processo..." in fonte


def test_34_fonte_menu_salvar_como():
    fonte = inspect.getsource(JanelaPrincipal._criar_menu)
    assert "Salvar como..." in fonte


def test_35_fonte_menu_fechar():
    fonte = inspect.getsource(JanelaPrincipal._criar_menu)
    assert "Fechar processo" in fonte
