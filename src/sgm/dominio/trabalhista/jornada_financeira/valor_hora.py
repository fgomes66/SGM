from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.jornada_financeira.divisor_jornada import (
    DivisorJornada,
)
from sgm.dominio.trabalhista.remuneracao.base_de_calculo import (
    BaseDeCalculo,
)


@dataclass(frozen=True, slots=True)
class ValorHora:
    valor: ValorMonetario
    base: BaseDeCalculo
    divisor: DivisorJornada
    formula_codigo: str = "FM-VH-001"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        formula_codigo = self.formula_codigo.strip().upper()
        object.__setattr__(
            self,
            "formula_codigo",
            formula_codigo,
        )

        if not formula_codigo:
            raise ValueError(
                "O código da fórmula do valor da hora é obrigatório."
            )

        if self.valor.moeda != self.base.valor.moeda:
            raise ValueError(
                "O valor da hora deve utilizar a mesma moeda da base."
            )

    def memoria_resumida(self) -> tuple[str, ...]:
        return (
            f"Base de cálculo: {self.base.descricao}",
            (
                "Valor da base: "
                f"{self.base.valor.moeda} "
                f"{format(self.base.valor.valor, 'f')}"
            ),
            f"Divisor: {format(self.divisor.divisor, 'f')}",
            (
                "Operação: "
                f"{format(self.base.valor.valor, 'f')} "
                f"/ {format(self.divisor.divisor, 'f')}"
            ),
            (
                "Valor da hora: "
                f"{self.valor.moeda} "
                f"{format(self.valor.valor, 'f')}"
            ),
            f"Fórmula: {self.formula_codigo}",
        )
