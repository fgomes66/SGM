from datetime import date

from sgm.dominio.jornada import Horario, Intervalo, PeriodoTrabalho, Tempo
from sgm.dominio.trabalhista.jornada_variavel import (
    RegraJornadaPosicional,
    ServicoJornadaVariavel,
)
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


def _periodo(saida: str) -> PeriodoTrabalho:
    return PeriodoTrabalho(
        entrada=Horario.de_texto("09:00"),
        saida=Horario.de_texto(saida),
        intervalos=(
            Intervalo(
                inicio=Horario.de_texto("12:00"),
                fim=Horario.de_texto("13:00"),
            ),
        ),
    )


def _regra() -> RegraJornadaPosicional:
    return RegraJornadaPosicional(
        periodo_ordinario=_periodo("20:45"),
        periodo_especial=_periodo("22:45"),
        primeiros_especiais=3,
        ultimos_especiais=3,
        limite_diario=Tempo(8 * 60),
        inicio_noturno=Horario.de_texto("22:00"),
        fundamento="Jornada reconhecida no título judicial.",
    )


def _datas() -> tuple[date, ...]:
    return tuple(
        date(2025, 1, dia)
        for dia in range(1, 11)
    )


def test_jornada_variavel_classifica_primeiros_e_ultimos_dias():
    resultado = ServicoJornadaVariavel.calcular(
        competencia=CompetenciaCalculo(2025, 1),
        datas_trabalhadas=_datas(),
        regra=_regra(),
    )

    especiais = tuple(
        item.data.day
        for item in resultado.dias
        if item.especial
    )

    assert especiais == (1, 2, 3, 8, 9, 10)
    assert resultado.quantidade_dias == 10


def test_jornada_variavel_calcula_horas_extras():
    resultado = ServicoJornadaVariavel.calcular(
        competencia=CompetenciaCalculo(2025, 1),
        datas_trabalhadas=_datas(),
        regra=_regra(),
    )

    # Ordinária:
    # 09:00-20:45 = 11h45 brutas
    # - 1h intervalo = 10h45 líquidas
    # - 8h = 2h45 extras
    #
    # Especial:
    # 09:00-22:45 = 13h45 brutas
    # - 1h intervalo = 12h45 líquidas
    # - 8h = 4h45 extras
    #
    # 4 ordinários x 2h45 = 11h
    # 6 especiais x 4h45 = 28h30
    # Total = 39h30

    assert resultado.total_horas_extras.minutos == (
        39 * 60 + 30
    )
    assert resultado.total_horas_extras.para_hhmm() == "39:30"


def test_jornada_variavel_calcula_tempo_noturno():
    resultado = ServicoJornadaVariavel.calcular(
        competencia=CompetenciaCalculo(2025, 1),
        datas_trabalhadas=_datas(),
        regra=_regra(),
    )

    # Apenas os 6 dias especiais ultrapassam 22:00.
    # 6 x 45 minutos = 270 minutos = 4h30.

    assert resultado.total_tempo_noturno.minutos == 270
    assert resultado.total_tempo_noturno.para_hhmm() == "04:30"


def test_jornada_variavel_memoria_identifica_totais():
    resultado = ServicoJornadaVariavel.calcular(
        competencia=CompetenciaCalculo(2025, 1),
        datas_trabalhadas=_datas(),
        regra=_regra(),
    )

    memoria = "\n".join(resultado.memoria_resumida())

    assert "2025-01" in memoria
    assert "39:30" in memoria
    assert "04:30" in memoria
    assert "JORNADA ESPECIAL" in memoria
    assert "JORNADA ORDINÁRIA" in memoria


def test_jornada_variavel_rejeita_data_de_outra_competencia():
    datas = (
        date(2025, 1, 31),
        date(2025, 2, 1),
    )

    try:
        ServicoJornadaVariavel.calcular(
            competencia=CompetenciaCalculo(2025, 1),
            datas_trabalhadas=datas,
            regra=_regra(),
        )
    except ValueError as exc:
        assert "competência" in str(exc).lower()
    else:
        raise AssertionError(
            "Era esperado ValueError para data de outra competência."
        )

