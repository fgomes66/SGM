from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from sgm.dominio.financeiro import (
    OrigemFinanceira,
    TipoOperacaoFinanceira,
    ValorMonetario,
)


def origem() -> OrigemFinanceira:
    return OrigemFinanceira(
        descricao="Salário-base",
        processo_id=uuid4(),
        criterio_id=uuid4(),
        formula_codigo="FM-SAL-001",
        documento_id="HOLERITE-2026-07",
    )


def valor(texto: str) -> ValorMonetario:
    return ValorMonetario.criar(
        texto,
        origem(),
        momento=datetime(2026, 7, 31, 19, 30, tzinfo=timezone.utc),
    )


def test_criacao_preserva_decimal_e_origem():
    item = valor("3000.00")
    assert item.valor == Decimal("3000.00")
    assert item.moeda == "BRL"
    assert item.origem.descricao == "Salário-base"
    assert item.historico[0].tipo == TipoOperacaoFinanceira.CRIACAO


def test_float_e_proibido():
    with pytest.raises(TypeError):
        ValorMonetario(3000.00, origem())


def test_objeto_e_imutavel():
    item = valor("100.00")
    with pytest.raises(FrozenInstanceError):
        item.valor = Decimal("200.00")


def test_soma_gera_novo_valor_e_historico():
    a = valor("100.00")
    b = valor("50.00")
    resultado = a.somar(b)

    assert resultado.valor == Decimal("150.00")
    assert resultado.id != a.id
    assert resultado.versao == a.versao + 1
    assert resultado.historico[-1].tipo == TipoOperacaoFinanceira.SOMA


def test_moedas_diferentes_sao_rejeitadas():
    a = valor("100.00")
    b = ValorMonetario.criar("50.00", origem(), moeda="USD")
    with pytest.raises(ValueError):
        a.somar(b)


def test_divisao_por_zero_e_rejeitada():
    with pytest.raises(ZeroDivisionError):
        valor("100.00").dividir(Decimal("0"))


def test_aplicar_percentual_retorna_apenas_parcela():
    resultado = valor("1000.00").aplicar_percentual(Decimal("0.50"))
    assert resultado.valor == Decimal("500.0000")


def test_acrescer_percentual_retorna_principal_mais_adicional():
    resultado = valor("1000.00").acrescer_percentual(Decimal("0.50"))
    assert resultado.valor == Decimal("1500.0000")


def test_arredondamento_half_up():
    resultado = valor("10.125").arredondar_centavos()
    assert resultado.valor == Decimal("10.13")
    assert (
        resultado.historico[-1].tipo
        == TipoOperacaoFinanceira.ARREDONDAMENTO
    )


def test_valor_negativo_e_permitido():
    item = valor("-250.00")
    assert item.valor == Decimal("-250.00")
    assert item.absoluto().valor == Decimal("250.00")


def test_serializacao_e_desserializacao_preservam_dna():
    original = valor("3000.00").dividir(Decimal("220"))
    restaurado = ValorMonetario.de_dict(original.para_dict())

    assert restaurado.id == original.id
    assert restaurado.valor == original.valor
    assert restaurado.origem == original.origem
    assert restaurado.historico == original.historico
    assert restaurado.versao == original.versao


def test_cadeia_financeira_hora_extra():
    salario = valor("3000.00")
    valor_hora = salario.dividir(Decimal("220"))
    hora_extra = valor_hora.acrescer_percentual(Decimal("0.50"))
    total = hora_extra.multiplicar(Decimal("180")).arredondar_centavos()

    assert total.valor == Decimal("3681.82")
    tipos = [item.tipo for item in total.historico]
    assert TipoOperacaoFinanceira.DIVISAO in tipos
    assert TipoOperacaoFinanceira.ACRESCIMO_PERCENTUAL in tipos
    assert TipoOperacaoFinanceira.MULTIPLICACAO in tipos
    assert TipoOperacaoFinanceira.ARREDONDAMENTO in tipos
