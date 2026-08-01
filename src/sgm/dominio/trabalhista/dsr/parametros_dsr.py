from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ParametrosDSR:
    dias_uteis: int
    dias_repouso: int
    fundamento: str
    criterio_juridico_id: UUID | None = None
    observacao: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.dias_uteis, int):
            raise TypeError("Dias úteis devem ser um número inteiro.")

        if not isinstance(self.dias_repouso, int):
            raise TypeError(
                "Dias de repouso devem ser um número inteiro."
            )

        if self.dias_uteis <= 0:
            raise ValueError(
                "A quantidade de dias úteis deve ser maior que zero."
            )

        if self.dias_repouso < 0:
            raise ValueError(
                "A quantidade de dias de repouso não pode ser negativa."
            )

        fundamento = self.fundamento.strip()
        object.__setattr__(self, "fundamento", fundamento)

        if not fundamento:
            raise ValueError(
                "O fundamento dos parâmetros de DSR é obrigatório."
            )

        if self.observacao is not None:
            observacao = self.observacao.strip()
            object.__setattr__(
                self,
                "observacao",
                observacao or None,
            )

    @property
    def fator(self) -> Decimal:
        return (
            Decimal(self.dias_repouso)
            / Decimal(self.dias_uteis)
        )
