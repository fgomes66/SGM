from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4
import re
from sgm.dominio.processos.enums import FaseProcessual, StatusProcesso

_PADRAO_CNJ = re.compile(
    r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$"
)

@dataclass(slots=True)
class ProcessoTrabalhista:
    identificador_interno: str
    tribunal: str
    fase_processual: FaseProcessual
    status: StatusProcesso
    data_recebimento: date
    numero_cnj: str | None = None
    vara: str | None = None
    municipio: str | None = None
    uf: str | None = None
    prazo: date | None = None
    data_distribuicao: date | None = None
    data_ajuizamento: date | None = None
    data_sentenca: date | None = None
    data_transito_julgado: date | None = None
    data_liquidacao: date | None = None
    data_base: date | None = None
    observacoes: str | None = None
    id: UUID = field(default_factory=uuid4)
    versao: int = 1

    def __post_init__(self) -> None:
        self.identificador_interno = self.identificador_interno.strip()
        self.tribunal = self.tribunal.strip().upper()
        if not self.identificador_interno:
            raise ValueError("O identificador interno é obrigatório.")
        if not self.tribunal:
            raise ValueError("O tribunal é obrigatório.")
        if self.versao < 1:
            raise ValueError("A versão deve ser igual ou superior a 1.")
        if self.uf is not None:
            self.uf = self.uf.strip().upper()
            if len(self.uf) != 2 or not self.uf.isalpha():
                raise ValueError("A UF deve conter exatamente duas letras.")
        if self.numero_cnj is not None:
            self.numero_cnj = self.numero_cnj.strip()
            if not _PADRAO_CNJ.fullmatch(self.numero_cnj):
                raise ValueError("Número CNJ em formato inválido.")
        self._validar_coerencia_temporal()

    def _validar_coerencia_temporal(self) -> None:
        if self.data_distribuicao and self.data_ajuizamento and self.data_distribuicao < self.data_ajuizamento:
            raise ValueError("A distribuição não pode anteceder o ajuizamento.")
        if self.data_sentenca and self.data_ajuizamento and self.data_sentenca < self.data_ajuizamento:
            raise ValueError("A sentença não pode anteceder o ajuizamento.")
        if self.data_transito_julgado and self.data_sentenca and self.data_transito_julgado < self.data_sentenca:
            raise ValueError("O trânsito em julgado não pode anteceder a sentença.")
        if self.data_liquidacao and self.data_transito_julgado and self.data_liquidacao < self.data_transito_julgado:
            raise ValueError("A liquidação não pode anteceder o trânsito em julgado.")

    @property
    def possui_numero_cnj(self) -> bool:
        return self.numero_cnj is not None

    @property
    def esta_encerrado(self) -> bool:
        return self.status in {StatusProcesso.ENCERRADO, StatusProcesso.ARQUIVADO}

    def alterar_status(self, novo_status: StatusProcesso) -> None:
        if self.esta_encerrado:
            raise ValueError("Processo encerrado ou arquivado não pode mudar de status.")
        if novo_status != self.status:
            self.status = novo_status
            self.versao += 1

    def definir_data_base(self, data_base: date) -> None:
        if data_base < self.data_recebimento:
            raise ValueError("A data-base não pode anteceder o recebimento do processo.")
        self.data_base = data_base
        self.versao += 1
