from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum


class TipoContratoTrabalho(StrEnum):
    INDETERMINADO = "INDETERMINADO"
    DETERMINADO = "DETERMINADO"
    EXPERIENCIA = "EXPERIENCIA"
    INTERMITENTE = "INTERMITENTE"
    TEMPORARIO = "TEMPORARIO"

    @property
    def titulo(self) -> str:
        return {
            self.INDETERMINADO: "Prazo indeterminado",
            self.DETERMINADO: "Prazo determinado",
            self.EXPERIENCIA: "Experiência",
            self.INTERMITENTE: "Intermitente",
            self.TEMPORARIO: "Temporário",
        }[self]


@dataclass(frozen=True, slots=True)
class ContratoTrabalho:
    data_admissao: date
    data_desligamento: date | None
    tipo_contrato: TipoContratoTrabalho
    cargo: str
    funcao: str
    cbo: str | None
    salario_inicial: Decimal
    jornada_semanal_horas: Decimal
    divisor_jornada: Decimal
    motivo_desligamento: str | None = None
    sindicato: str | None = None
    norma_coletiva: str | None = None
    observacoes: str | None = None

    def __post_init__(self) -> None:
        if self.data_desligamento and self.data_desligamento < self.data_admissao:
            raise ValueError("A data de desligamento não pode ser anterior à admissão.")
        if not isinstance(self.salario_inicial, Decimal) or self.salario_inicial <= 0:
            raise ValueError("O salário inicial deve ser maior que zero.")
        if not isinstance(self.jornada_semanal_horas, Decimal) or self.jornada_semanal_horas <= 0:
            raise ValueError("A jornada semanal deve ser maior que zero.")
        if self.jornada_semanal_horas > Decimal('60'):
            raise ValueError("A jornada semanal não pode superar 60 horas.")
        if not isinstance(self.divisor_jornada, Decimal) or self.divisor_jornada <= 0:
            raise ValueError("O divisor da jornada deve ser maior que zero.")
        for campo in ('cargo', 'funcao'):
            valor=getattr(self,campo).strip(); object.__setattr__(self,campo,valor)
            if not valor: raise ValueError(f"O campo {campo} é obrigatório.")
        for campo in ('cbo','motivo_desligamento','sindicato','norma_coletiva','observacoes'):
            valor=getattr(self,campo)
            if valor is not None:
                valor=valor.strip() or None; object.__setattr__(self,campo,valor)
