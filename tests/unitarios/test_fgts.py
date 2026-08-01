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
    AliquotaFGTS,
    CodigoVerba,
    FGTSApurado,
    ParcelaIncidencia,
    RegraIncidencia,
    ServicoComposicaoBase,
    ServicoFGTS,
    TipoBaseIncidencia,
)


def valor(texto: str, moeda: str = "BRL") -> ValorMonetario:
    return ValorMonetario.criar(
        texto,
        OrigemFinanceira(
            descricao="Verba apurada",
            documento_id="MEMORIA-001",
        ),
        moeda=moeda,
        momento=datetime(
            2026,
            7,
            31,
            23,
            30,
            tzinfo=timezone.utc,
        ),
    )


def regra(
    incide: bool = True,
    base=TipoBaseIncidencia.FGTS,
) -> RegraIncidencia:
    return RegraIncidencia(
        base_destino=base,
        incide=incide,
        fundamento="Critério jurídico informado.",
        criterio_juridico_id=uuid4(),
    )


def parcela(
    verba=CodigoVerba.HORA_EXTRA,
    texto: str = "102.27",
    incide: bool = True,
    base=TipoBaseIncidencia.FGTS,
    moeda: str = "BRL",
) -> ParcelaIncidencia:
    return ParcelaIncidencia(
        verba=verba,
        valor=valor(texto, moeda),
        regra=regra(incide=incide, base=base),
        descricao=f"Parcela {verba.value}",
    )


def base_fgts(
    incluir_dsr: bool = True,
    moeda: str = "BRL",
):
    parcelas = [
        parcela(
            CodigoVerba.HORA_EXTRA,
            "102.27",
            True,
            moeda=moeda,
        ),
        parcela(
            CodigoVerba.DSR,
            "20.45",
            incluir_dsr,
            moeda=moeda,
        ),
    ]
    return ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        tuple(parcelas),
    )


def aliquota(
    percentual: str = "0.08",
) -> AliquotaFGTS:
    return AliquotaFGTS(
        percentual=Decimal(percentual),
        fundamento="Alíquota aplicável ao caso concreto.",
        criterio_juridico_id=uuid4(),
    )


def test_01_aliquota_oito_por_cento_valida():
    item = aliquota()
    assert item.percentual == Decimal("0.08")


def test_02_aliquota_zero_valida():
    item = aliquota("0")
    assert item.percentual == Decimal("0")


def test_03_aliquota_um_valida():
    item = aliquota("1")
    assert item.percentual == Decimal("1")


def test_04_aliquota_rejeita_float():
    with pytest.raises(TypeError):
        AliquotaFGTS(
            percentual=0.08,
            fundamento="Critério.",
        )


def test_05_aliquota_rejeita_negativa():
    with pytest.raises(ValueError):
        aliquota("-0.01")


def test_06_aliquota_rejeita_superior_a_um():
    with pytest.raises(ValueError):
        aliquota("1.01")


def test_07_aliquota_rejeita_fundamento_vazio():
    with pytest.raises(ValueError):
        AliquotaFGTS(
            percentual=Decimal("0.08"),
            fundamento=" ",
        )


def test_08_aliquota_rejeita_versao_zero():
    with pytest.raises(ValueError):
        AliquotaFGTS(
            percentual=Decimal("0.08"),
            fundamento="Critério.",
            versao=0,
        )


def test_09_aliquota_e_imutavel():
    item = aliquota()
    with pytest.raises(FrozenInstanceError):
        item.percentual = Decimal("0.10")


def test_10_percentual_exibicao_converte_oito():
    assert aliquota().percentual_exibicao == Decimal("8.00")


def test_11_base_fgts_soma_hora_extra_e_dsr():
    base = base_fgts()
    assert base.total.valor == Decimal("122.72")


def test_12_servico_calcula_oito_por_cento():
    resultado = ServicoFGTS.calcular(
        base_fgts(),
        aliquota(),
    )
    assert resultado.valor.valor == Decimal("9.82")


