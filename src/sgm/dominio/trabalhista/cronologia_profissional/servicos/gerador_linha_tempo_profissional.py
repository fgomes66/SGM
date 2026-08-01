from __future__ import annotations

from sgm.dominio.trabalhista.caso_temporal import ResultadoCasoTemporal
from sgm.dominio.trabalhista.cronologia_profissional.linha_tempo_profissional import LinhaTempoProfissional
from sgm.dominio.trabalhista.cronologia_profissional.marco_temporal import (
    MarcoTemporal,
)
from sgm.dominio.trabalhista.cronologia_profissional.periodo_vigencia_profissional import PeriodoVigenciaProfissional
from sgm.dominio.trabalhista.cronologia_profissional.tipo_marco_temporal import TipoMarcoTemporal
from sgm.dominio.trabalhista.temporal import TipoEventoContratual


class GeradorLinhaTempoProfissional:
    VERSAO = "0.9.2-C"

    @classmethod
    def _tipo_marco_evento(
        cls,
        tipo_evento: TipoEventoContratual,
    ) -> TipoMarcoTemporal:
        if tipo_evento == TipoEventoContratual.AFASTAMENTO:
            return TipoMarcoTemporal.INATIVIDADE
        if tipo_evento == TipoEventoContratual.RETORNO:
            return TipoMarcoTemporal.RETOMADA
        if tipo_evento == TipoEventoContratual.RESCISAO:
            return TipoMarcoTemporal.RESCISAO
        return TipoMarcoTemporal.EVENTO_CONTRATUAL

    @classmethod
    def _descricao_evento(cls, evento) -> str:
        partes = [evento.descricao]

        if evento.novo_salario is not None:
            partes.append(
                f"novo salário={format(evento.novo_salario, 'f')}"
            )

        if evento.novo_divisor is not None:
            partes.append(
                f"novo divisor={format(evento.novo_divisor, 'f')}"
            )

        if evento.nova_jornada_semanal_minutos is not None:
            partes.append(
                "nova jornada="
                f"{evento.nova_jornada_semanal_minutos} minutos"
            )

        return "; ".join(partes)

    @classmethod
    def _gerar_vigencias(cls, estados):
        vigencias = []
        inicio = estados[0].competencia
        estado_base = estados[0]

        for indice in range(1, len(estados)):
            anterior = estados[indice - 1]
            atual = estados[indice]

            mudou = (
                atual.salario != anterior.salario
                or atual.divisor != anterior.divisor
                or (
                    atual.jornada_semanal_minutos
                    != anterior.jornada_semanal_minutos
                )
                or atual.ativo != anterior.ativo
                or atual.rescindido != anterior.rescindido
            )

            if mudou:
                vigencias.append(
                    PeriodoVigenciaProfissional(
                        inicio=inicio,
                        fim=anterior.competencia,
                        salario=estado_base.salario,
                        divisor=estado_base.divisor,
                        jornada_semanal_minutos=(
                            estado_base.jornada_semanal_minutos
                        ),
                        ativo=estado_base.ativo,
                        rescindido=estado_base.rescindido,
                    )
                )
                inicio = atual.competencia
                estado_base = atual

        ultimo = estados[-1]
        vigencias.append(
            PeriodoVigenciaProfissional(
                inicio=inicio,
                fim=ultimo.competencia,
                salario=estado_base.salario,
                divisor=estado_base.divisor,
                jornada_semanal_minutos=(
                    estado_base.jornada_semanal_minutos
                ),
                ativo=estado_base.ativo,
                rescindido=estado_base.rescindido,
            )
        )

        return tuple(vigencias)

    @classmethod
    def gerar(
        cls,
        resultado: ResultadoCasoTemporal,
    ) -> LinhaTempoProfissional:
        estados = resultado.linha_aplicada.estados
        marcos = [
            MarcoTemporal(
                competencia=resultado.plano.periodo.inicio,
                tipo=TipoMarcoTemporal.INICIO_PERIODO,
                titulo="Início do período analisado",
                descricao=(
                    "Primeira competência abrangida pelo cálculo."
                ),
                fundamento=(
                    "Período definido no plano temporal do caso."
                ),
                ordem_na_competencia=1,
            )
        ]

        for estado in estados:
            for ordem, evento in enumerate(
                estado.eventos_aplicados,
                start=2,
            ):
                marcos.append(
                    MarcoTemporal(
                        competencia=estado.competencia,
                        tipo=cls._tipo_marco_evento(evento.tipo),
                        titulo=evento.tipo.value.replace("_", " ").title(),
                        descricao=cls._descricao_evento(evento),
                        fundamento=evento.fundamento,
                        ordem_na_competencia=ordem,
                    )
                )

        marcos.append(
            MarcoTemporal(
                competencia=resultado.plano.periodo.fim,
                tipo=TipoMarcoTemporal.FIM_PERIODO,
                titulo="Fim do período analisado",
                descricao=(
                    "Última competência abrangida pelo cálculo."
                ),
                fundamento=(
                    "Período definido no plano temporal do caso."
                ),
                ordem_na_competencia=99,
            )
        )

        marcos_ordenados = tuple(
            sorted(
                marcos,
                key=lambda item: (
                    item.competencia,
                    item.ordem_na_competencia,
                ),
            )
        )

        vigencias = cls._gerar_vigencias(estados)

        return LinhaTempoProfissional(
            referencia=resultado.plano.referencia,
            periodo=resultado.plano.periodo,
            marcos=marcos_ordenados,
            vigencias=vigencias,
            versao_documento=cls.VERSAO,
        )
