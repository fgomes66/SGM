from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.juridico.enums import StatusPedido

@dataclass(slots=True)
class Pedido:
    codigo: str
    descricao_original: str
    status: StatusPedido = StatusPedido.IDENTIFICADO
    causa_pedir: str | None = None
    verba_codigo: str | None = None
    id: UUID = field(default_factory=uuid4)
    versao: int = 1

    def __post_init__(self) -> None:
        self.codigo = self.codigo.strip()
        self.descricao_original = self.descricao_original.strip()
        if not self.codigo:
            raise ValueError("O código do pedido é obrigatório.")
        if not self.descricao_original:
            raise ValueError("A descrição do pedido é obrigatória.")

    def alterar_status(self, novo_status: StatusPedido) -> None:
        if novo_status != self.status:
            self.status = novo_status
            self.versao += 1
