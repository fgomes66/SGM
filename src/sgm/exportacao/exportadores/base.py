from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from sgm.exportacao.documento_exportavel import DocumentoExportavel


class ExportadorBase(ABC):
    @abstractmethod
    def exportar(
        self,
        documento: DocumentoExportavel,
        destino: Path,
        sobrescrever: bool = False,
    ) -> Path:
        raise NotImplementedError

    @staticmethod
    def preparar_destino(
        destino: Path,
        sobrescrever: bool,
    ) -> Path:
        destino = Path(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)

        if destino.exists() and not sobrescrever:
            raise FileExistsError(
                f"O arquivo já existe: {destino}"
            )

        return destino
