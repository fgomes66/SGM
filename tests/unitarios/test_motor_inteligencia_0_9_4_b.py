import pytest

from sgm.ia import (
    ContextoIA,
    ErroProvedorIA,
    MotorInteligencia,
    RequisicaoIA,
    RespostaIA,
)


class ProvedorTeste:
    nome = "teste"

    def responder(self, requisicao: RequisicaoIA) -> RespostaIA:
        referencia = requisicao.contexto.processo_referencia or "sem processo"
        return RespostaIA(
            conteudo=f"{referencia}: {requisicao.mensagem}",
            provedor=self.nome,
            modelo="simulado",
        )


def test_01_motor_usa_provedor_injetado():
    motor = MotorInteligencia(ProvedorTeste())

    resposta = motor.consultar(
        "Resuma o caso",
        ContextoIA(processo_referencia="0001"),
    )

    assert resposta.conteudo == "0001: Resuma o caso"
    assert resposta.provedor == "teste"
    assert resposta.modelo == "simulado"


def test_02_motor_rejeita_mensagem_vazia():
    motor = MotorInteligencia(ProvedorTeste())

    with pytest.raises(ValueError, match="não pode ser vazia"):
        motor.consultar("   ")


def test_03_motor_sem_configuracao_falha_de_forma_controlada():
    motor = MotorInteligencia()

    with pytest.raises(ErroProvedorIA, match="Nenhum provedor"):
        motor.consultar("Olá")


def test_04_contexto_normaliza_dados_e_e_imutavel():
    contexto = ContextoIA(dados={" salário ": " 3500 "})

    assert contexto.dados["salário"] == "3500"
    with pytest.raises(TypeError):
        contexto.dados["salário"] = "4000"


def test_05_motor_valida_identidade_do_provedor():
    class ProvedorInconsistente:
        nome = "origem"

        def responder(self, requisicao: RequisicaoIA) -> RespostaIA:
            return RespostaIA(conteudo="ok", provedor="outro")

    motor = MotorInteligencia(ProvedorInconsistente())

    with pytest.raises(ErroProvedorIA, match="inconsistente"):
        motor.consultar("Teste")
