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


def _entrada_fgts(
    percentual: Decimal | None = Decimal("0.08"),
):
    verba = VerbaDeferida(
        codigo="FGTS",
        descricao="FGTS",
        fundamento="FGTS deferido em sentença.",
        parametros=ParametrosVerbaJudicial(
            percentual=percentual,
            fundamento="Alíquota de FGTS definida no título judicial.",
        ),
    )

    return EntradaCasoTrabalhista(
        referencia_processo="TESTE-JUDICIAL-FGTS-001",
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
                "Defere-se o recolhimento do FGTS."
            ),
            verbas_deferidas=(verba,),
        ),
        parametros=ParametrosLiquidacao(
            data_calculo=date(2025, 8, 1),
            divisor_horas=Decimal("220"),
        ),
    )


def test_fgts_8_por_cento():
    entrada = _entrada_fgts()

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is True

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    assert resultado.quantidade_itens == 1

    item = resultado.itens[0]

    assert item.codigo_verba == "FGTS"
    assert item.valor.moeda == "BRL"
    assert item.valor.valor == Decimal("288.00")
    assert item.formula_codigo == "FM-FGTS-001"
    assert item.memoria


def test_fgts_sem_aliquota_deve_bloquear():
    entrada = _entrada_fgts(
        percentual=None
    )

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is False

    assert any(
        item.codigo.endswith("-ALIQUOTA")
        for item in plano.validacao.erros
    )
