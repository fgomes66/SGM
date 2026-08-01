from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.atualizacao.fator_atualizacao import (
    FatorAtualizacao,
)


@dataclass(frozen=True, slots=True)
class ResultadoAtualizacao:
    valor_original: ValorMonetario
    fator: FatorAtualizacao
    valor_atualizado: ValorMonetario
    diferenca: ValorMonetario
    formula_codigo: str
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
                "O código da fórmula de atualização é obrigatório."
            )

        moedas = {
            self.valor_original.moeda,
            self.valor_atualizado.moeda,
            self.diferenca.moeda,
        }
        if len(moedas) != 1:
            raise ValueError(
                "Todos os valores da atualização devem usar a mesma moeda."
            )

    def memoria_resumida(self) -> tuple[str, ...]:
        return (
            (
                "Tipo: "
                f"{self.fator.tipo.value}"
            ),
            (
                "Valor original: "
                f"{self.valor_original.moeda} "
                f"{format(self.valor_original.valor, 'f')}"
            ),
            (
                "Fator: "
                f"{format(self.fator.fator, 'f')}"
            ),
            (
                "Percentual equivalente: "
                f"{format(self.fator.percentual_equivalente, 'f')}%"
            ),
            (
                "Período: "
                f"{self.fator.data_inicial.isoformat()} a "
                f"{self.fator.data_final.isoformat()}"
            ),
            (
                "Fonte: "
                f"{self.fator.fonte}"
            ),
            (
                "Valor atualizado: "
                f"{self.valor_atualizado.moeda} "
                f"{format(self.valor_atualizado.valor, 'f')}"
            ),
            (
                "Diferença: "
                f"{self.diferenca.moeda} "
                f"{format(self.diferenca.valor, 'f')}"
            ),
            f"Fórmula: {self.formula_codigo}",
        )
