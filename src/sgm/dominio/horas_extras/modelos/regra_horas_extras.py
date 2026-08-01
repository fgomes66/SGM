from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sgm.dominio.jornada import Tempo


@dataclass(frozen=True, slots=True)
class RegraHorasExtras:
    limite_diario: Tempo
    limite_semanal: Tempo
    adicional_padrao: Decimal = Decimal("0.50")
    considerar_excedente_diario: bool = True
    considerar_excedente_semanal: bool = True

    def __post_init__(self) -> None:
        if self.limite_diario.minutos <= 0:
            raise ValueError("O limite diário deve ser maior que zero.")
        if self.limite_semanal.minutos <= 0:
            raise ValueError("O limite semanal deve ser maior que zero.")
        if not isinstance(self.adicional_padrao, Decimal):
            raise TypeError("O adicional deve ser Decimal.")
        if not self.adicional_padrao.is_finite():
            raise ValueError("O adicional deve ser finito.")
        if self.adicional_padrao < 0:
            raise ValueError("O adicional não pode ser negativo.")
        if not (
            self.considerar_excedente_diario
            or self.considerar_excedente_semanal
        ):
            raise ValueError(
                "Ao menos um critério de excedente deve estar ativo."
            )
