from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from sgm.dominio.calculos import (
    ItemPlanoCalculo,
    NaturezaVerba,
    PlanoCalculo,
    StatusPlanoCalculo,
)
from sgm.dominio.juridico import (
    AcaoComando,
    ComandoJudicial,
    CriterioJuridico,
)


def criar_criterio_homologado() -> CriterioJuridico:
    comando = ComandoJudicial(
        AcaoComando.DEFERIR,
        "Horas extras",
        "Defiro horas extras excedentes à oitava diária.",
        "SENTENCA-001",
        pagina=12,
    )
    criterio = CriterioJuridico(
        "CRIT-HE-001",
        "HORAS_EXTRAS",
        "Apurar horas excedentes à oitava diária.",
        comando.id,
        base_calculo="SALARIO_CONTRATUAL",
        percentual=Decimal("0.50"),
        divisor=Decimal("220"),
        reflexos=("DSR", "FERIAS_1_3", "DECIMO_TERCEIRO", "FGTS"),
    )
    criterio.homologar(
        "Flávio Gomes",
        datetime(2026, 7, 31, 18, 30, tzinfo=timezone.utc),
    )
    return criterio


def criar_item(criterio: CriterioJuridico, codigo: str = "ITEM-001"):
    return ItemPlanoCalculo(
        codigo=codigo,
        verba_codigo="HORAS_EXTRAS",
        criterio_juridico_id=criterio.id,
        natureza=NaturezaVerba.SALARIAL,
        descricao="Horas extras excedentes à oitava diária",
        periodo_inicio=date(2021, 3, 1),
        periodo_fim=date(2024, 8, 18),
        base_calculo="SALARIO_CONTRATUAL",
        percentual=Decimal("0.50"),
        divisor=Decimal("220"),
        reflexos=("DSR", "FERIAS_1_3", "DECIMO_TERCEIRO", "FGTS"),
        incidencias=("INSS", "IRRF", "FGTS"),
    )


def criar_plano() -> PlanoCalculo:
    return PlanoCalculo(
        processo_id=uuid4(),
        nome="Liquidação inicial",
        data_base=date(2026, 7, 31),
        criado_por="Flávio Gomes",
    )


def test_item_rejeita_periodo_invertido():
    criterio = criar_criterio_homologado()
    with pytest.raises(ValueError):
        ItemPlanoCalculo(
            codigo="ITEM-001",
            verba_codigo="HORAS_EXTRAS",
            criterio_juridico_id=criterio.id,
            natureza=NaturezaVerba.SALARIAL,
            descricao="Período inválido",
            periodo_inicio=date(2024, 8, 18),
            periodo_fim=date(2021, 3, 1),
        )


def test_plano_adiciona_item_com_criterio_homologado():
    criterio = criar_criterio_homologado()
    plano = criar_plano()
    plano.adicionar_item(criar_item(criterio), criterio)

    assert len(plano.itens) == 1
    assert plano.versao == 2


def test_plano_rejeita_criterio_nao_homologado():
    comando = ComandoJudicial(
        AcaoComando.DEFERIR,
        "Horas extras",
        "Defiro horas extras.",
        "SENTENCA-001",
    )
    criterio = CriterioJuridico(
        "CRIT-001",
        "HORAS_EXTRAS",
        "Adicional de 50%",
        comando.id,
        percentual=Decimal("0.50"),
    )
    plano = criar_plano()

    with pytest.raises(ValueError):
        plano.adicionar_item(criar_item(criterio), criterio)


def test_plano_rejeita_item_vinculado_a_outro_criterio():
    criterio = criar_criterio_homologado()
    outro_criterio = criar_criterio_homologado()
    plano = criar_plano()

    with pytest.raises(ValueError):
        plano.adicionar_item(criar_item(criterio), outro_criterio)


def test_plano_rejeita_codigo_de_item_duplicado():
    criterio = criar_criterio_homologado()
    plano = criar_plano()
    plano.adicionar_item(criar_item(criterio), criterio)

    with pytest.raises(ValueError):
        plano.adicionar_item(criar_item(criterio), criterio)


def test_plano_vazio_nao_vai_para_revisao():
    plano = criar_plano()

    with pytest.raises(ValueError):
        plano.enviar_para_revisao()


def test_plano_homologado_gera_hash_e_fica_apto():
    criterio = criar_criterio_homologado()
    plano = criar_plano()
    plano.adicionar_item(criar_item(criterio), criterio)
    plano.enviar_para_revisao()

    momento = datetime(2026, 7, 31, 19, 0, tzinfo=timezone.utc)
    plano.homologar("Flávio Gomes", momento)
    plano.garantir_apto_para_execucao()

    assert plano.status == StatusPlanoCalculo.HOMOLOGADO
    assert plano.hash_homologacao is not None
    assert len(plano.hash_homologacao) == 64
    assert plano.homologado_em == momento


def test_plano_homologado_nao_pode_ser_editado():
    criterio = criar_criterio_homologado()
    plano = criar_plano()
    plano.adicionar_item(criar_item(criterio), criterio)
    plano.enviar_para_revisao()
    plano.homologar("Flávio Gomes")

    with pytest.raises(ValueError):
        plano.remover_item("ITEM-001")
