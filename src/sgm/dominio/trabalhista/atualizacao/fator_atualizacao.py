from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.atualizacao.tipo_atualizacao import (
    TipoAtualizacao,
)


@dataclass(frozen=True, slots=True)
class FatorAtualizacao:
    tipo: TipoAtualizacao
    fator: Decimal
    data_inicial: date
    data_final: date
    fonte: str
    fundamento: str
    criterio_juridico_id: UUID | None = None
    indice_codigo: str | None = None
    versao_fonte: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.fator, Decimal):
            raise TypeError("O fator de atualização deve ser Decimal.")

        if not self.fator.is_finite():
            raise ValueError("O fator de atualização deve ser finito.")

        if self.fator < 0:
            raise ValueError(
                "O fator de atualização não pode ser negativo."
            )

        if self.data_final < self.data_inicial:
            raise ValueError(
                "A data final não pode ser anterior à data inicial."
            )

        fonte = self.fonte.strip()
        fundamento = self.fundamento.strip()
        object.__setattr__(self, "fonte", fonte)
        object.__setattr__(self, "fundamento", fundamento)

        if not fonte:
            raise ValueError(
                "A fonte do fator de atualização é obrigatória."
            )

        if not fundamento:
            raise ValueError(
                "O fundamento do fator de atualização é obrigatório."
            )

        if self.indice_codigo is not None:
            indice_codigo = self.indice_codigo.strip().upper()
            object.__setattr__(
                self,
                "indice_codigo",
                indice_codigo or None,
            )

        if self.versao_fonte is not None:
            versao_fonte = self.versao_fonte.strip()
            object.__setattr__(
                self,
                "versao_fonte",
                versao_fonte or None,
            )

    @property
    def percentual_equivalente(self) -> Decimal:
        return (self.fator - Decimal("1")) * Decimal("100")
