from pathlib import Path
import csv
import zipfile
import xml.etree.ElementTree as ET

import pytest

from sgm.dominio.trabalhista import (
    GeradorDemonstrativoFinanceiro,
    GeradorLinhaTempoProfissional,
    GeradorMemoriaProfissional,
)
from sgm.exportacao import (
    DocumentoExportavel,
    ExportadorCSV,
    ExportadorDOCX,
    ExportadorPDF,
    ExportadorXLSX,
    FormatoExportacao,
    ServicoExportacao,
    montar_nome_arquivo,
    normalizar_nome,
)
from tests.unitarios.test_caso_temporal_completo import calcular


def documento():
    resultado = calcular()
    return DocumentoExportavel(
        referencia=resultado.plano.referencia,
        memoria=GeradorMemoriaProfissional.gerar(resultado),
        demonstrativo=GeradorDemonstrativoFinanceiro.gerar(
            resultado
        ),
        linha_tempo=GeradorLinhaTempoProfissional.gerar(
            resultado
        ),
    )


def test_01_formatos_e_extensoes():
    assert FormatoExportacao.PDF.extensao == "pdf"
    assert FormatoExportacao.DOCX.extensao == "docx"
    assert FormatoExportacao.XLSX.extensao == "xlsx"
    assert FormatoExportacao.CSV.extensao == "csv"


def test_02_normaliza_nome():
    assert normalizar_nome(" CASO 0013 / relatório ") == (
        "CASO_0013_relat_rio"
    )


def test_03_monta_nome_arquivo():
    assert montar_nome_arquivo(
        "CASO-0013",
        FormatoExportacao.PDF,
        "memoria",
    ) == "CASO-0013_memoria.pdf"


def test_04_documento_exige_referencias_iguais():
    item = documento()
    memoria = item.memoria
    object.__setattr__(memoria, "referencia", "OUTRA")
    with pytest.raises(ValueError):
        DocumentoExportavel(
            referencia="CASO-0013",
            memoria=memoria,
            demonstrativo=item.demonstrativo,
            linha_tempo=item.linha_tempo,
        )


def test_05_pdf_cria_arquivo(tmp_path):
    destino = tmp_path / "relatorio.pdf"
    resultado = ExportadorPDF().exportar(
        documento(),
        destino,
    )
    assert resultado == destino
    assert destino.exists()


def test_06_pdf_possui_assinatura_e_eof(tmp_path):
    destino = tmp_path / "relatorio.pdf"
    ExportadorPDF().exportar(documento(), destino)
    dados = destino.read_bytes()
    assert dados.startswith(b"%PDF-1.4")
    assert dados.rstrip().endswith(b"%%EOF")


def test_07_pdf_contem_referencia(tmp_path):
    destino = tmp_path / "relatorio.pdf"
    ExportadorPDF().exportar(documento(), destino)
    assert b"CASO-0013" in destino.read_bytes()


def test_08_pdf_rejeita_sobrescrita(tmp_path):
    destino = tmp_path / "relatorio.pdf"
    ExportadorPDF().exportar(documento(), destino)
    with pytest.raises(FileExistsError):
        ExportadorPDF().exportar(documento(), destino)


def test_09_docx_cria_pacote_valido(tmp_path):
    destino = tmp_path / "relatorio.docx"
    ExportadorDOCX().exportar(documento(), destino)
    assert zipfile.is_zipfile(destino)
    with zipfile.ZipFile(destino) as arquivo:
        assert "word/document.xml" in arquivo.namelist()


def test_10_docx_contem_titulo_e_referencia(tmp_path):
    destino = tmp_path / "relatorio.docx"
    ExportadorDOCX().exportar(documento(), destino)
    with zipfile.ZipFile(destino) as arquivo:
        xml = arquivo.read("word/document.xml").decode("utf-8")
    assert "MEMÓRIA DE CÁLCULO PROFISSIONAL" in xml
    assert "CASO-0013" in xml


def test_11_docx_xml_e_valido(tmp_path):
    destino = tmp_path / "relatorio.docx"
    ExportadorDOCX().exportar(documento(), destino)
    with zipfile.ZipFile(destino) as arquivo:
        ET.fromstring(arquivo.read("word/document.xml"))


def test_12_docx_permite_sobrescrever(tmp_path):
    destino = tmp_path / "relatorio.docx"
    exportador = ExportadorDOCX()
    exportador.exportar(documento(), destino)
    exportador.exportar(
        documento(),
        destino,
        sobrescrever=True,
    )
    assert destino.exists()


def test_13_xlsx_cria_pacote_valido(tmp_path):
    destino = tmp_path / "relatorio.xlsx"
    ExportadorXLSX().exportar(documento(), destino)
    assert zipfile.is_zipfile(destino)
    with zipfile.ZipFile(destino) as arquivo:
        assert "xl/workbook.xml" in arquivo.namelist()


def test_14_xlsx_possui_quatro_planilhas(tmp_path):
    destino = tmp_path / "relatorio.xlsx"
    ExportadorXLSX().exportar(documento(), destino)
    with zipfile.ZipFile(destino) as arquivo:
        xml = arquivo.read("xl/workbook.xml").decode("utf-8")
    assert 'name="Resumo"' in xml
    assert 'name="Competências"' in xml
    assert 'name="Verbas"' in xml
    assert 'name="Linha do Tempo"' in xml


