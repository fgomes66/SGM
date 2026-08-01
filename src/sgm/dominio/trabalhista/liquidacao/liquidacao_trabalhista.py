from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.atualizacao import (
    ResultadoAtualizacaoJuros,
)
from sgm.dominio.trabalhista.aviso_previo import AvisoPrevioApurado
from sgm.dominio.trabalhista.decimo_terceiro import (
    DecimoTerceiroApurado,
)
from sgm.dominio.trabalhista.dsr import ReflexoDSR
from sgm.dominio.trabalhista.ferias import FeriasApuradas
from sgm.dominio.trabalhista.fgts import FGTSApurado
from sgm.dominio.trabalhista.horas_extras_financeiras import (
    HoraExtraFinanceira,
)
from sgm.dominio.trabalhista.incidencias import (
    ComposicaoBaseIncidencia,
)
from sgm.dominio.trabalhista.jornada_financeira import ValorHora
from sgm.dominio.trabalhista.liquidacao.memoria_calculo import (
    MemoriaCalculo,
)
from sgm.dominio.trabalhista.liquidacao.plano_liquidacao_integrada import (
    PlanoLiquidacaoIntegrada,
)
from sgm.dominio.trabalhista.liquidacao.verba_liquidada import (
    VerbaLiquidada,
)


@dataclass(frozen=True, slots=True)
class LiquidacaoTrabalhista:
    plano: PlanoLiquidacaoIntegrada
    valor_hora: ValorHora
    horas_extras: HoraExtraFinanceira
    dsr: ReflexoDSR
    base_fgts: ComposicaoBaseIncidencia
    fgts: FGTSApurado
    base_ferias: ComposicaoBaseIncidencia
    ferias: FeriasApuradas
    base_decimo_terceiro: ComposicaoBaseIncidencia
    decimo_terceiro: DecimoTerceiroApurado
    base_aviso_previo: ComposicaoBaseIncidencia
    aviso_previo: AvisoPrevioApurado
    verbas: tuple[VerbaLiquidada, ...]
    subtotal: ValorMonetario
    atualizacao: ResultadoAtualizacaoJuros
    valor_final: ValorMonetario
    memoria: MemoriaCalculo
    versao_motor: str = "0.9.0"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        moedas = {
            verba.valor.moeda
            for verba in self.verbas
        } | {
            self.subtotal.moeda,
            self.valor_final.moeda,
        }

        if len(moedas) != 1:
            raise ValueError(
                "Todas as verbas da liquidação devem usar a mesma moeda."
            )

        if not self.verbas:
            raise ValueError(
                "A liquidação deve conter ao menos uma verba."
            )

        if self.valor_final != self.atualizacao.valor_final:
            raise ValueError(
                "O valor final deve coincidir com a atualização."
            )
