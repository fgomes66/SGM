from __future__ import annotations

from decimal import Decimal

from sgm.dominio.financeiro import ValorMonetario

from .competencia_equiparacao import CompetenciaEquiparacao
from .resultado_equiparacao import (
    ResultadoCompetenciaEquiparacao,
    ResultadoEquiparacaoSalarial,
)


class ServicoEquiparacaoSalarial:
    """Apura diferenças remuneratórias competência por competência."""

    VERSAO = "0.9.7-EQ"

    @classmethod
    def calcular(
        cls,
        competencias: tuple[CompetenciaEquiparacao, ...],
        referencia: str,
    ) -> ResultadoEquiparacaoSalarial:
        if not competencias:
            raise ValueError(
                "Informe ao menos uma competência para equiparação."
            )

        referencia = referencia.strip()

        if not referencia:
            raise ValueError(
                "A referência da equiparação é obrigatória."
            )

        ordenadas = tuple(
            sorted(
                competencias,
                key=lambda item: item.competencia,
            )
        )

        lista_competencias = tuple(
            item.competencia
            for item in ordenadas
        )

        if len(set(lista_competencias)) != len(lista_competencias):
            raise ValueError(
                "A equiparação não aceita competências duplicadas."
            )

        moedas = {
            item.remuneracao_reclamante.moeda
            for item in ordenadas
        } | {
            item.remuneracao_paradigma.moeda
            for item in ordenadas
        }

        if len(moedas) != 1:
            raise ValueError(
                "Todas as competências devem usar a mesma moeda."
            )

        resultados: list[ResultadoCompetenciaEquiparacao] = []

        for item in ordenadas:
            diferenca_bruta = (
                item.remuneracao_paradigma
                .subtrair(item.remuneracao_reclamante)
            )

            if diferenca_bruta.valor < Decimal("0"):
                diferenca = (
                    diferenca_bruta
                    .multiplicar(Decimal("0"))
                    .arredondar_centavos()
                )
            else:
                diferenca = diferenca_bruta.arredondar_centavos()

            resultados.append(
                ResultadoCompetenciaEquiparacao(
                    competencia=item.competencia,
                    remuneracao_reclamante=(
                        item.remuneracao_reclamante
                    ),
                    remuneracao_paradigma=(
                        item.remuneracao_paradigma
                    ),
                    diferenca=diferenca,
                    origem_reclamante=item.origem_reclamante,
                    origem_paradigma=item.origem_paradigma,
                    fundamento=item.fundamento,
                )
            )

        total = resultados[0].diferenca

        for resultado in resultados[1:]:
            total = total.somar(
                resultado.diferenca
            )

        total = total.arredondar_centavos()

        return ResultadoEquiparacaoSalarial(
            resultados=tuple(resultados),
            total_diferencas=total,
            referencia=referencia,
            versao_motor=cls.VERSAO,
        )
