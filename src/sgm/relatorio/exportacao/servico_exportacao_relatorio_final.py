from __future__ import annotations

from pathlib import Path

from sgm.exportacao.exportadores import ExportadorDOCX, ExportadorPDF
from sgm.exportacao.nome_arquivo import normalizar_nome
from sgm.relatorio.exportacao.adaptador_relatorio_exportavel import (
    AdaptadorRelatorioExportavel,
)
from sgm.relatorio.exportacao.formato_relatorio_final import (
    FormatoRelatorioFinal,
)
from sgm.relatorio.exportacao.resultado_exportacao_relatorio import (
    ResultadoExportacaoRelatorio,
)
from sgm.relatorio.geracao import RelatorioTecnicoGerado
from sgm.relatorio.renderizacao import (
    FormatoRenderizacao,
    ServicoRenderizacao,
)


class ServicoExportacaoRelatorioFinal:
    VERSAO = "0.9.2-E4"

    FORMATO_RENDERIZACAO = {
        FormatoRelatorioFinal.TXT: FormatoRenderizacao.TEXTO,
        FormatoRelatorioFinal.MARKDOWN: FormatoRenderizacao.MARKDOWN,
        FormatoRelatorioFinal.HTML: FormatoRenderizacao.HTML,
    }

    @classmethod
    def _nome(
        cls,
        relatorio: RelatorioTecnicoGerado,
        formato: FormatoRelatorioFinal,
        sufixo: str,
    ) -> str:
        referencia = normalizar_nome(
            relatorio.relatorio.referencia
        )
        sufixo = normalizar_nome(sufixo)
        return f"{referencia}_{sufixo}.{formato.extensao}"

    @staticmethod
    def _preparar_destino(
        pasta: Path,
        nome: str,
        sobrescrever: bool,
    ) -> Path:
        pasta = Path(pasta)
        pasta.mkdir(parents=True, exist_ok=True)
        destino = pasta / nome

        if destino.exists() and not sobrescrever:
            raise FileExistsError(
                f"O arquivo já existe: {destino}"
            )

        return destino

    @classmethod
    def exportar(
        cls,
        relatorio: RelatorioTecnicoGerado,
        formato: FormatoRelatorioFinal,
        pasta: Path,
        sufixo: str = "relatorio_tecnico",
        sobrescrever: bool = False,
    ) -> ResultadoExportacaoRelatorio:
        if not isinstance(formato, FormatoRelatorioFinal):
            raise TypeError(
                "O formato deve ser uma instância de "
                "FormatoRelatorioFinal."
            )

        nome = cls._nome(relatorio, formato, sufixo)
        destino = cls._preparar_destino(
            pasta,
            nome,
            sobrescrever,
        )

        if formato in cls.FORMATO_RENDERIZACAO:
            renderizado = ServicoRenderizacao.renderizar(
                relatorio,
                cls.FORMATO_RENDERIZACAO[formato],
            )
            destino.write_text(
                renderizado.conteudo,
                encoding="utf-8",
            )

        elif formato == FormatoRelatorioFinal.PDF:
            texto = ServicoRenderizacao.renderizar(
                relatorio,
                FormatoRenderizacao.TEXTO,
            ).conteudo
            adaptador = AdaptadorRelatorioExportavel(
                relatorio,
                texto,
            )
            ExportadorPDF().exportar(
                adaptador,
                destino,
                sobrescrever=sobrescrever,
            )

        elif formato == FormatoRelatorioFinal.DOCX:
            texto = ServicoRenderizacao.renderizar(
                relatorio,
                FormatoRenderizacao.TEXTO,
            ).conteudo
            adaptador = AdaptadorRelatorioExportavel(
                relatorio,
                texto,
            )
            ExportadorDOCX().exportar(
                adaptador,
                destino,
                sobrescrever=sobrescrever,
            )

        return ResultadoExportacaoRelatorio(
            formato=formato,
            caminho=destino,
            tamanho_bytes=destino.stat().st_size,
        )

    @classmethod
    def exportar_todos(
        cls,
        relatorio: RelatorioTecnicoGerado,
        pasta: Path,
        sufixo: str = "relatorio_tecnico",
        sobrescrever: bool = False,
    ) -> tuple[ResultadoExportacaoRelatorio, ...]:
        return tuple(
            cls.exportar(
                relatorio=relatorio,
                formato=formato,
                pasta=pasta,
                sufixo=sufixo,
                sobrescrever=sobrescrever,
            )
            for formato in FormatoRelatorioFinal
        )
