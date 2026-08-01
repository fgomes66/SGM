from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime

from sgm.desktop.aplicacao.calculo_desktop import ResultadoCalculoDesktop
from sgm.desktop.aplicacao.secao_desktop import SecaoDesktop
from sgm.desktop.aplicacao.contrato_trabalho import ContratoTrabalho
from sgm.desktop.aplicacao.evento_contratual_desktop import EventoContratualDesktop
from sgm.relatorio import IdentificacaoProcesso


@dataclass(frozen=True, slots=True)
class EstadoDesktop:
    secao_atual: SecaoDesktop = SecaoDesktop.INICIO
    referencia_processo: str | None = None
    identificacao_processo: IdentificacaoProcesso | None = None
    contrato_trabalho: ContratoTrabalho | None = None
    eventos_contratuais: tuple[EventoContratualDesktop, ...] = ()
    resultados_calculo: tuple[ResultadoCalculoDesktop, ...] = ()
    alteracoes_pendentes: bool = False
    mensagem_status: str = "SGM Desktop pronto."
    backend_homologado: str = "0.9.2-E5"
    total_testes_backend: int = 725
    ultimo_salvamento: datetime | None = None

    def navegar(self, secao: SecaoDesktop) -> "EstadoDesktop":
        if not isinstance(secao, SecaoDesktop):
            raise TypeError(
                "A seção deve ser uma instância de SecaoDesktop."
            )
        return replace(
            self,
            secao_atual=secao,
            mensagem_status=f"Seção aberta: {secao.titulo}.",
        )

    def iniciar_novo(
        self,
        referencia: str,
    ) -> "EstadoDesktop":
        referencia = referencia.strip()
        if not referencia:
            raise ValueError(
                "A referência interna é obrigatória."
            )
        return replace(
            self,
            secao_atual=SecaoDesktop.PROCESSO,
            referencia_processo=referencia,
            identificacao_processo=None,
            contrato_trabalho=None,
            eventos_contratuais=(),
            resultados_calculo=(),
            ultimo_salvamento=None,
            alteracoes_pendentes=True,
            mensagem_status=f"Novo processo: {referencia}.",
        )

    def definir_processo(
        self,
        referencia: str | None,
    ) -> "EstadoDesktop":
        normalizada = referencia.strip() if referencia else None
        normalizada = normalizada or None
        return replace(
            self,
            referencia_processo=normalizada,
            alteracoes_pendentes=bool(normalizada),
            mensagem_status=(
                f"Processo ativo: {normalizada}."
                if normalizada
                else "Nenhum processo ativo."
            ),
        )

    def definir_identificacao(
        self,
        identificacao: IdentificacaoProcesso,
    ) -> "EstadoDesktop":
        if not isinstance(identificacao, IdentificacaoProcesso):
            raise TypeError(
                "A identificação deve ser IdentificacaoProcesso."
            )
        return replace(
            self,
            identificacao_processo=identificacao,
            alteracoes_pendentes=True,
            mensagem_status=(
                "Dados processuais validados e registrados."
            ),
        )

    def carregar_processo(
        self,
        referencia: str,
        identificacao: IdentificacaoProcesso,
    ) -> "EstadoDesktop":
        return replace(
            self,
            secao_atual=SecaoDesktop.INICIO,
            referencia_processo=referencia.strip(),
            identificacao_processo=identificacao,
            alteracoes_pendentes=False,
            ultimo_salvamento=datetime.now(),
            mensagem_status=(
                f"Processo carregado: {referencia.strip()}."
            ),
        )


    def definir_contrato(self, contrato: ContratoTrabalho) -> "EstadoDesktop":
        if not isinstance(contrato, ContratoTrabalho):
            raise TypeError("O contrato deve ser ContratoTrabalho.")
        return replace(self, contrato_trabalho=contrato, alteracoes_pendentes=True, mensagem_status="Contrato de trabalho validado e registrado.")


    def definir_eventos(
        self,
        eventos: tuple[EventoContratualDesktop, ...],
        mensagem: str = "Eventos contratuais atualizados.",
    ) -> "EstadoDesktop":
        if not isinstance(eventos, tuple) or any(
            not isinstance(item, EventoContratualDesktop)
            for item in eventos
        ):
            raise TypeError("Os eventos devem formar uma tupla válida.")
        ordenados = tuple(sorted(eventos, key=lambda item: item.chave_ordenacao))
        return replace(
            self,
            eventos_contratuais=ordenados,
            alteracoes_pendentes=True,
            mensagem_status=mensagem,
        )


    def definir_resultados_calculo(
        self,
        resultados: tuple[ResultadoCalculoDesktop, ...],
        mensagem: str = "Resultados de cálculo atualizados.",
    ) -> "EstadoDesktop":
        if not isinstance(resultados, tuple) or any(
            not isinstance(item, ResultadoCalculoDesktop)
            for item in resultados
        ):
            raise TypeError(
                "Os resultados devem formar uma tupla válida."
            )
        ordenados = tuple(
            sorted(
                resultados,
                key=lambda item: (
                    item.competencia,
                    str(item.id),
                ),
            )
        )
        return replace(
            self,
            resultados_calculo=ordenados,
            alteracoes_pendentes=True,
            mensagem_status=mensagem,
        )


    def fechar_processo(self) -> "EstadoDesktop":
        return replace(
            self,
            secao_atual=SecaoDesktop.INICIO,
            referencia_processo=None,
            identificacao_processo=None,
            contrato_trabalho=None,
            eventos_contratuais=(),
            resultados_calculo=(),
            alteracoes_pendentes=False,
            ultimo_salvamento=None,
            mensagem_status="Processo fechado.",
        )

    def marcar_salvo(self) -> "EstadoDesktop":
        return replace(
            self,
            alteracoes_pendentes=False,
            ultimo_salvamento=datetime.now(),
            mensagem_status="Alterações salvas em disco.",
        )
