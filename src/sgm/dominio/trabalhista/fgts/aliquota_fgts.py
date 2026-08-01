from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class AliquotaFGTS:
    percentual: Decimal
    fundamento: str
    criterio_juridico_id: UUID | None = None
    descricao: str | None = None
    versao: int = 1
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.percentual, Decimal):
            raise TypeError("A alíquota do FGTS deve ser Decimal.")

        if not self.percentual.is_finite():
            raise ValueError("A alíquota do FGTS deve ser finita.")

        if self.percentual < 0:
            raise ValueError(
                "A alíquota do FGTS não pode ser negativa."
            )

        if self.percentual > 1:
            raise ValueError(
                "A alíquota do FGTS deve ser informada entre 0 e 1."
            )

        fundamento = self.fundamento.strip()
        object.__setattr__(self, "fundamento", fundamento)

        if not fundamento:
            raise ValueError(
                "O fundamento da alíquota do FGTS é obrigatório."
            )

        if self.versao < 1:
            raise ValueError(
                "A versão da alíquota deve ser igual ou superior a 1."
            )

        if self.descricao is not None:
            descricao = self.descricao.strip()
            object.__setattr__(
                self,
                "descricao",
                descricao or None,
            )

    @property
    def percentual_exibicao(self) -> Decimal:
        return self.percentual * Decimal("100")
