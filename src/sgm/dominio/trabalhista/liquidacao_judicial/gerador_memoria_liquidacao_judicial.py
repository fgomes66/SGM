from __future__ import annotations

from sgm.dominio.trabalhista.relatorios import (
    ItemMemoria,
    LinhaTabelaFinanceira,
    MemoriaCalculoProfissional,
    NivelObservacaoTecnica,
    ObservacaoTecnica,
    SecaoMemoria,
    TabelaFinanceira,
    TipoSecaoMemoria,
)

from .entrada_caso_trabalhista import EntradaCasoTrabalhista
from .resultado_atualizado_judicial import ResultadoAtualizadoJudicial


class GeradorMemoriaLiquidacaoJudicial:
    """Gera memória profissional completa da liquidação judicial."""

    VERSAO = "0.9.7-JM"

    @classmethod
    def gerar(
        cls,
        entrada: EntradaCasoTrabalhista,
        resultado: ResultadoAtualizadoJudicial,
    ) -> MemoriaCalculoProfissional:
        consolidado = resultado.consolidado
        origem = consolidado.resultado_origem

        identificacao = SecaoMemoria(
            ordem=1,
            tipo=TipoSecaoMemoria.IDENTIFICACAO,
            titulo="Identificação do cálculo",
            itens=(
                ItemMemoria(
                    "Processo",
                    entrada.referencia_processo,
                ),
                ItemMemoria(
                    "Data de admissão",
                    entrada.contrato.data_admissao.isoformat(),
                ),
                ItemMemoria(
                    "Data de desligamento",
                    (
                        entrada.contrato.data_desligamento.isoformat()
                        if entrada.contrato.data_desligamento
                        else "não informada"
                    ),
                ),
                ItemMemoria(
                    "Salário-base",
                    (
                        f"{entrada.parametros.moeda} "
                        f"{format(entrada.contrato.salario_base, 'f')}"
                    ),
                ),
                ItemMemoria(
                    "Data do cálculo",
                    entrada.parametros.data_calculo.isoformat(),
                ),
            ),
        )

        premissas_itens = []

        if entrada.sentenca.data_sentenca is not None:
            premissas_itens.append(
                ItemMemoria(
                    "Data da sentença",
                    entrada.sentenca.data_sentenca.isoformat(),
                )
            )

        if entrada.sentenca.data_transito_julgado is not None:
            premissas_itens.append(
                ItemMemoria(
                    "Trânsito em julgado",
                    entrada.sentenca.data_transito_julgado.isoformat(),
                )
            )

        premissas_itens.append(
            ItemMemoria(
                "Quantidade de verbas deferidas",
                str(len(entrada.sentenca.verbas_deferidas)),
            )
        )

        for indice, premissa in enumerate(
            entrada.premissas,
            start=1,
        ):
            premissas_itens.append(
                ItemMemoria(
                    f"Premissa {indice}",
                    premissa,
                )
            )

        titulo_judicial = SecaoMemoria(
            ordem=2,
            tipo=TipoSecaoMemoria.PREMISSAS,
            titulo="Título judicial e premissas",
            itens=tuple(premissas_itens),
        )

        linhas_verbas = tuple(
            LinhaTabelaFinanceira(
                chave=item.codigo_verba,
                descricao=item.descricao,
                valor=item.valor,
            )
            for item in origem.itens
        )

        tabela_verbas = TabelaFinanceira(
            titulo="Verbas apuradas",
            colunas=("Código", "Descrição", "Valor"),
            linhas=linhas_verbas,
            total=consolidado.subtotal,
        )

        demonstrativo_itens = tuple(
            ItemMemoria(
                rotulo=item.descricao,
                valor=(
                    f"{item.valor.moeda} "
                    f"{format(item.valor.valor, 'f')}"
                ),
                formula_codigo=item.formula_codigo,
            )
            for item in origem.itens
        )

        demonstrativo = SecaoMemoria(
            ordem=3,
            tipo=TipoSecaoMemoria.DEMONSTRATIVO,
            titulo="Demonstrativo das verbas",
            itens=demonstrativo_itens,
            tabelas=(tabela_verbas,),
        )

        atualizacao = resultado.atualizacao

        consolidacao = SecaoMemoria(
            ordem=4,
            tipo=TipoSecaoMemoria.CONSOLIDACAO,
            titulo="Consolidação e atualização",
            itens=(
                ItemMemoria(
                    "Subtotal nominal",
                    (
                        f"{consolidado.subtotal.moeda} "
                        f"{format(consolidado.subtotal.valor, 'f')}"
                    ),
                ),
                ItemMemoria(
                    "Valor após correção monetária",
                    (
                        f"{atualizacao.correcao.valor_atualizado.moeda} "
                        f"{format(atualizacao.correcao.valor_atualizado.valor, 'f')}"
                    ),
                    formula_codigo=(
                        atualizacao.correcao.formula_codigo
                    ),
                    fundamento=(
                        atualizacao.correcao.fator.fundamento
                    ),
                ),
                ItemMemoria(
                    "Valor final com juros",
                    (
                        f"{resultado.valor_final.moeda} "
                        f"{format(resultado.valor_final.valor, 'f')}"
                    ),
                    formula_codigo=(
                        atualizacao.formula_codigo
                    ),
                    fundamento=(
                        atualizacao.juros.fator.fundamento
                    ),
                ),
            ),
        )

        observacoes = []

        for premissa in entrada.premissas:
            observacoes.append(
                ObservacaoTecnica(
                    texto=premissa,
                    nivel=NivelObservacaoTecnica.ATENCAO,
                )
            )

        observacoes.append(
            ObservacaoTecnica(
                texto=(
                    "Os valores foram produzidos por motores "
                    "determinísticos do domínio trabalhista."
                ),
                nivel=NivelObservacaoTecnica.INFORMATIVA,
            )
        )

        observacoes.append(
            ObservacaoTecnica(
                texto=(
                    "A memória depende da correção dos parâmetros "
                    "informados para o caso concreto."
                ),
                nivel=NivelObservacaoTecnica.LIMITACAO,
            )
        )

        conclusao = SecaoMemoria(
            ordem=5,
            tipo=TipoSecaoMemoria.CONCLUSAO,
            titulo="Conclusão",
            itens=(
                ItemMemoria(
                    "Valor final da liquidação",
                    (
                        f"{resultado.valor_final.moeda} "
                        f"{format(resultado.valor_final.valor, 'f')}"
                    ),
                    formula_codigo=(
                        resultado.atualizacao.formula_codigo
                    ),
                ),
                ItemMemoria(
                    "Versão do gerador",
                    cls.VERSAO,
                ),
            ),
        )

        return MemoriaCalculoProfissional(
            titulo="MEMÓRIA DE CÁLCULO JUDICIAL — SGM",
            referencia=entrada.referencia_processo,
            secoes=(
                identificacao,
                titulo_judicial,
                demonstrativo,
                consolidacao,
                conclusao,
            ),
            observacoes=tuple(observacoes),
            versao_documento=cls.VERSAO,
        )