def test_13_servico_calcula_somente_horas_extras():
    resultado = ServicoFGTS.calcular(
        base_fgts(incluir_dsr=False),
        aliquota(),
    )
    assert resultado.base.total.valor == Decimal("102.27")
    assert resultado.valor.valor == Decimal("8.18")


def test_14_servico_calcula_aliquota_personalizada():
    resultado = ServicoFGTS.calcular(
        base_fgts(),
        aliquota("0.02"),
    )
    assert resultado.valor.valor == Decimal("2.45")


def test_15_servico_calcula_aliquota_zero():
    resultado = ServicoFGTS.calcular(
        base_fgts(),
        aliquota("0"),
    )
    assert resultado.valor.valor == Decimal("0.00")


def test_16_servico_rejeita_base_de_ferias():
    base = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FERIAS,
        (
            parcela(
                base=TipoBaseIncidencia.FERIAS,
            ),
        ),
    )
    with pytest.raises(ValueError):
        ServicoFGTS.calcular(base, aliquota())


def test_17_resultado_e_fgts_apurado():
    resultado = ServicoFGTS.calcular(
        base_fgts(),
        aliquota(),
    )
    assert isinstance(resultado, FGTSApurado)


def test_18_resultado_preserva_base():
    base = base_fgts()
    resultado = ServicoFGTS.calcular(base, aliquota())
    assert resultado.base is base


def test_19_resultado_preserva_aliquota():
    item = aliquota()
    resultado = ServicoFGTS.calcular(base_fgts(), item)
    assert resultado.aliquota is item


def test_20_resultado_registra_formula():
    resultado = ServicoFGTS.calcular(
        base_fgts(),
        aliquota(),
    )
    assert resultado.formula_codigo == "FM-FGTS-001"


def test_21_resultado_registra_verba_fgts():
    resultado = ServicoFGTS.calcular(
        base_fgts(),
        aliquota(),
    )
    assert resultado.verba_destino == CodigoVerba.FGTS


def test_22_resultado_mantem_moeda():
    resultado = ServicoFGTS.calcular(
        base_fgts(moeda="USD"),
        aliquota(),
    )
    assert resultado.valor.moeda == "USD"


def test_23_historico_registra_multiplicacao():
    resultado = ServicoFGTS.calcular(
        base_fgts(),
        aliquota(),
    )
    tipos = [item.tipo for item in resultado.valor.historico]
    assert TipoOperacaoFinanceira.MULTIPLICACAO in tipos


def test_24_historico_termina_com_arredondamento():
    resultado = ServicoFGTS.calcular(
        base_fgts(),
        aliquota(),
    )
    assert (
        resultado.valor.historico[-1].tipo
        == TipoOperacaoFinanceira.ARREDONDAMENTO
    )


def test_25_arredondamento_e_half_up():
    base = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (
            parcela(texto="100.0625"),
        ),
    )
    resultado = ServicoFGTS.calcular(
        base,
        aliquota("0.08"),
    )
    assert resultado.valor.valor == Decimal("8.00")


def test_26_memoria_expoe_base():
    resultado = ServicoFGTS.calcular(
        base_fgts(),
        aliquota(),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "Base do FGTS: BRL 122.72" in memoria


def test_27_memoria_expoe_aliquota():
    resultado = ServicoFGTS.calcular(
        base_fgts(),
        aliquota(),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "Alíquota: 8.00%" in memoria


def test_28_memoria_expoe_valor_apurado():
    resultado = ServicoFGTS.calcular(
        base_fgts(),
        aliquota(),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "FGTS apurado: BRL 9.82" in memoria


def test_29_memoria_expoe_parcelas_incluidas():
    resultado = ServicoFGTS.calcular(
        base_fgts(),
        aliquota(),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "PARCELA INCLUÍDA HORA_EXTRA: BRL 102.27" in memoria
    assert "PARCELA INCLUÍDA DSR: BRL 20.45" in memoria


def test_30_resultado_e_imutavel():
    resultado = ServicoFGTS.calcular(
        base_fgts(),
        aliquota(),
    )
    with pytest.raises(FrozenInstanceError):
        resultado.valor = valor("0")
