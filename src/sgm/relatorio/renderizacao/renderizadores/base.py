from __future__ import annotations

from abc import ABC, abstractmethod

from sgm.relatorio.geracao import RelatorioTecnicoGerado
from sgm.relatorio.renderizacao.documento_renderizado import (
    DocumentoRenderizado,
)


class RenderizadorBase(ABC):
    VERSAO = "0.9.2-E3"

    @abstractmethod
    def renderizar(
        self,
        relatorio: RelatorioTecnicoGerado,
    ) -> DocumentoRenderizado:
        raise NotImplementedError
