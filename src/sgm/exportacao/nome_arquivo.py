from __future__ import annotations

import re

from sgm.exportacao.formato_exportacao import FormatoExportacao


def normalizar_nome(texto: str) -> str:
    texto = texto.strip()
    texto = re.sub(r"[^A-Za-z0-9._-]+", "_", texto)
    texto = re.sub(r"_+", "_", texto)
    texto = texto.strip("._-")
    if not texto:
        raise ValueError("Não foi possível formar um nome de arquivo.")
    return texto


def montar_nome_arquivo(
    referencia: str,
    formato: FormatoExportacao,
    sufixo: str = "relatorio",
) -> str:
    referencia_normalizada = normalizar_nome(referencia)
    sufixo_normalizado = normalizar_nome(sufixo)
    return (
        f"{referencia_normalizada}_{sufixo_normalizado}."
        f"{formato.extensao}"
    )
