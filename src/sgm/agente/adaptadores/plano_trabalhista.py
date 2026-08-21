from __future__ import annotations

from decimal import Decimal

from sgm.agente.contexto import ContextoTrabalhista
from sgm.dominio.financeiro import OrigemFinanceira, ValorMonetario
from sgm.dominio.trabalhista import (
    CodigoVerba,
    ParametrosFerias,
    ParcelaIncidencia,
    RegraIncidencia,
    ServicoComposicaoBase,
    TipoBaseIncidencia,
)


class AdaptadorPlanoTrabalhista:

    @classmethod
    def preparar_ferias(
        cls,
        contexto: ContextoTrabalhista,
    ):
        salario_texto = contexto.buscar("salario")

        if salario_texto is None:
            raise ValueError(
                "O salário é obrigatório para o cálculo de férias."
            )

        avos = cls._obter_avos(contexto)

        salario = ValorMonetario.criar(
            salario_texto,
            OrigemFinanceira(
                descricao="Salário informado pelo usuário.",
                documento_id="AGENTE-CONTEXTO",
            ),
            moeda="BRL",
        )

        regra = RegraIncidencia(
            base_destino=TipoBaseIncidencia.FERIAS,
            incide=True,
            fundamento=(
                "Salário informado como base remuneratória "
                "para cálculo de férias."
            ),
        )

        parcela = ParcelaIncidencia(
            verba=CodigoVerba.SALARIO,
            valor=salario,
            regra=regra,
            descricao="Salário-base para férias",
            documento_id="AGENTE-CONTEXTO",
        )

        base = ServicoComposicaoBase.compor(
            TipoBaseIncidencia.FERIAS,
            (parcela,),
        )

        parametros = ParametrosFerias(
            avos=avos,
            percentual_terco=Decimal(
                "0.3333333333333333333333333333"
            ),
            fundamento=(
                "Parâmetros obtidos do contexto trabalhista."
            ),
        )

        return base, parametros

    @staticmethod
    def _obter_avos(
        contexto: ContextoTrabalhista,
    ) -> int:
        avos_texto = contexto.buscar("avos")

        if avos_texto is not None:
            return int(avos_texto)

        meses_texto = contexto.buscar("meses")

        if meses_texto is not None:
            meses = int(meses_texto)
            return min(meses, 12)

        raise ValueError(
            "Informe a quantidade de avos ou meses."
        )