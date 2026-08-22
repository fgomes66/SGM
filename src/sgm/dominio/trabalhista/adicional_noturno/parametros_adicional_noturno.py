from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ParametrosAdicionalNoturno:
    """Critérios financeiros aplicáveis ao adicional noturno."""

    percentual: Decimal
    fundamento: str
    observacao: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.percentual, Decimal):
            raise TypeError(
                "O percentual do adicional noturno deve ser Decimal."
            )

        if not self.percentual.is_finite():
            raise ValueError(
                "O percentual do adicional noturno deve ser finito."
            )

        if self.percentual < 0:
            raise ValueError(
                "O percentual do adicional noturno não pode ser negativo."
            )

        fundamento = self.fundamento.strip()

        if not fundamento:
            raise ValueError(
                "O fundamento do adicional noturno é obrigatório."
            )

        object.__setattr__(
            self,
            "fundamento",
            fundamento,
        )

        if self.observacao is not None:
            observacao = self.observacao.strip()
            object.__setattr__(
                self,
                "observacao",
                observacao or None,
            )

    @property
    def percentual_exibicao(self) -> Decimal:
        return self.percentual * Decimal("100")
