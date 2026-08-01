from __future__ import annotations

from sgm.dominio.jornada.modelos.periodo_trabalho import PeriodoTrabalho
from sgm.dominio.jornada.modelos.resultado_jornada import ResultadoJornada


class CalculadoraJornada:
    @staticmethod
    def calcular(periodo: PeriodoTrabalho) -> ResultadoJornada:
        advertencias: list[str] = []

        if periodo.duracao_liquida.minutos > 12 * 60:
            advertencias.append(
                "Jornada líquida superior a 12 horas; recomenda-se revisão."
            )

        if (
            periodo.duracao_bruta.minutos >= 6 * 60
            and periodo.duracao_intervalos.minutos == 0
        ):
            advertencias.append(
                "Período superior ou igual a 6 horas sem intervalo registrado."
            )

        return ResultadoJornada(
            tempo_bruto=periodo.duracao_bruta,
            tempo_intervalos=periodo.duracao_intervalos,
            tempo_liquido=periodo.duracao_liquida,
            advertencias=tuple(advertencias),
        )
