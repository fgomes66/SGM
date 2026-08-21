from __future__ import annotations

from dataclasses import dataclass

from sgm.dominio.financeiro import ValorMonetario


@dataclass(frozen=True, slots=True)
class ResultadoItemLiquidacaoJudicial:
    """Resultado auditável de uma verba executada."""

    codigo_verba: str
    descricao: str
    valor: ValorMonetario
    memoria: tuple[str, ...]
    formula_codigo: str | None = None

    def __post_init__(self) -> None:
        codigo = self.codigo_verba.strip().upper()
        descricao = self.descricao.strip()

        if not codigo:
            raise ValueError(
                "O código da verba do resultado é obrigatório."
            )

        if not descricao:
            raise ValueError(
                "A descrição do resultado é obrigatória."
            )

        object.__setattr__(self, "codigo_verba", codigo)
        object.__setattr__(self, "descricao", descricao)
