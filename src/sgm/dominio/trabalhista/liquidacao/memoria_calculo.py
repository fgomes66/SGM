from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class MemoriaCalculo:
    titulo: str
    linhas: tuple[str, ...]
    lema: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        titulo = self.titulo.strip()
        lema = self.lema.strip()
        object.__setattr__(self, "titulo", titulo)
        object.__setattr__(self, "lema", lema)

        if not titulo:
            raise ValueError(
                "O título da memória é obrigatório."
            )

        if not self.linhas:
            raise ValueError(
                "A memória deve conter ao menos uma linha."
            )

        if not lema:
            raise ValueError(
                "O lema da memória é obrigatório."
            )

    def como_texto(self) -> str:
        corpo = "\n".join(self.linhas)
        return f"{self.titulo}\n\n{corpo}\n\n{self.lema}"
