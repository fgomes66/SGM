from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.trabalhista.dependencias.codigo_verba import (
    CodigoVerba,
)
from sgm.dominio.trabalhista.dependencias.dependencia_verba import (
    DependenciaVerba,
)


@dataclass(frozen=True, slots=True)
class GrafoDependenciasVerbas:
    dependencias: tuple[DependenciaVerba, ...] = ()

    def __post_init__(self) -> None:
        normalizadas = tuple(sorted(set(self.dependencias)))
        object.__setattr__(self, "dependencias", normalizadas)
        self.ordem_calculo()

    def adicionar(
        self,
        origem: CodigoVerba,
        destino: CodigoVerba,
    ) -> "GrafoDependenciasVerbas":
        nova = DependenciaVerba(origem=origem, destino=destino)
        return GrafoDependenciasVerbas(
            dependencias=self.dependencias + (nova,)
        )

    def predecessoras(
        self,
        verba: CodigoVerba,
    ) -> tuple[CodigoVerba, ...]:
        return tuple(
            sorted(
                dependencia.origem
                for dependencia in self.dependencias
                if dependencia.destino == verba
            )
        )

    def dependentes_diretos(
        self,
        verba: CodigoVerba,
    ) -> tuple[CodigoVerba, ...]:
        return tuple(
            sorted(
                dependencia.destino
                for dependencia in self.dependencias
                if dependencia.origem == verba
            )
        )

    def dependentes_transitivos(
        self,
        verba: CodigoVerba,
    ) -> tuple[CodigoVerba, ...]:
        encontrados: set[CodigoVerba] = set()
        pendentes = list(self.dependentes_diretos(verba))

        while pendentes:
            atual = pendentes.pop(0)
            if atual in encontrados:
                continue
            encontrados.add(atual)
            pendentes.extend(self.dependentes_diretos(atual))

        return tuple(sorted(encontrados))

    def ordem_calculo(self) -> tuple[CodigoVerba, ...]:
        nos = {
            dependencia.origem
            for dependencia in self.dependencias
        } | {
            dependencia.destino
            for dependencia in self.dependencias
        }

        if not nos:
            return ()

        grau_entrada = {no: 0 for no in nos}
        sucessores = {no: set() for no in nos}

        for dependencia in self.dependencias:
            sucessores[dependencia.origem].add(
                dependencia.destino
            )
            grau_entrada[dependencia.destino] += 1

        disponiveis = sorted(
            no for no, grau in grau_entrada.items() if grau == 0
        )
        ordem: list[CodigoVerba] = []

        while disponiveis:
            atual = disponiveis.pop(0)
            ordem.append(atual)

            for sucessor in sorted(sucessores[atual]):
                grau_entrada[sucessor] -= 1
                if grau_entrada[sucessor] == 0:
                    disponiveis.append(sucessor)
                    disponiveis.sort()

        if len(ordem) != len(nos):
            raise ValueError(
                "O grafo de verbas contém dependência cíclica."
            )

        return tuple(ordem)
