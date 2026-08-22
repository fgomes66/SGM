from datetime import date
from decimal import Decimal

from sgm.dominio.trabalhista.liquidacao_judicial import (
    DadosContratoLiquidacao,
    EntradaCasoTrabalhista,
    ParametrosLiquidacao,
    ParametrosVerbaJudicial,
    SentencaTrabalhista,
    VerbaDeferida,
)

from sgm.dominio.trabalhista.liquidacao_judicial.analisador_capacidade_judicial import (
    AnalisadorCapacidadeJudicial,
)

from sgm.dominio.trabalhista.liquidacao_judicial.diagnostico_capacidade_judicial import (
    CapacidadeVerbaJudicial,
)


def _entrada(*verbas):
    return EntradaCasoTrabalhista(
        referencia_processo="TESTE-DIAGNOSTICO-001",
        contrato=DadosContratoLiquidacao(
            data_admissao=date(2024, 1, 2),
            data_desligamento=date(2025, 5, 31),
            salario_base=Decimal("3300.00"),
            jornada_semanal=Decimal("44"),
        ),
        sentenca=SentencaTrabalhista(
            data_sentenca=date(2025, 6, 10),
            texto_dispositivo="Teste de diagnóstico judicial.",
            verbas_deferidas=tuple(verbas),
        ),
        parametros=ParametrosLiquidacao(
            data_calculo=date(2025, 8, 1),
            divisor_horas=Decimal("220"),
            percentual_horas_extras=Decimal("0.50"),
        ),
    )


def test_verba_conhecida_completa_deve_ser_executavel():
    entrada = _entrada(
        VerbaDeferida(
            codigo="DECIMO_TERCEIRO",
            descricao="13º salário",
            fundamento="Deferido.",
            parametros=ParametrosVerbaJudicial(
                avos=12,
                fundamento="12/12 avos.",
            ),
        )
    )

    diagnostico = AnalisadorCapacidadeJudicial.analisar(
        entrada
    )

    assert len(diagnostico.executaveis) == 1
    assert (
        diagnostico.executaveis[0].capacidade
        is CapacidadeVerbaJudicial.EXECUTAVEL
    )


def test_verba_conhecida_sem_dado_deve_bloquear():
    entrada = _entrada(
        VerbaDeferida(
            codigo="DECIMO_TERCEIRO",
            descricao="13º salário",
            fundamento="Deferido.",
        )
    )

    diagnostico = AnalisadorCapacidadeJudicial.analisar(
        entrada
    )

    assert len(diagnostico.bloqueadas_por_dados) == 1

    item = diagnostico.bloqueadas_por_dados[0]

    assert (
        item.capacidade
        is CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
    )

    assert any(
        "avos" in motivo.lower()
        for motivo in item.motivos
    )


def test_verba_desconhecida_deve_ser_nao_suportada():
    entrada = _entrada(
        VerbaDeferida(
            codigo="ADICIONAL_NOTURNO",
            descricao="Adicional noturno",
            fundamento="Deferido.",
            parametros=ParametrosVerbaJudicial(
                percentual=Decimal("0.20"),
                fundamento="Adicional de 20%.",
            ),
        )
    )

    diagnostico = AnalisadorCapacidadeJudicial.analisar(
        entrada
    )

    assert len(diagnostico.nao_suportadas) == 1

    item = diagnostico.nao_suportadas[0]

    assert item.codigo_verba == "ADICIONAL_NOTURNO"
    assert (
        item.capacidade
        is CapacidadeVerbaJudicial.NAO_SUPORTADO
    )


def test_diagnostico_misto():
    entrada = _entrada(
        VerbaDeferida(
            codigo="FGTS",
            descricao="FGTS",
            fundamento="Deferido.",
            parametros=ParametrosVerbaJudicial(
                percentual=Decimal("0.08"),
                fundamento="Alíquota de 8%.",
            ),
        ),
        VerbaDeferida(
            codigo="FERIAS",
            descricao="Férias",
            fundamento="Deferidas.",
            parametros=ParametrosVerbaJudicial(
                avos=12,
            ),
        ),
        VerbaDeferida(
            codigo="EQUIPARACAO_SALARIAL",
            descricao="Equiparação salarial",
            fundamento="Deferida.",
        ),
    )

    diagnostico = AnalisadorCapacidadeJudicial.analisar(
        entrada
    )

    assert len(diagnostico.executaveis) == 1
    assert len(diagnostico.bloqueadas_por_dados) == 1
    assert len(diagnostico.nao_suportadas) == 1

    assert diagnostico.executaveis[0].codigo_verba == "FGTS"
    assert (
        diagnostico.bloqueadas_por_dados[0].codigo_verba
        == "FERIAS"
    )
    assert (
        diagnostico.nao_suportadas[0].codigo_verba
        == "EQUIPARACAO_SALARIAL"
    )

    assert diagnostico.totalmente_executavel is False
