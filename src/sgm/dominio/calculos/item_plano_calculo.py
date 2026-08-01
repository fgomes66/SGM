from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sgm.dominio.calculos.enums import NaturezaVerba


@dataclass(frozen=True, slots=True)
class ItemPlanoCalculo:
    codigo: str
    verba_codigo: str
    criterio_juridico_id: UUID
    natureza: NaturezaVerba
    descricao: str
    periodo_inicio: date | None = None
    periodo_fim: date | None = None
    base_calculo: str | None = None
    percentual: Decimal | None = None
    divisor: Decimal | None = None
    reflexos: tuple[str, ...] = ()
    incidencias: tuple[str, ...] = ()
    deducoes: tuple[str, ...] = ()
    observacoes: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        codigo = self.codigo.strip()
        verba_codigo = self.verba_codigo.strip()
        descricao = self.descricao.strip()

        object.__setattr__(self, "codigo", codigo)
        object.__setattr__(self, "verba_codigo", verba_codigo)
        object.__setattr__(self, "descricao", descricao)

        if not codigo:
            raise ValueError("O código do item é obrigatório.")
        if not verba_codigo:
            raise ValueError("O código da verba é obrigatório.")
        if not descricao:
            raise ValueError("A descrição do item é obrigatória.")

        if (
            self.periodo_inicio is not None
            and self.periodo_fim is not None
            and self.periodo_fim < self.periodo_inicio
        ):
            raise ValueError("O fim do período não pode anteceder o início.")

        if self.percentual is not None:
            if not isinstance(self.percentual, Decimal):
                raise TypeError("O percentual deve ser Decimal.")
            if not self.percentual.is_finite():
                raise ValueError("O percentual deve ser finito.")

        if self.divisor is not None:
            if not isinstance(self.divisor, Decimal):
                raise TypeError("O divisor deve ser Decimal.")
            if not self.divisor.is_finite() or self.divisor <= 0:
                raise ValueError("O divisor deve ser finito e maior que zero.")
