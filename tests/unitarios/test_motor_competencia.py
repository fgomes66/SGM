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
    ResultadoCompetencia,
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
            1,
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


def plano_competencia(
    competencia_texto: str = "2022-01",
    salario: str = "3000.00",
) -> PlanoCompetencia:
    competencia = CompetenciaCalculo.de_texto(
        competencia_texto
    )

    plano = PlanoLiquidacaoIntegrada(
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

    return PlanoCompetencia(
        competencia=competencia,
        plano_liquidacao=plano,
        referencia=f"COMP-{competencia.como_texto()}",
    )


def test_01_plano_valido():
    item = plano_competencia()
    assert item.competencia.como_texto() == "2022-01"


def test_02_plano_rejeita_referencia_vazia():
    item = plano_competencia()
    with pytest.raises(ValueError):
        PlanoCompetencia(
            competencia=item.competencia,
            plano_liquidacao=item.plano_liquidacao,
            referencia=" ",
        )


def test_03_plano_rejeita_competencia_divergente():
    item = plano_competencia()
    with pytest.raises(ValueError):
        PlanoCompetencia(
            competencia=CompetenciaCalculo.de_texto("2022-02"),
            plano_liquidacao=item.plano_liquidacao,
            referencia="COMP-2022-02",
        )


def test_04_plano_e_imutavel():
    item = plano_competencia()
    with pytest.raises(FrozenInstanceError):
        item.referencia = "OUTRA"


def test_05_motor_retorna_resultado_competencia():
    resultado = MotorCompetencia.calcular(
        plano_competencia()
    )
    assert isinstance(resultado, ResultadoCompetencia)


def test_06_resultado_preserva_competencia():
    resultado = MotorCompetencia.calcular(
        plano_competencia("2022-03")
    )
    assert resultado.competencia.como_texto() == "2022-03"


def test_07_resultado_preserva_plano():
    item = plano_competencia()
    resultado = MotorCompetencia.calcular(item)
    assert resultado.plano is item


def test_08_resultado_reutiliza_motor_integrado():
    resultado = MotorCompetencia.calcular(
        plano_competencia()
    )
    assert resultado.liquidacao.versao_motor == "0.9.0"


def test_09_subtotal_da_competencia():
    resultado = MotorCompetencia.calcular(
        plano_competencia()
    )
    assert resultado.subtotal.valor == Decimal("410.70")


def test_10_valor_final_da_competencia():
    resultado = MotorCompetencia.calcular(
        plano_competencia()
    )
    assert resultado.valor_final.valor == Decimal("474.36")


def test_11_memoria_identifica_competencia():
    resultado = MotorCompetencia.calcular(
        plano_competencia("2022-04")
    )
    assert "Competência: 2022-04" in resultado.memoria.como_texto()


def test_12_memoria_identifica_referencia():
    resultado = MotorCompetencia.calcular(
        plano_competencia()
    )
    assert "Referência: COMP-2022-01" in resultado.memoria.como_texto()


def test_13_memoria_preserva_secoes_da_liquidacao():
    texto = MotorCompetencia.calcular(
        plano_competencia()
    ).memoria.como_texto()
    assert "1. VALOR DA HORA" in texto
    assert "9. ATUALIZAÇÃO E JUROS" in texto


def test_14_memoria_preserva_lema():
    texto = MotorCompetencia.calcular(
        plano_competencia()
    ).memoria.como_texto()
    assert texto.endswith(
        "Cada competência deve ser auditável."
    )


def test_15_salario_maior_altera_resultado():
    primeiro = MotorCompetencia.calcular(
        plano_competencia("2022-01", "3000.00")
    )
    segundo = MotorCompetencia.calcular(
        plano_competencia("2022-02", "3300.00")
    )
    assert segundo.subtotal.valor > primeiro.subtotal.valor
    assert segundo.valor_final.valor > primeiro.valor_final.valor


def test_16_competencias_sao_isoladas():
    janeiro = MotorCompetencia.calcular(
        plano_competencia("2022-01", "3000.00")
    )
    marco = MotorCompetencia.calcular(
        plano_competencia("2022-03", "3300.00")
    )
    assert janeiro.plano.plano_liquidacao.base_remuneratoria.valor.valor == Decimal("3000.00")
    assert marco.plano.plano_liquidacao.base_remuneratoria.valor.valor == Decimal("3300.00")


def test_17_execucoes_iguais_sao_reproduziveis():
    primeiro = MotorCompetencia.calcular(
        plano_competencia()
    )
    segundo = MotorCompetencia.calcular(
        plano_competencia()
    )
    assert primeiro.subtotal.valor == segundo.subtotal.valor
    assert primeiro.valor_final.valor == segundo.valor_final.valor
    assert primeiro.memoria.como_texto() == segundo.memoria.como_texto()


def test_18_resultado_registra_versao():
    resultado = MotorCompetencia.calcular(
        plano_competencia()
    )
    assert resultado.versao_motor == "0.9.1-B"


def test_19_resultado_e_imutavel():
    resultado = MotorCompetencia.calcular(
        plano_competencia()
    )
    with pytest.raises(FrozenInstanceError):
        resultado.versao_motor = "OUTRA"


def test_20_resultado_financeiro_preserva_moeda():
    resultado = MotorCompetencia.calcular(
        plano_competencia()
    )
    assert resultado.subtotal.moeda == "BRL"
    assert resultado.valor_final.moeda == "BRL"
