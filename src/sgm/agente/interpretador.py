from dataclasses import dataclass
from enum import Enum


class Intencao(str, Enum):
    CALCULO_TRABALHISTA = "calculo_trabalhista"
    PESQUISA_LEGISLACAO = "pesquisa_legislacao"
    CALCULADORA = "calculadora"


@dataclass(slots=True, frozen=True)
class Interpretacao:
    texto_original: str
    intencao: Intencao


class Interpretador:

    def interpretar(self, texto: str) -> Interpretacao:
        texto_normalizado = texto.strip().lower()

        termos_calculo = (
            "cálculo",
            "calculo",
            "calcular",
            "férias",
            "ferias",
            "rescisão",
            "rescisao",
            "fgts",
            "horas extras",
            "salário",
            "salario",
        )

        termos_legislacao = (
            "lei",
            "artigo",
            "clt",
            "legislação",
            "legislacao",
            "norma",
            "decreto",
        )

        if any(termo in texto_normalizado for termo in termos_calculo):
            intencao = Intencao.CALCULO_TRABALHISTA
        elif any(termo in texto_normalizado for termo in termos_legislacao):
            intencao = Intencao.PESQUISA_LEGISLACAO
        else:
            intencao = Intencao.CALCULADORA

        return Interpretacao(
            texto_original=texto,
            intencao=intencao,
        )