from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sgm.dominio.jornada import Tempo


@dataclass(frozen=True, slots=True)
class ResultadoHorasExtrasDia:
    data: date
    tempo_trabalhado: Tempo
    horas_normais: Tempo
    extras_diarias: Tempo

    def __post_init__(self) -> None:
        if (
            self.horas_normais.minutos + self.extras_diarias.minutos
            != self.tempo_trabalhado.minutos
        ):
            raise ValueError(
                "Resultado diário inconsistente: normais + extras "
                "deve ser igual ao tempo trabalhado."
            )
