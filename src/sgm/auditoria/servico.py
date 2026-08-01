from __future__ import annotations
from datetime import datetime
import json
import sqlite3
from typing import Any

def registrar_evento(
    conexao: sqlite3.Connection,
    *,
    evento: str,
    categoria: str,
    versao_sistema: str,
    ambiente: str,
    estacao: str,
    resultado: str,
    usuario_id: int | None = None,
    processo_id: int | None = None,
    entidade: str | None = None,
    entidade_id: int | None = None,
    valor_anterior: Any = None,
    valor_posterior: Any = None,
    detalhes: str | None = None,
) -> None:
    conexao.execute(
        """
        INSERT INTO eventos_auditoria (
            processo_id, usuario_id, evento, categoria,
            entidade, entidade_id, valor_anterior, valor_posterior,
            data_hora, versao_sistema, ambiente, estacao, resultado, detalhes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            processo_id, usuario_id, evento, categoria, entidade, entidade_id,
            json.dumps(valor_anterior, ensure_ascii=False) if valor_anterior is not None else None,
            json.dumps(valor_posterior, ensure_ascii=False) if valor_posterior is not None else None,
            datetime.now().astimezone().isoformat(timespec="seconds"),
            versao_sistema, ambiente, estacao, resultado, detalhes,
        ),
    )
