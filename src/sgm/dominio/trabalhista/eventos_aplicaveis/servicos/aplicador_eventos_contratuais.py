from __future__ import annotations

from dataclasses import replace
from datetime import date

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.competencias import PlanoCompetencia
from sgm.dominio.trabalhista.eventos_aplicaveis.estado_contratual import EstadoContratual
from sgm.dominio.trabalhista.eventos_aplicaveis.evento_contratual_aplicavel import EventoContratualAplicavel
from sgm.dominio.trabalhista.eventos_aplicaveis.linha_tempo_aplicada import LinhaTempoAplicada
from sgm.dominio.trabalhista.liquidacao import PlanoLiquidacaoIntegrada
from sgm.dominio.trabalhista.temporal import (
    PeriodoContratual,
    TipoEventoContratual,
)


class AplicadorEventosContratuais:
    VERSAO = "0.9.1-D"

    @classmethod
    def aplicar(
        cls,
        periodo: PeriodoContratual,
        plano_modelo: PlanoLiquidacaoIntegrada,
        eventos: tuple[EventoContratualAplicavel, ...],
        referencia: str,
    ) -> LinhaTempoAplicada:
        referencia = referencia.strip()
        if not referencia:
            raise ValueError(
                "A referência da linha aplicada é obrigatória."
            )

        ordenados = tuple(
            sorted(
                eventos,
                key=lambda item: (
                    item.competencia,
                    item.tipo.value,
                    str(item.id),
                ),
            )
        )

        for evento in ordenados:
            if not periodo.contem(evento.competencia):
                raise ValueError(
                    "Todos os eventos devem estar dentro do período."
                )

        salario = plano_modelo.base_remuneratoria.valor.valor
        divisor = plano_modelo.divisor_jornada.divisor
        jornada = (
            plano_modelo.divisor_jornada.jornada_semanal_minutos
        )
        ativo = True
        rescindido = False

        estados: list[EstadoContratual] = []
        planos: list[PlanoCompetencia] = []
        inativas: list[str] = []

        for competencia in periodo.competencias():
            eventos_mes = tuple(
                evento
                for evento in ordenados
                if evento.competencia == competencia
            )

            for evento in eventos_mes:
                if rescindido:
                    raise ValueError(
                        "Não é permitido aplicar eventos após a rescisão."
                    )

                if evento.tipo in (
                    TipoEventoContratual.REAJUSTE,
                    TipoEventoContratual.PROMOCAO,
                ):
                    salario = evento.novo_salario
                elif (
                    evento.tipo
                    == TipoEventoContratual.ALTERACAO_DIVISOR
                ):
                    divisor = evento.novo_divisor
                elif (
                    evento.tipo
                    == TipoEventoContratual.ALTERACAO_JORNADA
                ):
                    jornada = evento.nova_jornada_semanal_minutos
                elif evento.tipo == TipoEventoContratual.AFASTAMENTO:
                    ativo = False
                elif evento.tipo == TipoEventoContratual.RETORNO:
                    ativo = True
                elif evento.tipo == TipoEventoContratual.RESCISAO:
                    ativo = False
                    rescindido = True
                elif evento.tipo == TipoEventoContratual.ADMISSAO:
                    ativo = True

            estado = EstadoContratual(
                competencia=competencia,
                salario=salario,
                divisor=divisor,
                jornada_semanal_minutos=jornada,
                ativo=ativo,
                rescindido=rescindido,
                eventos_aplicados=eventos_mes,
            )
            estados.append(estado)

            if ativo:
                valor_modelo = (
                    plano_modelo.base_remuneratoria.valor
                )
                novo_valor = ValorMonetario.criar(
                    format(salario, "f"),
                    valor_modelo.origem,
                    moeda=valor_modelo.moeda,
                )

                nova_base = replace(
                    plano_modelo.base_remuneratoria,
                    valor=novo_valor,
                    competencia=date(
                        competencia.ano,
                        competencia.mes,
                        1,
                    ),
                )
                novo_divisor = replace(
                    plano_modelo.divisor_jornada,
                    divisor=divisor,
                    jornada_semanal_minutos=jornada,
                )
                novo_plano_integrado = replace(
                    plano_modelo,
                    processo_referencia=(
                        f"{referencia}-{competencia.como_texto()}"
                    ),
                    base_remuneratoria=nova_base,
                    divisor_jornada=novo_divisor,
                )
                planos.append(
                    PlanoCompetencia(
                        competencia=competencia,
                        plano_liquidacao=novo_plano_integrado,
                        referencia=(
                            f"{referencia}-"
                            f"{competencia.como_texto()}"
                        ),
                    )
                )
            else:
                inativas.append(competencia.como_texto())

        return LinhaTempoAplicada(
            periodo=periodo,
            estados=tuple(estados),
            planos_ativos=tuple(planos),
            competencias_inativas=tuple(inativas),
            versao_motor=cls.VERSAO,
        )
