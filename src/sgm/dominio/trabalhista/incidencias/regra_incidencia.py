from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.incidencias.tipo_base_incidencia import (
    TipoBaseIncidencia,
)


@dataclass(frozen=True, slots=True)
class RegraIncidencia:
    base_destino: TipoBaseIncidencia
    incide: bool
    fundamento: str
    criterio_juridico_id: UUID | None = None
    versao: int = 1
    observacao: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.incide, bool):
            raise TypeError("O indicador de incidência deve ser booleano.")

        fundamento = self.fundamento.strip()
        object.__setattr__(self, "fundamento", fundamento)

        if not fundamento:
            raise ValueError(
                "O fundamento da regra de incidência é obrigatório."
            )

        if self.versao < 1:
            raise ValueError(
                "A versão da regra deve ser igual ou superior a 1."
            )

        if self.observacao is not None:
            observacao = self.observacao.strip()
            object.__setattr__(
                self,
                "observacao",
                observacao or None,
            )
