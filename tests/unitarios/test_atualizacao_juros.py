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
from sgm.dominio.trabalhista import (
    FatorAtualizacao,
    ResultadoAtualizacao,
    ResultadoAtualizacaoJuros,
    ServicoAtualizacao,
    TipoAtualizacao,
)


def valor(texto: str = "1000.00") -> ValorMonetario:
    return ValorMonetario.criar(
        texto,
        OrigemFinanceira(
            descricao="Crédito trabalhista",
            documento_id="MEMORIA-005",
        ),
        momento=datetime(
            2026,
            7,
            31,
            23,
            59,
            tzinfo=timezone.utc,
        ),
    )


def fator(
    tipo=TipoAtualizacao.CORRECAO_MONETARIA,
    numero: str = "1.10",
) -> FatorAtualizacao:
    return FatorAtualizacao(
        tipo=tipo,
        fator=Decimal(numero),
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 12, 31),
        fonte="Tabela fornecida ao plano de cálculo.",
        fundamento="Critério expressamente informado.",
        criterio_juridico_id=uuid4(),
        indice_codigo="INDICE-TESTE",
        versao_fonte="2025.1",
    )


def test_01_tipo_correcao_estavel():
    assert TipoAtualizacao.CORRECAO_MONETARIA.value == "CORRECAO_MONETARIA"


def test_02_tipo_juros_estavel():
    assert TipoAtualizacao.JUROS_MORA.value == "JUROS_MORA"


def test_03_fator_valido():
    item = fator()
    assert item.fator == Decimal("1.10")


def test_04_fator_rejeita_float():
    with pytest.raises(TypeError):
        FatorAtualizacao(
            tipo=TipoAtualizacao.CORRECAO_MONETARIA,
            fator=1.10,
            data_inicial=date(2025, 1, 1),
            data_final=date(2025, 12, 31),
            fonte="Fonte.",
            fundamento="Critério.",
        )


def test_05_fator_rejeita_negativo():
    with pytest.raises(ValueError):
        fator(numero="-0.01")


def test_06_fator_rejeita_periodo_invertido():
    with pytest.raises(ValueError):
        FatorAtualizacao(
            tipo=TipoAtualizacao.CORRECAO_MONETARIA,
            fator=Decimal("1.10"),
            data_inicial=date(2025, 12, 31),
            data_final=date(2025, 1, 1),
            fonte="Fonte.",
            fundamento="Critério.",
        )


def test_07_fator_rejeita_fonte_vazia():
    with pytest.raises(ValueError):
        FatorAtualizacao(
            tipo=TipoAtualizacao.CORRECAO_MONETARIA,
            fator=Decimal("1.10"),
            data_inicial=date(2025, 1, 1),
            data_final=date(2025, 12, 31),
            fonte=" ",
            fundamento="Critério.",
        )


def test_08_fator_rejeita_fundamento_vazio():
    with pytest.raises(ValueError):
        FatorAtualizacao(
            tipo=TipoAtualizacao.CORRECAO_MONETARIA,
            fator=Decimal("1.10"),
            data_inicial=date(2025, 1, 1),
            data_final=date(2025, 12, 31),
            fonte="Fonte.",
            fundamento=" ",
        )


def test_09_fator_e_imutavel():
    item = fator()
    with pytest.raises(FrozenInstanceError):
        item.fator = Decimal("1.20")


def test_10_percentual_equivalente():
    assert fator(numero="1.10").percentual_equivalente == Decimal("10.00")


def test_11_correcao_de_dez_por_cento():
    resultado = ServicoAtualizacao.aplicar(
        valor(),
        fator(numero="1.10"),
    )
    assert resultado.valor_atualizado.valor == Decimal("1100.00")


def test_12_diferenca_da_correcao():
    resultado = ServicoAtualizacao.aplicar(
        valor(),
        fator(numero="1.10"),
    )
    assert resultado.diferenca.valor == Decimal("100.00")


def test_13_juros_de_cinco_por_cento():
    resultado = ServicoAtualizacao.aplicar(
        valor(),
        fator(TipoAtualizacao.JUROS_MORA, "1.05"),
    )
    assert resultado.valor_atualizado.valor == Decimal("1050.00")
    assert resultado.formula_codigo == "FM-JUR-001"


def test_14_correcao_registra_formula():
    resultado = ServicoAtualizacao.aplicar(
        valor(),
        fator(),
    )
    assert resultado.formula_codigo == "FM-COR-001"


def test_15_resultado_e_tipo_correto():
    resultado = ServicoAtualizacao.aplicar(
        valor(),
        fator(),
    )
    assert isinstance(resultado, ResultadoAtualizacao)


def test_16_resultado_preserva_valor_original():
    original = valor()
    resultado = ServicoAtualizacao.aplicar(original, fator())
    assert resultado.valor_original is original


def test_17_resultado_preserva_fator():
    item = fator()
    resultado = ServicoAtualizacao.aplicar(valor(), item)
    assert resultado.fator is item


