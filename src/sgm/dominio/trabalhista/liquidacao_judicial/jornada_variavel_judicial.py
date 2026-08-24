from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sgm.dominio.trabalhista.jornada_variavel import (
    RegraJornadaPosicional,
)
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


@dataclass(frozen=True, slots=True)
class JornadaVariavelJudicial:
    """
    Dados temporais determinados pelo título judicial para
    apuração de jornada variável em uma competência.

    As datas representam dias efetivamente trabalhados.
    Nenhum calendário útil é presumido pelo domínio.
    """

    competencia: CompetenciaCalculo
    datas_trabalhadas: tuple[date, ...]
    regra: RegraJornadaPosicional

    def __post_init__(self) -> None:
        if not self.datas_trabalhadas:
            raise ValueError(
                "A jornada variável judicial exige ao menos "
                "uma data trabalhada."
            )

        datas = tuple(sorted(self.datas_trabalhadas))

        if len(set(datas)) != len(datas):
            raise ValueError(
                "Datas trabalhadas duplicadas não são permitidas "
                "na jornada variável judicial."
            )

        for data_trabalho in datas:
            if (
                data_trabalho.year != self.competencia.ano
                or data_trabalho.month != self.competencia.mes
            ):
                raise ValueError(
                    "Todas as datas trabalhadas devem pertencer "
                    "à competência da jornada variável judicial."
                )

        object.__setattr__(
            self,
            "datas_trabalhadas",
            datas,
        )
