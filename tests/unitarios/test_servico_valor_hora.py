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
from sgm.dominio.trabalhista import (
    BaseDeCalculo,
    DivisorJornada,
    ServicoValorHora,
    TipoBaseCalculo,
    ValorHora,
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
            20,
            0,
            tzinfo=timezone.utc,
        ),
    )


def criar_base(texto: str = "3000.00") -> BaseDeCalculo:
    return BaseDeCalculo(
        valor=criar_valor(texto),
        tipo=TipoBaseCalculo.SALARIO_CONTRATUAL,
        competencia=date(2026, 7, 1),
        descricao="Salário contratual da competência",
        origem_documental="Holerite de julho de 2026",
        criterio_juridico_id=uuid4(),
    )


def criar_divisor(
    valor: str = "220",
    minutos: int = 44 * 60,
) -> DivisorJornada:
    return DivisorJornada(
        divisor=Decimal(valor),
        jornada_semanal_minutos=minutos,
        fundamento="Jornada semanal reconhecida no critério jurídico.",
        criterio_juridico_id=uuid4(),
    )


def test_01_tipo_base_possui_valor_estavel():
    assert (
        TipoBaseCalculo.SALARIO_CONTRATUAL.value
        == "SALARIO_CONTRATUAL"
    )


def test_02_base_valida_e_criada():
    base = criar_base()
    assert base.valor.valor == Decimal("3000.00")
    assert base.tipo == TipoBaseCalculo.SALARIO_CONTRATUAL


def test_03_base_rejeita_descricao_vazia():
    with pytest.raises(ValueError):
        BaseDeCalculo(
            valor=criar_valor(),
            tipo=TipoBaseCalculo.SALARIO_CONTRATUAL,
            competencia=date(2026, 7, 1),
            descricao=" ",
            origem_documental="Holerite",
        )


def test_04_base_rejeita_origem_documental_vazia():
    with pytest.raises(ValueError):
        BaseDeCalculo(
            valor=criar_valor(),
            tipo=TipoBaseCalculo.SALARIO_CONTRATUAL,
            competencia=date(2026, 7, 1),
            descricao="Salário",
            origem_documental=" ",
        )


def test_05_base_e_imutavel():
    base = criar_base()
    with pytest.raises(FrozenInstanceError):
        base.descricao = "Alterada"


def test_06_divisor_220_e_valido():
    divisor = criar_divisor()
    assert divisor.divisor == Decimal("220")
    assert divisor.jornada_semanal_horas == Decimal("44")


def test_07_divisor_200_e_valido():
    divisor = criar_divisor("200", 40 * 60)
    assert divisor.divisor == Decimal("200")
    assert divisor.jornada_semanal_horas == Decimal("40")


def test_08_divisor_rejeita_float():
    with pytest.raises(TypeError):
        DivisorJornada(
            divisor=220.0,
            jornada_semanal_minutos=2640,
            fundamento="Critério.",
        )


def test_09_divisor_rejeita_zero():
    with pytest.raises(ValueError):
        criar_divisor("0")


def test_10_divisor_rejeita_jornada_zero():
    with pytest.raises(ValueError):
        criar_divisor("220", 0)


def test_11_divisor_rejeita_fundamento_vazio():
    with pytest.raises(ValueError):
        DivisorJornada(
            divisor=Decimal("220"),
            jornada_semanal_minutos=2640,
            fundamento=" ",
        )


def test_12_servico_calcula_3000_por_220():
    resultado = ServicoValorHora.calcular(
        criar_base("3000.00"),
        criar_divisor("220"),
    )
    assert resultado.valor.valor == (
        Decimal("3000.00") / Decimal("220")
    )


def test_13_servico_calcula_5500_por_200():
    resultado = ServicoValorHora.calcular(
        criar_base("5500.00"),
        criar_divisor("200", 2400),
    )
    assert resultado.valor.valor == Decimal("27.50")


def test_14_resultado_e_valor_hora():
    resultado = ServicoValorHora.calcular(
        criar_base(),
        criar_divisor(),
    )
    assert isinstance(resultado, ValorHora)


def test_15_resultado_preserva_base():
    base = criar_base()
    resultado = ServicoValorHora.calcular(base, criar_divisor())
    assert resultado.base is base


def test_16_resultado_preserva_divisor():
    divisor = criar_divisor()
    resultado = ServicoValorHora.calcular(criar_base(), divisor)
    assert resultado.divisor is divisor


def test_17_resultado_registra_formula_oficial():
    resultado = ServicoValorHora.calcular(
        criar_base(),
        criar_divisor(),
    )
    assert resultado.formula_codigo == "FM-VH-001"


def test_18_historico_financeiro_registra_divisao():
    resultado = ServicoValorHora.calcular(
        criar_base(),
        criar_divisor(),
    )
    assert (
        resultado.valor.historico[-1].tipo
        == TipoOperacaoFinanceira.DIVISAO
    )


def test_19_calculo_nao_altera_valor_da_base():
    base = criar_base("3000.00")
    ServicoValorHora.calcular(base, criar_divisor())
    assert base.valor.valor == Decimal("3000.00")
    assert base.valor.versao == 1


def test_20_memoria_resumida_expoe_formula_e_operacao():
    resultado = ServicoValorHora.calcular(
        criar_base(),
        criar_divisor(),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "3000.00 / 220" in memoria
    assert "FM-VH-001" in memoria
    assert "Valor da hora:" in memoria
