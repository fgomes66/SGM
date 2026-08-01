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


def _escapar_markdown(texto: str) -> str:
    for caractere in ("\\", "`", "*", "_", "{", "}", "[", "]"):
        texto = texto.replace(caractere, f"\\{caractere}")
    return texto


class RenderizadorMarkdown(RenderizadorBase):
    def renderizar(
        self,
        relatorio: RelatorioTecnicoGerado,
    ) -> DocumentoRenderizado:
        blocos = [
            f"# {_escapar_markdown(relatorio.relatorio.titulo)}",
            (
                f"**Referência:** "
                f"{_escapar_markdown(relatorio.relatorio.referencia)}"
            ),
            (
                f"**Versão do gerador:** "
                f"{_escapar_markdown(relatorio.versao_gerador)}"
            ),
        ]

        for secao in relatorio.secoes:
            linhas = [
                f"## {secao.ordem}. {_escapar_markdown(secao.titulo)}"
            ]
            linhas.extend(
                f"- {_escapar_markdown(linha)}"
                for linha in secao.linhas
            )
            blocos.append("\n".join(linhas))

        return DocumentoRenderizado(
            formato=FormatoRenderizacao.MARKDOWN,
            referencia=relatorio.relatorio.referencia,
            conteudo="\n\n".join(blocos),
            mime_type="text/markdown; charset=utf-8",
            versao_renderizador=self.VERSAO,
        )
