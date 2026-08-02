from .executor import Executor
from .interpretador import Assunto, Intencao, Interpretacao, Interpretador
from .memoria import Memoria


class Agente:
    _FERRAMENTAS_POR_ASSUNTO = {
        Assunto.FERIAS: "calculadora_ferias",
        Assunto.RESCISAO: "calculadora_rescisao",
        Assunto.FGTS: "calculadora_fgts",
        Assunto.HORAS_EXTRAS: "calculadora_horas_extras",
        Assunto.SALARIO: "calculadora_salario",
    }

    def __init__(self):
        self.interpretador = Interpretador()
        self.executor = Executor()
        self.memoria = Memoria()

    def executar(self, texto: str):
        interpretacao = self.interpretador.interpretar(texto)
        nome_ferramenta = self._selecionar_ferramenta(interpretacao)

        resultado = self.executor.executar(
            nome_ferramenta,
            texto,
        )

        self.memoria.adicionar(
            texto,
            resultado.mensagem,
        )

        return resultado

    def _selecionar_ferramenta(
        self,
        interpretacao: Interpretacao,
    ) -> str:
        if interpretacao.intencao is Intencao.PESQUISA_LEGISLACAO:
            return "pesquisa_legislacao"

        if interpretacao.intencao is Intencao.CALCULADORA:
            return "calculadora"

        return self._FERRAMENTAS_POR_ASSUNTO.get(
            interpretacao.assunto,
            "calculo_trabalhista",
        )