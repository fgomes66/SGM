from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.jornada.modelos.horario import Horario
from sgm.dominio.jornada.modelos.periodo_trabalho import PeriodoTrabalho
from sgm.dominio.jornada.modelos.tempo import Tempo


@dataclass(frozen=True, slots=True)
class RegraJornadaPosicional:
    """
    Define jornada ordinária e jornada especial conforme
    posição da data entre os dias efetivamente trabalhados.
    """

    periodo_ordinario: PeriodoTrabalho
    periodo_especial: PeriodoTrabalho
    primeiros_especiais: int
    ultimos_especiais: int
    limite_diario: Tempo = Tempo(8 * 60)
    inicio_noturno: Horario = Horario(22 * 60)
    fundamento: str = ""

    def __post_init__(self) -> None:
        if self.primeiros_especiais < 0:
            raise ValueError(
                "A quantidade de primeiros dias especiais "
                "não pode ser negativa."
            )

        if self.ultimos_especiais < 0:
            raise ValueError(
                "A quantidade de últimos dias especiais "
                "não pode ser negativa."
            )

        if self.limite_diario.minutos <= 0:
            raise ValueError(
                "O limite diário deve ser maior que zero."
            )

        fundamento = self.fundamento.strip()

        if not fundamento:
            raise ValueError(
                "O fundamento da jornada variável é obrigatório."
            )

        object.__setattr__(
            self,
            "fundamento",
            fundamento,
        )
