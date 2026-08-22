from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CapacidadeVerbaJudicial(StrEnum):
    EXECUTAVEL = "EXECUTAVEL"
    BLOQUEADO_POR_DADOS = "BLOQUEADO_POR_DADOS"
    NAO_SUPORTADO = "NAO_SUPORTADO"


@dataclass(frozen=True, slots=True)
class DiagnosticoVerbaJudicial:
    indice: int
    codigo_verba: str
    descricao: str
    capacidade: CapacidadeVerbaJudicial
    motivos: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        codigo = self.codigo_verba.strip().upper()
        descricao = self.descricao.strip()

        if self.indice < 0:
            raise ValueError(
                "O índice da verba não pode ser negativo."
            )

        if not codigo:
            raise ValueError(
                "O código da verba é obrigatório no diagnóstico."
            )

        if not descricao:
            raise ValueError(
                "A descrição da verba é obrigatória no diagnóstico."
            )

        motivos = tuple(
            motivo.strip()
            for motivo in self.motivos
            if motivo.strip()
        )

        object.__setattr__(self, "codigo_verba", codigo)
        object.__setattr__(self, "descricao", descricao)
        object.__setattr__(self, "motivos", motivos)


@dataclass(frozen=True, slots=True)
class DiagnosticoCapacidadeJudicial:
    referencia_processo: str
    verbas: tuple[DiagnosticoVerbaJudicial, ...]

    def __post_init__(self) -> None:
        referencia = self.referencia_processo.strip()

        if not referencia:
            raise ValueError(
                "A referência do processo é obrigatória."
            )

        object.__setattr__(
            self,
            "referencia_processo",
            referencia,
        )

    @property
    def executaveis(self) -> tuple[DiagnosticoVerbaJudicial, ...]:
        return tuple(
            item
            for item in self.verbas
            if item.capacidade
            is CapacidadeVerbaJudicial.EXECUTAVEL
        )

    @property
    def bloqueadas_por_dados(
        self,
    ) -> tuple[DiagnosticoVerbaJudicial, ...]:
        return tuple(
            item
            for item in self.verbas
            if item.capacidade
            is CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
        )

    @property
    def nao_suportadas(
        self,
    ) -> tuple[DiagnosticoVerbaJudicial, ...]:
        return tuple(
            item
            for item in self.verbas
            if item.capacidade
            is CapacidadeVerbaJudicial.NAO_SUPORTADO
        )

    @property
    def totalmente_executavel(self) -> bool:
        return bool(self.verbas) and all(
            item.capacidade
            is CapacidadeVerbaJudicial.EXECUTAVEL
            for item in self.verbas
        )
