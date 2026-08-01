from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

@dataclass(frozen=True, slots=True)
class Percentual:
    fator: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.fator, Decimal):
            raise TypeError("Percentual exige Decimal; float é proibido.")
        if not self.fator.is_finite():
            raise ValueError("O percentual deve ser finito.")

    @classmethod
    def de_percentual(cls, valor_percentual: str) -> "Percentual":
        try:
            valor = Decimal(valor_percentual)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Percentual inválido: {valor_percentual!r}.") from exc
        return cls(valor / Decimal("100"))

    @classmethod
    def de_fator(cls, fator: str) -> "Percentual":
        try:
            return cls(Decimal(fator))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Fator inválido: {fator!r}.") from exc

    @property
    def valor_percentual(self) -> Decimal:
        return self.fator * Decimal("100")

    @property
    def multiplicador_com_principal(self) -> Decimal:
        return Decimal("1") + self.fator
