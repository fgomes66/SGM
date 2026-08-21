from .modelos import Ferramenta


FERRAMENTAS = [
    Ferramenta(
        nome="calculo_trabalhista",
        descricao="Executa cÃ¡lculos trabalhistas genÃ©ricos.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="calculadora_ferias",
        descricao="Executa cÃ¡lculos relacionados a fÃ©rias.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="calculadora_decimo_terceiro",
        descricao="Executa cálculos relacionados ao 13º salário.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="calculadora_rescisao",
        descricao="Executa cÃ¡lculos relacionados Ã  rescisÃ£o contratual.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="calculadora_fgts",
        descricao="Executa cÃ¡lculos relacionados ao FGTS.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="calculadora_horas_extras",
        descricao="Executa cÃ¡lculos relacionados a horas extras.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="calculadora_salario",
        descricao="Executa cÃ¡lculos relacionados a salÃ¡rio e remuneraÃ§Ã£o.",
        categoria="trabalhista",
    ),
    Ferramenta(
        nome="pesquisa_legislacao",
        descricao="Pesquisa legislaÃ§Ã£o aplicÃ¡vel.",
        categoria="juridico",
    ),
    Ferramenta(
        nome="calculadora",
        descricao="Executa operaÃ§Ãµes matemÃ¡ticas gerais.",
        categoria="utilitario",
    ),
]
