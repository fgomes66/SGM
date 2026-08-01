from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping
from uuid import UUID, uuid4


class TipoEventoDesktop(StrEnum):
    ALTERACAO_SALARIAL = "ALTERACAO_SALARIAL"
    PROMOCAO = "PROMOCAO"
    ALTERACAO_FUNCAO = "ALTERACAO_FUNCAO"
    ALTERACAO_JORNADA = "ALTERACAO_JORNADA"
    ALTERACAO_DIVISOR = "ALTERACAO_DIVISOR"
    FERIAS = "FERIAS"
    AFASTAMENTO = "AFASTAMENTO"
    RETORNO = "RETORNO"
    SUSPENSAO = "SUSPENSAO"
    ESTABILIDADE = "ESTABILIDADE"
    RESCISAO = "RESCISAO"
    OUTRO = "OUTRO"

    @property
    def titulo(self) -> str:
        return {
            TipoEventoDesktop.ALTERACAO_SALARIAL: "Alteração salarial",
            TipoEventoDesktop.PROMOCAO: "Promoção",
            TipoEventoDesktop.ALTERACAO_FUNCAO: "Alteração de função",
            TipoEventoDesktop.ALTERACAO_JORNADA: "Alteração de jornada",
            TipoEventoDesktop.ALTERACAO_DIVISOR: "Alteração de divisor",
            TipoEventoDesktop.FERIAS: "Férias",
            TipoEventoDesktop.AFASTAMENTO: "Afastamento",
            TipoEventoDesktop.RETORNO: "Retorno",
            TipoEventoDesktop.SUSPENSAO: "Suspensão",
            TipoEventoDesktop.ESTABILIDADE: "Estabilidade",
            TipoEventoDesktop.RESCISAO: "Rescisão",
            TipoEventoDesktop.OUTRO: "Outro",
        }[self]


@dataclass(frozen=True, slots=True)
class EventoContratualDesktop:
    tipo: TipoEventoDesktop
    data_inicio: date
    descricao: str
    fundamento: str
    data_fim: date | None = None
    valor: Decimal | None = None
    documento: str | None = None
    dados: Mapping[str, str] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        descricao = self.descricao.strip()
        fundamento = self.fundamento.strip()
        documento = self.documento.strip() if self.documento else None
        dados = {
            str(chave).strip(): str(valor).strip()
            for chave, valor in dict(self.dados).items()
            if str(chave).strip() and str(valor).strip()
        }

        object.__setattr__(self, "descricao", descricao)
        object.__setattr__(self, "fundamento", fundamento)
        object.__setattr__(self, "documento", documento or None)
        object.__setattr__(self, "dados", MappingProxyType(dados))

        if not isinstance(self.tipo, TipoEventoDesktop):
            raise TypeError("O tipo do evento é inválido.")
        if not descricao:
            raise ValueError("A descrição do evento é obrigatória.")
        if not fundamento:
            raise ValueError("O fundamento ou motivo é obrigatório.")
        if self.data_fim is not None and self.data_fim < self.data_inicio:
            raise ValueError("A data final não pode anteceder a data inicial.")
        if self.valor is not None:
            if not isinstance(self.valor, Decimal):
                raise TypeError("O valor do evento deve ser Decimal.")
            if not self.valor.is_finite() or self.valor <= 0:
                raise ValueError("O valor do evento deve ser maior que zero.")

        if self.tipo == TipoEventoDesktop.ALTERACAO_SALARIAL and self.valor is None:
            raise ValueError("A alteração salarial exige o novo salário.")
        if self.tipo in (
            TipoEventoDesktop.FERIAS,
            TipoEventoDesktop.AFASTAMENTO,
            TipoEventoDesktop.SUSPENSAO,
            TipoEventoDesktop.ESTABILIDADE,
        ) and self.data_fim is None:
            raise ValueError(f"{self.tipo.titulo} exige data final.")

    @property
    def chave_ordenacao(self) -> tuple[date, str, str]:
        return self.data_inicio, self.tipo.value, str(self.id)
