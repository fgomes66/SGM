from __future__ import annotations

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.atualizacao.fator_atualizacao import (
    FatorAtualizacao,
)
from sgm.dominio.trabalhista.atualizacao.resultado_atualizacao import (
    ResultadoAtualizacao,
)
from sgm.dominio.trabalhista.atualizacao.resultado_atualizacao_juros import (
    ResultadoAtualizacaoJuros,
)
from sgm.dominio.trabalhista.atualizacao.tipo_atualizacao import (
    TipoAtualizacao,
)


class ServicoAtualizacao:
    FORMULA_CORRECAO = "FM-COR-001"
    FORMULA_JUROS = "FM-JUR-001"
    FORMULA_CONSOLIDADA = "FM-AJ-001"

    @classmethod
    def aplicar(
        cls,
        valor: ValorMonetario,
        fator: FatorAtualizacao,
    ) -> ResultadoAtualizacao:
        formula = (
            cls.FORMULA_CORRECAO
            if fator.tipo == TipoAtualizacao.CORRECAO_MONETARIA
            else cls.FORMULA_JUROS
        )

        valor_atualizado = (
            valor
            .multiplicar(fator.fator)
            .arredondar_centavos()
        )

        diferenca = (
            valor_atualizado
            .subtrair(valor)
            .arredondar_centavos()
        )

        return ResultadoAtualizacao(
            valor_original=valor,
            fator=fator,
            valor_atualizado=valor_atualizado,
            diferenca=diferenca,
            formula_codigo=formula,
        )

    @classmethod
    def aplicar_correcao_e_juros(
        cls,
        valor: ValorMonetario,
        fator_correcao: FatorAtualizacao,
        fator_juros: FatorAtualizacao,
    ) -> ResultadoAtualizacaoJuros:
        if (
            fator_correcao.tipo
            != TipoAtualizacao.CORRECAO_MONETARIA
        ):
            raise ValueError(
                "O primeiro fator deve ser de correção monetária."
            )

        if fator_juros.tipo != TipoAtualizacao.JUROS_MORA:
            raise ValueError(
                "O segundo fator deve ser de juros de mora."
            )

        correcao = cls.aplicar(valor, fator_correcao)
        juros = cls.aplicar(
            correcao.valor_atualizado,
            fator_juros,
        )

        return ResultadoAtualizacaoJuros(
            correcao=correcao,
            juros=juros,
            valor_final=juros.valor_atualizado,
            formula_codigo=cls.FORMULA_CONSOLIDADA,
        )
