from datetime import date
from decimal import Decimal

from sgm.dominio.trabalhista.liquidacao_judicial import (
    DadosContratoLiquidacao,
    EntradaCasoTrabalhista,
    MontadorPlanoLiquidacao,
    ParametrosLiquidacao,
    ParametrosVerbaJudicial,
    SentencaTrabalhista,
    StatusItemLiquidacao,
    ValidadorCasoTrabalhista,
    VerbaDeferida,
)


def _entrada_decimo_terceiro_completa():
    verba = VerbaDeferida(
        codigo="DECIMO_TERCEIRO",
        descricao="13º salário",
        fundamento="Verba deferida em sentença.",
        parametros=ParametrosVerbaJudicial(
            avos=12,
            fundamento="12/12 avos deferidos.",
        ),
    )

    sentenca = SentencaTrabalhista(
        data_sentenca=date(2025, 6, 10),
        data_transito_julgado=date(2025, 7, 15),
        texto_dispositivo=(
            "Defere-se o pagamento do 13º salário."
        ),
        verbas_deferidas=(verba,),
    )

    contrato = DadosContratoLiquidacao(
        data_admissao=date(2024, 1, 2),
        data_desligamento=date(2025, 5, 31),
        salario_base=Decimal("3600.00"),
        jornada_semanal=Decimal("44"),
    )

    parametros = ParametrosLiquidacao(
        data_calculo=date(2025, 8, 1),
        divisor_horas=Decimal("220"),
    )

    return EntradaCasoTrabalhista(
        referencia_processo="TESTE-13-001",
        contrato=contrato,
        sentenca=sentenca,
        parametros=parametros,
    )


def test_caso_completo_deve_ser_valido():
    entrada = _entrada_decimo_terceiro_completa()

    resultado = ValidadorCasoTrabalhista.validar(
        entrada
    )

    assert resultado.valido is True
    assert resultado.erros == ()


def test_plano_valido_deve_ficar_apto():
    entrada = _entrada_decimo_terceiro_completa()

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is True
    assert plano.quantidade_itens == 1
    assert plano.itens[0].codigo_verba == "DECIMO_TERCEIRO"
    assert plano.itens[0].status is StatusItemLiquidacao.APTO


def test_decimo_terceiro_sem_avos_deve_ser_invalido():
    verba = VerbaDeferida(
        codigo="DECIMO_TERCEIRO",
        descricao="13º salário",
        fundamento="Verba deferida em sentença.",
    )

    entrada = EntradaCasoTrabalhista(
        referencia_processo="TESTE-13-002",
        contrato=DadosContratoLiquidacao(
            data_admissao=date(2024, 1, 2),
            data_desligamento=date(2025, 5, 31),
            salario_base=Decimal("3600.00"),
            jornada_semanal=Decimal("44"),
        ),
        sentenca=SentencaTrabalhista(
            data_sentenca=date(2025, 6, 10),
            texto_dispositivo=(
                "Defere-se o pagamento do 13º salário."
            ),
            verbas_deferidas=(verba,),
        ),
        parametros=ParametrosLiquidacao(
            data_calculo=date(2025, 8, 1),
            divisor_horas=Decimal("220"),
        ),
    )

    resultado = ValidadorCasoTrabalhista.validar(
        entrada
    )

    assert resultado.valido is False
    assert any(
        item.codigo.endswith("-AVOS")
        for item in resultado.erros
    )


def test_plano_invalido_deve_bloquear_item():
    verba = VerbaDeferida(
        codigo="DECIMO_TERCEIRO",
        descricao="13º salário",
        fundamento="Verba deferida em sentença.",
    )

    entrada = EntradaCasoTrabalhista(
        referencia_processo="TESTE-13-003",
        contrato=DadosContratoLiquidacao(
            data_admissao=date(2024, 1, 2),
            data_desligamento=date(2025, 5, 31),
            salario_base=Decimal("3600.00"),
            jornada_semanal=Decimal("44"),
        ),
        sentenca=SentencaTrabalhista(
            data_sentenca=date(2025, 6, 10),
            texto_dispositivo=(
                "Defere-se o pagamento do 13º salário."
            ),
            verbas_deferidas=(verba,),
        ),
        parametros=ParametrosLiquidacao(
            data_calculo=date(2025, 8, 1),
            divisor_horas=Decimal("220"),
        ),
    )

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is False
    assert plano.itens[0].status is StatusItemLiquidacao.BLOQUEADO
