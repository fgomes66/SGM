from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.dependencias import CodigoVerba
from sgm.dominio.trabalhista.decimo_terceiro.parametros_decimo_terceiro import (
    ParametrosDecimoTerceiro,
)
from sgm.dominio.trabalhista.incidencias import (
    ComposicaoBaseIncidencia,
    TipoBaseIncidencia,
)


@dataclass(frozen=True, slots=True)
class DecimoTerceiroApurado:
    base: ComposicaoBaseIncidencia
    parametros: ParametrosDecimoTerceiro
    valor: ValorMonetario
    formula_codigo: str = "FM-13-001"
    verba_destino: CodigoVerba = CodigoVerba.DECIMO_TERCEIRO
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
                "O código da fórmula do 13º é obrigatório."
            )

        if (
            self.base.base_destino
            != TipoBaseIncidencia.DECIMO_TERCEIRO
        ):
            raise ValueError(
                "O 13º exige composição destinada à base 13º."
            )

        if self.valor.moeda != self.base.total.moeda:
            raise ValueError(
                "O 13º deve manter a moeda da base de incidência."
            )

    def memoria_resumida(self) -> tuple[str, ...]:
        linhas = [
            (
                "Base do 13º: "
                f"{self.base.total.moeda} "
                f"{format(self.base.total.valor, 'f')}"
            ),
            f"Avos: {self.parametros.avos}/12",
            (
                "Fator de avos: "
                f"{format(self.parametros.fator_avos, 'f')}"
            ),
            (
                "Operação: base do 13º × fator de avos"
            ),
            (
                "13º apurado: "
                f"{self.valor.moeda} "
                f"{format(self.valor.valor, 'f')}"
            ),
            f"Fórmula: {self.formula_codigo}",
            (
                "Fundamento: "
                f"{self.parametros.fundamento}"
            ),
        ]

        for parcela in self.base.parcelas_incluidas:
            linhas.append(
                "PARCELA INCLUÍDA "
                f"{parcela.verba.value}: "
                f"{parcela.valor.moeda} "
                f"{format(parcela.valor.valor, 'f')}"
            )

        for parcela in self.base.parcelas_excluidas:
            linhas.append(
                "PARCELA EXCLUÍDA "
                f"{parcela.verba.value}: "
                f"{parcela.regra.fundamento}"
            )

        return tuple(linhas)
