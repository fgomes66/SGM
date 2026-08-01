from decimal import Decimal
import pytest
from sgm.dominio.objetos_valor import Percentual

def test_percentual_de_cinquenta() -> None:
    percentual = Percentual.de_percentual("50")
    assert percentual.fator == Decimal("0.5")
    assert percentual.multiplicador_com_principal == Decimal("1.5")

def test_float_e_proibido() -> None:
    with pytest.raises(TypeError):
        Percentual(0.5)
