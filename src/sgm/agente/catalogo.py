from .modelos import Ferramenta


FERRAMENTAS = [
    Ferramenta(
        nome="calculo_trabalhista",
        descricao="Executa cálculos trabalhistas.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="calculadora",
        descricao="Executa operações matemáticas.",
        categoria="utilitario",
    ),
    Ferramenta(
        nome="pesquisa_legislacao",
        descricao="Pesquisa legislação aplicável.",
        categoria="juridico",
    ),
]