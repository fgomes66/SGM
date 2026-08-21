from datetime import date
from decimal import Decimal

from sgm.dominio.trabalhista.liquidacao_judicial import (
    ConsolidadorLiquidacaoJudicial,
    DadosContratoLiquidacao,
    EntradaCasoTrabalhista,
    MontadorPlanoLiquidacao,
    OrquestradorLiquidacaoJudicial,
    ParametrosLiquidacao,
    ParametrosVerbaJudicial,
    SentencaTrabalhista,
    VerbaDeferida,
)


def _entrada_completa():
    verbas = (
        VerbaDeferida(
            codigo="DECIMO_TERCEIRO",
            descricao="13º salário",
            fundamento="Deferido em sentença.",
            parametros=ParametrosVerbaJudicial(
                avos=12,
                fundamento="13º integral.",
            ),
        ),
        VerbaDeferida(
            codigo="FERIAS",
            descricao="Férias acrescidas do terço constitucional",
            fundamento="Deferidas em sentença.",
            parametros=ParametrosVerbaJudicial(
                avos=12,
                percentual=Decimal(
                    "0.3333333333333333333333333333"
                ),
                fundamento="Férias integrais + 1/3.",
            ),
        ),
        VerbaDeferida(
            codigo="FGTS",
            descricao="FGTS",
            fundamento="FGTS deferido.",
            parametros=ParametrosVerbaJudicial(
                percentual=Decimal("0.08"),
                fundamento="Alíquota de 8%.",
            ),
        ),
        VerbaDeferida(
            codigo="HORA_EXTRA",
            descricao="Horas extras",
            fundamento="Horas extras deferidas.",
            parametros=ParametrosVerbaJudicial(
                quantidade=Decimal("10"),
                percentual=Decimal("0.50"),
                divisor=Decimal("220"),
                fundamento="10 horas extras com adicional de 50%.",
            ),
        ),
        VerbaDeferida(
            codigo="DSR",
            descricao="Reflexo das horas extras em DSR",
            fundamento="DSR deferido.",
            parametros=ParametrosVerbaJudicial(
                dias_uteis=22,
                dias_repouso=4,
                fundamento="Reflexo das horas extras em DSR.",
            ),
        ),
        VerbaDeferida(
            codigo="AVISO_PREVIO",
            descricao="Aviso-prévio indenizado",
            fundamento="Aviso-prévio deferido.",
            parametros=ParametrosVerbaJudicial(
                dias_aviso=30,
                dias_mes_calculo=30,
                fundamento="Aviso-prévio indenizado de 30 dias.",
            ),
        ),
    )

    return EntradaCasoTrabalhista(
        referencia_processo="TESTE-CONSOLIDACAO-001",
        contrato=DadosContratoLiquidacao(
            data_admissao=date(2024, 1, 2),
            data_desligamento=date(2025, 5, 31),
            salario_base=Decimal("3300.00"),
            jornada_semanal=Decimal("44"),
        ),
        sentenca=SentencaTrabalhista(
            data_sentenca=date(2025, 6, 10),
            data_transito_julgado=date(2025, 7, 15),
            texto_dispositivo=(
                "Defere-se o pagamento das verbas descritas."
            ),
            verbas_deferidas=verbas,
        ),
        parametros=ParametrosLiquidacao(
            data_calculo=date(2025, 8, 1),
            divisor_horas=Decimal("220"),
            percentual_horas_extras=Decimal("0.50"),
        ),
    )


def test_consolidacao_completa():
    entrada = _entrada_completa()

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    assert plano.apto_para_execucao is True

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    consolidado = ConsolidadorLiquidacaoJudicial.consolidar(
        resultado
    )

    assert resultado.quantidade_itens == 6
    assert consolidado.quantidade_itens == 6
    assert consolidado.subtotal.moeda == "BRL"
    assert consolidado.subtotal.valor == Decimal("11529.91")
    assert consolidado.memoria
    assert any(
        "Subtotal judicial" in linha
        for linha in consolidado.memoria
    )


def test_consolidacao_preserva_referencia():
    entrada = _entrada_completa()

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    consolidado = ConsolidadorLiquidacaoJudicial.consolidar(
        resultado
    )

    assert (
        consolidado.referencia_processo
        == "TESTE-CONSOLIDACAO-001"
    )


def test_historico_financeiro_da_soma_e_preservado():
    entrada = _entrada_completa()

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    consolidado = ConsolidadorLiquidacaoJudicial.consolidar(
        resultado
    )

    assert consolidado.subtotal.historico
    assert consolidado.subtotal.versao > 1
