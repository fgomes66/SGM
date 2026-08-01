from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from sgm.desktop.aplicacao import (
    ControladorDesktop,
    EstadoDesktop,
    ServicoMemoriaCalculoDesktop,
)


class TelaMemoria(ttk.Frame):
    def __init__(
        self,
        mestre: tk.Misc,
        controlador: ControladorDesktop,
    ) -> None:
        super().__init__(mestre, padding=18)
        self.controlador = controlador

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(
            self,
            text="Memória de Cálculo",
            font=("Segoe UI", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 12),
        )

        painel_lista = ttk.Frame(self)
        painel_lista.grid(
            row=1,
            column=0,
            sticky="ns",
            padx=(0, 12),
        )

        ttk.Label(
            painel_lista,
            text="Resultados",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        self._lista = tk.Listbox(
            painel_lista,
            width=28,
            exportselection=False,
        )
        self._lista.pack(fill="y", expand=True)
        self._lista.bind(
            "<<ListboxSelect>>",
            self._selecionar,
        )

        painel_texto = ttk.Frame(self)
        painel_texto.grid(
            row=1,
            column=1,
            sticky="nsew",
        )
        painel_texto.columnconfigure(0, weight=1)
        painel_texto.rowconfigure(0, weight=1)

        self._texto = tk.Text(
            painel_texto,
            wrap="word",
            state="disabled",
            font=("Consolas", 10),
        )
        self._texto.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        rolagem = ttk.Scrollbar(
            painel_texto,
            orient="vertical",
            command=self._texto.yview,
        )
        rolagem.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        self._texto.configure(
            yscrollcommand=rolagem.set,
        )

        botoes = ttk.Frame(self)
        botoes.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="e",
            pady=(10, 0),
        )

        ttk.Button(
            botoes,
            text="Atualizar",
            command=self._atualizar_manual,
        ).pack(side="left", padx=3)

        ttk.Button(
            botoes,
            text="Copiar",
            command=self._copiar,
        ).pack(side="left", padx=3)

        ttk.Button(
            botoes,
            text="Limpar seleção",
            command=self._limpar_selecao,
        ).pack(side="left", padx=3)

        self._resultados = ()
        self._texto_atual = ""

    def carregar_estado(
        self,
        estado: EstadoDesktop,
    ) -> None:
        selecao_anterior = self._lista.curselection()
        indice_anterior = (
            selecao_anterior[0]
            if selecao_anterior
            else None
        )

        self._resultados = estado.resultados_calculo
        self._lista.delete(0, "end")

        for item in self._resultados:
            self._lista.insert(
                "end",
                (
                    f"{item.competencia.isoformat()} — "
                    f"Horas Extras — R$ {item.valor_total:.2f}"
                ),
            )

        if (
            indice_anterior is not None
            and indice_anterior < len(self._resultados)
        ):
            self._lista.selection_set(indice_anterior)
            self._exibir_indice(indice_anterior)
        elif self._resultados:
            self._lista.selection_set(0)
            self._exibir_indice(0)
        else:
            self._exibir_texto(
                "Nenhum cálculo disponível.\n\n"
                "Execute um cálculo na seção Cálculo."
            )

    def _atualizar_manual(self) -> None:
        self.carregar_estado(
            self.controlador.estado
        )

    def _selecionar(self, _evento=None) -> None:
        selecao = self._lista.curselection()
        if selecao:
            self._exibir_indice(selecao[0])

    def _exibir_indice(self, indice: int) -> None:
        if indice < 0 or indice >= len(self._resultados):
            return
        memoria = ServicoMemoriaCalculoDesktop.gerar(
            self._resultados[indice]
        )
        self._exibir_texto(memoria.como_texto())

    def _exibir_texto(self, texto: str) -> None:
        self._texto_atual = texto
        self._texto.configure(state="normal")
        self._texto.delete("1.0", "end")
        self._texto.insert("1.0", texto)
        self._texto.configure(state="disabled")

    def _copiar(self) -> None:
        if not self._texto_atual:
            messagebox.showinfo(
                "Memória de Cálculo",
                "Nenhuma memória disponível para copiar.",
                parent=self,
            )
            return

        self.clipboard_clear()
        self.clipboard_append(self._texto_atual)
        self.update_idletasks()

        messagebox.showinfo(
            "Memória de Cálculo",
            "Memória copiada para a área de transferência.",
            parent=self,
        )

    def _limpar_selecao(self) -> None:
        self._lista.selection_clear(0, "end")
        self._exibir_texto(
            "Selecione um cálculo para visualizar a memória."
        )
