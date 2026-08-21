from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from .parametros_verba_judicial import ParametrosVerbaJudicial


@dataclass(frozen=True, slots=True)
class VerbaDeferida:
    """Representa uma verba reconhecida pelo título judicial."""

    codigo: str
    descricao: str
    fundamento: str = ""
    percentual: Decimal | None = None
    quantidade: Decimal | None = None
    observacoes: str = ""
    parametros: ParametrosVerbaJudicial = field(
        default_factory=ParametrosVerbaJudicial
    )

    def __post_init__(self) -> None:
        codigo = self.codigo.strip().upper()
        descricao = self.descricao.strip()

        if not codigo:
            raise ValueError(
                "O código da verba é obrigatório."
            )

        if not descricao:
            raise ValueError(
                "A descrição da verba é obrigatória."
            )

        if self.percentual is not None:
            if not isinstance(self.percentual, Decimal):
                raise TypeError(
                    "O percentual da verba deve ser Decimal."
                )
            if self.percentual < 0:
                raise ValueError(
                    "O percentual da verba não pode ser negativo."
                )

        if self.quantidade is not None:
            if not isinstance(self.quantidade, Decimal):
                raise TypeError(
                    "A quantidade da verba deve ser Decimal."
                )
            if self.quantidade < 0:
                raise ValueError(
                    "A quantidade da verba não pode ser negativa."
                )

        object.__setattr__(self, "codigo", codigo)
        object.__setattr__(self, "descricao", descricao)
        object.__setattr__(
            self,
            "fundamento",
            self.fundamento.strip(),
        )
        object.__setattr__(
            self,
            "observacoes",
            self.observacoes.strip(),
        )
