from .contexto import ContextoTrabalhista
from .executor import Executor
from .extrator import Extrator
from .interpretador import Assunto, Intencao, Interpretador
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
        self.extrator = Extrator()
        self.executor = Executor()
        self.memoria = Memoria()

    def executar(self, texto: str):
        interpretacao = self.interpretador.interpretar(texto)
        entidades = self.extrator.extrair(texto)

        contexto = ContextoTrabalhista(
            interpretacao=interpretacao,
            entidades=entidades,
        )

        nome_ferramenta = self._selecionar_ferramenta(contexto)

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
        contexto: ContextoTrabalhista,
    ) -> str:
        if contexto.intencao is Intencao.PESQUISA_LEGISLACAO:
            return "pesquisa_legislacao"

        if contexto.intencao is Intencao.CALCULADORA:
            return "calculadora"

        return self._FERRAMENTAS_POR_ASSUNTO.get(
            contexto.assunto,
            "calculo_trabalhista",
        )