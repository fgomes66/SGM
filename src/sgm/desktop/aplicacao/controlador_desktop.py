from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

from sgm.desktop.aplicacao.dados_calculo_formulario import (
    DadosCalculoFormulario,
)
from sgm.desktop.aplicacao.dados_contrato_formulario import (
    DadosContratoFormulario,
)
from sgm.desktop.aplicacao.dados_evento_formulario import (
    DadosEventoFormulario,
)
from sgm.desktop.aplicacao.dados_processo_formulario import (
    DadosProcessoFormulario,
)
from sgm.desktop.aplicacao.estado_desktop import EstadoDesktop
from sgm.desktop.aplicacao.secao_desktop import SecaoDesktop
from sgm.desktop.aplicacao.servico_calculo_desktop import (
    ServicoCalculoDesktop,
)
from sgm.desktop.persistencia import (
    RegistroProcesso,
    RepositorioProcessosJSON,
)


ObservadorEstado = Callable[[EstadoDesktop], None]


class ControladorDesktop:
    def __init__(
        self,
        estado: EstadoDesktop | None = None,
        repositorio: RepositorioProcessosJSON | None = None,
        exigir_fluxo: bool = False,
    ) -> None:
        self._estado = estado or EstadoDesktop()
        self._observadores: list[ObservadorEstado] = []
        self._repositorio = repositorio
        self._exigir_fluxo = exigir_fluxo

    @property
    def estado(self) -> EstadoDesktop:
        return self._estado

    @property
    def repositorio(
        self,
    ) -> RepositorioProcessosJSON | None:
        return self._repositorio

    @property
    def processo_ativo(self) -> bool:
        return bool(
            self._estado.referencia_processo
            and self._estado.identificacao_processo
        )

    def configurar_repositorio(
        self,
        pasta: Path,
        exigir_fluxo: bool = True,
    ) -> None:
        self._repositorio = RepositorioProcessosJSON(pasta)
        self._exigir_fluxo = exigir_fluxo

    def observar(self, observador: ObservadorEstado) -> None:
        if observador not in self._observadores:
            self._observadores.append(observador)

    def remover_observador(
        self,
        observador: ObservadorEstado,
    ) -> None:
        if observador in self._observadores:
            self._observadores.remove(observador)

    def _publicar(self) -> None:
        for observador in tuple(self._observadores):
            observador(self._estado)

    def _registro_atual(self) -> RegistroProcesso:
        if not self._estado.referencia_processo:
            raise ValueError(
                "Crie ou abra um processo antes de salvar."
            )
        if self._estado.identificacao_processo is None:
            raise ValueError(
                "Valide e registre os dados processuais antes de salvar."
            )
        return RegistroProcesso(
            referencia=self._estado.referencia_processo,
            identificacao=self._estado.identificacao_processo,
            contrato=self._estado.contrato_trabalho,
            eventos=self._estado.eventos_contratuais,
            calculos=self._estado.resultados_calculo,
        )

    def _salvar_automaticamente(self) -> Path | None:
        if self._repositorio is None:
            return None
        caminho = self._repositorio.salvar(
            self._registro_atual()
        )
        self._estado = self._estado.marcar_salvo()
        return caminho

    def _finalizar_mutacao(
        self,
        mensagem_sucesso: str,
    ) -> tuple[str, ...]:
        try:
            caminho = self._salvar_automaticamente()
        except (OSError, RuntimeError, ValueError) as erro:
            return (
                "A alteração foi validada, mas não pôde ser salva: "
                f"{erro}",
            )

        if caminho is not None:
            self._estado = replace(
                self._estado,
                mensagem_status=mensagem_sucesso,
            )
        self._publicar()
        return ()

    def navegar(self, secao: SecaoDesktop) -> None:
        if not isinstance(secao, SecaoDesktop):
            raise TypeError(
                "A seção deve ser uma instância de SecaoDesktop."
            )

        protegidas = {
            SecaoDesktop.CONTRATO,
            SecaoDesktop.EVENTOS,
            SecaoDesktop.CALCULO,
            SecaoDesktop.MEMORIA,
            SecaoDesktop.RELATORIO,
            SecaoDesktop.EXPORTACAO,
        }
        if (
            self._exigir_fluxo
            and secao in protegidas
            and not self.processo_ativo
        ):
            self._estado = replace(
                self._estado,
                mensagem_status=(
                    "Crie ou abra um processo antes de acessar "
                    f"{secao.titulo}."
                ),
            )
            self._publicar()
            return

        if (
            self._exigir_fluxo
            and secao in {
                SecaoDesktop.EVENTOS,
                SecaoDesktop.CALCULO,
            }
            and self._estado.contrato_trabalho is None
        ):
            self._estado = replace(
                self._estado,
                mensagem_status=(
                    "Cadastre o contrato de trabalho antes de acessar "
                    f"{secao.titulo}."
                ),
            )
            self._publicar()
            return

        if (
            self._exigir_fluxo
            and secao == SecaoDesktop.MEMORIA
            and not self._estado.resultados_calculo
        ):
            self._estado = replace(
                self._estado,
                mensagem_status=(
                    "Execute ao menos um cálculo antes de abrir "
                    "a Memória de Cálculo."
                ),
            )
            self._publicar()
            return

        self._estado = self._estado.navegar(secao)
        self._publicar()

    def novo_processo(self, referencia: str) -> None:
        self._estado = self._estado.iniciar_novo(referencia)
        self._publicar()

    def registrar_identificacao(
        self,
        formulario: DadosProcessoFormulario,
    ) -> tuple[str, ...]:
        erros = formulario.validar()
        if erros:
            return erros

        if (
            self._exigir_fluxo
            and not self._estado.referencia_processo
        ):
            return (
                "Crie uma referência interna em Arquivo > Novo processo.",
            )

        self._estado = self._estado.definir_identificacao(
            formulario.criar_identificacao()
        )
        if self._repositorio is None:
            self._publicar()
            return ()
        return self._finalizar_mutacao(
            "Dados processuais registrados e salvos automaticamente."
        )

    def registrar_contrato(
        self,
        formulario: DadosContratoFormulario,
    ) -> tuple[str, ...]:
        if self._exigir_fluxo and not self.processo_ativo:
            return (
                "Crie ou abra um processo antes de cadastrar o contrato.",
            )

        erros = formulario.validar()
        if erros:
            return erros

        self._estado = self._estado.definir_contrato(
            formulario.criar_contrato()
        )
        if self._repositorio is None:
            self._publicar()
            return ()
        return self._finalizar_mutacao(
            "Contrato registrado e salvo automaticamente."
        )

    def registrar_evento(
        self,
        formulario: DadosEventoFormulario,
    ) -> tuple[str, ...]:
        if self._exigir_fluxo and not self.processo_ativo:
            return (
                "Crie ou abra um processo antes de cadastrar eventos.",
            )
        if (
            self._exigir_fluxo
            and self._estado.contrato_trabalho is None
        ):
            return (
                "Cadastre o contrato de trabalho antes dos eventos.",
            )

        erros = formulario.validar()
        if erros:
            return erros

        evento = formulario.criar_evento()
        existentes = [
            item
            for item in self._estado.eventos_contratuais
            if item.id != evento.id
        ]
        existentes.append(evento)
        self._estado = self._estado.definir_eventos(
            tuple(existentes),
            "Evento contratual registrado.",
        )
        if self._repositorio is None:
            self._publicar()
            return ()
        return self._finalizar_mutacao(
            "Evento contratual registrado e salvo automaticamente."
        )

    def excluir_evento(self, evento_id) -> bool:
        restantes = tuple(
            item
            for item in self._estado.eventos_contratuais
            if item.id != evento_id
        )
        if len(restantes) == len(
            self._estado.eventos_contratuais
        ):
            return False

        estado_anterior = self._estado
        self._estado = self._estado.definir_eventos(
            restantes,
            "Evento contratual excluído.",
        )
        if self._repositorio is None:
            self._publicar()
            return True
        erros = self._finalizar_mutacao(
            "Evento excluído e alteração salva automaticamente."
        )
        if erros:
            self._estado = estado_anterior
            self._publicar()
            return False
        return True

    def executar_calculo(
        self,
        formulario: DadosCalculoFormulario,
    ) -> tuple[str, ...]:
        if self._exigir_fluxo and not self.processo_ativo:
            return (
                "Crie ou abra um processo antes de calcular.",
            )
        if self._estado.contrato_trabalho is None:
            return (
                "Cadastre o contrato de trabalho antes de calcular.",
            )

        erros = formulario.validar()
        if erros:
            return erros

        competencia, quantidade, adicional, fundamento = (
            formulario.valores()
        )
        try:
            resultado = ServicoCalculoDesktop.calcular_horas_extras(
                self._estado.contrato_trabalho,
                self._estado.eventos_contratuais,
                competencia,
                quantidade,
                adicional,
                fundamento,
            )
        except (TypeError, ValueError) as erro:
            return (str(erro),)

        resultados = (
            self._estado.resultados_calculo + (resultado,)
        )
        self._estado = self._estado.definir_resultados_calculo(
            resultados,
            "Cálculo de horas extras executado.",
        )
        if self._repositorio is None:
            self._publicar()
            return ()
        return self._finalizar_mutacao(
            "Cálculo executado e salvo automaticamente."
        )

    def excluir_resultado_calculo(
        self,
        resultado_id,
    ) -> bool:
        restantes = tuple(
            item
            for item in self._estado.resultados_calculo
            if item.id != resultado_id
        )
        if len(restantes) == len(
            self._estado.resultados_calculo
        ):
            return False

        estado_anterior = self._estado
        self._estado = self._estado.definir_resultados_calculo(
            restantes,
            "Resultado de cálculo excluído.",
        )
        if self._repositorio is None:
            self._publicar()
            return True
        erros = self._finalizar_mutacao(
            "Resultado excluído e alteração salva automaticamente."
        )
        if erros:
            self._estado = estado_anterior
            self._publicar()
            return False
        return True

    def salvar(self) -> Path | None:
        if self._repositorio is None:
            self._estado = self._estado.marcar_salvo()
            self._publicar()
            return None

        caminho = self._repositorio.salvar(
            self._registro_atual()
        )
        self._estado = self._estado.marcar_salvo()
        self._publicar()
        return caminho


    def salvar_como(
        self,
        nova_referencia: str,
        sobrescrever: bool = False,
    ) -> Path:
        if self._repositorio is None:
            raise RuntimeError(
                "O repositório de processos não foi configurado."
            )
        if self._estado.identificacao_processo is None:
            raise ValueError(
                "Valide e registre os dados processuais antes de salvar."
            )

        nova_referencia = nova_referencia.strip()
        if not nova_referencia:
            raise ValueError("A nova referência é obrigatória.")
        if (
            not sobrescrever
            and self._repositorio.existe(nova_referencia)
            and nova_referencia != self._estado.referencia_processo
        ):
            raise FileExistsError(
                f"Já existe um processo com a referência: {nova_referencia}"
            )

        registro = RegistroProcesso(
            referencia=nova_referencia,
            identificacao=self._estado.identificacao_processo,
            contrato=self._estado.contrato_trabalho,
            eventos=self._estado.eventos_contratuais,
            calculos=self._estado.resultados_calculo,
        )
        caminho = self._repositorio.salvar(registro)
        self._estado = replace(
            self._estado.marcar_salvo(),
            referencia_processo=nova_referencia,
            mensagem_status=(
                f"Processo salvo como: {nova_referencia}."
            ),
        )
        self._publicar()
        return caminho

    def fechar_processo(self) -> None:
        self._estado = self._estado.fechar_processo()
        self._publicar()

    def abrir(self, referencia: str) -> None:
        if self._repositorio is None:
            raise RuntimeError(
                "O repositório de processos não foi configurado."
            )

        registro = self._repositorio.carregar(referencia)
        self._estado = self._estado.carregar_processo(
            registro.referencia,
            registro.identificacao,
        )
        self._estado = replace(
            self._estado,
            contrato_trabalho=registro.contrato,
            eventos_contratuais=registro.eventos,
            resultados_calculo=registro.calculos,
        )
        self._publicar()

    def carregar_ultimo(self) -> bool:
        if self._repositorio is None:
            return False

        registro = self._repositorio.carregar_ultimo()
        if registro is None:
            return False

        self._estado = self._estado.carregar_processo(
            registro.referencia,
            registro.identificacao,
        )
        self._estado = replace(
            self._estado,
            contrato_trabalho=registro.contrato,
            eventos_contratuais=registro.eventos,
            resultados_calculo=registro.calculos,
        )
        self._publicar()
        return True

    def listar_processos(self) -> tuple[str, ...]:
        if self._repositorio is None:
            return ()
        return self._repositorio.listar_referencias()
