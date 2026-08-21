from __future__ import annotations

from decimal import Decimal

from sgm.dominio.financeiro import OrigemFinanceira, ValorMonetario
from sgm.dominio.trabalhista import (
    CodigoVerba,
    ParametrosDecimoTerceiro,
    ParametrosFerias,
    ParcelaIncidencia,
    RegraIncidencia,
    ServicoComposicaoBase,
    ServicoDecimoTerceiro,
    ServicoFerias,
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

