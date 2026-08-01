from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from sgm.dominio.trabalhista import (
    GeradorLinhaTempoProfissional,
    LinhaTempoProfissional,
    MarcoTemporal,
    PeriodoVigenciaProfissional,
    TipoMarcoTemporal,
)
from sgm.dominio.trabalhista.temporal import CompetenciaCalculo
from tests.unitarios.test_caso_temporal_completo import calcular


def comp(texto: str) -> CompetenciaCalculo:
    return CompetenciaCalculo.de_texto(texto)


def gerar():
    return GeradorLinhaTempoProfissional.gerar(calcular())


def test_01_tipo_marco_estavel():
    assert TipoMarcoTemporal.RESCISAO.value == "RESCISAO"


def test_02_marco_valido():
    item = MarcoTemporal(
        competencia=comp("2022-01"),
        tipo=TipoMarcoTemporal.INICIO_PERIODO,
        titulo="Início",
        descricao="Início do período.",
        fundamento="Plano.",
    )
    assert item.titulo == "Início"


def test_03_marco_rejeita_titulo_vazio():
    with pytest.raises(ValueError):
        MarcoTemporal(
            competencia=comp("2022-01"),
            tipo=TipoMarcoTemporal.INICIO_PERIODO,
            titulo=" ",
            descricao="Descrição.",
            fundamento="Plano.",
        )


def test_04_marco_rejeita_ordem_zero():
    with pytest.raises(ValueError):
        MarcoTemporal(
            competencia=comp("2022-01"),
            tipo=TipoMarcoTemporal.INICIO_PERIODO,
            titulo="Início",
            descricao="Descrição.",
            fundamento="Plano.",
            ordem_na_competencia=0,
        )


def test_05_vigencia_valida():
    item = PeriodoVigenciaProfissional(
        inicio=comp("2022-01"),
        fim=comp("2022-02"),
        salario=Decimal("3000.00"),
        divisor=Decimal("220"),
        jornada_semanal_minutos=2640,
        ativo=True,
        rescindido=False,
    )
    assert item.descricao_estado == "ATIVO"


def test_06_vigencia_rejeita_periodo_invertido():
    with pytest.raises(ValueError):
        PeriodoVigenciaProfissional(
            inicio=comp("2022-02"),
            fim=comp("2022-01"),
            salario=Decimal("3000.00"),
            divisor=Decimal("220"),
            jornada_semanal_minutos=2640,
            ativo=True,
            rescindido=False,
        )


def test_07_vigencia_rescindida_nao_pode_estar_ativa():
    with pytest.raises(ValueError):
        PeriodoVigenciaProfissional(
            inicio=comp("2022-01"),
            fim=comp("2022-01"),
            salario=Decimal("3000.00"),
            divisor=Decimal("220"),
            jornada_semanal_minutos=2640,
            ativo=True,
            rescindido=True,
        )


def test_08_gerador_retorna_linha_profissional():
    assert isinstance(gerar(), LinhaTempoProfissional)


def test_09_linha_identifica_referencia():
    assert gerar().referencia == "CASO-0013"


def test_10_linha_identifica_periodo():
    item = gerar()
    assert item.periodo.inicio == comp("2022-01")
    assert item.periodo.fim == comp("2022-09")


def test_11_linha_possui_marcos_inicial_e_final():
    item = gerar()
    assert item.marcos[0].tipo == TipoMarcoTemporal.INICIO_PERIODO
    assert item.marcos[-1].tipo == TipoMarcoTemporal.FIM_PERIODO


def test_12_linha_registra_reajuste():
    item = gerar()
    reajuste = next(
        marco for marco in item.marcos
        if "Reajuste" in marco.titulo
    )
    assert reajuste.competencia == comp("2022-03")
    assert "novo salário=3300.00" in reajuste.descricao


def test_13_linha_registra_afastamento():
    item = gerar()
    afastamento = next(
        marco for marco in item.marcos
        if marco.tipo == TipoMarcoTemporal.INATIVIDADE
    )
    assert afastamento.competencia == comp("2022-04")


def test_14_linha_registra_retorno():
    item = gerar()
    retorno = next(
        marco for marco in item.marcos
        if marco.tipo == TipoMarcoTemporal.RETOMADA
    )
    assert retorno.competencia == comp("2022-05")


