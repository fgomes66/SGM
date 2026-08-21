from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ParametrosLiquidacao:
    """Critérios gerais utilizados na execução da liquidação."""

    data_calculo: date
    moeda: str = "BRL"
    divisor_horas: Decimal | None = None
    percentual_horas_extras: Decimal | None = None
    aplicar_fgts: bool = True
    aplicar_inss: bool = True
    aplicar_irrf: bool = True
    observacoes: str = ""

    def __post_init__(self) -> None:
        moeda = self.moeda.strip().upper()

        if len(moeda) != 3 or not moeda.isalpha():
            raise ValueError(
                "A moeda deve utilizar código alfabético de três letras."
            )

        if (
            self.divisor_horas is not None
            and self.divisor_horas <= 0
        ):
            raise ValueError(
                "O divisor de horas deve ser positivo."
            )

        if (
            self.percentual_horas_extras is not None
            and self.percentual_horas_extras < 0
        ):
            raise ValueError(
                "O percentual de horas extras não pode ser negativo."
            )

        object.__setattr__(self, "moeda", moeda)
        object.__setattr__(
            self,
            "observacoes",
            self.observacoes.strip(),
        )
