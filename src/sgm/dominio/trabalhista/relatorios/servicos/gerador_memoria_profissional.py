from __future__ import annotations

from sgm.dominio.trabalhista.caso_temporal import ResultadoCasoTemporal
from sgm.dominio.trabalhista.relatorios.item_memoria import ItemMemoria
from sgm.dominio.trabalhista.relatorios.linha_tabela_financeira import (
    LinhaTabelaFinanceira,
)
from sgm.dominio.trabalhista.relatorios.memoria_calculo_profissional import (
    MemoriaCalculoProfissional,
)
from sgm.dominio.trabalhista.relatorios.observacao_tecnica import (
    NivelObservacaoTecnica,
    ObservacaoTecnica,
)
from sgm.dominio.trabalhista.relatorios.secao_memoria import SecaoMemoria
from sgm.dominio.trabalhista.relatorios.tabela_financeira import (
    TabelaFinanceira,
)
from sgm.dominio.trabalhista.relatorios.tipo_secao_memoria import (
    TipoSecaoMemoria,
)


class GeradorMemoriaProfissional:
    VERSAO = "0.9.2-A"

    @classmethod
    def gerar(
        cls,
        resultado: ResultadoCasoTemporal,
    ) -> MemoriaCalculoProfissional:
        linha = resultado.linha_aplicada
        consolidado = resultado.consolidado

        identificacao = SecaoMemoria(
            ordem=1,
            tipo=TipoSecaoMemoria.IDENTIFICACAO,
            titulo="Identificação do cálculo",
            itens=(
                ItemMemoria(
                    "Referência",
                    resultado.plano.referencia,
                ),
                ItemMemoria(
                    "Período",
                    (
                        f"{resultado.plano.periodo.inicio.como_texto()} "
                        f"a "
                        f"{resultado.plano.periodo.fim.como_texto()}"
                    ),
                ),
                ItemMemoria(
                    "Motor temporal",
                    resultado.versao_motor,
                ),
            ),
        )

        itens_linha_tempo = tuple(
            ItemMemoria(
                rotulo=estado.competencia.como_texto(),
                valor=(
                    f"salário={format(estado.salario, 'f')}; "
                    f"divisor={format(estado.divisor, 'f')}; "
                    f"jornada={estado.jornada_semanal_minutos}; "
                    f"ativo={estado.ativo}; "
                    f"rescindido={estado.rescindido}"
                ),
                fundamento=(
                    ", ".join(
                        evento.fundamento
                        for evento in estado.eventos_aplicados
                    )
                    or "Sem evento na competência."
                ),
            )
            for estado in linha.estados
        )

        linha_tempo = SecaoMemoria(
            ordem=2,
            tipo=TipoSecaoMemoria.LINHA_TEMPO,
            titulo="Linha do tempo contratual",
            itens=itens_linha_tempo,
        )

        linhas_competencias = tuple(
            LinhaTabelaFinanceira(
                chave=item.competencia.como_texto(),
                descricao="Valor final da competência",
                valor=item.valor_final,
            )
            for item in resultado.resultados_mensais
        )

        tabela_competencias = TabelaFinanceira(
            titulo="Resultados mensais",
            colunas=("Competência", "Descrição", "Valor"),
            linhas=linhas_competencias,
            total=consolidado.valor_final_consolidado,
        )

        competencias = SecaoMemoria(
            ordem=3,
            tipo=TipoSecaoMemoria.COMPETENCIAS,
            titulo="Demonstrativo por competência",
            tabelas=(tabela_competencias,),
        )

        consolidacao = SecaoMemoria(
            ordem=4,
            tipo=TipoSecaoMemoria.CONSOLIDACAO,
            titulo="Consolidação financeira",
            itens=(
                ItemMemoria(
                    "Competências calculadas",
                    str(len(resultado.resultados_mensais)),
                ),
                ItemMemoria(
                    "Competências inativas",
                    str(len(linha.competencias_inativas)),
                ),
                ItemMemoria(
                    "Subtotal consolidado",
                    (
                        f"{consolidado.subtotal_consolidado.moeda} "
                        f"{format(consolidado.subtotal_consolidado.valor, 'f')}"
                    ),
                ),
                ItemMemoria(
                    "Valor final consolidado",
                    (
                        f"{consolidado.valor_final_consolidado.moeda} "
                        f"{format(consolidado.valor_final_consolidado.valor, 'f')}"
                    ),
                ),
            ),
        )

        observacoes = (
            ObservacaoTecnica(
                texto=(
                    "A memória foi gerada a partir de resultados "
                    "imutáveis e previamente calculados."
                ),
                nivel=NivelObservacaoTecnica.INFORMATIVA,
            ),
            ObservacaoTecnica(
                texto=(
                    "Esta fase estrutura o relatório, mas ainda não "
                    "gera arquivos PDF, DOCX ou XLSX."
                ),
                nivel=NivelObservacaoTecnica.LIMITACAO,
            ),
        )

        return MemoriaCalculoProfissional(
            titulo="MEMÓRIA DE CÁLCULO PROFISSIONAL — SGM",
            referencia=resultado.plano.referencia,
            secoes=(
                identificacao,
                linha_tempo,
                competencias,
                consolidacao,
            ),
            observacoes=observacoes,
            versao_documento=cls.VERSAO,
        )
