from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.financeiro import ValorMonetario


@dataclass(frozen=True, slots=True)
class LinhaTabelaFinanceira:
    chave: str
    descricao: str
    valor: ValorMonetario

    def __post_init__(self) -> None:
        chave = self.chave.strip()
        descricao = self.descricao.strip()
        object.__setattr__(self, "chave", chave)
        object.__setattr__(self, "descricao", descricao)

        if not chave:
            raise ValueError("A chave da linha é obrigatória.")

        if not descricao:
            raise ValueError("A descrição da linha é obrigatória.")
