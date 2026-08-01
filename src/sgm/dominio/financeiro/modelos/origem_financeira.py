from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OrigemFinanceira:
    descricao: str
    processo_id: UUID | None = None
    criterio_id: UUID | None = None
    formula_codigo: str | None = None
    documento_id: str | None = None
    observacao: str | None = None

    def __post_init__(self) -> None:
        descricao = self.descricao.strip()
        object.__setattr__(self, "descricao", descricao)

        if not descricao:
            raise ValueError("A descrição da origem financeira é obrigatória.")

        if self.formula_codigo is not None:
            codigo = self.formula_codigo.strip()
            object.__setattr__(self, "formula_codigo", codigo or None)

        if self.documento_id is not None:
            documento = self.documento_id.strip()
            object.__setattr__(self, "documento_id", documento or None)
