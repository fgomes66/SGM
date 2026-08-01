from __future__ import annotations

from sgm.dominio.trabalhista.jornada_financeira.divisor_jornada import (
    DivisorJornada,
)
from sgm.dominio.trabalhista.jornada_financeira.valor_hora import (
    ValorHora,
)
from sgm.dominio.trabalhista.remuneracao.base_de_calculo import (
    BaseDeCalculo,
)


class ServicoValorHora:
    FORMULA_CODIGO = "FM-VH-001"

    @classmethod
    def calcular(
        cls,
        base: BaseDeCalculo,
        divisor: DivisorJornada,
    ) -> ValorHora:
        valor_calculado = base.valor.dividir(divisor.divisor)

        return ValorHora(
            valor=valor_calculado,
            base=base,
            divisor=divisor,
            formula_codigo=cls.FORMULA_CODIGO,
        )
