from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any
from uuid import UUID, uuid4

from sgm.dominio.financeiro.modelos.operacao_financeira import (
    OperacaoFinanceira,
    TipoOperacaoFinanceira,
)
from sgm.dominio.financeiro.modelos.origem_financeira import OrigemFinanceira


_CENTAVO = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class ValorMonetario:
    valor: Decimal
    origem: OrigemFinanceira
    moeda: str = "BRL"
    historico: tuple[OperacaoFinanceira, ...] = ()
    id: UUID = field(default_factory=uuid4)
    versao: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.valor, Decimal):
            raise TypeError("ValorMonetario exige Decimal; float é proibido.")
        if not self.valor.is_finite():
            raise ValueError("O valor monetário deve ser finito.")

        moeda = self.moeda.strip().upper()
        object.__setattr__(self, "moeda", moeda)

        if len(moeda) != 3 or not moeda.isalpha():
            raise ValueError("A moeda deve usar código alfabético de três letras.")
        if self.versao < 1:
            raise ValueError("A versão deve ser igual ou superior a 1.")

    @classmethod
    def criar(
        cls,
        valor: str,
        origem: OrigemFinanceira,
        moeda: str = "BRL",
        momento: datetime | None = None,
    ) -> "ValorMonetario":
        try:
            decimal = Decimal(valor)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Valor monetário inválido: {valor!r}.") from exc

        instante = momento or datetime.now().astimezone()
        operacao = OperacaoFinanceira(
            tipo=TipoOperacaoFinanceira.CRIACAO,
            descricao="Criação do valor monetário.",
            operandos=(format(decimal, "f"),),
            resultado=format(decimal, "f"),
            executada_em=instante,
        )
        return cls(
            valor=decimal,
            origem=origem,
            moeda=moeda,
            historico=(operacao,),
        )

    def _validar_moeda(self, outro: "ValorMonetario") -> None:
        if self.moeda != outro.moeda:
            raise ValueError(
                f"Moedas incompatíveis: {self.moeda} e {outro.moeda}."
            )

    def _novo(
        self,
        valor: Decimal,
        tipo: TipoOperacaoFinanceira,
        descricao: str,
        operandos: tuple[str, ...],
        momento: datetime | None = None,
    ) -> "ValorMonetario":
        instante = momento or datetime.now().astimezone()
        operacao = OperacaoFinanceira(
            tipo=tipo,
            descricao=descricao,
            operandos=operandos,
            resultado=format(valor, "f"),
            executada_em=instante,
        )
        return ValorMonetario(
            valor=valor,
            origem=self.origem,
            moeda=self.moeda,
            historico=self.historico + (operacao,),
            versao=self.versao + 1,
        )

    def somar(self, outro: "ValorMonetario") -> "ValorMonetario":
        self._validar_moeda(outro)
        resultado = self.valor + outro.valor
        return self._novo(
            resultado,
            TipoOperacaoFinanceira.SOMA,
            "Soma de valores monetários.",
            (format(self.valor, "f"), format(outro.valor, "f")),
        )

    def subtrair(self, outro: "ValorMonetario") -> "ValorMonetario":
        self._validar_moeda(outro)
        resultado = self.valor - outro.valor
        return self._novo(
            resultado,
            TipoOperacaoFinanceira.SUBTRACAO,
            "Subtração de valores monetários.",
            (format(self.valor, "f"), format(outro.valor, "f")),
        )

    def multiplicar(self, fator: Decimal) -> "ValorMonetario":
        if not isinstance(fator, Decimal):
            raise TypeError("O fator deve ser Decimal.")
        if not fator.is_finite():
            raise ValueError("O fator deve ser finito.")
        resultado = self.valor * fator
        return self._novo(
            resultado,
            TipoOperacaoFinanceira.MULTIPLICACAO,
            "Multiplicação por fator.",
            (format(self.valor, "f"), format(fator, "f")),
        )

    def dividir(self, divisor: Decimal) -> "ValorMonetario":
        if not isinstance(divisor, Decimal):
            raise TypeError("O divisor deve ser Decimal.")
        if not divisor.is_finite():
            raise ValueError("O divisor deve ser finito.")
        if divisor == 0:
            raise ZeroDivisionError("O divisor não pode ser zero.")
        resultado = self.valor / divisor
        return self._novo(
            resultado,
            TipoOperacaoFinanceira.DIVISAO,
            "Divisão por divisor.",
            (format(self.valor, "f"), format(divisor, "f")),
        )

    def aplicar_percentual(self, percentual: Decimal) -> "ValorMonetario":
        if not isinstance(percentual, Decimal):
            raise TypeError("O percentual deve ser Decimal.")
        if not percentual.is_finite():
            raise ValueError("O percentual deve ser finito.")
        resultado = self.valor * percentual
        return self._novo(
            resultado,
            TipoOperacaoFinanceira.APLICACAO_PERCENTUAL,
            "Aplicação do percentual sobre o principal.",
            (format(self.valor, "f"), format(percentual, "f")),
        )

    def acrescer_percentual(self, percentual: Decimal) -> "ValorMonetario":
        if not isinstance(percentual, Decimal):
            raise TypeError("O percentual deve ser Decimal.")
        if not percentual.is_finite():
            raise ValueError("O percentual deve ser finito.")
        resultado = self.valor * (Decimal("1") + percentual)
        return self._novo(
            resultado,
            TipoOperacaoFinanceira.ACRESCIMO_PERCENTUAL,
            "Acréscimo percentual ao principal.",
            (format(self.valor, "f"), format(percentual, "f")),
        )

    def arredondar_centavos(self) -> "ValorMonetario":
        resultado = self.valor.quantize(_CENTAVO, rounding=ROUND_HALF_UP)
        return self._novo(
            resultado,
            TipoOperacaoFinanceira.ARREDONDAMENTO,
            "Arredondamento monetário para centavos pelo método HALF_UP.",
            (format(self.valor, "f"),),
        )

    def negar(self) -> "ValorMonetario":
        return self._novo(
            -self.valor,
            TipoOperacaoFinanceira.NEGACAO,
            "Inversão do sinal do valor.",
            (format(self.valor, "f"),),
        )

    def absoluto(self) -> "ValorMonetario":
        return self._novo(
            abs(self.valor),
            TipoOperacaoFinanceira.VALOR_ABSOLUTO,
            "Conversão para valor absoluto.",
            (format(self.valor, "f"),),
        )

    def para_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "valor": format(self.valor, "f"),
            "moeda": self.moeda,
            "versao": self.versao,
            "origem": {
                "descricao": self.origem.descricao,
                "processo_id": (
                    str(self.origem.processo_id)
                    if self.origem.processo_id is not None
                    else None
                ),
                "criterio_id": (
                    str(self.origem.criterio_id)
                    if self.origem.criterio_id is not None
                    else None
                ),
                "formula_codigo": self.origem.formula_codigo,
                "documento_id": self.origem.documento_id,
                "observacao": self.origem.observacao,
            },
            "historico": [
                {
                    "id": str(item.id),
                    "tipo": item.tipo.value,
                    "descricao": item.descricao,
                    "operandos": list(item.operandos),
                    "resultado": item.resultado,
                    "executada_em": item.executada_em.isoformat(),
                }
                for item in self.historico
            ],
        }

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> "ValorMonetario":
        origem_dados = dados["origem"]
        origem = OrigemFinanceira(
            descricao=origem_dados["descricao"],
            processo_id=(
                UUID(origem_dados["processo_id"])
                if origem_dados["processo_id"]
                else None
            ),
            criterio_id=(
                UUID(origem_dados["criterio_id"])
                if origem_dados["criterio_id"]
                else None
            ),
            formula_codigo=origem_dados["formula_codigo"],
            documento_id=origem_dados["documento_id"],
            observacao=origem_dados["observacao"],
        )
        historico = tuple(
            OperacaoFinanceira(
                id=UUID(item["id"]),
                tipo=TipoOperacaoFinanceira(item["tipo"]),
                descricao=item["descricao"],
                operandos=tuple(item["operandos"]),
                resultado=item["resultado"],
                executada_em=datetime.fromisoformat(item["executada_em"]),
            )
            for item in dados["historico"]
        )
        return cls(
            id=UUID(dados["id"]),
            valor=Decimal(dados["valor"]),
            moeda=dados["moeda"],
            origem=origem,
            historico=historico,
            versao=int(dados["versao"]),
        )
