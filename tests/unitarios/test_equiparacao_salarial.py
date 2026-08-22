from decimal import Decimal

from sgm.dominio.financeiro import OrigemFinanceira, ValorMonetario
from sgm.dominio.trabalhista.equiparacao_salarial import (
    CompetenciaEquiparacao,
    ServicoEquiparacaoSalarial,
)
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


def _valor(valor: str, documento: str):
    return ValorMonetario.criar(
        valor,
        OrigemFinanceira(
            descricao="Contracheque utilizado na equiparação.",
            documento_id=documento,
        ),
        moeda="BRL",
    )


def test_equiparacao_outubro_1999_material_didatico():
    competencia = CompetenciaEquiparacao(
        competencia=CompetenciaCalculo(
            ano=1999,
            mes=10,
        ),
        remuneracao_reclamante=_valor(
            "2006.33",
            "contracheque-reclamante-10-1999",
        ),
        remuneracao_paradigma=_valor(
            "2262.75",
            "contracheque-paradigma-10-1999",
        ),
        origem_reclamante="Contracheque reclamante 10/1999",
        origem_paradigma="Contracheque paradigma 10/1999",
        fundamento=(
            "Equiparação pela diferença de remuneração "
            "entre os comparados."
        ),
    )

    resultado = ServicoEquiparacaoSalarial.calcular(
        (competencia,),
        referencia="TESTE-EQUIPARACAO-001",
    )

    assert resultado.quantidade_competencias == 1
    assert resultado.resultados[0].competencia.como_texto() == "1999-10"
    assert (
        resultado.resultados[0].diferenca.valor
        == Decimal("256.42")
    )
    assert resultado.total_diferencas.valor == Decimal("256.42")
    assert resultado.total_diferencas.moeda == "BRL"
    assert resultado.memoria_resumida()


def test_equiparacao_soma_competencias():
    outubro = CompetenciaEquiparacao(
        competencia=CompetenciaCalculo(1999, 10),
        remuneracao_reclamante=_valor(
            "2006.33",
            "reclamante-1999-10",
        ),
        remuneracao_paradigma=_valor(
            "2262.75",
            "paradigma-1999-10",
        ),
        origem_reclamante="Contracheque reclamante 10/1999",
        origem_paradigma="Contracheque paradigma 10/1999",
        fundamento="Equiparação salarial.",
    )

    novembro = CompetenciaEquiparacao(
        competencia=CompetenciaCalculo(1999, 11),
        remuneracao_reclamante=_valor(
            "2100.00",
            "reclamante-1999-11",
        ),
        remuneracao_paradigma=_valor(
            "2300.00",
            "paradigma-1999-11",
        ),
        origem_reclamante="Contracheque reclamante 11/1999",
        origem_paradigma="Contracheque paradigma 11/1999",
        fundamento="Equiparação salarial.",
    )

    resultado = ServicoEquiparacaoSalarial.calcular(
        (novembro, outubro),
        referencia="TESTE-EQUIPARACAO-002",
    )

    assert resultado.quantidade_competencias == 2

    assert tuple(
        item.competencia.como_texto()
        for item in resultado.resultados
    ) == (
        "1999-10",
        "1999-11",
    )

    assert resultado.total_diferencas.valor == Decimal("456.42")


def test_equiparacao_nao_gera_diferenca_negativa():
    competencia = CompetenciaEquiparacao(
        competencia=CompetenciaCalculo(2000, 1),
        remuneracao_reclamante=_valor(
            "2500.00",
            "reclamante-2000-01",
        ),
        remuneracao_paradigma=_valor(
            "2400.00",
            "paradigma-2000-01",
        ),
        origem_reclamante="Contracheque reclamante 01/2000",
        origem_paradigma="Contracheque paradigma 01/2000",
        fundamento="Equiparação salarial.",
    )

    resultado = ServicoEquiparacaoSalarial.calcular(
        (competencia,),
        referencia="TESTE-EQUIPARACAO-003",
    )

    assert resultado.resultados[0].diferenca.valor == Decimal("0.00")
    assert resultado.total_diferencas.valor == Decimal("0.00")


def test_equiparacao_rejeita_competencia_duplicada():
    primeira = CompetenciaEquiparacao(
        competencia=CompetenciaCalculo(1999, 10),
        remuneracao_reclamante=_valor(
            "2000.00",
            "r1",
        ),
        remuneracao_paradigma=_valor(
            "2200.00",
            "p1",
        ),
        origem_reclamante="Contracheque R1",
        origem_paradigma="Contracheque P1",
        fundamento="Equiparação salarial.",
    )

    segunda = CompetenciaEquiparacao(
        competencia=CompetenciaCalculo(1999, 10),
        remuneracao_reclamante=_valor(
            "2050.00",
            "r2",
        ),
        remuneracao_paradigma=_valor(
            "2250.00",
            "p2",
        ),
        origem_reclamante="Contracheque R2",
        origem_paradigma="Contracheque P2",
        fundamento="Equiparação salarial.",
    )

    try:
        ServicoEquiparacaoSalarial.calcular(
            (primeira, segunda),
            referencia="TESTE-EQUIPARACAO-004",
        )
    except ValueError as erro:
        assert "duplicadas" in str(erro).lower()
    else:
        raise AssertionError(
            "Competências duplicadas deveriam ser rejeitadas."
        )
