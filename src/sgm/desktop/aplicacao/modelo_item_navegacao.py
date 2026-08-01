from __future__ import annotations

from dataclasses import dataclass

from sgm.desktop.aplicacao.secao_desktop import SecaoDesktop


@dataclass(frozen=True, slots=True)
class ItemNavegacao:
    secao: SecaoDesktop
    rotulo: str
    descricao: str
    habilitado: bool = True

    def __post_init__(self) -> None:
        rotulo = self.rotulo.strip()
        descricao = self.descricao.strip()
        object.__setattr__(self, "rotulo", rotulo)
        object.__setattr__(self, "descricao", descricao)

        if not rotulo:
            raise ValueError("O rótulo de navegação é obrigatório.")
        if not descricao:
            raise ValueError(
                "A descrição de navegação é obrigatória."
            )
