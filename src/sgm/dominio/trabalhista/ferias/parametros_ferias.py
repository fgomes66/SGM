from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ParametrosFerias:
    avos: int
    percentual_terco: Decimal
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

        if not isinstance(self.percentual_terco, Decimal):
            raise TypeError(
                "O percentual do terço deve ser Decimal."
            )

        if not self.percentual_terco.is_finite():
            raise ValueError(
                "O percentual do terço deve ser finito."
            )

        if self.percentual_terco < 0 or self.percentual_terco > 1:
            raise ValueError(
                "O percentual do terço deve estar entre 0 e 1."
            )

        fundamento = self.fundamento.strip()
        object.__setattr__(self, "fundamento", fundamento)

        if not fundamento:
            raise ValueError(
                "O fundamento dos parâmetros de férias é obrigatório."
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

    @property
    def percentual_terco_exibicao(self) -> Decimal:
        return self.percentual_terco * Decimal("100")
