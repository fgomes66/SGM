from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.atualizacao import (
    ResultadoAtualizacaoJuros,
)

from .resultado_consolidado_judicial import (
    ResultadoConsolidadoJudicial,
)


@dataclass(frozen=True, slots=True)
class ResultadoAtualizadoJudicial:
    """Resultado consolidado após correção monetária e juros."""

    consolidado: ResultadoConsolidadoJudicial
    atualizacao: ResultadoAtualizacaoJuros
    valor_final: ValorMonetario
    memoria: tuple[str, ...]
    versao_motor: str = "0.9.7-JA"

    def __post_init__(self) -> None:
        if self.valor_final != self.atualizacao.valor_final:
            raise ValueError(
                "O valor final deve coincidir com o resultado da atualização."
            )

        if not self.memoria:
            raise ValueError(
                "A memória da atualização judicial é obrigatória."
            )
