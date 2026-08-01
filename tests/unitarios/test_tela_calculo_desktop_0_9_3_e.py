from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal
from uuid import UUID

import pytest

from sgm.desktop import (
    ControladorDesktop,
    DadosCalculoFormulario,
    EventoContratualDesktop,
    RegistroProcesso,
    RepositorioProcessosJSON,
    ResultadoCalculoDesktop,
    SerializadorProcesso,
    ServicoCalculoDesktop,
    TipoEventoDesktop,
)
from tests.unitarios.test_cadastro_contrato_desktop_0_9_3_c import (
    form as contrato_valido,
)
from tests.unitarios.test_cadastro_processo_desktop_0_9_3_b import (
    formulario_valido,
)


def form_calculo():
    return DadosCalculoFormulario(
        competencia="2024-02-01",
        quantidade_horas="10",
        adicional_percentual="50",
        fundamento="Art. 7º, XVI, CF",
    )


def resultado():
    return ResultadoCalculoDesktop(
        competencia=date(2024, 2, 1),
        salario_base=Decimal("2200"),
        divisor=Decimal("220"),
        quantidade_horas=Decimal("10"),
        adicional_percentual=Decimal("0.5"),
        valor_hora=Decimal("10"),
        valor_hora_com_adicional=Decimal("15"),
        valor_total=Decimal("150"),
        fundamento="Art. 7º, XVI, CF",
    )


def test_01_formulario_valido():
    assert form_calculo().validar() == ()


def test_02_rejeita_data_invalida():
    assert replace(
        form_calculo(),
        competencia="01/02/2024",
    ).validar()


def test_03_rejeita_horas_zero():
    assert replace(
        form_calculo(),
        quantidade_horas="0",
    ).validar()


def test_04_rejeita_adicional_negativo():
    assert replace(
        form_calculo(),
        adicional_percentual="-1",
    ).validar()


def test_05_decimal_brasileiro():
    _, horas, adicional, _ = replace(
        form_calculo(),
        quantidade_horas="10,5",
    ).valores()
    assert horas == Decimal("10.5")
    assert adicional == Decimal("0.5")


def test_06_resultado_valido():
    assert resultado().valor_total == Decimal("150")


def test_07_resultado_imutavel():
    with pytest.raises(FrozenInstanceError):
        resultado().valor_total = Decimal("0")


def test_08_memoria_contem_formula():
    assert "Fórmula: FM-HE-001" in resultado().memoria_resumida()


def test_09_salario_inicial_vigente():
    contrato = contrato_valido().criar_contrato()
    salario = ServicoCalculoDesktop.salario_vigente(
        contrato,
        (),
        date(2024, 2, 1),
    )
    assert salario == contrato.salario_inicial


def test_10_salario_evento_vigente():
    contrato = contrato_valido().criar_contrato()
    evento = EventoContratualDesktop(
        TipoEventoDesktop.ALTERACAO_SALARIAL,
        date(2024, 1, 1),
        "Reajuste",
        "CCT",
        valor=Decimal("3500"),
    )
    assert ServicoCalculoDesktop.salario_vigente(
        contrato,
        (evento,),
        date(2024, 2, 1),
    ) == Decimal("3500")


def test_11_evento_futuro_nao_aplica():
    contrato = contrato_valido().criar_contrato()
    evento = EventoContratualDesktop(
        TipoEventoDesktop.ALTERACAO_SALARIAL,
        date(2025, 1, 1),
        "Reajuste",
        "CCT",
        valor=Decimal("3500"),
    )
    assert ServicoCalculoDesktop.salario_vigente(
        contrato,
        (evento,),
        date(2024, 2, 1),
    ) == contrato.salario_inicial


def test_12_divisor_inicial_vigente():
    contrato = contrato_valido().criar_contrato()
    assert ServicoCalculoDesktop.divisor_vigente(
        contrato,
        (),
        date(2024, 2, 1),
    ) == contrato.divisor_jornada


def test_13_divisor_evento_vigente():
    contrato = contrato_valido().criar_contrato()
    evento = EventoContratualDesktop(
        TipoEventoDesktop.ALTERACAO_DIVISOR,
        date(2024, 1, 1),
        "Mudança de divisor",
        "Jornada",
        valor=Decimal("200"),
    )
    assert ServicoCalculoDesktop.divisor_vigente(
        contrato,
        (evento,),
        date(2024, 2, 1),
    ) == Decimal("200")


def test_14_calculo_hora_extra():
    contrato = contrato_valido().criar_contrato()
    item = ServicoCalculoDesktop.calcular_horas_extras(
        contrato,
        (),
        date(2024, 2, 1),
        Decimal("10"),
        Decimal("0.5"),
        "Art. 7º, XVI, CF",
    )
    assert item.valor_total > 0


def test_15_calculo_usa_formula_oficial():
    contrato = contrato_valido().criar_contrato()
    item = ServicoCalculoDesktop.calcular_horas_extras(
        contrato,
        (),
        date(2024, 2, 1),
        Decimal("10"),
        Decimal("0.5"),
        "Fundamento",
    )
    assert item.formula_codigo == "FM-HE-001"


