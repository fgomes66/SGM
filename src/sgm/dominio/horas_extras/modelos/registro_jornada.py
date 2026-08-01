from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sgm.dominio.jornada import Tempo


@dataclass(frozen=True, slots=True)
class RegistroJornada:
    data: date
    tempo_trabalhado: Tempo
    identificador_fonte: str | None = None
    observacao: str | None = None

    def __post_init__(self) -> None:
        if self.identificador_fonte is not None:
            fonte = self.identificador_fonte.strip()
            object.__setattr__(self, "identificador_fonte", fonte or None)
