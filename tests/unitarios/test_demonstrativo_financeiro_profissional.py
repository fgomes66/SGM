from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from sgm.dominio.trabalhista import (
    DemonstrativoFinanceiroProfissional,
    GeradorDemonstrativoFinanceiro,
    NaturezaFinanceira,
    ResumoCompetencia,
    ResumoNatureza,
    ResumoVerba,
)
from tests.unitarios.test_caso_temporal_completo import calcular


def gerar():
    return GeradorDemonstrativoFinanceiro.gerar(calcular())


def test_01_natureza_estavel():
    assert NaturezaFinanceira.FUNDIARIA.value == "FUNDIARIA"


def test_02_resumo_competencia_valido():
    resultado = calcular().resultados_mensais[0]
    item = ResumoCompetencia(
        resultado.competencia,
        resultado.subtotal,
        resultado.valor_final,
        True,
        resultado.plano.referencia,
    )
    assert item.ativa is True


def test_03_resumo_competencia_rejeita_referencia_vazia():
    resultado = calcular().resultados_mensais[0]
    with pytest.raises(ValueError):
        ResumoCompetencia(
            resultado.competencia,
            resultado.subtotal,
            resultado.valor_final,
            True,
            " ",
        )


def test_04_resumo_verba_rejeita_quantidade_zero():
    verba = calcular().resultados_mensais[0].liquidacao.verbas[0]
    with pytest.raises(ValueError):
        ResumoVerba(
            verba.codigo,
            verba.descricao,
            NaturezaFinanceira.REMUNERATORIA,
            verba.valor,
            0,
        )


def test_05_resumo_natureza_rejeita_quantidade_zero():
    valor = calcular().resultados_mensais[0].subtotal
    with pytest.raises(ValueError):
        ResumoNatureza(
            NaturezaFinanceira.OUTRA,
            valor,
            0,
        )


def test_06_gerador_retorna_demonstrativo():
    assert isinstance(
        gerar(),
        DemonstrativoFinanceiroProfissional,
    )


def test_07_demonstrativo_identifica_referencia():
    assert gerar().referencia == "CASO-0013"


def test_08_demonstrativo_possui_seis_competencias():
    assert len(gerar().competencias) == 6


def test_09_competencias_estao_ordenadas():
    assert tuple(
        item.competencia.como_texto()
        for item in gerar().competencias
    ) == (
        "2022-01",
        "2022-02",
        "2022-03",
        "2022-05",
        "2022-06",
        "2022-07",
    )


def test_10_demonstrativo_possui_seis_verbas():
    assert len(gerar().verbas) == 6


def test_11_ordem_das_verbas_e_estavel():
    assert tuple(
        item.codigo.value for item in gerar().verbas
    ) == (
        "HORA_EXTRA",
        "DSR",
        "FGTS",
        "FERIAS",
        "DECIMO_TERCEIRO",
        "AVISO_PREVIO",
    )


def test_12_horas_extras_sao_remuneratorias():
    item = next(
        verba for verba in gerar().verbas
        if verba.codigo.value == "HORA_EXTRA"
    )
    assert item.natureza == NaturezaFinanceira.REMUNERATORIA


def test_13_fgts_e_fundiario():
    item = next(
        verba for verba in gerar().verbas
        if verba.codigo.value == "FGTS"
    )
    assert item.natureza == NaturezaFinanceira.FUNDIARIA


def test_14_aviso_e_indenizatorio():
    item = next(
        verba for verba in gerar().verbas
        if verba.codigo.value == "AVISO_PREVIO"
    )
    assert item.natureza == NaturezaFinanceira.INDENIZATORIA


def test_15_resumos_de_verba_contam_seis_competencias():
    assert all(
        item.quantidade_competencias == 6
        for item in gerar().verbas
    )


def test_16_demonstrativo_possui_quatro_naturezas():
    assert tuple(
        item.natureza for item in gerar().naturezas
    ) == (
        NaturezaFinanceira.REMUNERATORIA,
        NaturezaFinanceira.REFLEXA,
        NaturezaFinanceira.FUNDIARIA,
        NaturezaFinanceira.INDENIZATORIA,
    )


def test_17_subtotal_geral_coincide_com_consolidado():
    resultado = calcular()
    demonstrativo = GeradorDemonstrativoFinanceiro.gerar(
        resultado
    )
    assert (
        demonstrativo.subtotal_geral.valor
        == resultado.consolidado.subtotal_consolidado.valor
    )


def test_18_valor_final_geral_coincide_com_consolidado():
    resultado = calcular()
    demonstrativo = GeradorDemonstrativoFinanceiro.gerar(
        resultado
    )
    assert (
        demonstrativo.valor_final_geral.valor
        == resultado.consolidado.valor_final_consolidado.valor
    )


def test_19_texto_contem_resumo_por_competencia():
    texto = gerar().como_texto()
    assert "RESUMO POR COMPETÊNCIA" in texto
    assert "2022-01 | subtotal=" in texto


def test_20_texto_contem_resumo_por_verba():
    texto = gerar().como_texto()
    assert "RESUMO POR VERBA" in texto
    assert "HORA_EXTRA | Horas extras" in texto


def test_21_texto_contem_resumo_por_natureza():
    texto = gerar().como_texto()
    assert "RESUMO POR NATUREZA" in texto
    assert "FUNDIARIA | BRL" in texto


def test_22_texto_contem_totais_gerais():
    texto = gerar().como_texto()
    assert "Subtotal geral: BRL" in texto
    assert "Valor final geral: BRL" in texto


def test_23_demonstrativo_registra_versao():
    assert gerar().versao_documento == "0.9.2-B"


def test_24_demonstrativo_e_imutavel():
    item = gerar()
    with pytest.raises(FrozenInstanceError):
        item.referencia = "OUTRA"


def test_25_geracao_e_reproduzivel():
    primeiro = gerar()
    segundo = gerar()
    assert primeiro.como_texto() == segundo.como_texto()
    assert (
        primeiro.subtotal_geral.valor
        == segundo.subtotal_geral.valor
    )
    assert (
        primeiro.valor_final_geral.valor
        == segundo.valor_final_geral.valor
    )
