from __future__ import annotations
import base64
import hashlib
import hmac
import os

_ITERACOES = 600_000

def gerar_hash_senha(senha: str) -> str:
    if len(senha) < 12:
        raise ValueError("A senha deve possuir pelo menos 12 caracteres.")
    salt = os.urandom(16)
    derivada = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, _ITERACOES)
    return "$".join([
        "pbkdf2_sha256",
        str(_ITERACOES),
        base64.b64encode(salt).decode(),
        base64.b64encode(derivada).decode(),
    ])

def verificar_senha(senha: str, armazenado: str) -> bool:
    algoritmo, iteracoes, salt_b64, hash_b64 = armazenado.split("$", 3)
    if algoritmo != "pbkdf2_sha256":
        return False
    salt = base64.b64decode(salt_b64)
    esperado = base64.b64decode(hash_b64)
    obtido = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, int(iteracoes))
    return hmac.compare_digest(obtido, esperado)
