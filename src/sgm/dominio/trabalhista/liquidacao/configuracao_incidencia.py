from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.trabalhista.dependencias import CodigoVerba
from sgm.dominio.trabalhista.incidencias import RegraIncidencia


@dataclass(frozen=True, slots=True)
class ConfiguracaoIncidencia:
    verba_origem: CodigoVerba
    regra: RegraIncidencia

    def __post_init__(self) -> None:
        if self.verba_origem not in (
            CodigoVerba.HORA_EXTRA,
            CodigoVerba.DSR,
        ):
            raise ValueError(
                "A integração 0.9.0 aceita apenas HORA_EXTRA e DSR "
                "como parcelas reflexas de origem."
            )
