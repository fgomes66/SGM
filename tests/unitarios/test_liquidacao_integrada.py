from dataclasses import FrozenInstanceError
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from sgm.dominio.financeiro import (
    OrigemFinanceira,
    TipoOperacaoFinanceira,
    ValorMonetario,
)
from sgm.dominio.jornada import Tempo
from sgm.dominio.trabalhista import (
    AdicionalHoraExtra,
    AliquotaFGTS,
    BaseDeCalculo,
    CodigoVerba,
    ConfiguracaoIncidencia,
    DivisorJornada,
    FatorAtualizacao,
    LiquidacaoTrabalhista,
    MemoriaCalculo,
    ModoLiquidacao,
    MotorLiquidacaoTrabalhista,
    ParametrosAvisoPrevio,
    ParametrosDSR,
    ParametrosDecimoTerceiro,
    ParametrosFerias,
    PlanoLiquidacaoIntegrada,
    RegraIncidencia,
    TipoAdicionalHoraExtra,
    TipoAtualizacao,
    TipoAvisoPrevio,
    TipoBaseCalculo,
    TipoBaseIncidencia,
    VerbaLiquidada,
)


def dinheiro(texto="3000.00"):
    return ValorMonetario.criar(
        texto,
        OrigemFinanceira(
            descricao="Salário contratual",
            documento_id="HOLERITE-001",
        ),
        momento=datetime(
            2026,
            8,
            1,
            0,
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
                        fundamento=(
                            f"Inclusão expressa de {verba.value} "
                            f"na base {base.value}."
                        ),
                        criterio_juridico_id=uuid4(),
                    ),
                )
            )
    return tuple(itens)


def plano(configs=None, lema="Cada valor deve ser explicável e auditável."):
    return PlanoLiquidacaoIntegrada(
        processo_referencia="CASO-0011",
        modo=ModoLiquidacao.LIQUIDACAO,
        base_remuneratoria=BaseDeCalculo(
            valor=dinheiro(),
            tipo=TipoBaseCalculo.SALARIO_CONTRATUAL,
            competencia=date(2026, 7, 1),
            descricao="Salário contratual",
            origem_documental="Holerite",
        ),
        divisor_jornada=DivisorJornada(
            divisor=Decimal("220"),
            jornada_semanal_minutos=2640,
            fundamento="Divisor informado no plano.",
        ),
        quantidade_horas_extras=Tempo.de_hhmm("05:00"),
        adicional_hora_extra=AdicionalHoraExtra(
            percentual=Decimal("0.50"),
            tipo=TipoAdicionalHoraExtra.LEGAL_50,
            fundamento="Adicional informado no plano.",
        ),
        parametros_dsr=ParametrosDSR(
            dias_uteis=25,
            dias_repouso=5,
            fundamento="Calendário informado no plano.",
        ),
        configuracoes_incidencia=(
            configuracoes() if configs is None else configs
        ),
        aliquota_fgts=AliquotaFGTS(
            percentual=Decimal("0.08"),
            fundamento="Alíquota informada no plano.",
        ),
        parametros_ferias=ParametrosFerias(
            avos=6,
            percentual_terco=Decimal(
                "0.3333333333333333333333333333"
            ),
            fundamento="Férias proporcionais informadas.",
        ),
        parametros_decimo_terceiro=ParametrosDecimoTerceiro(
            avos=6,
            fundamento="13º proporcional informado.",
        ),
        parametros_aviso_previo=ParametrosAvisoPrevio(
            tipo=TipoAvisoPrevio.INDENIZADO,
            dias=33,
            dias_mes_calculo=30,
            fundamento="Aviso informado no plano.",
        ),
        fator_correcao=FatorAtualizacao(
            tipo=TipoAtualizacao.CORRECAO_MONETARIA,
            fator=Decimal("1.10"),
            data_inicial=date(2025, 1, 1),
            data_final=date(2025, 12, 31),
            fonte="Tabela de teste",
            fundamento="Fator de correção informado.",
        ),
        fator_juros=FatorAtualizacao(
            tipo=TipoAtualizacao.JUROS_MORA,
            fator=Decimal("1.05"),
            data_inicial=date(2026, 1, 1),
            data_final=date(2026, 7, 31),
            fonte="Tabela de teste",
            fundamento="Fator de juros informado.",
        ),
        lema_memoria=lema,
    )


