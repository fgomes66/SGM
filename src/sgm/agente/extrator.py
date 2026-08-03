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
        texto_normalizado = texto.lower()

        salario = re.search(
            r"r\$\s*([\d.,]+)"
            r"|sal[aá]rio\s*(?:de)?\s*r?\$?\s*([\d.,]+)",
            texto_normalizado,
        )
        if salario:
            valor = salario.group(1) or salario.group(2)
            entidades.append(
                Entidade(
                    tipo="salario",
                    valor=self._normalizar_numero(valor),
                )
            )

        percentual = re.search(
            r"(\d+(?:[.,]\d+)?)\s*%",
            texto_normalizado,
        )
        if percentual:
            entidades.append(
                Entidade(
                    tipo="percentual",
                    valor=self._normalizar_numero(
                        percentual.group(1)
                    ),
                )
            )

        horas = re.search(
            r"(\d+(?:[.,]\d+)?)\s*horas?",
            texto_normalizado,
        )
        if horas:
            entidades.append(
                Entidade(
                    tipo="horas",
                    valor=self._normalizar_numero(
                        horas.group(1)
                    ),
                )
            )

        dias = re.search(
            r"(\d+)\s*dias?",
            texto_normalizado,
        )
        if dias:
            entidades.append(
                Entidade(
                    tipo="dias",
                    valor=dias.group(1),
                )
            )

        avos = re.search(
            r"(\d{1,2})\s*(?:/12|avos?)",
            texto_normalizado,
        )
        if avos:
            entidades.append(
                Entidade(
                    tipo="avos",
                    valor=avos.group(1),
                )
            )

        meses = re.search(
            r"(\d{1,3})\s*mes(?:es)?",
            texto_normalizado,
        )
        if meses:
            entidades.append(
                Entidade(
                    tipo="meses",
                    valor=meses.group(1),
                )
            )

        return entidades

    @staticmethod
    def _normalizar_numero(valor: str) -> str:
        valor = valor.strip()

        if "." in valor and "," in valor:
            return valor.replace(".", "").replace(",", ".")

        if "," in valor:
            return valor.replace(",", ".")

        return valor