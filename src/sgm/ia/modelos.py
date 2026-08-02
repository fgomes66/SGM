from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ContextoIA:
    """Contexto mínimo enviado ao motor de inteligência."""

    processo_referencia: str | None = None
    dados: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        dados_normalizados = {
            str(chave).strip(): str(valor).strip()
            for chave, valor in self.dados.items()
            if str(chave).strip()
        }
        object.__setattr__(
            self,
            "dados",
            MappingProxyType(dados_normalizados),
        )


@dataclass(frozen=True, slots=True)
class RequisicaoIA:
    mensagem: str
    contexto: ContextoIA = field(default_factory=ContextoIA)

    def __post_init__(self) -> None:
        mensagem = self.mensagem.strip()
        if not mensagem:
            raise ValueError("A mensagem da IA não pode ser vazia.")
        object.__setattr__(self, "mensagem", mensagem)


@dataclass(frozen=True, slots=True)
class RespostaIA:
    conteudo: str
    provedor: str
    modelo: str | None = None
    metadados: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        conteudo = self.conteudo.strip()
        provedor = self.provedor.strip()
        if not conteudo:
            raise ValueError("A resposta da IA não pode ser vazia.")
        if not provedor:
            raise ValueError("O provedor da IA deve ser informado.")
        object.__setattr__(self, "conteudo", conteudo)
        object.__setattr__(self, "provedor", provedor)
        object.__setattr__(
            self,
            "metadados",
            MappingProxyType(dict(self.metadados)),
        )
