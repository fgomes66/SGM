from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
import hashlib
import json
from uuid import UUID, uuid4

from sgm.dominio.calculos.enums import StatusPlanoCalculo
from sgm.dominio.calculos.item_plano_calculo import ItemPlanoCalculo
from sgm.dominio.juridico.modelos.criterio_juridico import CriterioJuridico


@dataclass(slots=True)
class PlanoCalculo:
    processo_id: UUID
    nome: str
    data_base: date
    criado_por: str
    status: StatusPlanoCalculo = StatusPlanoCalculo.RASCUNHO
    itens: list[ItemPlanoCalculo] = field(default_factory=list)
    observacoes: str | None = None
    homologado_por: str | None = None
    homologado_em: datetime | None = None
    hash_homologacao: str | None = None
    id: UUID = field(default_factory=uuid4)
    versao: int = 1

    def __post_init__(self) -> None:
        self.nome = self.nome.strip()
        self.criado_por = self.criado_por.strip()

        if not self.nome:
            raise ValueError("O nome do plano é obrigatório.")
        if not self.criado_por:
            raise ValueError("O autor do plano é obrigatório.")
        if self.versao < 1:
            raise ValueError("A versão deve ser igual ou superior a 1.")

    @property
    def esta_homologado(self) -> bool:
        return self.status == StatusPlanoCalculo.HOMOLOGADO

    def adicionar_item(
        self,
        item: ItemPlanoCalculo,
        criterio: CriterioJuridico,
    ) -> None:
        self._garantir_editavel()
        criterio.garantir_apto_para_calculo()

        if item.criterio_juridico_id != criterio.id:
            raise ValueError(
                "O item não está vinculado ao critério jurídico informado."
            )

        if any(existente.codigo == item.codigo for existente in self.itens):
            raise ValueError(f"Já existe item com o código {item.codigo}.")

        self.itens.append(item)
        self.versao += 1
        self.hash_homologacao = None

    def remover_item(self, codigo: str) -> None:
        self._garantir_editavel()
        codigo = codigo.strip()
        quantidade_anterior = len(self.itens)
        self.itens = [item for item in self.itens if item.codigo != codigo]

        if len(self.itens) == quantidade_anterior:
            raise KeyError(f"Item não encontrado: {codigo}.")

        self.versao += 1
        self.hash_homologacao = None

    def enviar_para_revisao(self) -> None:
        self._garantir_editavel()
        if not self.itens:
            raise ValueError("Plano sem itens não pode ser enviado para revisão.")
        self.status = StatusPlanoCalculo.EM_REVISAO
        self.versao += 1

    def homologar(
        self,
        responsavel: str,
        momento: datetime | None = None,
    ) -> None:
        responsavel = responsavel.strip()

        if not responsavel:
            raise ValueError("O responsável pela homologação é obrigatório.")
        if self.status != StatusPlanoCalculo.EM_REVISAO:
            raise ValueError(
                "Somente plano em revisão pode ser homologado."
            )
        if not self.itens:
            raise ValueError("Plano sem itens não pode ser homologado.")

        self.homologado_por = responsavel
        self.homologado_em = momento or datetime.now().astimezone()
        self.status = StatusPlanoCalculo.HOMOLOGADO
        self.versao += 1
        self.hash_homologacao = self._calcular_hash()

    def garantir_apto_para_execucao(self) -> None:
        if not self.esta_homologado:
            raise ValueError(
                "O plano precisa estar homologado antes da execução."
            )
        if not self.hash_homologacao:
            raise ValueError("O plano homologado não possui hash de integridade.")
        if self.hash_homologacao != self._calcular_hash():
            raise ValueError(
                "A integridade do plano homologado não pôde ser confirmada."
            )

    def _garantir_editavel(self) -> None:
        if self.status in {
            StatusPlanoCalculo.HOMOLOGADO,
            StatusPlanoCalculo.SUSPENSO,
            StatusPlanoCalculo.SUBSTITUIDO,
        }:
            raise ValueError(
                "Plano homologado, suspenso ou substituído não pode ser editado."
            )

    def _calcular_hash(self) -> str:
        dados = {
            "id": str(self.id),
            "processo_id": str(self.processo_id),
            "nome": self.nome,
            "data_base": self.data_base.isoformat(),
            "criado_por": self.criado_por,
            "versao": self.versao,
            "homologado_por": self.homologado_por,
            "homologado_em": (
                self.homologado_em.isoformat()
                if self.homologado_em is not None
                else None
            ),
            "itens": [
                {
                    "id": str(item.id),
                    "codigo": item.codigo,
                    "verba_codigo": item.verba_codigo,
                    "criterio_juridico_id": str(item.criterio_juridico_id),
                    "natureza": item.natureza.value,
                    "descricao": item.descricao,
                    "periodo_inicio": (
                        item.periodo_inicio.isoformat()
                        if item.periodo_inicio is not None
                        else None
                    ),
                    "periodo_fim": (
                        item.periodo_fim.isoformat()
                        if item.periodo_fim is not None
                        else None
                    ),
                    "base_calculo": item.base_calculo,
                    "percentual": (
                        str(item.percentual)
                        if item.percentual is not None
                        else None
                    ),
                    "divisor": (
                        str(item.divisor)
                        if item.divisor is not None
                        else None
                    ),
                    "reflexos": list(item.reflexos),
                    "incidencias": list(item.incidencias),
                    "deducoes": list(item.deducoes),
                    "observacoes": item.observacoes,
                }
                for item in self.itens
            ],
        }
        serializado = json.dumps(
            dados,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return hashlib.sha256(serializado.encode("utf-8")).hexdigest()
