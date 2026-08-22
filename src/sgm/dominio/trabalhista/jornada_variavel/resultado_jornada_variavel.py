from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sgm.dominio.jornada.modelos.periodo_trabalho import PeriodoTrabalho
from sgm.dominio.jornada.modelos.tempo import Tempo
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo


@dataclass(frozen=True, slots=True)
class ResultadoDiaJornadaVariavel:
    data: date
    especial: bool
    periodo: PeriodoTrabalho
    tempo_liquido: Tempo
    horas_extras: Tempo
    tempo_noturno: Tempo

    def memoria_resumida(self) -> tuple[str, ...]:
        return (
            f"Data: {self.data.isoformat()}",
            (
                "Tipo: "
                + ("JORNADA ESPECIAL" if self.especial else "JORNADA ORDINÁRIA")
            ),
            (
                "Horário: "
                f"{self.periodo.entrada.para_texto()} "
                f"a {self.periodo.saida.para_texto()}"
            ),
            f"Tempo líquido: {self.tempo_liquido.para_hhmm()}",
            f"Horas extras: {self.horas_extras.para_hhmm()}",
            f"Tempo noturno: {self.tempo_noturno.para_hhmm()}",
        )


@dataclass(frozen=True, slots=True)
class ResultadoCompetenciaJornadaVariavel:
    competencia: CompetenciaCalculo
    dias: tuple[ResultadoDiaJornadaVariavel, ...]
    total_tempo_liquido: Tempo
    total_horas_extras: Tempo
    total_tempo_noturno: Tempo
    fundamento: str
    versao_motor: str = "0.9.7-JV"

    def __post_init__(self) -> None:
        if not self.dias:
            raise ValueError(
                "A jornada variável exige ao menos um dia trabalhado."
            )

    @property
    def quantidade_dias(self) -> int:
        return len(self.dias)

    def memoria_resumida(self) -> tuple[str, ...]:
        linhas = [
            f"Competência: {self.competencia.como_texto()}",
            f"Motor de jornada variável: {self.versao_motor}",
            f"Dias trabalhados: {self.quantidade_dias}",
            f"Fundamento: {self.fundamento}",
        ]

        for dia in self.dias:
            linhas.extend(("", *dia.memoria_resumida()))

        linhas.extend(
            (
                "",
                (
                    "TOTAL HORAS EXTRAS: "
                    f"{self.total_horas_extras.para_hhmm()}"
                ),
                (
                    "TOTAL TEMPO NOTURNO: "
                    f"{self.total_tempo_noturno.para_hhmm()}"
                ),
            )
        )

        return tuple(linhas)
