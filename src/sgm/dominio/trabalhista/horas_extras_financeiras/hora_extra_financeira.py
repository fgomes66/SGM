from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.jornada import Tempo
from sgm.dominio.trabalhista.horas_extras_financeiras.adicional_hora_extra import (
    AdicionalHoraExtra,
)
from sgm.dominio.trabalhista.jornada_financeira import ValorHora


@dataclass(frozen=True, slots=True)
class HoraExtraFinanceira:
    valor_hora: ValorHora
    quantidade: Tempo
    adicional: AdicionalHoraExtra
    valor_hora_com_adicional: ValorMonetario
    valor_total: ValorMonetario
    formula_codigo: str = "FM-HE-001"
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
                "O código da fórmula de horas extras é obrigatório."
            )

        moedas = {
            self.valor_hora.valor.moeda,
            self.valor_hora_com_adicional.moeda,
            self.valor_total.moeda,
        }
        if len(moedas) != 1:
            raise ValueError(
                "Todos os valores da hora extra devem usar a mesma moeda."
            )

    @property
    def quantidade_horas_exatas(self) -> Decimal:
        return Decimal(self.quantidade.minutos) / Decimal("60")

    def memoria_resumida(self) -> tuple[str, ...]:
        return (
            (
                "Valor da hora normal: "
                f"{self.valor_hora.valor.moeda} "
                f"{format(self.valor_hora.valor.valor, 'f')}"
            ),
            (
                "Adicional: "
                f"{format(self.adicional.percentual_exibicao, 'f')}%"
            ),
            (
                "Fator total: "
                f"{format(self.adicional.fator_total, 'f')}"
            ),
            (
                "Valor da hora com adicional: "
                f"{self.valor_hora_com_adicional.moeda} "
                f"{format(self.valor_hora_com_adicional.valor, 'f')}"
            ),
            (
                "Quantidade: "
                f"{self.quantidade.para_hhmm()} "
                f"({format(self.quantidade_horas_exatas, 'f')} horas)"
            ),
            (
                "Valor total: "
                f"{self.valor_total.moeda} "
                f"{format(self.valor_total.valor, 'f')}"
            ),
            f"Fórmula: {self.formula_codigo}",
        )
