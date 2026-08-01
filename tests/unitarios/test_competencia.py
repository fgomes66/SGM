from datetime import date
import pytest
from sgm.dominio.objetos_valor import Competencia

def test_competencia_bissexta() -> None:
    competencia = Competencia.de_texto("2024-02")
    assert competencia.inicio == date(2024, 2, 1)
    assert competencia.fim == date(2024, 2, 29)

def test_proxima_competencia_vira_o_ano() -> None:
    assert str(Competencia(2026, 12).proxima()) == "2027-01"

def test_formato_invalido_e_rejeitado() -> None:
    with pytest.raises(ValueError):
        Competencia.de_texto("02/2024")