def liquidar(configs=None):
    return MotorLiquidacaoTrabalhista.calcular(
        plano(configs=configs)
    )


def test_01_modo_liquidacao_estavel():
    assert ModoLiquidacao.LIQUIDACAO.value == "LIQUIDACAO"


def test_02_configuracao_valida():
    item = configuracoes()[0]
    assert item.verba_origem == CodigoVerba.HORA_EXTRA


def test_03_configuracao_rejeita_verba_nao_suportada():
    with pytest.raises(ValueError):
        ConfiguracaoIncidencia(
            verba_origem=CodigoVerba.FGTS,
            regra=RegraIncidencia(
                base_destino=TipoBaseIncidencia.FERIAS,
                incide=True,
                fundamento="Critério.",
            ),
        )


def test_04_plano_rejeita_processo_vazio():
    item = plano()
    with pytest.raises(ValueError):
        PlanoLiquidacaoIntegrada(
            processo_referencia=" ",
            modo=item.modo,
            base_remuneratoria=item.base_remuneratoria,
            divisor_jornada=item.divisor_jornada,
            quantidade_horas_extras=item.quantidade_horas_extras,
            adicional_hora_extra=item.adicional_hora_extra,
            parametros_dsr=item.parametros_dsr,
            configuracoes_incidencia=item.configuracoes_incidencia,
            aliquota_fgts=item.aliquota_fgts,
            parametros_ferias=item.parametros_ferias,
            parametros_decimo_terceiro=item.parametros_decimo_terceiro,
            parametros_aviso_previo=item.parametros_aviso_previo,
            fator_correcao=item.fator_correcao,
            fator_juros=item.fator_juros,
            lema_memoria=item.lema_memoria,
        )


def test_05_plano_rejeita_lema_vazio():
    with pytest.raises(ValueError):
        plano(lema=" ")


def test_06_plano_e_imutavel():
    item = plano()
    with pytest.raises(FrozenInstanceError):
        item.processo_referencia = "OUTRO"


def test_07_motor_rejeita_configuracao_faltante():
    configs = configuracoes()[:-1]
    with pytest.raises(ValueError):
        liquidar(configs)


def test_08_motor_rejeita_configuracao_duplicada():
    configs = configuracoes()
    with pytest.raises(ValueError):
        liquidar(configs + (configs[0],))


def test_09_liquidacao_e_tipo_correto():
    assert isinstance(liquidar(), LiquidacaoTrabalhista)


def test_10_valor_hora_integrado():
    resultado = liquidar()
    assert resultado.valor_hora.valor.valor == (
        Decimal("3000.00") / Decimal("220")
    )


def test_11_horas_extras_integradas():
    assert liquidar().horas_extras.valor_total.valor == Decimal("102.27")


def test_12_dsr_integrado():
    assert liquidar().dsr.valor.valor == Decimal("20.45")


def test_13_base_fgts_integrada():
    assert liquidar().base_fgts.total.valor == Decimal("122.72")


def test_14_fgts_integrado():
    assert liquidar().fgts.valor.valor == Decimal("9.82")


def test_15_base_ferias_integrada():
    assert liquidar().base_ferias.total.valor == Decimal("122.72")


def test_16_ferias_integradas():
    resultado = liquidar().ferias
    assert resultado.valor_ferias.valor == Decimal("61.36")
    assert resultado.valor_terco.valor == Decimal("20.45")
    assert resultado.valor_total.valor == Decimal("81.81")


def test_17_decimo_terceiro_integrado():
    assert liquidar().decimo_terceiro.valor.valor == Decimal("61.36")


def test_18_aviso_previo_integrado():
    assert liquidar().aviso_previo.valor.valor == Decimal("134.99")


def test_19_liquidacao_possui_seis_verbas():
    assert len(liquidar().verbas) == 6


def test_20_ordem_das_verbas_e_estavel():
    assert tuple(item.codigo for item in liquidar().verbas) == (
        CodigoVerba.HORA_EXTRA,
        CodigoVerba.DSR,
        CodigoVerba.FGTS,
        CodigoVerba.FERIAS,
        CodigoVerba.DECIMO_TERCEIRO,
        CodigoVerba.AVISO_PREVIO,
    )


def test_21_subtotal_integrado():
    assert liquidar().subtotal.valor == Decimal("410.70")


def test_22_correcao_integrada():
    resultado = liquidar()
    assert (
        resultado.atualizacao.correcao.valor_atualizado.valor
        == Decimal("451.77")
    )


