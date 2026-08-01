from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.dependencias import CodigoVerba
from sgm.dominio.trabalhista.fgts.aliquota_fgts import AliquotaFGTS
from sgm.dominio.trabalhista.incidencias import (
    ComposicaoBaseIncidencia,
    TipoBaseIncidencia,
)


@dataclass(frozen=True, slots=True)
class FGTSApurado:
    base: ComposicaoBaseIncidencia
    aliquota: AliquotaFGTS
    valor: ValorMonetario
    formula_codigo: str = "FM-FGTS-001"
    verba_destino: CodigoVerba = CodigoVerba.FGTS
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
                "O código da fórmula do FGTS é obrigatório."
            )

        if self.base.base_destino != TipoBaseIncidencia.FGTS:
            raise ValueError(
                "O FGTS exige uma composição destinada à base FGTS."
            )

        if self.valor.moeda != self.base.total.moeda:
            raise ValueError(
                "O FGTS deve manter a moeda da base de incidência."
            )

    def memoria_resumida(self) -> tuple[str, ...]:
        linhas = [
            (
                "Base do FGTS: "
                f"{self.base.total.moeda} "
                f"{format(self.base.total.valor, 'f')}"
            ),
            (
                "Alíquota: "
                f"{format(self.aliquota.percentual_exibicao, 'f')}%"
            ),
            (
                "Operação: base do FGTS × alíquota"
            ),
            (
                "FGTS apurado: "
                f"{self.valor.moeda} "
                f"{format(self.valor.valor, 'f')}"
            ),
            f"Fórmula: {self.formula_codigo}",
            (
                "Fundamento da alíquota: "
                f"{self.aliquota.fundamento}"
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
