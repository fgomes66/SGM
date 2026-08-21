from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ParametrosVerbaJudicial:
    """Parâmetros específicos determinados para uma verba judicial."""

    avos: int | None = None
    percentual: Decimal | None = None
    quantidade: Decimal | None = None
    dias_uteis: int | None = None
    dias_repouso: int | None = None
    dias_aviso: int | None = None
    dias_mes_calculo: int | None = None
    divisor: Decimal | None = None
    fundamento: str = ""
    observacoes: str = ""

    def __post_init__(self) -> None:
        if self.avos is not None:
            if not 0 <= self.avos <= 12:
                raise ValueError(
                    "Os avos devem estar entre 0 e 12."
                )

        for nome, valor in (
            ("percentual", self.percentual),
            ("quantidade", self.quantidade),
            ("divisor", self.divisor),
        ):
            if valor is not None:
                if not isinstance(valor, Decimal):
                    raise TypeError(
                        f"{nome} deve ser Decimal."
                    )
                if not valor.is_finite():
                    raise ValueError(
                        f"{nome} deve ser finito."
                    )
                if valor < 0:
                    raise ValueError(
                        f"{nome} não pode ser negativo."
                    )

        if self.dias_uteis is not None:
            if self.dias_uteis <= 0:
                raise ValueError(
                    "Dias úteis devem ser maiores que zero."
                )

        if self.dias_repouso is not None:
            if self.dias_repouso < 0:
                raise ValueError(
                    "Dias de repouso não podem ser negativos."
                )

        if self.dias_aviso is not None:
            if self.dias_aviso < 0:
                raise ValueError(
                    "Dias de aviso não podem ser negativos."
                )

        if self.dias_mes_calculo is not None:
            if self.dias_mes_calculo <= 0:
                raise ValueError(
                    "Dias do mês de cálculo devem ser maiores que zero."
                )

        object.__setattr__(
            self,
            "fundamento",
            self.fundamento.strip(),
        )
        object.__setattr__(
            self,
            "observacoes",
            self.observacoes.strip(),
        )
