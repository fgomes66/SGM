from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sgm.relatorio.exportacao.formato_relatorio_final import (
    FormatoRelatorioFinal,
)


@dataclass(frozen=True, slots=True)
class ResultadoExportacaoRelatorio:
    formato: FormatoRelatorioFinal
    caminho: Path
    tamanho_bytes: int

    def __post_init__(self) -> None:
        caminho = Path(self.caminho)
        object.__setattr__(self, "caminho", caminho)

        if caminho.suffix.lower() != f".{self.formato.extensao}":
            raise ValueError(
                "A extensão do arquivo diverge do formato informado."
            )

        if self.tamanho_bytes < 1:
            raise ValueError(
                "O tamanho do arquivo exportado deve ser positivo."
            )
