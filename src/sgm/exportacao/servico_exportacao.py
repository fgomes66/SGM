from __future__ import annotations

from pathlib import Path

from sgm.exportacao.documento_exportavel import DocumentoExportavel
from sgm.exportacao.exportadores import (
    ExportadorCSV,
    ExportadorDOCX,
    ExportadorPDF,
    ExportadorXLSX,
)
from sgm.exportacao.formato_exportacao import FormatoExportacao
from sgm.exportacao.nome_arquivo import montar_nome_arquivo


class ServicoExportacao:
    EXPORTADORES = {
        FormatoExportacao.PDF: ExportadorPDF,
        FormatoExportacao.DOCX: ExportadorDOCX,
        FormatoExportacao.XLSX: ExportadorXLSX,
        FormatoExportacao.CSV: ExportadorCSV,
    }

    @classmethod
    def exportar(
        cls,
        documento: DocumentoExportavel,
        formato: FormatoExportacao,
        pasta: Path,
        sufixo: str = "relatorio",
        sobrescrever: bool = False,
    ) -> Path:
        if not isinstance(formato, FormatoExportacao):
            raise TypeError(
                "O formato deve ser uma instância de FormatoExportacao."
            )

        pasta = Path(pasta)
        pasta.mkdir(parents=True, exist_ok=True)

        nome = montar_nome_arquivo(
            documento.referencia,
            formato,
            sufixo,
        )
        destino = pasta / nome
        exportador = cls.EXPORTADORES[formato]()
        return exportador.exportar(
            documento,
            destino,
            sobrescrever=sobrescrever,
        )

    @classmethod
    def exportar_todos(
        cls,
        documento: DocumentoExportavel,
        pasta: Path,
        sufixo: str = "relatorio",
        sobrescrever: bool = False,
    ) -> tuple[Path, ...]:
        return tuple(
            cls.exportar(
                documento=documento,
                formato=formato,
                pasta=pasta,
                sufixo=sufixo,
                sobrescrever=sobrescrever,
            )
            for formato in FormatoExportacao
        )
