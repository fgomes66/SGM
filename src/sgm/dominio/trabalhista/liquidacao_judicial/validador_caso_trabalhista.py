from __future__ import annotations

from .entrada_caso_trabalhista import EntradaCasoTrabalhista
from .resultado_validacao import (
    AchadoValidacao,
    NivelValidacao,
    ResultadoValidacaoCaso,
)


class ValidadorCasoTrabalhista:
    """Valida a entrada antes da montagem do plano de liquidação."""

    @classmethod
    def validar(
        cls,
        entrada: EntradaCasoTrabalhista,
    ) -> ResultadoValidacaoCaso:
        if not isinstance(entrada, EntradaCasoTrabalhista):
            raise TypeError(
                "A entrada deve ser uma EntradaCasoTrabalhista."
            )

        achados: list[AchadoValidacao] = []

        cls._validar_coerencia(entrada, achados)
        cls._validar_sentenca(entrada, achados)
        cls._validar_contrato(entrada, achados)
        cls._validar_parametros(entrada, achados)
        cls._validar_verbas(entrada, achados)
        cls._validar_premissas(entrada, achados)

        return ResultadoValidacaoCaso(tuple(achados))

    @staticmethod
    def _validar_coerencia(
        entrada: EntradaCasoTrabalhista,
        achados: list[AchadoValidacao],
    ) -> None:
        for indice, mensagem in enumerate(
            entrada.validar_coerencia(),
            start=1,
        ):
            achados.append(
                AchadoValidacao(
                    codigo=f"COERENCIA-{indice:03d}",
                    nivel=NivelValidacao.ERRO,
                    mensagem=mensagem,
                )
            )

    @staticmethod
    def _validar_sentenca(
        entrada: EntradaCasoTrabalhista,
        achados: list[AchadoValidacao],
    ) -> None:
        sentenca = entrada.sentenca

        if sentenca.data_sentenca is None:
            achados.append(
                AchadoValidacao(
                    codigo="SENTENCA-001",
                    nivel=NivelValidacao.ALERTA,
                    campo="sentenca.data_sentenca",
                    mensagem="A data da sentença não foi informada.",
                )
            )

        if not sentenca.texto_dispositivo:
            achados.append(
                AchadoValidacao(
                    codigo="SENTENCA-002",
                    nivel=NivelValidacao.ALERTA,
                    campo="sentenca.texto_dispositivo",
                    mensagem=(
                        "O dispositivo da sentença não foi registrado."
                    ),
                )
            )

        if not sentenca.verbas_deferidas:
            achados.append(
                AchadoValidacao(
                    codigo="SENTENCA-003",
                    nivel=NivelValidacao.ERRO,
                    campo="sentenca.verbas_deferidas",
                    mensagem="Nenhuma verba deferida foi cadastrada.",
                )
            )

    @staticmethod
    def _validar_contrato(
        entrada: EntradaCasoTrabalhista,
        achados: list[AchadoValidacao],
    ) -> None:
        contrato = entrada.contrato

        if contrato.data_desligamento is None:
            achados.append(
                AchadoValidacao(
                    codigo="CONTRATO-001",
                    nivel=NivelValidacao.ALERTA,
                    campo="contrato.data_desligamento",
                    mensagem=(
                        "A data de desligamento não foi informada."
                    ),
                )
            )

        if contrato.jornada_semanal is None:
            achados.append(
                AchadoValidacao(
                    codigo="CONTRATO-002",
                    nivel=NivelValidacao.ALERTA,
                    campo="contrato.jornada_semanal",
                    mensagem="A jornada semanal não foi informada.",
                )
            )

    @staticmethod
    def _validar_parametros(
        entrada: EntradaCasoTrabalhista,
        achados: list[AchadoValidacao],
    ) -> None:
        parametros = entrada.parametros

        if parametros.divisor_horas is None:
            achados.append(
                AchadoValidacao(
                    codigo="PARAM-001",
                    nivel=NivelValidacao.ALERTA,
                    campo="parametros.divisor_horas",
                    mensagem="O divisor de horas não foi informado.",
                )
            )

        if parametros.percentual_horas_extras is None:
            achados.append(
                AchadoValidacao(
                    codigo="PARAM-002",
                    nivel=NivelValidacao.INFORMACAO,
                    campo="parametros.percentual_horas_extras",
                    mensagem=(
                        "Não há percentual geral de horas extras definido."
                    ),
                )
            )

    @classmethod
    def _validar_verbas(
        cls,
        entrada: EntradaCasoTrabalhista,
        achados: list[AchadoValidacao],
    ) -> None:
        for indice, verba in enumerate(
            entrada.sentenca.verbas_deferidas,
            start=1,
        ):
            codigo = verba.codigo.upper()
            parametros = verba.parametros
            prefixo = f"VERBA-{indice:03d}"

            if not verba.fundamento and not parametros.fundamento:
                achados.append(
                    AchadoValidacao(
                        codigo=f"{prefixo}-FUNDAMENTO",
                        nivel=NivelValidacao.ALERTA,
                        campo=f"verbas[{indice - 1}].fundamento",
                        mensagem=(
                            f"A verba {codigo} não possui fundamento "
                            "registrado."
                        ),
                    )
                )

            if codigo == "DECIMO_TERCEIRO":
                if parametros.avos is None:
                    cls._erro_parametro(
                        achados,
                        f"{prefixo}-AVOS",
                        indice,
                        "avos",
                        "O 13º salário exige a quantidade de avos.",
                    )

            elif codigo == "FERIAS":
                if parametros.avos is None:
                    cls._erro_parametro(
                        achados,
                        f"{prefixo}-AVOS",
                        indice,
                        "avos",
                        "Férias exigem a quantidade de avos.",
                    )

                if parametros.percentual is None:
                    cls._erro_parametro(
                        achados,
                        f"{prefixo}-TERCO",
                        indice,
                        "percentual",
                        (
                            "Férias exigem o percentual do "
                            "terço constitucional."
                        ),
                    )

            elif codigo == "HORA_EXTRA":
                percentual = (
                    parametros.percentual
                    if parametros.percentual is not None
                    else entrada.parametros.percentual_horas_extras
                )

                quantidade = (
                    parametros.quantidade
                    if parametros.quantidade is not None
                    else verba.quantidade
                )

                if percentual is None:
                    cls._erro_parametro(
                        achados,
                        f"{prefixo}-PERCENTUAL",
                        indice,
                        "percentual",
                        (
                            "Horas extras exigem o percentual "
                            "do adicional."
                        ),
                    )

                if quantidade is None:
                    cls._erro_parametro(
                        achados,
                        f"{prefixo}-QUANTIDADE",
                        indice,
                        "quantidade",
                        (
                            "Horas extras exigem a quantidade "
                            "a ser apurada."
                        ),
                    )

                divisor = (
                    parametros.divisor
                    if parametros.divisor is not None
                    else entrada.parametros.divisor_horas
                )

                if divisor is None:
                    cls._erro_parametro(
                        achados,
                        f"{prefixo}-DIVISOR",
                        indice,
                        "divisor",
                        "Horas extras exigem divisor de jornada.",
                    )

            elif codigo == "DSR":
                if parametros.dias_uteis is None:
                    cls._erro_parametro(
                        achados,
                        f"{prefixo}-DIAS-UTEIS",
                        indice,
                        "dias_uteis",
                        "DSR exige a quantidade de dias úteis.",
                    )

                if parametros.dias_repouso is None:
                    cls._erro_parametro(
                        achados,
                        f"{prefixo}-REPOUSOS",
                        indice,
                        "dias_repouso",
                        "DSR exige a quantidade de dias de repouso.",
                    )

            elif codigo == "FGTS":
                percentual = (
                    parametros.percentual
                    if parametros.percentual is not None
                    else verba.percentual
                )

                if percentual is None:
                    cls._erro_parametro(
                        achados,
                        f"{prefixo}-ALIQUOTA",
                        indice,
                        "percentual",
                        "FGTS exige a alíquota aplicável.",
                    )

            elif codigo == "AVISO_PREVIO":
                if parametros.dias_aviso is None:
                    cls._erro_parametro(
                        achados,
                        f"{prefixo}-DIAS",
                        indice,
                        "dias_aviso",
                        (
                            "Aviso-prévio exige a quantidade "
                            "de dias."
                        ),
                    )

                if parametros.dias_mes_calculo is None:
                    cls._erro_parametro(
                        achados,
                        f"{prefixo}-MES",
                        indice,
                        "dias_mes_calculo",
                        (
                            "Aviso-prévio exige os dias do mês "
                            "utilizados no cálculo."
                        ),
                    )

    @staticmethod
    def _erro_parametro(
        achados: list[AchadoValidacao],
        codigo: str,
        indice: int,
        campo: str,
        mensagem: str,
    ) -> None:
        achados.append(
            AchadoValidacao(
                codigo=codigo,
                nivel=NivelValidacao.ERRO,
                campo=f"verbas[{indice - 1}].parametros.{campo}",
                mensagem=mensagem,
            )
        )

    @staticmethod
    def _validar_premissas(
        entrada: EntradaCasoTrabalhista,
        achados: list[AchadoValidacao],
    ) -> None:
        if entrada.premissas:
            achados.append(
                AchadoValidacao(
                    codigo="PREMISSA-001",
                    nivel=NivelValidacao.INFORMACAO,
                    campo="premissas",
                    mensagem=(
                        f"O caso possui {len(entrada.premissas)} "
                        "premissa(s) técnica(s) registrada(s)."
                    ),
                )
            )
