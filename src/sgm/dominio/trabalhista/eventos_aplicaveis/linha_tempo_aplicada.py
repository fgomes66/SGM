from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.competencias import PlanoCompetencia
from sgm.dominio.trabalhista.eventos_aplicaveis.estado_contratual import (
    EstadoContratual,
)
from sgm.dominio.trabalhista.temporal import PeriodoContratual


@dataclass(frozen=True, slots=True)
class LinhaTempoAplicada:
    periodo: PeriodoContratual
    estados: tuple[EstadoContratual, ...]
    planos_ativos: tuple[PlanoCompetencia, ...]
    competencias_inativas: tuple[str, ...]
    versao_motor: str = "0.9.1-D"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.estados:
            raise ValueError(
                "A linha aplicada deve conter estados contratuais."
            )

        competencias = tuple(
            estado.competencia for estado in self.estados
        )
        if tuple(sorted(competencias)) != competencias:
            raise ValueError(
                "Os estados devem estar em ordem cronológica."
            )

        if len(set(competencias)) != len(competencias):
            raise ValueError(
                "A linha aplicada não aceita competências duplicadas."
            )

    def estado_da_competencia(self, texto: str) -> EstadoContratual:
        for estado in self.estados:
            if estado.competencia.como_texto() == texto:
                return estado
        raise KeyError(
            f"Competência não encontrada na linha aplicada: {texto}."
        )
