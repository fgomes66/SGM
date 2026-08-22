from datetime import date
from decimal import Decimal

from sgm.dominio.trabalhista.liquidacao_judicial.analisador_capacidade_judicial import (
    AnalisadorCapacidadeJudicial,
)
from sgm.dominio.trabalhista.liquidacao_judicial.diagnostico_capacidade_judicial import (
    CapacidadeVerbaJudicial,
)
from sgm.dominio.trabalhista.liquidacao_judicial import (
    DadosContratoLiquidacao,
    EntradaCasoTrabalhista,
    ParametrosLiquidacao,
    ParametrosVerbaJudicial,
    SentencaTrabalhista,
    VerbaDeferida,
)


def _caso_didatico_001():
    """
    Caso Didático de Homologação Judicial nº 001.

    Os dados abaixo reproduzem apenas comandos identificáveis
    no material didático. Dados não fornecidos pelo documento
    permanecem ausentes propositalmente.
    """

    verbas = (
        VerbaDeferida(
            codigo="EQUIPARACAO_SALARIAL",
            descricao="Diferenças decorrentes de equiparação salarial",
            fundamento=(
                "Equiparação entre as remunerações dos comparados, "
                "com apuração pelos contracheques."
            ),
            observacoes=(
                "Período reconhecido: setembro/1997 a abril/2001, "
                "observado o marco prescricional de 06/02/1998."
            ),
        ),

        VerbaDeferida(
            codigo="HORA_EXTRA",
            descricao="Horas extraordinárias",
            fundamento=(
                "Horas excedentes da 8ª diária, deferidas até abril/2001."
            ),
            parametros=ParametrosVerbaJudicial(
                percentual=Decimal("0.50"),
                divisor=Decimal("200"),
                fundamento=(
                    "Adicional de 50% e divisor 200 fixados na sentença."
                ),
                observacoes=(
                    "Jornada reconhecida: 09h00 às 20h45; "
                    "nos três primeiros e três últimos dias do mês, "
                    "até 22h45; intervalo intrajornada de uma hora."
                ),
            ),
        ),

        VerbaDeferida(
            codigo="DSR",
            descricao="Reflexo das horas extras em RSR",
            fundamento=(
                "Integração das horas extras quitadas e por quitar "
                "no repouso semanal remunerado."
            ),
            observacoes=(
                "O sábado foi considerado repouso semanal remunerado."
            ),
        ),

        VerbaDeferida(
            codigo="ADICIONAL_NOTURNO",
            descricao="Adicional noturno",
            fundamento=(
                "Adicional noturno deferido para o labor após as 22h."
            ),
            parametros=ParametrosVerbaJudicial(
                percentual=Decimal("0.20"),
                fundamento="Percentual de 20% fixado na sentença.",
            ),
        ),

        VerbaDeferida(
            codigo="MULTA_NORMATIVA",
            descricao="Multas normativas",
            fundamento=(
                "Multas previstas nas convenções coletivas "
                "do período imprescrito."
            ),
            observacoes=(
                "Valores indicados no material: "
                "set/98=9,68; set/99=10,21; "
                "set/00=10,95; set/01=11,55."
            ),
        ),

        VerbaDeferida(
            codigo="FERIAS",
            descricao="Reflexos em férias acrescidas de 1/3",
            fundamento=(
                "Reflexos determinados sobre as diferenças deferidas."
            ),
        ),

        VerbaDeferida(
            codigo="DECIMO_TERCEIRO",
            descricao="Reflexos em 13º salário",
            fundamento=(
                "Reflexos determinados sobre as diferenças deferidas."
            ),
        ),

        VerbaDeferida(
            codigo="FGTS",
            descricao="Depósitos de FGTS",
            fundamento=(
                "Reflexos e depósitos de FGTS determinados na sentença."
            ),
        ),

        VerbaDeferida(
            codigo="MULTA_FGTS_40",
            descricao="Indenização compensatória de 40% do FGTS",
            fundamento=(
                "Reflexo expressamente determinado na sentença."
            ),
            parametros=ParametrosVerbaJudicial(
                percentual=Decimal("0.40"),
                fundamento="Percentual de 40% indicado no título.",
            ),
        ),

        VerbaDeferida(
            codigo="VERBAS_RESILITORIAS",
            descricao="Reflexos em verbas resilitórias",
            fundamento=(
                "Reflexos determinados na sentença."
            ),
        ),
    )

    sentenca = SentencaTrabalhista(
        data_sentenca=date(2011, 6, 4),
        texto_dispositivo=(
            "Procedência parcial com condenação em horas extras "
            "e reflexos, RSR, adicional noturno, multa normativa "
            "e equiparação salarial com respectivos reflexos."
        ),
        verbas_deferidas=verbas,
        observacoes=(
            "Material didático. O próprio documento apresenta "
            "inconsistências de identificação entre cabeçalho e dispositivo."
        ),
    )

    contrato = DadosContratoLiquidacao(
        data_admissao=date(1984, 10, 2),
        data_desligamento=date(2002, 5, 29),

        # O material contém exemplos remuneratórios, mas não fornece
        # uma remuneração única válida para todo o período.
        # Utiliza-se aqui apenas um valor técnico mínimo para permitir
        # a construção do objeto, sem tratá-lo como base definitiva.
        salario_base=Decimal("1.00"),

        # O título trabalha com limite diário e divisor 200;
        # este campo não representa a jornada judicial definitiva.
        jornada_semanal=Decimal("40"),
    )

    parametros = ParametrosLiquidacao(
        data_calculo=date(2011, 6, 4),

        # O divisor 200 é expressamente fixado no título.
        divisor_horas=Decimal("200"),

        percentual_horas_extras=Decimal("0.50"),
    )

    return EntradaCasoTrabalhista(
        referencia_processo="CASO-DIDATICO-HOMOLOGACAO-001",
        contrato=contrato,
        sentenca=sentenca,
        parametros=parametros,
        premissas=(
            "Prescrição dos créditos anteriores a 06/02/1998.",
            (
                "Equiparação depende da evolução remuneratória "
                "da reclamante e do paradigma por competência."
            ),
            (
                "Base das horas extras: salário-base, anuênio "
                "e adicional de função."
            ),
            (
                "Jornada variável conforme posição dos dias no mês."
            ),
            (
                "Dedução obrigatória de parcelas já satisfeitas "
                "sob títulos idênticos."
            ),
            (
                "Fatores reais de correção monetária e juros "
                "não foram informados neste teste estrutural."
            ),
        ),
        documentos_referencia=(
            "Sentença didática - 9 páginas",
            "Contracheques citados na sentença - não disponíveis",
            "Convenções coletivas citadas - não disponíveis integralmente",
        ),
    )


