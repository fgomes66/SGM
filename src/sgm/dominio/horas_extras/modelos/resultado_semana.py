from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sgm.dominio.jornada import Tempo
from sgm.dominio.horas_extras.modelos.resultado_dia import (
    ResultadoHorasExtrasDia,
)


@dataclass(frozen=True, slots=True)
class ResultadoHorasExtrasSemana:
    inicio_semana: date
    fim_semana: date
    resultados_diarios: tuple[ResultadoHorasExtrasDia, ...]
    total_trabalhado: Tempo
    total_normal: Tempo
    extras_diarias: Tempo
    extras_semanais_nao_duplicadas: Tempo
    total_horas_extras: Tempo
    adicional_aplicavel: Decimal
    memoria: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.fim_semana < self.inicio_semana:
            raise ValueError("O fim da semana não pode anteceder o início.")
        if (
            self.total_normal.minutos
            + self.total_horas_extras.minutos
            != self.total_trabalhado.minutos
        ):
            raise ValueError(
                "Resultado semanal inconsistente: normal + extras "
                "deve ser igual ao total trabalhado."
            )
        if (
            self.extras_diarias.minutos
            + self.extras_semanais_nao_duplicadas.minutos
            != self.total_horas_extras.minutos
        ):
            raise ValueError(
                "O total de extras deve corresponder à soma das "
                "extras diárias e semanais não duplicadas."
            )
