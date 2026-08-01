from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID, uuid4

@dataclass(slots=True)
class Evidencia:
    documento_id: str
    descricao: str
    pagina_inicial: int | None = None
    pagina_final: int | None = None
    trecho: str | None = None
    validada: bool = False
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.documento_id = self.documento_id.strip()
        self.descricao = self.descricao.strip()
        if not self.documento_id:
            raise ValueError("O documento da evidência é obrigatório.")
        if not self.descricao:
            raise ValueError("A descrição da evidência é obrigatória.")
        if self.pagina_inicial is not None and self.pagina_inicial < 1:
            raise ValueError("A página inicial deve ser positiva.")
        if (
            self.pagina_inicial is not None
            and self.pagina_final is not None
            and self.pagina_final < self.pagina_inicial
        ):
            raise ValueError("A página final não pode anteceder a inicial.")

    def validar(self) -> None:
        self.validada = True
