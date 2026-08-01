from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from sgm.desktop.aplicacao import (
    ControladorDesktop,
    EstadoDesktop,
    ServicoRelatorioTecnicoDesktop,
)


class TelaRelatorio(ttk.Frame):
    def __init__(
        self,
        mestre: tk.Misc,
        controlador: ControladorDesktop,
    ) -> None:
        super().__init__(mestre, padding=18)
        self.controlador = controlador
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        ttk.Label(
            self,
            text="Relatório Técnico",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self._situacao = ttk.Label(
            self,
            text="",
            wraplength=850,
            justify="left",
        )
        self._situacao.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(8, 8),
        )

        painel = ttk.Frame(self)
        painel.grid(row=2, column=0, sticky="nsew")
        painel.columnconfigure(0, weight=1)
        painel.rowconfigure(0, weight=1)

        self._texto = tk.Text(
            painel,
            wrap="word",
            state="disabled",
            font=("Consolas", 10),
        )
        self._texto.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(
            painel,
            orient="vertical",
            command=self._texto.yview,
        )
        barra.grid(row=0, column=1, sticky="ns")
        self._texto.configure(yscrollcommand=barra.set)

        botoes = ttk.Frame(self)
        botoes.grid(
            row=3,
            column=0,
            sticky="e",
            pady=(10, 0),
        )
        ttk.Button(
            botoes,
            text="Gerar / Atualizar",
            command=self._gerar,
        ).pack(side="left", padx=3)
        ttk.Button(
            botoes,
            text="Copiar",
            command=self._copiar,
        ).pack(side="left", padx=3)
        ttk.Button(
            botoes,
            text="Exportar",
            state="disabled",
        ).pack(side="left", padx=3)

        self._conteudo_atual = ""

    def carregar_estado(self, estado: EstadoDesktop) -> None:
        self._estado = estado
        self._gerar(mostrar_erro=False)

    def _gerar(self, mostrar_erro: bool = True) -> None:
        estado = self.controlador.estado
        erros = ServicoRelatorioTecnicoDesktop.validar_dados(
            estado.referencia_processo,
            estado.identificacao_processo,
            estado.contrato_trabalho,
            estado.resultados_calculo,
        )
        if erros:
            texto = "Não foi possível gerar o relatório:\n" + "\n".join(
                f"• {item}" for item in erros
            )
            self._situacao.configure(
                text=texto,
                foreground="#9b1c1c",
            )
            self._exibir("")
            if mostrar_erro:
                messagebox.showerror(
                    "Relatório Técnico",
                    texto,
                    parent=self,
                )
            return

        relatorio = ServicoRelatorioTecnicoDesktop.gerar(
            referencia=estado.referencia_processo,
            identificacao=estado.identificacao_processo,
            contrato=estado.contrato_trabalho,
            eventos=estado.eventos_contratuais,
            resultados=estado.resultados_calculo,
        )
        self._situacao.configure(
            text=(
                f"Relatório gerado para {relatorio.referencia}. "
                f"Total demonstrado: R$ {relatorio.total_geral:.2f}"
            ),
            foreground="#1b6e2b",
        )
        self._exibir(relatorio.conteudo)

    def _exibir(self, conteudo: str) -> None:
        self._conteudo_atual = conteudo
        self._texto.configure(state="normal")
        self._texto.delete("1.0", "end")
        if conteudo:
            self._texto.insert("1.0", conteudo)
        self._texto.configure(state="disabled")

    def _copiar(self) -> None:
        if not self._conteudo_atual:
            messagebox.showinfo(
                "Relatório Técnico",
                "Gere um relatório antes de copiar.",
                parent=self,
            )
            return
        self.clipboard_clear()
        self.clipboard_append(self._conteudo_atual)
        self.update_idletasks()
        messagebox.showinfo(
            "Relatório Técnico",
            "Relatório copiado para a área de transferência.",
            parent=self,
        )
