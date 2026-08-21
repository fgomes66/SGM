from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .entrada_caso_trabalhista import EntradaCasoTrabalhista
from .item_plano_liquidacao import ItemPlanoLiquidacao
from .resultado_validacao import ResultadoValidacaoCaso


@dataclass(frozen=True, slots=True)
class PlanoLiquidacaoJudicial:
    referencia_processo: str
    entrada: EntradaCasoTrabalhista
    validacao: ResultadoValidacaoCaso
    itens: tuple[ItemPlanoLiquidacao, ...]
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        referencia = self.referencia_processo.strip()

        if not referencia:
            raise ValueError(
                "A referência do processo é obrigatória no plano."
            )

        object.__setattr__(
            self,
            "referencia_processo",
            referencia,
        )

    @property
    def apto_para_execucao(self) -> bool:
        return self.validacao.valido and bool(self.itens)

    @property
    def quantidade_itens(self) -> int:
        return len(self.itens)
