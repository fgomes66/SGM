from enum import StrEnum


class FormatoRelatorioFinal(StrEnum):
    TXT = "TXT"
    MARKDOWN = "MARKDOWN"
    HTML = "HTML"
    PDF = "PDF"
    DOCX = "DOCX"

    @property
    def extensao(self) -> str:
        return {
            FormatoRelatorioFinal.TXT: "txt",
            FormatoRelatorioFinal.MARKDOWN: "md",
            FormatoRelatorioFinal.HTML: "html",
            FormatoRelatorioFinal.PDF: "pdf",
            FormatoRelatorioFinal.DOCX: "docx",
        }[self]
