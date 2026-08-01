from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sgm.dominio.trabalhista.eventos_aplicaveis.evento_contratual_aplicavel import EventoContratualAplicavel
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


@dataclass(frozen=True, slots=True)
class EstadoContratual:
    competencia: CompetenciaCalculo
    salario: Decimal
    divisor: Decimal
    jornada_semanal_minutos: int
    ativo: bool
    rescindido: bool
    eventos_aplicados: tuple[EventoContratualAplicavel, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.salario, Decimal):
            raise TypeError("O salário do estado deve ser Decimal.")
        if not isinstance(self.divisor, Decimal):
            raise TypeError("O divisor do estado deve ser Decimal.")
        if self.salario <= 0:
            raise ValueError("O salário deve ser maior que zero.")
        if self.divisor <= 0:
            raise ValueError("O divisor deve ser maior que zero.")
        if self.jornada_semanal_minutos <= 0:
            raise ValueError(
                "A jornada semanal deve ser maior que zero."
            )
        if self.rescindido and self.ativo:
            raise ValueError(
                "Um estado rescindido não pode permanecer ativo."
            )
