from __future__ import annotations

from decimal import Decimal

from sgm.dominio.jornada import Tempo
from sgm.dominio.trabalhista.jornada_financeira import ValorHora

from ..adicional_noturno_apurado import AdicionalNoturnoApurado
from ..parametros_adicional_noturno import ParametrosAdicionalNoturno


class ServicoAdicionalNoturno:
    """
    Apura exclusivamente a parcela adicional noturna.

    A determinação da quantidade de tempo noturno pertence
    à camada temporal/jornada e deve chegar previamente apurada.
    """

    FORMULA_CODIGO = "FM-AN-001"

    @classmethod
    def calcular(
        cls,
        valor_hora: ValorHora,
        quantidade: Tempo,
        parametros: ParametrosAdicionalNoturno,
    ) -> AdicionalNoturnoApurado:
        if quantidade.minutos <= 0:
            raise ValueError(
                "A quantidade de tempo noturno deve ser maior que zero."
            )

        valor_adicional_hora = (
            valor_hora.valor
            .aplicar_percentual(parametros.percentual)
        )

        quantidade_horas = (
            Decimal(quantidade.minutos)
            / Decimal("60")
        )

        valor_total = (
            valor_adicional_hora
            .multiplicar(quantidade_horas)
            .arredondar_centavos()
        )

        return AdicionalNoturnoApurado(
            valor_hora=valor_hora,
            quantidade=quantidade,
            parametros=parametros,
            valor_adicional_hora=valor_adicional_hora,
            valor_total=valor_total,
            formula_codigo=cls.FORMULA_CODIGO,
        )
