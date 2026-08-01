from dataclasses import FrozenInstanceError
import hashlib
import zipfile

import pytest

from sgm.homologacao import (
    ResultadoHomologacao,
    ServicoHomologacaoFinal,
)
from tests.unitarios.test_caso_temporal_completo import calcular


def homologar(tmp_path):
    return ServicoHomologacaoFinal.homologar(
        calcular(),
        tmp_path,
    )


def test_01_homologacao_retorna_resultado(tmp_path):
    assert isinstance(homologar(tmp_path), ResultadoHomologacao)


def test_02_referencia_e_preservada(tmp_path):
    assert homologar(tmp_path).referencia == "CASO-0013"


def test_03_relatorio_possui_doze_secoes(tmp_path):
    assert len(homologar(tmp_path).relatorio.secoes) == 12


def test_04_total_de_arquivos_e_cinco(tmp_path):
    assert homologar(tmp_path).total_arquivos == 5


def test_05_extensoes_finais(tmp_path):
    item = homologar(tmp_path)
    assert {exp.caminho.suffix for exp in item.exportacoes} == {
        ".txt",
        ".md",
        ".html",
        ".pdf",
        ".docx",
    }


def test_06_todos_os_arquivos_existem(tmp_path):
    item = homologar(tmp_path)
    assert all(exp.caminho.exists() for exp in item.exportacoes)


def test_07_tamanho_total_e_positivo(tmp_path):
    assert homologar(tmp_path).tamanho_total_bytes > 500


def test_08_relatorio_identifica_juizo(tmp_path):
    texto = homologar(tmp_path).relatorio.como_texto()
    assert "7ª Vara do Trabalho do Rio de Janeiro" in texto


def test_09_relatorio_identifica_magistrado(tmp_path):
    texto = homologar(tmp_path).relatorio.como_texto()
    assert "Magistrado(a): Dra. Maria da Silva" in texto


def test_10_relatorio_identifica_perito(tmp_path):
    texto = homologar(tmp_path).relatorio.como_texto()
    assert "Perito(a): João Perito" in texto


def test_11_relatorio_incorpora_memoria(tmp_path):
    texto = homologar(tmp_path).relatorio.como_texto()
    assert "MEMÓRIA DE CÁLCULO PROFISSIONAL — SGM" in texto


def test_12_relatorio_incorpora_demonstrativo(tmp_path):
    texto = homologar(tmp_path).relatorio.como_texto()
    assert "DEMONSTRATIVO FINANCEIRO PROFISSIONAL — SGM" in texto


def test_13_relatorio_incorpora_linha_tempo(tmp_path):
    texto = homologar(tmp_path).relatorio.como_texto()
    assert "LINHA DO TEMPO PROFISSIONAL — SGM" in texto


def test_14_txt_contem_conclusao(tmp_path):
    item = homologar(tmp_path)
    txt = next(
        exp.caminho
        for exp in item.exportacoes
        if exp.caminho.suffix == ".txt"
    )
    assert "Conclusão técnica" in txt.read_text(encoding="utf-8")


def test_15_markdown_contem_doze_secoes(tmp_path):
    item = homologar(tmp_path)
    md = next(
        exp.caminho
        for exp in item.exportacoes
        if exp.caminho.suffix == ".md"
    )
    texto = md.read_text(encoding="utf-8")
    assert sum(
        1 for linha in texto.splitlines()
        if linha.startswith("## ")
    ) == 12


def test_16_html_contem_doze_secoes(tmp_path):
    item = homologar(tmp_path)
    html = next(
        exp.caminho
        for exp in item.exportacoes
        if exp.caminho.suffix == ".html"
    )
    assert html.read_text(
        encoding="utf-8"
    ).count("<section ") == 12


def test_17_pdf_e_valido(tmp_path):
    item = homologar(tmp_path)
    pdf = next(
        exp.caminho
        for exp in item.exportacoes
        if exp.caminho.suffix == ".pdf"
    )
    dados = pdf.read_bytes()
    assert dados.startswith(b"%PDF-1.4")
    assert dados.rstrip().endswith(b"%%EOF")


def test_18_docx_e_valido(tmp_path):
    item = homologar(tmp_path)
    docx = next(
        exp.caminho
        for exp in item.exportacoes
        if exp.caminho.suffix == ".docx"
    )
    assert zipfile.is_zipfile(docx)


def test_19_hash_possui_64_caracteres(tmp_path):
    item = homologar(tmp_path)
    hash_sha256 = item.relatorio.relatorio.metadados.hash_sha256
    assert len(hash_sha256) == 64
    int(hash_sha256, 16)


def test_20_quantidades_sao_consistentes(tmp_path):
    item = homologar(tmp_path)
    metadados = item.relatorio.relatorio.metadados
    demonstrativo = item.relatorio.relatorio.demonstrativo
    assert metadados.quantidade_competencias == len(
        demonstrativo.competencias
    )
    assert metadados.quantidade_verbas == len(
        demonstrativo.verbas
    )


def test_21_eventos_sao_consistentes(tmp_path):
    item = homologar(tmp_path)
    eventos = tuple(
        marco
        for marco in item.relatorio.relatorio.linha_tempo.marcos
        if marco.tipo.value not in (
            "INICIO_PERIODO",
            "FIM_PERIODO",
        )
    )
    assert (
        item.relatorio.relatorio.metadados.quantidade_eventos
        == len(eventos)
    )


def test_22_resultado_e_imutavel(tmp_path):
    item = homologar(tmp_path)
    with pytest.raises(FrozenInstanceError):
        item.referencia = "OUTRA"


def test_23_homologacao_nao_altera_caso(tmp_path):
    resultado = calcular()
    referencia = resultado.plano.referencia
    ServicoHomologacaoFinal.homologar(resultado, tmp_path)
    assert resultado.plano.referencia == referencia


def test_24_homologacao_e_reproduzivel_no_conteudo(tmp_path):
    primeiro = ServicoHomologacaoFinal.homologar(
        calcular(),
        tmp_path / "primeiro",
    )
    segundo = ServicoHomologacaoFinal.homologar(
        calcular(),
        tmp_path / "segundo",
    )

    assert (
        primeiro.relatorio.relatorio.metadados.hash_sha256
        == segundo.relatorio.relatorio.metadados.hash_sha256
    )

    arquivos_1 = {
        exp.caminho.suffix: exp.caminho.read_bytes()
        for exp in primeiro.exportacoes
    }
    arquivos_2 = {
        exp.caminho.suffix: exp.caminho.read_bytes()
        for exp in segundo.exportacoes
    }

    assert arquivos_1[".txt"] == arquivos_2[".txt"]
    assert arquivos_1[".md"] == arquivos_2[".md"]
    assert arquivos_1[".html"] == arquivos_2[".html"]


def test_25_fluxo_completo_preserva_total_financeiro(tmp_path):
    item = homologar(tmp_path)
    demonstrativo = item.relatorio.relatorio.demonstrativo
    texto = item.relatorio.como_texto()
    total = format(
        demonstrativo.valor_final_geral.valor,
        "f",
    )
    assert f"crédito trabalhista apurado totaliza BRL {total}" in texto
