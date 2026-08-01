from datetime import date, datetime, timezone
from decimal import Decimal
import pytest

from sgm.dominio.juridico import (
    AcaoComando,
    ComandoJudicial,
    CriterioJuridico,
    Evidencia,
    Fato,
    Pedido,
    StatusCriterio,
    StatusPedido,
    TipoFato,
)

def test_fato_valido():
    fato = Fato("Jornada das 8h às 20h", TipoFato.JORNADA)
    assert fato.descricao == "Jornada das 8h às 20h"

def test_fato_com_periodo_invertido_e_rejeitado():
    with pytest.raises(ValueError):
        Fato(
            "Período inválido",
            TipoFato.CONTRATUAL,
            data_inicio=date(2025, 2, 1),
            data_fim=date(2025, 1, 31),
        )

def test_evidencia_pode_ser_validada():
    evidencia = Evidencia("DOC-001", "Trecho da sentença", pagina_inicial=3)
    evidencia.validar()
    assert evidencia.validada is True

def test_pedido_altera_status_e_versao():
    pedido = Pedido("PED-001", "Pagamento de horas extras")
    pedido.alterar_status(StatusPedido.DEFERIDO)
    assert pedido.status == StatusPedido.DEFERIDO
    assert pedido.versao == 2

def test_comando_exige_documento():
    with pytest.raises(ValueError):
        ComandoJudicial(
            AcaoComando.DEFERIR,
            "Horas extras",
            "Defiro horas extras",
            "",
        )

def test_criterio_exige_decimal():
    comando = ComandoJudicial(
        AcaoComando.DEFERIR,
        "Horas extras",
        "Defiro horas extras",
        "SENTENCA-001",
    )
    with pytest.raises(TypeError):
        CriterioJuridico(
            "CRIT-001",
            "HORAS_EXTRAS",
            "Adicional de 50%",
            comando.id,
            percentual=0.50,
        )

def test_criterio_nao_homologado_bloqueia_calculo():
    comando = ComandoJudicial(
        AcaoComando.DEFERIR,
        "Horas extras",
        "Defiro horas extras",
        "SENTENCA-001",
    )
    criterio = CriterioJuridico(
        "CRIT-001",
        "HORAS_EXTRAS",
        "Adicional de 50%",
        comando.id,
        percentual=Decimal("0.50"),
    )
    with pytest.raises(ValueError):
        criterio.garantir_apto_para_calculo()

def test_homologacao_libera_criterio_para_calculo():
    comando = ComandoJudicial(
        AcaoComando.DEFERIR,
        "Horas extras",
        "Defiro horas extras",
        "SENTENCA-001",
    )
    criterio = CriterioJuridico(
        "CRIT-001",
        "HORAS_EXTRAS",
        "Adicional de 50%",
        comando.id,
        percentual=Decimal("0.50"),
        divisor=Decimal("220"),
        reflexos=("DSR", "FERIAS_1_3", "DECIMO_TERCEIRO", "FGTS"),
    )
    momento = datetime(2026, 7, 31, 18, 30, tzinfo=timezone.utc)
    criterio.homologar("Flávio Gomes", momento)
    criterio.garantir_apto_para_calculo()

    assert criterio.status == StatusCriterio.HOMOLOGADO
    assert criterio.homologado_por == "Flávio Gomes"
    assert criterio.homologado_em == momento
    assert criterio.versao == 2
