from datetime import date
from decimal import Decimal

from sgm.dominio.financeiro import OrigemFinanceira, ValorMonetario
from sgm.dominio.trabalhista.equiparacao_salarial import (
    CompetenciaEquiparacao,
)
from sgm.dominio.trabalhista.liquidacao_judicial import (
    DadosContratoLiquidacao,
    EntradaCasoTrabalhista,
    ParametrosLiquidacao,
    SentencaTrabalhista,
    VerbaDeferida,
)
from sgm.dominio.trabalhista.liquidacao_judicial.analisador_capacidade_judicial import (
    AnalisadorCapacidadeJudicial,
)
from sgm.dominio.trabalhista.liquidacao_judicial.diagnostico_capacidade_judicial import (
    CapacidadeVerbaJudicial,
)
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


def _valor(valor: str, documento: str):
    return ValorMonetario.criar(
        valor,
        OrigemFinanceira(
            descricao="Contracheque da equiparação.",
            documento_id=documento,
        ),
        moeda="BRL",
    )


def _entrada(verba):
    return EntradaCasoTrabalhista(
        referencia_processo="TESTE-DIAGNOSTICO-EQ-001",
        contrato=DadosContratoLiquidacao(
            data_admissao=date(1998, 1, 1),
            data_desligamento=date(2001, 4, 30),
            salario_base=Decimal("2000.00"),
            jornada_semanal=Decimal("40"),
        ),
        sentenca=SentencaTrabalhista(
            data_sentenca=date(2011, 6, 4),
            texto_dispositivo="Equiparação salarial deferida.",
            verbas_deferidas=(verba,),
        ),
        parametros=ParametrosLiquidacao(
            data_calculo=date(2011, 6, 4),
            divisor_horas=Decimal("200"),
        ),
    )


def test_equiparacao_sem_competencias_fica_bloqueada_por_dados():
    verba = VerbaDeferida(
        codigo="EQUIPARACAO_SALARIAL",
        descricao="Equiparação salarial",
        fundamento="Equiparação deferida.",
    )

    diagnostico = AnalisadorCapacidadeJudicial.analisar(
        _entrada(verba)
    )

    item = diagnostico.verbas[0]

    assert (
        item.capacidade
        is CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
    )

    assert any(
        "competências remuneratórias" in motivo
        for motivo in item.motivos
    )


def test_equiparacao_com_competencias_fica_executavel():
    competencia = CompetenciaEquiparacao(
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
        fundamento="Equiparação por diferença remuneratória.",
    )

    verba = VerbaDeferida(
        codigo="EQUIPARACAO_SALARIAL",
        descricao="Equiparação salarial",
        fundamento="Equiparação deferida.",
        competencias_equiparacao=(competencia,),
    )

    diagnostico = AnalisadorCapacidadeJudicial.analisar(
        _entrada(verba)
    )

    item = diagnostico.verbas[0]

    assert (
        item.capacidade
        is CapacidadeVerbaJudicial.EXECUTAVEL
    )

    assert diagnostico.totalmente_executavel is True
