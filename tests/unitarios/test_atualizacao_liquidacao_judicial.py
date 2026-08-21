from datetime import date
from decimal import Decimal

from sgm.dominio.financeiro import OrigemFinanceira, ValorMonetario
from sgm.dominio.trabalhista.atualizacao import (
    FatorAtualizacao,
    TipoAtualizacao,
)
from sgm.dominio.trabalhista.liquidacao_judicial import (
    AtualizadorLiquidacaoJudicial,
    ParametrosAtualizacaoJudicial,
    ResultadoConsolidadoJudicial,
    ResultadoItemLiquidacaoJudicial,
    ResultadoLiquidacaoJudicial,
)


def _consolidado_dez_mil():
    origem = OrigemFinanceira(
        descricao="Valor artificial para teste judicial.",
        documento_id="TESTE-ATUALIZACAO-001",
    )

    valor = ValorMonetario.criar(
        "10000.00",
        origem,
        moeda="BRL",
    )

    item = ResultadoItemLiquidacaoJudicial(
        codigo_verba="TESTE",
        descricao="Verba artificial de teste",
        valor=valor,
        memoria=("Valor artificial para teste.",),
        formula_codigo="FM-TESTE-001",
    )

    resultado = ResultadoLiquidacaoJudicial(
        referencia_processo="TESTE-ATUALIZACAO-001",
        itens=(item,),
        memoria=("Resultado artificial.",),
    )

    return ResultadoConsolidadoJudicial(
        referencia_processo="TESTE-ATUALIZACAO-001",
        resultado_origem=resultado,
        subtotal=valor,
        memoria=("Subtotal artificial.",),
    )


def _parametros():
    correcao = FatorAtualizacao(
        tipo=TipoAtualizacao.CORRECAO_MONETARIA,
        fator=Decimal("1.10"),
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 6, 30),
        fonte="Fator artificial de teste",
        fundamento="Teste automatizado da correção monetária.",
        indice_codigo="TESTE-COR",
    )

    juros = FatorAtualizacao(
        tipo=TipoAtualizacao.JUROS_MORA,
        fator=Decimal("1.05"),
        data_inicial=date(2025, 7, 1),
        data_final=date(2025, 8, 1),
        fonte="Fator artificial de teste",
        fundamento="Teste automatizado dos juros.",
        indice_codigo="TESTE-JUR",
    )

    return ParametrosAtualizacaoJudicial(
        fator_correcao=correcao,
        fator_juros=juros,
        observacoes=(
            "Fatores artificiais utilizados apenas para teste."
        ),
    )


def test_atualizacao_judicial_controlada():
    consolidado = _consolidado_dez_mil()

    resultado = AtualizadorLiquidacaoJudicial.atualizar(
        consolidado,
        _parametros(),
    )

    assert resultado.atualizacao.correcao.valor_original.valor == Decimal(
        "10000.00"
    )

    assert resultado.atualizacao.correcao.valor_atualizado.valor == Decimal(
        "11000.00"
    )

    assert resultado.atualizacao.juros.valor_atualizado.valor == Decimal(
        "11550.00"
    )

    assert resultado.valor_final.valor == Decimal("11550.00")
    assert resultado.valor_final.moeda == "BRL"
    assert resultado.atualizacao.formula_codigo == "FM-AJ-001"
    assert resultado.memoria


def test_atualizacao_preserva_consolidado():
    consolidado = _consolidado_dez_mil()

    resultado = AtualizadorLiquidacaoJudicial.atualizar(
        consolidado,
        _parametros(),
    )

    assert resultado.consolidado is consolidado
    assert resultado.consolidado.subtotal.valor == Decimal("10000.00")


def test_memoria_contem_valor_final():
    consolidado = _consolidado_dez_mil()

    resultado = AtualizadorLiquidacaoJudicial.atualizar(
        consolidado,
        _parametros(),
    )

    assert any(
        "VALOR FINAL" in linha
        for linha in resultado.memoria
    )
