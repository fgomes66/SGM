from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sgm.desktop.aplicacao.calculo_desktop import ResultadoCalculoDesktop
from sgm.desktop.aplicacao.contrato_trabalho import ContratoTrabalho
from sgm.desktop.aplicacao.evento_contratual_desktop import (
    EventoContratualDesktop,
    TipoEventoDesktop,
)


@dataclass(frozen=True, slots=True)
class FundamentoJuridicoDesktop:
    descricao: str

    def __post_init__(self) -> None:
        descricao = self.descricao.strip()
        object.__setattr__(self, "descricao", descricao)
        if not descricao:
            raise ValueError("O fundamento jurídico é obrigatório.")


@dataclass(frozen=True, slots=True)
class FonteDadosDesktop:
    descricao: str

    def __post_init__(self) -> None:
        descricao = self.descricao.strip()
        object.__setattr__(self, "descricao", descricao)
        if not descricao:
            raise ValueError("A fonte de dados é obrigatória.")


@dataclass(frozen=True, slots=True)
class PremissasTecnicasDesktop:
    competencia: date
    verba: str
    motor: str
    versao_motor: str
    formula: str
    versao_formula: str
    salario_inicial: Decimal
    salario_vigente: Decimal
    origem_base: str
    evento_base: str | None
    divisor: Decimal
    jornada_semanal: Decimal
    quantidade: Decimal
    adicional_percentual: Decimal
    criterio_arredondamento: str
    precisao_intermediaria: int
    precisao_monetaria: int
    fundamentos: tuple[FundamentoJuridicoDesktop, ...]
    fontes: tuple[FonteDadosDesktop, ...]

    def __post_init__(self) -> None:
        for campo in (
            "verba",
            "motor",
            "versao_motor",
            "formula",
            "versao_formula",
            "origem_base",
            "criterio_arredondamento",
        ):
            valor = getattr(self, campo).strip()
            object.__setattr__(self, campo, valor)
            if not valor:
                raise ValueError(f"O campo {campo} é obrigatório.")

        if self.evento_base is not None:
            evento = self.evento_base.strip() or None
            object.__setattr__(self, "evento_base", evento)

        for campo in (
            "salario_inicial",
            "salario_vigente",
            "divisor",
            "jornada_semanal",
            "quantidade",
            "adicional_percentual",
        ):
            valor = getattr(self, campo)
            if not isinstance(valor, Decimal):
                raise TypeError(f"O campo {campo} deve ser Decimal.")
            if not valor.is_finite():
                raise ValueError(f"O campo {campo} deve ser finito.")

        if self.salario_inicial <= 0 or self.salario_vigente <= 0:
            raise ValueError("Os salários devem ser maiores que zero.")
        if self.divisor <= 0 or self.jornada_semanal <= 0:
            raise ValueError("Divisor e jornada devem ser maiores que zero.")
        if self.quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        if self.adicional_percentual < 0:
            raise ValueError("O adicional não pode ser negativo.")
        if self.precisao_intermediaria < 0 or self.precisao_monetaria < 0:
            raise ValueError("As precisões não podem ser negativas.")
        if not self.fundamentos:
            raise ValueError("Ao menos um fundamento jurídico é obrigatório.")
        if not self.fontes:
            raise ValueError("Ao menos uma fonte de dados é obrigatória.")


class PremissasTecnicasBuilderDesktop:
    VERSAO_ENGINE = "0.9.3-G1"
    VERSAO_FORMULA = "1.0"

    @classmethod
    def construir(
        cls,
        contrato: ContratoTrabalho,
        eventos: tuple[EventoContratualDesktop, ...],
        resultado: ResultadoCalculoDesktop,
    ) -> PremissasTecnicasDesktop:
        evento_salarial = cls._evento_salarial_vigente(
            eventos,
            resultado.competencia,
            resultado.salario_base,
        )
        origem = (
            "Evento contratual"
            if evento_salarial is not None
            else "Contrato de trabalho"
        )
        descricao_evento = None
        if evento_salarial is not None:
            descricao_evento = (
                f"{evento_salarial.tipo.titulo} de "
                f"{evento_salarial.data_inicio.strftime('%d/%m/%Y')}"
            )

        fundamentos = [FundamentoJuridicoDesktop(resultado.fundamento)]
        if "art. 59" not in resultado.fundamento.lower():
            fundamentos.append(
                FundamentoJuridicoDesktop("CLT, art. 59")
            )
        if evento_salarial is not None:
            fundamentos.append(
                FundamentoJuridicoDesktop(evento_salarial.fundamento)
            )
        elif contrato.norma_coletiva:
            fundamentos.append(
                FundamentoJuridicoDesktop(contrato.norma_coletiva)
            )

        fontes = [
            FonteDadosDesktop("Processo"),
            FonteDadosDesktop("Contrato de trabalho"),
        ]
        if evento_salarial is not None:
            fontes.append(FonteDadosDesktop(descricao_evento or "Evento contratual"))
        fontes.extend(
            [
                FonteDadosDesktop(
                    f"Resultado persistido {resultado.formula_codigo}"
                ),
                FonteDadosDesktop("Memória técnica persistida"),
            ]
        )

        return PremissasTecnicasDesktop(
            competencia=resultado.competencia,
            verba="Horas Extras",
            motor="SGM Engine — ServicoHoraExtra",
            versao_motor=cls.VERSAO_ENGINE,
            formula=resultado.formula_codigo,
            versao_formula=cls.VERSAO_FORMULA,
            salario_inicial=contrato.salario_inicial,
            salario_vigente=resultado.salario_base,
            origem_base=origem,
            evento_base=descricao_evento,
            divisor=resultado.divisor,
            jornada_semanal=contrato.jornada_semanal_horas,
            quantidade=resultado.quantidade_horas,
            adicional_percentual=resultado.adicional_percentual,
            criterio_arredondamento="ROUND_HALF_UP",
            precisao_intermediaria=6,
            precisao_monetaria=2,
            fundamentos=tuple(dict.fromkeys(fundamentos)),
            fontes=tuple(fontes),
        )

    @staticmethod
    def _evento_salarial_vigente(
        eventos: tuple[EventoContratualDesktop, ...],
        competencia: date,
        salario_base: Decimal,
    ) -> EventoContratualDesktop | None:
        candidatos = [
            evento
            for evento in eventos
            if evento.tipo == TipoEventoDesktop.ALTERACAO_SALARIAL
            and evento.data_inicio <= competencia
            and evento.valor == salario_base
        ]
        if not candidatos:
            return None
        return max(candidatos, key=lambda item: item.chave_ordenacao)
