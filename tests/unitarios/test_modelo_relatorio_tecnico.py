from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from sgm.dominio.trabalhista import (
    GeradorDemonstrativoFinanceiro,
    GeradorLinhaTempoProfissional,
    GeradorMemoriaProfissional,
)
from sgm.relatorio import (
    IdentificacaoProcesso,
    MetadadosRelatorio,
    OrgaoJulgador,
    ParametrosRelatorio,
    RelatorioTecnico,
    TipoRelatorio,
)
from tests.unitarios.test_caso_temporal_completo import calcular


HASH = "a" * 64


def documentos():
    resultado = calcular()
    return (
        resultado,
        GeradorMemoriaProfissional.gerar(resultado),
        GeradorDemonstrativoFinanceiro.gerar(resultado),
        GeradorLinhaTempoProfissional.gerar(resultado),
    )


def orgao():
    return OrgaoJulgador(
        tribunal="Tribunal Regional do Trabalho",
        regiao_trt=1,
        vara="7ª Vara do Trabalho do Rio de Janeiro",
        municipio="Rio de Janeiro",
        uf="rj",
    )


def identificacao():
    return IdentificacaoProcesso(
        orgao_julgador=orgao(),
        numero_processo="0001234-55.2024.5.01.0007",
        classe_processual="Reclamação Trabalhista",
        reclamante="Fulano de Tal",
        reclamada="Empresa XYZ Ltda.",
        magistrado="Dra. Maria da Silva",
        perito="João Perito",
    )


def metadados():
    _, _, demonstrativo, linha = documentos()
    eventos = tuple(
        marco
        for marco in linha.marcos
        if marco.tipo.value not in (
            "INICIO_PERIODO",
            "FIM_PERIODO",
        )
    )
    return MetadadosRelatorio(
        uuid=uuid4(),
        hash_sha256=HASH,
        versao_sgm="0.9.2-E1",
        versao_regras="2026.1",
        data_emissao=datetime(
            2026, 7, 31, 21, 30, tzinfo=timezone.utc
        ),
        quantidade_competencias=len(
            demonstrativo.competencias
        ),
        quantidade_verbas=len(demonstrativo.verbas),
        quantidade_eventos=len(eventos),
    )


def parametros():
    return ParametrosRelatorio(
        periodo_analisado="2022-01 a 2022-09",
        indice_correcao="Fator informado no plano.",
        juros="Fator informado no plano.",
        moeda="brl",
        observacoes=(
            "Critérios parametrizados.",
            " ",
        ),
    )


def relatorio():
    _, memoria, demonstrativo, linha = documentos()
    return RelatorioTecnico(
        tipo=TipoRelatorio.RELATORIO_TECNICO,
        identificacao=identificacao(),
        metadados=metadados(),
        parametros=parametros(),
        memoria=memoria,
        demonstrativo=demonstrativo,
        linha_tempo=linha,
    )


def test_01_tipo_relatorio_estavel():
    assert (
        TipoRelatorio.RELATORIO_TECNICO.value
        == "RELATORIO_TECNICO"
    )


def test_02_orgao_valido():
    item = orgao()
    assert item.regiao_trt == 1
    assert item.uf == "RJ"


def test_03_orgao_rejeita_regiao_zero():
    with pytest.raises(ValueError):
        OrgaoJulgador(
            "TRT",
            0,
            "Vara",
            "Rio",
            "RJ",
        )


def test_04_orgao_rejeita_uf_invalida():
    with pytest.raises(ValueError):
        OrgaoJulgador(
            "TRT",
            1,
            "Vara",
            "Rio",
            "R",
        )


def test_05_orgao_descricao_completa():
    texto = orgao().descricao_completa
    assert "1ª Região" in texto
    assert "Rio de Janeiro/RJ" in texto


def test_06_identificacao_valida():
    item = identificacao()
    assert item.reclamante == "Fulano de Tal"
    assert item.magistrado == "Dra. Maria da Silva"


def test_07_identificacao_rejeita_numero_cnj_invalido():
    with pytest.raises(ValueError):
        IdentificacaoProcesso(
            orgao_julgador=orgao(),
            numero_processo="123",
            classe_processual="Classe",
            reclamante="Autor",
            reclamada="Ré",
        )


def test_08_identificacao_rejeita_reclamante_vazio():
    with pytest.raises(ValueError):
        IdentificacaoProcesso(
            orgao_julgador=orgao(),
            numero_processo="0001234-55.2024.5.01.0007",
            classe_processual="Classe",
            reclamante=" ",
            reclamada="Ré",
        )


def test_09_identificacao_normaliza_opcionais():
    item = IdentificacaoProcesso(
        orgao_julgador=orgao(),
        numero_processo="0001234-55.2024.5.01.0007",
        classe_processual="Classe",
        reclamante="Autor",
        reclamada="Ré",
        magistrado=" ",
    )
    assert item.magistrado is None


