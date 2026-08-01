from dataclasses import FrozenInstanceError

import pytest

from sgm.dominio.trabalhista import (
    CompetenciaCalculo,
    EventoContratual,
    LinhaTempoContratual,
    PeriodoContratual,
    TipoEventoContratual,
)


def competencia(texto: str) -> CompetenciaCalculo:
    return CompetenciaCalculo.de_texto(texto)


def evento(
    texto: str = "2022-03",
    tipo=TipoEventoContratual.REAJUSTE,
    descricao: str = "Reajuste salarial",
) -> EventoContratual:
    return EventoContratual(
        competencia=competencia(texto),
        tipo=tipo,
        descricao=descricao,
        fundamento="Evento informado no contrato.",
        documento_id="DOC-001",
    )


def linha(*eventos):
    return LinhaTempoContratual(
        periodo=PeriodoContratual(
            competencia("2022-01"),
            competencia("2022-05"),
        ),
        eventos=tuple(eventos),
        referencia="CASO-0012",
    )


def test_01_competencia_valida():
    item = competencia("2022-03")
    assert item.ano == 2022
    assert item.mes == 3


def test_02_competencia_rejeita_mes_zero():
    with pytest.raises(ValueError):
        CompetenciaCalculo(2022, 0)


def test_03_competencia_rejeita_mes_treze():
    with pytest.raises(ValueError):
        CompetenciaCalculo(2022, 13)


def test_04_competencia_rejeita_ano_invalido():
    with pytest.raises(ValueError):
        CompetenciaCalculo(1899, 1)


def test_05_competencia_rejeita_texto_invalido():
    with pytest.raises(ValueError):
        competencia("03/2022")


def test_06_competencia_formata_texto():
    assert competencia("2022-03").como_texto() == "2022-03"


def test_07_competencia_proxima_no_mes():
    assert competencia("2022-03").proxima == competencia("2022-04")


def test_08_competencia_proxima_muda_ano():
    assert competencia("2022-12").proxima == competencia("2023-01")


def test_09_competencia_anterior_muda_ano():
    assert competencia("2022-01").anterior == competencia("2021-12")


def test_10_competencia_e_ordenavel():
    assert competencia("2022-01") < competencia("2022-02")


def test_11_competencia_e_imutavel():
    item = competencia("2022-03")
    with pytest.raises(FrozenInstanceError):
        item.mes = 4


def test_12_periodo_valido():
    item = PeriodoContratual(
        competencia("2022-01"),
        competencia("2022-05"),
    )
    assert item.quantidade_competencias == 5


def test_13_periodo_rejeita_ordem_invertida():
    with pytest.raises(ValueError):
        PeriodoContratual(
            competencia("2022-05"),
            competencia("2022-01"),
        )


def test_14_periodo_gera_competencias_inclusivas():
    item = PeriodoContratual(
        competencia("2022-11"),
        competencia("2023-02"),
    )
    assert tuple(x.como_texto() for x in item.competencias()) == (
        "2022-11",
        "2022-12",
        "2023-01",
        "2023-02",
    )


def test_15_periodo_contem_competencia():
    item = PeriodoContratual(
        competencia("2022-01"),
        competencia("2022-05"),
    )
    assert item.contem(competencia("2022-03")) is True


def test_16_periodos_sobrepostos():
    primeiro = PeriodoContratual(
        competencia("2022-01"),
        competencia("2022-03"),
    )
    segundo = PeriodoContratual(
        competencia("2022-03"),
        competencia("2022-05"),
    )
    assert primeiro.sobrepoe(segundo) is True


def test_17_periodos_nao_sobrepostos():
    primeiro = PeriodoContratual(
        competencia("2022-01"),
        competencia("2022-03"),
    )
    segundo = PeriodoContratual(
        competencia("2022-04"),
        competencia("2022-05"),
    )
    assert primeiro.sobrepoe(segundo) is False


def test_18_tipo_evento_e_estavel():
    assert TipoEventoContratual.REAJUSTE.value == "REAJUSTE"


def test_19_evento_valido():
    item = evento()
    assert item.competencia == competencia("2022-03")


def test_20_evento_rejeita_descricao_vazia():
    with pytest.raises(ValueError):
        evento(descricao=" ")


def test_21_evento_rejeita_fundamento_vazio():
    with pytest.raises(ValueError):
        EventoContratual(
            competencia=competencia("2022-03"),
            tipo=TipoEventoContratual.REAJUSTE,
            descricao="Reajuste",
            fundamento=" ",
        )


def test_22_linha_ordena_eventos():
    resultado = linha(
        evento("2022-04", TipoEventoContratual.PROMOCAO),
        evento("2022-02", TipoEventoContratual.REAJUSTE),
    )
    assert tuple(
        item.competencia.como_texto()
        for item in resultado.eventos
    ) == ("2022-02", "2022-04")


def test_23_linha_rejeita_evento_fora_do_periodo():
    with pytest.raises(ValueError):
        linha(evento("2021-12"))


def test_24_adicionar_evento_preserva_original():
    original = linha()
    novo = original.adicionar_evento(evento("2022-03"))
    assert original.eventos == ()
    assert len(novo.eventos) == 1


def test_25_linha_filtra_eventos_por_competencia_e_tipo():
    resultado = linha(
        evento("2022-03", TipoEventoContratual.REAJUSTE),
        evento("2022-03", TipoEventoContratual.PROMOCAO),
        evento("2022-04", TipoEventoContratual.REAJUSTE),
    )
    assert len(
        resultado.eventos_da_competencia(
            competencia("2022-03")
        )
    ) == 2
    assert len(
        resultado.eventos_do_tipo(
            TipoEventoContratual.REAJUSTE
        )
    ) == 2
    assert resultado.contem_evento(
        TipoEventoContratual.PROMOCAO,
        competencia("2022-03"),
    ) is True
