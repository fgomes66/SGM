from pathlib import Path
import json
from sgm import __version__
from sgm.infraestrutura.banco.conexao import conectar
from sgm.infraestrutura.banco.migracoes import aplicar_migracao

RAIZ = Path(__file__).resolve().parents[1]
CONFIG = json.loads((RAIZ / "config/desenvolvimento.json").read_text(encoding="utf-8"))
BANCO = RAIZ / CONFIG["caminho_banco"]
MIGRACAO = RAIZ / "src/sgm/infraestrutura/banco/migrations/0001_estrutura_fundamental.sql"

def main() -> None:
    with conectar(BANCO) as conexao:
        aplicada = aplicar_migracao(
            conexao, MIGRACAO, "0001_estrutura_fundamental",
            "Usuários, clientes, processos, auditoria e backups.", __version__
        )
        integridade = conexao.execute("PRAGMA integrity_check").fetchone()[0]
        fk = conexao.execute("PRAGMA foreign_keys").fetchone()[0]
    print(f"Banco: {BANCO}")
    print(f"Migração aplicada agora: {'SIM' if aplicada else 'NÃO, já existente'}")
    print(f"Integridade: {integridade}")
    print(f"Chaves estrangeiras ativas: {'SIM' if fk == 1 else 'NÃO'}")

if __name__ == "__main__":
    main()
