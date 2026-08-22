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


def _entrada(verba):
    return EntradaCasoTrabalhista(
        referencia_processo="TESTE-DIAGNOSTICO-AN-001",
        contrato=DadosContratoLiquidacao(
            data_admissao=date(2024, 1, 1),
            data_desligamento=date(2025, 1, 31),
            salario_base=Decimal("2000.00"),
            jornada_semanal=Decimal("40"),
        ),
        sentenca=SentencaTrabalhista(
            data_sentenca=date(2025, 2, 1),
            texto_dispositivo="Adicional noturno deferido.",
            verbas_deferidas=(verba,),
        ),
        parametros=ParametrosLiquidacao(
            data_calculo=date(2025, 3, 1),
            divisor_horas=Decimal("200"),
        ),
    )


def test_adicional_noturno_sem_percentual_e_quantidade_bloqueia():
    verba = VerbaDeferida(
        codigo="ADICIONAL_NOTURNO",
        descricao="Adicional noturno",
        fundamento="Deferido.",
    )

    diagnostico = AnalisadorCapacidadeJudicial.analisar(
        _entrada(verba)
    )

    item = diagnostico.verbas[0]

    assert (
        item.capacidade
        is CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
    )

    assert any(
        "percentual" in motivo.lower()
        for motivo in item.motivos
    )

    assert any(
        "quantidade" in motivo.lower()
        for motivo in item.motivos
    )


def test_adicional_noturno_sem_quantidade_bloqueia():
    verba = VerbaDeferida(
        codigo="ADICIONAL_NOTURNO",
        descricao="Adicional noturno",
        fundamento="Deferido.",
        parametros=ParametrosVerbaJudicial(
            percentual=Decimal("0.20"),
            fundamento="Adicional de 20%.",
        ),
    )

    diagnostico = AnalisadorCapacidadeJudicial.analisar(
        _entrada(verba)
    )

    item = diagnostico.verbas[0]

    assert (
        item.capacidade
        is CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
    )

    assert len(item.motivos) == 1

    assert "quantidade" in item.motivos[0].lower()


def test_adicional_noturno_com_percentual_e_quantidade_executavel():
    verba = VerbaDeferida(
        codigo="ADICIONAL_NOTURNO",
        descricao="Adicional noturno",
        fundamento="Deferido.",
        parametros=ParametrosVerbaJudicial(
            percentual=Decimal("0.20"),
            quantidade=Decimal("5"),
            fundamento="Adicional de 20% sobre 5 horas.",
        ),
    )

    diagnostico = AnalisadorCapacidadeJudicial.analisar(
        _entrada(verba)
    )

    item = diagnostico.verbas[0]

    assert (
        item.capacidade
        is CapacidadeVerbaJudicial.EXECUTAVEL
    )

    assert diagnostico.totalmente_executavel is True
