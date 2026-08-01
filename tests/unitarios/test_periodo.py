from datetime import date
import pytest
from sgm.dominio.objetos_valor import Periodo

def test_periodo_inclusivo() -> None:
    periodo = Periodo(date(2026, 7, 1), date(2026, 7, 31))
    assert periodo.quantidade_dias == 31
    assert periodo.contem(date(2026, 7, 31))

def test_intersecao() -> None:
    a = Periodo(date(2026, 1, 1), date(2026, 1, 20))
    b = Periodo(date(2026, 1, 15), date(2026, 1, 31))
    assert a.intersecao(b) == Periodo(date(2026, 1, 15), date(2026, 1, 20))

def test_periodo_invertido_e_rejeitado() -> None:
    with pytest.raises(ValueError):
        Periodo(date(2026, 2, 1), date(2026, 1, 31))
