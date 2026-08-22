from datetime import date
from decimal import Decimal

from sgm.dominio.financeiro import OrigemFinanceira, ValorMonetario
from sgm.dominio.jornada import Tempo
from sgm.dominio.trabalhista.adicional_noturno import (
    ParametrosAdicionalNoturno,
    ServicoAdicionalNoturno,
)
from sgm.dominio.trabalhista.jornada_financeira import (
    DivisorJornada,
    ServicoValorHora,
)
from sgm.dominio.trabalhista.remuneracao import (
    BaseDeCalculo,
    TipoBaseCalculo,
)


def _valor_hora_dez_reais():
    base = BaseDeCalculo(
        valor=ValorMonetario.criar(
            "2000.00",
            OrigemFinanceira(
                descricao="Salário-base para teste noturno.",
                documento_id="TESTE-AN-001",
            ),
            moeda="BRL",
        ),
        tipo=TipoBaseCalculo.SALARIO_CONTRATUAL,
        competencia=date(2025, 1, 1),
        descricao="Salário contratual",
        origem_documental="TESTE-AN-001",
    )

    divisor = DivisorJornada(
        divisor=Decimal("200"),
        jornada_semanal_minutos=2400,
        fundamento="Divisor artificial para teste.",
        descricao="Divisor 200",
    )

    return ServicoValorHora.calcular(
        base,
        divisor,
    )


def test_adicional_noturno_20_porcento_cinco_horas():
    valor_hora = _valor_hora_dez_reais()

    parametros = ParametrosAdicionalNoturno(
        percentual=Decimal("0.20"),
        fundamento="Adicional noturno de 20% para teste.",
    )

    resultado = ServicoAdicionalNoturno.calcular(
        valor_hora=valor_hora,
        quantidade=Tempo(300),
        parametros=parametros,
    )

    assert valor_hora.valor.valor == Decimal("10.00")

    assert (
        resultado.valor_adicional_hora.valor
        == Decimal("2.00")
    )

    assert resultado.quantidade_horas_exatas == Decimal("5")

    assert resultado.valor_total.moeda == "BRL"
    assert resultado.valor_total.valor == Decimal("10.00")
    assert resultado.formula_codigo == "FM-AN-001"
    assert resultado.memoria_resumida()


def test_adicional_noturno_uma_hora_e_meia():
    valor_hora = _valor_hora_dez_reais()

    parametros = ParametrosAdicionalNoturno(
        percentual=Decimal("0.20"),
        fundamento="Adicional noturno de 20% para teste.",
    )

    resultado = ServicoAdicionalNoturno.calcular(
        valor_hora=valor_hora,
        quantidade=Tempo(90),
        parametros=parametros,
    )

    assert resultado.quantidade_horas_exatas == Decimal("1.5")
    assert resultado.valor_total.valor == Decimal("3.00")


def test_adicional_noturno_rejeita_tempo_zero():
    valor_hora = _valor_hora_dez_reais()

    parametros = ParametrosAdicionalNoturno(
        percentual=Decimal("0.20"),
        fundamento="Adicional noturno de 20% para teste.",
    )

    try:
        ServicoAdicionalNoturno.calcular(
            valor_hora=valor_hora,
            quantidade=Tempo(0),
            parametros=parametros,
        )
    except ValueError as erro:
        assert "maior que zero" in str(erro).lower()
    else:
        raise AssertionError(
            "Tempo noturno zero deveria ser rejeitado."
        )


def test_percentual_noturno_nao_pode_ser_negativo():
    try:
        ParametrosAdicionalNoturno(
            percentual=Decimal("-0.20"),
            fundamento="Teste.",
        )
    except ValueError as erro:
        assert "não pode ser negativo" in str(erro).lower()
    else:
        raise AssertionError(
            "Percentual negativo deveria ser rejeitado."
        )
