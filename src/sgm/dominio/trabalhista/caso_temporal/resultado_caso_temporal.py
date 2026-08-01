from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.competencias import (
    ResultadoCompetencia,
)
from sgm.dominio.trabalhista.consolidacao import (
    ResultadoConsolidado,
)
from sgm.dominio.trabalhista.eventos_aplicaveis import (
    LinhaTempoAplicada,
)
from sgm.dominio.trabalhista.liquidacao import MemoriaCalculo
from sgm.dominio.trabalhista.caso_temporal.plano_caso_temporal import (
    PlanoCasoTemporal,
)


@dataclass(frozen=True, slots=True)
class ResultadoCasoTemporal:
    plano: PlanoCasoTemporal
    linha_aplicada: LinhaTempoAplicada
    resultados_mensais: tuple[ResultadoCompetencia, ...]
    consolidado: ResultadoConsolidado
    memoria: MemoriaCalculo
    versao_motor: str = "0.9.1-E"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.resultados_mensais:
            raise ValueError(
                "O caso temporal deve produzir ao menos um resultado."
            )

        if (
            self.consolidado.resultados
            != self.resultados_mensais
        ):
            raise ValueError(
                "O consolidado deve usar os resultados do caso."
            )

        competencias_planos = tuple(
            plano.competencia
            for plano in self.linha_aplicada.planos_ativos
        )
        competencias_resultados = tuple(
            resultado.competencia
            for resultado in self.resultados_mensais
        )

        if competencias_planos != competencias_resultados:
            raise ValueError(
                "Cada plano ativo deve possuir resultado mensal."
            )
