from dataclasses import FrozenInstanceError, replace
from datetime import datetime, date
from decimal import Decimal

import pytest

from sgm.desktop import (
    EventoContratualDesktop,
    RelatorioTecnicoDesktop,
    ResultadoCalculoDesktop,
    ServicoRelatorioTecnicoDesktop,
    TipoEventoDesktop,
)
from tests.unitarios.test_cadastro_contrato_desktop_0_9_3_c import (
    form as contrato_valido,
)
from tests.unitarios.test_cadastro_processo_desktop_0_9_3_b import (
    formulario_valido,
)


INSTANTE = datetime(2026, 8, 1, 12, 30, 45)


def resultado(total="310.91"):
    return ResultadoCalculoDesktop(
        competencia=date(2026, 7, 10),
        salario_base=Decimal("3800"),
        divisor=Decimal("220"),
        quantidade_horas=Decimal("12"),
        adicional_percentual=Decimal("0.5"),
        valor_hora=Decimal("17.272727"),
        valor_hora_com_adicional=Decimal("25.909091"),
        valor_total=Decimal(total),
        fundamento="Art. 7º, XVI, da Constituição Federal",
        formula_codigo="FM-HE-001",
    )


def evento():
    return EventoContratualDesktop(
        tipo=TipoEventoDesktop.ALTERACAO_SALARIAL,
        data_inicio=date(2026, 7, 1),
        descricao="Reajuste salarial",
        fundamento="ACT 2026",
        valor=Decimal("3800"),
    )


def gerar(resultados=None, eventos=None):
    return ServicoRelatorioTecnicoDesktop.gerar(
        referencia="CASO-001",
        identificacao=formulario_valido().criar_identificacao(),
        contrato=contrato_valido().criar_contrato(),
        eventos=tuple(eventos if eventos is not None else (evento(),)),
        resultados=tuple(
            resultados if resultados is not None else (resultado(),)
        ),
        gerado_em=INSTANTE,
    )


def test_01_valida_referencia_ausente():
    erros = ServicoRelatorioTecnicoDesktop.validar_dados(
        None,
        formulario_valido().criar_identificacao(),
        contrato_valido().criar_contrato(),
        (resultado(),),
    )
    assert "Abra ou crie um processo." in erros


def test_02_valida_identificacao_ausente():
    erros = ServicoRelatorioTecnicoDesktop.validar_dados(
        "CASO",
        None,
        contrato_valido().criar_contrato(),
        (resultado(),),
    )
    assert "Registre os dados processuais." in erros


def test_03_valida_contrato_ausente():
    erros = ServicoRelatorioTecnicoDesktop.validar_dados(
        "CASO",
        formulario_valido().criar_identificacao(),
        None,
        (resultado(),),
    )
    assert "Registre o contrato de trabalho." in erros


def test_04_valida_calculos_ausentes():
    erros = ServicoRelatorioTecnicoDesktop.validar_dados(
        "CASO",
        formulario_valido().criar_identificacao(),
        contrato_valido().criar_contrato(),
        (),
    )
    assert "Execute ao menos um cálculo." in erros


def test_05_gerar_rejeita_dados_incompletos():
    with pytest.raises(ValueError):
        ServicoRelatorioTecnicoDesktop.gerar(
            "",
            formulario_valido().criar_identificacao(),
            contrato_valido().criar_contrato(),
            (),
            (resultado(),),
            INSTANTE,
        )


def test_06_relatorio_valido():
    assert isinstance(gerar(), RelatorioTecnicoDesktop)


def test_07_relatorio_imutavel():
    with pytest.raises(FrozenInstanceError):
        gerar().conteudo = "Outro"


def test_08_referencia_preservada():
    assert gerar().referencia == "CASO-001"


def test_09_versao_preservada():
    assert gerar().versao == "0.9.3-G1"


def test_10_data_emissao_preservada():
    assert gerar().gerado_em == INSTANTE


def test_11_total_preservado():
    assert gerar().total_geral == Decimal("310.91")


def test_12_hash_sha256():
    assert len(gerar().identificador) == 64


def test_13_hash_deterministico():
    assert gerar().identificador == gerar().identificador


def test_14_contem_titulo():
    assert "RELATÓRIO TÉCNICO DE CÁLCULOS TRABALHISTAS" in gerar().conteudo


def test_15_contem_versao():
    assert "Versão 0.9.3-G1" in gerar().conteudo


def test_16_contem_emissao():
    assert "01/08/2026 12:30:45" in gerar().conteudo


def test_17_contem_referencia():
    assert "CASO-001" in gerar().conteudo


def test_18_contem_cnj():
    assert "0001234-55.2024.5.01.0007" in gerar().conteudo


def test_19_contem_reclamante():
    assert "Fulano de Tal" in gerar().conteudo


def test_20_contem_reclamada():
    assert "Empresa XYZ Ltda." in gerar().conteudo


def test_21_contem_contrato():
    assert "SÍNTESE DO CONTRATO DE TRABALHO" in gerar().conteudo


def test_22_contem_salario_inicial():
    assert "Salário inicial: R$" in gerar().conteudo


def test_23_contem_evento():
    assert "Alteração salarial" in gerar().conteudo


def test_24_contem_valor_evento():
    assert "R$ 3.800,00" in gerar().conteudo


def test_25_sem_eventos_e_permitido():
    assert "Nenhum evento contratual" in gerar(eventos=()).conteudo


def test_26_contem_premissas():
    assert "4. PREMISSAS TÉCNICAS" in gerar().conteudo


def test_27_contem_competencia():
    assert "10/07/2026" in gerar().conteudo


