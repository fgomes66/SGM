from __future__ import annotations

from decimal import Decimal

from sgm.dominio.trabalhista.dsr.parametros_dsr import (
    ParametrosDSR,
)
from sgm.dominio.trabalhista.dsr.reflexo_dsr import ReflexoDSR
from sgm.dominio.trabalhista.horas_extras_financeiras import (
    HoraExtraFinanceira,
)


class ServicoReflexoDSR:
    FORMULA_CODIGO = "FM-DSR-001"

    @classmethod
    def calcular(
        cls,
        origem: HoraExtraFinanceira,
        parametros: ParametrosDSR,
    ) -> ReflexoDSR:
        valor = (
            origem.valor_total
            .dividir(Decimal(parametros.dias_uteis))
            .multiplicar(Decimal(parametros.dias_repouso))
            .arredondar_centavos()
        )

        return ReflexoDSR(
            origem=origem,
            parametros=parametros,
            valor=valor,
            formula_codigo=cls.FORMULA_CODIGO,
        )
