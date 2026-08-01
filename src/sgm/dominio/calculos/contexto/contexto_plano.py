from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from sgm.dominio.calculos.contexto.cenario_estimativo import CenarioEstimativo
from sgm.dominio.calculos.contexto.enums import (
    FinalidadeCalculo,
    TipoOrigemPlano,
)


_FINALIDADES_PRE_PROCESSUAIS = {
    FinalidadeCalculo.ESTIMATIVA_PETICAO_INICIAL,
    FinalidadeCalculo.SIMULACAO_NEGOCIACAO,
    FinalidadeCalculo.ACORDO,
}

_FINALIDADES_JUDICIAIS = {
    FinalidadeCalculo.LIQUIDACAO_SENTENCA,
    FinalidadeCalculo.IMPUGNACAO_CALCULOS,
    FinalidadeCalculo.ATUALIZACAO_EXECUCAO,
}


@dataclass(slots=True)
class ContextoPlanoCalculo:
    finalidade: FinalidadeCalculo
    tipo_origem: TipoOrigemPlano
    responsavel_tecnico: str
    cenario_estimativo: CenarioEstimativo | None = None
    titulo_executivo_id: UUID | None = None
    revisado_por: str | None = None
    revisado_em: datetime | None = None
    ressalvas: tuple[str, ...] = ()
    id: UUID = field(default_factory=uuid4)
    versao: int = 1

    def __post_init__(self) -> None:
        self.responsavel_tecnico = self.responsavel_tecnico.strip()
        if not self.responsavel_tecnico:
            raise ValueError("O responsável técnico é obrigatório.")
        self._validar_coerencia_origem()

    def _validar_coerencia_origem(self) -> None:
        if self.finalidade in _FINALIDADES_PRE_PROCESSUAIS:
            if self.tipo_origem != TipoOrigemPlano.PREMISSA_PROFISSIONAL:
                raise ValueError(
                    "Finalidade estimativa exige origem em premissas profissionais."
                )
            if self.titulo_executivo_id is not None:
                raise ValueError(
                    "Plano estimativo não deve depender de título executivo."
                )

        if self.finalidade in _FINALIDADES_JUDICIAIS:
            if self.tipo_origem != TipoOrigemPlano.TITULO_EXECUTIVO:
                raise ValueError(
                    "Finalidade judicial exige origem em título executivo."
                )
            if self.titulo_executivo_id is None:
                raise ValueError(
                    "Plano judicial exige identificação do título executivo."
                )

    @property
    def natureza_estimativa(self) -> bool:
        return self.finalidade in _FINALIDADES_PRE_PROCESSUAIS

    def revisar(
        self,
        responsavel: str,
        momento: datetime | None = None,
    ) -> None:
        responsavel = responsavel.strip()
        if not responsavel:
            raise ValueError("O revisor é obrigatório.")

        if self.natureza_estimativa:
            if self.cenario_estimativo is None:
                raise ValueError(
                    "Plano estimativo exige cenário documentado."
                )
            self.cenario_estimativo.garantir_apto()

        self.revisado_por = responsavel
        self.revisado_em = momento or datetime.now().astimezone()
        self.versao += 1

    def garantir_apto_para_plano(self) -> None:
        if self.revisado_por is None or self.revisado_em is None:
            raise ValueError(
                "O contexto precisa ser revisado antes de gerar o plano."
            )
