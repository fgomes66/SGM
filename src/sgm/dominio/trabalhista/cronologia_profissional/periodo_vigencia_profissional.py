from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


@dataclass(frozen=True, slots=True)
class PeriodoVigenciaProfissional:
    inicio: CompetenciaCalculo
    fim: CompetenciaCalculo
    salario: Decimal
    divisor: Decimal
    jornada_semanal_minutos: int
    ativo: bool
    rescindido: bool

    def __post_init__(self) -> None:
        if self.fim < self.inicio:
            raise ValueError(
                "O fim da vigência não pode anteceder o início."
            )

        if not isinstance(self.salario, Decimal):
            raise TypeError("O salário da vigência deve ser Decimal.")

        if not isinstance(self.divisor, Decimal):
            raise TypeError("O divisor da vigência deve ser Decimal.")

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
                "Uma vigência rescindida não pode estar ativa."
            )

    @property
    def descricao_estado(self) -> str:
        if self.rescindido:
            return "RESCINDIDO"
        return "ATIVO" if self.ativo else "INATIVO"
