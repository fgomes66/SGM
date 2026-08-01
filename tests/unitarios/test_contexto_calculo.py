from datetime import datetime, timezone
from uuid import uuid4

import pytest

from sgm.dominio.calculos.contexto import (
    CenarioEstimativo,
    ContextoPlanoCalculo,
    FinalidadeCalculo,
    GrauConfianca,
    PremissaCalculo,
    TipoCenario,
    TipoOrigemPlano,
)


def criar_premissa(codigo: str = "PREM-001") -> PremissaCalculo:
    return PremissaCalculo(
        codigo=codigo,
        descricao="Jornada alegada na petição inicial",
        valor_declarado="08:00 às 20:00, de segunda a sexta",
        grau_confianca=GrauConfianca.MEDIO,
        origem="Entrevista com o cliente",
    )


def test_premissa_exige_valor_declarado():
    with pytest.raises(ValueError):
        PremissaCalculo(
            codigo="PREM-001",
            descricao="Salário alegado",
            valor_declarado=" ",
            grau_confianca=GrauConfianca.BAIXO,
        )


def test_cenario_rejeita_premissa_duplicada():
    cenario = CenarioEstimativo(
        "Cenário provável",
        TipoCenario.PROVAVEL,
    )
    cenario.adicionar_premissa(criar_premissa())

    with pytest.raises(ValueError):
        cenario.adicionar_premissa(criar_premissa())


def test_cenario_sem_premissas_nao_esta_apto():
    cenario = CenarioEstimativo(
        "Cenário conservador",
        TipoCenario.CONSERVADOR,
    )

    with pytest.raises(ValueError):
        cenario.garantir_apto()


def test_estimativa_da_inicial_exige_origem_profissional():
    with pytest.raises(ValueError):
        ContextoPlanoCalculo(
            finalidade=FinalidadeCalculo.ESTIMATIVA_PETICAO_INICIAL,
            tipo_origem=TipoOrigemPlano.TITULO_EXECUTIVO,
            responsavel_tecnico="Flávio Gomes",
        )


def test_liquidacao_exige_titulo_executivo():
    with pytest.raises(ValueError):
        ContextoPlanoCalculo(
            finalidade=FinalidadeCalculo.LIQUIDACAO_SENTENCA,
            tipo_origem=TipoOrigemPlano.TITULO_EXECUTIVO,
            responsavel_tecnico="Flávio Gomes",
        )


def test_contexto_estimativo_revisado_fica_apto():
    cenario = CenarioEstimativo(
        "Cenário provável",
        TipoCenario.PROVAVEL,
    )
    cenario.adicionar_premissa(criar_premissa())

    contexto = ContextoPlanoCalculo(
        finalidade=FinalidadeCalculo.ESTIMATIVA_PETICAO_INICIAL,
        tipo_origem=TipoOrigemPlano.PREMISSA_PROFISSIONAL,
        responsavel_tecnico="Flávio Gomes",
        cenario_estimativo=cenario,
        ressalvas=(
            "Valores sujeitos à prova e ao julgamento.",
        ),
    )
    momento = datetime(2026, 7, 31, 19, 30, tzinfo=timezone.utc)
    contexto.revisar("Advogado responsável", momento)
    contexto.garantir_apto_para_plano()

    assert contexto.natureza_estimativa is True
    assert contexto.revisado_em == momento
    assert contexto.versao == 2


def test_contexto_estimativo_sem_cenario_nao_pode_ser_revisado():
    contexto = ContextoPlanoCalculo(
        finalidade=FinalidadeCalculo.ESTIMATIVA_PETICAO_INICIAL,
        tipo_origem=TipoOrigemPlano.PREMISSA_PROFISSIONAL,
        responsavel_tecnico="Flávio Gomes",
    )

    with pytest.raises(ValueError):
        contexto.revisar("Advogado responsável")


def test_contexto_judicial_revisado_fica_apto():
    contexto = ContextoPlanoCalculo(
        finalidade=FinalidadeCalculo.LIQUIDACAO_SENTENCA,
        tipo_origem=TipoOrigemPlano.TITULO_EXECUTIVO,
        responsavel_tecnico="Flávio Gomes",
        titulo_executivo_id=uuid4(),
    )
    contexto.revisar("Flávio Gomes")
    contexto.garantir_apto_para_plano()

    assert contexto.natureza_estimativa is False
