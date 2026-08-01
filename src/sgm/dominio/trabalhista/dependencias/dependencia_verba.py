from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.trabalhista.dependencias.codigo_verba import (
    CodigoVerba,
)


@dataclass(frozen=True, slots=True, order=True)
class DependenciaVerba:
    origem: CodigoVerba
    destino: CodigoVerba

    def __post_init__(self) -> None:
        if self.origem == self.destino:
            raise ValueError(
                "Uma verba não pode depender diretamente de si mesma."
            )
