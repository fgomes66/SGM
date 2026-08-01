from __future__ import annotations

from sgm.dominio.trabalhista.decimo_terceiro.decimo_terceiro_apurado import (
    DecimoTerceiroApurado,
)
from sgm.dominio.trabalhista.decimo_terceiro.parametros_decimo_terceiro import (
    ParametrosDecimoTerceiro,
)
from sgm.dominio.trabalhista.incidencias import (
    ComposicaoBaseIncidencia,
    TipoBaseIncidencia,
)


class ServicoDecimoTerceiro:
    FORMULA_CODIGO = "FM-13-001"

    @classmethod
    def calcular(
        cls,
        base: ComposicaoBaseIncidencia,
        parametros: ParametrosDecimoTerceiro,
    ) -> DecimoTerceiroApurado:
        if (
            base.base_destino
            != TipoBaseIncidencia.DECIMO_TERCEIRO
        ):
            raise ValueError(
                "A composição informada não pertence à base do 13º."
            )

        valor = (
            base.total
            .multiplicar(parametros.fator_avos)
            .arredondar_centavos()
        )

        return DecimoTerceiroApurado(
            base=base,
            parametros=parametros,
            valor=valor,
            formula_codigo=cls.FORMULA_CODIGO,
        )