def test_28_contem_salario_vigente():
    assert "Salário vigente na competência: R$ 3.800,00" in gerar().conteudo


def test_29_contem_divisor():
    assert "Divisor contratual: 220,00" in gerar().conteudo


def test_30_contem_adicional():
    assert "Percentual aplicado: 50,00%" in gerar().conteudo


def test_31_contem_formula():
    assert "FM-HE-001" in gerar().conteudo


def test_32_contem_fundamento():
    assert "Art. 7º, XVI" in gerar().conteudo


def test_33_contem_hora_normal():
    assert "17,272727" in gerar().conteudo


def test_34_contem_hora_extra():
    assert "25,909091" in gerar().conteudo


def test_35_contem_resultado():
    assert "Resultado: R$ 310,91" in gerar().conteudo


def test_36_contem_memoria_resumida():
    assert "6. MEMÓRIA TÉCNICA RESUMIDA" in gerar().conteudo


def test_37_contem_tres_passos():
    texto = gerar().conteudo
    assert "Passo 1" in texto
    assert "Passo 2" in texto
    assert "Passo 3" in texto


def test_38_contem_conclusao():
    assert "CONCLUSÃO TÉCNICA" in gerar().conteudo


def test_39_conclusao_declara_sem_recalculo():
    assert "sem executar novo cálculo" in gerar().conteudo


def test_40_contem_rastreabilidade():
    assert "RASTREABILIDADE" in gerar().conteudo


def test_41_contem_motor():
    assert "ServicoValorHora + ServicoHoraExtra" in gerar().conteudo


def test_42_contem_origem_dados():
    assert "Processo → Contrato → Eventos" in gerar().conteudo


def test_43_contem_hash_no_texto():
    relatorio = gerar()
    assert relatorio.identificador in relatorio.conteudo


def test_44_soma_multiplos_resultados():
    relatorio = gerar(
        resultados=(resultado("310.91"), resultado("100.00"))
    )
    assert relatorio.total_geral == Decimal("410.91")


def test_45_ordena_resultados_por_competencia():
    antigo = replace(resultado(), competencia=date(2026, 6, 1))
    novo = replace(resultado(), competencia=date(2026, 7, 1))
    texto = gerar(resultados=(novo, antigo)).conteudo
    secao = texto.split(
        "4. PREMISSAS TÉCNICAS",
        1,
    )[1]
    assert secao.index("01/06/2026") < secao.index("01/07/2026")


def test_46_ordena_eventos_por_data():
    a = replace(evento(), data_inicio=date(2026, 8, 1))
    b = replace(evento(), data_inicio=date(2026, 6, 1))
    texto = gerar(eventos=(a, b)).conteudo
    secao = texto.split(
        "3. EVENTOS CONTRATUAIS CONSIDERADOS",
        1,
    )[1].split(
        "4. PREMISSAS TÉCNICAS",
        1,
    )[0]
    assert secao.index("01/06/2026") < secao.index("01/08/2026")


def test_47_nao_altera_resultado():
    item = resultado()
    gerar(resultados=(item,))
    assert item.valor_total == Decimal("310.91")


def test_48_nao_altera_evento():
    item = evento()
    gerar(eventos=(item,))
    assert item.valor == Decimal("3800")


def test_49_conteudo_deterministico_com_mesmo_instante():
    assert gerar().conteudo == gerar().conteudo


def test_50_identificador_muda_se_total_mudar():
    primeiro = gerar(resultados=(resultado("310.91"),))
    segundo = gerar(resultados=(resultado("311.00"),))
    assert primeiro.identificador != segundo.identificador



def test_51_contem_origem_base_evento():
    assert "Origem da base salarial: Evento contratual" in gerar().conteudo


def test_52_contem_evento_base():
    assert "Evento considerado: Alteração salarial de 01/07/2026" in gerar().conteudo


def test_53_contem_salario_inicial_e_vigente():
    texto = gerar().conteudo
    assert "Salário originalmente contratado: R$ 3.500,00" in texto
    assert "Salário vigente na competência: R$ 3.800,00" in texto


def test_54_contem_versoes_engine_e_formula():
    texto = gerar().conteudo
    assert "Versão do Engine: 0.9.3-G1" in texto
    assert "Versão da fórmula: 1.0" in texto


def test_55_contem_criterio_arredondamento():
    texto = gerar().conteudo
    assert "Critério de arredondamento: ROUND_HALF_UP" in texto
    assert "Precisão intermediária: 6 casas decimais" in texto
    assert "Precisão monetária: 2 casas decimais" in texto


def test_56_contem_fundamentacao_estruturada():
    texto = gerar().conteudo
    assert "Fundamentação jurídica:" in texto
    assert "CLT, art. 59" in texto
    assert "ACT 2026" in texto


def test_57_contem_fontes_estruturadas():
    texto = gerar().conteudo
    assert "Fontes de dados utilizadas:" in texto
    assert "✓ Processo" in texto
    assert "✓ Contrato de trabalho" in texto
    assert "✓ Resultado persistido FM-HE-001" in texto
    assert "✓ Memória técnica persistida" in texto


def test_58_contem_demonstrativo_financeiro():
    texto = gerar().conteudo
    assert "5. DEMONSTRATIVO FINANCEIRO" in texto
    assert "TOTAL GERAL | R$ 310,91" in texto


def test_59_contem_memoria_separada():
    assert "6. MEMÓRIA TÉCNICA RESUMIDA" in gerar().conteudo


def test_60_conclusao_e_rastreabilidade_renumeradas():
    texto = gerar().conteudo
    assert "7. CONCLUSÃO TÉCNICA" in texto
    assert "8. RASTREABILIDADE" in texto
