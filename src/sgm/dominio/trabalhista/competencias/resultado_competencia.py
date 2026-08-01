from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.liquidacao import (
    LiquidacaoTrabalhista,
    MemoriaCalculo,
)
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo
from sgm.dominio.trabalhista.competencias.plano_competencia import (
    PlanoCompetencia,
)


@dataclass(frozen=True, slots=True)
class ResultadoCompetencia:
    competencia: CompetenciaCalculo
    plano: PlanoCompetencia
    liquidacao: LiquidacaoTrabalhista
    subtotal: ValorMonetario
    valor_final: ValorMonetario
    memoria: MemoriaCalculo
    versao_motor: str = "0.9.1-B"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.competencia != self.plano.competencia:
            raise ValueError(
                "A competência do resultado deve coincidir com o plano."
            )

        if self.subtotal != self.liquidacao.subtotal:
            raise ValueError(
                "O subtotal deve coincidir com a liquidação."
            )

        if self.valor_final != self.liquidacao.valor_final:
            raise ValueError(
                "O valor final deve coincidir com a liquidação."
            )

        if (
            self.competencia.como_texto()
            not in self.memoria.como_texto()
        ):
            raise ValueError(
                "A memória deve identificar a competência."
            )
