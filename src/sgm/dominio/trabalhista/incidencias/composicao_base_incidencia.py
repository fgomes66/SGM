from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.incidencias.parcela_incidencia import (
    ParcelaIncidencia,
)
from sgm.dominio.trabalhista.incidencias.tipo_base_incidencia import (
    TipoBaseIncidencia,
)


@dataclass(frozen=True, slots=True)
class ComposicaoBaseIncidencia:
    base_destino: TipoBaseIncidencia
    parcelas_avaliadas: tuple[ParcelaIncidencia, ...]
    parcelas_incluidas: tuple[ParcelaIncidencia, ...]
    parcelas_excluidas: tuple[ParcelaIncidencia, ...]
    total: ValorMonetario
    formula_codigo: str = "FM-BASE-INC-001"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        formula_codigo = self.formula_codigo.strip().upper()
        object.__setattr__(
            self,
            "formula_codigo",
            formula_codigo,
        )

        if not formula_codigo:
            raise ValueError(
                "O código da fórmula de composição é obrigatório."
            )

        avaliadas = set(self.parcelas_avaliadas)
        classificadas = (
            set(self.parcelas_incluidas)
            | set(self.parcelas_excluidas)
        )

        if avaliadas != classificadas:
            raise ValueError(
                "Toda parcela avaliada deve estar incluída ou excluída."
            )

        if set(self.parcelas_incluidas) & set(
            self.parcelas_excluidas
        ):
            raise ValueError(
                "Uma parcela não pode estar incluída e excluída."
            )

    def memoria_resumida(self) -> tuple[str, ...]:
        linhas = [
            f"Base de destino: {self.base_destino.value}",
            (
                "Parcelas avaliadas: "
                f"{len(self.parcelas_avaliadas)}"
            ),
            (
                "Parcelas incluídas: "
                f"{len(self.parcelas_incluidas)}"
            ),
            (
                "Parcelas excluídas: "
                f"{len(self.parcelas_excluidas)}"
            ),
        ]

        for parcela in self.parcelas_incluidas:
            linhas.append(
                "INCLUIR "
                f"{parcela.verba.value}: "
                f"{parcela.valor.moeda} "
                f"{format(parcela.valor.valor, 'f')}"
            )

        for parcela in self.parcelas_excluidas:
            linhas.append(
                "EXCLUIR "
                f"{parcela.verba.value}: "
                f"{parcela.regra.fundamento}"
            )

        linhas.extend(
            (
                (
                    "Total da base: "
                    f"{self.total.moeda} "
                    f"{format(self.total.valor, 'f')}"
                ),
                f"Fórmula: {self.formula_codigo}",
            )
        )

        return tuple(linhas)
