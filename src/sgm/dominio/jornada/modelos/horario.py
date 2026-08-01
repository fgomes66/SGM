from __future__ import annotations

from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True, order=True, slots=True)
class Horario:
    minutos_desde_meia_noite: int

    def __post_init__(self) -> None:
        if not isinstance(self.minutos_desde_meia_noite, int):
            raise TypeError("Horário deve ser representado por minutos inteiros.")
        if not 0 <= self.minutos_desde_meia_noite <= 1439:
            raise ValueError("Horário deve estar entre 00:00 e 23:59.")

    @classmethod
    def de_texto(cls, texto: str) -> "Horario":
        partes = texto.strip().split(":")
        if len(partes) != 2:
            raise ValueError("Horário deve estar no formato HH:MM.")

        try:
            hora = int(partes[0])
            minuto = int(partes[1])
        except ValueError as exc:
            raise ValueError("Horário contém caracteres inválidos.") from exc

        if not 0 <= hora <= 23 or not 0 <= minuto <= 59:
            raise ValueError("Horário inválido.")

        return cls(hora * 60 + minuto)

    @classmethod
    def de_time(cls, valor: time) -> "Horario":
        return cls(valor.hour * 60 + valor.minute)

    def para_texto(self) -> str:
        hora, minuto = divmod(self.minutos_desde_meia_noite, 60)
        return f"{hora:02d}:{minuto:02d}"
