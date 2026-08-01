from dataclasses import FrozenInstanceError
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from sgm.dominio.financeiro import OrigemFinanceira, ValorMonetario
from sgm.dominio.jornada import Tempo
from sgm.dominio.trabalhista import (
    AdicionalHoraExtra,
    AliquotaFGTS,
    AplicadorEventosContratuais,
    BaseDeCalculo,
    CodigoVerba,
    CompetenciaCalculo,
    ConfiguracaoIncidencia,
    DivisorJornada,
    EstadoContratual,
    EventoContratualAplicavel,
    FatorAtualizacao,
    ModoLiquidacao,
    ParametrosAvisoPrevio,
    ParametrosDSR,
    ParametrosDecimoTerceiro,
    ParametrosFerias,
    PeriodoContratual,
    PlanoLiquidacaoIntegrada,
    RegraIncidencia,
    TipoAdicionalHoraExtra,
    TipoAtualizacao,
    TipoAvisoPrevio,
    TipoBaseCalculo,
    TipoBaseIncidencia,
    TipoEventoContratual,
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


def plano_modelo():
    valor = ValorMonetario.criar(
        "3000.00",
        OrigemFinanceira(
            descricao="Salário inicial",
            documento_id="CONTRATO-001",
        ),
        momento=datetime(
            2026,
            8,
            1,
            3,
            0,
            tzinfo=timezone.utc,
        ),
    )
    return PlanoLiquidacaoIntegrada(
        processo_referencia="CASO-0012-D",
        modo=ModoLiquidacao.LIQUIDACAO,
        base_remuneratoria=BaseDeCalculo(
            valor=valor,
            tipo=TipoBaseCalculo.SALARIO_CONTRATUAL,
            competencia=date(2022, 1, 1),
            descricao="Salário contratual",
            origem_documental="Contrato",
        ),
        divisor_jornada=DivisorJornada(
            divisor=Decimal("220"),
            jornada_semanal_minutos=2640,
            fundamento="Divisor inicial.",
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
        lema_memoria="Cada evento deve ser rastreável.",
    )


def comp(texto):
    return CompetenciaCalculo.de_texto(texto)


def evento(texto, tipo, **kwargs):
    return EventoContratualAplicavel(
        competencia=comp(texto),
        tipo=tipo,
        descricao=f"Evento {tipo.value}",
        fundamento="Evento informado.",
        **kwargs,
    )


def aplicar(*eventos):
    return AplicadorEventosContratuais.aplicar(
        PeriodoContratual(comp("2022-01"), comp("2022-06")),
        plano_modelo(),
        tuple(eventos),
        referencia="CASO-0012-D",
    )


def test_01_reajuste_exige_decimal():
    with pytest.raises(TypeError):
        evento(
            "2022-03",
            TipoEventoContratual.REAJUSTE,
            novo_salario=3300.00,
        )


def test_02_reajuste_rejeita_salario_zero():
    with pytest.raises(ValueError):
        evento(
            "2022-03",
            TipoEventoContratual.REAJUSTE,
            novo_salario=Decimal("0"),
        )


def test_03_alteracao_divisor_exige_decimal():
    with pytest.raises(TypeError):
        evento(
            "2022-03",
            TipoEventoContratual.ALTERACAO_DIVISOR,
            novo_divisor=200,
        )


def test_04_alteracao_jornada_rejeita_zero():
    with pytest.raises(ValueError):
        evento(
            "2022-03",
            TipoEventoContratual.ALTERACAO_JORNADA,
            nova_jornada_semanal_minutos=0,
        )


def test_05_linha_sem_eventos_preserva_estado():
    resultado = aplicar()
    assert len(resultado.estados) == 6
    assert len(resultado.planos_ativos) == 6
    assert resultado.estado_da_competencia(
        "2022-06"
    ).salario == Decimal("3000.00")


def test_06_reajuste_aplica_na_competencia():
    resultado = aplicar(
        evento(
            "2022-03",
            TipoEventoContratual.REAJUSTE,
            novo_salario=Decimal("3300.00"),
        )
    )
    assert resultado.estado_da_competencia(
        "2022-02"
    ).salario == Decimal("3000.00")
    assert resultado.estado_da_competencia(
        "2022-03"
    ).salario == Decimal("3300.00")


def test_07_reajuste_propaga_para_competencias_seguintes():
    resultado = aplicar(
        evento(
            "2022-03",
            TipoEventoContratual.REAJUSTE,
            novo_salario=Decimal("3300.00"),
        )
    )
    assert resultado.estado_da_competencia(
        "2022-06"
    ).salario == Decimal("3300.00")


def test_08_promocao_altera_salario():
    resultado = aplicar(
        evento(
            "2022-04",
            TipoEventoContratual.PROMOCAO,
            novo_salario=Decimal("4000.00"),
        )
    )
    assert resultado.estado_da_competencia(
        "2022-04"
    ).salario == Decimal("4000.00")


def test_09_alteracao_divisor_propaga():
    resultado = aplicar(
        evento(
            "2022-02",
            TipoEventoContratual.ALTERACAO_DIVISOR,
            novo_divisor=Decimal("200"),
        )
    )
    assert resultado.estado_da_competencia(
        "2022-06"
    ).divisor == Decimal("200")


def test_10_alteracao_jornada_propaga():
    resultado = aplicar(
        evento(
            "2022-02",
            TipoEventoContratual.ALTERACAO_JORNADA,
            nova_jornada_semanal_minutos=2400,
        )
    )
    assert resultado.estado_da_competencia(
        "2022-06"
    ).jornada_semanal_minutos == 2400


def test_11_afastamento_torna_competencia_inativa():
    resultado = aplicar(
        evento(
            "2022-03",
            TipoEventoContratual.AFASTAMENTO,
        )
    )
    assert resultado.estado_da_competencia(
        "2022-03"
    ).ativo is False
    assert "2022-03" in resultado.competencias_inativas


def test_12_retorno_reativa_competencia():
    resultado = aplicar(
        evento("2022-03", TipoEventoContratual.AFASTAMENTO),
        evento("2022-05", TipoEventoContratual.RETORNO),
    )
    assert resultado.estado_da_competencia(
        "2022-04"
    ).ativo is False
    assert resultado.estado_da_competencia(
        "2022-05"
    ).ativo is True


def test_13_planos_sao_gerados_apenas_para_ativos():
    resultado = aplicar(
        evento("2022-03", TipoEventoContratual.AFASTAMENTO),
        evento("2022-05", TipoEventoContratual.RETORNO),
    )
    assert len(resultado.planos_ativos) == 4
    assert resultado.competencias_inativas == (
        "2022-03",
        "2022-04",
    )


def test_14_rescisao_inativa_competencias_restantes():
    resultado = aplicar(
        evento("2022-04", TipoEventoContratual.RESCISAO),
    )
    assert resultado.estado_da_competencia(
        "2022-04"
    ).rescindido is True
    assert resultado.estado_da_competencia(
        "2022-06"
    ).ativo is False


def test_15_rejeita_evento_apos_rescisao():
    with pytest.raises(ValueError):
        aplicar(
            evento("2022-04", TipoEventoContratual.RESCISAO),
            evento(
                "2022-05",
                TipoEventoContratual.REAJUSTE,
                novo_salario=Decimal("3500.00"),
            ),
        )


def test_16_rejeita_evento_fora_do_periodo():
    with pytest.raises(ValueError):
        aplicar(
            evento(
                "2021-12",
                TipoEventoContratual.REAJUSTE,
                novo_salario=Decimal("3300.00"),
            )
        )


def test_17_plano_gerado_reflete_salario():
    resultado = aplicar(
        evento(
            "2022-03",
            TipoEventoContratual.REAJUSTE,
            novo_salario=Decimal("3300.00"),
        )
    )
    plano_marco = next(
        p for p in resultado.planos_ativos
        if p.competencia == comp("2022-03")
    )
    assert (
        plano_marco.plano_liquidacao
        .base_remuneratoria.valor.valor
        == Decimal("3300.00")
    )


def test_18_plano_gerado_reflete_divisor_e_jornada():
    resultado = aplicar(
        evento(
            "2022-03",
            TipoEventoContratual.ALTERACAO_DIVISOR,
            novo_divisor=Decimal("200"),
        ),
        evento(
            "2022-03",
            TipoEventoContratual.ALTERACAO_JORNADA,
            nova_jornada_semanal_minutos=2400,
        ),
    )
    plano_marco = next(
        p for p in resultado.planos_ativos
        if p.competencia == comp("2022-03")
    )
    divisor = plano_marco.plano_liquidacao.divisor_jornada
    assert divisor.divisor == Decimal("200")
    assert divisor.jornada_semanal_minutos == 2400


def test_19_estado_e_imutavel():
    resultado = aplicar()
    estado = resultado.estados[0]
    assert isinstance(estado, EstadoContratual)
    with pytest.raises(FrozenInstanceError):
        estado.ativo = False


def test_20_execucoes_sao_reproduziveis():
    eventos = (
        evento(
            "2022-03",
            TipoEventoContratual.REAJUSTE,
            novo_salario=Decimal("3300.00"),
        ),
    )
    primeiro = aplicar(*eventos)
    segundo = aplicar(*eventos)
    assert primeiro.estados == segundo.estados
    assert tuple(
        p.plano_liquidacao.base_remuneratoria.valor.valor
        for p in primeiro.planos_ativos
    ) == tuple(
        p.plano_liquidacao.base_remuneratoria.valor.valor
        for p in segundo.planos_ativos
    )
