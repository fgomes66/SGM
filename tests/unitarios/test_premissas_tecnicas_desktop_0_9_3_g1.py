from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest

from sgm.desktop import (
    FonteDadosDesktop,
    FundamentoJuridicoDesktop,
    PremissasTecnicasBuilderDesktop,
    PremissasTecnicasDesktop,
)
from tests.unitarios.test_cadastro_contrato_desktop_0_9_3_c import (
    form as contrato_valido,
)
from tests.unitarios.test_relatorio_tecnico_desktop_0_9_3_g import (
    evento,
    resultado,
)


def construir():
    return PremissasTecnicasBuilderDesktop.construir(
        contrato_valido().criar_contrato(),
        (evento(),),
        resultado(),
    )


def test_01_modelo_valido():
    assert isinstance(construir(), PremissasTecnicasDesktop)


def test_02_modelo_imutavel():
    premissas = construir()
    with pytest.raises(FrozenInstanceError):
        premissas.verba = "Outra"


def test_03_fundamento_valido():
    assert FundamentoJuridicoDesktop("CLT, art. 59").descricao == "CLT, art. 59"


def test_04_fundamento_vazio_rejeitado():
    with pytest.raises(ValueError):
        FundamentoJuridicoDesktop(" ")


def test_05_fonte_valida():
    assert FonteDadosDesktop("Processo").descricao == "Processo"


def test_06_fonte_vazia_rejeitada():
    with pytest.raises(ValueError):
        FonteDadosDesktop("")


def test_07_competencia_preservada():
    assert construir().competencia == date(2026, 7, 10)


def test_08_salario_inicial_preservado():
    assert construir().salario_inicial == Decimal("3500.00")


def test_09_salario_vigente_preservado():
    assert construir().salario_vigente == Decimal("3800")


def test_10_evento_salarial_identificado():
    premissas = construir()
    assert premissas.origem_base == "Evento contratual"
    assert premissas.evento_base == "Alteração salarial de 01/07/2026"


def test_11_sem_evento_usa_contrato():
    premissas = PremissasTecnicasBuilderDesktop.construir(
        contrato_valido().criar_contrato(),
        (),
        resultado(),
    )
    assert premissas.origem_base == "Contrato de trabalho"
    assert premissas.evento_base is None


def test_12_formula_e_versao():
    premissas = construir()
    assert premissas.formula == "FM-HE-001"
    assert premissas.versao_formula == "1.0"


def test_13_motor_e_versao():
    premissas = construir()
    assert premissas.motor == "SGM Engine — ServicoHoraExtra"
    assert premissas.versao_motor == "0.9.3-G1"


def test_14_precisoes():
    premissas = construir()
    assert premissas.precisao_intermediaria == 6
    assert premissas.precisao_monetaria == 2


def test_15_fundamentos_incluem_clt_e_evento():
    descricoes = tuple(item.descricao for item in construir().fundamentos)
    assert "CLT, art. 59" in descricoes
    assert "ACT 2026" in descricoes


def test_16_fontes_incluem_resultado_e_memoria():
    descricoes = tuple(item.descricao for item in construir().fontes)
    assert "Resultado persistido FM-HE-001" in descricoes
    assert "Memória técnica persistida" in descricoes
