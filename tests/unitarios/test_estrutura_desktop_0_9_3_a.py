from dataclasses import FrozenInstanceError

import pytest

from sgm.desktop import (
    ControladorDesktop,
    EstadoDesktop,
    ItemNavegacao,
    SecaoDesktop,
    criar_catalogo_navegacao,
)


def test_01_secoes_estaveis():
    assert SecaoDesktop.INICIO.value == "INICIO"
    assert SecaoDesktop.EXPORTACAO.value == "EXPORTACAO"


def test_02_titulos_das_secoes():
    assert SecaoDesktop.PROCESSO.titulo == "Processo"
    assert (
        SecaoDesktop.CONTRATO.titulo
        == "Contrato de Trabalho"
    )


def test_03_estado_inicial():
    estado = EstadoDesktop()
    assert estado.secao_atual == SecaoDesktop.INICIO
    assert estado.total_testes_backend == 725


def test_04_estado_navega():
    estado = EstadoDesktop().navegar(
        SecaoDesktop.PROCESSO
    )
    assert estado.secao_atual == SecaoDesktop.PROCESSO


def test_05_estado_rejeita_secao_invalida():
    with pytest.raises(TypeError):
        EstadoDesktop().navegar("PROCESSO")


def test_06_estado_define_processo():
    estado = EstadoDesktop().definir_processo(" CASO-100 ")
    assert estado.referencia_processo == "CASO-100"
    assert estado.alteracoes_pendentes


def test_07_estado_remove_processo_vazio():
    estado = EstadoDesktop().definir_processo(" ")
    assert estado.referencia_processo is None


def test_08_estado_marca_salvo():
    estado = (
        EstadoDesktop()
        .definir_processo("CASO")
        .marcar_salvo()
    )
    assert not estado.alteracoes_pendentes


def test_09_estado_e_imutavel():
    estado = EstadoDesktop()
    with pytest.raises(FrozenInstanceError):
        estado.mensagem_status = "Outro"


def test_10_item_navegacao_valido():
    item = ItemNavegacao(
        SecaoDesktop.INICIO,
        "Início",
        "Visão geral.",
    )
    assert item.habilitado


def test_11_item_rejeita_rotulo_vazio():
    with pytest.raises(ValueError):
        ItemNavegacao(
            SecaoDesktop.INICIO,
            " ",
            "Descrição",
        )


def test_12_catalogo_possui_oito_itens():
    assert len(criar_catalogo_navegacao()) == 8


def test_13_catalogo_preserva_ordem():
    catalogo = criar_catalogo_navegacao()
    assert catalogo[0].secao == SecaoDesktop.INICIO
    assert catalogo[-1].secao == SecaoDesktop.EXPORTACAO


def test_14_catalogo_nao_repete_secoes():
    secoes = tuple(
        item.secao for item in criar_catalogo_navegacao()
    )
    assert len(secoes) == len(set(secoes))


def test_15_controlador_inicia_com_estado():
    controlador = ControladorDesktop()
    assert controlador.estado.secao_atual == SecaoDesktop.INICIO


def test_16_controlador_navega():
    controlador = ControladorDesktop()
    controlador.navegar(SecaoDesktop.RELATORIO)
    assert controlador.estado.secao_atual == (
        SecaoDesktop.RELATORIO
    )


def test_17_controlador_cria_processo():
    controlador = ControladorDesktop()
    controlador.novo_processo("CASO-200")
    assert controlador.estado.referencia_processo == "CASO-200"


def test_18_controlador_salva():
    controlador = ControladorDesktop()
    controlador.novo_processo("CASO-200")
    controlador.salvar()
    assert not controlador.estado.alteracoes_pendentes


def test_19_controlador_publica_estado():
    controlador = ControladorDesktop()
    recebidos = []
    controlador.observar(recebidos.append)
    controlador.navegar(SecaoDesktop.CALCULO)
    assert recebidos[-1].secao_atual == SecaoDesktop.CALCULO


def test_20_controlador_nao_duplica_observador():
    controlador = ControladorDesktop()
    recebidos = []
    controlador.observar(recebidos.append)
    controlador.observar(recebidos.append)
    controlador.salvar()
    assert len(recebidos) == 1


def test_21_controlador_remove_observador():
    controlador = ControladorDesktop()
    recebidos = []
    controlador.observar(recebidos.append)
    controlador.remover_observador(recebidos.append)
    controlador.salvar()
    assert recebidos == []


def test_22_navegacao_nao_muda_referencia():
    controlador = ControladorDesktop()
    controlador.novo_processo("CASO-300")
    controlador.navegar(SecaoDesktop.EVENTOS)
    assert controlador.estado.referencia_processo == "CASO-300"


def test_23_salvar_nao_muda_secao():
    controlador = ControladorDesktop()
    controlador.navegar(SecaoDesktop.MEMORIA)
    controlador.salvar()
    assert controlador.estado.secao_atual == SecaoDesktop.MEMORIA


def test_24_backend_homologado_e_exposto():
    estado = EstadoDesktop()
    assert estado.backend_homologado == "0.9.2-E5"


def test_25_catalogo_tem_descricoes():
    assert all(
        item.descricao
        for item in criar_catalogo_navegacao()
    )
