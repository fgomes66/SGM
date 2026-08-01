from decimal import Decimal

import pytest

from sgm.dominio.jornada import (
    CalculadoraJornada,
    Horario,
    Intervalo,
    PeriodoTrabalho,
    Tempo,
)


def test_tempo_converte_hhmm_para_minutos():
    tempo = Tempo.de_hhmm("08:15")
    assert tempo.minutos == 495
    assert tempo.para_hhmm() == "08:15"
    assert tempo.para_texto() == "8h15min"


def test_tempo_rejeita_minutos_invalidos():
    with pytest.raises(ValueError):
        Tempo.de_hhmm("08:75")


def test_tempo_converte_para_horas_decimais():
    tempo = Tempo.de_hhmm("01:15")
    assert tempo.horas_decimais == Decimal("1.2500")


def test_horario_valido():
    horario = Horario.de_texto("07:58")
    assert horario.minutos_desde_meia_noite == 478
    assert horario.para_texto() == "07:58"


def test_horario_invalido():
    with pytest.raises(ValueError):
        Horario.de_texto("24:00")


def test_jornada_com_intervalo():
    periodo = PeriodoTrabalho(
        entrada=Horario.de_texto("08:00"),
        saida=Horario.de_texto("17:15"),
        intervalos=(
            Intervalo(
                Horario.de_texto("12:00"),
                Horario.de_texto("13:00"),
            ),
        ),
    )
    resultado = CalculadoraJornada.calcular(periodo)

    assert resultado.tempo_bruto.minutos == 555
    assert resultado.tempo_intervalos.minutos == 60
    assert resultado.tempo_liquido.minutos == 495


def test_jornada_sem_intervalo():
    periodo = PeriodoTrabalho(
        entrada=Horario.de_texto("08:00"),
        saida=Horario.de_texto("16:00"),
    )
    resultado = CalculadoraJornada.calcular(periodo)

    assert resultado.tempo_liquido.para_hhmm() == "08:00"
    assert resultado.advertencias


def test_intervalo_fora_da_jornada_e_rejeitado():
    with pytest.raises(ValueError):
        PeriodoTrabalho(
            entrada=Horario.de_texto("08:00"),
            saida=Horario.de_texto("17:00"),
            intervalos=(
                Intervalo(
                    Horario.de_texto("07:30"),
                    Horario.de_texto("08:30"),
                ),
            ),
        )


def test_intervalos_sobrepostos_sao_rejeitados():
    with pytest.raises(ValueError):
        PeriodoTrabalho(
            entrada=Horario.de_texto("08:00"),
            saida=Horario.de_texto("18:00"),
            intervalos=(
                Intervalo(
                    Horario.de_texto("12:00"),
                    Horario.de_texto("13:00"),
                ),
                Intervalo(
                    Horario.de_texto("12:30"),
                    Horario.de_texto("13:30"),
                ),
            ),
        )


def test_saida_antes_da_entrada_e_rejeitada_nesta_versao():
    with pytest.raises(ValueError):
        PeriodoTrabalho(
            entrada=Horario.de_texto("17:00"),
            saida=Horario.de_texto("08:00"),
        )
