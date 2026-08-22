from __future__ import annotations

from datetime import date

from sgm.dominio.jornada.modelos.periodo_trabalho import PeriodoTrabalho
from sgm.dominio.jornada.modelos.tempo import Tempo
from sgm.dominio.jornada.servicos.calculadora_jornada import (
    CalculadoraJornada,
)
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo

from ..regra_jornada_posicional import RegraJornadaPosicional
from ..resultado_jornada_variavel import (
    ResultadoCompetenciaJornadaVariavel,
    ResultadoDiaJornadaVariavel,
)


class ServicoJornadaVariavel:
    """
    Apura jornada por posição entre datas efetivamente trabalhadas.

    Não presume calendário útil, domingos ou feriados.
    As datas trabalhadas devem ser fornecidas explicitamente.
    """

    VERSAO = "0.9.7-JV"

    @classmethod
    def calcular(
        cls,
        competencia: CompetenciaCalculo,
        datas_trabalhadas: tuple[date, ...],
        regra: RegraJornadaPosicional,
    ) -> ResultadoCompetenciaJornadaVariavel:
        if not datas_trabalhadas:
            raise ValueError(
                "Informe ao menos uma data trabalhada."
            )

        datas = tuple(sorted(datas_trabalhadas))

        if len(set(datas)) != len(datas):
            raise ValueError(
                "Datas trabalhadas duplicadas não são permitidas."
            )

        for data_trabalho in datas:
            if (
                data_trabalho.year != competencia.ano
                or data_trabalho.month != competencia.mes
            ):
                raise ValueError(
                    "Todas as datas devem pertencer à competência."
                )

        especiais = set(
            datas[:regra.primeiros_especiais]
        )

        if regra.ultimos_especiais:
            especiais.update(
                datas[-regra.ultimos_especiais:]
            )

        resultados: list[ResultadoDiaJornadaVariavel] = []

        for data_trabalho in datas:
            especial = data_trabalho in especiais

            periodo = (
                regra.periodo_especial
                if especial
                else regra.periodo_ordinario
            )

            jornada = CalculadoraJornada.calcular(periodo)

            excedente = max(
                jornada.tempo_liquido.minutos
                - regra.limite_diario.minutos,
                0,
            )

            tempo_noturno = cls._tempo_noturno(
                periodo,
                regra.inicio_noturno.minutos_desde_meia_noite,
            )

            resultados.append(
                ResultadoDiaJornadaVariavel(
                    data=data_trabalho,
                    especial=especial,
                    periodo=periodo,
                    tempo_liquido=jornada.tempo_liquido,
                    horas_extras=Tempo(excedente),
                    tempo_noturno=Tempo(tempo_noturno),
                )
            )

        total_liquido = Tempo(
            sum(
                item.tempo_liquido.minutos
                for item in resultados
            )
        )

        total_extras = Tempo(
            sum(
                item.horas_extras.minutos
                for item in resultados
            )
        )

        total_noturno = Tempo(
            sum(
                item.tempo_noturno.minutos
                for item in resultados
            )
        )

        return ResultadoCompetenciaJornadaVariavel(
            competencia=competencia,
            dias=tuple(resultados),
            total_tempo_liquido=total_liquido,
            total_horas_extras=total_extras,
            total_tempo_noturno=total_noturno,
            fundamento=regra.fundamento,
            versao_motor=cls.VERSAO,
        )

    @staticmethod
    def _tempo_noturno(
        periodo: PeriodoTrabalho,
        inicio_noturno: int,
    ) -> int:
        """
        Calcula minutos efetivamente trabalhados após o início
        noturno, descontando intervalos que incidam nessa faixa.
        """
        inicio = max(
            periodo.entrada.minutos_desde_meia_noite,
            inicio_noturno,
        )

        fim = periodo.saida.minutos_desde_meia_noite

        if fim <= inicio:
            return 0

        minutos = fim - inicio

        for intervalo in periodo.intervalos:
            sobreposicao_inicio = max(
                intervalo.inicio.minutos_desde_meia_noite,
                inicio,
            )

            sobreposicao_fim = min(
                intervalo.fim.minutos_desde_meia_noite,
                fim,
            )

            if sobreposicao_fim > sobreposicao_inicio:
                minutos -= (
                    sobreposicao_fim
                    - sobreposicao_inicio
                )

        return max(minutos, 0)
