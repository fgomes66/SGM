from dataclasses import dataclass

from .extrator import Entidade
from .interpretador import Assunto, Intencao, Interpretacao


@dataclass(slots=True, frozen=True)
class ContextoTrabalhista:
    interpretacao: Interpretacao
    entidades: list[Entidade]

    @property
    def intencao(self) -> Intencao:
        return self.interpretacao.intencao

    @property
    def assunto(self) -> Assunto:
        return self.interpretacao.assunto

    @property
    def texto(self) -> str:
        return self.interpretacao.texto_original

    def buscar(self, tipo: str) -> str | None:
        for entidade in self.entidades:
            if entidade.tipo == tipo:
                return entidade.valor

        return None

    def buscar_todas(self, tipo: str) -> list[str]:
        return [
            entidade.valor
            for entidade in self.entidades
            if entidade.tipo == tipo
        ]

    def possui(self, tipo: str) -> bool:
        return self.buscar(tipo) is not None