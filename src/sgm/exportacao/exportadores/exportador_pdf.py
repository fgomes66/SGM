from __future__ import annotations

from pathlib import Path

from sgm.exportacao.documento_exportavel import DocumentoExportavel
from sgm.exportacao.exportadores.base import ExportadorBase


def _escapar_pdf(texto: str) -> str:
    texto = texto.replace("\\", "\\\\")
    texto = texto.replace("(", "\\(")
    texto = texto.replace(")", "\\)")
    return texto


def _latin1_seguro(texto: str) -> str:
    return texto.encode(
        "latin-1",
        errors="replace",
    ).decode("latin-1")


class ExportadorPDF(ExportadorBase):
    LINHAS_POR_PAGINA = 48

    def exportar(
        self,
        documento: DocumentoExportavel,
        destino: Path,
        sobrescrever: bool = False,
    ) -> Path:
        destino = self.preparar_destino(destino, sobrescrever)

        linhas = [
            _latin1_seguro(linha)
            for linha in documento.texto_integral().splitlines()
        ]
        paginas = [
            linhas[indice:indice + self.LINHAS_POR_PAGINA]
            for indice in range(0, len(linhas), self.LINHAS_POR_PAGINA)
        ] or [[]]

        objetos: list[bytes] = []
        objetos.append(b"<< /Type /Catalog /Pages 2 0 R >>")
        objetos.append(b"")  # páginas preenchidas depois
        objetos.append(
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
        )

        ids_paginas = []
        for pagina in paginas:
            comandos = [
                "BT",
                "/F1 9 Tf",
                "50 790 Td",
                "11 TL",
            ]
            for linha in pagina:
                comandos.append(
                    f"({_escapar_pdf(linha)}) Tj"
                )
                comandos.append("T*")
            comandos.append("ET")
            fluxo = "\n".join(comandos).encode("latin-1")

            id_conteudo = len(objetos) + 1
            objetos.append(
                (
                    f"<< /Length {len(fluxo)} >>\nstream\n"
                ).encode("ascii")
                + fluxo
                + b"\nendstream"
            )

            id_pagina = len(objetos) + 1
            objetos.append(
                (
                    "<< /Type /Page /Parent 2 0 R "
                    "/MediaBox [0 0 595 842] "
                    "/Resources << /Font << /F1 3 0 R >> >> "
                    f"/Contents {id_conteudo} 0 R >>"
                ).encode("ascii")
            )
            ids_paginas.append(id_pagina)

        filhos = " ".join(
            f"{identificador} 0 R"
            for identificador in ids_paginas
        )
        objetos[1] = (
            f"<< /Type /Pages /Kids [{filhos}] "
            f"/Count {len(ids_paginas)} >>"
        ).encode("ascii")

        conteudo = bytearray(b"%PDF-1.4\n%SGM\n")
        offsets = [0]

        for indice, objeto in enumerate(objetos, start=1):
            offsets.append(len(conteudo))
            conteudo.extend(
                f"{indice} 0 obj\n".encode("ascii")
            )
            conteudo.extend(objeto)
            conteudo.extend(b"\nendobj\n")

        inicio_xref = len(conteudo)
        conteudo.extend(
            f"xref\n0 {len(objetos) + 1}\n".encode("ascii")
        )
        conteudo.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            conteudo.extend(
                f"{offset:010d} 00000 n \n".encode("ascii")
            )

        conteudo.extend(
            (
                "trailer\n"
                f"<< /Size {len(objetos) + 1} /Root 1 0 R >>\n"
                "startxref\n"
                f"{inicio_xref}\n"
                "%%EOF\n"
            ).encode("ascii")
        )

        destino.write_bytes(bytes(conteudo))
        return destino
