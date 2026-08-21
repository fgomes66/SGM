from __future__ import annotations

from datetime import date
from decimal import Decimal

from sgm.dominio.jornada import Tempo

from sgm.dominio.financeiro import OrigemFinanceira, ValorMonetario
from sgm.dominio.trabalhista import (
    AdicionalHoraExtra,
    AliquotaFGTS,
    BaseDeCalculo,
    CodigoVerba,
    DivisorJornada,
    ParametrosDecimoTerceiro,
    ParametrosDSR,
    ParametrosAvisoPrevio,
    ParametrosFerias,
    ParcelaIncidencia,
    RegraIncidencia,
    ServicoComposicaoBase,
    ServicoDecimoTerceiro,
    ServicoFerias,
    ServicoFGTS,
    ServicoHoraExtra,
    ServicoReflexoDSR,
    ServicoValorHora,
    ServicoAvisoPrevio,
    TipoAdicionalHoraExtra,
    TipoAvisoPrevio,
    TipoBaseCalculo,
    TipoBaseIncidencia,
)

from .plano_liquidacao_judicial import PlanoLiquidacaoJudicial
from .resultado_item_liquidacao_judicial import (
    ResultadoItemLiquidacaoJudicial,
)
from .resultado_liquidacao_judicial import (
    ResultadoLiquidacaoJudicial,
)


