from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from uuid import UUID

from sgm.desktop.aplicacao import (
    ControladorDesktop,
    DadosEventoFormulario,
    EstadoDesktop,
    TipoEventoDesktop,
)


class TelaEventos(ttk.Frame):
    def __init__(self, mestre: tk.Misc, controlador: ControladorDesktop) -> None:
        super().__init__(mestre, padding=18)
        self.controlador = controlador
        self.columnconfigure(1, weight=1)
        self.rowconfigure(10, weight=1)
        self._id = tk.StringVar()
        self._vars = {
            "tipo": tk.StringVar(value=TipoEventoDesktop.ALTERACAO_SALARIAL.value),
            "data_inicio": tk.StringVar(),
            "data_fim": tk.StringVar(),
            "descricao": tk.StringVar(),
            "fundamento": tk.StringVar(),
            "valor": tk.StringVar(),
            "documento": tk.StringVar(),
        }

        ttk.Label(
            self,
            text="Cadastro dos Eventos Contratuais",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        campos = (
            ("tipo", "Tipo do evento"),
            ("data_inicio", "Data inicial (AAAA-MM-DD)"),
            ("data_fim", "Data final — quando aplicável"),
            ("descricao", "Descrição"),
            ("fundamento", "Motivo/Fundamento"),
            ("valor", "Novo valor/salário — quando aplicável"),
            ("documento", "Documento — opcional"),
        )
        for linha, (campo, rotulo) in enumerate(campos, start=1):
            ttk.Label(self, text=rotulo).grid(
                row=linha, column=0, sticky="w", padx=(0, 12), pady=3
            )
            if campo == "tipo":
                widget = ttk.Combobox(
                    self,
                    textvariable=self._vars[campo],
                    values=tuple(item.value for item in TipoEventoDesktop),
                    state="readonly",
                )
            else:
                widget = ttk.Entry(self, textvariable=self._vars[campo])
            widget.grid(row=linha, column=1, sticky="ew", pady=3)

        ttk.Label(
            self,
            text="Detalhes adicionais (uma linha por item: chave=valor)",
        ).grid(row=8, column=0, sticky="nw", padx=(0, 12), pady=3)
        self._detalhes = tk.Text(self, height=3, width=60)
        self._detalhes.grid(row=8, column=1, sticky="ew", pady=3)

        botoes = ttk.Frame(self)
        botoes.grid(row=9, column=0, columnspan=2, sticky="e", pady=(8, 8))
        ttk.Button(botoes, text="Adicionar/Atualizar", command=self._registrar).pack(side="left", padx=3)
        ttk.Button(botoes, text="Novo", command=self._limpar).pack(side="left", padx=3)
        ttk.Button(botoes, text="Excluir selecionado", command=self._excluir).pack(side="left", padx=3)

        colunas = ("data", "tipo", "descricao", "valor")
        self._lista = ttk.Treeview(self, columns=colunas, show="headings", height=9)
        for coluna, titulo, largura in (
            ("data", "Data", 100),
            ("tipo", "Tipo", 180),
            ("descricao", "Descrição", 360),
            ("valor", "Valor", 110),
        ):
            self._lista.heading(coluna, text=titulo)
            self._lista.column(coluna, width=largura, anchor="w")
        self._lista.grid(row=10, column=0, columnspan=2, sticky="nsew")
        self._lista.bind("<<TreeviewSelect>>", self._selecionar)

        self._mensagem = ttk.Label(self, text="")
        self._mensagem.grid(row=11, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self._eventos_por_id = {}

    def _formulario(self) -> DadosEventoFormulario:
        return DadosEventoFormulario(
            **{campo: var.get() for campo, var in self._vars.items()},
            detalhes=self._detalhes.get("1.0", "end").strip(),
            id=self._id.get(),
        )

    def _registrar(self) -> None:
        erros = self.controlador.registrar_evento(self._formulario())
        if erros:
            texto = "\n".join(f"• {item}" for item in erros)
            self._mensagem.configure(text=texto, foreground="#9b1c1c")
            messagebox.showerror("Evento contratual", texto, parent=self)
            return
        self._mensagem.configure(
            text="Evento contratual registrado.", foreground="#1b6e2b"
        )
        self._limpar()

    def _excluir(self) -> None:
        selecionados = self._lista.selection()
        if not selecionados:
            messagebox.showinfo(
                "Eventos contratuais",
                "Selecione um evento na lista.",
                parent=self,
            )
            return
        evento_id = UUID(selecionados[0])
        if messagebox.askyesno(
            "Excluir evento",
            "Confirma a exclusão do evento selecionado?",
            parent=self,
        ):
            self.controlador.excluir_evento(evento_id)
            self._limpar()

    def _selecionar(self, _evento=None) -> None:
        selecionados = self._lista.selection()
        if not selecionados:
            return
        evento = self._eventos_por_id.get(selecionados[0])
        if evento is None:
            return
        self._id.set(str(evento.id))
        self._vars["tipo"].set(evento.tipo.value)
        self._vars["data_inicio"].set(evento.data_inicio.isoformat())
        self._vars["data_fim"].set(evento.data_fim.isoformat() if evento.data_fim else "")
        self._vars["descricao"].set(evento.descricao)
        self._vars["fundamento"].set(evento.fundamento)
        self._vars["valor"].set(str(evento.valor) if evento.valor else "")
        self._vars["documento"].set(evento.documento or "")
        self._detalhes.delete("1.0", "end")
        self._detalhes.insert(
            "1.0",
            "\n".join(f"{chave}={valor}" for chave, valor in evento.dados.items()),
        )

    def _limpar(self) -> None:
        self._id.set("")
        self._vars["tipo"].set(TipoEventoDesktop.ALTERACAO_SALARIAL.value)
        for campo in (
            "data_inicio", "data_fim", "descricao",
            "fundamento", "valor", "documento"
        ):
            self._vars[campo].set("")
        self._detalhes.delete("1.0", "end")

    def carregar_estado(self, estado: EstadoDesktop) -> None:
        for item in self._lista.get_children():
            self._lista.delete(item)
        self._eventos_por_id = {
            str(evento.id): evento for evento in estado.eventos_contratuais
        }
        for evento in estado.eventos_contratuais:
            self._lista.insert(
                "",
                "end",
                iid=str(evento.id),
                values=(
                    evento.data_inicio.isoformat(),
                    evento.tipo.titulo,
                    evento.descricao,
                    str(evento.valor) if evento.valor else "",
                ),
            )
