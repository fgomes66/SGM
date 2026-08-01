from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.dependencias import CodigoVerba
from sgm.dominio.trabalhista.incidencias.regra_incidencia import (
    RegraIncidencia,
)


@dataclass(frozen=True, slots=True)
class ParcelaIncidencia:
    verba: CodigoVerba
    valor: ValorMonetario
    regra: RegraIncidencia
    descricao: str
    documento_id: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        descricao = self.descricao.strip()
        object.__setattr__(self, "descricao", descricao)

        if not descricao:
            raise ValueError(
                "A descrição da parcela de incidência é obrigatória."
            )

        if self.documento_id is not None:
            documento_id = self.documento_id.strip()
            object.__setattr__(
                self,
                "documento_id",
                documento_id or None,
            )
