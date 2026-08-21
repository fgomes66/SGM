from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class NivelValidacao(StrEnum):
    ERRO = "ERRO"
    ALERTA = "ALERTA"
    INFORMACAO = "INFORMACAO"


@dataclass(frozen=True, slots=True)
class AchadoValidacao:
    codigo: str
    nivel: NivelValidacao
    mensagem: str
    campo: str | None = None

    def __post_init__(self) -> None:
        codigo = self.codigo.strip().upper()
        mensagem = self.mensagem.strip()
        campo = self.campo.strip() if self.campo else None

        if not codigo:
            raise ValueError("O código do achado é obrigatório.")

        if not mensagem:
            raise ValueError("A mensagem do achado é obrigatória.")

        object.__setattr__(self, "codigo", codigo)
        object.__setattr__(self, "mensagem", mensagem)
        object.__setattr__(self, "campo", campo)


@dataclass(frozen=True, slots=True)
class ResultadoValidacaoCaso:
    achados: tuple[AchadoValidacao, ...] = ()

    @property
    def erros(self) -> tuple[AchadoValidacao, ...]:
        return tuple(
            item
            for item in self.achados
            if item.nivel is NivelValidacao.ERRO
        )

    @property
    def alertas(self) -> tuple[AchadoValidacao, ...]:
        return tuple(
            item
            for item in self.achados
            if item.nivel is NivelValidacao.ALERTA
        )

    @property
    def informacoes(self) -> tuple[AchadoValidacao, ...]:
        return tuple(
            item
            for item in self.achados
            if item.nivel is NivelValidacao.INFORMACAO
        )

    @property
    def valido(self) -> bool:
        return not self.erros
