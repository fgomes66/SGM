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


def _entrada_aviso(
    salario=Decimal("3000.00"),
    dias_aviso=30,
    dias_mes=30,
):
    verba = VerbaDeferida(
        codigo="AVISO_PREVIO",
        descricao="Aviso-prévio indenizado",
        fundamento="Aviso-prévio deferido em sentença.",
        parametros=ParametrosVerbaJudicial(
            dias_aviso=dias_aviso,
            dias_mes_calculo=dias_mes,
            fundamento=(
                "Aviso-prévio indenizado conforme título judicial."
            ),
        ),
    )

    return EntradaCasoTrabalhista(
        referencia_processo="TESTE-JUDICIAL-AVISO-001",
        contrato=DadosContratoLiquidacao(
            data_admissao=date(2024, 1, 2),
            data_desligamento=date(2025, 5, 31),
            salario_base=salario,
            jornada_semanal=Decimal("44"),
        ),
        sentenca=SentencaTrabalhista(
            data_sentenca=date(2025, 6, 10),
            data_transito_julgado=date(2025, 7, 15),
            texto_dispositivo=(
                "Defere-se o pagamento do aviso-prévio indenizado."
            ),
            verbas_deferidas=(verba,),
        ),
        parametros=ParametrosLiquidacao(
            data_calculo=date(2025, 8, 1),
            divisor_horas=Decimal("220"),
        ),
    )


def test_aviso_30_dias():
    entrada = _entrada_aviso()

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is True

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    item = resultado.itens[0]

    assert item.codigo_verba == "AVISO_PREVIO"
    assert item.valor.moeda == "BRL"
    assert item.valor.valor == Decimal("3000.00")
    assert item.formula_codigo == "FM-AVP-001"
    assert item.memoria


def test_aviso_45_dias():
    entrada = _entrada_aviso(
        dias_aviso=45,
        dias_mes=30,
    )

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is True

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    item = resultado.itens[0]

    assert item.valor.valor == Decimal("4500.00")


def test_aviso_sem_dias_deve_bloquear():
    entrada = _entrada_aviso(
        dias_aviso=None
    )

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is False

    assert any(
        item.codigo.endswith("-DIAS")
        for item in plano.validacao.erros
    )


def test_aviso_sem_dias_mes_deve_bloquear():
    entrada = _entrada_aviso(
        dias_mes=None
    )

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is False

    assert any(
        item.codigo.endswith("-MES")
        for item in plano.validacao.erros
    )
