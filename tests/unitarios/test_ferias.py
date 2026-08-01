from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from sgm.dominio.financeiro import (
    OrigemFinanceira,
    TipoOperacaoFinanceira,
    ValorMonetario,
)
from sgm.dominio.trabalhista import (
    CodigoVerba,
    FeriasApuradas,
    ParametrosFerias,
    ParcelaIncidencia,
    RegraIncidencia,
    ServicoComposicaoBase,
    ServicoFerias,
    TipoBaseIncidencia,
)


def valor(texto: str, moeda: str = "BRL") -> ValorMonetario:
    return ValorMonetario.criar(
        texto,
        OrigemFinanceira(
            descricao="Verba apurada",
            documento_id="MEMORIA-002",
        ),
        moeda=moeda,
        momento=datetime(
            2026,
            7,
            31,
            23,
            45,
            tzinfo=timezone.utc,
        ),
    )


def regra(
    incide: bool = True,
    base=TipoBaseIncidencia.FERIAS,
) -> RegraIncidencia:
    return RegraIncidencia(
        base_destino=base,
        incide=incide,
        fundamento="Critério jurídico informado.",
        criterio_juridico_id=uuid4(),
    )


def parcela(
    verba=CodigoVerba.HORA_EXTRA,
    texto: str = "3000.00",
    incide: bool = True,
    base=TipoBaseIncidencia.FERIAS,
    moeda: str = "BRL",
) -> ParcelaIncidencia:
    return ParcelaIncidencia(
        verba=verba,
        valor=valor(texto, moeda),
        regra=regra(incide=incide, base=base),
        descricao=f"Parcela {verba.value}",
    )


def base_ferias(
    incluir_dsr: bool = True,
    moeda: str = "BRL",
):
    return ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FERIAS,
        (
            parcela(
                CodigoVerba.HORA_EXTRA,
                "3000.00",
                True,
                moeda=moeda,
            ),
            parcela(
                CodigoVerba.DSR,
                "300.00",
                incluir_dsr,
                moeda=moeda,
            ),
        ),
    )


def parametros(
    avos: int = 12,
    percentual_terco: str = "0.3333333333333333333333333333",
) -> ParametrosFerias:
    return ParametrosFerias(
        avos=avos,
        percentual_terco=Decimal(percentual_terco),
        fundamento="Parâmetros aplicáveis ao caso concreto.",
        criterio_juridico_id=uuid4(),
    )


def test_01_parametros_integrais_validos():
    item = parametros()
    assert item.avos == 12
    assert item.fator_avos == Decimal("1")


def test_02_parametros_proporcionais_validos():
    item = parametros(6)
    assert item.fator_avos == Decimal("0.5")


def test_03_parametros_zero_avos_validos():
    item = parametros(0)
    assert item.fator_avos == Decimal("0")


def test_04_parametros_rejeitam_avos_negativos():
    with pytest.raises(ValueError):
        parametros(-1)


def test_05_parametros_rejeitam_avos_superiores_a_doze():
    with pytest.raises(ValueError):
        parametros(13)


def test_06_parametros_rejeitam_avos_float():
    with pytest.raises(TypeError):
        ParametrosFerias(
            avos=12.0,
            percentual_terco=Decimal("0.3333"),
            fundamento="Critério.",
        )


def test_07_parametros_rejeitam_terco_float():
    with pytest.raises(TypeError):
        ParametrosFerias(
            avos=12,
            percentual_terco=0.3333,
            fundamento="Critério.",
        )


def test_08_parametros_rejeitam_terco_negativo():
    with pytest.raises(ValueError):
        parametros(12, "-0.01")


def test_09_parametros_rejeitam_terco_superior_a_um():
    with pytest.raises(ValueError):
        parametros(12, "1.01")


def test_10_parametros_rejeitam_fundamento_vazio():
    with pytest.raises(ValueError):
        ParametrosFerias(
            avos=12,
            percentual_terco=Decimal("0.3333"),
            fundamento=" ",
        )


def test_11_parametros_sao_imutaveis():
    item = parametros()
    with pytest.raises(FrozenInstanceError):
        item.avos = 6


def test_12_base_ferias_soma_parcelas_incluidas():
    base = base_ferias()
    assert base.total.valor == Decimal("3300.00")


def test_13_ferias_integrais_sobre_base():
    resultado = ServicoFerias.calcular(
        base_ferias(),
        parametros(),
    )
    assert resultado.valor_ferias.valor == Decimal("3300.00")


