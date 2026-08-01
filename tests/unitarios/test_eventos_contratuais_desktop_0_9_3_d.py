from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal
from uuid import UUID

import pytest

from sgm.desktop import (
    ControladorDesktop,
    DadosEventoFormulario,
    EventoContratualDesktop,
    RegistroProcesso,
    RepositorioProcessosJSON,
    SerializadorProcesso,
    TipoEventoDesktop,
)
from tests.unitarios.test_cadastro_processo_desktop_0_9_3_b import formulario_valido


def evento_salario(data="2024-01-01", valor="3500,00", identificador=""):
    return DadosEventoFormulario(
        tipo=TipoEventoDesktop.ALTERACAO_SALARIAL.value,
        data_inicio=data,
        descricao="Reajuste salarial",
        fundamento="Norma coletiva",
        valor=valor,
        documento="CCT-2024",
        detalhes="percentual=5%\norigem=CCT",
        id=identificador,
    )


def test_01_tipos_estaveis():
    assert TipoEventoDesktop.RESCISAO.value == "RESCISAO"


def test_02_titulo_tipo():
    assert TipoEventoDesktop.ALTERACAO_SALARIAL.titulo == "Alteração salarial"


def test_03_cria_evento_salario():
    item = evento_salario().criar_evento()
    assert item.valor == Decimal("3500.00")


def test_04_normaliza_descricao():
    item = EventoContratualDesktop(
        TipoEventoDesktop.OUTRO, date(2024, 1, 1), " Evento ", " Motivo "
    )
    assert item.descricao == "Evento"


def test_05_rejeita_descricao_vazia():
    with pytest.raises(ValueError):
        EventoContratualDesktop(
            TipoEventoDesktop.OUTRO, date(2024, 1, 1), " ", "Motivo"
        )


def test_06_rejeita_fundamento_vazio():
    with pytest.raises(ValueError):
        EventoContratualDesktop(
            TipoEventoDesktop.OUTRO, date(2024, 1, 1), "Evento", " "
        )


def test_07_rejeita_data_final_anterior():
    with pytest.raises(ValueError):
        EventoContratualDesktop(
            TipoEventoDesktop.FERIAS,
            date(2024, 2, 1),
            "Férias",
            "Concessão",
            data_fim=date(2024, 1, 1),
        )


def test_08_ferias_exige_fim():
    with pytest.raises(ValueError):
        EventoContratualDesktop(
            TipoEventoDesktop.FERIAS, date(2024, 1, 1), "Férias", "Concessão"
        )


def test_09_salario_exige_valor():
    with pytest.raises(ValueError):
        EventoContratualDesktop(
            TipoEventoDesktop.ALTERACAO_SALARIAL,
            date(2024, 1, 1),
            "Reajuste",
            "CCT",
        )


def test_10_rejeita_valor_zero():
    with pytest.raises(ValueError):
        replace(evento_salario().criar_evento(), valor=Decimal("0"))


def test_11_dados_sao_imutaveis():
    item = evento_salario().criar_evento()
    with pytest.raises(TypeError):
        item.dados["x"] = "y"


def test_12_evento_e_imutavel():
    item = evento_salario().criar_evento()
    with pytest.raises(FrozenInstanceError):
        item.descricao = "Outro"


def test_13_formulario_valido():
    assert evento_salario().validar() == ()


def test_14_rejeita_tipo_invalido():
    erros = replace(evento_salario(), tipo="INVALIDO").validar()
    assert erros


def test_15_rejeita_data_invalida():
    assert replace(evento_salario(), data_inicio="01/01/2024").validar()


def test_16_decimal_brasileiro():
    assert evento_salario(valor="3.500,75").criar_evento().valor == Decimal("3500.75")


def test_17_detalhes_chave_valor():
    item = evento_salario().criar_evento()
    assert item.dados["percentual"] == "5%"


def test_18_preserva_id_na_edicao():
    original = evento_salario().criar_evento()
    editado = evento_salario(identificador=str(original.id)).criar_evento()
    assert editado.id == original.id


def test_19_controlador_adiciona_evento():
    controlador = ControladorDesktop()
    assert controlador.registrar_evento(evento_salario()) == ()
    assert len(controlador.estado.eventos_contratuais) == 1


def test_20_controlador_ordena_eventos():
    controlador = ControladorDesktop()
    controlador.registrar_evento(evento_salario("2024-02-01"))
    controlador.registrar_evento(evento_salario("2024-01-01"))
    datas = tuple(item.data_inicio for item in controlador.estado.eventos_contratuais)
    assert datas == (date(2024, 1, 1), date(2024, 2, 1))


