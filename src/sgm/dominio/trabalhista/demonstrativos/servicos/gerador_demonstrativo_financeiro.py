from __future__ import annotations

from collections import defaultdict

from sgm.dominio.trabalhista.caso_temporal import ResultadoCasoTemporal
from sgm.dominio.trabalhista.dependencias import CodigoVerba
from sgm.dominio.trabalhista.demonstrativos.demonstrativo_financeiro_profissional import (
    DemonstrativoFinanceiroProfissional,
)
from sgm.dominio.trabalhista.demonstrativos.natureza_financeira import (
    NaturezaFinanceira,
)
from sgm.dominio.trabalhista.demonstrativos.resumo_competencia import (
    ResumoCompetencia,
)
from sgm.dominio.trabalhista.demonstrativos.resumo_natureza import (
    ResumoNatureza,
)
from sgm.dominio.trabalhista.demonstrativos.resumo_verba import (
    ResumoVerba,
)


class GeradorDemonstrativoFinanceiro:
    VERSAO = "0.9.2-B"

    NATUREZA_POR_VERBA = {
        CodigoVerba.HORA_EXTRA: NaturezaFinanceira.REMUNERATORIA,
        CodigoVerba.DSR: NaturezaFinanceira.REFLEXA,
        CodigoVerba.FGTS: NaturezaFinanceira.FUNDIARIA,
        CodigoVerba.FERIAS: NaturezaFinanceira.REFLEXA,
        CodigoVerba.DECIMO_TERCEIRO: NaturezaFinanceira.REFLEXA,
        CodigoVerba.AVISO_PREVIO: NaturezaFinanceira.INDENIZATORIA,
    }

    @classmethod
    def gerar(
        cls,
        resultado: ResultadoCasoTemporal,
    ) -> DemonstrativoFinanceiroProfissional:
        competencias = tuple(
            ResumoCompetencia(
                competencia=item.competencia,
                subtotal=item.subtotal,
                valor_final=item.valor_final,
                ativa=True,
                referencia=item.plano.referencia,
            )
            for item in resultado.resultados_mensais
        )

        acumulado_verbas = {}
        quantidade_competencias = defaultdict(int)
        descricao_por_codigo = {}

        for resultado_mensal in resultado.resultados_mensais:
            for verba in resultado_mensal.liquidacao.verbas:
                descricao_por_codigo[verba.codigo] = verba.descricao
                quantidade_competencias[verba.codigo] += 1

                if verba.codigo not in acumulado_verbas:
                    acumulado_verbas[verba.codigo] = verba.valor
                else:
                    acumulado_verbas[verba.codigo] = (
                        acumulado_verbas[verba.codigo]
                        .somar(verba.valor)
                        .arredondar_centavos()
                    )

        ordem = (
            CodigoVerba.HORA_EXTRA,
            CodigoVerba.DSR,
            CodigoVerba.FGTS,
            CodigoVerba.FERIAS,
            CodigoVerba.DECIMO_TERCEIRO,
            CodigoVerba.AVISO_PREVIO,
        )

        verbas = tuple(
            ResumoVerba(
                codigo=codigo,
                descricao=descricao_por_codigo[codigo],
                natureza=cls.NATUREZA_POR_VERBA.get(
                    codigo,
                    NaturezaFinanceira.OUTRA,
                ),
                valor=acumulado_verbas[codigo],
                quantidade_competencias=(
                    quantidade_competencias[codigo]
                ),
            )
            for codigo in ordem
            if codigo in acumulado_verbas
        )

        acumulado_naturezas = {}
        contagem_naturezas = defaultdict(int)

        for verba in verbas:
            contagem_naturezas[verba.natureza] += 1
            if verba.natureza not in acumulado_naturezas:
                acumulado_naturezas[verba.natureza] = verba.valor
            else:
                acumulado_naturezas[verba.natureza] = (
                    acumulado_naturezas[verba.natureza]
                    .somar(verba.valor)
                    .arredondar_centavos()
                )

        naturezas = tuple(
            ResumoNatureza(
                natureza=natureza,
                valor=acumulado_naturezas[natureza],
                quantidade_verbas=contagem_naturezas[natureza],
            )
            for natureza in NaturezaFinanceira
            if natureza in acumulado_naturezas
        )

        return DemonstrativoFinanceiroProfissional(
            referencia=resultado.plano.referencia,
            competencias=competencias,
            verbas=verbas,
            naturezas=naturezas,
            subtotal_geral=(
                resultado.consolidado.subtotal_consolidado
            ),
            valor_final_geral=(
                resultado.consolidado.valor_final_consolidado
            ),
            versao_documento=cls.VERSAO,
        )
