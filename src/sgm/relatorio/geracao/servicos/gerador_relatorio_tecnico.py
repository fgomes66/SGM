from __future__ import annotations

from sgm.relatorio.geracao.relatorio_tecnico_gerado import (
    RelatorioTecnicoGerado,
)
from sgm.relatorio.geracao.secao_relatorio import SecaoRelatorio
from sgm.relatorio.geracao.tipo_secao_relatorio import (
    TipoSecaoRelatorio,
)
from sgm.relatorio.relatorio_tecnico import RelatorioTecnico


class GeradorRelatorioTecnico:
    VERSAO = "0.9.2-E2"

    @staticmethod
    def _capa(relatorio: RelatorioTecnico) -> SecaoRelatorio:
        identificacao = relatorio.identificacao
        linhas = [
            "PODER JUDICIÁRIO",
            "JUSTIÇA DO TRABALHO",
            identificacao.orgao_julgador.descricao_completa,
            relatorio.titulo,
            f"Processo: {identificacao.numero_processo}",
            f"Reclamante: {identificacao.reclamante}",
            f"Reclamada: {identificacao.reclamada}",
        ]
        if identificacao.magistrado:
            linhas.append(
                f"Magistrado(a): {identificacao.magistrado}"
            )
        if identificacao.perito:
            linhas.append(f"Perito(a): {identificacao.perito}")

        linhas.extend(
            (
                (
                    "Data de emissão: "
                    f"{relatorio.metadados.data_emissao.isoformat()}"
                ),
                f"Versão SGM: {relatorio.metadados.versao_sgm}",
            )
        )

        return SecaoRelatorio(
            ordem=1,
            tipo=TipoSecaoRelatorio.CAPA,
            titulo="Capa",
            linhas=tuple(linhas),
        )

    @staticmethod
    def _sumario() -> SecaoRelatorio:
        itens = (
            "1. Capa",
            "2. Sumário",
            "3. Introdução",
            "4. Dados processuais",
            "5. Metodologia",
            "6. Linha do tempo",
            "7. Critérios jurídicos",
            "8. Memória de cálculo",
            "9. Demonstrativo financeiro",
            "10. Atualização monetária",
            "11. Conclusão técnica",
            "12. Assinatura técnica",
        )
        return SecaoRelatorio(
            ordem=2,
            tipo=TipoSecaoRelatorio.SUMARIO,
            titulo="Sumário",
            linhas=itens,
        )

    @staticmethod
    def _introducao() -> SecaoRelatorio:
        return SecaoRelatorio(
            ordem=3,
            tipo=TipoSecaoRelatorio.INTRODUCAO,
            titulo="Introdução",
            linhas=(
                (
                    "O presente relatório técnico foi elaborado "
                    "automaticamente pelo SGM a partir de objetos "
                    "previamente calculados e homologados."
                ),
                (
                    "Os resultados permanecem rastreáveis por "
                    "competência, verba e evento contratual."
                ),
                (
                    "A geração documental não recalcula, não altera "
                    "e não reordena valores financeiros."
                ),
            ),
        )

    @staticmethod
    def _dados_processuais(
        relatorio: RelatorioTecnico,
    ) -> SecaoRelatorio:
        identificacao = relatorio.identificacao
        linhas = list(relatorio.resumo_identificacao())
        linhas.extend(
            (
                f"Versão das regras: {relatorio.metadados.versao_regras}",
                f"UUID documental: {relatorio.metadados.uuid}",
                (
                    "Competências calculadas: "
                    f"{relatorio.metadados.quantidade_competencias}"
                ),
                (
                    "Verbas consolidadas: "
                    f"{relatorio.metadados.quantidade_verbas}"
                ),
                (
                    "Eventos contratuais: "
                    f"{relatorio.metadados.quantidade_eventos}"
                ),
            )
        )

        opcionais = (
            ("Assistente do reclamante", identificacao.assistente_reclamante),
            ("Assistente da reclamada", identificacao.assistente_reclamada),
            ("Advogado do reclamante", identificacao.advogado_reclamante),
            ("Advogado da reclamada", identificacao.advogado_reclamada),
        )
        for rotulo, valor in opcionais:
            if valor:
                linhas.append(f"{rotulo}: {valor}")

        return SecaoRelatorio(
            ordem=4,
            tipo=TipoSecaoRelatorio.DADOS_PROCESSUAIS,
            titulo="Dados processuais",
            linhas=tuple(linhas),
        )

    @staticmethod
    def _metodologia(
        relatorio: RelatorioTecnico,
    ) -> SecaoRelatorio:
        return SecaoRelatorio(
            ordem=5,
            tipo=TipoSecaoRelatorio.METODOLOGIA,
            titulo="Metodologia",
            linhas=(
                "Aplicação prospectiva dos eventos contratuais.",
                "Geração de planos independentes por competência.",
                "Cálculo financeiro por competência.",
                "Consolidação cronológica dos resultados mensais.",
                "Classificação financeira por verba e natureza.",
                (
                    "Correção monetária: "
                    f"{relatorio.parametros.indice_correcao}"
                ),
                f"Juros: {relatorio.parametros.juros}",
                f"Moeda: {relatorio.parametros.moeda}",
            ),
        )

    @staticmethod
    def _linha_tempo(
        relatorio: RelatorioTecnico,
    ) -> SecaoRelatorio:
        return SecaoRelatorio(
            ordem=6,
            tipo=TipoSecaoRelatorio.LINHA_TEMPO,
            titulo="Linha do tempo",
            linhas=tuple(
                relatorio.linha_tempo.como_texto().splitlines()
            ),
        )

    @staticmethod
    def _criterios_juridicos(
        relatorio: RelatorioTecnico,
    ) -> SecaoRelatorio:
        linhas = [
            "Horas extras e adicional parametrizado.",
            "DSR e reflexos conforme configurações de incidência.",
            "FGTS conforme alíquota informada no plano.",
            "Férias e adicional constitucional parametrizados.",
            "13º salário proporcional parametrizado.",
            "Aviso-prévio conforme modalidade e dias informados.",
            (
                "Critério de atualização: "
                f"{relatorio.parametros.indice_correcao}"
            ),
            f"Critério de juros: {relatorio.parametros.juros}",
        ]
        linhas.extend(relatorio.parametros.observacoes)

        return SecaoRelatorio(
            ordem=7,
            tipo=TipoSecaoRelatorio.CRITERIOS_JURIDICOS,
            titulo="Critérios jurídicos e parâmetros",
            linhas=tuple(linhas),
        )

    @staticmethod
    def _memoria(
        relatorio: RelatorioTecnico,
    ) -> SecaoRelatorio:
        return SecaoRelatorio(
            ordem=8,
            tipo=TipoSecaoRelatorio.MEMORIA_CALCULO,
            titulo="Memória de cálculo",
            linhas=tuple(
                relatorio.memoria.como_texto().splitlines()
            ),
        )

    @staticmethod
    def _demonstrativo(
        relatorio: RelatorioTecnico,
    ) -> SecaoRelatorio:
        return SecaoRelatorio(
            ordem=9,
            tipo=TipoSecaoRelatorio.DEMONSTRATIVO_FINANCEIRO,
            titulo="Demonstrativo financeiro",
            linhas=tuple(
                relatorio.demonstrativo.como_texto().splitlines()
            ),
        )

    @staticmethod
    def _atualizacao(
        relatorio: RelatorioTecnico,
    ) -> SecaoRelatorio:
        demonstrativo = relatorio.demonstrativo
        diferenca = (
            demonstrativo.valor_final_geral.valor
            - demonstrativo.subtotal_geral.valor
        )
        return SecaoRelatorio(
            ordem=10,
            tipo=TipoSecaoRelatorio.ATUALIZACAO_MONETARIA,
            titulo="Atualização monetária e juros",
            linhas=(
                (
                    "Valor histórico consolidado: "
                    f"{demonstrativo.subtotal_geral.moeda} "
                    f"{format(demonstrativo.subtotal_geral.valor, 'f')}"
                ),
                (
                    "Acréscimo total de atualização e juros: "
                    f"{demonstrativo.valor_final_geral.moeda} "
                    f"{format(diferenca, 'f')}"
                ),
                (
                    "Valor final atualizado: "
                    f"{demonstrativo.valor_final_geral.moeda} "
                    f"{format(demonstrativo.valor_final_geral.valor, 'f')}"
                ),
            ),
        )

    @staticmethod
    def _conclusao(
        relatorio: RelatorioTecnico,
    ) -> SecaoRelatorio:
        demonstrativo = relatorio.demonstrativo
        return SecaoRelatorio(
            ordem=11,
            tipo=TipoSecaoRelatorio.CONCLUSAO,
            titulo="Conclusão técnica",
            linhas=(
                (
                    "Após aplicação dos critérios parametrizados, "
                    "o crédito trabalhista apurado totaliza "
                    f"{demonstrativo.valor_final_geral.moeda} "
                    f"{format(demonstrativo.valor_final_geral.valor, 'f')}."
                ),
                (
                    "As parcelas encontram-se discriminadas por "
                    "competência, verba, natureza e evento contratual."
                ),
                (
                    "O relatório representa os resultados homologados "
                    "sem alteração manual posterior."
                ),
            ),
        )

    @staticmethod
    def _assinatura(
        relatorio: RelatorioTecnico,
    ) -> SecaoRelatorio:
        linhas = [
            "Documento produzido automaticamente pelo SGM.",
            f"Versão SGM: {relatorio.metadados.versao_sgm}",
            f"Versão das regras: {relatorio.metadados.versao_regras}",
            f"UUID: {relatorio.metadados.uuid}",
            f"SHA-256 informado: {relatorio.metadados.hash_sha256}",
            (
                "Data e hora: "
                f"{relatorio.metadados.data_emissao.isoformat()}"
            ),
        ]
        if relatorio.identificacao.perito:
            linhas.append(
                f"Responsável técnico: {relatorio.identificacao.perito}"
            )
        else:
            linhas.append(
                "Responsável técnico: não informado."
            )

        return SecaoRelatorio(
            ordem=12,
            tipo=TipoSecaoRelatorio.ASSINATURA_TECNICA,
            titulo="Assinatura técnica",
            linhas=tuple(linhas),
        )

    @classmethod
    def gerar(
        cls,
        relatorio: RelatorioTecnico,
    ) -> RelatorioTecnicoGerado:
        secoes = (
            cls._capa(relatorio),
            cls._sumario(),
            cls._introducao(),
            cls._dados_processuais(relatorio),
            cls._metodologia(relatorio),
            cls._linha_tempo(relatorio),
            cls._criterios_juridicos(relatorio),
            cls._memoria(relatorio),
            cls._demonstrativo(relatorio),
            cls._atualizacao(relatorio),
            cls._conclusao(relatorio),
            cls._assinatura(relatorio),
        )

        conteudo_base_hash = "\n\n".join(
            secao.como_texto() for secao in secoes
        )

        return RelatorioTecnicoGerado(
            relatorio=relatorio,
            secoes=secoes,
            conteudo_base_hash=conteudo_base_hash,
            versao_gerador=cls.VERSAO,
        )
