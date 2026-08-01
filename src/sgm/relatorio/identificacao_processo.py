from __future__ import annotations

import re
from dataclasses import dataclass

from sgm.relatorio.orgao_julgador import OrgaoJulgador


PADRAO_CNJ = re.compile(
    r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$"
)


def _normalizar_opcional(valor: str | None) -> str | None:
    if valor is None:
        return None
    normalizado = valor.strip()
    return normalizado or None


@dataclass(frozen=True, slots=True)
class IdentificacaoProcesso:
    orgao_julgador: OrgaoJulgador
    numero_processo: str
    classe_processual: str
    reclamante: str
    reclamada: str
    magistrado: str | None = None
    perito: str | None = None
    assistente_reclamante: str | None = None
    assistente_reclamada: str | None = None
    advogado_reclamante: str | None = None
    advogado_reclamada: str | None = None

    def __post_init__(self) -> None:
        numero = self.numero_processo.strip()
        classe = self.classe_processual.strip()
        reclamante = self.reclamante.strip()
        reclamada = self.reclamada.strip()

        object.__setattr__(self, "numero_processo", numero)
        object.__setattr__(self, "classe_processual", classe)
        object.__setattr__(self, "reclamante", reclamante)
        object.__setattr__(self, "reclamada", reclamada)

        if not PADRAO_CNJ.fullmatch(numero):
            raise ValueError(
                "O número do processo deve usar o padrão CNJ."
            )

        if not classe:
            raise ValueError(
                "A classe processual é obrigatória."
            )

        if not reclamante:
            raise ValueError("O reclamante é obrigatório.")

        if not reclamada:
            raise ValueError("A reclamada é obrigatória.")

        for campo in (
            "magistrado",
            "perito",
            "assistente_reclamante",
            "assistente_reclamada",
            "advogado_reclamante",
            "advogado_reclamada",
        ):
            object.__setattr__(
                self,
                campo,
                _normalizar_opcional(getattr(self, campo)),
            )
