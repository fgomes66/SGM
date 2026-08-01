from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4


class NivelObservacaoTecnica(StrEnum):
    INFORMATIVA = "INFORMATIVA"
    ATENCAO = "ATENCAO"
    LIMITACAO = "LIMITACAO"


@dataclass(frozen=True, slots=True)
class ObservacaoTecnica:
    texto: str
    nivel: NivelObservacaoTecnica
    fundamento: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        texto = self.texto.strip()
        object.__setattr__(self, "texto", texto)

        if not texto:
            raise ValueError(
                "O texto da observação técnica é obrigatório."
            )

        if self.fundamento is not None:
            fundamento = self.fundamento.strip()
            object.__setattr__(
                self,
                "fundamento",
                fundamento or None,
            )
