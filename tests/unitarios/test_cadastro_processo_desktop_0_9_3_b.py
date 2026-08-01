from dataclasses import FrozenInstanceError, replace

import pytest

from sgm.desktop import (
    ControladorDesktop,
    DadosProcessoFormulario,
    EstadoDesktop,
    SecaoDesktop,
)
from sgm.relatorio import IdentificacaoProcesso


def formulario_valido():
    return DadosProcessoFormulario(
        tribunal="Tribunal Regional do Trabalho",
        regiao_trt="1",
        vara="7ª Vara do Trabalho do Rio de Janeiro",
        municipio="Rio de Janeiro",
        uf="rj",
        numero_processo="0001234-55.2024.5.01.0007",
        classe_processual="Reclamação Trabalhista",
        reclamante="Fulano de Tal",
        reclamada="Empresa XYZ Ltda.",
        magistrado="Dra. Maria da Silva",
        perito="João Perito",
    )


def test_01_formulario_padrao():
    item = DadosProcessoFormulario()
    assert item.regiao_trt == "1"
    assert item.classe_processual == "Reclamação Trabalhista"


def test_02_formulario_normaliza_campos():
    item = DadosProcessoFormulario(
        tribunal=" TRT ",
        regiao_trt=" 1 ",
    )
    assert item.tribunal == "TRT"
    assert item.regiao_trt == "1"


def test_03_formulario_valido_sem_erros():
    assert formulario_valido().validar() == ()


def test_04_rejeita_tribunal_vazio():
    item = replace(formulario_valido(), tribunal=" ")
    assert "Informe o tribunal." in item.validar()


def test_05_rejeita_regiao_nao_numerica():
    item = DadosProcessoFormulario(
        tribunal="TRT",
        regiao_trt="A",
    )
    assert (
        "A região do TRT deve ser numérica."
        in item.validar()
    )


def test_06_rejeita_regiao_fora_do_intervalo():
    item = DadosProcessoFormulario(
        tribunal="TRT",
        regiao_trt="25",
    )
    assert (
        "A região do TRT deve estar entre 1 e 24."
        in item.validar()
    )


def test_07_rejeita_uf_invalida():
    item = replace(formulario_valido(), uf="R")
    assert "A UF deve possuir duas letras." in item.validar()


def test_08_rejeita_numero_cnj_invalido():
    item = replace(
        formulario_valido(),
        numero_processo="123",
    )
    assert any(
        "padrão CNJ" in erro
        for erro in item.validar()
    )


def test_09_rejeita_reclamante_vazio():
    item = replace(formulario_valido(), reclamante="")
    assert "Informe o reclamante." in item.validar()


def test_10_rejeita_reclamada_vazia():
    item = replace(formulario_valido(), reclamada="")
    assert "Informe a reclamada." in item.validar()


def test_11_cria_identificacao():
    identificacao = formulario_valido().criar_identificacao()
    assert isinstance(identificacao, IdentificacaoProcesso)


def test_12_normaliza_uf_no_dominio():
    identificacao = formulario_valido().criar_identificacao()
    assert identificacao.orgao_julgador.uf == "RJ"


def test_13_preserva_magistrado():
    identificacao = formulario_valido().criar_identificacao()
    assert identificacao.magistrado == "Dra. Maria da Silva"


def test_14_preserva_perito():
    identificacao = formulario_valido().criar_identificacao()
    assert identificacao.perito == "João Perito"


def test_15_opcionais_vazios_viram_none():
    item = DadosProcessoFormulario(
        tribunal="TRT",
        regiao_trt="1",
        vara="Vara",
        municipio="Rio",
        uf="RJ",
        numero_processo="0001234-55.2024.5.01.0007",
        classe_processual="Classe",
        reclamante="Autor",
        reclamada="Ré",
    )
    identificacao = item.criar_identificacao()
    assert identificacao.magistrado is None
    assert identificacao.perito is None


def test_16_estado_recebe_identificacao():
    identificacao = formulario_valido().criar_identificacao()
    estado = EstadoDesktop().definir_identificacao(
        identificacao
    )
    assert estado.identificacao_processo == identificacao


def test_17_estado_marca_alteracao_pendente():
    identificacao = formulario_valido().criar_identificacao()
    estado = EstadoDesktop().definir_identificacao(
        identificacao
    )
    assert estado.alteracoes_pendentes


def test_18_estado_rejeita_tipo_invalido():
    with pytest.raises(TypeError):
        EstadoDesktop().definir_identificacao("processo")


def test_19_controlador_registra_formulario():
    controlador = ControladorDesktop()
    erros = controlador.registrar_identificacao(
        formulario_valido()
    )
    assert erros == ()
    assert controlador.estado.identificacao_processo is not None


def test_20_controlador_nao_registra_invalido():
    controlador = ControladorDesktop()
    erros = controlador.registrar_identificacao(
        DadosProcessoFormulario()
    )
    assert erros
    assert controlador.estado.identificacao_processo is None


def test_21_controlador_publica_identificacao():
    controlador = ControladorDesktop()
    recebidos = []
    controlador.observar(recebidos.append)
    controlador.registrar_identificacao(formulario_valido())
    assert recebidos[-1].identificacao_processo is not None


def test_22_registro_nao_muda_secao():
    controlador = ControladorDesktop()
    controlador.navegar(SecaoDesktop.PROCESSO)
    controlador.registrar_identificacao(formulario_valido())
    assert controlador.estado.secao_atual == SecaoDesktop.PROCESSO


def test_23_salvar_preserva_identificacao():
    controlador = ControladorDesktop()
    controlador.registrar_identificacao(formulario_valido())
    identificacao = controlador.estado.identificacao_processo
    controlador.salvar()
    assert controlador.estado.identificacao_processo == identificacao


def test_24_estado_continua_imutavel():
    estado = EstadoDesktop()
    with pytest.raises(FrozenInstanceError):
        estado.identificacao_processo = None


def test_25_formulario_e_imutavel():
    item = formulario_valido()
    with pytest.raises(FrozenInstanceError):
        item.reclamante = "Outro"
