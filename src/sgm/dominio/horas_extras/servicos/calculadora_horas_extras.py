from __future__ import annotations

from collections.abc import Iterable
from datetime import timedelta

from sgm.dominio.horas_extras.modelos.registro_jornada import RegistroJornada
from sgm.dominio.horas_extras.modelos.regra_horas_extras import (
    RegraHorasExtras,
)
from sgm.dominio.horas_extras.modelos.resultado_dia import (
    ResultadoHorasExtrasDia,
)
from sgm.dominio.horas_extras.modelos.resultado_semana import (
    ResultadoHorasExtrasSemana,
)
from sgm.dominio.jornada import Tempo


class CalculadoraHorasExtras:
    @staticmethod
    def apurar_dia(
        registro: RegistroJornada,
        regra: RegraHorasExtras,
    ) -> ResultadoHorasExtrasDia:
        if regra.considerar_excedente_diario:
            extras = max(
                0,
                registro.tempo_trabalhado.minutos
                - regra.limite_diario.minutos,
            )
        else:
            extras = 0

        normais = registro.tempo_trabalhado.minutos - extras

        return ResultadoHorasExtrasDia(
            data=registro.data,
            tempo_trabalhado=registro.tempo_trabalhado,
            horas_normais=Tempo(normais),
            extras_diarias=Tempo(extras),
        )

    @classmethod
    def apurar_semana(
        cls,
        registros: Iterable[RegistroJornada],
        regra: RegraHorasExtras,
    ) -> ResultadoHorasExtrasSemana:
        lista = sorted(registros, key=lambda item: item.data)
        if not lista:
            raise ValueError(
                "É necessário informar ao menos um registro de jornada."
            )

        datas = [item.data for item in lista]
        if len(set(datas)) != len(datas):
            raise ValueError(
                "Não pode haver mais de um registro para a mesma data."
            )

        inicio = lista[0].data
        fim_maximo = inicio + timedelta(days=6)
        if lista[-1].data > fim_maximo:
            raise ValueError(
                "Os registros devem pertencer a uma janela máxima de sete dias."
            )

        resultados = tuple(cls.apurar_dia(item, regra) for item in lista)
        total_trabalhado = sum(
            item.tempo_trabalhado.minutos for item in resultados
        )
        extras_diarias = sum(
            item.extras_diarias.minutos for item in resultados
        )

        if regra.considerar_excedente_semanal:
            excedente_semanal_bruto = max(
                0,
                total_trabalhado - regra.limite_semanal.minutos,
            )
        else:
            excedente_semanal_bruto = 0

        extras_semanais_nao_duplicadas = max(
            0,
            excedente_semanal_bruto - extras_diarias,
        )
        total_extras = extras_diarias + extras_semanais_nao_duplicadas
        total_normal = total_trabalhado - total_extras

        memoria = (
            f"Total trabalhado: {Tempo(total_trabalhado).para_hhmm()}",
            f"Limite diário: {regra.limite_diario.para_hhmm()}",
            f"Limite semanal: {regra.limite_semanal.para_hhmm()}",
            f"Extras diárias: {Tempo(extras_diarias).para_hhmm()}",
            (
                "Extras semanais não duplicadas: "
                f"{Tempo(extras_semanais_nao_duplicadas).para_hhmm()}"
            ),
            f"Total de horas extras: {Tempo(total_extras).para_hhmm()}",
            f"Adicional previsto: {regra.adicional_padrao}",
        )

        return ResultadoHorasExtrasSemana(
            inicio_semana=inicio,
            fim_semana=lista[-1].data,
            resultados_diarios=resultados,
            total_trabalhado=Tempo(total_trabalhado),
            total_normal=Tempo(total_normal),
            extras_diarias=Tempo(extras_diarias),
            extras_semanais_nao_duplicadas=Tempo(
                extras_semanais_nao_duplicadas
            ),
            total_horas_extras=Tempo(total_extras),
            adicional_aplicavel=regra.adicional_padrao,
            memoria=memoria,
        )
