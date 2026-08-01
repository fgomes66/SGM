from __future__ import annotations

from sgm.dominio.trabalhista.aviso_previo.aviso_previo_apurado import (
    AvisoPrevioApurado,
)
from sgm.dominio.trabalhista.aviso_previo.parametros_aviso_previo import (
    ParametrosAvisoPrevio,
)
from sgm.dominio.trabalhista.incidencias import (
    ComposicaoBaseIncidencia,
    TipoBaseIncidencia,
)


class ServicoAvisoPrevio:
    FORMULA_CODIGO = "FM-AVP-001"

    @classmethod
    def calcular(
        cls,
        base: ComposicaoBaseIncidencia,
        parametros: ParametrosAvisoPrevio,
    ) -> AvisoPrevioApurado:
        if (
            base.base_destino
            != TipoBaseIncidencia.AVISO_PREVIO
        ):
            raise ValueError(
                "A composição informada não pertence à base do aviso."
            )

        valor = (
            base.total
            .multiplicar(parametros.fator_dias)
            .arredondar_centavos()
        )

        return AvisoPrevioApurado(
            base=base,
            parametros=parametros,
            valor=valor,
            formula_codigo=cls.FORMULA_CODIGO,
        )
