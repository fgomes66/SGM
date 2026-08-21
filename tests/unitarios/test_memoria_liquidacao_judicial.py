from datetime import date
from decimal import Decimal

from sgm.dominio.trabalhista.atualizacao import (
    FatorAtualizacao,
    TipoAtualizacao,
)
from sgm.dominio.trabalhista.liquidacao_judicial import (
    AtualizadorLiquidacaoJudicial,
    ConsolidadorLiquidacaoJudicial,
    DadosContratoLiquidacao,
    EntradaCasoTrabalhista,
    GeradorMemoriaLiquidacaoJudicial,
    MontadorPlanoLiquidacao,
    OrquestradorLiquidacaoJudicial,
    ParametrosAtualizacaoJudicial,
    ParametrosLiquidacao,
    ParametrosVerbaJudicial,
    SentencaTrabalhista,
    VerbaDeferida,
)


def _entrada():
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
        referencia_processo="TESTE-MEMORIA-001",
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
        premissas=(
            "Teste automatizado de memória judicial.",
        ),
    )


def _resultado_atualizado():
    entrada = _entrada()

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    consolidado = ConsolidadorLiquidacaoJudicial.consolidar(
        resultado
    )

    correcao = FatorAtualizacao(
        tipo=TipoAtualizacao.CORRECAO_MONETARIA,
        fator=Decimal("1.10"),
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 6, 30),
        fonte="Fator artificial de teste",
        fundamento="Correção artificial para teste.",
        indice_codigo="TESTE-COR",
    )

    juros = FatorAtualizacao(
        tipo=TipoAtualizacao.JUROS_MORA,
        fator=Decimal("1.05"),
        data_inicial=date(2025, 7, 1),
        data_final=date(2025, 8, 1),
        fonte="Fator artificial de teste",
        fundamento="Juros artificiais para teste.",
        indice_codigo="TESTE-JUR",
    )

    atualizado = AtualizadorLiquidacaoJudicial.atualizar(
        consolidado,
        ParametrosAtualizacaoJudicial(
            fator_correcao=correcao,
            fator_juros=juros,
        ),
    )

    return entrada, atualizado


def test_memoria_judicial_tem_secoes_em_ordem():
    entrada, atualizado = _resultado_atualizado()

    memoria = GeradorMemoriaLiquidacaoJudicial.gerar(
        entrada,
        atualizado,
    )

    ordens = tuple(
        secao.ordem
        for secao in memoria.secoes
    )

    assert ordens == (1, 2, 3, 4, 5)


def test_tabela_de_verbas_fecha_com_subtotal():
    entrada, atualizado = _resultado_atualizado()

    memoria = GeradorMemoriaLiquidacaoJudicial.gerar(
        entrada,
        atualizado,
    )

    demonstrativo = memoria.secoes[2]
    tabela = demonstrativo.tabelas[0]

    assert tabela.total.valor == Decimal("11529.91")
    assert len(tabela.linhas) == 6


def test_memoria_contem_valor_final_e_formulas():
    entrada, atualizado = _resultado_atualizado()

    memoria = GeradorMemoriaLiquidacaoJudicial.gerar(
        entrada,
        atualizado,
    )

    texto = memoria.como_texto()

    assert "MEMÓRIA DE CÁLCULO JUDICIAL" in texto
    assert "11529.91" in texto
    assert "FM-AJ-001" in texto
    assert "FM-HE-001" in texto
    assert "FM-FGTS-001" in texto


def test_valor_final_atualizado_aparece_na_conclusao():
    entrada, atualizado = _resultado_atualizado()

    memoria = GeradorMemoriaLiquidacaoJudicial.gerar(
        entrada,
        atualizado,
    )

    conclusao = memoria.secoes[-1]

    assert any(
        atualizado.valor_final.valor
        == Decimal(item.valor.split()[-1])
        for item in conclusao.itens
        if item.rotulo == "Valor final da liquidação"
    )
