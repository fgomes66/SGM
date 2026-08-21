from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .verba_deferida import VerbaDeferida


@dataclass(frozen=True, slots=True)
class SentencaTrabalhista:
    """Dados estruturados do título judicial utilizado na liquidação."""

    data_sentenca: date | None = None
    data_transito_julgado: date | None = None
    texto_dispositivo: str = ""
    observacoes: str = ""
    verbas_deferidas: tuple[VerbaDeferida, ...] = ()

    def __post_init__(self) -> None:
        if (
            self.data_sentenca is not None
            and self.data_transito_julgado is not None
            and self.data_transito_julgado < self.data_sentenca
        ):
            raise ValueError(
                "O trânsito em julgado não pode anteceder a sentença."
            )

        object.__setattr__(
            self,
            "texto_dispositivo",
            self.texto_dispositivo.strip(),
        )
        object.__setattr__(
            self,
            "observacoes",
            self.observacoes.strip(),
        )

    @property
    def possui_verbas(self) -> bool:
        return bool(self.verbas_deferidas)
