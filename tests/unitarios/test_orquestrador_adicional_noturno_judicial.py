from datetime import date
from decimal import Decimal

from sgm.dominio.trabalhista.liquidacao_judicial import (
    DadosContratoLiquidacao,
    EntradaCasoTrabalhista,
    MontadorPlanoLiquidacao,
    OrquestradorLiquidacaoJudicial,
    ParametrosLiquidacao,
    ParametrosVerbaJudicial,
    SentencaTrabalhista,
    VerbaDeferida,
)


def _entrada():
    verba = VerbaDeferida(
        codigo="ADICIONAL_NOTURNO",
        descricao="Adicional noturno",
        fundamento="Adicional noturno deferido.",
        parametros=ParametrosVerbaJudicial(
            percentual=Decimal("0.20"),
            quantidade=Decimal("5"),
            divisor=Decimal("200"),
            fundamento="Adicional noturno de 20%.",
        ),
    )

    return EntradaCasoTrabalhista(
        referencia_processo="TESTE-ORQUESTRADOR-AN-001",
        contrato=DadosContratoLiquidacao(
            data_admissao=date(2020, 1, 1),
            data_desligamento=date(2021, 12, 31),
            salario_base=Decimal("2000.00"),
            jornada_semanal=Decimal("40"),
        ),
        sentenca=SentencaTrabalhista(
            data_sentenca=date(2022, 6, 1),
            texto_dispositivo="Adicional noturno deferido.",
            verbas_deferidas=(verba,),
        ),
        parametros=ParametrosLiquidacao(
            data_calculo=date(2022, 6, 1),
            divisor_horas=Decimal("200"),
        ),
    )


def test_orquestrador_executa_adicional_noturno():
    entrada = _entrada()

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is True

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    assert resultado.quantidade_itens == 1

    item = resultado.itens[0]

    assert item.codigo_verba == "ADICIONAL_NOTURNO"
    assert item.valor.moeda == "BRL"
    assert item.valor.valor == Decimal("10.00")
    assert item.formula_codigo == "FM-AN-001"
    assert item.memoria


def test_memoria_adicional_noturno_contem_calculo():
    entrada = _entrada()

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    item = resultado.itens[0]

    memoria = "\n".join(item.memoria)

    assert "20" in memoria
    assert "5" in memoria
    assert "10.00" in memoria
