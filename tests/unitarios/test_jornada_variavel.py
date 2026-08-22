from datetime import date

from sgm.dominio.jornada import (
    Horario,
    Intervalo,
    PeriodoTrabalho,
    Tempo,
)
from sgm.dominio.trabalhista.jornada_variavel import (
    RegraJornadaPosicional,
    ServicoJornadaVariavel,
)
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


def _periodo(saida: str) -> PeriodoTrabalho:
    return PeriodoTrabalho(
        entrada=Horario.de_texto("08:00"),
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
        fundamento="Jornada variável reconhecida no título judicial.",
    )


def test_jornada_variavel_classifica_primeiros_e_ultimos_dias():
    competencia = CompetenciaCalculo(2026, 1)

    datas = tuple(
        date(2026, 1, dia)
        for dia in range(2, 12)
    )

    resultado = ServicoJornadaVariavel.calcular(
        competencia=competencia,
        datas_trabalhadas=datas,
        regra=_regra(),
    )

    assert resultado.quantidade_dias == 10

    especiais = tuple(
        item.data.day
        for item in resultado.dias
        if item.especial
    )

    assert especiais == (2, 3, 4, 9, 10, 11)


def test_jornada_variavel_calcula_horas_extras_por_tipo_de_dia():
    competencia = CompetenciaCalculo(2026, 1)

    datas = tuple(
        date(2026, 1, dia)
        for dia in range(2, 12)
    )

    resultado = ServicoJornadaVariavel.calcular(
        competencia=competencia,
        datas_trabalhadas=datas,
        regra=_regra(),
    )

    especiais = tuple(
        item
        for item in resultado.dias
        if item.especial
    )

    ordinarios = tuple(
        item
        for item in resultado.dias
        if not item.especial
    )

    # Especial:
    # 08:00-22:45 = 14h45 brutas
    # - 1h intervalo = 13h45 líquidas
    # - 8h normais = 5h45 extras.
    assert all(
        item.horas_extras.minutos == 345
        for item in especiais
    )

    # Ordinária:
    # 08:00-20:45 = 12h45 brutas
    # - 1h intervalo = 11h45 líquidas
    # - 8h normais = 3h45 extras.
    assert all(
        item.horas_extras.minutos == 225
        for item in ordinarios
    )

    # 6 dias especiais x 345 = 2070
    # 4 dias ordinários x 225 = 900
    # Total = 2970 minutos = 49h30.
    assert resultado.total_horas_extras.minutos == 2970
    assert resultado.total_horas_extras.para_hhmm() == "49:30"


def test_jornada_variavel_calcula_tempo_noturno():
    competencia = CompetenciaCalculo(2026, 1)

    datas = tuple(
        date(2026, 1, dia)
        for dia in range(2, 12)
    )

    resultado = ServicoJornadaVariavel.calcular(
        competencia=competencia,
        datas_trabalhadas=datas,
        regra=_regra(),
    )

    # Somente os 6 dias especiais ultrapassam 22:00.
    # Cada um possui 45 minutos após 22:00.
    # 6 x 45 = 270 minutos = 4h30.
    assert resultado.total_tempo_noturno.minutos == 270
    assert resultado.total_tempo_noturno.para_hhmm() == "04:30"


def test_jornada_variavel_considera_posicao_e_nao_dia_do_mes():
    competencia = CompetenciaCalculo(2026, 1)

    # Datas propositalmente espaçadas.
    datas = (
        date(2026, 1, 5),
        date(2026, 1, 8),
        date(2026, 1, 12),
        date(2026, 1, 19),
        date(2026, 1, 23),
        date(2026, 1, 28),
        date(2026, 1, 30),
    )

    resultado = ServicoJornadaVariavel.calcular(
        competencia=competencia,
        datas_trabalhadas=datas,
        regra=_regra(),
    )

    especiais = tuple(
        item.data.day
        for item in resultado.dias
        if item.especial
    )

    # Primeiros 3 e últimos 3 DIAS TRABALHADOS.
    assert especiais == (5, 8, 12, 23, 28, 30)


def test_jornada_variavel_rejeita_data_de_outra_competencia():
    competencia = CompetenciaCalculo(2026, 1)

    datas = (
        date(2026, 1, 30),
        date(2026, 2, 2),
    )

    try:
        ServicoJornadaVariavel.calcular(
            competencia=competencia,
            datas_trabalhadas=datas,
            regra=_regra(),
        )
    except ValueError as exc:
        assert "competência" in str(exc)
    else:
        raise AssertionError(
            "Era esperado ValueError para data de outra competência."
        )
