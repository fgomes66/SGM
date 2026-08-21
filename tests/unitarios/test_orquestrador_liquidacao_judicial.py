from datetime import date
from decimal import Decimal

from sgm.dominio.trabalhista.liquidacao_judicial import (
    DadosContratoLiquidacao,
    EntradaCasoTrabalhista,
    MontadorPlanoLiquidacao,
    OrquestradorLiquidacaoJudicial,
    ParametrosLiquidacao,
    ParametrosVerbaJudicial,
    SentencaTrabalhista,
    VerbaDeferida,
)


def test_fluxo_completo_decimo_terceiro():
    verba = VerbaDeferida(
        codigo="DECIMO_TERCEIRO",
        descricao="13º salário",
        fundamento="Verba deferida em sentença.",
        parametros=ParametrosVerbaJudicial(
            avos=12,
            fundamento="13º salário integral, 12/12 avos.",
        ),
    )

    sentenca = SentencaTrabalhista(
        data_sentenca=date(2025, 6, 10),
        data_transito_julgado=date(2025, 7, 15),
        texto_dispositivo=(
            "Defere-se o pagamento integral do 13º salário."
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

    entrada = EntradaCasoTrabalhista(
        referencia_processo="TESTE-JUDICIAL-13-001",
        contrato=contrato,
        sentenca=sentenca,
        parametros=parametros,
    )

    plano = MontadorPlanoLiquidacao.montar(entrada)

    assert plano.apto_para_execucao is True

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    assert resultado.quantidade_itens == 1

    item = resultado.itens[0]

    assert item.codigo_verba == "DECIMO_TERCEIRO"
    assert item.valor.moeda == "BRL"
    assert item.valor.valor == Decimal("3600.00")
    assert item.formula_codigo is not None
    assert item.memoria


def test_orquestrador_nao_executa_plano_invalido():
    verba = VerbaDeferida(
        codigo="DECIMO_TERCEIRO",
        descricao="13º salário",
        fundamento="Verba deferida em sentença.",
    )

    entrada = EntradaCasoTrabalhista(
        referencia_processo="TESTE-JUDICIAL-13-002",
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

    plano = MontadorPlanoLiquidacao.montar(entrada)

    assert plano.apto_para_execucao is False

    try:
        OrquestradorLiquidacaoJudicial.executar(plano)
    except ValueError as erro:
        assert "não está apto" in str(erro)
    else:
        raise AssertionError(
            "Plano inválido não poderia ter sido executado."
        )
