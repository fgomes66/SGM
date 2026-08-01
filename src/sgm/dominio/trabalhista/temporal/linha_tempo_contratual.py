from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.temporal.competencia_calculo import (
    CompetenciaCalculo,
)
from sgm.dominio.trabalhista.temporal.evento_contratual import (
    EventoContratual,
)
from sgm.dominio.trabalhista.temporal.periodo_contratual import (
    PeriodoContratual,
)
from sgm.dominio.trabalhista.temporal.tipo_evento_contratual import (
    TipoEventoContratual,
)


@dataclass(frozen=True, slots=True)
class LinhaTempoContratual:
    periodo: PeriodoContratual
    eventos: tuple[EventoContratual, ...] = ()
    referencia: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        ordenados = tuple(
            sorted(
                self.eventos,
                key=lambda item: (
                    item.competencia,
                    item.tipo.value,
                    str(item.id),
                ),
            )
        )
        object.__setattr__(self, "eventos", ordenados)

        for evento in ordenados:
            if not self.periodo.contem(evento.competencia):
                raise ValueError(
                    "Todos os eventos devem estar dentro do período."
                )

        if self.referencia is not None:
            referencia = self.referencia.strip()
            object.__setattr__(
                self,
                "referencia",
                referencia or None,
            )

    def adicionar_evento(
        self,
        evento: EventoContratual,
    ) -> "LinhaTempoContratual":
        return LinhaTempoContratual(
            periodo=self.periodo,
            eventos=self.eventos + (evento,),
            referencia=self.referencia,
        )

    def eventos_da_competencia(
        self,
        competencia: CompetenciaCalculo,
    ) -> tuple[EventoContratual, ...]:
        return tuple(
            evento
            for evento in self.eventos
            if evento.competencia == competencia
        )

    def eventos_do_tipo(
        self,
        tipo: TipoEventoContratual,
    ) -> tuple[EventoContratual, ...]:
        return tuple(
            evento
            for evento in self.eventos
            if evento.tipo == tipo
        )

    @property
    def competencias(self) -> tuple[CompetenciaCalculo, ...]:
        return self.periodo.competencias()

    def contem_evento(
        self,
        tipo: TipoEventoContratual,
        competencia: CompetenciaCalculo,
    ) -> bool:
        return any(
            evento.tipo == tipo
            and evento.competencia == competencia
            for evento in self.eventos
        )
