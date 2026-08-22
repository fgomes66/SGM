from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.jornada import Tempo
from sgm.dominio.trabalhista.jornada_financeira import ValorHora

from .parametros_adicional_noturno import ParametrosAdicionalNoturno


@dataclass(frozen=True, slots=True)
class AdicionalNoturnoApurado:
    """Resultado financeiro do adicional noturno."""

    valor_hora: ValorHora
    quantidade: Tempo
    parametros: ParametrosAdicionalNoturno
    valor_adicional_hora: ValorMonetario
    valor_total: ValorMonetario
    formula_codigo: str = "FM-AN-001"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        formula_codigo = self.formula_codigo.strip().upper()

        if not formula_codigo:
            raise ValueError(
                "O código da fórmula do adicional noturno é obrigatório."
            )

        object.__setattr__(
            self,
            "formula_codigo",
            formula_codigo,
        )

        moedas = {
            self.valor_hora.valor.moeda,
            self.valor_adicional_hora.moeda,
            self.valor_total.moeda,
        }

        if len(moedas) != 1:
            raise ValueError(
                "Os valores do adicional noturno devem usar "
                "a mesma moeda."
            )

    @property
    def quantidade_horas_exatas(self) -> Decimal:
        return (
            Decimal(self.quantidade.minutos)
            / Decimal("60")
        )

    def memoria_resumida(self) -> tuple[str, ...]:
        return (
            (
                "Valor da hora normal: "
                f"{self.valor_hora.valor.moeda} "
                f"{format(self.valor_hora.valor.valor, 'f')}"
            ),
            (
                "Percentual noturno: "
                f"{format(self.parametros.percentual_exibicao, 'f')}%"
            ),
            (
                "Valor do adicional por hora: "
                f"{self.valor_adicional_hora.moeda} "
                f"{format(self.valor_adicional_hora.valor, 'f')}"
            ),
            (
                "Quantidade noturna: "
                f"{self.quantidade.para_hhmm()} "
                f"({format(self.quantidade_horas_exatas, 'f')} horas)"
            ),
            (
                "Operação: valor-hora × percentual × "
                "quantidade de horas noturnas"
            ),
            (
                "Adicional noturno apurado: "
                f"{self.valor_total.moeda} "
                f"{format(self.valor_total.valor, 'f')}"
            ),
            f"Fundamento: {self.parametros.fundamento}",
            f"Fórmula: {self.formula_codigo}",
        )