def test_23_juros_integrados():
    resultado = liquidar()
    assert (
        resultado.atualizacao.juros.valor_atualizado.valor
        == Decimal("474.36")
    )


def test_24_valor_final_integrado():
    assert liquidar().valor_final.valor == Decimal("474.36")


def test_25_versao_motor():
    assert liquidar().versao_motor == "0.9.0"


def test_26_verba_liquidada_valida():
    verba = liquidar().verbas[0]
    assert isinstance(verba, VerbaLiquidada)
    assert verba.formula_codigo == "FM-HE-001"


def test_27_memoria_e_tipo_correto():
    assert isinstance(liquidar().memoria, MemoriaCalculo)


def test_28_memoria_contem_todas_as_secoes():
    texto = liquidar().memoria.como_texto()
    for secao in (
        "1. VALOR DA HORA",
        "2. HORAS EXTRAS",
        "3. REFLEXO EM DSR",
        "4. FGTS",
        "5. FÉRIAS",
        "6. 13º SALÁRIO",
        "7. AVISO-PRÉVIO",
        "8. RESUMO DAS VERBAS",
        "9. ATUALIZAÇÃO E JUROS",
    ):
        assert secao in texto


def test_29_memoria_contem_processo_e_modo():
    texto = liquidar().memoria.como_texto()
    assert "Processo: CASO-0011" in texto
    assert "Modo: LIQUIDACAO" in texto


def test_30_memoria_contem_subtotal():
    assert "Subtotal: BRL 410.70" in liquidar().memoria.como_texto()


def test_31_memoria_contem_valor_final():
    assert "VALOR FINAL: BRL 474.36" in liquidar().memoria.como_texto()


def test_32_memoria_termina_com_lema():
    texto = liquidar().memoria.como_texto()
    assert texto.endswith(
        "Cada valor deve ser explicável e auditável."
    )


def test_33_memoria_preserva_formulas():
    texto = liquidar().memoria.como_texto()
    for formula in (
        "FM-VH-001",
        "FM-HE-001",
        "FM-DSR-001",
        "FM-FGTS-001",
        "FM-FER-001",
        "FM-13-001",
        "FM-AVP-001",
        "FM-AJ-001",
    ):
        assert formula in texto


def test_34_subtotal_registra_somas():
    tipos = [item.tipo for item in liquidar().subtotal.historico]
    assert TipoOperacaoFinanceira.SOMA in tipos


def test_35_subtotal_termina_com_arredondamento():
    assert (
        liquidar().subtotal.historico[-1].tipo
        == TipoOperacaoFinanceira.ARREDONDAMENTO
    )


def test_36_resultado_preserva_plano():
    item = plano()
    resultado = MotorLiquidacaoTrabalhista.calcular(item)
    assert resultado.plano is item


def test_37_resultado_e_imutavel():
    resultado = liquidar()
    with pytest.raises(FrozenInstanceError):
        resultado.versao_motor = "1.0.0"


def test_38_memoria_e_imutavel():
    memoria = liquidar().memoria
    with pytest.raises(FrozenInstanceError):
        memoria.titulo = "Outro"


def test_39_exclusao_dsr_fgts_altera_apenas_base_fgts():
    configs = list(configuracoes())
    for indice, item in enumerate(configs):
        if (
            item.verba_origem == CodigoVerba.DSR
            and item.regra.base_destino
            == TipoBaseIncidencia.FGTS
        ):
            configs[indice] = ConfiguracaoIncidencia(
                verba_origem=CodigoVerba.DSR,
                regra=RegraIncidencia(
                    base_destino=TipoBaseIncidencia.FGTS,
                    incide=False,
                    fundamento="Exclusão expressa para teste.",
                ),
            )
    resultado = liquidar(tuple(configs))
    assert resultado.base_fgts.total.valor == Decimal("102.27")
    assert resultado.fgts.valor.valor == Decimal("8.18")
    assert resultado.base_ferias.total.valor == Decimal("122.72")


def test_40_execucoes_repetidas_sao_reproduziveis():
    primeiro = liquidar()
    segundo = liquidar()
    assert primeiro.subtotal.valor == segundo.subtotal.valor
    assert primeiro.valor_final.valor == segundo.valor_final.valor
    assert (
        primeiro.memoria.como_texto()
        == segundo.memoria.como_texto()
    )
