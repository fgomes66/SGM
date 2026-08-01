from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.dependencias import CodigoVerba
from sgm.dominio.trabalhista.demonstrativos.natureza_financeira import (
    NaturezaFinanceira,
)


@dataclass(frozen=True, slots=True)
class ResumoVerba:
    codigo: CodigoVerba
    descricao: str
    natureza: NaturezaFinanceira
    valor: ValorMonetario
    quantidade_competencias: int

    def __post_init__(self) -> None:
        descricao = self.descricao.strip()
        object.__setattr__(self, "descricao", descricao)

        if not descricao:
            raise ValueError(
                "A descrição do resumo por verba é obrigatória."
            )

        if self.quantidade_competencias < 1:
            raise ValueError(
                "A quantidade de competências deve ser positiva."
            )
