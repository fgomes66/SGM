from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from uuid import UUID

from sgm.desktop.aplicacao.evento_contratual_desktop import (
    EventoContratualDesktop,
    TipoEventoDesktop,
)


@dataclass(frozen=True, slots=True)
class DadosEventoFormulario:
    tipo: str = TipoEventoDesktop.ALTERACAO_SALARIAL.value
    data_inicio: str = ""
    data_fim: str = ""
    descricao: str = ""
    fundamento: str = ""
    valor: str = ""
    documento: str = ""
    detalhes: str = ""
    id: str = ""

    def __post_init__(self) -> None:
        for campo in self.__dataclass_fields__:
            valor = getattr(self, campo)
            object.__setattr__(self, campo, valor.strip())

    @staticmethod
    def _data(texto: str, obrigatoria: bool) -> date | None:
        if not texto:
            if obrigatoria:
                raise ValueError("Informe a data inicial.")
            return None
        try:
            return date.fromisoformat(texto)
        except ValueError as erro:
            raise ValueError("Use datas no formato AAAA-MM-DD.") from erro

    @staticmethod
    def _valor(texto: str) -> Decimal | None:
        if not texto:
            return None
        try:
            valor = Decimal(texto.replace(".", "").replace(",", "."))
        except InvalidOperation as erro:
            raise ValueError("Informe um valor monetário válido.") from erro
        return valor

    def criar_evento(self) -> EventoContratualDesktop:
        try:
            tipo = TipoEventoDesktop(self.tipo)
        except ValueError as erro:
            raise ValueError("Selecione um tipo de evento válido.") from erro

        dados = {}
        for linha in self.detalhes.splitlines():
            if "=" in linha:
                chave, valor = linha.split("=", 1)
                if chave.strip() and valor.strip():
                    dados[chave.strip()] = valor.strip()

        identificador = UUID(self.id) if self.id else None
        kwargs = {}
        if identificador is not None:
            kwargs["id"] = identificador

        return EventoContratualDesktop(
            tipo=tipo,
            data_inicio=self._data(self.data_inicio, True),
            data_fim=self._data(self.data_fim, False),
            descricao=self.descricao,
            fundamento=self.fundamento,
            valor=self._valor(self.valor),
            documento=self.documento or None,
            dados=dados,
            **kwargs,
        )

    def validar(self) -> tuple[str, ...]:
        try:
            self.criar_evento()
        except (TypeError, ValueError) as erro:
            return (str(erro),)
        return ()
