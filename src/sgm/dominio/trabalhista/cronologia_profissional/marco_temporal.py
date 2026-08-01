from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.cronologia_profissional.tipo_marco_temporal import (
    TipoMarcoTemporal,
)
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


@dataclass(frozen=True, slots=True)
class MarcoTemporal:
    competencia: CompetenciaCalculo
    tipo: TipoMarcoTemporal
    titulo: str
    descricao: str
    fundamento: str
    ordem_na_competencia: int = 1
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        titulo = self.titulo.strip()
        descricao = self.descricao.strip()
        fundamento = self.fundamento.strip()

        object.__setattr__(self, "titulo", titulo)
        object.__setattr__(self, "descricao", descricao)
        object.__setattr__(self, "fundamento", fundamento)

        if not titulo:
            raise ValueError("O título do marco temporal é obrigatório.")

        if not descricao:
            raise ValueError(
                "A descrição do marco temporal é obrigatória."
            )

        if not fundamento:
            raise ValueError(
                "O fundamento do marco temporal é obrigatório."
            )

        if self.ordem_na_competencia < 1:
            raise ValueError(
                "A ordem do marco deve ser igual ou superior a 1."
            )
