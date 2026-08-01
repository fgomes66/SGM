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
    AvisoPrevioApurado,
    CodigoVerba,
    ParametrosAvisoPrevio,
    ParcelaIncidencia,
    RegraIncidencia,
    ServicoAvisoPrevio,
    ServicoComposicaoBase,
    TipoAvisoPrevio,
    TipoBaseIncidencia,
)


def valor(texto: str, moeda: str = "BRL") -> ValorMonetario:
    return ValorMonetario.criar(
        texto,
        OrigemFinanceira(
            descricao="Verba apurada",
            documento_id="MEMORIA-004",
        ),
        moeda=moeda,
        momento=datetime(
            2026,
            7,
            31,
            23,
            55,
            tzinfo=timezone.utc,
        ),
    )


def regra(
    incide: bool = True,
    base=TipoBaseIncidencia.AVISO_PREVIO,
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
    base=TipoBaseIncidencia.AVISO_PREVIO,
    moeda: str = "BRL",
) -> ParcelaIncidencia:
    return ParcelaIncidencia(
        verba=verba,
        valor=valor(texto, moeda),
        regra=regra(incide=incide, base=base),
        descricao=f"Parcela {verba.value}",
    )


def base_aviso(
    incluir_dsr: bool = True,
    moeda: str = "BRL",
):
    return ServicoComposicaoBase.compor(
        TipoBaseIncidencia.AVISO_PREVIO,
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
    dias: int = 30,
    dias_mes_calculo: int = 30,
    tipo=TipoAvisoPrevio.INDENIZADO,
) -> ParametrosAvisoPrevio:
    return ParametrosAvisoPrevio(
        tipo=tipo,
        dias=dias,
        dias_mes_calculo=dias_mes_calculo,
        fundamento="Parâmetros aplicáveis ao caso concreto.",
        criterio_juridico_id=uuid4(),
    )


def test_01_tipo_indenizado_e_estavel():
    assert TipoAvisoPrevio.INDENIZADO.value == "INDENIZADO"


def test_02_tipo_trabalhado_e_estavel():
    assert TipoAvisoPrevio.TRABALHADO.value == "TRABALHADO"


def test_03_parametros_trinta_dias_validos():
    item = parametros()
    assert item.dias == 30
    assert item.fator_dias == Decimal("1")


def test_04_parametros_trinta_e_tres_dias_validos():
    item = parametros(33)
    assert item.fator_dias == Decimal("1.1")


def test_05_parametros_zero_dias_validos():
    item = parametros(0)
    assert item.fator_dias == Decimal("0")


def test_06_parametros_rejeitam_dias_negativos():
    with pytest.raises(ValueError):
        parametros(-1)


def test_07_parametros_rejeitam_dias_float():
    with pytest.raises(TypeError):
        ParametrosAvisoPrevio(
            tipo=TipoAvisoPrevio.INDENIZADO,
            dias=30.0,
            dias_mes_calculo=30,
            fundamento="Critério.",
        )


def test_08_parametros_rejeitam_mes_zero():
    with pytest.raises(ValueError):
        parametros(30, 0)


def test_09_parametros_rejeitam_mes_float():
    with pytest.raises(TypeError):
        ParametrosAvisoPrevio(
            tipo=TipoAvisoPrevio.INDENIZADO,
            dias=30,
            dias_mes_calculo=30.0,
            fundamento="Critério.",
        )


def test_10_parametros_rejeitam_fundamento_vazio():
    with pytest.raises(ValueError):
        ParametrosAvisoPrevio(
            tipo=TipoAvisoPrevio.INDENIZADO,
            dias=30,
            dias_mes_calculo=30,
            fundamento=" ",
        )


def test_11_parametros_sao_imutaveis():
    item = parametros()
    with pytest.raises(FrozenInstanceError):
        item.dias = 33


def test_12_base_aviso_soma_parcelas_incluidas():
    base = base_aviso()
    assert base.total.valor == Decimal("3300.00")


def test_13_aviso_trinta_dias():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(),
        parametros(),
    )
    assert resultado.valor.valor == Decimal("3300.00")


def test_14_aviso_trinta_e_tres_dias():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(),
        parametros(33),
    )
    assert resultado.valor.valor == Decimal("3630.00")


def test_15_aviso_quinze_dias():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(),
        parametros(15),
    )
    assert resultado.valor.valor == Decimal("1650.00")


def test_16_aviso_zero_dias():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(),
        parametros(0),
    )
    assert resultado.valor.valor == Decimal("0.00")


def test_17_aviso_trabalhado_usa_mesma_formula_financeira():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(),
        parametros(
            30,
            30,
            TipoAvisoPrevio.TRABALHADO,
        ),
    )
    assert resultado.parametros.tipo == TipoAvisoPrevio.TRABALHADO
    assert resultado.valor.valor == Decimal("3300.00")


def test_18_exclusao_do_dsr_altera_base():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(incluir_dsr=False),
        parametros(),
    )
    assert resultado.base.total.valor == Decimal("3000.00")
    assert resultado.valor.valor == Decimal("3000.00")


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
        ServicoAvisoPrevio.calcular(base, parametros())


def test_20_resultado_e_aviso_apurado():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(),
        parametros(),
    )
    assert isinstance(resultado, AvisoPrevioApurado)


def test_21_resultado_preserva_base():
    base = base_aviso()
    resultado = ServicoAvisoPrevio.calcular(
        base,
        parametros(),
    )
    assert resultado.base is base


def test_22_resultado_preserva_parametros():
    item = parametros()
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(),
        item,
    )
    assert resultado.parametros is item


def test_23_resultado_registra_formula():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(),
        parametros(),
    )
    assert resultado.formula_codigo == "FM-AVP-001"


def test_24_resultado_registra_verba_destino():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(),
        parametros(),
    )
    assert resultado.verba_destino == CodigoVerba.AVISO_PREVIO


def test_25_resultado_mantem_moeda():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(moeda="USD"),
        parametros(),
    )
    assert resultado.valor.moeda == "USD"


def test_26_historico_registra_multiplicacao():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(),
        parametros(33),
    )
    tipos = [item.tipo for item in resultado.valor.historico]
    assert TipoOperacaoFinanceira.MULTIPLICACAO in tipos


def test_27_historico_termina_com_arredondamento():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(),
        parametros(33),
    )
    assert (
        resultado.valor.historico[-1].tipo
        == TipoOperacaoFinanceira.ARREDONDAMENTO
    )


def test_28_memoria_expoe_tipo_dias_e_valor():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(),
        parametros(33),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "Tipo: INDENIZADO" in memoria
    assert "Dias do aviso: 33" in memoria
    assert "Aviso-prévio apurado: BRL 3630.00" in memoria


def test_29_memoria_expoe_parcela_excluida():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(incluir_dsr=False),
        parametros(),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "PARCELA EXCLUÍDA DSR" in memoria


def test_30_resultado_e_imutavel():
    resultado = ServicoAvisoPrevio.calcular(
        base_aviso(),
        parametros(),
    )
    with pytest.raises(FrozenInstanceError):
        resultado.valor = valor("0")
