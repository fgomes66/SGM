from dataclasses import FrozenInstanceError
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from sgm.dominio.financeiro import (
    OrigemFinanceira,
    TipoOperacaoFinanceira,
    ValorMonetario,
)
from sgm.dominio.jornada import Tempo
from sgm.dominio.trabalhista import (
    AdicionalHoraExtra,
    BaseDeCalculo,
    CodigoVerba,
    DependenciaVerba,
    DivisorJornada,
    GrafoDependenciasVerbas,
    ParametrosDSR,
    ServicoHoraExtra,
    ServicoReflexoDSR,
    ServicoValorHora,
    TipoAdicionalHoraExtra,
    TipoBaseCalculo,
)


def criar_valor(texto: str = "3000.00") -> ValorMonetario:
    return ValorMonetario.criar(
        texto,
        OrigemFinanceira(
            descricao="Salário contratual",
            documento_id="HOLERITE-07-2026",
        ),
        momento=datetime(
            2026,
            7,
            31,
            22,
            0,
            tzinfo=timezone.utc,
        ),
    )


def criar_horas_extras(
    horas: str = "05:00",
    salario: str = "3000.00",
    adicional: str = "0.50",
):
    base = BaseDeCalculo(
        valor=criar_valor(salario),
        tipo=TipoBaseCalculo.SALARIO_CONTRATUAL,
        competencia=date(2026, 7, 1),
        descricao="Salário contratual",
        origem_documental="Holerite",
    )
    divisor = DivisorJornada(
        divisor=Decimal("220"),
        jornada_semanal_minutos=44 * 60,
        fundamento="Critério reconhecido.",
    )
    valor_hora = ServicoValorHora.calcular(base, divisor)
    adicional_obj = AdicionalHoraExtra(
        percentual=Decimal(adicional),
        tipo=TipoAdicionalHoraExtra.LEGAL_50,
        fundamento="Critério aplicável.",
    )
    return ServicoHoraExtra.calcular(
        valor_hora,
        Tempo.de_hhmm(horas),
        adicional_obj,
    )


def parametros(
    dias_uteis: int = 25,
    dias_repouso: int = 5,
) -> ParametrosDSR:
    return ParametrosDSR(
        dias_uteis=dias_uteis,
        dias_repouso=dias_repouso,
        fundamento="Calendário e critério informados no processo.",
        criterio_juridico_id=uuid4(),
    )


def test_01_codigo_verba_hora_extra_e_estavel():
    assert CodigoVerba.HORA_EXTRA.value == "HORA_EXTRA"


def test_02_dependencia_valida_e_criada():
    item = DependenciaVerba(
        CodigoVerba.HORA_EXTRA,
        CodigoVerba.DSR,
    )
    assert item.origem == CodigoVerba.HORA_EXTRA
    assert item.destino == CodigoVerba.DSR


def test_03_dependencia_rejeita_autorreferencia():
    with pytest.raises(ValueError):
        DependenciaVerba(
            CodigoVerba.DSR,
            CodigoVerba.DSR,
        )


def test_04_grafo_vazio_possui_ordem_vazia():
    assert GrafoDependenciasVerbas().ordem_calculo() == ()


def test_05_adicionar_dependencia_retorna_novo_grafo():
    original = GrafoDependenciasVerbas()
    novo = original.adicionar(
        CodigoVerba.HORA_EXTRA,
        CodigoVerba.DSR,
    )
    assert original.dependencias == ()
    assert len(novo.dependencias) == 1


def test_06_grafo_remove_dependencias_duplicadas():
    dependencia = DependenciaVerba(
        CodigoVerba.HORA_EXTRA,
        CodigoVerba.DSR,
    )
    grafo = GrafoDependenciasVerbas(
        (dependencia, dependencia)
    )
    assert len(grafo.dependencias) == 1


def test_07_ordem_coloca_hora_extra_antes_do_dsr():
    grafo = GrafoDependenciasVerbas().adicionar(
        CodigoVerba.HORA_EXTRA,
        CodigoVerba.DSR,
    )
    assert grafo.ordem_calculo() == (
        CodigoVerba.HORA_EXTRA,
        CodigoVerba.DSR,
    )


def test_08_ordem_respeita_cadeia_de_tres_verbas():
    grafo = (
        GrafoDependenciasVerbas()
        .adicionar(CodigoVerba.HORA_EXTRA, CodigoVerba.DSR)
        .adicionar(CodigoVerba.DSR, CodigoVerba.FERIAS)
    )
    assert grafo.ordem_calculo() == (
        CodigoVerba.HORA_EXTRA,
        CodigoVerba.DSR,
        CodigoVerba.FERIAS,
    )


def test_09_grafo_rejeita_ciclo():
    with pytest.raises(ValueError):
        GrafoDependenciasVerbas(
            (
                DependenciaVerba(
                    CodigoVerba.HORA_EXTRA,
                    CodigoVerba.DSR,
                ),
                DependenciaVerba(
                    CodigoVerba.DSR,
                    CodigoVerba.HORA_EXTRA,
                ),
            )
        )


def test_10_predecessoras_do_dsr():
    grafo = GrafoDependenciasVerbas().adicionar(
        CodigoVerba.HORA_EXTRA,
        CodigoVerba.DSR,
    )
    assert grafo.predecessoras(CodigoVerba.DSR) == (
        CodigoVerba.HORA_EXTRA,
    )


