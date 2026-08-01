from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class TipoOperacaoFinanceira(StrEnum):
    CRIACAO = "CRIACAO"
    SOMA = "SOMA"
    SUBTRACAO = "SUBTRACAO"
    MULTIPLICACAO = "MULTIPLICACAO"
    DIVISAO = "DIVISAO"
    APLICACAO_PERCENTUAL = "APLICACAO_PERCENTUAL"
    ACRESCIMO_PERCENTUAL = "ACRESCIMO_PERCENTUAL"
    ARREDONDAMENTO = "ARREDONDAMENTO"
    NEGACAO = "NEGACAO"
    VALOR_ABSOLUTO = "VALOR_ABSOLUTO"


@dataclass(frozen=True, slots=True)
class OperacaoFinanceira:
    tipo: TipoOperacaoFinanceira
    descricao: str
    operandos: tuple[str, ...]
    resultado: str
    executada_em: datetime
    id: UUID = uuid4()

    def __post_init__(self) -> None:
        descricao = self.descricao.strip()
        object.__setattr__(self, "descricao", descricao)
        if not descricao:
            raise ValueError("A descrição da operação é obrigatória.")
