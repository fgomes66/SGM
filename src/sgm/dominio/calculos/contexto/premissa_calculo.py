from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.calculos.contexto.enums import GrauConfianca


@dataclass(frozen=True, slots=True)
class PremissaCalculo:
    codigo: str
    descricao: str
    valor_declarado: str
    grau_confianca: GrauConfianca
    origem: str | None = None
    fato_id: UUID | None = None
    evidencia_id: UUID | None = None
    requer_confirmacao: bool = True
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        codigo = self.codigo.strip()
        descricao = self.descricao.strip()
        valor_declarado = self.valor_declarado.strip()

        object.__setattr__(self, "codigo", codigo)
        object.__setattr__(self, "descricao", descricao)
        object.__setattr__(self, "valor_declarado", valor_declarado)

        if not codigo:
            raise ValueError("O código da premissa é obrigatório.")
        if not descricao:
            raise ValueError("A descrição da premissa é obrigatória.")
        if not valor_declarado:
            raise ValueError("O valor declarado da premissa é obrigatório.")
