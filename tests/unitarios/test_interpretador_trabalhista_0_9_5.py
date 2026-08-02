from datetime import date
from decimal import Decimal

import pytest

from sgm.ia import (
    IntencaoTrabalhista,
    InterpretadorTrabalhista,
    TipoRescisao,
)


def test_01_identifica_rescisao_sem_justa_causa_e_dados():
    resultado = InterpretadorTrabalhista().interpretar(
        "Empregado admitido em 10/02/2020, dispensado sem justa causa "
        "em 15/07/2025, salário de R$ 3.500,00. Calcule as verbas rescisórias."
    )

    assert resultado.intencao == IntencaoTrabalhista.RESCISAO
    assert resultado.tipo_rescisao == TipoRescisao.SEM_JUSTA_CAUSA
    assert resultado.datas == (date(2020, 2, 10), date(2025, 7, 15))
    assert resultado.valores == (Decimal("3500.00"),)


def test_02_identifica_horas_extras_com_acentos_e_caixa_variada():
    resultado = InterpretadorTrabalhista().interpretar(
        "CALCULE as Horas Extras e os reflexos."
    )

    assert resultado.intencao == IntencaoTrabalhista.HORAS_EXTRAS
    assert resultado.tipo_rescisao is None


def test_03_identifica_pedido_de_demissao():
    resultado = InterpretadorTrabalhista().interpretar(
        "Pedi demissão em 01-08-2026 e quero saber a rescisão."
    )

    assert resultado.intencao == IntencaoTrabalhista.RESCISAO
    assert resultado.tipo_rescisao == TipoRescisao.PEDIDO_DEMISSAO
    assert resultado.datas == (date(2026, 8, 1),)


def test_04_ignora_data_invalida_e_remove_repeticoes():
    resultado = InterpretadorTrabalhista().interpretar(
        "Férias em 31/02/2025. Valor R$ 1.500,00 e novamente R$ 1.500,00."
    )

    assert resultado.intencao == IntencaoTrabalhista.FERIAS
    assert resultado.datas == ()
    assert resultado.valores == (Decimal("1500.00"),)


def test_05_rejeita_texto_vazio():
    with pytest.raises(ValueError, match="não pode ser vazio"):
        InterpretadorTrabalhista().interpretar("   ")
