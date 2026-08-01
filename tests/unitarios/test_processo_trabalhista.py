from datetime import date
import pytest
from sgm.dominio.processos import FaseProcessual, ProcessoTrabalhista, StatusProcesso

def criar_processo(**alteracoes):
    dados = {
        "identificador_interno": "SGM-2026-0001",
        "tribunal": "TRT1",
        "fase_processual": FaseProcessual.LIQUIDACAO,
        "status": StatusProcesso.CADASTRADO,
        "data_recebimento": date(2026, 7, 31),
        "numero_cnj": "0101234-55.2025.5.01.0007",
        "vara": "7ª Vara do Trabalho",
        "municipio": "Rio de Janeiro",
        "uf": "RJ",
    }
    dados.update(alteracoes)
    return ProcessoTrabalhista(**dados)

def test_cria_processo_valido():
    processo = criar_processo()
    assert processo.possui_numero_cnj
    assert processo.versao == 1

def test_numero_cnj_invalido_e_rejeitado():
    with pytest.raises(ValueError):
        criar_processo(numero_cnj="123")

def test_uf_invalida_e_rejeitada():
    with pytest.raises(ValueError):
        criar_processo(uf="RIO")

def test_sentenca_nao_pode_anteceder_ajuizamento():
    with pytest.raises(ValueError):
        criar_processo(
            data_ajuizamento=date(2025, 5, 10),
            data_sentenca=date(2025, 5, 9),
        )

def test_alterar_status_incrementa_versao():
    processo = criar_processo()
    processo.alterar_status(StatusProcesso.EM_ANALISE)
    assert processo.status == StatusProcesso.EM_ANALISE
    assert processo.versao == 2

def test_processo_encerrado_nao_muda_status():
    processo = criar_processo(status=StatusProcesso.ENCERRADO)
    with pytest.raises(ValueError):
        processo.alterar_status(StatusProcesso.EM_ANALISE)

def test_data_base_nao_pode_anteceder_recebimento():
    processo = criar_processo()
    with pytest.raises(ValueError):
        processo.definir_data_base(date(2026, 7, 30))

def test_definir_data_base_incrementa_versao():
    processo = criar_processo()
    processo.definir_data_base(date(2026, 8, 31))
    assert processo.versao == 2
