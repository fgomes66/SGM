from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista import (
    GeradorMemoriaProfissional,
    ItemMemoria,
    LinhaTabelaFinanceira,
    MemoriaCalculoProfissional,
    NivelObservacaoTecnica,
    ObservacaoTecnica,
    SecaoMemoria,
    TabelaFinanceira,
    TipoSecaoMemoria,
)
from tests.unitarios.test_caso_temporal_completo import calcular


def moeda(texto: str) -> ValorMonetario:
    resultado = calcular()
    modelo = resultado.consolidado.valor_final_consolidado
    return ValorMonetario.criar(
        texto,
        modelo.origem,
        moeda=modelo.moeda,
    )


def test_01_tipo_secao_estavel():
    assert TipoSecaoMemoria.CONSOLIDACAO.value == "CONSOLIDACAO"


def test_02_item_valido():
    item = ItemMemoria("Salário", "BRL 3000.00")
    assert item.rotulo == "Salário"


def test_03_item_rejeita_rotulo_vazio():
    with pytest.raises(ValueError):
        ItemMemoria(" ", "Valor")


def test_04_item_rejeita_valor_vazio():
    with pytest.raises(ValueError):
        ItemMemoria("Rótulo", " ")


def test_05_item_normaliza_formula():
    item = ItemMemoria(
        "Horas extras",
        "BRL 100.00",
        formula_codigo=" fm-he-001 ",
    )
    assert item.formula_codigo == "FM-HE-001"


def test_06_linha_financeira_valida():
    linha = LinhaTabelaFinanceira(
        "2022-01",
        "Resultado mensal",
        moeda("100.00"),
    )
    assert linha.chave == "2022-01"


def test_07_linha_rejeita_descricao_vazia():
    with pytest.raises(ValueError):
        LinhaTabelaFinanceira(
            "2022-01",
            " ",
            moeda("100.00"),
        )


def test_08_tabela_valida_total():
    tabela = TabelaFinanceira(
        "Resultados",
        ("Competência", "Valor"),
        (
            LinhaTabelaFinanceira(
                "2022-01", "Janeiro", moeda("100.00")
            ),
            LinhaTabelaFinanceira(
                "2022-02", "Fevereiro", moeda("200.00")
            ),
        ),
        moeda("300.00"),
    )
    assert tabela.total.valor == Decimal("300.00")


def test_09_tabela_rejeita_total_incorreto():
    with pytest.raises(ValueError):
        TabelaFinanceira(
            "Resultados",
            ("Competência", "Valor"),
            (
                LinhaTabelaFinanceira(
                    "2022-01", "Janeiro", moeda("100.00")
                ),
            ),
            moeda("99.00"),
        )


def test_10_observacao_valida():
    item = ObservacaoTecnica(
        "Nota técnica.",
        NivelObservacaoTecnica.INFORMATIVA,
    )
    assert item.texto == "Nota técnica."


def test_11_observacao_rejeita_texto_vazio():
    with pytest.raises(ValueError):
        ObservacaoTecnica(
            " ",
            NivelObservacaoTecnica.ATENCAO,
        )


def test_12_secao_exige_conteudo():
    with pytest.raises(ValueError):
        SecaoMemoria(
            1,
            TipoSecaoMemoria.IDENTIFICACAO,
            "Identificação",
        )


def test_13_secao_rejeita_ordem_zero():
    with pytest.raises(ValueError):
        SecaoMemoria(
            0,
            TipoSecaoMemoria.IDENTIFICACAO,
            "Identificação",
            itens=(ItemMemoria("A", "B"),),
        )


def test_14_gerador_retorna_memoria_profissional():
    memoria = GeradorMemoriaProfissional.gerar(calcular())
    assert isinstance(memoria, MemoriaCalculoProfissional)


def test_15_memoria_possui_quatro_secoes():
    memoria = GeradorMemoriaProfissional.gerar(calcular())
    assert len(memoria.secoes) == 4


def test_16_memoria_ordena_secoes():
    memoria = GeradorMemoriaProfissional.gerar(calcular())
    assert tuple(secao.ordem for secao in memoria.secoes) == (
        1, 2, 3, 4
    )


def test_17_memoria_identifica_referencia():
    memoria = GeradorMemoriaProfissional.gerar(calcular())
    assert memoria.referencia == "CASO-0013"


def test_18_memoria_lista_linha_do_tempo():
    texto = GeradorMemoriaProfissional.gerar(
        calcular()
    ).como_texto()
    assert "2. Linha do tempo contratual" in texto
    assert "2022-03:" in texto
    assert "salário=3300.00" in texto


def test_19_memoria_lista_competencias_calculadas():
    texto = GeradorMemoriaProfissional.gerar(
        calcular()
    ).como_texto()
    assert "Tabela: Resultados mensais" in texto
    assert "2022-01 | Valor final da competência" in texto
    assert "2022-07 | Valor final da competência" in texto


def test_20_memoria_expoe_total_consolidado():
    resultado = calcular()
    texto = GeradorMemoriaProfissional.gerar(
        resultado
    ).como_texto()
    esperado = (
        f"{resultado.consolidado.valor_final_consolidado.moeda} "
        f"{format(resultado.consolidado.valor_final_consolidado.valor, 'f')}"
    )
    assert f"Valor final consolidado: {esperado}" in texto


def test_21_memoria_registra_limitacao_exportacao():
    texto = GeradorMemoriaProfissional.gerar(
        calcular()
    ).como_texto()
    assert "[LIMITACAO]" in texto
    assert "ainda não gera arquivos PDF" in texto


def test_22_memoria_rejeita_ordens_duplicadas():
    secao = SecaoMemoria(
        1,
        TipoSecaoMemoria.IDENTIFICACAO,
        "Identificação",
        itens=(ItemMemoria("A", "B"),),
    )
    with pytest.raises(ValueError):
        MemoriaCalculoProfissional(
            "Memória",
            "CASO",
            (secao, secao),
            (),
        )


def test_23_memoria_e_imutavel():
    memoria = GeradorMemoriaProfissional.gerar(calcular())
    with pytest.raises(FrozenInstanceError):
        memoria.titulo = "Outro"


def test_24_geracao_e_reproduzivel():
    primeiro = GeradorMemoriaProfissional.gerar(
        calcular()
    )
    segundo = GeradorMemoriaProfissional.gerar(
        calcular()
    )
    assert primeiro.como_texto() == segundo.como_texto()