def test_21_controlador_edita_evento():
    controlador = ControladorDesktop()
    controlador.registrar_evento(evento_salario())
    item = controlador.estado.eventos_contratuais[0]
    controlador.registrar_evento(
        replace(evento_salario(identificador=str(item.id)), descricao="Reajuste editado")
    )
    assert len(controlador.estado.eventos_contratuais) == 1
    assert controlador.estado.eventos_contratuais[0].descricao == "Reajuste editado"


def test_22_controlador_exclui_evento():
    controlador = ControladorDesktop()
    controlador.registrar_evento(evento_salario())
    item = controlador.estado.eventos_contratuais[0]
    assert controlador.excluir_evento(item.id)
    assert controlador.estado.eventos_contratuais == ()


def test_23_exclusao_inexistente_retorna_false():
    controlador = ControladorDesktop()
    assert not controlador.excluir_evento(UUID("00000000-0000-0000-0000-000000000001"))


def test_24_evento_marca_pendencia():
    controlador = ControladorDesktop()
    controlador.registrar_evento(evento_salario())
    assert controlador.estado.alteracoes_pendentes


def test_25_serializa_eventos():
    item = evento_salario().criar_evento()
    registro = RegistroProcesso(
        "CASO-EVT", formulario_valido().criar_identificacao(), eventos=(item,)
    )
    dados = SerializadorProcesso.para_dict(registro)
    assert dados["eventos"][0]["tipo"] == "ALTERACAO_SALARIAL"


def test_26_desserializa_eventos():
    item = evento_salario().criar_evento()
    registro = RegistroProcesso(
        "CASO-EVT", formulario_valido().criar_identificacao(), eventos=(item,)
    )
    carregado = SerializadorProcesso.de_dict(
        SerializadorProcesso.para_dict(registro)
    )
    assert carregado.eventos == (item,)


def test_27_arquivo_antigo_sem_eventos():
    registro = RegistroProcesso(
        "CASO-ANTIGO", formulario_valido().criar_identificacao()
    )
    dados = SerializadorProcesso.para_dict(registro)
    dados.pop("eventos")
    assert SerializadorProcesso.de_dict(dados).eventos == ()


def test_28_repositorio_preserva_eventos(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    registro = RegistroProcesso(
        "CASO-EVT",
        formulario_valido().criar_identificacao(),
        eventos=(evento_salario().criar_evento(),),
    )
    repo.salvar(registro)
    assert len(repo.carregar("CASO-EVT").eventos) == 1


def test_29_controlador_salva_eventos(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    controlador = ControladorDesktop(repositorio=repo)
    controlador.novo_processo("CASO-EVT")
    controlador.registrar_identificacao(formulario_valido())
    controlador.registrar_evento(evento_salario())
    controlador.salvar()
    assert len(repo.carregar("CASO-EVT").eventos) == 1


def test_30_controlador_abre_eventos(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    registro = RegistroProcesso(
        "CASO-EVT",
        formulario_valido().criar_identificacao(),
        eventos=(evento_salario().criar_evento(),),
    )
    repo.salvar(registro)
    controlador = ControladorDesktop(repositorio=repo)
    controlador.abrir("CASO-EVT")
    assert len(controlador.estado.eventos_contratuais) == 1


def test_31_novo_processo_limpa_eventos():
    controlador = ControladorDesktop()
    controlador.registrar_evento(evento_salario())
    controlador.novo_processo("NOVO")
    assert controlador.estado.eventos_contratuais == ()


def test_32_afastamento_com_periodo():
    formulario = DadosEventoFormulario(
        tipo="AFASTAMENTO",
        data_inicio="2024-01-01",
        data_fim="2024-01-10",
        descricao="Afastamento previdenciário",
        fundamento="Benefício previdenciário",
    )
    assert formulario.validar() == ()


def test_33_rescisao_sem_data_final():
    formulario = DadosEventoFormulario(
        tipo="RESCISAO",
        data_inicio="2024-12-31",
        descricao="Rescisão contratual",
        fundamento="Dispensa sem justa causa",
    )
    assert formulario.validar() == ()


def test_34_registro_ordena_eventos():
    a = evento_salario("2024-02-01").criar_evento()
    b = evento_salario("2024-01-01").criar_evento()
    registro = RegistroProcesso(
        "CASO", formulario_valido().criar_identificacao(), eventos=(a, b)
    )
    assert registro.eventos[0].data_inicio == date(2024, 1, 1)


def test_35_serializacao_e_deterministica():
    item = evento_salario().criar_evento()
    registro = RegistroProcesso(
        "CASO", formulario_valido().criar_identificacao(), eventos=(item,)
    )
    assert SerializadorProcesso.para_dict(registro) == SerializadorProcesso.para_dict(registro)
