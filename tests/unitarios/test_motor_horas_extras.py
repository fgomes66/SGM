from datetime import date
from decimal import Decimal

import pytest

from sgm.dominio.horas_extras import (
    CalculadoraHorasExtras,
    RegraHorasExtras,
    RegistroJornada,
)
from sgm.dominio.jornada import Tempo


def regra_padrao() -> RegraHorasExtras:
    return RegraHorasExtras(
        limite_diario=Tempo.de_hhmm("08:00"),
        limite_semanal=Tempo.de_hhmm("44:00"),
        adicional_padrao=Decimal("0.50"),
    )


def registro(dia: int, horas: str) -> RegistroJornada:
    return RegistroJornada(
        data=date(2026, 7, dia),
        tempo_trabalhado=Tempo.de_hhmm(horas),
    )


def test_regra_rejeita_limite_diario_zero():
    with pytest.raises(ValueError):
        RegraHorasExtras(
            limite_diario=Tempo.zero(),
            limite_semanal=Tempo.de_hhmm("44:00"),
        )


def test_regra_rejeita_adicional_float():
    with pytest.raises(TypeError):
        RegraHorasExtras(
            limite_diario=Tempo.de_hhmm("08:00"),
            limite_semanal=Tempo.de_hhmm("44:00"),
            adicional_padrao=0.50,
        )


def test_dia_de_oito_horas_nao_gera_extra():
    resultado = CalculadoraHorasExtras.apurar_dia(
        registro(1, "08:00"),
        regra_padrao(),
    )
    assert resultado.extras_diarias.minutos == 0
    assert resultado.horas_normais.para_hhmm() == "08:00"


def test_dia_de_nove_horas_gera_uma_extra():
    resultado = CalculadoraHorasExtras.apurar_dia(
        registro(1, "09:00"),
        regra_padrao(),
    )
    assert resultado.extras_diarias.para_hhmm() == "01:00"
    assert resultado.horas_normais.para_hhmm() == "08:00"


def test_semana_de_quarenta_horas_nao_gera_extra():
    registros = [registro(dia, "08:00") for dia in range(1, 6)]
    resultado = CalculadoraHorasExtras.apurar_semana(
        registros,
        regra_padrao(),
    )
    assert resultado.total_horas_extras.minutos == 0
    assert resultado.total_normal.para_hhmm() == "40:00"


def test_semana_com_extras_diarias_sem_duplicidade():
    registros = [registro(dia, "09:00") for dia in range(1, 6)]
    resultado = CalculadoraHorasExtras.apurar_semana(
        registros,
        regra_padrao(),
    )
    assert resultado.extras_diarias.para_hhmm() == "05:00"
    assert resultado.extras_semanais_nao_duplicadas.minutos == 0
    assert resultado.total_horas_extras.para_hhmm() == "05:00"


def test_excedente_semanal_nao_contado_diariamente():
    regra = RegraHorasExtras(
        limite_diario=Tempo.de_hhmm("10:00"),
        limite_semanal=Tempo.de_hhmm("44:00"),
        adicional_padrao=Decimal("0.50"),
    )
    registros = [registro(dia, "09:00") for dia in range(1, 6)]
    resultado = CalculadoraHorasExtras.apurar_semana(registros, regra)

    assert resultado.extras_diarias.minutos == 0
    assert resultado.extras_semanais_nao_duplicadas.para_hhmm() == "01:00"
    assert resultado.total_horas_extras.para_hhmm() == "01:00"


def test_semana_vazia_e_rejeitada():
    with pytest.raises(ValueError):
        CalculadoraHorasExtras.apurar_semana([], regra_padrao())


def test_registros_duplicados_na_mesma_data_sao_rejeitados():
    registros = [
        registro(1, "08:00"),
        registro(1, "07:00"),
    ]
    with pytest.raises(ValueError):
        CalculadoraHorasExtras.apurar_semana(
            registros,
            regra_padrao(),
        )


def test_memoria_registra_total_e_adicional():
    registros = [registro(dia, "09:00") for dia in range(1, 6)]
    resultado = CalculadoraHorasExtras.apurar_semana(
        registros,
        regra_padrao(),
    )

    memoria = "\n".join(resultado.memoria)
    assert "Total de horas extras: 05:00" in memoria
    assert "Adicional previsto: 0.50" in memoria
