from __future__ import annotations

from sgm.relatorio.geracao import RelatorioTecnicoGerado
from sgm.relatorio.renderizacao.documento_renderizado import (
    DocumentoRenderizado,
)
from sgm.relatorio.renderizacao.formato_renderizacao import (
    FormatoRenderizacao,
)
from sgm.relatorio.renderizacao.renderizadores.base import (
    RenderizadorBase,
)


class RenderizadorTexto(RenderizadorBase):
    def renderizar(
        self,
        relatorio: RelatorioTecnicoGerado,
    ) -> DocumentoRenderizado:
        return DocumentoRenderizado(
            formato=FormatoRenderizacao.TEXTO,
            referencia=relatorio.relatorio.referencia,
            conteudo=relatorio.como_texto(),
            mime_type="text/plain; charset=utf-8",
            versao_renderizador=self.VERSAO,
        )
