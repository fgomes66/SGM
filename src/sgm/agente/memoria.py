class Memoria:

    def __init__(self):
        self._historico = []

    def adicionar(self, pergunta: str, resposta: str):

        self._historico.append(
            {
                "pergunta": pergunta,
                "resposta": resposta,
            }
        )

    def historico(self):

        return list(self._historico)