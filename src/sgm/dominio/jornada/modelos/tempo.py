from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import re


_PADRAO_HHMM = re.compile(r"^(?P<hora>\d{1,3}):(?P<minuto>\d{2})$")


@dataclass(frozen=True, order=True, slots=True)
class Tempo:
    minutos: int

    def __post_init__(self) -> None:
        if not isinstance(self.minutos, int):
            raise TypeError("Tempo deve ser representado em minutos inteiros.")
        if self.minutos < 0:
            raise ValueError("Tempo não pode ser negativo.")

    @classmethod
    def de_hhmm(cls, texto: str) -> "Tempo":
        correspondencia = _PADRAO_HHMM.fullmatch(texto.strip())
        if not correspondencia:
            raise ValueError("Tempo deve estar no formato HH:MM.")

        horas = int(correspondencia.group("hora"))
        minutos = int(correspondencia.group("minuto"))

        if minutos > 59:
            raise ValueError("A parte dos minutos deve estar entre 00 e 59.")

        return cls(horas * 60 + minutos)

    @classmethod
    def zero(cls) -> "Tempo":
        return cls(0)

    @property
    def horas_decimais(self) -> Decimal:
        return (Decimal(self.minutos) / Decimal("60")).quantize(
            Decimal("0.0001"),
            rounding=ROUND_HALF_UP,
        )

    def para_hhmm(self) -> str:
        horas, minutos = divmod(self.minutos, 60)
        return f"{horas:02d}:{minutos:02d}"

    def para_texto(self) -> str:
        horas, minutos = divmod(self.minutos, 60)
        return f"{horas}h{minutos:02d}min"

    def __add__(self, outro: "Tempo") -> "Tempo":
        if not isinstance(outro, Tempo):
            return NotImplemented
        return Tempo(self.minutos + outro.minutos)

    def __sub__(self, outro: "Tempo") -> "Tempo":
        if not isinstance(outro, Tempo):
            return NotImplemented
        if outro.minutos > self.minutos:
            raise ValueError("A subtração produziria tempo negativo.")
        return Tempo(self.minutos - outro.minutos)
