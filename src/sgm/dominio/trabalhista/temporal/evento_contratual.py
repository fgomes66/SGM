from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.temporal.competencia_calculo import (
    CompetenciaCalculo,
)
from sgm.dominio.trabalhista.temporal.tipo_evento_contratual import (
    TipoEventoContratual,
)


@dataclass(frozen=True, slots=True)
class EventoContratual:
    competencia: CompetenciaCalculo
    tipo: TipoEventoContratual
    descricao: str
    fundamento: str
    documento_id: str | None = None
    criterio_juridico_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        descricao = self.descricao.strip()
        fundamento = self.fundamento.strip()

        object.__setattr__(self, "descricao", descricao)
        object.__setattr__(self, "fundamento", fundamento)

        if not descricao:
            raise ValueError(
                "A descrição do evento contratual é obrigatória."
            )

        if not fundamento:
            raise ValueError(
                "O fundamento do evento contratual é obrigatório."
            )

        if self.documento_id is not None:
            documento_id = self.documento_id.strip()
            object.__setattr__(
                self,
                "documento_id",
                documento_id or None,
            )
