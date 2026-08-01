from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sgm.dominio.juridico.enums import StatusCriterio

@dataclass(slots=True)
class CriterioJuridico:
    codigo: str
    verba_codigo: str
    descricao: str
    comando_judicial_id: UUID
    status: StatusCriterio = StatusCriterio.RASCUNHO
    periodo_inicio: date | None = None
    periodo_fim: date | None = None
    base_calculo: str | None = None
    percentual: Decimal | None = None
    divisor: Decimal | None = None
    reflexos: tuple[str, ...] = ()
    limitacoes: tuple[str, ...] = ()
    homologado_por: str | None = None
    homologado_em: datetime | None = None
    id: UUID = field(default_factory=uuid4)
    versao: int = 1

    def __post_init__(self) -> None:
        self.codigo = self.codigo.strip()
        self.verba_codigo = self.verba_codigo.strip()
        self.descricao = self.descricao.strip()
        if not self.codigo:
            raise ValueError("O código do critério é obrigatório.")
        if not self.verba_codigo:
            raise ValueError("A verba do critério é obrigatória.")
        if not self.descricao:
            raise ValueError("A descrição do critério é obrigatória.")
        if self.percentual is not None and not isinstance(self.percentual, Decimal):
            raise TypeError("O percentual deve ser Decimal.")
        if self.divisor is not None:
            if not isinstance(self.divisor, Decimal):
                raise TypeError("O divisor deve ser Decimal.")
            if self.divisor <= 0:
                raise ValueError("O divisor deve ser maior que zero.")
        if self.periodo_inicio and self.periodo_fim and self.periodo_fim < self.periodo_inicio:
            raise ValueError("O fim do critério não pode anteceder o início.")

    @property
    def esta_homologado(self) -> bool:
        return self.status == StatusCriterio.HOMOLOGADO

    def homologar(self, responsavel: str, momento: datetime | None = None) -> None:
        responsavel = responsavel.strip()
        if not responsavel:
            raise ValueError("O responsável pela homologação é obrigatório.")
        if self.status in {StatusCriterio.SUSPENSO, StatusCriterio.SUBSTITUIDO}:
            raise ValueError("Critério suspenso ou substituído não pode ser homologado.")
        self.status = StatusCriterio.HOMOLOGADO
        self.homologado_por = responsavel
        self.homologado_em = momento or datetime.now().astimezone()
        self.versao += 1

    def garantir_apto_para_calculo(self) -> None:
        if not self.esta_homologado:
            raise ValueError("O critério precisa estar homologado antes do cálculo.")
