from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


HASH_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class MetadadosRelatorio:
    uuid: UUID
    hash_sha256: str
    versao_sgm: str
    versao_regras: str
    data_emissao: datetime
    quantidade_competencias: int
    quantidade_verbas: int
    quantidade_eventos: int

    def __post_init__(self) -> None:
        hash_sha256 = self.hash_sha256.strip().lower()
        versao_sgm = self.versao_sgm.strip()
        versao_regras = self.versao_regras.strip()

        object.__setattr__(self, "hash_sha256", hash_sha256)
        object.__setattr__(self, "versao_sgm", versao_sgm)
        object.__setattr__(self, "versao_regras", versao_regras)

        if not HASH_SHA256.fullmatch(hash_sha256):
            raise ValueError(
                "O hash SHA-256 deve conter 64 caracteres hexadecimais."
            )

        if not versao_sgm:
            raise ValueError("A versão do SGM é obrigatória.")

        if not versao_regras:
            raise ValueError(
                "A versão das regras é obrigatória."
            )

        if self.data_emissao.tzinfo is None:
            raise ValueError(
                "A data de emissão deve possuir fuso horário."
            )

        for nome in (
            "quantidade_competencias",
            "quantidade_verbas",
            "quantidade_eventos",
        ):
            valor = getattr(self, nome)
            if not isinstance(valor, int):
                raise TypeError(
                    f"{nome} deve ser inteiro."
                )
            if valor < 0:
                raise ValueError(
                    f"{nome} não pode ser negativo."
                )
