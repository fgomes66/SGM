from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.cronologia_profissional.marco_temporal import (
    MarcoTemporal,
)
from sgm.dominio.trabalhista.cronologia_profissional.periodo_vigencia_profissional import PeriodoVigenciaProfissional
from sgm.dominio.trabalhista.temporal import PeriodoContratual


@dataclass(frozen=True, slots=True)
class LinhaTempoProfissional:
    referencia: str
    periodo: PeriodoContratual
    marcos: tuple[MarcoTemporal, ...]
    vigencias: tuple[PeriodoVigenciaProfissional, ...]
    versao_documento: str = "0.9.2-C"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        referencia = self.referencia.strip()
        object.__setattr__(self, "referencia", referencia)

        if not referencia:
            raise ValueError(
                "A referência da linha do tempo é obrigatória."
            )

        if not self.marcos:
            raise ValueError(
                "A linha do tempo deve conter marcos."
            )

        if not self.vigencias:
            raise ValueError(
                "A linha do tempo deve conter vigências."
            )

        chaves_marcos = tuple(
            (marco.competencia, marco.ordem_na_competencia)
            for marco in self.marcos
        )
        if tuple(sorted(chaves_marcos)) != chaves_marcos:
            raise ValueError(
                "Os marcos devem estar em ordem cronológica."
            )

        inicios_vigencias = tuple(
            vigencia.inicio for vigencia in self.vigencias
        )
        if tuple(sorted(inicios_vigencias)) != inicios_vigencias:
            raise ValueError(
                "As vigências devem estar em ordem cronológica."
            )

    def como_texto(self) -> str:
        linhas = [
            "LINHA DO TEMPO PROFISSIONAL — SGM",
            f"Referência: {self.referencia}",
            (
                "Período: "
                f"{self.periodo.inicio.como_texto()} a "
                f"{self.periodo.fim.como_texto()}"
            ),
            f"Versão documental: {self.versao_documento}",
            "",
            "MARCOS CONTRATUAIS",
        ]

        for marco in self.marcos:
            linhas.append(
                f"{marco.competencia.como_texto()} | "
                f"{marco.tipo.value} | "
                f"{marco.titulo} | "
                f"{marco.descricao} | "
                f"Fundamento: {marco.fundamento}"
            )

        linhas.extend(("", "PERÍODOS DE VIGÊNCIA"))

        for vigencia in self.vigencias:
            linhas.append(
                f"{vigencia.inicio.como_texto()} a "
                f"{vigencia.fim.como_texto()} | "
                f"salário={format(vigencia.salario, 'f')} | "
                f"divisor={format(vigencia.divisor, 'f')} | "
                f"jornada={vigencia.jornada_semanal_minutos} | "
                f"estado={vigencia.descricao_estado}"
            )

        return "\n".join(linhas)
