from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.cronologia_profissional import (
    LinhaTempoProfissional,
)
from sgm.dominio.trabalhista.demonstrativos import (
    DemonstrativoFinanceiroProfissional,
)
from sgm.dominio.trabalhista.relatorios import (
    MemoriaCalculoProfissional,
)
from sgm.relatorio.identificacao_processo import IdentificacaoProcesso
from sgm.relatorio.metadados_relatorio import MetadadosRelatorio
from sgm.relatorio.parametros_relatorio import ParametrosRelatorio
from sgm.relatorio.tipo_relatorio import TipoRelatorio


@dataclass(frozen=True, slots=True)
class RelatorioTecnico:
    tipo: TipoRelatorio
    identificacao: IdentificacaoProcesso
    metadados: MetadadosRelatorio
    parametros: ParametrosRelatorio
    memoria: MemoriaCalculoProfissional
    demonstrativo: DemonstrativoFinanceiroProfissional
    linha_tempo: LinhaTempoProfissional
    titulo: str = "RELATÓRIO TÉCNICO DE CÁLCULOS TRABALHISTAS"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        titulo = self.titulo.strip()
        object.__setattr__(self, "titulo", titulo)

        if not titulo:
            raise ValueError(
                "O título do relatório é obrigatório."
            )

        referencias = {
            self.memoria.referencia,
            self.demonstrativo.referencia,
            self.linha_tempo.referencia,
        }
        if len(referencias) != 1:
            raise ValueError(
                "Memória, demonstrativo e linha do tempo devem "
                "possuir a mesma referência."
            )

        if (
            self.metadados.quantidade_competencias
            != len(self.demonstrativo.competencias)
        ):
            raise ValueError(
                "A quantidade de competências dos metadados diverge "
                "do demonstrativo."
            )

        if (
            self.metadados.quantidade_verbas
            != len(self.demonstrativo.verbas)
        ):
            raise ValueError(
                "A quantidade de verbas dos metadados diverge "
                "do demonstrativo."
            )

        eventos = tuple(
            marco
            for marco in self.linha_tempo.marcos
            if marco.tipo.value not in (
                "INICIO_PERIODO",
                "FIM_PERIODO",
            )
        )
        if self.metadados.quantidade_eventos != len(eventos):
            raise ValueError(
                "A quantidade de eventos dos metadados diverge "
                "da linha do tempo."
            )

    @property
    def referencia(self) -> str:
        return self.memoria.referencia

    def resumo_identificacao(self) -> tuple[str, ...]:
        itens = [
            "PODER JUDICIÁRIO",
            "JUSTIÇA DO TRABALHO",
            self.identificacao.orgao_julgador.descricao_completa,
            f"Processo: {self.identificacao.numero_processo}",
            f"Classe: {self.identificacao.classe_processual}",
            f"Reclamante: {self.identificacao.reclamante}",
            f"Reclamada: {self.identificacao.reclamada}",
        ]

        if self.identificacao.magistrado:
            itens.append(
                f"Magistrado(a): {self.identificacao.magistrado}"
            )

        if self.identificacao.perito:
            itens.append(
                f"Perito(a): {self.identificacao.perito}"
            )

        return tuple(itens)
