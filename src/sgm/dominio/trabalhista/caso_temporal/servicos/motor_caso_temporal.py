from __future__ import annotations

from sgm.dominio.trabalhista.competencias import MotorCompetencia
from sgm.dominio.trabalhista.consolidacao import (
    ConsolidadorCompetencias,
)
from sgm.dominio.trabalhista.eventos_aplicaveis import (
    AplicadorEventosContratuais,
)
from sgm.dominio.trabalhista.liquidacao import MemoriaCalculo
from sgm.dominio.trabalhista.caso_temporal.plano_caso_temporal import (
    PlanoCasoTemporal,
)
from sgm.dominio.trabalhista.caso_temporal.resultado_caso_temporal import (
    ResultadoCasoTemporal,
)


class MotorCasoTemporal:
    VERSAO = "0.9.1-E"

    @classmethod
    def calcular(
        cls,
        plano: PlanoCasoTemporal,
    ) -> ResultadoCasoTemporal:
        linha = AplicadorEventosContratuais.aplicar(
            periodo=plano.periodo,
            plano_modelo=plano.plano_modelo,
            eventos=plano.eventos,
            referencia=plano.referencia,
        )

        resultados = tuple(
            MotorCompetencia.calcular(plano_competencia)
            for plano_competencia in linha.planos_ativos
        )

        if not resultados:
            raise ValueError(
                "O caso temporal não possui competências ativas."
            )

        consolidado = ConsolidadorCompetencias.consolidar(
            resultados=resultados,
            referencia=plano.referencia,
            lema=plano.lema,
        )

        linhas = [
            f"Referência: {plano.referencia}",
            f"Motor temporal completo: {cls.VERSAO}",
            (
                "Período contratual: "
                f"{plano.periodo.inicio.como_texto()} a "
                f"{plano.periodo.fim.como_texto()}"
            ),
            (
                "Estados contratuais: "
                f"{len(linha.estados)}"
            ),
            (
                "Competências calculadas: "
                f"{len(resultados)}"
            ),
            (
                "Competências inativas: "
                f"{len(linha.competencias_inativas)}"
            ),
            "",
            "LINHA DO TEMPO CONTRATUAL",
        ]

        for estado in linha.estados:
            eventos = (
                ", ".join(
                    evento.tipo.value
                    for evento in estado.eventos_aplicados
                )
                or "SEM_EVENTO"
            )
            linhas.append(
                f"{estado.competencia.como_texto()} | "
                f"salário={format(estado.salario, 'f')} | "
                f"divisor={format(estado.divisor, 'f')} | "
                f"jornada={estado.jornada_semanal_minutos} | "
                f"ativo={estado.ativo} | "
                f"rescindido={estado.rescindido} | "
                f"eventos={eventos}"
            )

        linhas.extend(
            (
                "",
                "RESULTADOS MENSAIS",
            )
        )

        for resultado in resultados:
            linhas.extend(
                (
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
                )
            )

        linhas.extend(
            (
                "",
                "CONSOLIDAÇÃO",
                (
                    "Subtotal consolidado: "
                    f"{consolidado.subtotal_consolidado.moeda} "
                    f"{format(consolidado.subtotal_consolidado.valor, 'f')}"
                ),
                (
                    "Valor final consolidado: "
                    f"{consolidado.valor_final_consolidado.moeda} "
                    f"{format(consolidado.valor_final_consolidado.valor, 'f')}"
                ),
            )
        )

        memoria = MemoriaCalculo(
            titulo=(
                "MEMÓRIA DO CASO TEMPORAL COMPLETO — SGM"
            ),
            linhas=tuple(linhas),
            lema=plano.lema,
        )

        return ResultadoCasoTemporal(
            plano=plano,
            linha_aplicada=linha,
            resultados_mensais=resultados,
            consolidado=consolidado,
            memoria=memoria,
            versao_motor=cls.VERSAO,
        )
