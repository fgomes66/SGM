import json

import pytest

from sgm.desktop import (
    ControladorDesktop,
    RegistroProcesso,
    RepositorioProcessosJSON,
    SerializadorProcesso,
)
from tests.unitarios.test_cadastro_processo_desktop_0_9_3_b import (
    formulario_valido,
)


def registro():
    return RegistroProcesso(
        referencia="CASO-500",
        identificacao=(
            formulario_valido().criar_identificacao()
        ),
    )


def test_01_registro_valido():
    item = registro()
    assert item.referencia == "CASO-500"


def test_02_registro_rejeita_referencia_vazia():
    with pytest.raises(ValueError):
        RegistroProcesso(
            referencia=" ",
            identificacao=(
                formulario_valido().criar_identificacao()
            ),
        )


def test_03_serializa_schema():
    dados = SerializadorProcesso.para_dict(registro())
    assert dados["schema"] == 1


def test_04_serializa_referencia():
    dados = SerializadorProcesso.para_dict(registro())
    assert dados["referencia"] == "CASO-500"


def test_05_serializa_numero_cnj():
    dados = SerializadorProcesso.para_dict(registro())
    assert (
        dados["identificacao"]["numero_processo"]
        == "0001234-55.2024.5.01.0007"
    )


def test_06_desserializa_registro():
    dados = SerializadorProcesso.para_dict(registro())
    item = SerializadorProcesso.de_dict(dados)
    assert item == registro()


def test_07_rejeita_schema_invalido():
    dados = SerializadorProcesso.para_dict(registro())
    dados["schema"] = 99
    with pytest.raises(ValueError):
        SerializadorProcesso.de_dict(dados)


def test_08_repositorio_cria_pasta(tmp_path):
    pasta = tmp_path / "dados" / "processos"
    RepositorioProcessosJSON(pasta)
    assert pasta.exists()


def test_09_caminho_normalizado(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    caminho = repo.caminho_para("CASO 500")
    assert caminho.name == "CASO_500_processo.json"


def test_10_salva_arquivo(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    caminho = repo.salvar(registro())
    assert caminho.exists()


def test_11_arquivo_e_json_utf8(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    caminho = repo.salvar(registro())
    dados = json.loads(
        caminho.read_text(encoding="utf-8")
    )
    assert dados["referencia"] == "CASO-500"


def test_12_salvamento_cria_indice(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    repo.salvar(registro())
    assert repo.arquivo_indice.exists()


def test_13_carrega_processo(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    repo.salvar(registro())
    assert repo.carregar("CASO-500") == registro()


def test_14_carrega_ultimo(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    repo.salvar(registro())
    assert repo.carregar_ultimo() == registro()


def test_15_ultimo_inexistente_retorna_none(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    assert repo.carregar_ultimo() is None


def test_16_lista_referencias(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    repo.salvar(registro())
    assert repo.listar_referencias() == ("CASO-500",)


def test_17_controlador_salva(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    controlador = ControladorDesktop(repositorio=repo)
    controlador.novo_processo("CASO-500")
    controlador.registrar_identificacao(
        formulario_valido()
    )
    caminho = controlador.salvar()
    assert caminho.exists()
    assert not controlador.estado.alteracoes_pendentes


def test_18_controlador_rejeita_salvar_sem_referencia(tmp_path):
    controlador = ControladorDesktop(
        repositorio=RepositorioProcessosJSON(tmp_path)
    )
    with pytest.raises(ValueError):
        controlador.salvar()


def test_19_controlador_rejeita_salvar_sem_identificacao(tmp_path):
    controlador = ControladorDesktop(
        repositorio=RepositorioProcessosJSON(tmp_path)
    )
    controlador.novo_processo("CASO-500")
    with pytest.raises(ValueError):
        controlador.salvar()


def test_20_controlador_abre_processo(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    repo.salvar(registro())
    controlador = ControladorDesktop(repositorio=repo)
    controlador.abrir("CASO-500")
    assert controlador.estado.referencia_processo == "CASO-500"
    assert controlador.estado.identificacao_processo is not None


def test_21_controlador_carrega_ultimo(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    repo.salvar(registro())
    controlador = ControladorDesktop(repositorio=repo)
    assert controlador.carregar_ultimo()
    assert controlador.estado.referencia_processo == "CASO-500"


def test_22_controlador_sem_ultimo_retorna_false(tmp_path):
    controlador = ControladorDesktop(
        repositorio=RepositorioProcessosJSON(tmp_path)
    )
    assert not controlador.carregar_ultimo()


def test_23_abertura_limpa_pendencias(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    repo.salvar(registro())
    controlador = ControladorDesktop(repositorio=repo)
    controlador.abrir("CASO-500")
    assert not controlador.estado.alteracoes_pendentes


def test_24_salvamento_preserva_opcionais(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    repo.salvar(registro())
    carregado = repo.carregar("CASO-500")
    assert carregado.identificacao.magistrado == (
        "Dra. Maria da Silva"
    )
    assert carregado.identificacao.perito == "João Perito"


def test_25_regravacao_e_deterministica(tmp_path):
    repo = RepositorioProcessosJSON(tmp_path)
    primeiro = repo.salvar(registro()).read_bytes()
    segundo = repo.salvar(registro()).read_bytes()
    assert primeiro == segundo
