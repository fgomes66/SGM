from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.jornada.modelos.horario import Horario
from sgm.dominio.jornada.modelos.tempo import Tempo


@dataclass(frozen=True, slots=True)
class Intervalo:
    inicio: Horario
    fim: Horario

    def __post_init__(self) -> None:
        if self.fim <= self.inicio:
            raise ValueError(
                "Nesta versão, o intervalo deve terminar após o início no mesmo dia."
            )

    @property
    def duracao(self) -> Tempo:
        return Tempo(
            self.fim.minutos_desde_meia_noite
            - self.inicio.minutos_desde_meia_noite
        )
