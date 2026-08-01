from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True, order=True)
class CompetenciaCalculo:
    ano: int
    mes: int

    def __post_init__(self) -> None:
        if not isinstance(self.ano, int):
            raise TypeError("O ano da competência deve ser inteiro.")

        if not isinstance(self.mes, int):
            raise TypeError("O mês da competência deve ser inteiro.")

        if self.ano < 1900 or self.ano > 9999:
            raise ValueError(
                "O ano da competência deve estar entre 1900 e 9999."
            )

        if self.mes < 1 or self.mes > 12:
            raise ValueError(
                "O mês da competência deve estar entre 1 e 12."
            )

    @classmethod
    def de_texto(cls, texto: str) -> "CompetenciaCalculo":
        partes = texto.strip().split("-")
        if len(partes) != 2:
            raise ValueError(
                "A competência deve usar o formato AAAA-MM."
            )

        try:
            ano = int(partes[0])
            mes = int(partes[1])
        except ValueError as exc:
            raise ValueError(
                "A competência deve usar números no formato AAAA-MM."
            ) from exc

        return cls(ano=ano, mes=mes)

    @property
    def primeiro_dia(self) -> date:
        return date(self.ano, self.mes, 1)

    @property
    def proxima(self) -> "CompetenciaCalculo":
        if self.mes == 12:
            return CompetenciaCalculo(self.ano + 1, 1)
        return CompetenciaCalculo(self.ano, self.mes + 1)

    @property
    def anterior(self) -> "CompetenciaCalculo":
        if self.mes == 1:
            return CompetenciaCalculo(self.ano - 1, 12)
        return CompetenciaCalculo(self.ano, self.mes - 1)

    def como_texto(self) -> str:
        return f"{self.ano:04d}-{self.mes:02d}"
