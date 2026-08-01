from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.atualizacao.resultado_atualizacao import (
    ResultadoAtualizacao,
)


@dataclass(frozen=True, slots=True)
class ResultadoAtualizacaoJuros:
    correcao: ResultadoAtualizacao
    juros: ResultadoAtualizacao
    valor_final: ValorMonetario
    formula_codigo: str = "FM-AJ-001"
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
                "O código da fórmula consolidada é obrigatório."
            )

        moedas = {
            self.correcao.valor_original.moeda,
            self.correcao.valor_atualizado.moeda,
            self.juros.valor_atualizado.moeda,
            self.valor_final.moeda,
        }
        if len(moedas) != 1:
            raise ValueError(
                "Correção, juros e total devem usar a mesma moeda."
            )

    def memoria_resumida(self) -> tuple[str, ...]:
        return (
            "ETAPA 1 — CORREÇÃO MONETÁRIA",
            *self.correcao.memoria_resumida(),
            "ETAPA 2 — JUROS",
            *self.juros.memoria_resumida(),
            (
                "VALOR FINAL: "
                f"{self.valor_final.moeda} "
                f"{format(self.valor_final.valor, 'f')}"
            ),
            f"Fórmula consolidada: {self.formula_codigo}",
        )
