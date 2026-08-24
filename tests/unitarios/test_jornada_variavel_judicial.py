from datetime import date

import pytest

from sgm.dominio.jornada import Horario, PeriodoTrabalho, Tempo
from sgm.dominio.trabalhista.jornada_variavel import RegraJornadaPosicional
from sgm.dominio.trabalhista.liquidacao_judicial.jornada_variavel_judicial import (
    JornadaVariavelJudicial,
)
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


def _regra():
    return RegraJornadaPosicional(
        periodo_ordinario=PeriodoTrabalho(
            entrada=Horario(8 * 60),
            saida=Horario(17 * 60),
        ),
        periodo_especial=PeriodoTrabalho(
            entrada=Horario(14 * 60),
            saida=Horario(23 * 60),
        ),
        primeiros_especiais=1,
        ultimos_especiais=1,
        limite_diario=Tempo(8 * 60),
        inicio_noturno=Horario(22 * 60),
        fundamento="Jornada variável reconhecida no título.",
    )


def test_jornada_variavel_judicial_deve_ordenar_datas():
    jornada = JornadaVariavelJudicial(
        competencia=CompetenciaCalculo(ano=2026, mes=8),
        datas_trabalhadas=(
            date(2026, 8, 20),
            date(2026, 8, 5),
            date(2026, 8, 12),
        ),
        regra=_regra(),
    )

    assert jornada.datas_trabalhadas == (
        date(2026, 8, 5),
        date(2026, 8, 12),
        date(2026, 8, 20),
    )


def test_jornada_variavel_judicial_deve_rejeitar_data_de_outra_competencia():
    with pytest.raises(
        ValueError,
        match="competência da jornada variável judicial",
    ):
        JornadaVariavelJudicial(
            competencia=CompetenciaCalculo(ano=2026, mes=8),
            datas_trabalhadas=(
                date(2026, 8, 5),
                date(2026, 9, 1),
            ),
            regra=_regra(),
        )


def test_jornada_variavel_judicial_deve_rejeitar_datas_duplicadas():
    with pytest.raises(
        ValueError,
        match="Datas trabalhadas duplicadas",
    ):
        JornadaVariavelJudicial(
            competencia=CompetenciaCalculo(ano=2026, mes=8),
            datas_trabalhadas=(
                date(2026, 8, 5),
                date(2026, 8, 5),
            ),
            regra=_regra(),
        )
