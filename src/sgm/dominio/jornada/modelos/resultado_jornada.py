from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.jornada.modelos.tempo import Tempo


@dataclass(frozen=True, slots=True)
class ResultadoJornada:
    tempo_bruto: Tempo
    tempo_intervalos: Tempo
    tempo_liquido: Tempo
    advertencias: tuple[str, ...] = ()
    inconsistencias: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if (
            self.tempo_bruto.minutos
            != self.tempo_intervalos.minutos + self.tempo_liquido.minutos
        ):
            raise ValueError(
                "Resultado inconsistente: bruto deve ser igual a intervalos + líquido."
            )

    @property
    def possui_inconsistencias(self) -> bool:
        return bool(self.inconsistencias)
