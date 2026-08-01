from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sgm.relatorio import (
    RelatorioTecnicoGerado,
    ResultadoExportacaoRelatorio,
)


@dataclass(frozen=True, slots=True)
class ResultadoHomologacao:
    referencia: str
    relatorio: RelatorioTecnicoGerado
    exportacoes: tuple[ResultadoExportacaoRelatorio, ...]
    pasta_saida: Path

    def __post_init__(self) -> None:
        referencia = self.referencia.strip()
        pasta = Path(self.pasta_saida)

        object.__setattr__(self, "referencia", referencia)
        object.__setattr__(self, "pasta_saida", pasta)

        if not referencia:
            raise ValueError(
                "A referência da homologação é obrigatória."
            )

        if referencia != self.relatorio.relatorio.referencia:
            raise ValueError(
                "A referência da homologação diverge do relatório."
            )

        if len(self.exportacoes) != 5:
            raise ValueError(
                "A homologação final deve conter cinco exportações."
            )

        caminhos = tuple(item.caminho for item in self.exportacoes)
        if len(set(caminhos)) != len(caminhos):
            raise ValueError(
                "Os caminhos exportados devem ser únicos."
            )

        if any(not caminho.exists() for caminho in caminhos):
            raise ValueError(
                "Todos os arquivos exportados devem existir."
            )

        if any(item.tamanho_bytes < 1 for item in self.exportacoes):
            raise ValueError(
                "Todos os arquivos exportados devem possuir conteúdo."
            )

    @property
    def total_arquivos(self) -> int:
        return len(self.exportacoes)

    @property
    def tamanho_total_bytes(self) -> int:
        return sum(item.tamanho_bytes for item in self.exportacoes)