def test_diagnostico_do_caso_didatico_001():
    entrada = _caso_didatico_001()

    diagnostico = AnalisadorCapacidadeJudicial.analisar(
        entrada
    )

    mapa = {
        item.codigo_verba: item.capacidade
        for item in diagnostico.verbas
    }

    # Motores ainda inexistentes.
    assert mapa["EQUIPARACAO_SALARIAL"] is (
        CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
    )
    assert mapa["ADICIONAL_NOTURNO"] is (
        CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
    )
    assert mapa["MULTA_NORMATIVA"] is (
        CapacidadeVerbaJudicial.NAO_SUPORTADO
    )
    assert mapa["MULTA_FGTS_40"] is (
        CapacidadeVerbaJudicial.NAO_SUPORTADO
    )
    assert mapa["VERBAS_RESILITORIAS"] is (
        CapacidadeVerbaJudicial.NAO_SUPORTADO
    )

    # Motores conhecidos, mas sem dados suficientes para este caso.
    assert mapa["HORA_EXTRA"] is (
        CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
    )
    assert mapa["DSR"] is (
        CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
    )
    assert mapa["FERIAS"] is (
        CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
    )
    assert mapa["DECIMO_TERCEIRO"] is (
        CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
    )
    assert mapa["FGTS"] is (
        CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
    )

    assert diagnostico.totalmente_executavel is False


def test_caso_didatico_registra_pendencias_documentais():
    entrada = _caso_didatico_001()

    assert any(
        "Contracheques" in documento
        for documento in entrada.documentos_referencia
    )

    assert any(
        "Convenções coletivas" in documento
        for documento in entrada.documentos_referencia
    )

    assert any(
        "Prescrição" in premissa
        for premissa in entrada.premissas
    )


def test_diagnostico_expoe_motivos_dos_bloqueios():
    entrada = _caso_didatico_001()

    diagnostico = AnalisadorCapacidadeJudicial.analisar(
        entrada
    )

    hora_extra = next(
        item
        for item in diagnostico.verbas
        if item.codigo_verba == "HORA_EXTRA"
    )

    assert hora_extra.motivos
    assert any(
        "quantidade" in motivo.lower()
        for motivo in hora_extra.motivos
    )


