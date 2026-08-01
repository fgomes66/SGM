from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.dependencias import CodigoVerba


@dataclass(frozen=True, slots=True)
class VerbaLiquidada:
    codigo: CodigoVerba
    descricao: str
    valor: ValorMonetario
    formula_codigo: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        descricao = self.descricao.strip()
        formula = self.formula_codigo.strip().upper()
        object.__setattr__(self, "descricao", descricao)
        object.__setattr__(self, "formula_codigo", formula)

        if not descricao:
            raise ValueError(
                "A descrição da verba liquidada é obrigatória."
            )

        if not formula:
            raise ValueError(
                "A fórmula da verba liquidada é obrigatória."
            )
