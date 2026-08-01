from __future__ import annotations
import hashlib
from datetime import datetime
from pathlib import Path
import sqlite3

def _agora_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")

def aplicar_migracao(
    conexao: sqlite3.Connection,
    arquivo_sql: Path,
    codigo: str,
    descricao: str,
    versao_sistema: str,
) -> bool:
    conteudo = arquivo_sql.read_bytes()
    checksum = hashlib.sha256(conteudo).hexdigest()

    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS versoes_banco (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_migracao TEXT NOT NULL UNIQUE,
            descricao TEXT NOT NULL,
            aplicada_em TEXT NOT NULL,
            versao_sistema TEXT NOT NULL,
            checksum TEXT NOT NULL,
            resultado TEXT NOT NULL
        )
        """
    )

    existente = conexao.execute(
        "SELECT checksum FROM versoes_banco WHERE codigo_migracao = ?",
        (codigo,),
    ).fetchone()

    if existente:
        if existente["checksum"] != checksum:
            raise RuntimeError(f"A migração {codigo} já foi aplicada com checksum diferente.")
        return False

    try:
        conexao.executescript(conteudo.decode("utf-8"))
        conexao.execute(
            """
            INSERT INTO versoes_banco (
                codigo_migracao, descricao, aplicada_em,
                versao_sistema, checksum, resultado
            ) VALUES (?, ?, ?, ?, ?, 'APLICADA')
            """,
            (codigo, descricao, _agora_iso(), versao_sistema, checksum),
        )
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise

    return True
