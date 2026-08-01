from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from sgm.desktop.aplicacao import (
    ControladorDesktop,
    EstadoDesktop,
    SecaoDesktop,
    criar_catalogo_navegacao,
)
from sgm.desktop.apresentacao.telas.tela_conteudo import TelaConteudo


class JanelaPrincipal(tk.Tk):
    TITULO_BASE = "SGM Desktop — Cálculos Trabalhistas"
    VERSAO = "0.9.3-F3"

    def __init__(
        self,
        controlador: ControladorDesktop | None = None,
    ) -> None:
        super().__init__()
        pasta_dados = Path.cwd() / "dados" / "processos"
        self.controlador = controlador or ControladorDesktop()
        if self.controlador.repositorio is None:
            self.controlador.configurar_repositorio(
                pasta_dados,
                exigir_fluxo=True,
            )

        self.title(self.TITULO_BASE)
        self.geometry("1180x780")
        self.minsize(980, 640)
        self._configurar_estilo()
        self._criar_menu()
        self._criar_layout()
        self.controlador.observar(self._atualizar)
        self.protocol("WM_DELETE_WINDOW", self._solicitar_saida)

        carregou = self.controlador.carregar_ultimo()
        if not carregou:
            self._atualizar(self.controlador.estado)

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style(self)
        if "vista" in estilo.theme_names():
            estilo.theme_use("vista")
        estilo.configure(
            "Navegacao.TButton",
            anchor="w",
            padding=(14, 10),
        )

    def _criar_menu(self) -> None:
        # Mantém referências Python explícitas dos menus. Em algumas
        # combinações de Tk/Tcl no Windows, menus criados apenas em
        # variáveis locais podem permanecer visíveis na barra, mas não
        # abrir o submenu de forma confiável.
        self._barra_menu = tk.Menu(self)
        self._menu_arquivo = tk.Menu(
            self._barra_menu,
            tearoff=False,
        )
        self._menu_arquivo.add_command(
            label="Novo processo...",
            command=self._novo_processo,
            accelerator="Ctrl+N",
        )
        self._menu_arquivo.add_command(
            label="Abrir processo...",
            command=self._abrir_processo,
            accelerator="Ctrl+O",
        )
        self._menu_arquivo.add_separator()
        self._menu_arquivo.add_command(
            label="Salvar",
            command=self._salvar,
            accelerator="Ctrl+S",
        )
        self._menu_arquivo.add_command(
            label="Salvar como...",
            command=self._salvar_como,
            accelerator="Ctrl+Shift+S",
        )
        self._menu_arquivo.add_separator()
        self._menu_arquivo.add_command(
            label="Fechar processo",
            command=self._fechar_processo,
            accelerator="Ctrl+W",
        )
        self._menu_arquivo.add_separator()
        self._menu_arquivo.add_command(
            label="Sair",
            command=self._solicitar_saida,
            accelerator="Alt+F4",
        )
        self._barra_menu.add_cascade(
            label="Arquivo",
            menu=self._menu_arquivo,
        )

        self._menu_ajuda = tk.Menu(
            self._barra_menu,
            tearoff=False,
        )
        self._menu_ajuda.add_command(
            label="Sobre",
            command=self._sobre,
        )
        self._barra_menu.add_cascade(
            label="Ajuda",
            menu=self._menu_ajuda,
        )
        self.configure(menu=self._barra_menu)
        # Força o Tcl a processar imediatamente a associação da barra.
        self.update_idletasks()

        self.bind_all("<Control-n>", self._atalho_novo)
        self.bind_all("<Control-o>", self._atalho_abrir)
        self.bind_all("<Control-s>", self._atalho_salvar)
        self.bind_all("<Control-Shift-S>", self._atalho_salvar_como)
        self.bind_all("<Control-w>", self._atalho_fechar)

    def _criar_layout(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # Barra de acesso rápido: além de facilitar o uso, oferece um
        # caminho visível caso o menu nativo do Windows não abra por
        # alguma limitação local do Tk.
        self._barra_acoes = ttk.Frame(self, padding=(8, 6))
        self._barra_acoes.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
        )
        ttk.Button(
            self._barra_acoes,
            text="Novo processo...",
            command=self._novo_processo,
        ).pack(side="left", padx=(0, 4))
        ttk.Button(
            self._barra_acoes,
            text="Abrir processo...",
            command=self._abrir_processo,
        ).pack(side="left", padx=4)
        ttk.Button(
            self._barra_acoes,
            text="Salvar",
            command=self._salvar,
        ).pack(side="left", padx=4)
        ttk.Button(
            self._barra_acoes,
            text="Fechar processo",
            command=self._fechar_processo,
        ).pack(side="left", padx=4)

        lateral = ttk.Frame(self, padding=(12, 16))
        lateral.grid(row=1, column=0, sticky="ns")
        lateral.configure(width=250)
        lateral.grid_propagate(False)

        ttk.Label(
            lateral,
            text="SGM",
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w")
        ttk.Label(lateral, text="Cálculos Trabalhistas").pack(
            anchor="w", pady=(0, 18)
        )

        for item in criar_catalogo_navegacao():
            ttk.Button(
                lateral,
                text=item.rotulo,
                style="Navegacao.TButton",
                command=lambda secao=item.secao: (
                    self.controlador.navegar(secao)
                ),
            ).pack(fill="x", pady=2)

        self._conteudo = TelaConteudo(self, self.controlador)
        self._conteudo.grid(row=1, column=1, sticky="nsew")
        self._status = tk.StringVar()
        ttk.Label(
            self,
            textvariable=self._status,
            relief="sunken",
            anchor="w",
            padding=(8, 4),
        ).grid(row=2, column=0, columnspan=2, sticky="ew")

    def _atalho_novo(self, _evento=None) -> str:
        self._novo_processo()
        return "break"

    def _atalho_abrir(self, _evento=None) -> str:
        self._abrir_processo()
        return "break"

    def _atalho_salvar(self, _evento=None) -> str:
        self._salvar()
        return "break"

    def _atalho_salvar_como(self, _evento=None) -> str:
        self._salvar_como()
        return "break"

    def _atalho_fechar(self, _evento=None) -> str:
        self._fechar_processo()
        return "break"

    def _novo_processo(self) -> None:
        if not self._confirmar_descarte():
            return
        referencia = simpledialog.askstring(
            "Novo processo",
            "Informe uma referência interna para o caso:",
            parent=self,
        )
        if not referencia:
            return
        try:
            self.controlador.novo_processo(referencia)
            self.controlador.navegar(SecaoDesktop.PROCESSO)
        except ValueError as erro:
            messagebox.showerror("Novo processo", str(erro), parent=self)

    def _abrir_processo(self) -> None:
        if not self._confirmar_descarte():
            return
        referencias = self.controlador.listar_processos()
        if not referencias:
            messagebox.showinfo(
                "Abrir processo",
                "Nenhum processo salvo foi encontrado.",
                parent=self,
            )
            return
        referencia = simpledialog.askstring(
            "Abrir processo",
            "Informe a referência do processo.\n\nDisponíveis:\n"
            + "\n".join(referencias),
            parent=self,
        )
        if not referencia:
            return
        try:
            self.controlador.abrir(referencia)
        except (FileNotFoundError, ValueError) as erro:
            messagebox.showerror("Abrir processo", str(erro), parent=self)

    def _salvar(self, exibir_confirmacao: bool = True) -> bool:
        try:
            caminho = self.controlador.salvar()
        except (RuntimeError, ValueError, OSError) as erro:
            messagebox.showerror("Salvar processo", str(erro), parent=self)
            return False
        if exibir_confirmacao:
            mensagem = (
                "Alterações registradas na sessão."
                if caminho is None
                else f"Processo salvo em:\n{caminho}"
            )
            messagebox.showinfo("Salvar processo", mensagem, parent=self)
        return True

    def _salvar_como(self) -> bool:
        if self.controlador.estado.identificacao_processo is None:
            messagebox.showerror(
                "Salvar como",
                "Valide e registre os dados processuais antes de salvar.",
                parent=self,
            )
            return False
        referencia = simpledialog.askstring(
            "Salvar como",
            "Informe a nova referência interna:",
            initialvalue=(self.controlador.estado.referencia_processo or ""),
            parent=self,
        )
        if not referencia:
            return False
        try:
            caminho = self.controlador.salvar_como(referencia)
        except FileExistsError:
            sobrescrever = messagebox.askyesno(
                "Salvar como",
                "A referência já existe. Deseja sobrescrever?",
                parent=self,
            )
            if not sobrescrever:
                return False
            caminho = self.controlador.salvar_como(
                referencia,
                sobrescrever=True,
            )
        except (RuntimeError, ValueError, OSError) as erro:
            messagebox.showerror("Salvar como", str(erro), parent=self)
            return False
        messagebox.showinfo(
            "Salvar como",
            f"Nova cópia salva em:\n{caminho}",
            parent=self,
        )
        return True

    def _fechar_processo(self) -> bool:
        if not self.controlador.estado.referencia_processo:
            self._status.set("Nenhum processo está aberto.")
            return True
        if not self._confirmar_descarte():
            return False
        self.controlador.fechar_processo()
        return True

    def _confirmar_descarte(self) -> bool:
        if not self.controlador.estado.alteracoes_pendentes:
            return True
        resposta = messagebox.askyesnocancel(
            "Alterações pendentes",
            "Existem alterações não salvas.\n\n"
            "Deseja salvá-las antes de continuar?",
            parent=self,
        )
        if resposta is None:
            return False
        if resposta:
            return self._salvar(exibir_confirmacao=False)
        return True

    def _solicitar_saida(self) -> None:
        if self._confirmar_descarte():
            self.destroy()

    def _sobre(self) -> None:
        messagebox.showinfo(
            "Sobre o SGM",
            "SGM Desktop 0.9.3-F3\n"
            "Gerenciamento de Processos\n\n"
            "Cálculos Trabalhistas",
            parent=self,
        )

    @classmethod
    def _titulo_para(cls, estado: EstadoDesktop) -> str:
        referencia = estado.referencia_processo
        if not referencia:
            return cls.TITULO_BASE
        pendencia = " *" if estado.alteracoes_pendentes else ""
        return f"{cls.TITULO_BASE} — {referencia}{pendencia}"

    @staticmethod
    def _status_para(estado: EstadoDesktop) -> str:
        processo = estado.referencia_processo or "nenhum"
        pendencia = (
            "alterações pendentes"
            if estado.alteracoes_pendentes
            else "salvo"
        )
        return (
            f"Processo ativo: {processo} | "
            f"{estado.mensagem_status} | {pendencia}"
        )

    def _atualizar(self, estado: EstadoDesktop) -> None:
        self._conteudo.atualizar(estado)
        self.title(self._titulo_para(estado))
        self._status.set(self._status_para(estado))
