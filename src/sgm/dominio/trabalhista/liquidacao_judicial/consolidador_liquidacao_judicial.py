from __future__ import annotations

from .resultado_consolidado_judicial import (
    ResultadoConsolidadoJudicial,
)
from .resultado_liquidacao_judicial import (
    ResultadoLiquidacaoJudicial,
)


class ConsolidadorLiquidacaoJudicial:
    """
    Consolida resultados já calculados pelo orquestrador judicial.

    Não executa fórmulas trabalhistas.
    Apenas soma resultados monetários homologados e produz memória.
    """

    VERSAO = "0.9.7-JC"

    @classmethod
    def consolidar(
        cls,
        resultado: ResultadoLiquidacaoJudicial,
    ) -> ResultadoConsolidadoJudicial:
        if not resultado.itens:
            raise ValueError(
                "A consolidação exige ao menos um item calculado."
            )

        moedas = {
            item.valor.moeda
            for item in resultado.itens
        }

        if len(moedas) != 1:
            raise ValueError(
                "Todas as verbas devem usar a mesma moeda."
            )

        subtotal = resultado.itens[0].valor

        for item in resultado.itens[1:]:
            subtotal = subtotal.somar(
                item.valor
            )

        subtotal = subtotal.arredondar_centavos()

        linhas = [
            f"Referência: {resultado.referencia_processo}",
            f"Motor de consolidação judicial: {cls.VERSAO}",
            (
                "Quantidade de verbas consolidadas: "
                f"{resultado.quantidade_itens}"
            ),
            "",
            "VERBAS CONSOLIDADAS",
        ]

        for item in resultado.itens:
            linhas.extend(
                (
                    "",
                    (
                        f"{item.codigo_verba} - "
                        f"{item.descricao}"
                    ),
                    (
                        "Valor: "
                        f"{item.valor.moeda} "
                        f"{format(item.valor.valor, 'f')}"
                    ),
                    (
                        "Fórmula: "
                        f"{item.formula_codigo or 'não informada'}"
                    ),
                )
            )

            for linha_memoria in item.memoria:
                linhas.append(
                    f"Memória: {linha_memoria}"
                )

        linhas.extend(
            (
                "",
                "RESUMO CONSOLIDADO",
                (
                    "Subtotal judicial: "
                    f"{subtotal.moeda} "
                    f"{format(subtotal.valor, 'f')}"
                ),
            )
        )

        return ResultadoConsolidadoJudicial(
            referencia_processo=resultado.referencia_processo,
            resultado_origem=resultado,
            subtotal=subtotal,
            memoria=tuple(linhas),
            versao_motor=cls.VERSAO,
        )
