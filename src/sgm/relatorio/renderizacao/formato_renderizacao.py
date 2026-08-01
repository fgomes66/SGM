from enum import StrEnum


class FormatoRenderizacao(StrEnum):
    TEXTO = "TEXTO"
    MARKDOWN = "MARKDOWN"
    HTML = "HTML"

    @property
    def extensao(self) -> str:
        return {
            FormatoRenderizacao.TEXTO: "txt",
            FormatoRenderizacao.MARKDOWN: "md",
            FormatoRenderizacao.HTML: "html",
        }[self]
