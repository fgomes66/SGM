from __future__ import annotations
from dataclasses import dataclass
from datetime import date
import calendar
import re

_PADRAO = re.compile(r"^(?P<ano>\d{4})-(?P<mes>\d{2})$")

@dataclass(frozen=True, order=True, slots=True)
class Competencia:
    ano: int
    mes: int

    def __post_init__(self) -> None:
        if self.ano < 1:
            raise ValueError("O ano deve ser positivo.")
        if not 1 <= self.mes <= 12:
            raise ValueError("O mês deve estar entre 1 e 12.")

    @classmethod
    def de_texto(cls, texto: str) -> "Competencia":
        correspondencia = _PADRAO.fullmatch(texto)
        if not correspondencia:
            raise ValueError("Competência deve estar no formato AAAA-MM.")
        return cls(int(correspondencia.group("ano")), int(correspondencia.group("mes")))

    @property
    def inicio(self) -> date:
        return date(self.ano, self.mes, 1)

    @property
    def fim(self) -> date:
        return date(self.ano, self.mes, calendar.monthrange(self.ano, self.mes)[1])

    def proxima(self) -> "Competencia":
        return Competencia(self.ano + 1, 1) if self.mes == 12 else Competencia(self.ano, self.mes + 1)

    def anterior(self) -> "Competencia":
        if self.ano == 1 and self.mes == 1:
            raise ValueError("Não existe competência anterior representável.")
        return Competencia(self.ano - 1, 12) if self.mes == 1 else Competencia(self.ano, self.mes - 1)

    def __str__(self) -> str:
        return f"{self.ano:04d}-{self.mes:02d}"
