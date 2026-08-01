from dataclasses import FrozenInstanceError

import pytest

from sgm.relatorio import (
    DocumentoRenderizado,
    FormatoRenderizacao,
    GeradorRelatorioTecnico,
    RenderizadorHTML,
    RenderizadorMarkdown,
    RenderizadorTexto,
    ServicoRenderizacao,
)
from tests.unitarios.test_modelo_relatorio_tecnico import relatorio


def gerado():
    return GeradorRelatorioTecnico.gerar(relatorio())


def test_01_formatos_e_extensoes():
    assert FormatoRenderizacao.TEXTO.extensao == "txt"
    assert FormatoRenderizacao.MARKDOWN.extensao == "md"
    assert FormatoRenderizacao.HTML.extensao == "html"


def test_02_documento_renderizado_valido():
    item = DocumentoRenderizado(
        FormatoRenderizacao.TEXTO,
        "CASO",
        "Conteúdo",
        "text/plain",
        "0.9.2-E3",
    )
    assert item.referencia == "CASO"


def test_03_documento_rejeita_conteudo_vazio():
    with pytest.raises(ValueError):
        DocumentoRenderizado(
            FormatoRenderizacao.TEXTO,
            "CASO",
            " ",
            "text/plain",
            "0.9.2-E3",
        )


def test_04_texto_preserva_conteudo_do_gerador():
    origem = gerado()
    destino = RenderizadorTexto().renderizar(origem)
    assert destino.conteudo == origem.como_texto()


def test_05_texto_possui_mime_type():
    item = RenderizadorTexto().renderizar(gerado())
    assert item.mime_type == "text/plain; charset=utf-8"


def test_06_markdown_possui_titulo_principal():
    item = RenderizadorMarkdown().renderizar(gerado())
    assert item.conteudo.startswith(
        "# RELATÓRIO TÉCNICO DE CÁLCULOS TRABALHISTAS"
    )


def test_07_markdown_possui_doze_secoes():
    item = RenderizadorMarkdown().renderizar(gerado())
    assert sum(
        1 for linha in item.conteudo.splitlines()
        if linha.startswith("## ")
    ) == 12


def test_08_markdown_preserva_ordem():
    texto = RenderizadorMarkdown().renderizar(gerado()).conteudo
    assert texto.index("## 1. Capa") < texto.index(
        "## 12. Assinatura técnica"
    )


def test_09_html_possui_doctype():
    item = RenderizadorHTML().renderizar(gerado())
    assert item.conteudo.startswith("<!DOCTYPE html>")


def test_10_html_possui_charset_utf8():
    item = RenderizadorHTML().renderizar(gerado())
    assert '<meta charset="utf-8">' in item.conteudo


def test_11_html_possui_doze_secoes():
    item = RenderizadorHTML().renderizar(gerado())
    assert item.conteudo.count("<section ") == 12


def test_12_html_preserva_ordem():
    texto = RenderizadorHTML().renderizar(gerado()).conteudo
    assert texto.index(">1. Capa</h2>") < texto.index(
        ">12. Assinatura técnica</h2>"
    )


def test_13_html_escapa_caracteres():
    texto = RenderizadorHTML().renderizar(gerado()).conteudo
    assert "<strong>Referência:</strong>" in texto
    assert "<script>" not in texto


def test_14_servico_renderiza_texto():
    item = ServicoRenderizacao.renderizar(
        gerado(),
        FormatoRenderizacao.TEXTO,
    )
    assert item.formato == FormatoRenderizacao.TEXTO


def test_15_servico_renderiza_markdown():
    item = ServicoRenderizacao.renderizar(
        gerado(),
        FormatoRenderizacao.MARKDOWN,
    )
    assert item.mime_type.startswith("text/markdown")


def test_16_servico_renderiza_html():
    item = ServicoRenderizacao.renderizar(
        gerado(),
        FormatoRenderizacao.HTML,
    )
    assert item.mime_type.startswith("text/html")


def test_17_servico_rejeita_formato_invalido():
    with pytest.raises(TypeError):
        ServicoRenderizacao.renderizar(gerado(), "HTML")


def test_18_servico_renderiza_todos():
    itens = ServicoRenderizacao.renderizar_todos(gerado())
    assert len(itens) == 3
    assert {item.formato for item in itens} == set(
        FormatoRenderizacao
    )


def test_19_renderizacao_nao_altera_origem():
    origem = gerado()
    antes = origem.como_texto()
    ServicoRenderizacao.renderizar_todos(origem)
    assert origem.como_texto() == antes


def test_20_renderizacao_e_reproduzivel():
    origem = gerado()
    primeiro = ServicoRenderizacao.renderizar_todos(origem)
    segundo = ServicoRenderizacao.renderizar_todos(origem)
    assert tuple(item.conteudo for item in primeiro) == tuple(
        item.conteudo for item in segundo
    )


def test_21_documento_renderizado_e_imutavel():
    item = RenderizadorTexto().renderizar(gerado())
    with pytest.raises(FrozenInstanceError):
        item.conteudo = "Outro"
