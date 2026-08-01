from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from sgm.desktop.aplicacao import (
    ControladorDesktop,
    EstadoDesktop,
    SecaoDesktop,
)
from sgm.desktop.apresentacao.telas.tela_calculo import TelaCalculo
from sgm.desktop.apresentacao.telas.tela_contrato import TelaContrato
from sgm.desktop.apresentacao.telas.tela_eventos import TelaEventos
from sgm.desktop.apresentacao.telas.tela_memoria import TelaMemoria
from sgm.desktop.apresentacao.telas.tela_relatorio import TelaRelatorio
from sgm.desktop.apresentacao.telas.tela_processo import (
    TelaProcesso,
)


class TelaConteudo(ttk.Frame):
    def __init__(
        self,
        mestre: tk.Misc,
        controlador: ControladorDesktop,
    ) -> None:
        super().__init__(mestre, padding=18)
        self.controlador = controlador
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._quadros: dict[SecaoDesktop, ttk.Frame] = {}

        self._inicio = self._criar_inicio()
        self._processo = TelaProcesso(self, controlador)
        self._contrato = TelaContrato(self, controlador)
        self._calculo = TelaCalculo(self, controlador)
        self._eventos = TelaEventos(self, controlador)
        self._memoria = TelaMemoria(self, controlador)
        self._relatorio = TelaRelatorio(self, controlador)
        self._placeholder = self._criar_placeholder()

        self._quadros[SecaoDesktop.INICIO] = self._inicio
        self._quadros[SecaoDesktop.PROCESSO] = self._processo
        self._quadros[SecaoDesktop.CONTRATO] = self._contrato
        self._quadros[SecaoDesktop.EVENTOS] = self._eventos
        self._quadros[SecaoDesktop.CALCULO] = self._calculo
        self._quadros[SecaoDesktop.MEMORIA] = self._memoria
        self._quadros[SecaoDesktop.RELATORIO] = self._relatorio

    def _criar_inicio(self) -> ttk.Frame:
        quadro = ttk.Frame(self, padding=18)
        quadro.columnconfigure(0, weight=1)

        ttk.Label(
            quadro,
            text="Início",
            font=("Segoe UI", 20, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self._resumo = ttk.Label(
            quadro,
            text="",
            wraplength=780,
            justify="left",
        )
        self._resumo.grid(
            row=1,
            column=0,
            sticky="nw",
            pady=(12, 0),
        )
        return quadro

    def _criar_placeholder(self) -> ttk.Frame:
        quadro = ttk.Frame(self, padding=18)
        self._placeholder_titulo = ttk.Label(
            quadro,
            text="",
            font=("Segoe UI", 20, "bold"),
        )
        self._placeholder_titulo.pack(anchor="w")

        self._placeholder_texto = ttk.Label(
            quadro,
            text=(
                "Esta seção será implementada em uma próxima "
                "sub-release do SGM Desktop."
            ),
            wraplength=780,
            justify="left",
        )
        self._placeholder_texto.pack(
            anchor="w",
            pady=(12, 0),
        )
        return quadro

    def _ocultar_todos(self) -> None:
        self._inicio.grid_forget()
        self._processo.grid_forget()
        self._contrato.grid_forget()
        self._eventos.grid_forget()
        self._calculo.grid_forget()
        self._memoria.grid_forget()
        self._relatorio.grid_forget()
        self._placeholder.grid_forget()

    def mostrar_secao(
        self,
        secao: SecaoDesktop,
        estado: EstadoDesktop,
    ) -> None:
        self._ocultar_todos()

        if secao == SecaoDesktop.INICIO:
            self._atualizar_inicio(estado)
            self._inicio.grid(
                row=0,
                column=0,
                sticky="nsew",
            )
            return

        if secao == SecaoDesktop.PROCESSO:
            self._processo.carregar_estado(estado)
            self._processo.grid(
                row=0,
                column=0,
                sticky="nsew",
            )
            return

        if secao == SecaoDesktop.CONTRATO:
            self._contrato.carregar_estado(estado)
            self._contrato.grid(row=0, column=0, sticky="nsew")
            return

        if secao == SecaoDesktop.EVENTOS:
            self._eventos.carregar_estado(estado)
            self._eventos.grid(row=0, column=0, sticky="nsew")
            return

        if secao == SecaoDesktop.CALCULO:
            self._calculo.carregar_estado(estado)
            self._calculo.grid(
                row=0,
                column=0,
                sticky="nsew",
            )
            return

        if secao == SecaoDesktop.MEMORIA:
            self._memoria.carregar_estado(estado)
            self._memoria.grid(
                row=0,
                column=0,
                sticky="nsew",
            )
            return

        if secao == SecaoDesktop.RELATORIO:
            self._relatorio.carregar_estado(estado)
            self._relatorio.grid(
                row=0,
                column=0,
                sticky="nsew",
            )
            return

        self._placeholder_titulo.configure(
            text=secao.titulo
        )
        self._placeholder.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

    def _atualizar_inicio(
        self,
        estado: EstadoDesktop,
    ) -> None:
        referencia = (
            estado.referencia_processo
            or "nenhum processo ativo"
        )

        if estado.identificacao_processo is None:
            situacao = "dados processuais não registrados"
            detalhes = ""
        else:
            identificacao = estado.identificacao_processo
            situacao = "dados processuais registrados"
            detalhes = (
                "\n"
                f"Processo CNJ: {identificacao.numero_processo}\n"
                f"Reclamante: {identificacao.reclamante}\n"
                f"Reclamada: {identificacao.reclamada}"
            )

        self._resumo.configure(
            text=(
                f"Processo: {referencia}\n"
                f"Situação: {situacao}"
                f"{detalhes}\n\n"
                f"{estado.mensagem_status}\n\n"
                f"Backend homologado: "
                f"{estado.backend_homologado}\n"
                f"Testes aprovados: "
                f"{estado.total_testes_backend}"
            )
        )

    def atualizar(self, estado: EstadoDesktop) -> None:
        self.mostrar_secao(
            estado.secao_atual,
            estado,
        )
