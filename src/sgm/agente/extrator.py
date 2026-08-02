from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Entidade:
    tipo: str
    valor: str


class Extrator:
    def extrair(self, texto: str) -> list[Entidade]:
        entidades: list[Entidade] = []

        texto = texto.lower()

        salario = re.search(
            r"r\$\s*([\d\.\,]+)|sal[aá]rio\s*(?:de)?\s*([\d\.\,]+)",
            texto,
        )
        if salario:
            valor = salario.group(1) or salario.group(2)
            entidades.append(Entidade("salario", valor))

        percentual = re.search(r"(\d{1,3})\s*%", texto)
        if percentual:
            entidades.append(
                Entidade("percentual", percentual.group(1))
            )

        horas = re.search(r"(\d+(?:[\.,]\d+)?)\s*horas?", texto)
        if horas:
            entidades.append(
                Entidade("horas", horas.group(1))
            )

        dias = re.search(r"(\d+)\s*dias?", texto)
        if dias:
            entidades.append(
                Entidade("dias", dias.group(1))
            )

        return entidades