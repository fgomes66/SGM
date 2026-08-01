from __future__ import annotations

from dataclasses import dataclass, field

from sgm.dominio.jornada.modelos.horario import Horario
from sgm.dominio.jornada.modelos.intervalo import Intervalo
from sgm.dominio.jornada.modelos.tempo import Tempo


@dataclass(frozen=True, slots=True)
class PeriodoTrabalho:
    entrada: Horario
    saida: Horario
    intervalos: tuple[Intervalo, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.saida <= self.entrada:
            raise ValueError(
                "Nesta versão, a saída deve ocorrer após a entrada no mesmo dia."
            )

        ordenados = sorted(
            self.intervalos,
            key=lambda item: item.inicio.minutos_desde_meia_noite,
        )

        anterior: Intervalo | None = None
        for intervalo in ordenados:
            if intervalo.inicio < self.entrada or intervalo.fim > self.saida:
                raise ValueError(
                    "Todo intervalo deve estar contido no período de trabalho."
                )
            if anterior is not None and intervalo.inicio < anterior.fim:
                raise ValueError("Intervalos não podem se sobrepor.")
            anterior = intervalo

        if self.duracao_intervalos.minutos > self.duracao_bruta.minutos:
            raise ValueError(
                "A soma dos intervalos não pode superar a duração bruta."
            )

    @property
    def duracao_bruta(self) -> Tempo:
        return Tempo(
            self.saida.minutos_desde_meia_noite
            - self.entrada.minutos_desde_meia_noite
        )

    @property
    def duracao_intervalos(self) -> Tempo:
        return Tempo(sum(intervalo.duracao.minutos for intervalo in self.intervalos))

    @property
    def duracao_liquida(self) -> Tempo:
        return self.duracao_bruta - self.duracao_intervalos
