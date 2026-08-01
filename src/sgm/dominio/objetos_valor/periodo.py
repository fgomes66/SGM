from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterator

@dataclass(frozen=True, slots=True)
class Periodo:
    inicio: date
    fim: date

    def __post_init__(self) -> None:
        if self.fim < self.inicio:
            raise ValueError("A data final não pode anteceder a inicial.")

    @property
    def quantidade_dias(self) -> int:
        return (self.fim - self.inicio).days + 1

    def contem(self, data: date) -> bool:
        return self.inicio <= data <= self.fim

    def sobrepoe(self, outro: "Periodo") -> bool:
        return self.inicio <= outro.fim and outro.inicio <= self.fim

    def intersecao(self, outro: "Periodo") -> "Periodo | None":
        inicio = max(self.inicio, outro.inicio)
        fim = min(self.fim, outro.fim)
        return None if fim < inicio else Periodo(inicio, fim)

    def dias(self) -> Iterator[date]:
        atual = self.inicio
        while atual <= self.fim:
            yield atual
            atual += timedelta(days=1)
