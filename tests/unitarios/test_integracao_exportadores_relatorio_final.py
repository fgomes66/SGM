from dataclasses import FrozenInstanceError
import zipfile

import pytest

from sgm.relatorio import (
    AdaptadorRelatorioExportavel,
    FormatoRelatorioFinal,
    GeradorRelatorioTecnico,
    ResultadoExportacaoRelatorio,
    ServicoExportacaoRelatorioFinal,
)
from tests.unitarios.test_modelo_relatorio_tecnico import relatorio


def gerado():
    return GeradorRelatorioTecnico.gerar(relatorio())


def test_01_formatos_e_extensoes():
    assert FormatoRelatorioFinal.TXT.extensao == "txt"
    assert FormatoRelatorioFinal.MARKDOWN.extensao == "md"
    assert FormatoRelatorioFinal.HTML.extensao == "html"
    assert FormatoRelatorioFinal.PDF.extensao == "pdf"
    assert FormatoRelatorioFinal.DOCX.extensao == "docx"


def test_02_adaptador_preserva_referencia():
    item = gerado()
    adaptador = AdaptadorRelatorioExportavel(
        item,
        item.como_texto(),
    )
    assert adaptador.referencia == "CASO-0013"


def test_03_adaptador_preserva_texto():
    item = gerado()
    adaptador = AdaptadorRelatorioExportavel(
        item,
        item.como_texto(),
    )
    assert adaptador.texto_integral() == item.como_texto()


def test_04_adaptador_rejeita_conteudo_vazio():
    with pytest.raises(ValueError):
        AdaptadorRelatorioExportavel(gerado(), " ")


def test_05_exporta_txt(tmp_path):
    resultado = ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.TXT,
        tmp_path,
    )
    assert resultado.caminho.suffix == ".txt"
    assert resultado.caminho.exists()


def test_06_txt_contem_titulo(tmp_path):
    resultado = ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.TXT,
        tmp_path,
    )
    texto = resultado.caminho.read_text(encoding="utf-8")
    assert "RELATÓRIO TÉCNICO DE CÁLCULOS TRABALHISTAS" in texto


def test_07_exporta_markdown(tmp_path):
    resultado = ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.MARKDOWN,
        tmp_path,
    )
    texto = resultado.caminho.read_text(encoding="utf-8")
    assert texto.startswith(
        "# RELATÓRIO TÉCNICO DE CÁLCULOS TRABALHISTAS"
    )


def test_08_exporta_html(tmp_path):
    resultado = ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.HTML,
        tmp_path,
    )
    texto = resultado.caminho.read_text(encoding="utf-8")
    assert texto.startswith("<!DOCTYPE html>")
    assert texto.count("<section ") == 12


def test_09_exporta_pdf_valido(tmp_path):
    resultado = ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.PDF,
        tmp_path,
    )
    dados = resultado.caminho.read_bytes()
    assert dados.startswith(b"%PDF-1.4")
    assert dados.rstrip().endswith(b"%%EOF")


def test_10_pdf_contem_referencia(tmp_path):
    resultado = ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.PDF,
        tmp_path,
    )
    assert b"CASO-0013" in resultado.caminho.read_bytes()


def test_11_exporta_docx_valido(tmp_path):
    resultado = ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.DOCX,
        tmp_path,
    )
    assert zipfile.is_zipfile(resultado.caminho)
    with zipfile.ZipFile(resultado.caminho) as arquivo:
        assert "word/document.xml" in arquivo.namelist()


def test_12_docx_contem_titulo(tmp_path):
    resultado = ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.DOCX,
        tmp_path,
    )
    with zipfile.ZipFile(resultado.caminho) as arquivo:
        xml = arquivo.read("word/document.xml").decode("utf-8")
    assert "RELATÓRIO TÉCNICO DE CÁLCULOS TRABALHISTAS" in xml


def test_13_nome_automatico(tmp_path):
    resultado = ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.PDF,
        tmp_path,
    )
    assert resultado.caminho.name == (
        "CASO-0013_relatorio_tecnico.pdf"
    )


def test_14_sufixo_personalizado(tmp_path):
    resultado = ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.HTML,
        tmp_path,
        sufixo="laudo final",
    )
    assert resultado.caminho.name == "CASO-0013_laudo_final.html"


def test_15_cria_diretorio(tmp_path):
    pasta = tmp_path / "saida" / "relatorios"
    ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.TXT,
        pasta,
    )
    assert pasta.exists()


def test_16_rejeita_sobrescrita(tmp_path):
    ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.TXT,
        tmp_path,
    )
    with pytest.raises(FileExistsError):
        ServicoExportacaoRelatorioFinal.exportar(
            gerado(),
            FormatoRelatorioFinal.TXT,
            tmp_path,
        )


def test_17_permite_sobrescrita(tmp_path):
    ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.TXT,
        tmp_path,
    )
    resultado = ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.TXT,
        tmp_path,
        sobrescrever=True,
    )
    assert resultado.caminho.exists()


def test_18_rejeita_formato_invalido(tmp_path):
    with pytest.raises(TypeError):
        ServicoExportacaoRelatorioFinal.exportar(
            gerado(),
            "PDF",
            tmp_path,
        )


def test_19_exporta_todos(tmp_path):
    resultados = ServicoExportacaoRelatorioFinal.exportar_todos(
        gerado(),
        tmp_path,
    )
    assert len(resultados) == 5
    assert {
        item.caminho.suffix for item in resultados
    } == {".txt", ".md", ".html", ".pdf", ".docx"}


def test_20_todos_arquivos_nao_vazios(tmp_path):
    resultados = ServicoExportacaoRelatorioFinal.exportar_todos(
        gerado(),
        tmp_path,
    )
    assert all(item.tamanho_bytes > 100 for item in resultados)


def test_21_resultado_confere_tamanho(tmp_path):
    resultado = ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.HTML,
        tmp_path,
    )
    assert resultado.tamanho_bytes == (
        resultado.caminho.stat().st_size
    )


def test_22_resultado_e_imutavel(tmp_path):
    resultado = ServicoExportacaoRelatorioFinal.exportar(
        gerado(),
        FormatoRelatorioFinal.TXT,
        tmp_path,
    )
    with pytest.raises(FrozenInstanceError):
        resultado.tamanho_bytes = 0


def test_23_exportacao_nao_altera_relatorio(tmp_path):
    origem = gerado()
    antes = origem.como_texto()
    ServicoExportacaoRelatorioFinal.exportar_todos(
        origem,
        tmp_path,
    )
    assert origem.como_texto() == antes


def test_24_exportacao_e_reproduzivel(tmp_path):
    origem = gerado()
    primeira = ServicoExportacaoRelatorioFinal.exportar_todos(
        origem,
        tmp_path / "primeira",
    )
    segunda = ServicoExportacaoRelatorioFinal.exportar_todos(
        origem,
        tmp_path / "segunda",
    )
    conteudos_1 = {
        item.formato: item.caminho.read_bytes()
        for item in primeira
    }
    conteudos_2 = {
        item.formato: item.caminho.read_bytes()
        for item in segunda
    }
    assert conteudos_1 == conteudos_2
