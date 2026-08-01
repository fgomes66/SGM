from sgm.desktop import (
    ControladorDesktop,
    SecaoDesktop,
)
from tests.unitarios.test_cadastro_processo_desktop_0_9_3_b import (
    formulario_valido,
)


def test_01_navegacao_processo_publica_secao():
    controlador = ControladorDesktop()
    recebidos = []
    controlador.observar(recebidos.append)

    controlador.navegar(SecaoDesktop.PROCESSO)

    assert recebidos[-1].secao_atual == (
        SecaoDesktop.PROCESSO
    )


def test_02_registro_mantem_secao_processo():
    controlador = ControladorDesktop()
    controlador.navegar(SecaoDesktop.PROCESSO)

    erros = controlador.registrar_identificacao(
        formulario_valido()
    )

    assert erros == ()
    assert controlador.estado.secao_atual == (
        SecaoDesktop.PROCESSO
    )


def test_03_inicio_expoe_identificacao_registrada():
    controlador = ControladorDesktop()
    controlador.registrar_identificacao(
        formulario_valido()
    )
    controlador.navegar(SecaoDesktop.INICIO)

    estado = controlador.estado
    assert estado.identificacao_processo is not None
    assert (
        estado.identificacao_processo.numero_processo
        == "0001234-55.2024.5.01.0007"
    )


def test_04_novo_processo_preserva_navegacao_manual():
    controlador = ControladorDesktop()
    controlador.novo_processo("CASO-400")
    controlador.navegar(SecaoDesktop.PROCESSO)

    assert controlador.estado.referencia_processo == "CASO-400"
    assert controlador.estado.secao_atual == (
        SecaoDesktop.PROCESSO
    )


def test_05_salvar_preserva_dados_processuais():
    controlador = ControladorDesktop()
    controlador.registrar_identificacao(
        formulario_valido()
    )
    identificacao = controlador.estado.identificacao_processo

    controlador.salvar()

    assert controlador.estado.identificacao_processo == identificacao
    assert not controlador.estado.alteracoes_pendentes
