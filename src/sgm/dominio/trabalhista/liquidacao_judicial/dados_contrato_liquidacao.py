from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class DadosContratoLiquidacao:
    """Dados mínimos do contrato necessários à liquidação."""

    data_admissao: date
    data_desligamento: date | None
    salario_base: Decimal
    jornada_semanal: Decimal | None = None

    def __post_init__(self) -> None:
        if self.data_desligamento is not None:
            if self.data_desligamento < self.data_admissao:
                raise ValueError(
                    "A data de desligamento não pode anteceder a admissão."
                )

        if self.salario_base <= 0:
            raise ValueError("O salário-base deve ser positivo.")

        if (
            self.jornada_semanal is not None
            and self.jornada_semanal <= 0
        ):
            raise ValueError(
                "A jornada semanal deve ser positiva."
            )
