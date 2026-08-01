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
    ComposicaoBaseIncidencia,
    ParcelaIncidencia,
    RegraIncidencia,
    ServicoComposicaoBase,
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
            0,
            tzinfo=timezone.utc,
        ),
    )


def regra(
    base=TipoBaseIncidencia.FGTS,
    incide: bool = True,
    fundamento: str = "Critério jurídico informado.",
) -> RegraIncidencia:
    return RegraIncidencia(
        base_destino=base,
        incide=incide,
        fundamento=fundamento,
        criterio_juridico_id=uuid4(),
    )


def parcela(
    verba=CodigoVerba.HORA_EXTRA,
    texto: str = "100.00",
    base=TipoBaseIncidencia.FGTS,
    incide: bool = True,
    moeda: str = "BRL",
) -> ParcelaIncidencia:
    return ParcelaIncidencia(
        verba=verba,
        valor=valor(texto, moeda),
        regra=regra(base=base, incide=incide),
        descricao=f"Parcela {verba.value}",
    )


def test_01_tipo_base_fgts_e_estavel():
    assert TipoBaseIncidencia.FGTS.value == "FGTS"


def test_02_regra_inclusiva_valida():
    item = regra()
    assert item.incide is True
    assert item.base_destino == TipoBaseIncidencia.FGTS


def test_03_regra_exclusiva_valida():
    item = regra(incide=False)
    assert item.incide is False


def test_04_regra_rejeita_indicador_nao_booleano():
    with pytest.raises(TypeError):
        RegraIncidencia(
            base_destino=TipoBaseIncidencia.FGTS,
            incide=1,
            fundamento="Critério.",
        )


def test_05_regra_rejeita_fundamento_vazio():
    with pytest.raises(ValueError):
        regra(fundamento=" ")


def test_06_regra_rejeita_versao_zero():
    with pytest.raises(ValueError):
        RegraIncidencia(
            base_destino=TipoBaseIncidencia.FGTS,
            incide=True,
            fundamento="Critério.",
            versao=0,
        )


def test_07_regra_e_imutavel():
    item = regra()
    with pytest.raises(FrozenInstanceError):
        item.incide = False


def test_08_parcela_valida_e_criada():
    item = parcela()
    assert item.verba == CodigoVerba.HORA_EXTRA
    assert item.valor.valor == Decimal("100.00")


def test_09_parcela_rejeita_descricao_vazia():
    with pytest.raises(ValueError):
        ParcelaIncidencia(
            verba=CodigoVerba.HORA_EXTRA,
            valor=valor("100.00"),
            regra=regra(),
            descricao=" ",
        )


def test_10_parcela_e_imutavel():
    item = parcela()
    with pytest.raises(FrozenInstanceError):
        item.descricao = "Alterada"


def test_11_servico_rejeita_lista_vazia():
    with pytest.raises(ValueError):
        ServicoComposicaoBase.compor(
            TipoBaseIncidencia.FGTS,
            (),
        )


def test_12_servico_rejeita_regra_de_outra_base():
    with pytest.raises(ValueError):
        ServicoComposicaoBase.compor(
            TipoBaseIncidencia.FGTS,
            (
                parcela(
                    base=TipoBaseIncidencia.FERIAS,
                ),
            ),
        )


def test_13_servico_rejeita_moedas_diferentes():
    with pytest.raises(ValueError):
        ServicoComposicaoBase.compor(
            TipoBaseIncidencia.FGTS,
            (
                parcela(texto="100.00", moeda="BRL"),
                parcela(texto="20.00", moeda="USD"),
            ),
        )


def test_14_uma_parcela_incluida_forma_base():
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (parcela(texto="100.00"),),
    )
    assert resultado.total.valor == Decimal("100.00")


