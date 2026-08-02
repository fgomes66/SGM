from .executor import Executor
from .interpretador import Interpretador
from .memoria import Memoria


class Agente:

    def __init__(self):
        self.interpretador = Interpretador()
        self.executor = Executor()
        self.memoria = Memoria()

    def executar(self, texto: str):

        interpretacao = self.interpretador.interpretar(texto)

        resultado = self.executor.executar(
            interpretacao.intencao.value,
            texto,
        )

        self.memoria.adicionar(
            texto,
            resultado.mensagem,
        )

        return resultado