from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.financeiro import ValorMonetario

from .resultado_liquidacao_judicial import ResultadoLiquidacaoJudicial


@dataclass(frozen=True, slots=True)
class ResultadoConsolidadoJudicial:
    """
    Resultado financeiro consolidado de uma liquidação judicial.

    Consolida verbas já apuradas sem recalcular os motores individuais.
    """

    referencia_processo: str
    resultado_origem: ResultadoLiquidacaoJudicial
    subtotal: ValorMonetario
    memoria: tuple[str, ...]
    versao_motor: str = "0.9.7-JC"

    def __post_init__(self) -> None:
        referencia = self.referencia_processo.strip()

        if not referencia:
            raise ValueError(
                "A referência do processo é obrigatória."
            )

        if not self.memoria:
            raise ValueError(
                "A memória consolidada é obrigatória."
            )

        object.__setattr__(
            self,
            "referencia_processo",
            referencia,
        )

    @property
    def quantidade_itens(self) -> int:
        return self.resultado_origem.quantidade_itens
