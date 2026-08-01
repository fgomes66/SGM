from __future__ import annotations

import hashlib
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from sgm.dominio.trabalhista import (
    GeradorDemonstrativoFinanceiro,
    GeradorLinhaTempoProfissional,
    GeradorMemoriaProfissional,
)
from sgm.relatorio import (
    GeradorRelatorioTecnico,
    IdentificacaoProcesso,
    MetadadosRelatorio,
    OrgaoJulgador,
    ParametrosRelatorio,
    RelatorioTecnico,
    ServicoExportacaoRelatorioFinal,
    TipoRelatorio,
)
from sgm.homologacao.resultado_homologacao import ResultadoHomologacao


class ServicoHomologacaoFinal:
    VERSAO = "0.9.2-E5"

    @classmethod
    def homologar(
        cls,
        resultado_caso_temporal,
        pasta_saida: Path,
        numero_processo: str = "0001234-55.2024.5.01.0007",
        reclamante: str = "Fulano de Tal",
        reclamada: str = "Empresa XYZ Ltda.",
        magistrado: str | None = "Dra. Maria da Silva",
        perito: str | None = "João Perito",
    ) -> ResultadoHomologacao:
        memoria = GeradorMemoriaProfissional.gerar(
            resultado_caso_temporal
        )
        demonstrativo = GeradorDemonstrativoFinanceiro.gerar(
            resultado_caso_temporal
        )
        linha_tempo = GeradorLinhaTempoProfissional.gerar(
            resultado_caso_temporal
        )

        orgao = OrgaoJulgador(
            tribunal="Tribunal Regional do Trabalho",
            regiao_trt=1,
            vara="7ª Vara do Trabalho do Rio de Janeiro",
            municipio="Rio de Janeiro",
            uf="RJ",
        )
        identificacao = IdentificacaoProcesso(
            orgao_julgador=orgao,
            numero_processo=numero_processo,
            classe_processual="Reclamação Trabalhista",
            reclamante=reclamante,
            reclamada=reclamada,
            magistrado=magistrado,
            perito=perito,
        )

        eventos = tuple(
            marco
            for marco in linha_tempo.marcos
            if marco.tipo.value not in (
                "INICIO_PERIODO",
                "FIM_PERIODO",
            )
        )

        data_emissao = datetime(
            2026,
            7,
            31,
            22,
            0,
            tzinfo=timezone.utc,
        )

        conteudo_integridade = "\n".join(
            (
                memoria.como_texto(),
                demonstrativo.como_texto(),
                linha_tempo.como_texto(),
                numero_processo,
                reclamante,
                reclamada,
                data_emissao.isoformat(),
                cls.VERSAO,
            )
        )
        hash_sha256 = hashlib.sha256(
            conteudo_integridade.encode("utf-8")
        ).hexdigest()

        metadados = MetadadosRelatorio(
            uuid=uuid5(NAMESPACE_URL, hash_sha256),
            hash_sha256=hash_sha256,
            versao_sgm=cls.VERSAO,
            versao_regras="2026.1",
            data_emissao=data_emissao,
            quantidade_competencias=len(
                demonstrativo.competencias
            ),
            quantidade_verbas=len(demonstrativo.verbas),
            quantidade_eventos=len(eventos),
        )

        parametros = ParametrosRelatorio(
            periodo_analisado=(
                f"{resultado_caso_temporal.plano.periodo.inicio.como_texto()}"
                " a "
                f"{resultado_caso_temporal.plano.periodo.fim.como_texto()}"
            ),
            indice_correcao=(
                "Fatores monetários definidos no plano temporal."
            ),
            juros="Fatores de juros definidos no plano temporal.",
            moeda=demonstrativo.subtotal_geral.moeda,
            observacoes=(
                "Relatório final gerado sem recálculo documental.",
                "Resultados consolidados por competência.",
            ),
        )

        modelo = RelatorioTecnico(
            tipo=TipoRelatorio.RELATORIO_TECNICO,
            identificacao=identificacao,
            metadados=metadados,
            parametros=parametros,
            memoria=memoria,
            demonstrativo=demonstrativo,
            linha_tempo=linha_tempo,
        )

        relatorio = GeradorRelatorioTecnico.gerar(modelo)
        exportacoes = (
            ServicoExportacaoRelatorioFinal.exportar_todos(
                relatorio,
                pasta_saida,
                sufixo="relatorio_tecnico_final",
            )
        )

        return ResultadoHomologacao(
            referencia=resultado_caso_temporal.plano.referencia,
            relatorio=relatorio,
            exportacoes=exportacoes,
            pasta_saida=Path(pasta_saida),
        )