def test_15_duas_parcelas_incluidas_sao_somadas():
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (
            parcela(
                verba=CodigoVerba.HORA_EXTRA,
                texto="100.00",
            ),
            parcela(
                verba=CodigoVerba.DSR,
                texto="20.00",
            ),
        ),
    )
    assert resultado.total.valor == Decimal("120.00")


def test_16_parcela_excluida_nao_compõe_base():
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (
            parcela(texto="100.00", incide=True),
            parcela(
                verba=CodigoVerba.DSR,
                texto="20.00",
                incide=False,
            ),
        ),
    )
    assert resultado.total.valor == Decimal("100.00")


def test_17_todas_excluidas_geram_base_zero():
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (
            parcela(texto="100.00", incide=False),
            parcela(
                verba=CodigoVerba.DSR,
                texto="20.00",
                incide=False,
            ),
        ),
    )
    assert resultado.total.valor == Decimal("0.00")


def test_18_resultado_preserva_base_destino():
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FERIAS,
        (
            parcela(
                base=TipoBaseIncidencia.FERIAS,
            ),
        ),
    )
    assert resultado.base_destino == TipoBaseIncidencia.FERIAS


def test_19_resultado_classifica_incluidas():
    incluida = parcela(incide=True)
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (incluida,),
    )
    assert resultado.parcelas_incluidas == (incluida,)


def test_20_resultado_classifica_excluidas():
    excluida = parcela(incide=False)
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (excluida,),
    )
    assert resultado.parcelas_excluidas == (excluida,)


def test_21_resultado_preserva_todas_avaliadas():
    itens = (
        parcela(texto="100.00"),
        parcela(
            verba=CodigoVerba.DSR,
            texto="20.00",
            incide=False,
        ),
    )
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        itens,
    )
    assert resultado.parcelas_avaliadas == itens


def test_22_resultado_registra_formula():
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (parcela(),),
    )
    assert resultado.formula_codigo == "FM-BASE-INC-001"


def test_23_soma_preserva_historico_financeiro():
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (
            parcela(texto="100.00"),
            parcela(
                verba=CodigoVerba.DSR,
                texto="20.00",
            ),
        ),
    )
    tipos = [item.tipo for item in resultado.total.historico]
    assert TipoOperacaoFinanceira.SOMA in tipos


def test_24_total_termina_com_arredondamento():
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (parcela(texto="100.005"),),
    )
    assert resultado.total.valor == Decimal("100.01")
    assert (
        resultado.total.historico[-1].tipo
        == TipoOperacaoFinanceira.ARREDONDAMENTO
    )


def test_25_base_zero_mantem_moeda():
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (
            parcela(
                texto="100.00",
                incide=False,
                moeda="USD",
            ),
        ),
    )
    assert resultado.total.moeda == "USD"


def test_26_memoria_expoe_inclusao():
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (parcela(texto="100.00"),),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "INCLUIR HORA_EXTRA: BRL 100.00" in memoria


def test_27_memoria_expoe_exclusao_e_fundamento():
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (parcela(texto="100.00", incide=False),),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "EXCLUIR HORA_EXTRA" in memoria
    assert "Critério jurídico informado." in memoria


def test_28_memoria_expoe_total():
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (parcela(texto="100.00"),),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "Total da base: BRL 100.00" in memoria


def test_29_mesma_parcela_pode_ter_regra_para_outra_base():
    fgts = parcela(
        texto="100.00",
        base=TipoBaseIncidencia.FGTS,
        incide=True,
    )
    ferias = parcela(
        texto="100.00",
        base=TipoBaseIncidencia.FERIAS,
        incide=False,
    )
    assert fgts.regra.base_destino != ferias.regra.base_destino
    assert fgts.regra.incide is True
    assert ferias.regra.incide is False


def test_30_composicao_e_imutavel():
    resultado = ServicoComposicaoBase.compor(
        TipoBaseIncidencia.FGTS,
        (parcela(),),
    )
    with pytest.raises(FrozenInstanceError):
        resultado.base_destino = TipoBaseIncidencia.FERIAS