def test_14_terco_sobre_ferias_integrais():
    resultado = ServicoFerias.calcular(
        base_ferias(),
        parametros(),
    )
    assert resultado.valor_terco.valor == Decimal("1100.00")


def test_15_total_integrais_com_terco():
    resultado = ServicoFerias.calcular(
        base_ferias(),
        parametros(),
    )
    assert resultado.valor_total.valor == Decimal("4400.00")


def test_16_ferias_seis_doze_avos():
    resultado = ServicoFerias.calcular(
        base_ferias(),
        parametros(6),
    )
    assert resultado.valor_ferias.valor == Decimal("1650.00")
    assert resultado.valor_terco.valor == Decimal("550.00")
    assert resultado.valor_total.valor == Decimal("2200.00")


def test_17_zero_avos_gera_zero():
    resultado = ServicoFerias.calcular(
        base_ferias(),
        parametros(0),
    )
    assert resultado.valor_ferias.valor == Decimal("0.00")
    assert resultado.valor_terco.valor == Decimal("0.00")
    assert resultado.valor_total.valor == Decimal("0.00")


def test_18_exclusao_do_dsr_altera_base():
    resultado = ServicoFerias.calcular(
        base_ferias(incluir_dsr=False),
        parametros(),
    )
    assert resultado.base.total.valor == Decimal("3000.00")
    assert resultado.valor_total.valor == Decimal("4000.00")


def test_19_servico_rejeita_base_fgts():
    base = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (
            parcela(
                base=TipoBaseIncidencia.FGTS,
            ),
        ),
    )
    with pytest.raises(ValueError):
        ServicoFerias.calcular(base, parametros())


def test_20_resultado_e_ferias_apuradas():
    resultado = ServicoFerias.calcular(
        base_ferias(),
        parametros(),
    )
    assert isinstance(resultado, FeriasApuradas)


def test_21_resultado_preserva_base():
    base = base_ferias()
    resultado = ServicoFerias.calcular(base, parametros())
    assert resultado.base is base


def test_22_resultado_preserva_parametros():
    item = parametros()
    resultado = ServicoFerias.calcular(base_ferias(), item)
    assert resultado.parametros is item


def test_23_resultado_registra_formulas():
    resultado = ServicoFerias.calcular(
        base_ferias(),
        parametros(),
    )
    assert resultado.formula_ferias_codigo == "FM-FER-001"
    assert resultado.formula_terco_codigo == "FM-FER-002"


def test_24_resultado_registra_verba_ferias():
    resultado = ServicoFerias.calcular(
        base_ferias(),
        parametros(),
    )
    assert resultado.verba_destino == CodigoVerba.FERIAS


def test_25_resultado_mantem_moeda():
    resultado = ServicoFerias.calcular(
        base_ferias(moeda="USD"),
        parametros(),
    )
    assert resultado.valor_total.moeda == "USD"


def test_26_historico_ferias_registra_multiplicacao():
    resultado = ServicoFerias.calcular(
        base_ferias(),
        parametros(6),
    )
    tipos = [item.tipo for item in resultado.valor_ferias.historico]
    assert TipoOperacaoFinanceira.MULTIPLICACAO in tipos


def test_27_historico_total_registra_soma():
    resultado = ServicoFerias.calcular(
        base_ferias(),
        parametros(),
    )
    tipos = [item.tipo for item in resultado.valor_total.historico]
    assert TipoOperacaoFinanceira.SOMA in tipos


def test_28_memoria_expoe_base_avos_e_total():
    resultado = ServicoFerias.calcular(
        base_ferias(),
        parametros(6),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "Base de férias: BRL 3300.00" in memoria
    assert "Avos: 6/12" in memoria
    assert "Total de férias: BRL 2200.00" in memoria


def test_29_memoria_expoe_parcelas_incluidas():
    resultado = ServicoFerias.calcular(
        base_ferias(),
        parametros(),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "PARCELA INCLUÍDA HORA_EXTRA: BRL 3000.00" in memoria
    assert "PARCELA INCLUÍDA DSR: BRL 300.00" in memoria


def test_30_resultado_e_imutavel():
    resultado = ServicoFerias.calcular(
        base_ferias(),
        parametros(),
    )
    with pytest.raises(FrozenInstanceError):
        resultado.valor_total = valor("0")
