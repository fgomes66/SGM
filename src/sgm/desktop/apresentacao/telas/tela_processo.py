from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from sgm.desktop.aplicacao import (
    ControladorDesktop,
    DadosProcessoFormulario,
    EstadoDesktop,
)


class TelaProcesso(ttk.Frame):
    CAMPOS = (
        ("tribunal", "Tribunal"),
        ("regiao_trt", "Região do TRT"),
        ("vara", "Vara do Trabalho"),
        ("municipio", "Município"),
        ("uf", "UF"),
        ("numero_processo", "Número do processo (CNJ)"),
        ("classe_processual", "Classe processual"),
        ("reclamante", "Reclamante"),
        ("reclamada", "Reclamada"),
        ("magistrado", "Magistrado(a) — opcional"),
        ("perito", "Perito/Calculista — opcional"),
        (
            "assistente_reclamante",
            "Assistente do reclamante — opcional",
        ),
        (
            "assistente_reclamada",
            "Assistente da reclamada — opcional",
        ),
        (
            "advogado_reclamante",
            "Advogado do reclamante — opcional",
        ),
        (
            "advogado_reclamada",
            "Advogado da reclamada — opcional",
        ),
    )

    def __init__(
        self,
        mestre: tk.Misc,
        controlador: ControladorDesktop,
    ) -> None:
        super().__init__(mestre, padding=20)
        self.controlador = controlador
        self.columnconfigure(1, weight=1)

        ttk.Label(
            self,
            text="Cadastro do Processo",
            font=("Segoe UI", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 14),
        )

        self._variaveis: dict[str, tk.StringVar] = {}

        valores_iniciais = DadosProcessoFormulario()
        for indice, (campo, rotulo) in enumerate(
            self.CAMPOS,
            start=1,
        ):
            ttk.Label(self, text=rotulo).grid(
                row=indice,
                column=0,
                sticky="w",
                padx=(0, 12),
                pady=4,
            )
            variavel = tk.StringVar(
                value=getattr(valores_iniciais, campo)
            )
            self._variaveis[campo] = variavel
            ttk.Entry(
                self,
                textvariable=variavel,
                width=70,
            ).grid(
                row=indice,
                column=1,
                sticky="ew",
                pady=4,
            )

        botoes = ttk.Frame(self)
        botoes.grid(
            row=len(self.CAMPOS) + 1,
            column=0,
            columnspan=2,
            sticky="e",
            pady=(16, 0),
        )

        ttk.Button(
            botoes,
            text="Validar e registrar",
            command=self._registrar,
        ).pack(side="left", padx=4)

        ttk.Button(
            botoes,
            text="Limpar",
            command=self._limpar,
        ).pack(side="left", padx=4)

        self._mensagem = ttk.Label(
            self,
            text="",
            foreground="#444444",
            wraplength=760,
            justify="left",
        )
        self._mensagem.grid(
            row=len(self.CAMPOS) + 2,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(12, 0),
        )

    def _formulario(self) -> DadosProcessoFormulario:
        return DadosProcessoFormulario(
            **{
                campo: variavel.get()
                for campo, variavel in self._variaveis.items()
            }
        )

    def _registrar(self) -> None:
        erros = self.controlador.registrar_identificacao(
            self._formulario()
        )
        if erros:
            texto = "\n".join(f"• {erro}" for erro in erros)
            self._mensagem.configure(
                text=texto,
                foreground="#9b1c1c",
            )
            messagebox.showerror(
                "Cadastro do processo",
                texto,
                parent=self,
            )
            return

        self._mensagem.configure(
            text="Dados processuais registrados com sucesso.",
            foreground="#1b6e2b",
        )

    def _limpar(self) -> None:
        padrao = DadosProcessoFormulario()
        for campo, variavel in self._variaveis.items():
            variavel.set(getattr(padrao, campo))
        self._mensagem.configure(text="")

    def carregar_estado(self, estado: EstadoDesktop) -> None:
        identificacao = estado.identificacao_processo
        if identificacao is None:
            return

        valores = {
            "tribunal": identificacao.orgao_julgador.tribunal,
            "regiao_trt": str(
                identificacao.orgao_julgador.regiao_trt
            ),
            "vara": identificacao.orgao_julgador.vara,
            "municipio": identificacao.orgao_julgador.municipio,
            "uf": identificacao.orgao_julgador.uf,
            "numero_processo": identificacao.numero_processo,
            "classe_processual": identificacao.classe_processual,
            "reclamante": identificacao.reclamante,
            "reclamada": identificacao.reclamada,
            "magistrado": identificacao.magistrado or "",
            "perito": identificacao.perito or "",
            "assistente_reclamante": (
                identificacao.assistente_reclamante or ""
            ),
            "assistente_reclamada": (
                identificacao.assistente_reclamada or ""
            ),
            "advogado_reclamante": (
                identificacao.advogado_reclamante or ""
            ),
            "advogado_reclamada": (
                identificacao.advogado_reclamada or ""
            ),
        }
        for campo, valor in valores.items():
            self._variaveis[campo].set(valor)
