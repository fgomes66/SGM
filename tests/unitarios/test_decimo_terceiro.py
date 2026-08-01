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
    DecimoTerceiroApurado,
    ParametrosDecimoTerceiro,
    ParcelaIncidencia,
    RegraIncidencia,
    ServicoComposicaoBase,
    ServicoDecimoTerceiro,
    TipoBaseIncidencia,
)


def valor(texto: str, moeda: str = "BRL") -> ValorMonetario:
    return ValorMonetario.criar(
        texto,
        OrigemFinanceira(
            descricao="Verba apurada",
            documento_id="MEMORIA-003",
        ),
        moeda=moeda,
        momento=datetime(
            2026,
            7,
            31,
            23,
            50,
            tzinfo=timezone.utc,
        ),
    )


def regra(
    incide: bool = True,
    base=TipoBaseIncidencia.DECIMO_TERCEIRO,
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
    base=TipoBaseIncidencia.DECIMO_TERCEIRO,
    moeda: str = "BRL",
) -> ParcelaIncidencia:
    return ParcelaIncidencia(
        verba=verba,
        valor=valor(texto, moeda),
        regra=regra(incide=incide, base=base),
        descricao=f"Parcela {verba.value}",
    )


def base_decimo(
    incluir_dsr: bool = True,
    moeda: str = "BRL",
):
    return ServicoComposicaoBase.compor(
        TipoBaseIncidencia.DECIMO_TERCEIRO,
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
) -> ParametrosDecimoTerceiro:
    return ParametrosDecimoTerceiro(
        avos=avos,
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
        ParametrosDecimoTerceiro(
            avos=12.0,
            fundamento="Critério.",
        )


def test_07_parametros_rejeitam_fundamento_vazio():
    with pytest.raises(ValueError):
        ParametrosDecimoTerceiro(
            avos=12,
            fundamento=" ",
        )


def test_08_parametros_sao_imutaveis():
    item = parametros()
    with pytest.raises(FrozenInstanceError):
        item.avos = 6


def test_09_base_decimo_soma_parcelas_incluidas():
    base = base_decimo()
    assert base.total.valor == Decimal("3300.00")


def test_10_decimo_integral_sobre_base():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(),
    )
    assert resultado.valor.valor == Decimal("3300.00")


def test_11_decimo_seis_doze_avos():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(6),
    )
    assert resultado.valor.valor == Decimal("1650.00")


def test_12_decimo_um_doze_avo():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(1),
    )
    assert resultado.valor.valor == Decimal("275.00")


def test_13_zero_avos_gera_zero():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(0),
    )
    assert resultado.valor.valor == Decimal("0.00")


def test_14_exclusao_do_dsr_altera_base():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(incluir_dsr=False),
        parametros(),
    )
    assert resultado.base.total.valor == Decimal("3000.00")
    assert resultado.valor.valor == Decimal("3000.00")


def test_15_servico_rejeita_base_fgts():
    base = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (
            parcela(
                base=TipoBaseIncidencia.FGTS,
            ),
        ),
    )
    with pytest.raises(ValueError):
        ServicoDecimoTerceiro.calcular(base, parametros())


def test_16_resultado_e_decimo_terceiro_apurado():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(),
    )
    assert isinstance(resultado, DecimoTerceiroApurado)


def test_17_resultado_preserva_base():
    base = base_decimo()
    resultado = ServicoDecimoTerceiro.calcular(
        base,
        parametros(),
    )
    assert resultado.base is base


def test_18_resultado_preserva_parametros():
    item = parametros()
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        item,
    )
    assert resultado.parametros is item


def test_19_resultado_registra_formula():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(),
    )
    assert resultado.formula_codigo == "FM-13-001"


def test_20_resultado_registra_verba_destino():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(),
    )
    assert resultado.verba_destino == CodigoVerba.DECIMO_TERCEIRO


def test_21_resultado_mantem_moeda():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(moeda="USD"),
        parametros(),
    )
    assert resultado.valor.moeda == "USD"


def test_22_historico_registra_multiplicacao():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(6),
    )
    tipos = [item.tipo for item in resultado.valor.historico]
    assert TipoOperacaoFinanceira.MULTIPLICACAO in tipos


def test_23_historico_termina_com_arredondamento():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(1),
    )
    assert (
        resultado.valor.historico[-1].tipo
        == TipoOperacaoFinanceira.ARREDONDAMENTO
    )


def test_24_arredondamento_final():
    base = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.DECIMO_TERCEIRO,
        (
            parcela(texto="100.01"),
        ),
    )
    resultado = ServicoDecimoTerceiro.calcular(
        base,
        parametros(1),
    )
    assert resultado.valor.valor == Decimal("8.33")


def test_25_memoria_expoe_base():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "Base do 13º: BRL 3300.00" in memoria


def test_26_memoria_expoe_avos():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(6),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "Avos: 6/12" in memoria


def test_27_memoria_expoe_valor():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(6),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "13º apurado: BRL 1650.00" in memoria


def test_28_memoria_expoe_parcelas_incluidas():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "PARCELA INCLUÍDA HORA_EXTRA: BRL 3000.00" in memoria
    assert "PARCELA INCLUÍDA DSR: BRL 300.00" in memoria


def test_29_memoria_expoe_parcela_excluida():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(incluir_dsr=False),
        parametros(),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "PARCELA EXCLUÍDA DSR" in memoria


def test_30_resultado_e_imutavel():
    resultado = ServicoDecimoTerceiro.calcular(
        base_decimo(),
        parametros(),
    )
    with pytest.raises(FrozenInstanceError):
        resultado.valor = valor("0")
