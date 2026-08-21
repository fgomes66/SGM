from __future__ import annotations

from .entrada_caso_trabalhista import EntradaCasoTrabalhista
from .item_plano_liquidacao import (
    ItemPlanoLiquidacao,
    StatusItemLiquidacao,
)
from .plano_liquidacao_judicial import PlanoLiquidacaoJudicial
from .validador_caso_trabalhista import ValidadorCasoTrabalhista


class MontadorPlanoLiquidacao:
    """Transforma a entrada validada em plano de cálculo."""

    @classmethod
    def montar(
        cls,
        entrada: EntradaCasoTrabalhista,
    ) -> PlanoLiquidacaoJudicial:
        validacao = ValidadorCasoTrabalhista.validar(
            entrada
        )

        itens: list[ItemPlanoLiquidacao] = []

        for verba in entrada.sentenca.verbas_deferidas:
            status = (
                StatusItemLiquidacao.APTO
                if validacao.valido
                else StatusItemLiquidacao.BLOQUEADO
            )

            itens.append(
                ItemPlanoLiquidacao(
                    codigo_verba=verba.codigo,
                    descricao=verba.descricao,
                    fundamento=verba.fundamento,
                    status=status,
                    observacoes=verba.observacoes,
                )
            )

        return PlanoLiquidacaoJudicial(
            referencia_processo=entrada.referencia_processo,
            entrada=entrada,
            validacao=validacao,
            itens=tuple(itens),
        )
