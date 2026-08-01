from __future__ import annotations

from sgm.dominio.trabalhista.competencias import ResultadoCompetencia
from sgm.dominio.trabalhista.consolidacao.resultado_consolidado import (
    ResultadoConsolidado,
)
from sgm.dominio.trabalhista.liquidacao import MemoriaCalculo
from sgm.dominio.trabalhista.temporal import PeriodoContratual


class ConsolidadorCompetencias:
    VERSAO = "0.9.1-C"

    @classmethod
    def consolidar(
        cls,
        resultados: tuple[ResultadoCompetencia, ...],
        referencia: str,
        lema: str,
    ) -> ResultadoConsolidado:
        if not resultados:
            raise ValueError(
                "Informe ao menos um resultado por competência."
            )

        referencia = referencia.strip()
        lema = lema.strip()

        if not referencia:
            raise ValueError(
                "A referência da consolidação é obrigatória."
            )

        if not lema:
            raise ValueError(
                "O lema da consolidação é obrigatório."
            )

        ordenados = tuple(
            sorted(
                resultados,
                key=lambda item: item.competencia,
            )
        )

        competencias = tuple(
            item.competencia for item in ordenados
        )

        if len(set(competencias)) != len(competencias):
            raise ValueError(
                "A consolidação não aceita competências duplicadas."
            )

        moedas = {
            item.subtotal.moeda for item in ordenados
        } | {
            item.valor_final.moeda for item in ordenados
        }

        if len(moedas) != 1:
            raise ValueError(
                "Todas as competências devem usar a mesma moeda."
            )

        subtotal = ordenados[0].subtotal
        valor_final = ordenados[0].valor_final

        for resultado in ordenados[1:]:
            subtotal = subtotal.somar(resultado.subtotal)
            valor_final = valor_final.somar(
                resultado.valor_final
            )

        subtotal = subtotal.arredondar_centavos()
        valor_final = valor_final.arredondar_centavos()

        periodo = PeriodoContratual(
            inicio=competencias[0],
            fim=competencias[-1],
        )

        linhas = [
            f"Referência: {referencia}",
            f"Motor de consolidação: {cls.VERSAO}",
            (
                "Período: "
                f"{periodo.inicio.como_texto()} a "
                f"{periodo.fim.como_texto()}"
            ),
            (
                "Quantidade de competências: "
                f"{len(ordenados)}"
            ),
            "",
            "COMPETÊNCIAS CONSOLIDADAS",
        ]

        for resultado in ordenados:
            linhas.extend(
                (
                    "",
                    (
                        f"Competência "
                        f"{resultado.competencia.como_texto()}"
                    ),
                    (
                        "Subtotal: "
                        f"{resultado.subtotal.moeda} "
                        f"{format(resultado.subtotal.valor, 'f')}"
                    ),
                    (
                        "Valor final: "
                        f"{resultado.valor_final.moeda} "
                        f"{format(resultado.valor_final.valor, 'f')}"
                    ),
                    (
                        "Referência mensal: "
                        f"{resultado.plano.referencia}"
                    ),
                )
            )

        linhas.extend(
            (
                "",
                "RESUMO CONSOLIDADO",
                (
                    "Subtotal consolidado: "
                    f"{subtotal.moeda} "
                    f"{format(subtotal.valor, 'f')}"
                ),
                (
                    "Valor final consolidado: "
                    f"{valor_final.moeda} "
                    f"{format(valor_final.valor, 'f')}"
                ),
            )
        )

        memoria = MemoriaCalculo(
            titulo=(
                "MEMÓRIA CONSOLIDADA POR COMPETÊNCIAS — SGM"
            ),
            linhas=tuple(linhas),
            lema=lema,
        )

        return ResultadoConsolidado(
            periodo=periodo,
            resultados=ordenados,
            subtotal_consolidado=subtotal,
            valor_final_consolidado=valor_final,
            memoria=memoria,
            versao_motor=cls.VERSAO,
        )
