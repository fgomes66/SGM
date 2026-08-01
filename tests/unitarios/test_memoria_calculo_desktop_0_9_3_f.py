from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal

import pytest

from sgm.desktop import (
    MemoriaCalculoDesktop,
    PassoMemoriaCalculo,
    ResultadoCalculoDesktop,
    ServicoMemoriaCalculoDesktop,
)


def resultado():
    return ResultadoCalculoDesktop(
        competencia=date(2026, 7, 10),
        salario_base=Decimal("3500"),
        divisor=Decimal("220"),
        quantidade_horas=Decimal("12"),
        adicional_percentual=Decimal("0.5"),
        valor_hora=Decimal("15.909090909"),
        valor_hora_com_adicional=Decimal("23.863636364"),
        valor_total=Decimal("286.36"),
        fundamento="Art. 7º, XVI, da Constituição Federal",
        formula_codigo="FM-HE-001",
    )


def passo():
    return PassoMemoriaCalculo(
        ordem=1,
        titulo="Valor da hora",
        expressao="3500 ÷ 220",
        resultado="15,909091",
        explicacao="Divisão do salário pelo divisor.",
    )


def memoria():
    return MemoriaCalculoDesktop(
        titulo="Memória Técnica",
        competencia="2026-07-10",
        verba="Horas Extras",
        fundamento="Art. 7º, XVI, CF",
        formula_codigo="FM-HE-001",
        motor="ServicoHoraExtra",
        passos=(passo(),),
        valor_total=Decimal("286.36"),
    )


def test_01_passo_valido():
    assert passo().ordem == 1


def test_02_passo_imutavel():
    with pytest.raises(FrozenInstanceError):
        passo().titulo = "Outro"


def test_03_rejeita_ordem_zero():
    with pytest.raises(ValueError):
        replace(passo(), ordem=0)


def test_04_rejeita_titulo_vazio():
    with pytest.raises(ValueError):
        replace(passo(), titulo=" ")


def test_05_rejeita_expressao_vazia():
    with pytest.raises(ValueError):
        replace(passo(), expressao=" ")


def test_06_rejeita_resultado_vazio():
    with pytest.raises(ValueError):
        replace(passo(), resultado=" ")


def test_07_rejeita_explicacao_vazia():
    with pytest.raises(ValueError):
        replace(passo(), explicacao=" ")


def test_08_memoria_valida():
    assert memoria().verba == "Horas Extras"


def test_09_memoria_imutavel():
    with pytest.raises(FrozenInstanceError):
        memoria().verba = "Outra"


def test_10_rejeita_memoria_sem_passos():
    with pytest.raises(ValueError):
        replace(memoria(), passos=())


def test_11_rejeita_titulo_memoria_vazio():
    with pytest.raises(ValueError):
        replace(memoria(), titulo=" ")


def test_12_rejeita_competencia_vazia():
    with pytest.raises(ValueError):
        replace(memoria(), competencia=" ")


def test_13_rejeita_verba_vazia():
    with pytest.raises(ValueError):
        replace(memoria(), verba=" ")


def test_14_rejeita_fundamento_vazio():
    with pytest.raises(ValueError):
        replace(memoria(), fundamento=" ")


def test_15_rejeita_formula_vazia():
    with pytest.raises(ValueError):
        replace(memoria(), formula_codigo=" ")


def test_16_rejeita_motor_vazio():
    with pytest.raises(ValueError):
        replace(memoria(), motor=" ")


def test_17_texto_contem_titulo():
    assert "MEMÓRIA TÉCNICA" in memoria().como_texto()


def test_18_texto_contem_competencia():
    assert "2026-07-10" in memoria().como_texto()


def test_19_texto_contem_formula():
    assert "FM-HE-001" in memoria().como_texto()


def test_20_texto_contem_motor():
    assert "ServicoHoraExtra" in memoria().como_texto()


def test_21_texto_contem_passo():
    assert "PASSO 1" in memoria().como_texto()


def test_22_texto_contem_resultado_final():
    assert "R$ 286,36" in memoria().como_texto()


def test_23_servico_gera_memoria():
    item = ServicoMemoriaCalculoDesktop.gerar(resultado())
    assert isinstance(item, MemoriaCalculoDesktop)


def test_24_servico_rejeita_tipo_invalido():
    with pytest.raises(TypeError):
        ServicoMemoriaCalculoDesktop.gerar(object())


def test_25_memoria_tem_tres_passos():
    assert len(
        ServicoMemoriaCalculoDesktop.gerar(resultado()).passos
    ) == 3


def test_26_primeiro_passo_valor_hora():
    item = ServicoMemoriaCalculoDesktop.gerar(resultado())
    assert "hora normal" in item.passos[0].titulo.lower()


def test_27_segundo_passo_adicional():
    item = ServicoMemoriaCalculoDesktop.gerar(resultado())
    assert "adicional" in item.passos[1].titulo.lower()


def test_28_terceiro_passo_quantidade():
    item = ServicoMemoriaCalculoDesktop.gerar(resultado())
    assert "quantidade" in item.passos[2].titulo.lower()


def test_29_memoria_preserva_fundamento():
    item = ServicoMemoriaCalculoDesktop.gerar(resultado())
    assert item.fundamento == resultado().fundamento


def test_30_memoria_preserva_formula():
    item = ServicoMemoriaCalculoDesktop.gerar(resultado())
    assert item.formula_codigo == "FM-HE-001"


def test_31_memoria_preserva_total():
    item = ServicoMemoriaCalculoDesktop.gerar(resultado())
    assert item.valor_total == Decimal("286.36")


def test_32_expressao_salario_divisor():
    item = ServicoMemoriaCalculoDesktop.gerar(resultado())
    assert "3.500,00" in item.passos[0].expressao
    assert "220,00" in item.passos[0].expressao


def test_33_expressao_adicional():
    item = ServicoMemoriaCalculoDesktop.gerar(resultado())
    assert "1,50" in item.passos[1].expressao


def test_34_expressao_quantidade():
    item = ServicoMemoriaCalculoDesktop.gerar(resultado())
    assert "12,00" in item.passos[2].expressao


def test_35_geracao_deterministica():
    primeiro = ServicoMemoriaCalculoDesktop.gerar(
        resultado()
    ).como_texto()
    segundo = ServicoMemoriaCalculoDesktop.gerar(
        resultado()
    ).como_texto()
    assert primeiro == segundo
