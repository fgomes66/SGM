from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape
import zipfile

from sgm.exportacao.documento_exportavel import DocumentoExportavel
from sgm.exportacao.exportadores.base import ExportadorBase


def _coluna(indice: int) -> str:
    resultado = ""
    while indice:
        indice, resto = divmod(indice - 1, 26)
        resultado = chr(65 + resto) + resultado
    return resultado


def _celula_texto(linha: int, coluna: int, valor: str) -> str:
    referencia = f"{_coluna(coluna)}{linha}"
    return (
        f'<c r="{referencia}" t="inlineStr">'
        f"<is><t>{escape(valor)}</t></is></c>"
    )


def _celula_numero(linha: int, coluna: int, valor: str) -> str:
    referencia = f"{_coluna(coluna)}{linha}"
    return f'<c r="{referencia}"><v>{valor}</v></c>'


def _planilha(linhas: list[list[tuple[str, str]]]) -> str:
    xml_linhas = []
    for numero, celulas in enumerate(linhas, start=1):
        conteudo = []
        for coluna, (tipo, valor) in enumerate(celulas, start=1):
            if tipo == "n":
                conteudo.append(
                    _celula_numero(numero, coluna, valor)
                )
            else:
                conteudo.append(
                    _celula_texto(numero, coluna, valor)
                )
        xml_linhas.append(
            f'<row r="{numero}">' + "".join(conteudo) + "</row>"
        )

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/'
        'spreadsheetml/2006/main">'
        "<sheetData>"
        + "".join(xml_linhas)
        + "</sheetData></worksheet>"
    )


class ExportadorXLSX(ExportadorBase):
    def exportar(
        self,
        documento: DocumentoExportavel,
        destino: Path,
        sobrescrever: bool = False,
    ) -> Path:
        destino = self.preparar_destino(destino, sobrescrever)

        resumo = [
            [("s", "Referência"), ("s", documento.referencia)],
            [],
            [
                ("s", "Subtotal geral"),
                (
                    "n",
                    format(
                        documento.demonstrativo.subtotal_geral.valor,
                        "f",
                    ),
                ),
            ],
            [
                ("s", "Valor final geral"),
                (
                    "n",
                    format(
                        documento.demonstrativo.valor_final_geral.valor,
                        "f",
                    ),
                ),
            ],
        ]

        competencias = [
            [
                ("s", "Competência"),
                ("s", "Subtotal"),
                ("s", "Valor final"),
                ("s", "Moeda"),
            ]
        ]
        for item in documento.demonstrativo.competencias:
            competencias.append(
                [
                    ("s", item.competencia.como_texto()),
                    ("n", format(item.subtotal.valor, "f")),
                    ("n", format(item.valor_final.valor, "f")),
                    ("s", item.subtotal.moeda),
                ]
            )

        verbas = [
            [
                ("s", "Código"),
                ("s", "Descrição"),
                ("s", "Natureza"),
                ("s", "Valor"),
                ("s", "Moeda"),
            ]
        ]
        for item in documento.demonstrativo.verbas:
            verbas.append(
                [
                    ("s", item.codigo.value),
                    ("s", item.descricao),
                    ("s", item.natureza.value),
                    ("n", format(item.valor.valor, "f")),
                    ("s", item.valor.moeda),
                ]
            )

        linha_tempo = [
            [
                ("s", "Competência"),
                ("s", "Tipo"),
                ("s", "Título"),
                ("s", "Descrição"),
            ]
        ]
        for item in documento.linha_tempo.marcos:
            linha_tempo.append(
                [
                    ("s", item.competencia.como_texto()),
                    ("s", item.tipo.value),
                    ("s", item.titulo),
                    ("s", item.descricao),
                ]
            )

        folhas = [
            ("Resumo", resumo),
            ("Competências", competencias),
            ("Verbas", verbas),
            ("Linha do Tempo", linha_tempo),
        ]

        workbook_sheets = "".join(
            (
                f'<sheet name="{escape(nome)}" '
                f'sheetId="{indice}" r:id="rId{indice}"/>'
            )
            for indice, (nome, _) in enumerate(folhas, start=1)
        )

        workbook = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/'
            'spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships">'
            f"<sheets>{workbook_sheets}</sheets></workbook>"
        )

        rels_itens = "".join(
            (
                f'<Relationship Id="rId{indice}" '
                'Type="http://schemas.openxmlformats.org/'
                'officeDocument/2006/relationships/worksheet" '
                f'Target="worksheets/sheet{indice}.xml"/>'
            )
            for indice in range(1, len(folhas) + 1)
        )
        workbook_rels = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/'
            'package/2006/relationships">'
            f"{rels_itens}</Relationships>"
        )

        root_rels = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/'
            'package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/officeDocument" '
            'Target="xl/workbook.xml"/>'
            "</Relationships>"
        )

        overrides = "".join(
            (
                f'<Override PartName="/xl/worksheets/sheet{indice}.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.'
                'spreadsheetml.worksheet+xml"/>'
            )
            for indice in range(1, len(folhas) + 1)
        )
        content_types = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/'
            'package/2006/content-types">'
            '<Default Extension="rels" '
            'ContentType="application/vnd.openxmlformats-package.'
            'relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.sheet.main+xml"/>'
            f"{overrides}</Types>"
        )

        with zipfile.ZipFile(
            destino,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as arquivo:
            arquivo.writestr("[Content_Types].xml", content_types)
            arquivo.writestr("_rels/.rels", root_rels)
            arquivo.writestr("xl/workbook.xml", workbook)
            arquivo.writestr(
                "xl/_rels/workbook.xml.rels",
                workbook_rels,
            )
            for indice, (_, linhas) in enumerate(folhas, start=1):
                arquivo.writestr(
                    f"xl/worksheets/sheet{indice}.xml",
                    _planilha(linhas),
                )

        return destino
