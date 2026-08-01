from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True, slots=True)
class DadosCalculoFormulario:
    competencia: str = ""
    quantidade_horas: str = ""
    adicional_percentual: str = "50"
    fundamento: str = "Art. 7º, XVI, da Constituição Federal"

    def __post_init__(self) -> None:
        for campo in self.__dataclass_fields__:
            object.__setattr__(self, campo, getattr(self, campo).strip())

    @staticmethod
    def _decimal(texto: str, rotulo: str) -> Decimal:
        try:
            valor = Decimal(texto.replace(".", "").replace(",", "."))
        except InvalidOperation as erro:
            raise ValueError(f"Informe {rotulo} válido.") from erro
        if not valor.is_finite():
            raise ValueError(f"Informe {rotulo} finito.")
        return valor

    def valores(self) -> tuple[date, Decimal, Decimal, str]:
        try:
            competencia = date.fromisoformat(self.competencia)
        except ValueError as erro:
            raise ValueError(
                "Informe a competência no formato AAAA-MM-DD."
            ) from erro

        quantidade = self._decimal(
            self.quantidade_horas,
            "uma quantidade de horas",
        )
        adicional_exibicao = self._decimal(
            self.adicional_percentual,
            "um percentual de adicional",
        )
        adicional = adicional_exibicao / Decimal("100")

        if quantidade <= 0:
            raise ValueError(
                "A quantidade de horas deve ser maior que zero."
            )
        if adicional < 0:
            raise ValueError("O adicional não pode ser negativo.")
        if not self.fundamento:
            raise ValueError("Informe o fundamento do cálculo.")

        return competencia, quantidade, adicional, self.fundamento

    def validar(self) -> tuple[str, ...]:
        try:
            self.valores()
        except ValueError as erro:
            return (str(erro),)
        return ()
