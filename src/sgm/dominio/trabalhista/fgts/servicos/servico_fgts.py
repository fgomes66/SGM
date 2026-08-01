from __future__ import annotations

from sgm.dominio.trabalhista.fgts.aliquota_fgts import AliquotaFGTS
from sgm.dominio.trabalhista.fgts.fgts_apurado import FGTSApurado
from sgm.dominio.trabalhista.incidencias import (
    ComposicaoBaseIncidencia,
    TipoBaseIncidencia,
)


class ServicoFGTS:
    FORMULA_CODIGO = "FM-FGTS-001"

    @classmethod
    def calcular(
        cls,
        base: ComposicaoBaseIncidencia,
        aliquota: AliquotaFGTS,
    ) -> FGTSApurado:
        if base.base_destino != TipoBaseIncidencia.FGTS:
            raise ValueError(
                "A composição informada não pertence à base do FGTS."
            )

        valor = (
            base.total
            .multiplicar(aliquota.percentual)
            .arredondar_centavos()
        )

        return FGTSApurado(
            base=base,
            aliquota=aliquota,
            valor=valor,
            formula_codigo=cls.FORMULA_CODIGO,
        )
