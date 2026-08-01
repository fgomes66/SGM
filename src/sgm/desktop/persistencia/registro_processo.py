from __future__ import annotations

from dataclasses import dataclass

from sgm.relatorio import IdentificacaoProcesso
from sgm.desktop.aplicacao.calculo_desktop import ResultadoCalculoDesktop
from sgm.desktop.aplicacao.contrato_trabalho import ContratoTrabalho
from sgm.desktop.aplicacao.evento_contratual_desktop import EventoContratualDesktop


@dataclass(frozen=True, slots=True)
class RegistroProcesso:
    referencia: str
    identificacao: IdentificacaoProcesso
    contrato: ContratoTrabalho | None = None
    eventos: tuple[EventoContratualDesktop, ...] = ()
    calculos: tuple[ResultadoCalculoDesktop, ...] = ()

    def __post_init__(self) -> None:
        referencia = self.referencia.strip()
        object.__setattr__(self, "referencia", referencia)

        if not referencia:
            raise ValueError(
                "A referência interna do processo é obrigatória."
            )

        if not isinstance(
            self.identificacao,
            IdentificacaoProcesso,
        ):
            raise TypeError(
                "A identificação deve ser IdentificacaoProcesso."
            )

        if not isinstance(self.eventos, tuple) or any(
            not isinstance(item, EventoContratualDesktop)
            for item in self.eventos
        ):
            raise TypeError("Os eventos do registro são inválidos.")


        if not isinstance(self.calculos, tuple) or any(
            not isinstance(item, ResultadoCalculoDesktop)
            for item in self.calculos
        ):
            raise TypeError(
                "Os resultados de cálculo do registro são inválidos."
            )
        object.__setattr__(
            self,
            "calculos",
            tuple(
                sorted(
                    self.calculos,
                    key=lambda item: (
                        item.competencia,
                        str(item.id),
                    ),
                )
            ),
        )

        object.__setattr__(
            self,
            "eventos",
            tuple(sorted(self.eventos, key=lambda item: item.chave_ordenacao)),
        )
