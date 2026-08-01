from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParametrosRelatorio:
    periodo_analisado: str
    indice_correcao: str
    juros: str
    moeda: str
    observacoes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        periodo = self.periodo_analisado.strip()
        indice = self.indice_correcao.strip()
        juros = self.juros.strip()
        moeda = self.moeda.strip().upper()

        object.__setattr__(self, "periodo_analisado", periodo)
        object.__setattr__(self, "indice_correcao", indice)
        object.__setattr__(self, "juros", juros)
        object.__setattr__(self, "moeda", moeda)

        if not periodo:
            raise ValueError(
                "O período analisado é obrigatório."
            )

        if not indice:
            raise ValueError(
                "O critério de correção monetária é obrigatório."
            )

        if not juros:
            raise ValueError(
                "O critério de juros é obrigatório."
            )

        if len(moeda) != 3 or not moeda.isalpha():
            raise ValueError(
                "A moeda deve usar código alfabético de três letras."
            )

        observacoes = tuple(
            item.strip()
            for item in self.observacoes
            if item.strip()
        )
        object.__setattr__(self, "observacoes", observacoes)
