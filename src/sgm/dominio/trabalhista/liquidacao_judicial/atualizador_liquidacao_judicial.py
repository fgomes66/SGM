from __future__ import annotations

from sgm.dominio.trabalhista.atualizacao import (
    ServicoAtualizacao,
)

from .parametros_atualizacao_judicial import (
    ParametrosAtualizacaoJudicial,
)
from .resultado_atualizado_judicial import (
    ResultadoAtualizadoJudicial,
)
from .resultado_consolidado_judicial import (
    ResultadoConsolidadoJudicial,
)


class AtualizadorLiquidacaoJudicial:
    """Aplica correção monetária e juros ao subtotal judicial consolidado."""

    VERSAO = "0.9.7-JA"

    @classmethod
    def atualizar(
        cls,
        consolidado: ResultadoConsolidadoJudicial,
        parametros: ParametrosAtualizacaoJudicial,
    ) -> ResultadoAtualizadoJudicial:
        atualizacao = ServicoAtualizacao.aplicar_correcao_e_juros(
            consolidado.subtotal,
            parametros.fator_correcao,
            parametros.fator_juros,
        )

        linhas = [
            f"Referência: {consolidado.referencia_processo}",
            f"Motor de atualização judicial: {cls.VERSAO}",
            (
                "Subtotal antes da atualização: "
                f"{consolidado.subtotal.moeda} "
                f"{format(consolidado.subtotal.valor, 'f')}"
            ),
            "",
            *atualizacao.memoria_resumida(),
        ]

        if parametros.observacoes:
            linhas.extend(
                (
                    "",
                    f"Observações: {parametros.observacoes}",
                )
            )

        return ResultadoAtualizadoJudicial(
            consolidado=consolidado,
            atualizacao=atualizacao,
            valor_final=atualizacao.valor_final,
            memoria=tuple(linhas),
            versao_motor=cls.VERSAO,
        )
