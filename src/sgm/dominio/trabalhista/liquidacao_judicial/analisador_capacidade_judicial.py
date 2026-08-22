from __future__ import annotations

from .diagnostico_capacidade_judicial import (
    CapacidadeVerbaJudicial,
    DiagnosticoCapacidadeJudicial,
    DiagnosticoVerbaJudicial,
)
from .entrada_caso_trabalhista import EntradaCasoTrabalhista
from .resultado_validacao import NivelValidacao
from .validador_caso_trabalhista import ValidadorCasoTrabalhista


class AnalisadorCapacidadeJudicial:
    """
    Diagnostica se cada verba reconhecida no título pode ser
    executada pelo motor judicial atual.

    A análise não substitui o ValidadorCasoTrabalhista.
    Ela reutiliza seus achados e acrescenta a noção de
    capacidade funcional do motor.
    """

    VERBAS_SUPORTADAS = frozenset(
        {
            "DECIMO_TERCEIRO",
            "FERIAS",
            "FGTS",
            "HORA_EXTRA",
            "DSR",
            "AVISO_PREVIO",
            "EQUIPARACAO_SALARIAL",
        }
    )

    @classmethod
    def analisar(
        cls,
        entrada: EntradaCasoTrabalhista,
    ) -> DiagnosticoCapacidadeJudicial:
        if not isinstance(entrada, EntradaCasoTrabalhista):
            raise TypeError(
                "A entrada deve ser uma EntradaCasoTrabalhista."
            )

        validacao = ValidadorCasoTrabalhista.validar(entrada)

        diagnosticos: list[DiagnosticoVerbaJudicial] = []

        for indice, verba in enumerate(
            entrada.sentenca.verbas_deferidas
        ):
            codigo = verba.codigo.upper()

            if codigo not in cls.VERBAS_SUPORTADAS:
                diagnosticos.append(
                    DiagnosticoVerbaJudicial(
                        indice=indice,
                        codigo_verba=codigo,
                        descricao=verba.descricao,
                        capacidade=(
                            CapacidadeVerbaJudicial.NAO_SUPORTADO
                        ),
                        motivos=(
                            (
                                f"A verba {codigo} ainda não possui "
                                "executor integrado ao motor de "
                                "liquidação judicial."
                            ),
                        ),
                    )
                )
                continue

            if (
                codigo == "EQUIPARACAO_SALARIAL"
                and not verba.competencias_equiparacao
            ):
                diagnosticos.append(
                    DiagnosticoVerbaJudicial(
                        indice=indice,
                        codigo_verba=codigo,
                        descricao=verba.descricao,
                        capacidade=(
                            CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
                        ),
                        motivos=(
                            (
                                "A equiparação salarial exige "
                                "competências remuneratórias da "
                                "reclamante e do paradigma."
                            ),
                        ),
                    )
                )
                continue

            prefixo_campo = f"verbas[{indice}]"

            erros_verba = tuple(
                achado
                for achado in validacao.achados
                if (
                    achado.nivel is NivelValidacao.ERRO
                    and achado.campo is not None
                    and achado.campo.startswith(prefixo_campo)
                )
            )

            if erros_verba:
                diagnosticos.append(
                    DiagnosticoVerbaJudicial(
                        indice=indice,
                        codigo_verba=codigo,
                        descricao=verba.descricao,
                        capacidade=(
                            CapacidadeVerbaJudicial.BLOQUEADO_POR_DADOS
                        ),
                        motivos=tuple(
                            achado.mensagem
                            for achado in erros_verba
                        ),
                    )
                )
                continue

            diagnosticos.append(
                DiagnosticoVerbaJudicial(
                    indice=indice,
                    codigo_verba=codigo,
                    descricao=verba.descricao,
                    capacidade=CapacidadeVerbaJudicial.EXECUTAVEL,
                )
            )

        return DiagnosticoCapacidadeJudicial(
            referencia_processo=entrada.referencia_processo,
            verbas=tuple(diagnosticos),
        )

