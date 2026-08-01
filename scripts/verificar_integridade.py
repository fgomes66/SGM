from pathlib import Path
import json
from sgm.infraestrutura.banco.conexao import conectar

RAIZ = Path(__file__).resolve().parents[1]
CONFIG = json.loads((RAIZ / "config/desenvolvimento.json").read_text(encoding="utf-8"))
BANCO = RAIZ / CONFIG["caminho_banco"]

def main() -> None:
    if not BANCO.exists():
        raise FileNotFoundError(f"Banco não encontrado: {BANCO}")
    with conectar(BANCO) as conexao:
        integridade = conexao.execute("PRAGMA integrity_check").fetchone()[0]
        erros_fk = conexao.execute("PRAGMA foreign_key_check").fetchall()
        migracoes = conexao.execute(
            "SELECT codigo_migracao, aplicada_em, resultado FROM versoes_banco ORDER BY id"
        ).fetchall()
    print(f"Integridade: {integridade}")
    print(f"Erros de chave estrangeira: {len(erros_fk)}")
    for migracao in migracoes:
        print(dict(migracao))
    if integridade != "ok" or erros_fk:
        raise RuntimeError("Falha de integridade detectada.")

if __name__ == "__main__":
    main()
