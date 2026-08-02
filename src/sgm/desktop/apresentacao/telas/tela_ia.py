from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from sgm.desktop.aplicacao import EstadoDesktop


class TelaIA(ttk.Frame):
    TITULO = "SGM AI"
    SUBTITULO = "Assistente inteligente para processos trabalhistas"
    STATUS_INICIAL = "Nenhum processo analisado pela IA."

    def __init__(self, mestre: tk.Misc) -> None:
        super().__init__(mestre, padding=18)
        self.columnconfigure(0, weight=1)

        ttk.Label(
            self,
            text=self.TITULO,
            font=("Segoe UI", 20, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            self,
            text=self.SUBTITULO,
            font=("Segoe UI", 11),
        ).grid(row=1, column=0, sticky="w", pady=(4, 18))

        quadro_acoes = ttk.LabelFrame(
            self,
            text="Ações disponíveis",
            padding=14,
        )
        quadro_acoes.grid(row=2, column=0, sticky="ew")
        quadro_acoes.columnconfigure(0, weight=1)

        ttk.Button(
            quadro_acoes,
            text="Importar processo",
            state="disabled",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            quadro_acoes,
            text=(
                "A importação de documentos será habilitada na "
                "próxima entrega do módulo IA."
            ),
            wraplength=720,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(10, 0))

        quadro_status = ttk.LabelFrame(
            self,
            text="Status",
            padding=14,
        )
        quadro_status.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(16, 0),
        )

        self._status = ttk.Label(
            quadro_status,
            text=self.STATUS_INICIAL,
            wraplength=720,
            justify="left",
        )
        self._status.grid(row=0, column=0, sticky="w")

    def carregar_estado(self, estado: EstadoDesktop) -> None:
        referencia = estado.referencia_processo
        if referencia:
            texto = (
                f"Processo ativo: {referencia}. "
                "Aguardando análise pela IA."
            )
        else:
            texto = self.STATUS_INICIAL
        self._status.configure(text=texto)
