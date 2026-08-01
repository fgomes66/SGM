from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.liquidacao import (
    PlanoLiquidacaoIntegrada,
)
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


@dataclass(frozen=True, slots=True)
class PlanoCompetencia:
    competencia: CompetenciaCalculo
    plano_liquidacao: PlanoLiquidacaoIntegrada
    referencia: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        referencia = self.referencia.strip()
        object.__setattr__(self, "referencia", referencia)

        if not referencia:
            raise ValueError(
                "A referência do plano por competência é obrigatória."
            )

        if (
            self.plano_liquidacao.base_remuneratoria.competencia.year
            != self.competencia.ano
            or
            self.plano_liquidacao.base_remuneratoria.competencia.month
            != self.competencia.mes
        ):
            raise ValueError(
                "A competência da base remuneratória deve coincidir "
                "com a competência do plano."
            )
