from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.trabalhista.temporal.competencia_calculo import (
    CompetenciaCalculo,
)


@dataclass(frozen=True, slots=True)
class PeriodoContratual:
    inicio: CompetenciaCalculo
    fim: CompetenciaCalculo

    def __post_init__(self) -> None:
        if self.fim < self.inicio:
            raise ValueError(
                "A competência final não pode ser anterior à inicial."
            )

    def contem(self, competencia: CompetenciaCalculo) -> bool:
        return self.inicio <= competencia <= self.fim

    def competencias(self) -> tuple[CompetenciaCalculo, ...]:
        atual = self.inicio
        itens: list[CompetenciaCalculo] = []

        while atual <= self.fim:
            itens.append(atual)
            atual = atual.proxima

        return tuple(itens)

    @property
    def quantidade_competencias(self) -> int:
        return len(self.competencias())

    def sobrepoe(self, outro: "PeriodoContratual") -> bool:
        return not (
            self.fim < outro.inicio
            or outro.fim < self.inicio
        )
