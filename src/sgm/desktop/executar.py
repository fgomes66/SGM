from sgm.desktop.apresentacao import JanelaPrincipal


def executar() -> None:
    aplicacao = JanelaPrincipal()
    aplicacao.mainloop()


if __name__ == "__main__":
    executar()
