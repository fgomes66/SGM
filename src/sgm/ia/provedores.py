from __future__ import annotations

from typing import Protocol, runtime_checkable

from .modelos import RequisicaoIA, RespostaIA


class ErroProvedorIA(RuntimeError):
    """Falha controlada de um provedor de inteligência artificial."""


@runtime_checkable
class ProvedorIA(Protocol):
    @property
    def nome(self) -> str: ...

    def responder(self, requisicao: RequisicaoIA) -> RespostaIA: ...


class ProvedorIndisponivel:
    """Provedor seguro usado enquanto nenhuma integração estiver configurada."""

    nome = "indisponivel"

    def responder(self, requisicao: RequisicaoIA) -> RespostaIA:
        raise ErroProvedorIA(
            "Nenhum provedor de IA foi configurado no SGM."
        )
