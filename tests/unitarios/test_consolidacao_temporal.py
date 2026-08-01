from dataclasses import FrozenInstanceError
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from sgm.dominio.financeiro import OrigemFinanceira, ValorMonetario
from sgm.dominio.jornada import Tempo
from sgm.dominio.trabalhista import (
    AdicionalHoraExtra,
    AliquotaFGTS,
    BaseDeCalculo,
    CodigoVerba,
    CompetenciaCalculo,
    ConfiguracaoIncidencia,
    ConsolidadorCompetencias,
    DivisorJornada,
    FatorAtualizacao,
    ModoLiquidacao,
    MotorCompetencia,
    ParametrosAvisoPrevio,
    ParametrosDSR,
    ParametrosDecimoTerceiro,
    ParametrosFerias,
    PlanoCompetencia,
    PlanoLiquidacaoIntegrada,
    RegraIncidencia,
    ResultadoConsolidado,
    TipoAdicionalHoraExtra,
    TipoAtualizacao,
    TipoAvisoPrevio,
    TipoBaseCalculo,
    TipoBaseIncidencia,
)


def dinheiro(texto: str, competencia: CompetenciaCalculo):
    return ValorMonetario.criar(
        texto,
        OrigemFinanceira(
            descricao="Salário da competência",
            documento_id=f"HOLERITE-{competencia.como_texto()}",
        ),
        momento=datetime(
            2026,
            8,
            1,
            2,
            0,
            tzinfo=timezone.utc,
        ),
    )


def configuracoes():
    itens = []
    for base in (
        TipoBaseIncidencia.FGTS,
        TipoBaseIncidencia.FERIAS,
        TipoBaseIncidencia.DECIMO_TERCEIRO,
        TipoBaseIncidencia.AVISO_PREVIO,
    ):
        for verba in (
            CodigoVerba.HORA_EXTRA,
            CodigoVerba.DSR,
        ):
            itens.append(
                ConfiguracaoIncidencia(
                    verba_origem=verba,
                    regra=RegraIncidencia(
                        base_destino=base,
                        incide=True,
                        fundamento="Inclusão expressa.",
                    ),
                )
            )
    return tuple(itens)


def resultado(
    competencia_texto: str,
    salario: str,
):
    competencia = CompetenciaCalculo.de_texto(
        competencia_texto
    )

    plano_integrado = PlanoLiquidacaoIntegrada(
        processo_referencia="CASO-0012",
        modo=ModoLiquidacao.LIQUIDACAO,
        base_remuneratoria=BaseDeCalculo(
            valor=dinheiro(salario, competencia),
            tipo=TipoBaseCalculo.SALARIO_CONTRATUAL,
            competencia=date(
                competencia.ano,
                competencia.mes,
                1,
            ),
            descricao="Salário contratual",
            origem_documental="Holerite",
        ),
        divisor_jornada=DivisorJornada(
            divisor=Decimal("220"),
            jornada_semanal_minutos=2640,
            fundamento="Divisor informado.",
        ),
        quantidade_horas_extras=Tempo.de_hhmm("05:00"),
        adicional_hora_extra=AdicionalHoraExtra(
            percentual=Decimal("0.50"),
            tipo=TipoAdicionalHoraExtra.LEGAL_50,
            fundamento="Adicional informado.",
        ),
        parametros_dsr=ParametrosDSR(
            dias_uteis=25,
            dias_repouso=5,
            fundamento="Calendário informado.",
        ),
        configuracoes_incidencia=configuracoes(),
        aliquota_fgts=AliquotaFGTS(
            percentual=Decimal("0.08"),
            fundamento="Alíquota informada.",
        ),
        parametros_ferias=ParametrosFerias(
            avos=6,
            percentual_terco=Decimal(
                "0.3333333333333333333333333333"
            ),
            fundamento="Férias informadas.",
        ),
        parametros_decimo_terceiro=ParametrosDecimoTerceiro(
            avos=6,
            fundamento="13º informado.",
        ),
        parametros_aviso_previo=ParametrosAvisoPrevio(
            tipo=TipoAvisoPrevio.INDENIZADO,
            dias=33,
            dias_mes_calculo=30,
            fundamento="Aviso informado.",
        ),
        fator_correcao=FatorAtualizacao(
            tipo=TipoAtualizacao.CORRECAO_MONETARIA,
            fator=Decimal("1.10"),
            data_inicial=date(2025, 1, 1),
            data_final=date(2025, 12, 31),
            fonte="Tabela de teste",
            fundamento="Correção informada.",
        ),
        fator_juros=FatorAtualizacao(
            tipo=TipoAtualizacao.JUROS_MORA,
            fator=Decimal("1.05"),
            data_inicial=date(2026, 1, 1),
            data_final=date(2026, 7, 31),
            fonte="Tabela de teste",
            fundamento="Juros informados.",
        ),
        lema_memoria="Cada competência deve ser auditável.",
    )

    plano = PlanoCompetencia(
        competencia=competencia,
        plano_liquidacao=plano_integrado,
        referencia=f"COMP-{competencia_texto}",
    )
    return MotorCompetencia.calcular(plano)


def consolidar(*resultados):
    return ConsolidadorCompetencias.consolidar(
        tuple(resultados),
        referencia="CASO-0012-C",
        lema="O total deve preservar cada competência.",
    )


