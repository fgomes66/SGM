from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.dependencias import CodigoVerba
from sgm.dominio.trabalhista.dsr.parametros_dsr import ParametrosDSR
from sgm.dominio.trabalhista.horas_extras_financeiras import (
    HoraExtraFinanceira,
)


@dataclass(frozen=True, slots=True)
class ReflexoDSR:
    origem: HoraExtraFinanceira
    parametros: ParametrosDSR
    valor: ValorMonetario
    formula_codigo: str = "FM-DSR-001"
    verba_origem: CodigoVerba = CodigoVerba.HORA_EXTRA
    verba_destino: CodigoVerba = CodigoVerba.DSR
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
                "O código da fórmula de DSR é obrigatório."
            )

        if self.valor.moeda != self.origem.valor_total.moeda:
            raise ValueError(
                "O reflexo em DSR deve manter a moeda da verba-base."
            )

    def memoria_resumida(self) -> tuple[str, ...]:
        return (
            (
                "Base de horas extras: "
                f"{self.origem.valor_total.moeda} "
                f"{format(self.origem.valor_total.valor, 'f')}"
            ),
            f"Dias úteis: {self.parametros.dias_uteis}",
            f"Dias de repouso: {self.parametros.dias_repouso}",
            (
                "Fator: "
                f"{format(self.parametros.fator, 'f')}"
            ),
            (
                "Operação: base ÷ dias úteis × dias de repouso"
            ),
            (
                "Reflexo em DSR: "
                f"{self.valor.moeda} "
                f"{format(self.valor.valor, 'f')}"
            ),
            f"Fórmula: {self.formula_codigo}",
        )
