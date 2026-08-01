from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape
import zipfile

from sgm.exportacao.documento_exportavel import DocumentoExportavel
from sgm.exportacao.exportadores.base import ExportadorBase


class ExportadorDOCX(ExportadorBase):
    def exportar(
        self,
        documento: DocumentoExportavel,
        destino: Path,
        sobrescrever: bool = False,
    ) -> Path:
        destino = self.preparar_destino(destino, sobrescrever)

        paragrafos = []
        for linha in documento.texto_integral().splitlines():
            if linha:
                paragrafos.append(
                    "<w:p><w:r><w:t xml:space=\"preserve\">"
                    f"{escape(linha)}"
                    "</w:t></w:r></w:p>"
                )
            else:
                paragrafos.append("<w:p/>")

        documento_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document '
            'xmlns:w="http://schemas.openxmlformats.org/'
            'wordprocessingml/2006/main">'
            "<w:body>"
            + "".join(paragrafos)
            + "<w:sectPr>"
            '<w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1134" w:right="1134" '
            'w:bottom="1134" w:left="1134"/>'
            "</w:sectPr></w:body></w:document>"
        )

        content_types = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/'
            'package/2006/content-types">'
            '<Default Extension="rels" '
            'ContentType="application/vnd.openxmlformats-package.'
            'relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'wordprocessingml.document.main+xml"/>'
            "</Types>"
        )

        rels = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/'
            'package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/>'
            "</Relationships>"
        )

        with zipfile.ZipFile(
            destino,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as arquivo:
            arquivo.writestr("[Content_Types].xml", content_types)
            arquivo.writestr("_rels/.rels", rels)
            arquivo.writestr("word/document.xml", documento_xml)

        return destino