def test_01_rejeita_lista_vazia():
    with pytest.raises(ValueError):
        ConsolidadorCompetencias.consolidar(
            (),
            referencia="CASO",
            lema="Lema.",
        )


def test_02_rejeita_referencia_vazia():
    with pytest.raises(ValueError):
        ConsolidadorCompetencias.consolidar(
            (resultado("2022-01", "3000.00"),),
            referencia=" ",
            lema="Lema.",
        )


def test_03_rejeita_lema_vazio():
    with pytest.raises(ValueError):
        ConsolidadorCompetencias.consolidar(
            (resultado("2022-01", "3000.00"),),
            referencia="CASO",
            lema=" ",
        )


def test_04_rejeita_competencia_duplicada():
    janeiro = resultado("2022-01", "3000.00")
    with pytest.raises(ValueError):
        consolidar(janeiro, janeiro)


def test_05_retorna_resultado_consolidado():
    item = consolidar(
        resultado("2022-01", "3000.00"),
        resultado("2022-02", "3000.00"),
    )
    assert isinstance(item, ResultadoConsolidado)


def test_06_ordena_resultados_cronologicamente():
    item = consolidar(
        resultado("2022-03", "3300.00"),
        resultado("2022-01", "3000.00"),
        resultado("2022-02", "3000.00"),
    )
    assert tuple(
        r.competencia.como_texto()
        for r in item.resultados
    ) == ("2022-01", "2022-02", "2022-03")


def test_07_periodo_consolidado():
    item = consolidar(
        resultado("2022-01", "3000.00"),
        resultado("2022-03", "3300.00"),
    )
    assert item.periodo.inicio.como_texto() == "2022-01"
    assert item.periodo.fim.como_texto() == "2022-03"


def test_08_quantidade_competencias():
    item = consolidar(
        resultado("2022-01", "3000.00"),
        resultado("2022-02", "3000.00"),
        resultado("2022-03", "3300.00"),
    )
    assert item.quantidade_competencias == 3


def test_09_subtotal_duas_competencias_iguais():
    item = consolidar(
        resultado("2022-01", "3000.00"),
        resultado("2022-02", "3000.00"),
    )
    assert item.subtotal_consolidado.valor == Decimal("821.40")


def test_10_valor_final_duas_competencias_iguais():
    item = consolidar(
        resultado("2022-01", "3000.00"),
        resultado("2022-02", "3000.00"),
    )
    assert item.valor_final_consolidado.valor == Decimal("948.72")


def test_11_salario_maior_afeta_consolidado():
    base = consolidar(
        resultado("2022-01", "3000.00"),
    )
    maior = consolidar(
        resultado("2022-01", "3300.00"),
    )
    assert maior.subtotal_consolidado.valor > base.subtotal_consolidado.valor
    assert maior.valor_final_consolidado.valor > base.valor_final_consolidado.valor


def test_12_memoria_identifica_periodo():
    texto = consolidar(
        resultado("2022-01", "3000.00"),
        resultado("2022-03", "3300.00"),
    ).memoria.como_texto()
    assert "Período: 2022-01 a 2022-03" in texto


def test_13_memoria_lista_competencias():
    texto = consolidar(
        resultado("2022-01", "3000.00"),
        resultado("2022-02", "3000.00"),
    ).memoria.como_texto()
    assert "Competência 2022-01" in texto
    assert "Competência 2022-02" in texto


def test_14_memoria_expoe_totais():
    texto = consolidar(
        resultado("2022-01", "3000.00"),
        resultado("2022-02", "3000.00"),
    ).memoria.como_texto()
    assert "Subtotal consolidado: BRL 821.40" in texto
    assert "Valor final consolidado: BRL 948.72" in texto


def test_15_memoria_preserva_referencias_mensais():
    texto = consolidar(
        resultado("2022-01", "3000.00"),
    ).memoria.como_texto()
    assert "Referência mensal: COMP-2022-01" in texto


def test_16_memoria_preserva_lema():
    texto = consolidar(
        resultado("2022-01", "3000.00"),
    ).memoria.como_texto()
    assert texto.endswith(
        "O total deve preservar cada competência."
    )


def test_17_resultados_originais_sao_preservados():
    janeiro = resultado("2022-01", "3000.00")
    item = consolidar(janeiro)
    assert item.resultados[0] is janeiro


def test_18_resultado_registra_versao():
    item = consolidar(
        resultado("2022-01", "3000.00"),
    )
    assert item.versao_motor == "0.9.1-C"


def test_19_resultado_e_imutavel():
    item = consolidar(
        resultado("2022-01", "3000.00"),
    )
    with pytest.raises(FrozenInstanceError):
        item.versao_motor = "OUTRA"


def test_20_execucoes_sao_reproduziveis():
    primeiro = consolidar(
        resultado("2022-01", "3000.00"),
        resultado("2022-02", "3000.00"),
    )
    segundo = consolidar(
        resultado("2022-01", "3000.00"),
        resultado("2022-02", "3000.00"),
    )
    assert primeiro.subtotal_consolidado.valor == segundo.subtotal_consolidado.valor
    assert primeiro.valor_final_consolidado.valor == segundo.valor_final_consolidado.valor
    assert primeiro.memoria.como_texto() == segundo.memoria.como_texto()
