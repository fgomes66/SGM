from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

_CENTAVO = Decimal("0.01")

@dataclass(frozen=True, slots=True)
class Dinheiro:
    valor: Decimal
    moeda: str = "BRL"

    def __post_init__(self) -> None:
        if not isinstance(self.valor, Decimal):
            raise TypeError("Dinheiro exige Decimal; float é proibido.")
        if not self.valor.is_finite():
            raise ValueError("O valor monetário deve ser finito.")
        if len(self.moeda) != 3:
            raise ValueError("A moeda deve utilizar código de três letras.")

    @classmethod
    def de_texto(cls, valor: str, moeda: str = "BRL") -> "Dinheiro":
        try:
            decimal = Decimal(valor)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Valor monetário inválido: {valor!r}.") from exc
        return cls(decimal, moeda.upper())

    @classmethod
    def zero(cls, moeda: str = "BRL") -> "Dinheiro":
        return cls(Decimal("0"), moeda.upper())

    def quantizado(self) -> "Dinheiro":
        return Dinheiro(
            self.valor.quantize(_CENTAVO, rounding=ROUND_HALF_UP),
            self.moeda,
        )

    def _validar_moeda(self, outro: "Dinheiro") -> None:
        if self.moeda != outro.moeda:
            raise ValueError(f"Moedas incompatíveis: {self.moeda} e {outro.moeda}.")

    def __add__(self, outro: "Dinheiro") -> "Dinheiro":
        if not isinstance(outro, Dinheiro):
            return NotImplemented
        self._validar_moeda(outro)
        return Dinheiro(self.valor + outro.valor, self.moeda)

    def __sub__(self, outro: "Dinheiro") -> "Dinheiro":
        if not isinstance(outro, Dinheiro):
            return NotImplemented
        self._validar_moeda(outro)
        return Dinheiro(self.valor - outro.valor, self.moeda)

    def multiplicar(self, fator: Decimal) -> "Dinheiro":
        if not isinstance(fator, Decimal):
            raise TypeError("O fator deve ser Decimal.")
        return Dinheiro(self.valor * fator, self.moeda)

    def dividir(self, divisor: Decimal) -> "Dinheiro":
        if not isinstance(divisor, Decimal):
            raise TypeError("O divisor deve ser Decimal.")
        if divisor == 0:
            raise ZeroDivisionError("O divisor não pode ser zero.")
        return Dinheiro(self.valor / divisor, self.moeda)

    def para_banco(self) -> str:
        return format(self.valor, "f")
