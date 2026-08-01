from __future__ import annotations

from sgm.dominio.trabalhista.ferias.ferias_apuradas import (
    FeriasApuradas,
)
from sgm.dominio.trabalhista.ferias.parametros_ferias import (
    ParametrosFerias,
)
from sgm.dominio.trabalhista.incidencias import (
    ComposicaoBaseIncidencia,
    TipoBaseIncidencia,
)


class ServicoFerias:
    FORMULA_FERIAS_CODIGO = "FM-FER-001"
    FORMULA_TERCO_CODIGO = "FM-FER-002"

    @classmethod
    def calcular(
        cls,
        base: ComposicaoBaseIncidencia,
        parametros: ParametrosFerias,
    ) -> FeriasApuradas:
        if base.base_destino != TipoBaseIncidencia.FERIAS:
            raise ValueError(
                "A composição informada não pertence à base de férias."
            )

        valor_ferias = (
            base.total
            .multiplicar(parametros.fator_avos)
            .arredondar_centavos()
        )

        valor_terco = (
            valor_ferias
            .multiplicar(parametros.percentual_terco)
            .arredondar_centavos()
        )

        valor_total = (
            valor_ferias
            .somar(valor_terco)
            .arredondar_centavos()
        )

        return FeriasApuradas(
            base=base,
            parametros=parametros,
            valor_ferias=valor_ferias,
            valor_terco=valor_terco,
            valor_total=valor_total,
            formula_ferias_codigo=cls.FORMULA_FERIAS_CODIGO,
            formula_terco_codigo=cls.FORMULA_TERCO_CODIGO,
        )
