from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from sgm.dominio.juridico.enums import AcaoComando

@dataclass(slots=True)
class ComandoJudicial:
    acao: AcaoComando
    objeto: str
    descricao: str
    documento_id: str
    pagina: int | None = None
    periodo_inicio: date | None = None
    periodo_fim: date | None = None
    limitacao: str | None = None
    id: UUID = field(default_factory=uuid4)
    versao: int = 1

    def __post_init__(self) -> None:
        self.objeto = self.objeto.strip()
        self.descricao = self.descricao.strip()
        self.documento_id = self.documento_id.strip()
        if not self.objeto:
            raise ValueError("O objeto do comando é obrigatório.")
        if not self.descricao:
            raise ValueError("A descrição do comando é obrigatória.")
        if not self.documento_id:
            raise ValueError("O documento do comando é obrigatório.")
        if self.pagina is not None and self.pagina < 1:
            raise ValueError("A página deve ser positiva.")
        if self.periodo_inicio and self.periodo_fim and self.periodo_fim < self.periodo_inicio:
            raise ValueError("O fim do período não pode anteceder o início.")
