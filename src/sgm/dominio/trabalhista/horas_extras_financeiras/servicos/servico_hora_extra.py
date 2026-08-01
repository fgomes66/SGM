from __future__ import annotations

from decimal import Decimal

from sgm.dominio.jornada import Tempo
from sgm.dominio.trabalhista.horas_extras_financeiras.adicional_hora_extra import (
    AdicionalHoraExtra,
)
from sgm.dominio.trabalhista.horas_extras_financeiras.hora_extra_financeira import (
    HoraExtraFinanceira,
)
from sgm.dominio.trabalhista.jornada_financeira import ValorHora


class ServicoHoraExtra:
    FORMULA_CODIGO = "FM-HE-001"

    @classmethod
    def calcular(
        cls,
        valor_hora: ValorHora,
        quantidade: Tempo,
        adicional: AdicionalHoraExtra,
    ) -> HoraExtraFinanceira:
        if quantidade.minutos <= 0:
            raise ValueError(
                "A quantidade de horas extras deve ser maior que zero."
            )

        valor_hora_com_adicional = (
            valor_hora.valor.acrescer_percentual(
                adicional.percentual
            )
        )

        quantidade_horas = (
            Decimal(quantidade.minutos) / Decimal("60")
        )

        valor_total = (
            valor_hora_com_adicional
            .multiplicar(quantidade_horas)
            .arredondar_centavos()
        )

        return HoraExtraFinanceira(
            valor_hora=valor_hora,
            quantidade=quantidade,
            adicional=adicional,
            valor_hora_com_adicional=valor_hora_com_adicional,
            valor_total=valor_total,
            formula_codigo=cls.FORMULA_CODIGO,
        )
