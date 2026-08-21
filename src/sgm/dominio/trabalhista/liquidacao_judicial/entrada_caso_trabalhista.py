from __future__ import annotations

from dataclasses import dataclass, field

from .dados_contrato_liquidacao import DadosContratoLiquidacao
from .parametros_liquidacao import ParametrosLiquidacao
from .sentenca import SentencaTrabalhista


@dataclass(frozen=True, slots=True)
class EntradaCasoTrabalhista:
    """Entrada estruturada e validável de um caso trabalhista."""

    referencia_processo: str
    contrato: DadosContratoLiquidacao
    sentenca: SentencaTrabalhista
    parametros: ParametrosLiquidacao
    premissas: tuple[str, ...] = ()
    documentos_referencia: tuple[str, ...] = ()
    observacoes: str = ""

    def __post_init__(self) -> None:
        referencia = self.referencia_processo.strip()

        if not referencia:
            raise ValueError(
                "A referência do processo é obrigatória."
            )

        premissas = tuple(
            item.strip()
            for item in self.premissas
            if item.strip()
        )

        documentos = tuple(
            item.strip()
            for item in self.documentos_referencia
            if item.strip()
        )

        object.__setattr__(
            self,
            "referencia_processo",
            referencia,
        )
        object.__setattr__(
            self,
            "premissas",
            premissas,
        )
        object.__setattr__(
            self,
            "documentos_referencia",
            documentos,
        )
        object.__setattr__(
            self,
            "observacoes",
            self.observacoes.strip(),
        )

    def validar_coerencia(self) -> tuple[str, ...]:
        erros: list[str] = []

        if (
            self.sentenca.data_sentenca is not None
            and self.sentenca.data_sentenca
            < self.contrato.data_admissao
        ):
            erros.append(
                "A sentença não pode anteceder a admissão."
            )

        if (
            self.contrato.data_desligamento is not None
            and self.parametros.data_calculo
            < self.contrato.data_desligamento
        ):
            erros.append(
                "A data de cálculo não pode anteceder o desligamento."
            )

        return tuple(erros)

    @property
    def esta_valida(self) -> bool:
        return not self.validar_coerencia()
