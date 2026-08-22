from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


@dataclass(frozen=True, slots=True)
class CompetenciaEquiparacao:
    """Dados remuneratórios dos comparados em uma competência."""

    competencia: CompetenciaCalculo
    remuneracao_reclamante: ValorMonetario
    remuneracao_paradigma: ValorMonetario
    origem_reclamante: str
    origem_paradigma: str
    fundamento: str

    def __post_init__(self) -> None:
        origem_reclamante = self.origem_reclamante.strip()
        origem_paradigma = self.origem_paradigma.strip()
        fundamento = self.fundamento.strip()

        if not origem_reclamante:
            raise ValueError(
                "A origem documental da remuneração da reclamante "
                "é obrigatória."
            )

        if not origem_paradigma:
            raise ValueError(
                "A origem documental da remuneração do paradigma "
                "é obrigatória."
            )

        if not fundamento:
            raise ValueError(
                "O fundamento da equiparação é obrigatório."
            )

        if (
            self.remuneracao_reclamante.moeda
            != self.remuneracao_paradigma.moeda
        ):
            raise ValueError(
                "As remunerações comparadas devem usar a mesma moeda."
            )

        object.__setattr__(
            self,
            "origem_reclamante",
            origem_reclamante,
        )
        object.__setattr__(
            self,
            "origem_paradigma",
            origem_paradigma,
        )
        object.__setattr__(
            self,
            "fundamento",
            fundamento,
        )
