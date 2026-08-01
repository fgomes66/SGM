from __future__ import annotations

from typing import Any

from sgm.desktop.persistencia.registro_processo import (
    RegistroProcesso,
)
from decimal import Decimal
from datetime import date
from uuid import UUID
from sgm.relatorio import IdentificacaoProcesso, OrgaoJulgador
from sgm.desktop.aplicacao.calculo_desktop import ResultadoCalculoDesktop
from sgm.desktop.aplicacao.contrato_trabalho import ContratoTrabalho, TipoContratoTrabalho
from sgm.desktop.aplicacao.evento_contratual_desktop import (
    EventoContratualDesktop,
    TipoEventoDesktop,
)


class SerializadorProcesso:
    VERSAO_SCHEMA = 1

    @classmethod
    def para_dict(
        cls,
        registro: RegistroProcesso,
    ) -> dict[str, Any]:
        identificacao = registro.identificacao
        orgao = identificacao.orgao_julgador

        return {
            "schema": cls.VERSAO_SCHEMA,
            "referencia": registro.referencia,
            "contrato": cls._contrato_para_dict(registro.contrato),
            "eventos": [
                cls._evento_para_dict(item)
                for item in registro.eventos
            ],
            "calculos": [
                cls._calculo_para_dict(item)
                for item in registro.calculos
            ],
            "identificacao": {
                "orgao_julgador": {
                    "tribunal": orgao.tribunal,
                    "regiao_trt": orgao.regiao_trt,
                    "vara": orgao.vara,
                    "municipio": orgao.municipio,
                    "uf": orgao.uf,
                },
                "numero_processo": identificacao.numero_processo,
                "classe_processual": identificacao.classe_processual,
                "reclamante": identificacao.reclamante,
                "reclamada": identificacao.reclamada,
                "magistrado": identificacao.magistrado,
                "perito": identificacao.perito,
                "assistente_reclamante": (
                    identificacao.assistente_reclamante
                ),
                "assistente_reclamada": (
                    identificacao.assistente_reclamada
                ),
                "advogado_reclamante": (
                    identificacao.advogado_reclamante
                ),
                "advogado_reclamada": (
                    identificacao.advogado_reclamada
                ),
            },
        }

    @staticmethod
    def _contrato_para_dict(contrato):
        if contrato is None: return None
        return {
            "data_admissao": contrato.data_admissao.isoformat(),
            "data_desligamento": contrato.data_desligamento.isoformat() if contrato.data_desligamento else None,
            "tipo_contrato": contrato.tipo_contrato.value, "cargo": contrato.cargo, "funcao": contrato.funcao,
            "cbo": contrato.cbo, "salario_inicial": str(contrato.salario_inicial),
            "jornada_semanal_horas": str(contrato.jornada_semanal_horas), "divisor_jornada": str(contrato.divisor_jornada),
            "motivo_desligamento": contrato.motivo_desligamento, "sindicato": contrato.sindicato,
            "norma_coletiva": contrato.norma_coletiva, "observacoes": contrato.observacoes,
        }

    @staticmethod
    def _contrato_de_dict(dados):
        if not dados: return None
        return ContratoTrabalho(
            data_admissao=date.fromisoformat(dados["data_admissao"]),
            data_desligamento=date.fromisoformat(dados["data_desligamento"]) if dados.get("data_desligamento") else None,
            tipo_contrato=TipoContratoTrabalho(dados["tipo_contrato"]), cargo=dados["cargo"], funcao=dados["funcao"],
            cbo=dados.get("cbo"), salario_inicial=Decimal(dados["salario_inicial"]),
            jornada_semanal_horas=Decimal(dados["jornada_semanal_horas"]), divisor_jornada=Decimal(dados["divisor_jornada"]),
            motivo_desligamento=dados.get("motivo_desligamento"), sindicato=dados.get("sindicato"),
            norma_coletiva=dados.get("norma_coletiva"), observacoes=dados.get("observacoes"),
        )


    @staticmethod
    def _evento_para_dict(evento: EventoContratualDesktop) -> dict[str, Any]:
        return {
            "id": str(evento.id),
            "tipo": evento.tipo.value,
            "data_inicio": evento.data_inicio.isoformat(),
            "data_fim": evento.data_fim.isoformat() if evento.data_fim else None,
            "descricao": evento.descricao,
            "fundamento": evento.fundamento,
            "valor": str(evento.valor) if evento.valor is not None else None,
            "documento": evento.documento,
            "dados": dict(evento.dados),
        }

    @staticmethod
    def _evento_de_dict(dados: dict[str, Any]) -> EventoContratualDesktop:
        return EventoContratualDesktop(
            id=UUID(dados["id"]),
            tipo=TipoEventoDesktop(dados["tipo"]),
            data_inicio=date.fromisoformat(dados["data_inicio"]),
            data_fim=(
                date.fromisoformat(dados["data_fim"])
                if dados.get("data_fim")
                else None
            ),
            descricao=dados["descricao"],
            fundamento=dados["fundamento"],
            valor=Decimal(dados["valor"]) if dados.get("valor") else None,
            documento=dados.get("documento"),
            dados=dados.get("dados", {}),
        )


    @staticmethod
    def _calculo_para_dict(
        item: ResultadoCalculoDesktop,
    ) -> dict[str, Any]:
        return {
            "id": str(item.id),
            "competencia": item.competencia.isoformat(),
            "salario_base": str(item.salario_base),
            "divisor": str(item.divisor),
            "quantidade_horas": str(item.quantidade_horas),
            "adicional_percentual": str(
                item.adicional_percentual
            ),
            "valor_hora": str(item.valor_hora),
            "valor_hora_com_adicional": str(
                item.valor_hora_com_adicional
            ),
            "valor_total": str(item.valor_total),
            "fundamento": item.fundamento,
            "formula_codigo": item.formula_codigo,
        }

    @staticmethod
    def _calculo_de_dict(
        dados: dict[str, Any],
    ) -> ResultadoCalculoDesktop:
        return ResultadoCalculoDesktop(
            id=UUID(dados["id"]),
            competencia=date.fromisoformat(dados["competencia"]),
            salario_base=Decimal(dados["salario_base"]),
            divisor=Decimal(dados["divisor"]),
            quantidade_horas=Decimal(
                dados["quantidade_horas"]
            ),
            adicional_percentual=Decimal(
                dados["adicional_percentual"]
            ),
            valor_hora=Decimal(dados["valor_hora"]),
            valor_hora_com_adicional=Decimal(
                dados["valor_hora_com_adicional"]
            ),
            valor_total=Decimal(dados["valor_total"]),
            fundamento=dados["fundamento"],
            formula_codigo=dados["formula_codigo"],
        )

    @classmethod
    def de_dict(
        cls,
        dados: dict[str, Any],
    ) -> RegistroProcesso:
        if dados.get("schema", 1) not in (1, cls.VERSAO_SCHEMA):
            raise ValueError(
                "Versão de arquivo de processo não suportada."
            )

        identificacao = dados["identificacao"]
        orgao_dados = identificacao["orgao_julgador"]

        orgao = OrgaoJulgador(
            tribunal=orgao_dados["tribunal"],
            regiao_trt=int(orgao_dados["regiao_trt"]),
            vara=orgao_dados["vara"],
            municipio=orgao_dados["municipio"],
            uf=orgao_dados["uf"],
        )

        objeto = IdentificacaoProcesso(
            orgao_julgador=orgao,
            numero_processo=identificacao["numero_processo"],
            classe_processual=identificacao["classe_processual"],
            reclamante=identificacao["reclamante"],
            reclamada=identificacao["reclamada"],
            magistrado=identificacao.get("magistrado"),
            perito=identificacao.get("perito"),
            assistente_reclamante=(
                identificacao.get("assistente_reclamante")
            ),
            assistente_reclamada=(
                identificacao.get("assistente_reclamada")
            ),
            advogado_reclamante=(
                identificacao.get("advogado_reclamante")
            ),
            advogado_reclamada=(
                identificacao.get("advogado_reclamada")
            ),
        )

        return RegistroProcesso(
            referencia=dados["referencia"],
            identificacao=objeto,
            contrato=cls._contrato_de_dict(dados.get("contrato")),
            eventos=tuple(
                cls._evento_de_dict(item)
                for item in dados.get("eventos", ())
            ),
            calculos=tuple(
                cls._calculo_de_dict(item)
                for item in dados.get("calculos", ())
            ),
        )
