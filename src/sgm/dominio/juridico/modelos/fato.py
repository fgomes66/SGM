from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from sgm.dominio.juridico.enums import TipoFato

@dataclass(slots=True)
class Fato:
    descricao: str
    tipo: TipoFato
    data_inicio: date | None = None
    data_fim: date | None = None
    fonte: str | None = None
    id: UUID = field(default_factory=uuid4)
    versao: int = 1

    def __post_init__(self) -> None:
        self.descricao = self.descricao.strip()
        if not self.descricao:
            raise ValueError("A descrição do fato é obrigatória.")
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValueError("O fim do fato não pode anteceder o início.")
