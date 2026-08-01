from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sgm.desktop.aplicacao.calculo_desktop import ResultadoCalculoDesktop


def _moeda(valor: Decimal, casas: int = 2) -> str:
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def _numero(valor: Decimal, casas: int = 6) -> str:
    texto = f"{valor:.{casas}f}"
    return texto.replace(".", ",")


@dataclass(frozen=True, slots=True)
class PassoMemoriaCalculo:
    ordem: int
    titulo: str
    expressao: str
    resultado: str
    explicacao: str

    def __post_init__(self) -> None:
        titulo = self.titulo.strip()
        expressao = self.expressao.strip()
        resultado = self.resultado.strip()
        explicacao = self.explicacao.strip()

        object.__setattr__(self, "titulo", titulo)
        object.__setattr__(self, "expressao", expressao)
        object.__setattr__(self, "resultado", resultado)
        object.__setattr__(self, "explicacao", explicacao)

        if self.ordem <= 0:
            raise ValueError("A ordem do passo deve ser positiva.")
        if not titulo:
            raise ValueError("O título do passo é obrigatório.")
        if not expressao:
            raise ValueError("A expressão do passo é obrigatória.")
        if not resultado:
            raise ValueError("O resultado do passo é obrigatório.")
        if not explicacao:
            raise ValueError("A explicação do passo é obrigatória.")


@dataclass(frozen=True, slots=True)
class MemoriaCalculoDesktop:
    titulo: str
    competencia: str
    verba: str
    fundamento: str
    formula_codigo: str
    motor: str
    passos: tuple[PassoMemoriaCalculo, ...]
    valor_total: Decimal

    def __post_init__(self) -> None:
        for campo in (
            "titulo",
            "competencia",
            "verba",
            "fundamento",
            "formula_codigo",
            "motor",
        ):
            valor = getattr(self, campo).strip()
            object.__setattr__(self, campo, valor)
            if not valor:
                raise ValueError(f"O campo {campo} é obrigatório.")

        if not isinstance(self.passos, tuple) or not self.passos:
            raise ValueError("A memória deve possuir ao menos um passo.")
        if any(
            not isinstance(item, PassoMemoriaCalculo)
            for item in self.passos
        ):
            raise TypeError("Os passos da memória são inválidos.")
        if not isinstance(self.valor_total, Decimal):
            raise TypeError("O valor total deve ser Decimal.")

    def como_texto(self) -> str:
        linhas = [
            self.titulo.upper(),
            "",
            f"Competência: {self.competencia}",
            f"Verba: {self.verba}",
            f"Fundamento: {self.fundamento}",
            f"Fórmula oficial: {self.formula_codigo}",
            f"Motor: {self.motor}",
            "",
        ]

        for passo in self.passos:
            linhas.extend(
                [
                    f"PASSO {passo.ordem} — {passo.titulo}",
                    passo.explicacao,
                    "",
                    f"Expressão: {passo.expressao}",
                    f"Resultado: {passo.resultado}",
                    "",
                ]
            )

        linhas.extend(
            [
                "RESULTADO FINAL",
                f"R$ {_moeda(self.valor_total)}",
            ]
        )
        return "\n".join(linhas)


class ServicoMemoriaCalculoDesktop:
    MOTOR = "ServicoValorHora + ServicoHoraExtra"

    @classmethod
    def gerar(
        cls,
        resultado: ResultadoCalculoDesktop,
    ) -> MemoriaCalculoDesktop:
        if not isinstance(resultado, ResultadoCalculoDesktop):
            raise TypeError(
                "O resultado deve ser ResultadoCalculoDesktop."
            )

        multiplicador = (
            Decimal("1") + resultado.adicional_percentual
        )

        passos = (
            PassoMemoriaCalculo(
                ordem=1,
                titulo="Apuração do valor da hora normal",
                expressao=(
                    f"R$ {_moeda(resultado.salario_base)} ÷ "
                    f"{_numero(resultado.divisor, 2)}"
                ),
                resultado=(
                    f"R$ {_numero(resultado.valor_hora, 6)}"
                ),
                explicacao=(
                    "Divisão do salário-base vigente pelo divisor "
                    "contratual vigente na competência."
                ),
            ),
            PassoMemoriaCalculo(
                ordem=2,
                titulo="Aplicação do adicional de horas extras",
                expressao=(
                    f"R$ {_numero(resultado.valor_hora, 6)} × "
                    f"{_numero(multiplicador, 2)}"
                ),
                resultado=(
                    "R$ "
                    f"{_numero(resultado.valor_hora_com_adicional, 6)}"
                ),
                explicacao=(
                    "Aplicação do adicional de "
                    f"{_numero(resultado.adicional_percentual * 100, 2)}% "
                    "sobre a hora normal."
                ),
            ),
            PassoMemoriaCalculo(
                ordem=3,
                titulo="Multiplicação pela quantidade de horas",
                expressao=(
                    "R$ "
                    f"{_numero(resultado.valor_hora_com_adicional, 6)} × "
                    f"{_numero(resultado.quantidade_horas, 2)}"
                ),
                resultado=f"R$ {_moeda(resultado.valor_total)}",
                explicacao=(
                    "Multiplicação do valor unitário da hora extra "
                    "pela quantidade apurada."
                ),
            ),
        )

        return MemoriaCalculoDesktop(
            titulo="Memória Técnica do Cálculo",
            competencia=resultado.competencia.isoformat(),
            verba="Horas Extras",
            fundamento=resultado.fundamento,
            formula_codigo=resultado.formula_codigo,
            motor=cls.MOTOR,
            passos=passos,
            valor_total=resultado.valor_total,
        )
