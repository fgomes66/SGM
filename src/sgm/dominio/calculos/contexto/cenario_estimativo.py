from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.calculos.contexto.enums import TipoCenario
from sgm.dominio.calculos.contexto.premissa_calculo import PremissaCalculo


@dataclass(slots=True)
class CenarioEstimativo:
    nome: str
    tipo: TipoCenario
    premissas: list[PremissaCalculo] = field(default_factory=list)
    observacoes: str | None = None
    id: UUID = field(default_factory=uuid4)
    versao: int = 1

    def __post_init__(self) -> None:
        self.nome = self.nome.strip()
        if not self.nome:
            raise ValueError("O nome do cenário é obrigatório.")

    def adicionar_premissa(self, premissa: PremissaCalculo) -> None:
        if any(item.codigo == premissa.codigo for item in self.premissas):
            raise ValueError(
                f"Já existe premissa com o código {premissa.codigo}."
            )
        self.premissas.append(premissa)
        self.versao += 1

    def garantir_apto(self) -> None:
        if not self.premissas:
            raise ValueError(
                "O cenário estimativo precisa possuir ao menos uma premissa."
            )
