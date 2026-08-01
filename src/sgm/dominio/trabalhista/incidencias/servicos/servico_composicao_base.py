from __future__ import annotations

from sgm.dominio.financeiro import OrigemFinanceira, ValorMonetario
from sgm.dominio.trabalhista.incidencias.composicao_base_incidencia import (
    ComposicaoBaseIncidencia,
)
from sgm.dominio.trabalhista.incidencias.parcela_incidencia import (
    ParcelaIncidencia,
)
from sgm.dominio.trabalhista.incidencias.tipo_base_incidencia import (
    TipoBaseIncidencia,
)


class ServicoComposicaoBase:
    FORMULA_CODIGO = "FM-BASE-INC-001"

    @classmethod
    def compor(
        cls,
        base_destino: TipoBaseIncidencia,
        parcelas: tuple[ParcelaIncidencia, ...],
    ) -> ComposicaoBaseIncidencia:
        if not parcelas:
            raise ValueError(
                "A composição exige ao menos uma parcela avaliada."
            )

        for parcela in parcelas:
            if parcela.regra.base_destino != base_destino:
                raise ValueError(
                    "Todas as regras devem apontar para a base informada."
                )

        moedas = {parcela.valor.moeda for parcela in parcelas}
        if len(moedas) != 1:
            raise ValueError(
                "Todas as parcelas devem utilizar a mesma moeda."
            )

        incluidas = tuple(
            parcela
            for parcela in parcelas
            if parcela.regra.incide
        )
        excluidas = tuple(
            parcela
            for parcela in parcelas
            if not parcela.regra.incide
        )

        if incluidas:
            total = incluidas[0].valor
            for parcela in incluidas[1:]:
                total = total.somar(parcela.valor)
        else:
            moeda = parcelas[0].valor.moeda
            total = ValorMonetario.criar(
                "0",
                OrigemFinanceira(
                    descricao=(
                        "Base de incidência sem parcelas incluídas: "
                        f"{base_destino.value}"
                    ),
                    formula_codigo=cls.FORMULA_CODIGO,
                ),
                moeda=moeda,
            )

        total = total.arredondar_centavos()

        return ComposicaoBaseIncidencia(
            base_destino=base_destino,
            parcelas_avaliadas=parcelas,
            parcelas_incluidas=incluidas,
            parcelas_excluidas=excluidas,
            total=total,
            formula_codigo=cls.FORMULA_CODIGO,
        )
