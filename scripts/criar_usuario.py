from getpass import getpass
from pathlib import Path
from datetime import datetime
import json
from sgm import __version__
from sgm.auditoria.servico import registrar_evento
from sgm.infraestrutura.banco.conexao import conectar
from sgm.infraestrutura.seguranca.senhas import gerar_hash_senha

RAIZ = Path(__file__).resolve().parents[1]
CONFIG = json.loads((RAIZ / "config/desenvolvimento.json").read_text(encoding="utf-8"))
BANCO = RAIZ / CONFIG["caminho_banco"]

def main() -> None:
    nome = input("Nome do administrador: ").strip()
    login = input("Login: ").strip()
    senha = getpass("Senha (mínimo 12 caracteres): ")
    confirmar = getpass("Confirme a senha: ")

    if not nome or not login:
        raise ValueError("Nome e login são obrigatórios.")
    if senha != confirmar:
        raise ValueError("As senhas não coincidem.")

    agora = datetime.now().astimezone().isoformat(timespec="seconds")
    with conectar(BANCO) as conexao:
        existente = conexao.execute(
            "SELECT COUNT(*) FROM usuarios WHERE perfil='ADMINISTRADOR' AND excluido_em IS NULL"
        ).fetchone()[0]
        if existente:
            raise RuntimeError("Já existe administrador ativo.")

        cursor = conexao.execute(
            """
            INSERT INTO usuarios (
                nome, login, senha_hash, perfil, ativo,
                criado_em, alterado_em, versao
            ) VALUES (?, ?, ?, 'ADMINISTRADOR', 1, ?, ?, 1)
            """,
            (nome, login, gerar_hash_senha(senha), agora, agora),
        )
        usuario_id = cursor.lastrowid
        registrar_evento(
            conexao,
            evento="USUARIO_ADMINISTRADOR_CRIADO",
            categoria="SEGURANCA",
            versao_sistema=__version__,
            ambiente=CONFIG["ambiente"],
            estacao=CONFIG["estacao"],
            resultado="SUCESSO",
            usuario_id=usuario_id,
            entidade="usuarios",
            entidade_id=usuario_id,
        )
        conexao.commit()

    print("Administrador criado com sucesso.")

if __name__ == "__main__":
    main()
