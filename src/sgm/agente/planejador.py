from .modelos import PlanoExecucao, PassoPlano


class Planejador:

    def criar_plano(self, objetivo: str) -> PlanoExecucao:

        objetivo_lower = objetivo.lower()

        if "cálculo" in objetivo_lower or "calculo" in objetivo_lower:
            ferramenta = "calculo_trabalhista"

        elif "lei" in objetivo_lower:
            ferramenta = "pesquisa_legislacao"

        else:
            ferramenta = "calculadora"

        return PlanoExecucao(
            objetivo=objetivo,
            passos=[
                PassoPlano(
                    ferramenta=ferramenta,
                    objetivo=objetivo,
                )
            ],
        )