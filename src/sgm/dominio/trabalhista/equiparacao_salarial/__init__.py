"""Domínio da equiparação salarial por competência."""

from .competencia_equiparacao import CompetenciaEquiparacao
from .resultado_equiparacao import (
    ResultadoCompetenciaEquiparacao,
    ResultadoEquiparacaoSalarial,
)
from .servico_equiparacao_salarial import ServicoEquiparacaoSalarial

__all__ = [
    "CompetenciaEquiparacao",
    "ResultadoCompetenciaEquiparacao",
    "ResultadoEquiparacaoSalarial",
    "ServicoEquiparacaoSalarial",
]
