from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.competencias import ResultadoCompetencia
from sgm.dominio.trabalhista.liquidacao import MemoriaCalculo
from sgm.dominio.trabalhista.temporal import PeriodoContratual


@dataclass(frozen=True, slots=True)
class ResultadoConsolidado:
    periodo: PeriodoContratual
    resultados: tuple[ResultadoCompetencia, ...]
    subtotal_consolidado: ValorMonetario
    valor_final_consolidado: ValorMonetario
    memoria: MemoriaCalculo
    versao_motor: str = "0.9.1-C"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.resultados:
            raise ValueError(
                "A consolidação exige ao menos uma competência."
            )

        competencias = tuple(
            resultado.competencia
            for resultado in self.resultados
        )

        if len(set(competencias)) != len(competencias):
            raise ValueError(
                "A consolidação não aceita competências duplicadas."
            )

        if tuple(sorted(competencias)) != competencias:
            raise ValueError(
                "Os resultados devem estar em ordem cronológica."
            )

        if competencias[0] != self.periodo.inicio:
            raise ValueError(
                "O período deve iniciar na primeira competência."
            )

        if competencias[-1] != self.periodo.fim:
            raise ValueError(
                "O período deve terminar na última competência."
            )

        moedas = {
            resultado.subtotal.moeda
            for resultado in self.resultados
        } | {
            resultado.valor_final.moeda
            for resultado in self.resultados
        } | {
            self.subtotal_consolidado.moeda,
            self.valor_final_consolidado.moeda,
        }

        if len(moedas) != 1:
            raise ValueError(
                "Todos os resultados consolidados devem usar a mesma moeda."
            )

    @property
    def quantidade_competencias(self) -> int:
        return len(self.resultados)
