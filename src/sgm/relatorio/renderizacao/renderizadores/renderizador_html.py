from __future__ import annotations

from html import escape

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


class RenderizadorHTML(RenderizadorBase):
    def renderizar(
        self,
        relatorio: RelatorioTecnicoGerado,
    ) -> DocumentoRenderizado:
        secoes = []

        for secao in relatorio.secoes:
            itens = "".join(
                f"<li>{escape(linha)}</li>"
                for linha in secao.linhas
            )
            secoes.append(
                "<section "
                f'data-tipo="{escape(secao.tipo.value)}">'
                f"<h2>{secao.ordem}. {escape(secao.titulo)}</h2>"
                f"<ul>{itens}</ul>"
                "</section>"
            )

        conteudo = (
            "<!DOCTYPE html>"
            '<html lang="pt-BR">'
            "<head>"
            '<meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f"<title>{escape(relatorio.relatorio.titulo)}</title>"
            "</head>"
            "<body>"
            "<main>"
            f"<h1>{escape(relatorio.relatorio.titulo)}</h1>"
            f"<p><strong>Referência:</strong> "
            f"{escape(relatorio.relatorio.referencia)}</p>"
            f"<p><strong>Versão do gerador:</strong> "
            f"{escape(relatorio.versao_gerador)}</p>"
            + "".join(secoes)
            + "</main></body></html>"
        )

        return DocumentoRenderizado(
            formato=FormatoRenderizacao.HTML,
            referencia=relatorio.relatorio.referencia,
            conteudo=conteudo,
            mime_type="text/html; charset=utf-8",
            versao_renderizador=self.VERSAO,
        )
