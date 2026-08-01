from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.financeiro import ValorMonetario
from sgm.dominio.trabalhista.demonstrativos.resumo_competencia import (
    ResumoCompetencia,
)
from sgm.dominio.trabalhista.demonstrativos.resumo_natureza import (
    ResumoNatureza,
)
from sgm.dominio.trabalhista.demonstrativos.resumo_verba import (
    ResumoVerba,
)


@dataclass(frozen=True, slots=True)
class DemonstrativoFinanceiroProfissional:
    referencia: str
    competencias: tuple[ResumoCompetencia, ...]
    verbas: tuple[ResumoVerba, ...]
    naturezas: tuple[ResumoNatureza, ...]
    subtotal_geral: ValorMonetario
    valor_final_geral: ValorMonetario
    versao_documento: str = "0.9.2-B"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        referencia = self.referencia.strip()
        object.__setattr__(self, "referencia", referencia)

        if not referencia:
            raise ValueError(
                "A referência do demonstrativo é obrigatória."
            )

        if not self.competencias:
            raise ValueError(
                "O demonstrativo deve conter competências."
            )

        if not self.verbas:
            raise ValueError(
                "O demonstrativo deve conter verbas."
            )

        competencias = tuple(
            item.competencia for item in self.competencias
        )
        if tuple(sorted(competencias)) != competencias:
            raise ValueError(
                "As competências devem estar em ordem cronológica."
            )

        moedas = {
            item.subtotal.moeda for item in self.competencias
        } | {
            item.valor_final.moeda for item in self.competencias
        } | {
            item.valor.moeda for item in self.verbas
        } | {
            item.valor.moeda for item in self.naturezas
        } | {
            self.subtotal_geral.moeda,
            self.valor_final_geral.moeda,
        }

        if len(moedas) != 1:
            raise ValueError(
                "Todo o demonstrativo deve usar a mesma moeda."
            )

    def como_texto(self) -> str:
        linhas = [
            "DEMONSTRATIVO FINANCEIRO PROFISSIONAL — SGM",
            f"Referência: {self.referencia}",
            f"Versão documental: {self.versao_documento}",
            "",
            "RESUMO POR COMPETÊNCIA",
        ]

        for item in self.competencias:
            linhas.append(
                f"{item.competencia.como_texto()} | "
                f"subtotal={item.subtotal.moeda} "
                f"{format(item.subtotal.valor, 'f')} | "
                f"valor final={item.valor_final.moeda} "
                f"{format(item.valor_final.valor, 'f')} | "
                f"ativa={item.ativa}"
            )

        linhas.extend(("", "RESUMO POR VERBA"))

        for item in self.verbas:
            linhas.append(
                f"{item.codigo.value} | {item.descricao} | "
                f"{item.natureza.value} | "
                f"{item.valor.moeda} "
                f"{format(item.valor.valor, 'f')} | "
                f"competências={item.quantidade_competencias}"
            )

        linhas.extend(("", "RESUMO POR NATUREZA"))

        for item in self.naturezas:
            linhas.append(
                f"{item.natureza.value} | "
                f"{item.valor.moeda} "
                f"{format(item.valor.valor, 'f')} | "
                f"verbas={item.quantidade_verbas}"
            )

        linhas.extend(
            (
                "",
                (
                    "Subtotal geral: "
                    f"{self.subtotal_geral.moeda} "
                    f"{format(self.subtotal_geral.valor, 'f')}"
                ),
                (
                    "Valor final geral: "
                    f"{self.valor_final_geral.moeda} "
                    f"{format(self.valor_final_geral.valor, 'f')}"
                ),
            )
        )

        return "\n".join(linhas)
