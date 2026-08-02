from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Ferramenta:
    nome: str
    descricao: str
    categoria: str


@dataclass(slots=True)
class PassoPlano:
    ferramenta: str
    objetivo: str


@dataclass(slots=True)
class PlanoExecucao:
    objetivo: str
    passos: list[PassoPlano] = field(default_factory=list)


@dataclass(slots=True)
class ResultadoFerramenta:
    sucesso: bool
    mensagem: str
    dados: Any = None