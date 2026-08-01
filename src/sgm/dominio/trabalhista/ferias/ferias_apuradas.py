from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.dependencias import CodigoVerba
from sgm.dominio.trabalhista.ferias.parametros_ferias import (
    ParametrosFerias,
)
from sgm.dominio.trabalhista.incidencias import (
    ComposicaoBaseIncidencia,
    TipoBaseIncidencia,
)


@dataclass(frozen=True, slots=True)
class FeriasApuradas:
    base: ComposicaoBaseIncidencia
    parametros: ParametrosFerias
    valor_ferias: ValorMonetario
    valor_terco: ValorMonetario
    valor_total: ValorMonetario
    formula_ferias_codigo: str = "FM-FER-001"
    formula_terco_codigo: str = "FM-FER-002"
    verba_destino: CodigoVerba = CodigoVerba.FERIAS
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        formula_ferias = self.formula_ferias_codigo.strip().upper()
        formula_terco = self.formula_terco_codigo.strip().upper()

        object.__setattr__(
            self,
            "formula_ferias_codigo",
            formula_ferias,
        )
        object.__setattr__(
            self,
            "formula_terco_codigo",
            formula_terco,
        )

        if not formula_ferias or not formula_terco:
            raise ValueError(
                "Os códigos das fórmulas de férias são obrigatórios."
            )

        if self.base.base_destino != TipoBaseIncidencia.FERIAS:
            raise ValueError(
                "As férias exigem uma composição destinada à base FÉRIAS."
            )

        moedas = {
            self.base.total.moeda,
            self.valor_ferias.moeda,
            self.valor_terco.moeda,
            self.valor_total.moeda,
        }
        if len(moedas) != 1:
            raise ValueError(
                "Todos os valores de férias devem usar a mesma moeda."
            )

    def memoria_resumida(self) -> tuple[str, ...]:
        linhas = [
            (
                "Base de férias: "
                f"{self.base.total.moeda} "
                f"{format(self.base.total.valor, 'f')}"
            ),
            f"Avos: {self.parametros.avos}/12",
            (
                "Fator de avos: "
                f"{format(self.parametros.fator_avos, 'f')}"
            ),
            (
                "Férias apuradas: "
                f"{self.valor_ferias.moeda} "
                f"{format(self.valor_ferias.valor, 'f')}"
            ),
            (
                "Percentual do terço: "
                f"{format(self.parametros.percentual_terco_exibicao, 'f')}%"
            ),
            (
                "Terço constitucional: "
                f"{self.valor_terco.moeda} "
                f"{format(self.valor_terco.valor, 'f')}"
            ),
            (
                "Total de férias: "
                f"{self.valor_total.moeda} "
                f"{format(self.valor_total.valor, 'f')}"
            ),
            f"Fórmula férias: {self.formula_ferias_codigo}",
            f"Fórmula terço: {self.formula_terco_codigo}",
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
