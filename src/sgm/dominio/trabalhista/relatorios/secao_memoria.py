from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.relatorios.item_memoria import ItemMemoria
from sgm.dominio.trabalhista.relatorios.tabela_financeira import (
    TabelaFinanceira,
)
from sgm.dominio.trabalhista.relatorios.tipo_secao_memoria import (
    TipoSecaoMemoria,
)


@dataclass(frozen=True, slots=True)
class SecaoMemoria:
    ordem: int
    tipo: TipoSecaoMemoria
    titulo: str
    itens: tuple[ItemMemoria, ...] = ()
    tabelas: tuple[TabelaFinanceira, ...] = ()
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        titulo = self.titulo.strip()
        object.__setattr__(self, "titulo", titulo)

        if self.ordem < 1:
            raise ValueError(
                "A ordem da seção deve ser igual ou superior a 1."
            )

        if not titulo:
            raise ValueError("O título da seção é obrigatório.")

        if not self.itens and not self.tabelas:
            raise ValueError(
                "A seção deve conter itens ou tabelas."
            )
