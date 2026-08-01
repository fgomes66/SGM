from __future__ import annotations
import sqlite3
from pathlib import Path

def conectar(caminho_banco: Path) -> sqlite3.Connection:
    caminho_banco.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(caminho_banco)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.execute("PRAGMA journal_mode = WAL")
    conexao.execute("PRAGMA synchronous = FULL")
    conexao.execute("PRAGMA busy_timeout = 5000")
    return conexao
