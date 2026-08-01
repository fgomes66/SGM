from dataclasses import FrozenInstanceError, replace

import pytest

from sgm.relatorio import (
    GeradorRelatorioTecnico,
    RelatorioTecnicoGerado,
    SecaoRelatorio,
    TipoSecaoRelatorio,
)
from tests.unitarios.test_modelo_relatorio_tecnico import (
    identificacao,
    relatorio,
)


def gerar():
    return GeradorRelatorioTecnico.gerar(relatorio())


def texto():
    return gerar().como_texto()


def test_01_tipo_secao_estavel():
    assert TipoSecaoRelatorio.CAPA.value == "CAPA"


def test_02_secao_valida():
    secao = SecaoRelatorio(
        ordem=1,
        tipo=TipoSecaoRelatorio.CAPA,
        titulo="Capa",
        linhas=("Linha",),
    )
    assert secao.como_texto() == "1. Capa\nLinha"


def test_03_secao_rejeita_ordem_zero():
    with pytest.raises(ValueError):
        SecaoRelatorio(
            ordem=0,
            tipo=TipoSecaoRelatorio.CAPA,
            titulo="Capa",
            linhas=("Linha",),
        )


def test_04_secao_rejeita_linhas_vazias():
    with pytest.raises(ValueError):
        SecaoRelatorio(
            ordem=1,
            tipo=TipoSecaoRelatorio.CAPA,
            titulo="Capa",
            linhas=(" ",),
        )


def test_05_gerador_retorna_relatorio_gerado():
    assert isinstance(gerar(), RelatorioTecnicoGerado)


def test_06_relatorio_possui_doze_secoes():
    assert len(gerar().secoes) == 12


def test_07_ordem_das_secoes():
    assert tuple(secao.ordem for secao in gerar().secoes) == tuple(
        range(1, 13)
    )


def test_08_tipos_das_secoes():
    assert tuple(secao.tipo for secao in gerar().secoes) == (
        TipoSecaoRelatorio.CAPA,
        TipoSecaoRelatorio.SUMARIO,
        TipoSecaoRelatorio.INTRODUCAO,
        TipoSecaoRelatorio.DADOS_PROCESSUAIS,
        TipoSecaoRelatorio.METODOLOGIA,
        TipoSecaoRelatorio.LINHA_TEMPO,
        TipoSecaoRelatorio.CRITERIOS_JURIDICOS,
        TipoSecaoRelatorio.MEMORIA_CALCULO,
        TipoSecaoRelatorio.DEMONSTRATIVO_FINANCEIRO,
        TipoSecaoRelatorio.ATUALIZACAO_MONETARIA,
        TipoSecaoRelatorio.CONCLUSAO,
        TipoSecaoRelatorio.ASSINATURA_TECNICA,
    )


def test_09_capa_identifica_juizo():
    assert "7ª Vara do Trabalho" in texto()
    assert "JUSTIÇA DO TRABALHO" in texto()


def test_10_capa_identifica_partes():
    assert "Reclamante: Fulano de Tal" in texto()
    assert "Reclamada: Empresa XYZ Ltda." in texto()


def test_11_capa_identifica_magistrado():
    assert "Magistrado(a): Dra. Maria da Silva" in texto()


def test_12_sumario_lista_secoes():
    assert "2. Sumário" in texto()
    assert "12. Assinatura técnica" in texto()


def test_13_introducao_declara_ausencia_de_recalculo():
    assert "não recalcula" in texto()


def test_14_dados_processuais_identificam_uuid():
    item = gerar()
    assert str(item.relatorio.metadados.uuid) in item.como_texto()


def test_15_metodologia_lista_competencias():
    assert "Geração de planos independentes por competência." in texto()


def test_16_metodologia_identifica_moeda():
    assert "Moeda: BRL" in texto()


def test_17_linha_tempo_e_incorporada():
    assert "LINHA DO TEMPO PROFISSIONAL — SGM" in texto()
    assert "2022-03 | EVENTO_CONTRATUAL" in texto()


def test_18_criterios_listam_fgts():
    assert "FGTS conforme alíquota informada no plano." in texto()


def test_19_memoria_e_incorporada():
    assert "MEMÓRIA DE CÁLCULO PROFISSIONAL — SGM" in texto()


def test_20_demonstrativo_e_incorporado():
    assert "DEMONSTRATIVO FINANCEIRO PROFISSIONAL — SGM" in texto()


def test_21_atualizacao_expoe_valor_historico():
    assert "Valor histórico consolidado: BRL" in texto()


def test_22_atualizacao_expoe_valor_final():
    assert "Valor final atualizado: BRL" in texto()


def test_23_conclusao_expoe_total():
    valor = format(
        gerar().relatorio.demonstrativo.valor_final_geral.valor,
        "f",
    )
    assert f"crédito trabalhista apurado totaliza BRL {valor}" in texto()


def test_24_assinatura_expoe_hash():
    assert "SHA-256 informado: " + ("a" * 64) in texto()


def test_25_assinatura_expoe_perito():
    assert "Responsável técnico: João Perito" in texto()


def test_26_perito_ausente_e_tratado():
    item = relatorio()
    identificacao_sem_perito = replace(
        item.identificacao,
        perito=None,
    )
    relatorio_sem_perito = replace(
        item,
        identificacao=identificacao_sem_perito,
    )
    gerado = GeradorRelatorioTecnico.gerar(
        relatorio_sem_perito
    )
    assert "Responsável técnico: não informado." in gerado.como_texto()


def test_27_conteudo_base_hash_nao_e_vazio():
    assert gerar().conteudo_base_hash


def test_28_conteudo_base_hash_preserva_ordem():
    item = gerar()
    assert (
        item.conteudo_base_hash.index("1. Capa")
        < item.conteudo_base_hash.index("12. Assinatura técnica")
    )


def test_29_relatorio_gerado_e_imutavel():
    item = gerar()
    with pytest.raises(FrozenInstanceError):
        item.versao_gerador = "OUTRA"


def test_30_geracao_e_reproduzivel_no_conteudo():
    modelo = relatorio()
    primeiro = GeradorRelatorioTecnico.gerar(modelo)
    segundo = GeradorRelatorioTecnico.gerar(modelo)

    assert primeiro.como_texto() == segundo.como_texto()
    assert (
        primeiro.conteudo_base_hash
        == segundo.conteudo_base_hash
    )
