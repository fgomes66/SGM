from pathlib import Path
import pytest
from sgm.infraestrutura.banco.conexao import conectar
from sgm.infraestrutura.banco.migracoes import aplicar_migracao

def migracao_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "src/sgm/infraestrutura/banco/migrations/0001_estrutura_fundamental.sql"
    )

def test_migracao_cria_tabelas_e_e_idempotente(tmp_path: Path) -> None:
    with conectar(tmp_path / "teste.db") as conexao:
        primeira = aplicar_migracao(
            conexao, migracao_path(), "0001_estrutura_fundamental", "Teste", "0.1.0"
        )
        segunda = aplicar_migracao(
            conexao, migracao_path(), "0001_estrutura_fundamental", "Teste", "0.1.0"
        )
        tabelas = {
            row[0] for row in conexao.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert primeira is True
        assert segunda is False
        assert {"usuarios","clientes","processos","eventos_auditoria","backups"} <= tabelas
        assert conexao.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert conexao.execute("PRAGMA foreign_keys").fetchone()[0] == 1

def test_chave_estrangeira_rejeita_processo_invalido(tmp_path: Path) -> None:
    with conectar(tmp_path / "teste.db") as conexao:
        aplicar_migracao(
            conexao, migracao_path(), "0001_estrutura_fundamental", "Teste", "0.1.0"
        )
        with pytest.raises(Exception):
            conexao.execute(
                """
                INSERT INTO processos (
                    identificador_interno, cliente_id, tribunal, fase_processual,
                    tipo_trabalho, status, data_recebimento, ambiente_origem,
                    criado_em, alterado_em, criado_por_id, alterado_por_id
                ) VALUES (
                    'PROC-TESTE', 999, 'TRT', 'LIQUIDACAO', 'SIMULACAO',
                    'CADASTRADO', '2026-07-31', 'DESENVOLVIMENTO',
                    '2026-07-31T12:00:00-03:00', '2026-07-31T12:00:00-03:00',
                    999, 999
                )
                """
            )
            conexao.commit()
        conexao.rollback()
        assert conexao.execute("SELECT COUNT(*) FROM processos").fetchone()[0] == 0
