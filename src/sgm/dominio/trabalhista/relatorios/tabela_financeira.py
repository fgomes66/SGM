from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.relatorios.linha_tabela_financeira import (
    LinhaTabelaFinanceira,
)


@dataclass(frozen=True, slots=True)
class TabelaFinanceira:
    titulo: str
    colunas: tuple[str, ...]
    linhas: tuple[LinhaTabelaFinanceira, ...]
    total: ValorMonetario
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        titulo = self.titulo.strip()
        object.__setattr__(self, "titulo", titulo)

        if not titulo:
            raise ValueError("O título da tabela é obrigatório.")

        if not self.colunas:
            raise ValueError("A tabela deve possuir colunas.")

        if not self.linhas:
            raise ValueError("A tabela deve possuir linhas.")

        moedas = {
            linha.valor.moeda for linha in self.linhas
        } | {self.total.moeda}

        if len(moedas) != 1:
            raise ValueError(
                "As linhas e o total devem usar a mesma moeda."
            )

        soma = self.linhas[0].valor
        for linha in self.linhas[1:]:
            soma = soma.somar(linha.valor)
        soma = soma.arredondar_centavos()

        if soma.valor != self.total.valor:
            raise ValueError(
                "O total da tabela deve corresponder à soma das linhas."
            )
