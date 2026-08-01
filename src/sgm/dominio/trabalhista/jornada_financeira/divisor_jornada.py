from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class DivisorJornada:
    divisor: Decimal
    jornada_semanal_minutos: int
    fundamento: str
    criterio_juridico_id: UUID | None = None
    descricao: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.divisor, Decimal):
            raise TypeError("O divisor deve ser Decimal.")

        if not self.divisor.is_finite():
            raise ValueError("O divisor deve ser finito.")

        if self.divisor <= 0:
            raise ValueError("O divisor deve ser maior que zero.")

        if not isinstance(self.jornada_semanal_minutos, int):
            raise TypeError(
                "A jornada semanal deve ser informada em minutos inteiros."
            )

        if self.jornada_semanal_minutos <= 0:
            raise ValueError(
                "A jornada semanal deve ser maior que zero."
            )

        fundamento = self.fundamento.strip()
        object.__setattr__(self, "fundamento", fundamento)

        if not fundamento:
            raise ValueError("O fundamento do divisor é obrigatório.")

        if self.descricao is not None:
            descricao = self.descricao.strip()
            object.__setattr__(
                self,
                "descricao",
                descricao or None,
            )

    @property
    def jornada_semanal_horas(self) -> Decimal:
        return Decimal(self.jornada_semanal_minutos) / Decimal("60")
