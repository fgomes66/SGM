from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ItemMemoria:
    rotulo: str
    valor: str
    formula_codigo: str | None = None
    fundamento: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        rotulo = self.rotulo.strip()
        valor = self.valor.strip()
        object.__setattr__(self, "rotulo", rotulo)
        object.__setattr__(self, "valor", valor)

        if not rotulo:
            raise ValueError("O rótulo do item é obrigatório.")

        if not valor:
            raise ValueError("O valor do item é obrigatório.")

        if self.formula_codigo is not None:
            formula = self.formula_codigo.strip().upper()
            object.__setattr__(
                self,
                "formula_codigo",
                formula or None,
            )

        if self.fundamento is not None:
            fundamento = self.fundamento.strip()
            object.__setattr__(
                self,
                "fundamento",
                fundamento or None,
            )
