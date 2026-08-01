from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.aviso_previo.tipo_aviso_previo import (
    TipoAvisoPrevio,
)


@dataclass(frozen=True, slots=True)
class ParametrosAvisoPrevio:
    tipo: TipoAvisoPrevio
    dias: int
    dias_mes_calculo: int
    fundamento: str
    criterio_juridico_id: UUID | None = None
    observacao: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.dias, int):
            raise TypeError(
                "A quantidade de dias do aviso deve ser inteira."
            )

        if not isinstance(self.dias_mes_calculo, int):
            raise TypeError(
                "Os dias do mês de cálculo devem ser inteiros."
            )

        if self.dias < 0:
            raise ValueError(
                "A quantidade de dias do aviso não pode ser negativa."
            )

        if self.dias_mes_calculo <= 0:
            raise ValueError(
                "Os dias do mês de cálculo devem ser maiores que zero."
            )

        fundamento = self.fundamento.strip()
        object.__setattr__(self, "fundamento", fundamento)

        if not fundamento:
            raise ValueError(
                "O fundamento dos parâmetros do aviso é obrigatório."
            )

        if self.observacao is not None:
            observacao = self.observacao.strip()
            object.__setattr__(
                self,
                "observacao",
                observacao or None,
            )

    @property
    def fator_dias(self) -> Decimal:
        return (
            Decimal(self.dias)
            / Decimal(self.dias_mes_calculo)
        )
