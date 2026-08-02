from .executor import Executor
from .memoria import Memoria
from .planejador import Planejador


class Agente:

    def __init__(self):
        self.planejador = Planejador()
        self.executor = Executor()
        self.memoria = Memoria()

    def executar(self, objetivo: str):

        plano = self.planejador.criar_plano(objetivo)

        ultimo = None

        for passo in plano.passos:
            ultimo = self.executor.executar(
                passo.ferramenta,
                passo.objetivo,
            )

        self.memoria.adicionar(
            objetivo,
            ultimo.mensagem if ultimo else "",
        )

        return ultimo