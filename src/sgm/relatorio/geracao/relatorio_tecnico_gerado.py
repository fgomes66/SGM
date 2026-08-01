from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.relatorio.geracao.secao_relatorio import SecaoRelatorio
from sgm.relatorio.relatorio_tecnico import RelatorioTecnico


@dataclass(frozen=True, slots=True)
class RelatorioTecnicoGerado:
    relatorio: RelatorioTecnico
    secoes: tuple[SecaoRelatorio, ...]
    conteudo_base_hash: str
    versao_gerador: str = "0.9.2-E2"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        conteudo = self.conteudo_base_hash.strip()
        object.__setattr__(self, "conteudo_base_hash", conteudo)

        if not self.secoes:
            raise ValueError(
                "O relatório gerado deve possuir seções."
            )

        ordens = tuple(secao.ordem for secao in self.secoes)
        if len(set(ordens)) != len(ordens):
            raise ValueError(
                "As ordens das seções não podem ser duplicadas."
            )

        if tuple(sorted(ordens)) != ordens:
            raise ValueError(
                "As seções devem estar em ordem crescente."
            )

        if not conteudo:
            raise ValueError(
                "O conteúdo-base do hash é obrigatório."
            )

    def como_texto(self) -> str:
        blocos = [
            self.relatorio.titulo,
            f"Referência: {self.relatorio.referencia}",
            f"Versão do gerador: {self.versao_gerador}",
        ]
        blocos.extend(
            secao.como_texto() for secao in self.secoes
        )
        return "\n\n".join(blocos)
