from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ParametrosDecimoTerceiro:
    avos: int
    fundamento: str
    criterio_juridico_id: UUID | None = None
    observacao: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.avos, int):
            raise TypeError("A quantidade de avos deve ser inteira.")

        if self.avos < 0 or self.avos > 12:
            raise ValueError(
                "A quantidade de avos deve estar entre 0 e 12."
            )

        fundamento = self.fundamento.strip()
        object.__setattr__(self, "fundamento", fundamento)

        if not fundamento:
            raise ValueError(
                "O fundamento dos parâmetros do 13º é obrigatório."
            )

        if self.observacao is not None:
            observacao = self.observacao.strip()
            object.__setattr__(
                self,
                "observacao",
                observacao or None,
            )

    @property
    def fator_avos(self) -> Decimal:
        return Decimal(self.avos) / Decimal("12")