def test_16_rejeita_competencia_antes_admissao():
    contrato = contrato_valido().criar_contrato()
    with pytest.raises(ValueError):
        ServicoCalculoDesktop.calcular_horas_extras(
            contrato,
            (),
            date(2000, 1, 1),
            Decimal("10"),
            Decimal("0.5"),
            "Fundamento",
        )


def test_17_controlador_exige_contrato():
    controlador = ControladorDesktop()
    assert controlador.executar_calculo(form_calculo())


def test_18_controlador_executa():
    controlador = ControladorDesktop()
    controlador.registrar_contrato(contrato_valido())
    assert controlador.executar_calculo(form_calculo()) == ()
    assert len(controlador.estado.resultados_calculo) == 1


def test_19_controlador_marca_pendencia():
    controlador = ControladorDesktop()
    controlador.registrar_contrato(contrato_valido())
    controlador.executar_calculo(form_calculo())
    assert controlador.estado.alteracoes_pendentes


def test_20_controlador_exclui_resultado():
    controlador = ControladorDesktop()
    controlador.registrar_contrato(contrato_valido())
    controlador.executar_calculo(form_calculo())
    item = controlador.estado.resultados_calculo[0]
    assert controlador.excluir_resultado_calculo(item.id)
    assert controlador.estado.resultados_calculo == ()


def test_21_exclusao_inexistente():
    controlador = ControladorDesktop()
    assert not controlador.excluir_resultado_calculo(
        UUID("00000000-0000-0000-0000-000000000001")
    )


def test_22_serializa_calculo():
    registro = RegistroProcesso(
        "CASO-CALC",
        formulario_valido().criar_identificacao(),
        calculos=(resultado(),),
    )
    dados = SerializadorProcesso.para_dict(registro)
    assert dados["calculos"][0]["valor_total"] == "150"


def test_23_desserializa_calculo():
    registro = RegistroProcesso(
        "CASO-CALC",
        formulario_valido().criar_identificacao(),
        calculos=(resultado(),),
    )
    carregado = SerializadorProcesso.de_dict(
        SerializadorProcesso.para_dict(registro)
    )
    assert carregado.calculos == registro.calculos


def test_24_arquivo_antigo_sem_calculos():
    registro = RegistroProcesso(
        "CASO-ANTIGO",
        formulario_valido().criar_identificacao(),
    )
    dados = SerializadorProcesso.para_dict(registro)
    dados.pop("calculos")
    assert SerializadorProcesso.de_dict(dados).calculos == ()


def test_25_repositorio_preserva_calculos(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    item = resultado()
    registro = RegistroProcesso(
        "CASO-CALC",
        formulario_valido().criar_identificacao(),
        calculos=(item,),
    )
    repo.salvar(registro)
    assert repo.carregar("CASO-CALC").calculos == (item,)


def test_26_controlador_salva_calculos(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    controlador = ControladorDesktop(repositorio=repo)
    controlador.novo_processo("CASO-CALC")
    controlador.registrar_identificacao(formulario_valido())
    controlador.registrar_contrato(contrato_valido())
    controlador.executar_calculo(form_calculo())
    controlador.salvar()
    assert len(repo.carregar("CASO-CALC").calculos) == 1


def test_27_controlador_abre_calculos(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    repo.salvar(
        RegistroProcesso(
            "CASO-CALC",
            formulario_valido().criar_identificacao(),
            calculos=(resultado(),),
        )
    )
    controlador = ControladorDesktop(repositorio=repo)
    controlador.abrir("CASO-CALC")
    assert len(controlador.estado.resultados_calculo) == 1


def test_28_novo_processo_limpa_calculos():
    controlador = ControladorDesktop()
    controlador.registrar_contrato(contrato_valido())
    controlador.executar_calculo(form_calculo())
    controlador.novo_processo("NOVO")
    assert controlador.estado.resultados_calculo == ()


def test_29_resultados_ordenados():
    controlador = ControladorDesktop()
    controlador.registrar_contrato(contrato_valido())
    controlador.executar_calculo(
        replace(form_calculo(), competencia="2024-03-01")
    )
    controlador.executar_calculo(
        replace(form_calculo(), competencia="2024-02-01")
    )
    assert controlador.estado.resultados_calculo[0].competencia == (
        date(2024, 2, 1)
    )


def test_30_calculo_com_evento_salarial():
    contrato = contrato_valido().criar_contrato()
    evento = EventoContratualDesktop(
        TipoEventoDesktop.ALTERACAO_SALARIAL,
        date(2024, 1, 1),
        "Reajuste",
        "CCT",
        valor=Decimal("4400"),
    )
    item = ServicoCalculoDesktop.calcular_horas_extras(
        contrato,
        (evento,),
        date(2024, 2, 1),
        Decimal("1"),
        Decimal("0.5"),
        "Fundamento",
    )
    assert item.salario_base == Decimal("4400")
