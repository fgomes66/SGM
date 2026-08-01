from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.horas_extras_financeiras.tipo_adicional_hora_extra import (
    TipoAdicionalHoraExtra,
)


@dataclass(frozen=True, slots=True)
class AdicionalHoraExtra:
    percentual: Decimal
    tipo: TipoAdicionalHoraExtra
    fundamento: str
    criterio_juridico_id: UUID | None = None
    descricao: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.percentual, Decimal):
            raise TypeError("O percentual do adicional deve ser Decimal.")

        if not self.percentual.is_finite():
            raise ValueError("O percentual do adicional deve ser finito.")

        if self.percentual < 0:
            raise ValueError(
                "O percentual do adicional não pode ser negativo."
            )

        fundamento = self.fundamento.strip()
        object.__setattr__(self, "fundamento", fundamento)

        if not fundamento:
            raise ValueError(
                "O fundamento do adicional de hora extra é obrigatório."
            )

        if self.descricao is not None:
            descricao = self.descricao.strip()
            object.__setattr__(
                self,
                "descricao",
                descricao or None,
            )

    @property
    def fator_total(self) -> Decimal:
        return Decimal("1") + self.percentual

    @property
    def percentual_exibicao(self) -> Decimal:
        return self.percentual * Decimal("100")