def test_15_linha_registra_alteracao_divisor():
    item = gerar()
    divisor = next(
        marco for marco in item.marcos
        if "Divisor" in marco.titulo
    )
    assert "novo divisor=200" in divisor.descricao


def test_16_linha_registra_promocao():
    item = gerar()
    promocao = next(
        marco for marco in item.marcos
        if "Promocao" in marco.titulo
    )
    assert promocao.competencia == comp("2022-07")
    assert "novo salário=4000.00" in promocao.descricao


def test_17_linha_registra_rescisao():
    item = gerar()
    rescisao = next(
        marco for marco in item.marcos
        if marco.tipo == TipoMarcoTemporal.RESCISAO
    )
    assert rescisao.competencia == comp("2022-08")


def test_18_vigencias_agregam_competencias_iguais():
    item = gerar()
    primeira = item.vigencias[0]
    assert primeira.inicio == comp("2022-01")
    assert primeira.fim == comp("2022-02")
    assert primeira.salario == Decimal("3000.00")


def test_19_vigencia_do_reajuste():
    item = gerar()
    vigencia = next(
        v for v in item.vigencias
        if v.inicio == comp("2022-03")
    )
    assert vigencia.fim == comp("2022-03")
    assert vigencia.salario == Decimal("3300.00")
    assert vigencia.ativo is True


def test_20_vigencia_do_afastamento():
    item = gerar()
    vigencia = next(
        v for v in item.vigencias
        if v.inicio == comp("2022-04")
    )
    assert vigencia.descricao_estado == "INATIVO"


def test_21_vigencia_apos_retorno():
    item = gerar()
    vigencia = next(
        v for v in item.vigencias
        if v.inicio == comp("2022-05")
    )
    assert vigencia.ativo is True
    assert vigencia.salario == Decimal("3300.00")


def test_22_vigencia_do_novo_divisor():
    item = gerar()
    vigencia = next(
        v for v in item.vigencias
        if v.inicio == comp("2022-06")
    )
    assert vigencia.divisor == Decimal("200")


def test_23_vigencia_da_promocao():
    item = gerar()
    vigencia = next(
        v for v in item.vigencias
        if v.inicio == comp("2022-07")
    )
    assert vigencia.salario == Decimal("4000.00")


def test_24_vigencia_rescindida_vai_ate_fim_periodo():
    item = gerar()
    ultima = item.vigencias[-1]
    assert ultima.inicio == comp("2022-08")
    assert ultima.fim == comp("2022-09")
    assert ultima.descricao_estado == "RESCINDIDO"


def test_25_texto_contem_marcos():
    texto = gerar().como_texto()
    assert "MARCOS CONTRATUAIS" in texto
    assert "2022-03 | EVENTO_CONTRATUAL" in texto


def test_26_texto_contem_vigencias():
    texto = gerar().como_texto()
    assert "PERÍODOS DE VIGÊNCIA" in texto
    assert "2022-01 a 2022-02" in texto
    assert "estado=ATIVO" in texto


def test_27_linha_registra_versao():
    assert gerar().versao_documento == "0.9.2-C"


def test_28_linha_e_imutavel():
    item = gerar()
    with pytest.raises(FrozenInstanceError):
        item.referencia = "OUTRA"


def test_29_marcos_estao_ordenados():
    item = gerar()
    chaves = tuple(
        (marco.competencia, marco.ordem_na_competencia)
        for marco in item.marcos
    )
    assert chaves == tuple(sorted(chaves))


def test_30_geracao_e_reproduzivel():
    primeiro = gerar()
    segundo = gerar()

    assert primeiro.como_texto() == segundo.como_texto()

    conteudo_primeiro = tuple(
        (
            marco.competencia,
            marco.tipo,
            marco.titulo,
            marco.descricao,
            marco.fundamento,
            marco.ordem_na_competencia,
        )
        for marco in primeiro.marcos
    )
    conteudo_segundo = tuple(
        (
            marco.competencia,
            marco.tipo,
            marco.titulo,
            marco.descricao,
            marco.fundamento,
            marco.ordem_na_competencia,
        )
        for marco in segundo.marcos
    )

    assert conteudo_primeiro == conteudo_segundo
    assert primeiro.vigencias == segundo.vigencias
