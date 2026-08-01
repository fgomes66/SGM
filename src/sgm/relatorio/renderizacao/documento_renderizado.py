from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.relatorio.renderizacao.formato_renderizacao import (
    FormatoRenderizacao,
)


@dataclass(frozen=True, slots=True)
class DocumentoRenderizado:
    formato: FormatoRenderizacao
    referencia: str
    conteudo: str
    mime_type: str
    versao_renderizador: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        referencia = self.referencia.strip()
        conteudo = self.conteudo.strip()
        mime_type = self.mime_type.strip()
        versao = self.versao_renderizador.strip()

        object.__setattr__(self, "referencia", referencia)
        object.__setattr__(self, "conteudo", conteudo)
        object.__setattr__(self, "mime_type", mime_type)
        object.__setattr__(self, "versao_renderizador", versao)

        if not referencia:
            raise ValueError("A referência renderizada é obrigatória.")

        if not conteudo:
            raise ValueError("O conteúdo renderizado é obrigatório.")

        if not mime_type:
            raise ValueError("O MIME type é obrigatório.")

        if not versao:
            raise ValueError(
                "A versão do renderizador é obrigatória."
            )
