from __future__ import annotations

from sgm.relatorio.geracao import RelatorioTecnicoGerado
from sgm.relatorio.renderizacao.documento_renderizado import (
    DocumentoRenderizado,
)
from sgm.relatorio.renderizacao.formato_renderizacao import (
    FormatoRenderizacao,
)
from sgm.relatorio.renderizacao.renderizadores import (
    RenderizadorHTML,
    RenderizadorMarkdown,
    RenderizadorTexto,
)


class ServicoRenderizacao:
    RENDERIZADORES = {
        FormatoRenderizacao.TEXTO: RenderizadorTexto,
        FormatoRenderizacao.MARKDOWN: RenderizadorMarkdown,
        FormatoRenderizacao.HTML: RenderizadorHTML,
    }

    @classmethod
    def renderizar(
        cls,
        relatorio: RelatorioTecnicoGerado,
        formato: FormatoRenderizacao,
    ) -> DocumentoRenderizado:
        if not isinstance(formato, FormatoRenderizacao):
            raise TypeError(
                "O formato deve ser uma instância de FormatoRenderizacao."
            )

        renderizador = cls.RENDERIZADORES[formato]()
        return renderizador.renderizar(relatorio)

    @classmethod
    def renderizar_todos(
        cls,
        relatorio: RelatorioTecnicoGerado,
    ) -> tuple[DocumentoRenderizado, ...]:
        return tuple(
            cls.renderizar(relatorio, formato)
            for formato in FormatoRenderizacao
        )
