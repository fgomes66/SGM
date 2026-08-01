from __future__ import annotations

from sgm.dominio.trabalhista.competencias.plano_competencia import (
    PlanoCompetencia,
)
from sgm.dominio.trabalhista.competencias.resultado_competencia import (
    ResultadoCompetencia,
)
from sgm.dominio.trabalhista.liquidacao import (
    MemoriaCalculo,
    MotorLiquidacaoTrabalhista,
)


class MotorCompetencia:
    VERSAO = "0.9.1-B"

    @classmethod
    def calcular(
        cls,
        plano: PlanoCompetencia,
    ) -> ResultadoCompetencia:
        liquidacao = MotorLiquidacaoTrabalhista.calcular(
            plano.plano_liquidacao
        )

        linhas = (
            f"Competência: {plano.competencia.como_texto()}",
            f"Referência: {plano.referencia}",
            f"Motor por competência: {cls.VERSAO}",
            "",
            *liquidacao.memoria.linhas,
        )

        memoria = MemoriaCalculo(
            titulo=(
                "MEMÓRIA DE CÁLCULO POR COMPETÊNCIA — SGM"
            ),
            linhas=linhas,
            lema=liquidacao.memoria.lema,
        )

        # Recria apenas a memória externa da competência, preservando
        # integralmente o resultado financeiro do motor 0.9.0.
        return ResultadoCompetencia(
            competencia=plano.competencia,
            plano=plano,
            liquidacao=liquidacao,
            subtotal=liquidacao.subtotal,
            valor_final=liquidacao.valor_final,
            memoria=memoria,
            versao_motor=cls.VERSAO,
        )
