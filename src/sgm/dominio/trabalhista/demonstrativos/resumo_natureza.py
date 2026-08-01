from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.demonstrativos.natureza_financeira import (
    NaturezaFinanceira,
)


@dataclass(frozen=True, slots=True)
class ResumoNatureza:
    natureza: NaturezaFinanceira
    valor: ValorMonetario
    quantidade_verbas: int

    def __post_init__(self) -> None:
        if self.quantidade_verbas < 1:
            raise ValueError(
                "A quantidade de verbas deve ser positiva."
            )