class OrquestradorLiquidacaoJudicial:
    """
    Executa seletivamente somente as verbas deferidas e homologadas.

    A regra matemática permanece nos serviços de domínio já existentes.
    """

    @classmethod
    def executar(
        cls,
        plano: PlanoLiquidacaoJudicial,
    ) -> ResultadoLiquidacaoJudicial:
        if not isinstance(plano, PlanoLiquidacaoJudicial):
            raise TypeError(
                "O plano deve ser um PlanoLiquidacaoJudicial."
            )

        if not plano.apto_para_execucao:
            raise ValueError(
                "O plano judicial não está apto para execução."
            )

        resultados: list[ResultadoItemLiquidacaoJudicial] = []
        memoria: list[str] = [
            f"Processo: {plano.referencia_processo}",
            "Liquidação judicial seletiva",
            "",
        ]

        for verba in plano.entrada.sentenca.verbas_deferidas:
            if verba.codigo == "DECIMO_TERCEIRO":
                resultado = cls._executar_decimo_terceiro(
                    plano,
                    verba,
                )
            elif verba.codigo == "FERIAS":
                resultado = cls._executar_ferias(
                    plano,
                    verba,
                )
            elif verba.codigo == "FGTS":
                resultado = cls._executar_fgts(
                    plano,
                    verba,
                )
            elif verba.codigo == "HORA_EXTRA":
                resultado = cls._executar_hora_extra(
                    plano,
                    verba,
                )
            elif verba.codigo == "DSR":
                resultado = cls._executar_dsr(
                    plano,
                    verba,
                )
            elif verba.codigo == "AVISO_PREVIO":
                resultado = cls._executar_aviso_previo(
                    plano,
                    verba,
                )
            else:
                raise NotImplementedError(
                    "A verba "
                    f"{verba.codigo} ainda não foi liberada "
                    "no orquestrador judicial."
                )

            resultados.append(resultado)

            memoria.extend(
                (
                    f"VERBA: {resultado.descricao}",
                    *resultado.memoria,
                    "",
                )
            )

        return ResultadoLiquidacaoJudicial(
            referencia_processo=plano.referencia_processo,
            itens=tuple(resultados),
            memoria=tuple(memoria),
        )

    @staticmethod
    def _criar_hora_extra_apurada(
        plano: PlanoLiquidacaoJudicial,
        verba,
    ):
        parametros = verba.parametros

        percentual = (
            parametros.percentual
            if parametros.percentual is not None
            else plano.entrada.parametros.percentual_horas_extras
        )

        quantidade = (
            parametros.quantidade
            if parametros.quantidade is not None
            else verba.quantidade
        )

        divisor = (
            parametros.divisor
            if parametros.divisor is not None
            else plano.entrada.parametros.divisor_horas
        )

        if percentual is None:
            raise ValueError(
                "Horas extras exigem percentual definido."
            )

        if quantidade is None:
            raise ValueError(
                "Horas extras exigem quantidade definida."
            )

        if divisor is None:
            raise ValueError(
                "Horas extras exigem divisor definido."
            )

        fundamento = (
            parametros.fundamento
            or verba.fundamento
        )

        if not fundamento:
            raise ValueError(
                "Horas extras exigem fundamento registrado."
            )

        jornada = plano.entrada.contrato.jornada_semanal

        if jornada is None:
            raise ValueError(
                "Horas extras exigem jornada semanal informada."
            )

        salario = ValorMonetario.criar(
            str(plano.entrada.contrato.salario_base),
            OrigemFinanceira(
                descricao="Salário-base do caso judicial.",
                documento_id=plano.referencia_processo,
            ),
            moeda=plano.entrada.parametros.moeda,
        )

        base = BaseDeCalculo(
            valor=salario,
            tipo=TipoBaseCalculo.SALARIO_CONTRATUAL,
            competencia=plano.entrada.parametros.data_calculo,
            descricao="Salário contratual para cálculo da hora",
            origem_documental=plano.referencia_processo,
        )

        divisor_obj = DivisorJornada(
            divisor=divisor,
            jornada_semanal_minutos=int(
                jornada * Decimal("60")
            ),
            fundamento=fundamento,
            descricao="Divisor definido no caso judicial",
        )

        valor_hora = ServicoValorHora.calcular(
            base,
            divisor_obj,
        )

        adicional = AdicionalHoraExtra(
            percentual=percentual,
            tipo=TipoAdicionalHoraExtra.JUDICIAL,
            fundamento=fundamento,
            descricao="Adicional de hora extra judicial",
        )

        quantidade_tempo = Tempo(
            int(quantidade * Decimal("60"))
        )

        return ServicoHoraExtra.calcular(
            valor_hora,
            quantidade_tempo,
            adicional,
        )

    @classmethod
    def _executar_hora_extra(
        cls,
        plano: PlanoLiquidacaoJudicial,
        verba,
    ) -> ResultadoItemLiquidacaoJudicial:
        apurado = cls._criar_hora_extra_apurada(
            plano,
            verba,
        )

        return ResultadoItemLiquidacaoJudicial(
            codigo_verba=verba.codigo,
            descricao=verba.descricao,
            valor=apurado.valor_total,
            memoria=apurado.memoria_resumida(),
            formula_codigo=apurado.formula_codigo,
        )

    @classmethod
    def _executar_dsr(
        cls,
        plano: PlanoLiquidacaoJudicial,
        verba,
    ) -> ResultadoItemLiquidacaoJudicial:
        parametros_dsr = verba.parametros

        if parametros_dsr.dias_uteis is None:
            raise ValueError(
                "DSR exige dias úteis definidos."
            )

        if parametros_dsr.dias_repouso is None:
            raise ValueError(
                "DSR exige dias de repouso definidos."
            )

        fundamento = (
            parametros_dsr.fundamento
            or verba.fundamento
        )

        if not fundamento:
            raise ValueError(
                "DSR exige fundamento registrado."
            )

        verba_he = next(
            (
                item
                for item in plano.entrada.sentenca.verbas_deferidas
                if item.codigo == "HORA_EXTRA"
            ),
            None,
        )

        if verba_he is None:
            raise ValueError(
                "DSR exige verba HORA_EXTRA no mesmo título judicial."
            )

        horas_extras = cls._criar_hora_extra_apurada(
            plano,
            verba_he,
        )

        parametros = ParametrosDSR(
            dias_uteis=parametros_dsr.dias_uteis,
            dias_repouso=parametros_dsr.dias_repouso,
            fundamento=fundamento,
            observacao=(
                parametros_dsr.observacoes or None
            ),
        )

        apurado = ServicoReflexoDSR.calcular(
            horas_extras,
            parametros,
        )

        return ResultadoItemLiquidacaoJudicial(
            codigo_verba=verba.codigo,
            descricao=verba.descricao,
            valor=apurado.valor,
            memoria=apurado.memoria_resumida(),
            formula_codigo=apurado.formula_codigo,
        )
    @staticmethod
    def _executar_aviso_previo(
        plano: PlanoLiquidacaoJudicial,
        verba,
    ) -> ResultadoItemLiquidacaoJudicial:
        """
        Executa aviso-prévio deferido judicialmente.

        A matemática permanece delegada ao ServicoAvisoPrevio.
        """
        parametros_judiciais = verba.parametros

        if parametros_judiciais.dias_aviso is None:
            raise ValueError(
                "Aviso-prévio exige quantidade de dias definida."
            )

        if parametros_judiciais.dias_mes_calculo is None:
            raise ValueError(
                "Aviso-prévio exige dias do mês de cálculo."
            )

        fundamento = (
            parametros_judiciais.fundamento
            or verba.fundamento
        )

        if not fundamento:
            raise ValueError(
                "Aviso-prévio exige fundamento registrado."
            )

        salario = ValorMonetario.criar(
            str(plano.entrada.contrato.salario_base),
            OrigemFinanceira(
                descricao="Salário-base do caso judicial.",
                documento_id=plano.referencia_processo,
            ),
            moeda=plano.entrada.parametros.moeda,
        )

        regra = RegraIncidencia(
            base_destino=TipoBaseIncidencia.AVISO_PREVIO,
            incide=True,
            fundamento=(
                "Salário-base integrante da base do aviso-prévio "
                "conforme parâmetros do caso judicial."
            ),
        )

        parcela = ParcelaIncidencia(
            verba=CodigoVerba.SALARIO,
            valor=salario,
            regra=regra,
            descricao="Salário-base do caso judicial",
            documento_id=plano.referencia_processo,
        )

        base = ServicoComposicaoBase.compor(
            TipoBaseIncidencia.AVISO_PREVIO,
            (parcela,),
        )

        parametros = ParametrosAvisoPrevio(
            tipo=TipoAvisoPrevio.INDENIZADO,
            dias=parametros_judiciais.dias_aviso,
            dias_mes_calculo=(
                parametros_judiciais.dias_mes_calculo
            ),
            fundamento=fundamento,
            observacao=(
                parametros_judiciais.observacoes or None
            ),
        )

        apurado = ServicoAvisoPrevio.calcular(
            base,
            parametros,
        )

        return ResultadoItemLiquidacaoJudicial(
            codigo_verba=verba.codigo,
            descricao=verba.descricao,
            valor=apurado.valor,
            memoria=apurado.memoria_resumida(),
            formula_codigo=apurado.formula_codigo,
        )
    @staticmethod
    def _executar_fgts(
        plano: PlanoLiquidacaoJudicial,
        verba,
    ) -> ResultadoItemLiquidacaoJudicial:
        """
        Executa FGTS deferido judicialmente.

        A matemática permanece delegada ao ServicoFGTS.
        """

        parametros_judiciais = verba.parametros

        percentual = (
            parametros_judiciais.percentual
            if parametros_judiciais.percentual is not None
            else verba.percentual
        )

        if percentual is None:
            raise ValueError(
                "FGTS exige alíquota definida."
            )

        fundamento = (
            parametros_judiciais.fundamento
            or verba.fundamento
        )

        if not fundamento:
            raise ValueError(
                "FGTS exige fundamento registrado."
            )

        salario = ValorMonetario.criar(
            str(plano.entrada.contrato.salario_base),
            OrigemFinanceira(
                descricao=(
                    "Salário-base informado no caso judicial."
                ),
                documento_id=plano.referencia_processo,
            ),
            moeda=plano.entrada.parametros.moeda,
        )

        regra = RegraIncidencia(
            base_destino=TipoBaseIncidencia.FGTS,
            incide=True,
            fundamento=(
                "Salário-base integrante da base do FGTS "
                "conforme parâmetros do caso judicial."
            ),
        )

        parcela = ParcelaIncidencia(
            verba=CodigoVerba.SALARIO,
            valor=salario,
            regra=regra,
            descricao="Salário-base do caso judicial",
            documento_id=plano.referencia_processo,
        )

        base = ServicoComposicaoBase.compor(
            TipoBaseIncidencia.FGTS,
            (parcela,),
        )

        aliquota = AliquotaFGTS(
            percentual=percentual,
            fundamento=fundamento,
            descricao="Alíquota definida no título judicial",
        )

        apurado = ServicoFGTS.calcular(
            base,
            aliquota,
        )

        return ResultadoItemLiquidacaoJudicial(
            codigo_verba=verba.codigo,
            descricao=verba.descricao,
            valor=apurado.valor,
            memoria=apurado.memoria_resumida(),
            formula_codigo=apurado.formula_codigo,
        )
    @staticmethod
    def _executar_ferias(
        plano: PlanoLiquidacaoJudicial,
        verba,
    ) -> ResultadoItemLiquidacaoJudicial:
        """
        Executa férias deferidas judicialmente.

        A matemática permanece delegada ao ServicoFerias.
        O orquestrador apenas converte os parâmetros do título judicial
        para os objetos de domínio já homologados.
        """
        parametros_judiciais = verba.parametros

        if parametros_judiciais.avos is None:
            raise ValueError(
                "Férias exigem avos definidos."
            )

        fundamento = (
            parametros_judiciais.fundamento
            or verba.fundamento
        )

        if not fundamento:
            raise ValueError(
                "Férias exigem fundamento registrado."
            )

        percentual_terco = (
            parametros_judiciais.percentual
            if parametros_judiciais.percentual is not None
            else Decimal("0.3333333333333333333333333333")
        )

        salario = ValorMonetario.criar(
            str(plano.entrada.contrato.salario_base),
            OrigemFinanceira(
                descricao=(
                    "Salário-base informado no caso judicial."
                ),
                documento_id=plano.referencia_processo,
            ),
            moeda=plano.entrada.parametros.moeda,
        )

        regra = RegraIncidencia(
            base_destino=TipoBaseIncidencia.FERIAS,
            incide=True,
            fundamento=(
                "Salário-base integrante da base de férias "
                "conforme parâmetros do caso judicial."
            ),
        )

        parcela = ParcelaIncidencia(
            verba=CodigoVerba.SALARIO,
            valor=salario,
            regra=regra,
            descricao="Salário-base do caso judicial",
            documento_id=plano.referencia_processo,
        )

        base = ServicoComposicaoBase.compor(
            TipoBaseIncidencia.FERIAS,
            (parcela,),
        )

        parametros = ParametrosFerias(
            avos=parametros_judiciais.avos,
            percentual_terco=percentual_terco,
            fundamento=fundamento,
            observacao=(
                parametros_judiciais.observacoes or None
            ),
        )

        apurado = ServicoFerias.calcular(
            base,
            parametros,
        )

        return ResultadoItemLiquidacaoJudicial(
            codigo_verba=verba.codigo,
            descricao=verba.descricao,
            valor=apurado.valor_total,
            memoria=apurado.memoria_resumida(),
            formula_codigo=(
                f"{apurado.formula_ferias_codigo}+"
                f"{apurado.formula_terco_codigo}"
            ),
        )
    @staticmethod
    def _executar_decimo_terceiro(
        plano: PlanoLiquidacaoJudicial,
        verba,
    ) -> ResultadoItemLiquidacaoJudicial:
        parametros_judiciais = verba.parametros

        if parametros_judiciais.avos is None:
            raise ValueError(
                "O 13º salário exige avos definidos."
            )

        fundamento = (
            parametros_judiciais.fundamento
            or verba.fundamento
        )

        if not fundamento:
            raise ValueError(
                "O 13º salário exige fundamento registrado."
            )

        salario = ValorMonetario.criar(
            str(plano.entrada.contrato.salario_base),
            OrigemFinanceira(
                descricao=(
                    "Salário-base informado no caso judicial."
                ),
                documento_id=plano.referencia_processo,
            ),
            moeda=plano.entrada.parametros.moeda,
        )

        regra = RegraIncidencia(
            base_destino=TipoBaseIncidencia.DECIMO_TERCEIRO,
            incide=True,
            fundamento=(
                "Salário-base integrante da base do 13º salário "
                "conforme parâmetros do caso judicial."
            ),
        )

        parcela = ParcelaIncidencia(
            verba=CodigoVerba.SALARIO,
            valor=salario,
            regra=regra,
            descricao="Salário-base do caso judicial",
            documento_id=plano.referencia_processo,
        )

        base = ServicoComposicaoBase.compor(
            TipoBaseIncidencia.DECIMO_TERCEIRO,
            (parcela,),
        )

        parametros = ParametrosDecimoTerceiro(
            avos=parametros_judiciais.avos,
            fundamento=fundamento,
            observacao=(
                parametros_judiciais.observacoes or None
            ),
        )

        apurado = ServicoDecimoTerceiro.calcular(
            base,
            parametros,
        )

        return ResultadoItemLiquidacaoJudicial(
            codigo_verba=verba.codigo,
            descricao=verba.descricao,
            valor=apurado.valor,
            memoria=apurado.memoria_resumida(),
            formula_codigo=apurado.formula_codigo,
        )