def test_15_xlsx_contem_totais(tmp_path):
    destino = tmp_path / "relatorio.xlsx"
    item = documento()
    ExportadorXLSX().exportar(item, destino)
    with zipfile.ZipFile(destino) as arquivo:
        xml = arquivo.read(
            "xl/worksheets/sheet1.xml"
        ).decode("utf-8")
    assert "Subtotal geral" in xml
    assert format(
        item.demonstrativo.valor_final_geral.valor,
        "f",
    ) in xml


def test_16_xlsx_xml_principal_e_valido(tmp_path):
    destino = tmp_path / "relatorio.xlsx"
    ExportadorXLSX().exportar(documento(), destino)
    with zipfile.ZipFile(destino) as arquivo:
        ET.fromstring(arquivo.read("xl/workbook.xml"))


def test_17_csv_cria_utf8_com_bom(tmp_path):
    destino = tmp_path / "relatorio.csv"
    ExportadorCSV().exportar(documento(), destino)
    assert destino.read_bytes().startswith(b"\xef\xbb\xbf")


def test_18_csv_usa_ponto_e_virgula(tmp_path):
    destino = tmp_path / "relatorio.csv"
    ExportadorCSV().exportar(documento(), destino)
    primeira = destino.read_text(
        encoding="utf-8-sig"
    ).splitlines()[0]
    assert primeira == (
        "Competência;Subtotal;Valor final;Moeda;Referência"
    )


def test_19_csv_possui_seis_competencias(tmp_path):
    destino = tmp_path / "relatorio.csv"
    ExportadorCSV().exportar(documento(), destino)
    with destino.open(
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:
        linhas = list(csv.reader(arquivo, delimiter=";"))
    competencias = [
        linha[0]
        for linha in linhas
        if linha and linha[0].startswith("2022-")
    ]
    assert len(competencias) == 6


def test_20_csv_contem_totais(tmp_path):
    destino = tmp_path / "relatorio.csv"
    ExportadorCSV().exportar(documento(), destino)
    texto = destino.read_text(encoding="utf-8-sig")
    assert "Subtotal geral" in texto
    assert "Valor final geral" in texto


def test_21_servico_cria_diretorio_e_nome(tmp_path):
    pasta = tmp_path / "saida" / "laudos"
    caminho = ServicoExportacao.exportar(
        documento(),
        FormatoExportacao.PDF,
        pasta,
        sufixo="memoria",
    )
    assert pasta.exists()
    assert caminho.name == "CASO-0013_memoria.pdf"


def test_22_servico_rejeita_formato_invalido(tmp_path):
    with pytest.raises(TypeError):
        ServicoExportacao.exportar(
            documento(),
            "PDF",
            tmp_path,
        )


def test_23_servico_seleciona_csv(tmp_path):
    caminho = ServicoExportacao.exportar(
        documento(),
        FormatoExportacao.CSV,
        tmp_path,
    )
    assert caminho.suffix == ".csv"
    assert caminho.exists()


def test_24_servico_exporta_todos(tmp_path):
    caminhos = ServicoExportacao.exportar_todos(
        documento(),
        tmp_path,
    )
    assert len(caminhos) == 4
    assert {caminho.suffix for caminho in caminhos} == {
        ".pdf", ".docx", ".xlsx", ".csv"
    }


def test_25_servico_rejeita_arquivos_existentes(tmp_path):
    ServicoExportacao.exportar_todos(
        documento(),
        tmp_path,
    )
    with pytest.raises(FileExistsError):
        ServicoExportacao.exportar_todos(
            documento(),
            tmp_path,
        )


def test_26_servico_sobrescreve_todos(tmp_path):
    ServicoExportacao.exportar_todos(
        documento(),
        tmp_path,
    )
    caminhos = ServicoExportacao.exportar_todos(
        documento(),
        tmp_path,
        sobrescrever=True,
    )
    assert all(caminho.exists() for caminho in caminhos)


def test_27_conteudo_integral_contem_tres_documentos():
    texto = documento().texto_integral()
    assert "MEMÓRIA DE CÁLCULO PROFISSIONAL" in texto
    assert "DEMONSTRATIVO FINANCEIRO PROFISSIONAL" in texto
    assert "LINHA DO TEMPO PROFISSIONAL" in texto


def test_28_exportacao_nao_altera_documento(tmp_path):
    item = documento()
    antes = item.texto_integral()
    ServicoExportacao.exportar_todos(item, tmp_path)
    depois = item.texto_integral()
    assert antes == depois


def test_29_arquivos_exportados_nao_estao_vazios(tmp_path):
    caminhos = ServicoExportacao.exportar_todos(
        documento(),
        tmp_path,
    )
    assert all(
        caminho.stat().st_size > 100
        for caminho in caminhos
    )


def test_30_exportacao_e_reproduzivel(tmp_path):
    primeira = tmp_path / "primeira"
    segunda = tmp_path / "segunda"
    caminhos_1 = ServicoExportacao.exportar_todos(
        documento(),
        primeira,
    )
    caminhos_2 = ServicoExportacao.exportar_todos(
        documento(),
        segunda,
    )
    por_extensao_1 = {
        caminho.suffix: caminho.read_bytes()
        for caminho in caminhos_1
    }
    por_extensao_2 = {
        caminho.suffix: caminho.read_bytes()
        for caminho in caminhos_2
    }
    assert por_extensao_1 == por_extensao_2
