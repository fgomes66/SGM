from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ResultadoCalculoDesktop:
    competencia: date
    salario_base: Decimal
    divisor: Decimal
    quantidade_horas: Decimal
    adicional_percentual: Decimal
    valor_hora: Decimal
    valor_hora_com_adicional: Decimal
    valor_total: Decimal
    fundamento: str
    formula_codigo: str = "FM-HE-001"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        fundamento = self.fundamento.strip()
        formula = self.formula_codigo.strip().upper()
        object.__setattr__(self, "fundamento", fundamento)
        object.__setattr__(self, "formula_codigo", formula)

        if not fundamento:
            raise ValueError("O fundamento do cálculo é obrigatório.")
        if not formula:
            raise ValueError("O código da fórmula é obrigatório.")

        for nome in (
            "salario_base",
            "divisor",
            "quantidade_horas",
            "adicional_percentual",
            "valor_hora",
            "valor_hora_com_adicional",
            "valor_total",
        ):
            valor = getattr(self, nome)
            if not isinstance(valor, Decimal):
                raise TypeError(f"O campo {nome} deve ser Decimal.")
            if not valor.is_finite():
                raise ValueError(f"O campo {nome} deve ser finito.")

        if self.salario_base <= 0:
            raise ValueError("O salário-base deve ser maior que zero.")
        if self.divisor <= 0:
            raise ValueError("O divisor deve ser maior que zero.")
        if self.quantidade_horas <= 0:
            raise ValueError("A quantidade de horas deve ser maior que zero.")
        if self.adicional_percentual < 0:
            raise ValueError("O adicional não pode ser negativo.")
        if self.valor_total < 0:
            raise ValueError("O total não pode ser negativo.")

    def memoria_resumida(self) -> tuple[str, ...]:
        return (
            f"Competência: {self.competencia.isoformat()}",
            f"Salário-base: R$ {self.salario_base:.2f}",
            f"Divisor: {self.divisor}",
            f"Valor-hora: R$ {self.valor_hora:.6f}",
            f"Adicional: {self.adicional_percentual * Decimal('100')}%",
            (
                "Valor-hora com adicional: "
                f"R$ {self.valor_hora_com_adicional:.6f}"
            ),
            f"Quantidade: {self.quantidade_horas} horas",
            f"Total: R$ {self.valor_total:.2f}",
            f"Fórmula: {self.formula_codigo}",
            f"Fundamento: {self.fundamento}",
        )
