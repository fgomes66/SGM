from .modelos import Ferramenta


FERRAMENTAS = [
    Ferramenta(
        nome="calculo_trabalhista",
        descricao="Executa cálculos trabalhistas genéricos.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="calculadora_ferias",
        descricao="Executa cálculos relacionados a férias.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="calculadora_rescisao",
        descricao="Executa cálculos relacionados à rescisão contratual.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="calculadora_fgts",
        descricao="Executa cálculos relacionados ao FGTS.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="calculadora_horas_extras",
        descricao="Executa cálculos relacionados a horas extras.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="calculadora_salario",
        descricao="Executa cálculos relacionados a salário e remuneração.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="pesquisa_legislacao",
        descricao="Pesquisa legislação aplicável.",
        categoria="juridico",
    ),
    Ferramenta(
        nome="calculadora",
        descricao="Executa operações matemáticas gerais.",
        categoria="utilitario",
    ),
]