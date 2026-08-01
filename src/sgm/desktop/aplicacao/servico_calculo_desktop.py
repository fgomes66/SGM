from __future__ import annotations

from datetime import date
from decimal import Decimal

from sgm.desktop.aplicacao.calculo_desktop import ResultadoCalculoDesktop
from sgm.desktop.aplicacao.contrato_trabalho import ContratoTrabalho
from sgm.desktop.aplicacao.evento_contratual_desktop import (
    EventoContratualDesktop,
    TipoEventoDesktop,
)
from sgm.dominio.financeiro import OrigemFinanceira, ValorMonetario
from sgm.dominio.jornada import Tempo
from sgm.dominio.trabalhista.horas_extras_financeiras import (
    AdicionalHoraExtra,
    TipoAdicionalHoraExtra,
)
from sgm.dominio.trabalhista.horas_extras_financeiras.servicos import (
    ServicoHoraExtra,
)
from sgm.dominio.trabalhista.jornada_financeira import (
    DivisorJornada,
    ServicoValorHora,
)
from sgm.dominio.trabalhista.remuneracao import (
    BaseDeCalculo,
    TipoBaseCalculo,
)


class ServicoCalculoDesktop:
    @staticmethod
    def salario_vigente(
        contrato: ContratoTrabalho,
        eventos: tuple[EventoContratualDesktop, ...],
        competencia: date,
    ) -> Decimal:
        salario = contrato.salario_inicial
        alteracoes = sorted(
            (
                evento
                for evento in eventos
                if evento.tipo == TipoEventoDesktop.ALTERACAO_SALARIAL
                and evento.data_inicio <= competencia
                and evento.valor is not None
            ),
            key=lambda item: item.chave_ordenacao,
        )
        if alteracoes:
            salario = alteracoes[-1].valor
        return salario

    @staticmethod
    def divisor_vigente(
        contrato: ContratoTrabalho,
        eventos: tuple[EventoContratualDesktop, ...],
        competencia: date,
    ) -> Decimal:
        divisor = contrato.divisor_jornada
        alteracoes = sorted(
            (
                evento
                for evento in eventos
                if evento.tipo == TipoEventoDesktop.ALTERACAO_DIVISOR
                and evento.data_inicio <= competencia
                and evento.valor is not None
            ),
            key=lambda item: item.chave_ordenacao,
        )
        if alteracoes:
            divisor = alteracoes[-1].valor
        return divisor

    @classmethod
    def calcular_horas_extras(
        cls,
        contrato: ContratoTrabalho,
        eventos: tuple[EventoContratualDesktop, ...],
        competencia: date,
        quantidade_horas: Decimal,
        adicional_percentual: Decimal,
        fundamento: str,
    ) -> ResultadoCalculoDesktop:
        if competencia < contrato.data_admissao:
            raise ValueError(
                "A competência não pode anteceder a admissão."
            )
        if (
            contrato.data_desligamento is not None
            and competencia > contrato.data_desligamento
        ):
            raise ValueError(
                "A competência não pode ser posterior ao desligamento."
            )

        salario = cls.salario_vigente(
            contrato,
            eventos,
            competencia,
        )
        divisor_valor = cls.divisor_vigente(
            contrato,
            eventos,
            competencia,
        )

        origem = OrigemFinanceira(
            descricao="Cálculo de horas extras no SGM Desktop.",
            formula_codigo="FM-HE-001",
        )
        monetario = ValorMonetario.criar(
            format(salario, "f"),
            origem,
        )
        base = BaseDeCalculo(
            valor=monetario,
            tipo=TipoBaseCalculo.SALARIO_CONTRATUAL,
            competencia=competencia,
            descricao="Salário vigente na competência.",
            origem_documental="Contrato e eventos contratuais.",
        )
        divisor = DivisorJornada(
            divisor=divisor_valor,
            jornada_semanal_minutos=int(
                contrato.jornada_semanal_horas * Decimal("60")
            ),
            fundamento="Contrato e eventos contratuais.",
        )
        valor_hora = ServicoValorHora.calcular(
            base,
            divisor,
        )
        adicional = AdicionalHoraExtra(
            percentual=adicional_percentual,
            tipo=TipoAdicionalHoraExtra.PERSONALIZADO,
            fundamento=fundamento,
        )
        minutos = int(
            (quantidade_horas * Decimal("60")).to_integral_value()
        )
        hora_extra = ServicoHoraExtra.calcular(
            valor_hora,
            Tempo(minutos),
            adicional,
        )

        return ResultadoCalculoDesktop(
            competencia=competencia,
            salario_base=salario,
            divisor=divisor_valor,
            quantidade_horas=quantidade_horas,
            adicional_percentual=adicional_percentual,
            valor_hora=valor_hora.valor.valor,
            valor_hora_com_adicional=(
                hora_extra.valor_hora_com_adicional.valor
            ),
            valor_total=hora_extra.valor_total.valor,
            fundamento=fundamento,
            formula_codigo=hora_extra.formula_codigo,
        )
