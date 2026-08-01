from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.aviso_previo.parametros_aviso_previo import (
    ParametrosAvisoPrevio,
)
from sgm.dominio.trabalhista.dependencias import CodigoVerba
from sgm.dominio.trabalhista.incidencias import (
    ComposicaoBaseIncidencia,
    TipoBaseIncidencia,
)


@dataclass(frozen=True, slots=True)
class AvisoPrevioApurado:
    base: ComposicaoBaseIncidencia
    parametros: ParametrosAvisoPrevio
    valor: ValorMonetario
    formula_codigo: str = "FM-AVP-001"
    verba_destino: CodigoVerba = CodigoVerba.AVISO_PREVIO
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
                "O código da fórmula do aviso-prévio é obrigatório."
            )

        if (
            self.base.base_destino
            != TipoBaseIncidencia.AVISO_PREVIO
        ):
            raise ValueError(
                "O aviso-prévio exige composição destinada à sua base."
            )

        if self.valor.moeda != self.base.total.moeda:
            raise ValueError(
                "O aviso-prévio deve manter a moeda da base."
            )

    def memoria_resumida(self) -> tuple[str, ...]:
        linhas = [
            (
                "Base do aviso-prévio: "
                f"{self.base.total.moeda} "
                f"{format(self.base.total.valor, 'f')}"
            ),
            f"Tipo: {self.parametros.tipo.value}",
            f"Dias do aviso: {self.parametros.dias}",
            (
                "Dias do mês de cálculo: "
                f"{self.parametros.dias_mes_calculo}"
            ),
            (
                "Fator de dias: "
                f"{format(self.parametros.fator_dias, 'f')}"
            ),
            (
                "Operação: base do aviso × fator de dias"
            ),
            (
                "Aviso-prévio apurado: "
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
