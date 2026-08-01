from dataclasses import replace
from datetime import date
from pathlib import Path

from sgm.desktop import (
    ControladorDesktop,
    DadosCalculoFormulario,
    DadosContratoFormulario,
    DadosEventoFormulario,
    RepositorioProcessosJSON,
    SecaoDesktop,
)
from tests.unitarios.test_cadastro_processo_desktop_0_9_3_b import (
    formulario_valido,
)


def contrato():
    return DadosContratoFormulario(
        data_admissao="2024-01-01",
        data_desligamento="",
        tipo_contrato="INDETERMINADO",
        cargo="Analista",
        funcao="Analista",
        cbo="",
        salario_inicial="3500,00",
        jornada_semanal_horas="44",
        divisor_jornada="220",
        motivo_desligamento="",
        sindicato="",
        norma_coletiva="",
        observacoes="",
    )


def evento():
    return DadosEventoFormulario(
        tipo="ALTERACAO_SALARIAL",
        data_inicio="2024-02-01",
        descricao="Reajuste",
        fundamento="CCT",
        valor="4000,00",
    )


def calculo():
    return DadosCalculoFormulario(
        competencia="2024-03-01",
        quantidade_horas="10",
        adicional_percentual="50",
        fundamento="Art. 7º, XVI, CF",
    )


def controlador(tmp_path):
    return ControladorDesktop(
        repositorio=RepositorioProcessosJSON(tmp_path),
        exigir_fluxo=True,
    )


def preparar_processo(ctrl):
    ctrl.novo_processo("CASO-F1")
    assert ctrl.registrar_identificacao(
        formulario_valido()
    ) == ()


