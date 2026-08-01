from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.relatorio.geracao.tipo_secao_relatorio import (
    TipoSecaoRelatorio,
)


@dataclass(frozen=True, slots=True)
class SecaoRelatorio:
    ordem: int
    tipo: TipoSecaoRelatorio
    titulo: str
    linhas: tuple[str, ...]
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        titulo = self.titulo.strip()
        linhas = tuple(
            linha.rstrip()
            for linha in self.linhas
            if linha.strip()
        )

        object.__setattr__(self, "titulo", titulo)
        object.__setattr__(self, "linhas", linhas)

        if self.ordem < 1:
            raise ValueError(
                "A ordem da seção deve ser igual ou superior a 1."
            )

        if not titulo:
            raise ValueError("O título da seção é obrigatório.")

        if not linhas:
            raise ValueError(
                "A seção deve possuir ao menos uma linha."
            )

    def como_texto(self) -> str:
        return "\n".join(
            (f"{self.ordem}. {self.titulo}", *self.linhas)
        )
