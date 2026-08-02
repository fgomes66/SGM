from .catalogo import FERRAMENTAS
from .modelos import ResultadoFerramenta


class Executor:

    def executar(self, nome_ferramenta: str, objetivo: str) -> ResultadoFerramenta:

        for ferramenta in FERRAMENTAS:

            if ferramenta.nome == nome_ferramenta:

                return ResultadoFerramenta(
                    sucesso=True,
                    mensagem=f"Ferramenta '{nome_ferramenta}' executada.",
                    dados={
                        "objetivo": objetivo,
                        "categoria": ferramenta.categoria,
                    },
                )

        return ResultadoFerramenta(
            sucesso=False,
            mensagem="Ferramenta inexistente.",
        )