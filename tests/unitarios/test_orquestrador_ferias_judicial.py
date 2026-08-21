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


def _entrada_ferias(
    avos: int = 12,
    percentual_terco: Decimal | None = Decimal(
        "0.3333333333333333333333333333"
    ),
):
    verba = VerbaDeferida(
        codigo="FERIAS",
        descricao="Férias acrescidas do terço constitucional",
        fundamento="Verba deferida em sentença.",
        parametros=ParametrosVerbaJudicial(
            avos=avos,
            percentual=percentual_terco,
            fundamento=(
                "Férias e terço constitucional deferidos."
            ),
        ),
    )

    return EntradaCasoTrabalhista(
        referencia_processo="TESTE-JUDICIAL-FERIAS-001",
        contrato=DadosContratoLiquidacao(
            data_admissao=date(2024, 1, 2),
            data_desligamento=date(2025, 5, 31),
            salario_base=Decimal("3600.00"),
            jornada_semanal=Decimal("44"),
        ),
        sentenca=SentencaTrabalhista(
            data_sentenca=date(2025, 6, 10),
            data_transito_julgado=date(2025, 7, 15),
            texto_dispositivo=(
                "Defere-se o pagamento de férias acrescidas "
                "do terço constitucional."
            ),
            verbas_deferidas=(verba,),
        ),
        parametros=ParametrosLiquidacao(
            data_calculo=date(2025, 8, 1),
            divisor_horas=Decimal("220"),
        ),
    )


def test_ferias_12_avos_com_terco():
    entrada = _entrada_ferias()

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is True

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    assert resultado.quantidade_itens == 1

    item = resultado.itens[0]

    assert item.codigo_verba == "FERIAS"
    assert item.valor.moeda == "BRL"
    assert item.valor.valor == Decimal("4800.00")
    assert "FM-FER-001" in item.formula_codigo
    assert "FM-FER-002" in item.formula_codigo
    assert item.memoria


def test_ferias_6_avos_com_terco():
    entrada = _entrada_ferias(avos=6)

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is True

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    item = resultado.itens[0]

    assert item.valor.valor == Decimal("2400.00")


def test_ferias_sem_percentual_do_terco_deve_bloquear():
    entrada = _entrada_ferias(
        percentual_terco=None
    )

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is False

    assert any(
        item.codigo.endswith("-TERCO")
        for item in plano.validacao.erros
    )
