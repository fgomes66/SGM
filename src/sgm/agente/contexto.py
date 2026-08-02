from dataclasses import dataclass

from .extrator import Entidade
from .interpretador import Interpretacao


@dataclass(slots=True, frozen=True)
class ContextoTrabalhista:
    interpretacao: Interpretacao
    entidades: list[Entidade]

    @property
    def intencao(self):
        return self.interpretacao.intencao

    @property
    def assunto(self):
        return self.interpretacao.assunto

    @property
    def texto(self):
        return self.interpretacao.texto_original