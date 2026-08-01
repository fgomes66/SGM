from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.jornada import Tempo
from sgm.dominio.trabalhista.atualizacao import FatorAtualizacao
from sgm.dominio.trabalhista.aviso_previo import ParametrosAvisoPrevio
from sgm.dominio.trabalhista.decimo_terceiro import (
    ParametrosDecimoTerceiro,
)
from sgm.dominio.trabalhista.dsr import ParametrosDSR
from sgm.dominio.trabalhista.ferias import ParametrosFerias
from sgm.dominio.trabalhista.fgts import AliquotaFGTS
from sgm.dominio.trabalhista.horas_extras_financeiras import (
    AdicionalHoraExtra,
)
from sgm.dominio.trabalhista.jornada_financeira import DivisorJornada
from sgm.dominio.trabalhista.remuneracao import BaseDeCalculo
from sgm.dominio.trabalhista.liquidacao.configuracao_incidencia import (
    ConfiguracaoIncidencia,
)
from sgm.dominio.trabalhista.liquidacao.modo_liquidacao import (
    ModoLiquidacao,
)


@dataclass(frozen=True, slots=True)
class PlanoLiquidacaoIntegrada:
    processo_referencia: str
    modo: ModoLiquidacao
    base_remuneratoria: BaseDeCalculo
    divisor_jornada: DivisorJornada
    quantidade_horas_extras: Tempo
    adicional_hora_extra: AdicionalHoraExtra
    parametros_dsr: ParametrosDSR
    configuracoes_incidencia: tuple[ConfiguracaoIncidencia, ...]
    aliquota_fgts: AliquotaFGTS
    parametros_ferias: ParametrosFerias
    parametros_decimo_terceiro: ParametrosDecimoTerceiro
    parametros_aviso_previo: ParametrosAvisoPrevio
    fator_correcao: FatorAtualizacao
    fator_juros: FatorAtualizacao
    lema_memoria: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        processo = self.processo_referencia.strip()
        lema = self.lema_memoria.strip()
        object.__setattr__(self, "processo_referencia", processo)
        object.__setattr__(self, "lema_memoria", lema)

        if not processo:
            raise ValueError(
                "A referência do processo é obrigatória."
            )

        if not lema:
            raise ValueError(
                "O lema da memória de cálculo é obrigatório."
            )

        if self.quantidade_horas_extras.minutos <= 0:
            raise ValueError(
                "A liquidação integrada exige horas extras positivas."
            )