def test_10_parametros_validos():
    item = parametros()
    assert item.moeda == "BRL"
    assert item.observacoes == ("Critérios parametrizados.",)


def test_11_parametros_rejeitam_moeda_invalida():
    with pytest.raises(ValueError):
        ParametrosRelatorio(
            periodo_analisado="2022",
            indice_correcao="Índice",
            juros="Juros",
            moeda="R$",
        )


def test_12_parametros_rejeitam_periodo_vazio():
    with pytest.raises(ValueError):
        ParametrosRelatorio(
            periodo_analisado=" ",
            indice_correcao="Índice",
            juros="Juros",
            moeda="BRL",
        )


def test_13_metadados_validos():
    item = metadados()
    assert isinstance(item.uuid, UUID)
    assert item.hash_sha256 == HASH


def test_14_metadados_rejeitam_hash_invalido():
    with pytest.raises(ValueError):
        replace(metadados(), hash_sha256="xyz")


def test_15_metadados_rejeitam_data_sem_fuso():
    with pytest.raises(ValueError):
        replace(
            metadados(),
            data_emissao=datetime(2026, 7, 31, 21, 30),
        )


def test_16_metadados_rejeitam_quantidade_negativa():
    with pytest.raises(ValueError):
        replace(
            metadados(),
            quantidade_competencias=-1,
        )


def test_17_relatorio_valido():
    item = relatorio()
    assert item.tipo == TipoRelatorio.RELATORIO_TECNICO
    assert item.referencia == "CASO-0013"


def test_18_relatorio_identifica_juizo():
    resumo = relatorio().resumo_identificacao()
    texto = "\n".join(resumo)
    assert "JUSTIÇA DO TRABALHO" in texto
    assert "7ª Vara do Trabalho" in texto


def test_19_relatorio_exibe_magistrado_quando_informado():
    texto = "\n".join(relatorio().resumo_identificacao())
    assert "Magistrado(a): Dra. Maria da Silva" in texto


def test_20_relatorio_exibe_perito_quando_informado():
    texto = "\n".join(relatorio().resumo_identificacao())
    assert "Perito(a): João Perito" in texto


def test_21_relatorio_rejeita_referencias_divergentes():
    item = relatorio()
    memoria = replace(item.memoria, referencia="OUTRA")
    with pytest.raises(ValueError):
        replace(item, memoria=memoria)


def test_22_relatorio_rejeita_quantidade_competencias_divergente():
    item = relatorio()
    metadados_divergentes = replace(
        item.metadados,
        quantidade_competencias=99,
    )
    with pytest.raises(ValueError):
        replace(item, metadados=metadados_divergentes)


def test_23_relatorio_rejeita_quantidade_verbas_divergente():
    item = relatorio()
    metadados_divergentes = replace(
        item.metadados,
        quantidade_verbas=99,
    )
    with pytest.raises(ValueError):
        replace(item, metadados=metadados_divergentes)


def test_24_relatorio_rejeita_quantidade_eventos_divergente():
    item = relatorio()
    metadados_divergentes = replace(
        item.metadados,
        quantidade_eventos=99,
    )
    with pytest.raises(ValueError):
        replace(item, metadados=metadados_divergentes)


def test_25_relatorio_rejeita_titulo_vazio():
    with pytest.raises(ValueError):
        replace(relatorio(), titulo=" ")


def test_26_relatorio_e_imutavel():
    item = relatorio()
    with pytest.raises(FrozenInstanceError):
        item.titulo = "Outro"


def test_27_orgao_e_imutavel():
    item = orgao()
    with pytest.raises(FrozenInstanceError):
        item.uf = "SP"


def test_28_identificacao_e_imutavel():
    item = identificacao()
    with pytest.raises(FrozenInstanceError):
        item.reclamante = "Outro"


def test_29_documentos_de_origem_sao_preservados():
    item = relatorio()
    _, memoria, demonstrativo, linha = documentos()
    assert item.memoria.como_texto() == memoria.como_texto()
    assert (
        item.demonstrativo.como_texto()
        == demonstrativo.como_texto()
    )
    assert (
        item.linha_tempo.como_texto()
        == linha.como_texto()
    )


def test_30_construcao_e_reproduzivel_no_conteudo():
    primeiro = relatorio()
    segundo = relatorio()

    assert primeiro.resumo_identificacao() == (
        segundo.resumo_identificacao()
    )
    assert primeiro.parametros == segundo.parametros
    assert primeiro.memoria.como_texto() == (
        segundo.memoria.como_texto()
    )
    assert primeiro.demonstrativo.como_texto() == (
        segundo.demonstrativo.como_texto()
    )
    assert primeiro.linha_tempo.como_texto() == (
        segundo.linha_tempo.como_texto()
    )
