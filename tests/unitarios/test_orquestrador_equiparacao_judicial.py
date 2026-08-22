from datetime import date
from decimal import Decimal

from sgm.dominio.financeiro import OrigemFinanceira, ValorMonetario
from sgm.dominio.trabalhista.equiparacao_salarial import (
    CompetenciaEquiparacao,
)
from sgm.dominio.trabalhista.liquidacao_judicial import (
    DadosContratoLiquidacao,
    EntradaCasoTrabalhista,
    MontadorPlanoLiquidacao,
    OrquestradorLiquidacaoJudicial,
    ParametrosLiquidacao,
    SentencaTrabalhista,
    VerbaDeferida,
)
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


def _valor(valor: str, documento: str):
    return ValorMonetario.criar(
        valor,
        OrigemFinanceira(
            descricao="Contracheque de equiparação.",
            documento_id=documento,
        ),
        moeda="BRL",
    )


def _entrada():
    outubro = CompetenciaEquiparacao(
        competencia=CompetenciaCalculo(1999, 10),
        remuneracao_reclamante=_valor(
            "2006.33",
            "reclamante-1999-10",
        ),
        remuneracao_paradigma=_valor(
            "2262.75",
            "paradigma-1999-10",
        ),
        origem_reclamante="Contracheque reclamante 10/1999",
        origem_paradigma="Contracheque paradigma 10/1999",
        fundamento="Equiparação salarial por remuneração.",
    )

    novembro = CompetenciaEquiparacao(
        competencia=CompetenciaCalculo(1999, 11),
        remuneracao_reclamante=_valor(
            "2100.00",
            "reclamante-1999-11",
        ),
        remuneracao_paradigma=_valor(
            "2300.00",
            "paradigma-1999-11",
        ),
        origem_reclamante="Contracheque reclamante 11/1999",
        origem_paradigma="Contracheque paradigma 11/1999",
        fundamento="Equiparação salarial por remuneração.",
    )

    verba = VerbaDeferida(
        codigo="EQUIPARACAO_SALARIAL",
        descricao="Diferenças de equiparação salarial",
        fundamento="Equiparação deferida.",
        competencias_equiparacao=(
            outubro,
            novembro,
        ),
    )

    return EntradaCasoTrabalhista(
        referencia_processo="TESTE-ORQUESTRADOR-EQ-001",
        contrato=DadosContratoLiquidacao(
            data_admissao=date(1998, 1, 1),
            data_desligamento=date(2001, 4, 30),
            salario_base=Decimal("2000.00"),
            jornada_semanal=Decimal("40"),
        ),
        sentenca=SentencaTrabalhista(
            data_sentenca=date(2011, 6, 4),
            texto_dispositivo="Equiparação salarial deferida.",
            verbas_deferidas=(verba,),
        ),
        parametros=ParametrosLiquidacao(
            data_calculo=date(2011, 6, 4),
            divisor_horas=Decimal("200"),
        ),
    )


def test_orquestrador_executa_equiparacao():
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

    assert item.codigo_verba == "EQUIPARACAO_SALARIAL"
    assert item.valor.moeda == "BRL"
    assert item.valor.valor == Decimal("456.42")
    assert item.formula_codigo == "FM-EQ-001"
    assert item.memoria


def test_memoria_equiparacao_contem_competencias():
    entrada = _entrada()

    plano = MontadorPlanoLiquidacao.montar(
        entrada
    )

    resultado = OrquestradorLiquidacaoJudicial.executar(
        plano
    )

    item = resultado.itens[0]

    assert any(
        "1999-10" in linha
        for linha in item.memoria
    )

    assert any(
        "1999-11" in linha
        for linha in item.memoria
    )

    assert any(
        "456.42" in linha
        for linha in item.memoria
    )
