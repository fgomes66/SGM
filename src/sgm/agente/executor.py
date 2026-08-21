from .adaptadores.plano_trabalhista import AdaptadorPlanoTrabalhista
from .catalogo import FERRAMENTAS
from .contexto import ContextoTrabalhista
from .modelos import ResultadoFerramenta

from sgm.dominio.trabalhista import ServicoFerias


class Executor:

    def executar(
        self,
        nome_ferramenta: str,
        contexto: ContextoTrabalhista | str,
    ) -> ResultadoFerramenta:

        for ferramenta in FERRAMENTAS:

            if ferramenta.nome == nome_ferramenta:

                if (
                    nome_ferramenta == "calculadora_ferias"
                    and isinstance(contexto, ContextoTrabalhista)
                ):
                    base, parametros = (
                        AdaptadorPlanoTrabalhista.preparar_ferias(
                            contexto
                        )
                    )

                    ferias = ServicoFerias.calcular(
                        base,
                        parametros,
                    )

                    return ResultadoFerramenta(
                        sucesso=True,
                        mensagem="Cálculo de férias executado.",
                        dados={
                            "valor_ferias": str(
                                ferias.valor_ferias.valor
                            ),
                            "valor_terco": str(
                                ferias.valor_terco.valor
                            ),
                            "valor_total": str(
                                ferias.valor_total.valor
                            ),
                            "moeda": ferias.valor_total.moeda,
                            "avos": ferias.parametros.avos,
                            "memoria": list(
                                ferias.memoria_resumida()
                            ),
                        },
                    )

                dados = self._preparar_dados(
                    contexto=contexto,
                    categoria=ferramenta.categoria,
                )

                return ResultadoFerramenta(
                    sucesso=True,
                    mensagem=f"Ferramenta '{nome_ferramenta}' executada.",
                    dados=dados,
                )

        return ResultadoFerramenta(
            sucesso=False,
            mensagem="Ferramenta inexistente.",
        )

    def _preparar_dados(
        self,
        contexto: ContextoTrabalhista | str,
        categoria: str,
    ) -> dict:

        if isinstance(contexto, str):
            return {
                "objetivo": contexto,
                "categoria": categoria,
            }

        entidades = [
            {
                "tipo": entidade.tipo,
                "valor": entidade.valor,
            }
            for entidade in contexto.entidades
        ]

        return {
            "objetivo": contexto.texto,
            "categoria": categoria,
            "intencao": contexto.intencao.value,
            "assunto": contexto.assunto.value,
            "entidades": entidades,
        }