def test_11_dependentes_diretos_da_hora_extra():
    grafo = GrafoDependenciasVerbas().adicionar(
        CodigoVerba.HORA_EXTRA,
        CodigoVerba.DSR,
    )
    assert grafo.dependentes_diretos(
        CodigoVerba.HORA_EXTRA
    ) == (CodigoVerba.DSR,)


def test_12_dependentes_transitivos():
    grafo = (
        GrafoDependenciasVerbas()
        .adicionar(CodigoVerba.HORA_EXTRA, CodigoVerba.DSR)
        .adicionar(CodigoVerba.DSR, CodigoVerba.FERIAS)
        .adicionar(
            CodigoVerba.FERIAS,
            CodigoVerba.DECIMO_TERCEIRO,
        )
    )
    assert grafo.dependentes_transitivos(
        CodigoVerba.HORA_EXTRA
    ) == (
        CodigoVerba.DECIMO_TERCEIRO,
        CodigoVerba.DSR,
        CodigoVerba.FERIAS,
    )


def test_13_parametros_validos():
    item = parametros()
    assert item.dias_uteis == 25
    assert item.dias_repouso == 5


def test_14_parametros_rejeitam_dias_uteis_zero():
    with pytest.raises(ValueError):
        parametros(dias_uteis=0)


def test_15_parametros_rejeitam_repouso_negativo():
    with pytest.raises(ValueError):
        parametros(dias_repouso=-1)


def test_16_parametros_rejeitam_float():
    with pytest.raises(TypeError):
        ParametrosDSR(
            dias_uteis=25.0,
            dias_repouso=5,
            fundamento="Critério.",
        )


def test_17_parametros_rejeitam_fundamento_vazio():
    with pytest.raises(ValueError):
        ParametrosDSR(
            dias_uteis=25,
            dias_repouso=5,
            fundamento=" ",
        )


def test_18_parametros_sao_imutaveis():
    item = parametros()
    with pytest.raises(FrozenInstanceError):
        item.dias_uteis = 24


def test_19_fator_e_calculado_com_decimal():
    assert parametros().fator == Decimal("0.2")


def test_20_dsr_de_102_27_com_fator_5_sobre_25():
    origem = criar_horas_extras()
    resultado = ServicoReflexoDSR.calcular(
        origem,
        parametros(),
    )
    assert origem.valor_total.valor == Decimal("102.27")
    assert resultado.valor.valor == Decimal("20.45")


def test_21_dsr_zero_quando_nao_ha_repousos():
    resultado = ServicoReflexoDSR.calcular(
        criar_horas_extras(),
        parametros(dias_repouso=0),
    )
    assert resultado.valor.valor == Decimal("0.00")


def test_22_dsr_com_seis_repousos():
    resultado = ServicoReflexoDSR.calcular(
        criar_horas_extras(),
        parametros(dias_uteis=24, dias_repouso=6),
    )
    assert resultado.valor.valor == Decimal("25.57")


def test_23_resultado_preserva_origem():
    origem = criar_horas_extras()
    resultado = ServicoReflexoDSR.calcular(
        origem,
        parametros(),
    )
    assert resultado.origem is origem


def test_24_resultado_preserva_parametros():
    item = parametros()
    resultado = ServicoReflexoDSR.calcular(
        criar_horas_extras(),
        item,
    )
    assert resultado.parametros is item


def test_25_resultado_registra_formula():
    resultado = ServicoReflexoDSR.calcular(
        criar_horas_extras(),
        parametros(),
    )
    assert resultado.formula_codigo == "FM-DSR-001"


def test_26_resultado_registra_verbas_origem_e_destino():
    resultado = ServicoReflexoDSR.calcular(
        criar_horas_extras(),
        parametros(),
    )
    assert resultado.verba_origem == CodigoVerba.HORA_EXTRA
    assert resultado.verba_destino == CodigoVerba.DSR


def test_27_historico_registra_divisao():
    resultado = ServicoReflexoDSR.calcular(
        criar_horas_extras(),
        parametros(),
    )
    tipos = [item.tipo for item in resultado.valor.historico]
    assert TipoOperacaoFinanceira.DIVISAO in tipos


def test_28_historico_registra_multiplicacao():
    resultado = ServicoReflexoDSR.calcular(
        criar_horas_extras(),
        parametros(),
    )
    tipos = [item.tipo for item in resultado.valor.historico]
    assert TipoOperacaoFinanceira.MULTIPLICACAO in tipos


def test_29_historico_termina_com_arredondamento():
    resultado = ServicoReflexoDSR.calcular(
        criar_horas_extras(),
        parametros(),
    )
    assert (
        resultado.valor.historico[-1].tipo
        == TipoOperacaoFinanceira.ARREDONDAMENTO
    )


def test_30_memoria_expoe_formula_e_parametros():
    resultado = ServicoReflexoDSR.calcular(
        criar_horas_extras(),
        parametros(),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "Dias úteis: 25" in memoria
    assert "Dias de repouso: 5" in memoria
    assert "Reflexo em DSR: BRL 20.45" in memoria
    assert "FM-DSR-001" in memoria
