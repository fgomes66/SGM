from enum import StrEnum


class FormatoExportacao(StrEnum):
    PDF = "PDF"
    DOCX = "DOCX"
    XLSX = "XLSX"
    CSV = "CSV"

    @property
    def extensao(self) -> str:
        return self.value.lower()
