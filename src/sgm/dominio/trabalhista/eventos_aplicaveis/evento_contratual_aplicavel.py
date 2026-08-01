from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.temporal import (
    CompetenciaCalculo,
    TipoEventoContratual,
)


@dataclass(frozen=True, slots=True)
class EventoContratualAplicavel:
    competencia: CompetenciaCalculo
    tipo: TipoEventoContratual
    descricao: str
    fundamento: str
    novo_salario: Decimal | None = None
    novo_divisor: Decimal | None = None
    nova_jornada_semanal_minutos: int | None = None
    documento_id: str | None = None
    criterio_juridico_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        descricao = self.descricao.strip()
        fundamento = self.fundamento.strip()
        object.__setattr__(self, "descricao", descricao)
        object.__setattr__(self, "fundamento", fundamento)

        if not descricao:
            raise ValueError(
                "A descrição do evento aplicável é obrigatória."
            )

        if not fundamento:
            raise ValueError(
                "O fundamento do evento aplicável é obrigatório."
            )

        if self.documento_id is not None:
            documento_id = self.documento_id.strip()
            object.__setattr__(
                self,
                "documento_id",
                documento_id or None,
            )

        if self.tipo in (
            TipoEventoContratual.REAJUSTE,
            TipoEventoContratual.PROMOCAO,
        ):
            if not isinstance(self.novo_salario, Decimal):
                raise TypeError(
                    "Reajuste e promoção exigem novo salário Decimal."
                )
            if (
                not self.novo_salario.is_finite()
                or self.novo_salario <= 0
            ):
                raise ValueError(
                    "O novo salário deve ser finito e maior que zero."
                )

        if self.tipo == TipoEventoContratual.ALTERACAO_DIVISOR:
            if not isinstance(self.novo_divisor, Decimal):
                raise TypeError(
                    "A alteração de divisor exige Decimal."
                )
            if (
                not self.novo_divisor.is_finite()
                or self.novo_divisor <= 0
            ):
                raise ValueError(
                    "O novo divisor deve ser finito e maior que zero."
                )

        if self.tipo == TipoEventoContratual.ALTERACAO_JORNADA:
            if not isinstance(
                self.nova_jornada_semanal_minutos,
                int,
            ):
                raise TypeError(
                    "A nova jornada deve ser informada em minutos."
                )
            if self.nova_jornada_semanal_minutos <= 0:
                raise ValueError(
                    "A nova jornada deve ser maior que zero."
                )
