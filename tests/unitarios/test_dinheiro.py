from decimal import Decimal
import pytest
from sgm.dominio.objetos_valor import Dinheiro

def test_soma_e_quantizacao() -> None:
    total = Dinheiro.de_texto("10.105") + Dinheiro.de_texto("5.205")
    assert total.valor == Decimal("15.310")
    assert total.quantizado().valor == Decimal("15.31")

def test_float_e_proibido() -> None:
    with pytest.raises(TypeError):
        Dinheiro(10.50)

def test_moedas_incompativeis_sao_rejeitadas() -> None:
    with pytest.raises(ValueError):
        Dinheiro.de_texto("10", "BRL") + Dinheiro.de_texto("5", "USD")

def test_divisao_por_zero_e_rejeitada() -> None:
    with pytest.raises(ZeroDivisionError):
        Dinheiro.de_texto("100").dividir(Decimal("0"))
