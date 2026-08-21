from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.trabalhista.atualizacao import (
    FatorAtualizacao,
)


@dataclass(frozen=True, slots=True)
class ParametrosAtualizacaoJudicial:
    """Fatores explícitos de atualização aplicáveis ao crédito judicial."""

    fator_correcao: FatorAtualizacao
    fator_juros: FatorAtualizacao
    observacoes: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "observacoes",
            self.observacoes.strip(),
        )
