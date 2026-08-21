from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from .sentenca import SentencaTrabalhista


@dataclass(slots=True)
class CasoLiquidacao:
    """Agregado de entrada para uma liquidação trabalhista."""

    referencia_processo: str
    sentenca: SentencaTrabalhista
    data_calculo: date
    observacoes: str = ""
    id: UUID = field(default_factory=uuid4)
    versao: int = 1

    def __post_init__(self) -> None:
        self.referencia_processo = self.referencia_processo.strip()
        self.observacoes = self.observacoes.strip()

        if not self.referencia_processo:
            raise ValueError("A referência do processo é obrigatória.")

        if self.versao < 1:
            raise ValueError("A versão deve ser igual ou superior a 1.")

    def atualizar_sentenca(
        self,
        sentenca: SentencaTrabalhista,
    ) -> None:
        if not isinstance(sentenca, SentencaTrabalhista):
            raise TypeError(
                "A sentença deve ser uma SentencaTrabalhista."
            )

        self.sentenca = sentenca
        self.versao += 1
