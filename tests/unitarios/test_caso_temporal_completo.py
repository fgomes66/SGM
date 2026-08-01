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
    EventoContratualAplicavel,
    FatorAtualizacao,
    ModoLiquidacao,
    MotorCasoTemporal,
    ParametrosAvisoPrevio,
    ParametrosDSR,
    ParametrosDecimoTerceiro,
    ParametrosFerias,
    PeriodoContratual,
    PlanoCasoTemporal,
    PlanoLiquidacaoIntegrada,
    RegraIncidencia,
    ResultadoCasoTemporal,
    TipoAdicionalHoraExtra,
    TipoAtualizacao,
    TipoAvisoPrevio,
    TipoBaseCalculo,
    TipoBaseIncidencia,
    TipoEventoContratual,
)


def comp(texto: str) -> CompetenciaCalculo:
    return CompetenciaCalculo.de_texto(texto)


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
            4,
            0,
            tzinfo=timezone.utc,
        ),
    )

    return PlanoLiquidacaoIntegrada(
        processo_referencia="CASO-0013",
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
        lema_memoria="Cada etapa temporal deve ser explicável.",
    )


def evento(texto, tipo, **kwargs):
    return EventoContratualAplicavel(
        competencia=comp(texto),
        tipo=tipo,
        descricao=f"Evento {tipo.value}",
        fundamento="Evento contratual informado.",
        **kwargs,
    )


def plano_caso():
    eventos = (
        evento(
            "2022-03",
            TipoEventoContratual.REAJUSTE,
            novo_salario=Decimal("3300.00"),
        ),
        evento(
            "2022-04",
            TipoEventoContratual.AFASTAMENTO,
        ),
        evento(
            "2022-05",
            TipoEventoContratual.RETORNO,
        ),
        evento(
            "2022-06",
            TipoEventoContratual.ALTERACAO_DIVISOR,
            novo_divisor=Decimal("200"),
        ),
        evento(
            "2022-07",
            TipoEventoContratual.PROMOCAO,
            novo_salario=Decimal("4000.00"),
        ),
        evento(
            "2022-08",
            TipoEventoContratual.RESCISAO,
        ),
    )
    return PlanoCasoTemporal(
        referencia="CASO-0013",
        periodo=PeriodoContratual(
            comp("2022-01"),
            comp("2022-09"),
        ),
        plano_modelo=plano_modelo(),
        eventos=eventos,
        lema="Cada etapa temporal deve ser explicável.",
    )


def calcular():
    return MotorCasoTemporal.calcular(plano_caso())


def test_01_plano_valido():
    assert plano_caso().referencia == "CASO-0013"


def test_02_plano_rejeita_referencia_vazia():
    item = plano_caso()
    with pytest.raises(ValueError):
        PlanoCasoTemporal(
            referencia=" ",
            periodo=item.periodo,
            plano_modelo=item.plano_modelo,
            eventos=item.eventos,
            lema=item.lema,
        )


def test_03_plano_rejeita_lema_vazio():
    item = plano_caso()
    with pytest.raises(ValueError):
        PlanoCasoTemporal(
            referencia=item.referencia,
            periodo=item.periodo,
            plano_modelo=item.plano_modelo,
            eventos=item.eventos,
            lema=" ",
        )


def test_04_resultado_tipo_correto():
    assert isinstance(calcular(), ResultadoCasoTemporal)


def test_05_linha_possui_nove_estados():
    assert len(calcular().linha_aplicada.estados) == 9


def test_06_janeiro_preserva_salario_inicial():
    estado = calcular().linha_aplicada.estado_da_competencia(
        "2022-01"
    )
    assert estado.salario == Decimal("3000.00")


def test_07_fevereiro_nao_sofre_reajuste_retroativo():
    estado = calcular().linha_aplicada.estado_da_competencia(
        "2022-02"
    )
    assert estado.salario == Decimal("3000.00")


def test_08_marco_recebe_reajuste():
    estado = calcular().linha_aplicada.estado_da_competencia(
        "2022-03"
    )
    assert estado.salario == Decimal("3300.00")


