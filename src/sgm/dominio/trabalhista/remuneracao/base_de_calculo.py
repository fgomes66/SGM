from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.remuneracao.tipo_base import (
    TipoBaseCalculo,
)


@dataclass(frozen=True, slots=True)
class BaseDeCalculo:
    valor: ValorMonetario
    tipo: TipoBaseCalculo
    competencia: date
    descricao: str
    origem_documental: str
    criterio_juridico_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        descricao = self.descricao.strip()
        origem_documental = self.origem_documental.strip()

        object.__setattr__(self, "descricao", descricao)
        object.__setattr__(
            self,
            "origem_documental",
            origem_documental,
        )

        if not descricao:
            raise ValueError(
                "A descrição da base de cálculo é obrigatória."
            )

        if not origem_documental:
            raise ValueError(
                "A origem documental da base de cálculo é obrigatória."
            )
