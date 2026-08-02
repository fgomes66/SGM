from dataclasses import dataclass
from enum import Enum


class Intencao(str, Enum):
    CALCULO_TRABALHISTA = "calculo_trabalhista"
    PESQUISA_LEGISLACAO = "pesquisa_legislacao"
    CALCULADORA = "calculadora"


class Assunto(str, Enum):
    FERIAS = "ferias"
    RESCISAO = "rescisao"
    FGTS = "fgts"
    HORAS_EXTRAS = "horas_extras"
    SALARIO = "salario"
    CLT = "clt"
    LEGISLACAO = "legislacao"
    MATEMATICA = "matematica"
    GENERICO = "generico"


@dataclass(slots=True, frozen=True)
class Interpretacao:
    texto_original: str
    texto_normalizado: str
    intencao: Intencao
    assunto: Assunto


class Interpretador:

    def interpretar(self, texto: str) -> Interpretacao:
        texto_normalizado = texto.strip().lower()

        intencao = self._identificar_intencao(texto_normalizado)
        assunto = self._identificar_assunto(texto_normalizado)

        return Interpretacao(
            texto_original=texto,
            texto_normalizado=texto_normalizado,
            intencao=intencao,
            assunto=assunto,
        )

    def _identificar_intencao(self, texto: str) -> Intencao:
        termos_calculo_trabalhista = (
            "cálculo",
            "calculo",
            "calcular",
            "quanto recebo",
            "quanto vou receber",
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

        if any(termo in texto for termo in termos_calculo_trabalhista):
            return Intencao.CALCULO_TRABALHISTA

        if any(termo in texto for termo in termos_legislacao):
            return Intencao.PESQUISA_LEGISLACAO

        return Intencao.CALCULADORA

    def _identificar_assunto(self, texto: str) -> Assunto:
        assuntos = (
            (Assunto.FERIAS, ("férias", "ferias")),
            (Assunto.RESCISAO, ("rescisão", "rescisao", "demissão", "demissao")),
            (Assunto.FGTS, ("fgts", "fundo de garantia")),
            (Assunto.HORAS_EXTRAS, ("hora extra", "horas extras")),
            (Assunto.SALARIO, ("salário", "salario", "remuneração", "remuneracao")),
            (Assunto.CLT, ("clt",)),
            (
                Assunto.LEGISLACAO,
                ("lei", "artigo", "legislação", "legislacao", "norma", "decreto"),
            ),
            (
                Assunto.MATEMATICA,
                ("somar", "subtrair", "multiplicar", "dividir", "calculadora"),
            ),
        )

        for assunto, termos in assuntos:
            if any(termo in texto for termo in termos):
                return assunto

        return Assunto.GENERICO