def test_01_identificacao_autosalva(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    assert (
        tmp_path / "CASO-F1_processo.json"
    ).exists()


def test_02_identificacao_limpa_pendencia(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    assert not ctrl.estado.alteracoes_pendentes


def test_03_identificacao_registra_ultimo_salvamento(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    assert ctrl.estado.ultimo_salvamento is not None


def test_04_contrato_exige_processo(tmp_path):
    ctrl = controlador(tmp_path)
    assert ctrl.registrar_contrato(contrato())


def test_05_contrato_autosalva(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    assert ctrl.registrar_contrato(contrato()) == ()
    assert ctrl.repositorio.carregar(
        "CASO-F1"
    ).contrato is not None


def test_06_evento_exige_processo(tmp_path):
    ctrl = controlador(tmp_path)
    assert ctrl.registrar_evento(evento())


def test_07_evento_exige_contrato(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    assert ctrl.registrar_evento(evento())


def test_08_evento_autosalva(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.registrar_contrato(contrato())
    assert ctrl.registrar_evento(evento()) == ()
    assert len(
        ctrl.repositorio.carregar("CASO-F1").eventos
    ) == 1


def test_09_calculo_exige_processo(tmp_path):
    ctrl = controlador(tmp_path)
    assert ctrl.executar_calculo(calculo())


def test_10_calculo_exige_contrato(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    assert ctrl.executar_calculo(calculo())


def test_11_calculo_autosalva(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.registrar_contrato(contrato())
    assert ctrl.executar_calculo(calculo()) == ()
    assert len(
        ctrl.repositorio.carregar("CASO-F1").calculos
    ) == 1


def test_12_fluxo_completo_reabre(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.registrar_contrato(contrato())
    ctrl.registrar_evento(evento())
    ctrl.executar_calculo(calculo())

    novo = controlador(tmp_path)
    novo.abrir("CASO-F1")

    assert novo.estado.identificacao_processo is not None
    assert novo.estado.contrato_trabalho is not None
    assert len(novo.estado.eventos_contratuais) == 1
    assert len(novo.estado.resultados_calculo) == 1


def test_13_carregar_ultimo_restaura_fluxo(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.registrar_contrato(contrato())
    ctrl.executar_calculo(calculo())

    novo = controlador(tmp_path)
    assert novo.carregar_ultimo()
    assert len(novo.estado.resultados_calculo) == 1


def test_14_navegacao_contrato_bloqueada_sem_processo(tmp_path):
    ctrl = controlador(tmp_path)
    ctrl.navegar(SecaoDesktop.CONTRATO)
    assert ctrl.estado.secao_atual == SecaoDesktop.INICIO


def test_15_navegacao_eventos_bloqueada_sem_contrato(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.navegar(SecaoDesktop.EVENTOS)
    assert ctrl.estado.secao_atual == SecaoDesktop.PROCESSO


def test_16_navegacao_calculo_bloqueada_sem_contrato(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.navegar(SecaoDesktop.CALCULO)
    assert ctrl.estado.secao_atual == SecaoDesktop.PROCESSO


def test_17_navegacao_memoria_bloqueada_sem_calculo(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.registrar_contrato(contrato())
    ctrl.navegar(SecaoDesktop.MEMORIA)
    assert ctrl.estado.secao_atual == SecaoDesktop.PROCESSO


def test_18_navegacao_memoria_liberada_com_calculo(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.registrar_contrato(contrato())
    ctrl.executar_calculo(calculo())
    ctrl.navegar(SecaoDesktop.MEMORIA)
    assert ctrl.estado.secao_atual == SecaoDesktop.MEMORIA


def test_19_excluir_evento_autosalva(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.registrar_contrato(contrato())
    ctrl.registrar_evento(evento())
    item = ctrl.estado.eventos_contratuais[0]
    assert ctrl.excluir_evento(item.id)
    assert ctrl.repositorio.carregar(
        "CASO-F1"
    ).eventos == ()


def test_20_excluir_calculo_autosalva(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.registrar_contrato(contrato())
    ctrl.executar_calculo(calculo())
    item = ctrl.estado.resultados_calculo[0]
    assert ctrl.excluir_resultado_calculo(item.id)
    assert ctrl.repositorio.carregar(
        "CASO-F1"
    ).calculos == ()


def test_21_autosave_preserva_evento_e_calculo(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.registrar_contrato(contrato())
    ctrl.registrar_evento(evento())
    ctrl.executar_calculo(calculo())
    registro = ctrl.repositorio.carregar("CASO-F1")
    assert len(registro.eventos) == 1
    assert len(registro.calculos) == 1


def test_22_novo_processo_nao_cria_arquivo_incompleto(tmp_path):
    ctrl = controlador(tmp_path)
    ctrl.novo_processo("INCOMPLETO")
    assert not (
        tmp_path / "INCOMPLETO_processo.json"
    ).exists()


def test_23_salvar_manual_continua_funcionando(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    caminho = ctrl.salvar()
    assert isinstance(caminho, Path)
    assert caminho.exists()


def test_24_estado_reaberto_sem_pendencias(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    novo = controlador(tmp_path)
    novo.abrir("CASO-F1")
    assert not novo.estado.alteracoes_pendentes


def test_25_mensagem_autosalvamento_calculo(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.registrar_contrato(contrato())
    ctrl.executar_calculo(calculo())
    assert "salvo automaticamente" in (
        ctrl.estado.mensagem_status.lower()
    )


def test_26_processo_ativo_falso_inicialmente(tmp_path):
    ctrl = controlador(tmp_path)
    assert not ctrl.processo_ativo


def test_27_processo_ativo_apos_identificacao(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    assert ctrl.processo_ativo


def test_28_autosave_nao_deixa_pendencia_evento(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.registrar_contrato(contrato())
    ctrl.registrar_evento(evento())
    assert not ctrl.estado.alteracoes_pendentes


def test_29_autosave_nao_deixa_pendencia_calculo(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.registrar_contrato(contrato())
    ctrl.executar_calculo(calculo())
    assert not ctrl.estado.alteracoes_pendentes


def test_30_multiplos_calculos_persistem(tmp_path):
    ctrl = controlador(tmp_path)
    preparar_processo(ctrl)
    ctrl.registrar_contrato(contrato())
    ctrl.executar_calculo(calculo())
    ctrl.executar_calculo(
        replace(calculo(), competencia="2024-04-01")
    )
    assert len(
        ctrl.repositorio.carregar("CASO-F1").calculos
    ) == 2
