import pytest
from sgm.infraestrutura.seguranca.senhas import gerar_hash_senha, verificar_senha

def test_hash_e_verificacao() -> None:
    senha = "Senha-Forte-123!"
    armazenado = gerar_hash_senha(senha)
    assert senha not in armazenado
    assert verificar_senha(senha, armazenado)
    assert not verificar_senha("senha-incorreta", armazenado)

def test_senha_curta_e_rejeitada() -> None:
    with pytest.raises(ValueError):
        gerar_hash_senha("curta")
