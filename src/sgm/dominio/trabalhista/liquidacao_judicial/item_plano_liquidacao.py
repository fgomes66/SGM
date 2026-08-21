from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class StatusItemLiquidacao(StrEnum):
    PENDENTE = "PENDENTE"
    APTO = "APTO"
    BLOQUEADO = "BLOQUEADO"
    EXECUTADO = "EXECUTADO"
    ERRO = "ERRO"


@dataclass(frozen=True, slots=True)
class ItemPlanoLiquidacao:
    codigo_verba: str
    descricao: str
    fundamento: str
    status: StatusItemLiquidacao = StatusItemLiquidacao.PENDENTE
    observacoes: str = ""

    def __post_init__(self) -> None:
        codigo = self.codigo_verba.strip().upper()
        descricao = self.descricao.strip()
        fundamento = self.fundamento.strip()
        observacoes = self.observacoes.strip()

        if not codigo:
            raise ValueError(
                "O código da verba do plano é obrigatório."
            )

        if not descricao:
            raise ValueError(
                "A descrição do item do plano é obrigatória."
            )

        object.__setattr__(self, "codigo_verba", codigo)
        object.__setattr__(self, "descricao", descricao)
        object.__setattr__(self, "fundamento", fundamento)
        object.__setattr__(self, "observacoes", observacoes)