def test_09_abril_afastado_nao_gera_resultado():
    resultado = calcular()
    assert "2022-04" in resultado.linha_aplicada.competencias_inativas
    assert all(
        item.competencia != comp("2022-04")
        for item in resultado.resultados_mensais
    )


def test_10_maio_retorna_e_gera_resultado():
    resultado = calcular()
    assert any(
        item.competencia == comp("2022-05")
        for item in resultado.resultados_mensais
    )


def test_11_junho_recebe_novo_divisor():
    estado = calcular().linha_aplicada.estado_da_competencia(
        "2022-06"
    )
    assert estado.divisor == Decimal("200")


def test_12_julho_recebe_promocao():
    estado = calcular().linha_aplicada.estado_da_competencia(
        "2022-07"
    )
    assert estado.salario == Decimal("4000.00")


def test_13_agosto_rescindido_nao_gera_resultado():
    resultado = calcular()
    estado = resultado.linha_aplicada.estado_da_competencia(
        "2022-08"
    )
    assert estado.rescindido is True
    assert all(
        item.competencia != comp("2022-08")
        for item in resultado.resultados_mensais
    )


def test_14_setembro_permanece_inativo():
    resultado = calcular()
    estado = resultado.linha_aplicada.estado_da_competencia(
        "2022-09"
    )
    assert estado.ativo is False
    assert all(
        item.competencia != comp("2022-09")
        for item in resultado.resultados_mensais
    )


def test_15_seis_competencias_calculadas():
    assert len(calcular().resultados_mensais) == 6


def test_16_ordem_dos_resultados():
    assert tuple(
        item.competencia.como_texto()
        for item in calcular().resultados_mensais
    ) == (
        "2022-01",
        "2022-02",
        "2022-03",
        "2022-05",
        "2022-06",
        "2022-07",
    )


def test_17_resultado_marco_superior_a_fevereiro():
    resultados = {
        item.competencia.como_texto(): item
        for item in calcular().resultados_mensais
    }
    assert (
        resultados["2022-03"].subtotal.valor
        > resultados["2022-02"].subtotal.valor
    )


def test_18_resultado_junho_reflete_divisor_menor():
    resultados = {
        item.competencia.como_texto(): item
        for item in calcular().resultados_mensais
    }
    assert (
        resultados["2022-06"].subtotal.valor
        > resultados["2022-05"].subtotal.valor
    )


def test_19_resultado_julho_reflete_promocao():
    resultados = {
        item.competencia.como_texto(): item
        for item in calcular().resultados_mensais
    }
    assert (
        resultados["2022-07"].subtotal.valor
        > resultados["2022-06"].subtotal.valor
    )


def test_20_consolidado_preserva_resultados():
    resultado = calcular()
    assert (
        resultado.consolidado.resultados
        == resultado.resultados_mensais
    )


def test_21_memoria_identifica_linha_do_tempo():
    texto = calcular().memoria.como_texto()
    assert "LINHA DO TEMPO CONTRATUAL" in texto
    assert "2022-03 | salário=3300.00" in texto


def test_22_memoria_identifica_inativos():
    texto = calcular().memoria.como_texto()
    assert "Competências inativas: 3" in texto


def test_23_memoria_lista_resultados_mensais():
    texto = calcular().memoria.como_texto()
    assert "Competência 2022-01" in texto
    assert "Competência 2022-07" in texto
    assert "Competência 2022-04" not in texto


def test_24_memoria_expoe_consolidado():
    texto = calcular().memoria.como_texto()
    assert "Subtotal consolidado:" in texto
    assert "Valor final consolidado:" in texto


def test_25_resultado_e_imutavel():
    resultado = calcular()
    with pytest.raises(FrozenInstanceError):
        resultado.versao_motor = "OUTRA"


def test_26_execucao_reproduzivel():
    primeiro = calcular()
    segundo = calcular()
    assert (
        primeiro.consolidado.subtotal_consolidado.valor
        == segundo.consolidado.subtotal_consolidado.valor
    )
    assert (
        primeiro.consolidado.valor_final_consolidado.valor
        == segundo.consolidado.valor_final_consolidado.valor
    )
    assert (
        primeiro.memoria.como_texto()
        == segundo.memoria.como_texto()
    )
