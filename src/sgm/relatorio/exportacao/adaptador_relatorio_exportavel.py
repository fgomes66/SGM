from __future__ import annotations

from dataclasses import dataclass

from sgm.relatorio.geracao import RelatorioTecnicoGerado


@dataclass(frozen=True, slots=True)
class AdaptadorRelatorioExportavel:
    relatorio: RelatorioTecnicoGerado
    conteudo: str

    def __post_init__(self) -> None:
        conteudo = self.conteudo.strip()
        object.__setattr__(self, "conteudo", conteudo)

        if not conteudo:
            raise ValueError(
                "O conteúdo adaptado para exportação é obrigatório."
            )

    @property
    def referencia(self) -> str:
        return self.relatorio.relatorio.referencia

    def texto_integral(self) -> str:
        return self.conteudo
