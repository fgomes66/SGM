from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.trabalhista.cronologia_profissional import (
    LinhaTempoProfissional,
)
from sgm.dominio.trabalhista.demonstrativos import (
    DemonstrativoFinanceiroProfissional,
)
from sgm.dominio.trabalhista.relatorios import (
    MemoriaCalculoProfissional,
)


@dataclass(frozen=True, slots=True)
class DocumentoExportavel:
    referencia: str
    memoria: MemoriaCalculoProfissional
    demonstrativo: DemonstrativoFinanceiroProfissional
    linha_tempo: LinhaTempoProfissional

    def __post_init__(self) -> None:
        referencia = self.referencia.strip()
        object.__setattr__(self, "referencia", referencia)

        if not referencia:
            raise ValueError(
                "A referência do documento exportável é obrigatória."
            )

        referencias = {
            self.memoria.referencia,
            self.demonstrativo.referencia,
            self.linha_tempo.referencia,
            referencia,
        }
        if len(referencias) != 1:
            raise ValueError(
                "Todos os componentes devem possuir a mesma referência."
            )

    def texto_integral(self) -> str:
        return "\n\n".join(
            (
                self.memoria.como_texto(),
                self.demonstrativo.como_texto(),
                self.linha_tempo.como_texto(),
            )
        )
