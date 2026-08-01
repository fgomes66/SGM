from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from uuid import UUID

from sgm.desktop.aplicacao import (
    ControladorDesktop,
    DadosCalculoFormulario,
    EstadoDesktop,
)


class TelaCalculo(ttk.Frame):
    def __init__(
        self,
        mestre: tk.Misc,
        controlador: ControladorDesktop,
    ) -> None:
        super().__init__(mestre, padding=18)
        self.controlador = controlador
        self.columnconfigure(1, weight=1)
        self.rowconfigure(7, weight=1)

        self._vars = {
            "competencia": tk.StringVar(),
            "quantidade_horas": tk.StringVar(),
            "adicional_percentual": tk.StringVar(value="50"),
            "fundamento": tk.StringVar(
                value="Art. 7º, XVI, da Constituição Federal"
            ),
        }

        ttk.Label(
            self,
            text="Cálculo de Horas Extras",
            font=("Segoe UI", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 12),
        )

        campos = (
            ("competencia", "Competência/Data (AAAA-MM-DD)"),
            ("quantidade_horas", "Quantidade de horas"),
            ("adicional_percentual", "Adicional (%)"),
            ("fundamento", "Fundamento"),
        )
        for linha, (campo, rotulo) in enumerate(
            campos,
            start=1,
        ):
            ttk.Label(self, text=rotulo).grid(
                row=linha,
                column=0,
                sticky="w",
                padx=(0, 12),
                pady=4,
            )
            ttk.Entry(
                self,
                textvariable=self._vars[campo],
            ).grid(
                row=linha,
                column=1,
                sticky="ew",
                pady=4,
            )

        ttk.Button(
            self,
            text="Executar cálculo",
            command=self._calcular,
        ).grid(
            row=5,
            column=1,
            sticky="e",
            pady=(8, 8),
        )

        colunas = (
            "competencia",
            "salario",
            "divisor",
            "horas",
            "adicional",
            "total",
        )
        self._lista = ttk.Treeview(
            self,
            columns=colunas,
            show="headings",
            height=9,
        )
        configuracao = (
            ("competencia", "Competência", 100),
            ("salario", "Salário-base", 120),
            ("divisor", "Divisor", 80),
            ("horas", "Horas", 80),
            ("adicional", "Adicional", 90),
            ("total", "Total", 120),
        )
        for coluna, titulo, largura in configuracao:
            self._lista.heading(coluna, text=titulo)
            self._lista.column(
                coluna,
                width=largura,
                anchor="w",
            )
        self._lista.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="nsew",
        )
        self._lista.bind(
            "<<TreeviewSelect>>",
            self._mostrar_memoria,
        )

        botoes = ttk.Frame(self)
        botoes.grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="e",
            pady=(8, 0),
        )
        ttk.Button(
            botoes,
            text="Excluir resultado",
            command=self._excluir,
        ).pack(side="left", padx=3)

        self._memoria = tk.Text(
            self,
            height=8,
            state="disabled",
        )
        self._memoria.grid(
            row=9,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(8, 0),
        )

        self._mensagem = ttk.Label(self, text="")
        self._mensagem.grid(
            row=10,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(8, 0),
        )
        self._resultados = {}

    def _formulario(self) -> DadosCalculoFormulario:
        return DadosCalculoFormulario(
            **{
                campo: variavel.get()
                for campo, variavel in self._vars.items()
            }
        )

    def _calcular(self) -> None:
        erros = self.controlador.executar_calculo(
            self._formulario()
        )
        if erros:
            texto = "\n".join(f"• {item}" for item in erros)
            self._mensagem.configure(
                text=texto,
                foreground="#9b1c1c",
            )
            messagebox.showerror(
                "Cálculo",
                texto,
                parent=self,
            )
            return
        self._mensagem.configure(
            text="Cálculo executado com sucesso.",
            foreground="#1b6e2b",
        )

    def _mostrar_memoria(self, _evento=None) -> None:
        selecionados = self._lista.selection()
        if not selecionados:
            return
        resultado = self._resultados.get(selecionados[0])
        if resultado is None:
            return
        texto = "\n".join(resultado.memoria_resumida())
        self._memoria.configure(state="normal")
        self._memoria.delete("1.0", "end")
        self._memoria.insert("1.0", texto)
        self._memoria.configure(state="disabled")

    def _excluir(self) -> None:
        selecionados = self._lista.selection()
        if not selecionados:
            messagebox.showinfo(
                "Cálculo",
                "Selecione um resultado.",
                parent=self,
            )
            return
        if messagebox.askyesno(
            "Excluir resultado",
            "Confirma a exclusão do resultado selecionado?",
            parent=self,
        ):
            self.controlador.excluir_resultado_calculo(
                UUID(selecionados[0])
            )

    def carregar_estado(self, estado: EstadoDesktop) -> None:
        for item in self._lista.get_children():
            self._lista.delete(item)
        self._resultados = {
            str(item.id): item
            for item in estado.resultados_calculo
        }
        for item in estado.resultados_calculo:
            self._lista.insert(
                "",
                "end",
                iid=str(item.id),
                values=(
                    item.competencia.isoformat(),
                    f"R$ {item.salario_base:.2f}",
                    str(item.divisor),
                    str(item.quantidade_horas),
                    (
                        f"{item.adicional_percentual * 100}%"
                    ),
                    f"R$ {item.valor_total:.2f}",
                ),
            )
