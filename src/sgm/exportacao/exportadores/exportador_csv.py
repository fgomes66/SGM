from __future__ import annotations

import csv
from pathlib import Path

from sgm.exportacao.documento_exportavel import DocumentoExportavel
from sgm.exportacao.exportadores.base import ExportadorBase


class ExportadorCSV(ExportadorBase):
    def exportar(
        self,
        documento: DocumentoExportavel,
        destino: Path,
        sobrescrever: bool = False,
    ) -> Path:
        destino = self.preparar_destino(destino, sobrescrever)

        with destino.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as arquivo:
            escritor = csv.writer(
                arquivo,
                delimiter=";",
                quoting=csv.QUOTE_MINIMAL,
            )
            escritor.writerow(
                (
                    "Competência",
                    "Subtotal",
                    "Valor final",
                    "Moeda",
                    "Referência",
                )
            )

            for item in documento.demonstrativo.competencias:
                escritor.writerow(
                    (
                        item.competencia.como_texto(),
                        format(item.subtotal.valor, "f"),
                        format(item.valor_final.valor, "f"),
                        item.subtotal.moeda,
                        item.referencia,
                    )
                )

            escritor.writerow(())
            escritor.writerow(
                (
                    "Subtotal geral",
                    format(
                        documento.demonstrativo.subtotal_geral.valor,
                        "f",
                    ),
                    documento.demonstrativo.subtotal_geral.moeda,
                )
            )
            escritor.writerow(
                (
                    "Valor final geral",
                    format(
                        documento.demonstrativo.valor_final_geral.valor,
                        "f",
                    ),
                    documento.demonstrativo.valor_final_geral.moeda,
                )
            )

        return destino