def test_18_historico_registra_multiplicacao():
    resultado = ServicoAtualizacao.aplicar(valor(), fator())
    tipos = [item.tipo for item in resultado.valor_atualizado.historico]
    assert TipoOperacaoFinanceira.MULTIPLICACAO in tipos


def test_19_historico_atualizado_termina_com_arredondamento():
    resultado = ServicoAtualizacao.aplicar(valor(), fator())
    assert (
        resultado.valor_atualizado.historico[-1].tipo
        == TipoOperacaoFinanceira.ARREDONDAMENTO
    )


def test_20_diferenca_registra_subtracao():
    resultado = ServicoAtualizacao.aplicar(valor(), fator())
    tipos = [item.tipo for item in resultado.diferenca.historico]
    assert TipoOperacaoFinanceira.SUBTRACAO in tipos


def test_21_aplica_correcao_e_juros_em_sequencia():
    resultado = ServicoAtualizacao.aplicar_correcao_e_juros(
        valor(),
        fator(TipoAtualizacao.CORRECAO_MONETARIA, "1.10"),
        fator(TipoAtualizacao.JUROS_MORA, "1.05"),
    )
    assert resultado.correcao.valor_atualizado.valor == Decimal("1100.00")
    assert resultado.juros.valor_atualizado.valor == Decimal("1155.00")
    assert resultado.valor_final.valor == Decimal("1155.00")


def test_22_consolidado_e_tipo_correto():
    resultado = ServicoAtualizacao.aplicar_correcao_e_juros(
        valor(),
        fator(TipoAtualizacao.CORRECAO_MONETARIA, "1.10"),
        fator(TipoAtualizacao.JUROS_MORA, "1.05"),
    )
    assert isinstance(resultado, ResultadoAtualizacaoJuros)


def test_23_consolidado_rejeita_primeiro_fator_de_juros():
    with pytest.raises(ValueError):
        ServicoAtualizacao.aplicar_correcao_e_juros(
            valor(),
            fator(TipoAtualizacao.JUROS_MORA, "1.10"),
            fator(TipoAtualizacao.JUROS_MORA, "1.05"),
        )


def test_24_consolidado_rejeita_segundo_fator_de_correcao():
    with pytest.raises(ValueError):
        ServicoAtualizacao.aplicar_correcao_e_juros(
            valor(),
            fator(TipoAtualizacao.CORRECAO_MONETARIA, "1.10"),
            fator(TipoAtualizacao.CORRECAO_MONETARIA, "1.05"),
        )


def test_25_consolidado_registra_formula():
    resultado = ServicoAtualizacao.aplicar_correcao_e_juros(
        valor(),
        fator(TipoAtualizacao.CORRECAO_MONETARIA, "1.10"),
        fator(TipoAtualizacao.JUROS_MORA, "1.05"),
    )
    assert resultado.formula_codigo == "FM-AJ-001"


def test_26_memoria_expoe_periodo_e_fonte():
    resultado = ServicoAtualizacao.aplicar(valor(), fator())
    memoria = "\n".join(resultado.memoria_resumida())
    assert "2025-01-01 a 2025-12-31" in memoria
    assert "Tabela fornecida ao plano de cálculo." in memoria


def test_27_memoria_expoe_valores():
    resultado = ServicoAtualizacao.aplicar(valor(), fator())
    memoria = "\n".join(resultado.memoria_resumida())
    assert "Valor original: BRL 1000.00" in memoria
    assert "Valor atualizado: BRL 1100.00" in memoria
    assert "Diferença: BRL 100.00" in memoria


def test_28_memoria_consolidada_separa_etapas():
    resultado = ServicoAtualizacao.aplicar_correcao_e_juros(
        valor(),
        fator(TipoAtualizacao.CORRECAO_MONETARIA, "1.10"),
        fator(TipoAtualizacao.JUROS_MORA, "1.05"),
    )
    memoria = "\n".join(resultado.memoria_resumida())
    assert "ETAPA 1 — CORREÇÃO MONETÁRIA" in memoria
    assert "ETAPA 2 — JUROS" in memoria
    assert "VALOR FINAL: BRL 1155.00" in memoria


def test_29_fator_unitario_nao_altera_valor():
    resultado = ServicoAtualizacao.aplicar(
        valor(),
        fator(numero="1"),
    )
    assert resultado.valor_atualizado.valor == Decimal("1000.00")
    assert resultado.diferenca.valor == Decimal("0.00")


def test_30_resultado_consolidado_e_imutavel():
    resultado = ServicoAtualizacao.aplicar_correcao_e_juros(
        valor(),
        fator(TipoAtualizacao.CORRECAO_MONETARIA, "1.10"),
        fator(TipoAtualizacao.JUROS_MORA, "1.05"),
    )
    with pytest.raises(FrozenInstanceError):
        resultado.valor_final = valor("0")
