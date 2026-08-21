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


def _verba_hora_extra(
    quantidade=Decimal("10"),
    percentual=Decimal("0.50"),
):
    return VerbaDeferida(
        codigo="HORA_EXTRA",
        descricao="Horas extras",
        fundamento="Horas extras deferidas em sentença.",
        parametros=ParametrosVerbaJudicial(
            quantidade=quantidade,
            percentual=percentual,
            divisor=Decimal("220"),
            fundamento=(
                "10 horas extras com adicional judicial de 50%."
            ),
        ),
    )


def _verba_dsr(
    dias_uteis=22,
    dias_repouso=4,
):
    return VerbaDeferida(
        codigo="DSR",
        descricao="Reflexo das horas extras em DSR",
        fundamento="Reflexo em DSR deferido em sentença.",
        parametros=ParametrosVerbaJudicial(
            dias_uteis=dias_uteis,
            dias_repouso=dias_repouso,
            fundamento=(
                "Reflexo das horas extras em DSR."
            ),
        ),
    )


def _entrada(*verbas):
    return EntradaCasoTrabalhista(
        referencia_processo="TESTE-JUDICIAL-HE-DSR-001",
        contrato=DadosContratoLiquidacao(
            data_admissao=date(2024, 1, 2),
            data_desligamento=date(2025, 5, 31),
            salario_base=Decimal("3300.00"),
            jornada_semanal=Decimal("44"),
        ),
        sentenca=SentencaTrabalhista(
            data_sentenca=date(2025, 6, 10),
            data_transito_julgado=date(2025, 7, 15),
            texto_dispositivo=(
                "Defere-se o pagamento de horas extras "
                "e reflexos em DSR."
            ),
            verbas_deferidas=tuple(verbas),
        ),
        parametros=ParametrosLiquidacao(
            data_calculo=date(2025, 8, 1),
            divisor_horas=Decimal("220"),
            percentual_horas_extras=Decimal("0.50"),
        ),
    )


def test_hora_extra_10_horas_adicional_50():
    entrada = _entrada(
        _verba_hora_extra()
    )

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is True

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    assert resultado.quantidade_itens == 1

    item = resultado.itens[0]

    assert item.codigo_verba == "HORA_EXTRA"
    assert item.valor.moeda == "BRL"
    assert item.valor.valor == Decimal("225.00")
    assert item.formula_codigo == "FM-HE-001"
    assert item.memoria


def test_hora_extra_e_dsr_encadeados():
    entrada = _entrada(
        _verba_hora_extra(),
        _verba_dsr(),
    )

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is True

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    assert resultado.quantidade_itens == 2

    hora_extra = resultado.itens[0]
    dsr = resultado.itens[1]

    assert hora_extra.codigo_verba == "HORA_EXTRA"
    assert hora_extra.valor.valor == Decimal("225.00")

    assert dsr.codigo_verba == "DSR"
    assert dsr.valor.valor == Decimal("40.91")
    assert dsr.formula_codigo == "FM-DSR-001"
    assert dsr.memoria


def test_hora_extra_sem_quantidade_deve_bloquear():
    entrada = _entrada(
        _verba_hora_extra(
            quantidade=None
        )
    )

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is False

    assert any(
        item.codigo.endswith("-QUANTIDADE")
        for item in plano.validacao.erros
    )


def test_dsr_sem_dias_uteis_deve_bloquear():
    entrada = _entrada(
        _verba_hora_extra(),
        _verba_dsr(
            dias_uteis=None
        ),
    )

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is False

    assert any(
        item.codigo.endswith("-DIAS-UTEIS")
        for item in plano.validacao.erros
    )
