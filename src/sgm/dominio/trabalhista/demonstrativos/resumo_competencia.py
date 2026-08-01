from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


@dataclass(frozen=True, slots=True)
class ResumoCompetencia:
    competencia: CompetenciaCalculo
    subtotal: ValorMonetario
    valor_final: ValorMonetario
    ativa: bool
    referencia: str

    def __post_init__(self) -> None:
        referencia = self.referencia.strip()
        object.__setattr__(self, "referencia", referencia)

        if not referencia:
            raise ValueError(
                "A referência da competência é obrigatória."
            )

        if self.subtotal.moeda != self.valor_final.moeda:
            raise ValueError(
                "Subtotal e valor final devem usar a mesma moeda."
            )
