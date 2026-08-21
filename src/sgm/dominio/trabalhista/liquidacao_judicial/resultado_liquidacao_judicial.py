from __future__ import annotations

from dataclasses import dataclass

from .resultado_item_liquidacao_judicial import (
    ResultadoItemLiquidacaoJudicial,
)


@dataclass(frozen=True, slots=True)
class ResultadoLiquidacaoJudicial:
    """Resultado seletivo da execução do título judicial."""

    referencia_processo: str
    itens: tuple[ResultadoItemLiquidacaoJudicial, ...]
    memoria: tuple[str, ...]

    def __post_init__(self) -> None:
        referencia = self.referencia_processo.strip()

        if not referencia:
            raise ValueError(
                "A referência do processo é obrigatória."
            )

        if not self.itens:
            raise ValueError(
                "A liquidação judicial deve possuir ao menos um resultado."
            )

        object.__setattr__(
            self,
            "referencia_processo",
            referencia,
        )

    @property
    def quantidade_itens(self) -> int:
        return len(self.itens)
