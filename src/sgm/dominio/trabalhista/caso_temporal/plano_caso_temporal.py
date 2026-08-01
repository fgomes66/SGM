from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.eventos_aplicaveis import (
    EventoContratualAplicavel,
)
from sgm.dominio.trabalhista.liquidacao import (
    PlanoLiquidacaoIntegrada,
)
from sgm.dominio.trabalhista.temporal import PeriodoContratual


@dataclass(frozen=True, slots=True)
class PlanoCasoTemporal:
    referencia: str
    periodo: PeriodoContratual
    plano_modelo: PlanoLiquidacaoIntegrada
    eventos: tuple[EventoContratualAplicavel, ...]
    lema: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        referencia = self.referencia.strip()
        lema = self.lema.strip()
        object.__setattr__(self, "referencia", referencia)
        object.__setattr__(self, "lema", lema)

        if not referencia:
            raise ValueError(
                "A referência do caso temporal é obrigatória."
            )

        if not lema:
            raise ValueError(
                "O lema do caso temporal é obrigatório."
            )
