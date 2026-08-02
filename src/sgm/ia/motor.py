from __future__ import annotations

from .modelos import ContextoIA, RequisicaoIA, RespostaIA
from .provedores import ErroProvedorIA, ProvedorIA, ProvedorIndisponivel


class MotorInteligencia:
    """Ponto único de acesso aos provedores de IA do SGM."""

    def __init__(self, provedor: ProvedorIA | None = None) -> None:
        self._provedor = provedor or ProvedorIndisponivel()

    @property
    def provedor(self) -> ProvedorIA:
        return self._provedor

    def consultar(
        self,
        mensagem: str,
        contexto: ContextoIA | None = None,
    ) -> RespostaIA:
        requisicao = RequisicaoIA(
            mensagem=mensagem,
            contexto=contexto or ContextoIA(),
        )
        try:
            resposta = self._provedor.responder(requisicao)
        except ErroProvedorIA:
            raise
        except Exception as erro:  # pragma: no cover - proteção externa
            raise ErroProvedorIA(
                f"Falha inesperada no provedor {self._provedor.nome}."
            ) from erro

        if resposta.provedor != self._provedor.nome:
            raise ErroProvedorIA(
                "O provedor retornou uma identificação inconsistente."
            )
        return resposta
