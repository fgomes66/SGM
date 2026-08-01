from dataclasses import FrozenInstanceError
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from sgm.dominio.financeiro import (
    OrigemFinanceira,
    TipoOperacaoFinanceira,
    ValorMonetario,
)
from sgm.dominio.jornada import Tempo
from sgm.dominio.trabalhista import (
    AdicionalHoraExtra,
    BaseDeCalculo,
    DivisorJornada,
    ServicoHoraExtra,
    ServicoValorHora,
    TipoAdicionalHoraExtra,
    TipoBaseCalculo,
)


def criar_valor(texto: str = "3000.00") -> ValorMonetario:
    return ValorMonetario.criar(
        texto,
        OrigemFinanceira(
            descricao="Salário contratual",
            documento_id="HOLERITE-07-2026",
            formula_codigo="FM-BASE-001",
        ),
        momento=datetime(
            2026,
            7,
            31,
            21,
            0,
            tzinfo=timezone.utc,
        ),
    )


def criar_base(texto: str = "3000.00") -> BaseDeCalculo:
    return BaseDeCalculo(
        valor=criar_valor(texto),
        tipo=TipoBaseCalculo.SALARIO_CONTRATUAL,
        competencia=date(2026, 7, 1),
        descricao="Salário contratual",
        origem_documental="Holerite de julho de 2026",
        criterio_juridico_id=uuid4(),
    )


def criar_divisor(valor: str = "220") -> DivisorJornada:
    return DivisorJornada(
        divisor=Decimal(valor),
        jornada_semanal_minutos=44 * 60,
        fundamento="Jornada semanal reconhecida.",
        criterio_juridico_id=uuid4(),
    )


def criar_valor_hora(
    salario: str = "3000.00",
    divisor: str = "220",
):
    return ServicoValorHora.calcular(
        criar_base(salario),
        criar_divisor(divisor),
    )


def criar_adicional(
    percentual: str = "0.50",
    tipo=TipoAdicionalHoraExtra.LEGAL_50,
) -> AdicionalHoraExtra:
    return AdicionalHoraExtra(
        percentual=Decimal(percentual),
        tipo=tipo,
        fundamento="Critério jurídico aplicável.",
        criterio_juridico_id=uuid4(),
    )


def test_01_tipo_adicional_possui_valor_estavel():
    assert TipoAdicionalHoraExtra.LEGAL_50.value == "LEGAL_50"


def test_02_adicional_50_e_valido():
    adicional = criar_adicional()
    assert adicional.percentual == Decimal("0.50")


def test_03_adicional_100_e_valido():
    adicional = criar_adicional(
        "1.00",
        TipoAdicionalHoraExtra.INTEGRAL_100,
    )
    assert adicional.fator_total == Decimal("2.00")


def test_04_adicional_rejeita_float():
    with pytest.raises(TypeError):
        AdicionalHoraExtra(
            percentual=0.50,
            tipo=TipoAdicionalHoraExtra.LEGAL_50,
            fundamento="Critério.",
        )


def test_05_adicional_rejeita_percentual_negativo():
    with pytest.raises(ValueError):
        criar_adicional("-0.01")


def test_06_adicional_rejeita_fundamento_vazio():
    with pytest.raises(ValueError):
        AdicionalHoraExtra(
            percentual=Decimal("0.50"),
            tipo=TipoAdicionalHoraExtra.LEGAL_50,
            fundamento=" ",
        )


def test_07_adicional_e_imutavel():
    adicional = criar_adicional()
    with pytest.raises(FrozenInstanceError):
        adicional.percentual = Decimal("1.00")


def test_08_percentual_exibicao_converte_50():
    assert criar_adicional().percentual_exibicao == Decimal("50.00")


def test_09_servico_rejeita_quantidade_zero():
    with pytest.raises(ValueError):
        ServicoHoraExtra.calcular(
            criar_valor_hora(),
            Tempo.zero(),
            criar_adicional(),
        )


def test_10_uma_hora_extra_50():
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("01:00"),
        criar_adicional(),
    )
    assert resultado.valor_total.valor == Decimal("20.45")


def test_11_cinco_horas_extras_50():
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("05:00"),
        criar_adicional(),
    )
    assert resultado.valor_total.valor == Decimal("102.27")


def test_12_uma_hora_extra_100():
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("01:00"),
        criar_adicional(
            "1.00",
            TipoAdicionalHoraExtra.INTEGRAL_100,
        ),
    )
    assert resultado.valor_total.valor == Decimal("27.27")


def test_13_cento_e_oitenta_horas_50():
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("180:00"),
        criar_adicional(),
    )
    assert resultado.valor_total.valor == Decimal("3681.82")


def test_14_quantidade_fracionaria_de_trinta_minutos():
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("00:30"),
        criar_adicional(),
    )
    assert resultado.valor_total.valor == Decimal("10.23")


def test_15_quantidade_de_um_minuto_preserva_precisao():
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("00:01"),
        criar_adicional(),
    )
    assert resultado.valor_total.valor == Decimal("0.34")


def test_16_valor_hora_com_adicional_nao_e_arredondado_antes():
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("01:00"),
        criar_adicional(),
    )
    esperado = (
        Decimal("3000.00")
        / Decimal("220")
        * Decimal("1.50")
    )
    assert resultado.valor_hora_com_adicional.valor == esperado


def test_17_total_e_arredondado_somente_no_final():
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("05:00"),
        criar_adicional(),
    )
    assert resultado.valor_total.valor.as_tuple().exponent == -2


def test_18_historico_registra_acrescimo_percentual():
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("01:00"),
        criar_adicional(),
    )
    tipos = [
        operacao.tipo
        for operacao in resultado.valor_total.historico
    ]
    assert TipoOperacaoFinanceira.ACRESCIMO_PERCENTUAL in tipos


def test_19_historico_registra_multiplicacao():
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("01:00"),
        criar_adicional(),
    )
    tipos = [
        operacao.tipo
        for operacao in resultado.valor_total.historico
    ]
    assert TipoOperacaoFinanceira.MULTIPLICACAO in tipos


def test_20_historico_registra_arredondamento():
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("01:00"),
        criar_adicional(),
    )
    assert (
        resultado.valor_total.historico[-1].tipo
        == TipoOperacaoFinanceira.ARREDONDAMENTO
    )


def test_21_resultado_preserva_valor_hora():
    valor_hora = criar_valor_hora()
    resultado = ServicoHoraExtra.calcular(
        valor_hora,
        Tempo.de_hhmm("01:00"),
        criar_adicional(),
    )
    assert resultado.valor_hora is valor_hora


def test_22_resultado_preserva_quantidade():
    quantidade = Tempo.de_hhmm("02:15")
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        quantidade,
        criar_adicional(),
    )
    assert resultado.quantidade is quantidade


def test_23_resultado_preserva_adicional():
    adicional = criar_adicional()
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("01:00"),
        adicional,
    )
    assert resultado.adicional is adicional


def test_24_resultado_registra_formula_oficial():
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("01:00"),
        criar_adicional(),
    )
    assert resultado.formula_codigo == "FM-HE-001"


def test_25_memoria_expoe_componentes_do_calculo():
    resultado = ServicoHoraExtra.calcular(
        criar_valor_hora(),
        Tempo.de_hhmm("05:00"),
        criar_adicional(),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "Adicional: 50.00%" in memoria
    assert "Quantidade: 05:00" in memoria
    assert "Valor total: BRL 102.27" in memoria
    assert "FM-HE-001" in memoria
