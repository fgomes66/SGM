from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


@dataclass(frozen=True, slots=True)
class ResultadoCompetenciaEquiparacao:
    competencia: CompetenciaCalculo
    remuneracao_reclamante: ValorMonetario
    remuneracao_paradigma: ValorMonetario
    diferenca: ValorMonetario
    origem_reclamante: str
    origem_paradigma: str
    fundamento: str

    def memoria_resumida(self) -> tuple[str, ...]:
        return (
            f"Competência: {self.competencia.como_texto()}",
            (
                "Remuneração reclamante: "
                f"{self.remuneracao_reclamante.moeda} "
                f"{format(self.remuneracao_reclamante.valor, 'f')}"
            ),
            (
                "Remuneração paradigma: "
                f"{self.remuneracao_paradigma.moeda} "
                f"{format(self.remuneracao_paradigma.valor, 'f')}"
            ),
            (
                "Diferença apurada: "
                f"{self.diferenca.moeda} "
                f"{format(self.diferenca.valor, 'f')}"
            ),
            (
                "Origem reclamante: "
                f"{self.origem_reclamante}"
            ),
            (
                "Origem paradigma: "
                f"{self.origem_paradigma}"
            ),
            f"Fundamento: {self.fundamento}",
        )


@dataclass(frozen=True, slots=True)
class ResultadoEquiparacaoSalarial:
    resultados: tuple[ResultadoCompetenciaEquiparacao, ...]
    total_diferencas: ValorMonetario
    referencia: str
    versao_motor: str = "0.9.7-EQ"

    def __post_init__(self) -> None:
        referencia = self.referencia.strip()

        if not referencia:
            raise ValueError(
                "A referência da equiparação é obrigatória."
            )

        if not self.resultados:
            raise ValueError(
                "A equiparação exige ao menos uma competência."
            )

        competencias = tuple(
            item.competencia
            for item in self.resultados
        )

        if tuple(sorted(competencias)) != competencias:
            raise ValueError(
                "As competências devem estar em ordem cronológica."
            )

        if len(set(competencias)) != len(competencias):
            raise ValueError(
                "A equiparação não aceita competências duplicadas."
            )

        moedas = {
            item.diferenca.moeda
            for item in self.resultados
        } | {
            self.total_diferencas.moeda
        }

        if len(moedas) != 1:
            raise ValueError(
                "Todos os resultados devem usar a mesma moeda."
            )

        object.__setattr__(
            self,
            "referencia",
            referencia,
        )

    @property
    def quantidade_competencias(self) -> int:
        return len(self.resultados)

    def memoria_resumida(self) -> tuple[str, ...]:
        linhas = [
            f"Referência: {self.referencia}",
            f"Motor de equiparação: {self.versao_motor}",
            (
                "Quantidade de competências: "
                f"{self.quantidade_competencias}"
            ),
        ]

        for resultado in self.resultados:
            linhas.extend(
                (
                    "",
                    *resultado.memoria_resumida(),
                )
            )

        linhas.extend(
            (
                "",
                (
                    "TOTAL DAS DIFERENÇAS: "
                    f"{self.total_diferencas.moeda} "
                    f"{format(self.total_diferencas.valor, 'f')}"
                ),
            )
        )

        return tuple(linhas)
