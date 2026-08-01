from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from sgm.dominio.trabalhista.relatorios.observacao_tecnica import (
    ObservacaoTecnica,
)
from sgm.dominio.trabalhista.relatorios.secao_memoria import SecaoMemoria


@dataclass(frozen=True, slots=True)
class MemoriaCalculoProfissional:
    titulo: str
    referencia: str
    secoes: tuple[SecaoMemoria, ...]
    observacoes: tuple[ObservacaoTecnica, ...]
    versao_documento: str = "0.9.2-A"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        titulo = self.titulo.strip()
        referencia = self.referencia.strip()
        object.__setattr__(self, "titulo", titulo)
        object.__setattr__(self, "referencia", referencia)

        if not titulo:
            raise ValueError("O título da memória é obrigatório.")

        if not referencia:
            raise ValueError(
                "A referência da memória é obrigatória."
            )

        if not self.secoes:
            raise ValueError(
                "A memória profissional deve conter seções."
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

    def como_texto(self) -> str:
        linhas = [
            self.titulo,
            f"Referência: {self.referencia}",
            f"Versão documental: {self.versao_documento}",
        ]

        for secao in self.secoes:
            linhas.extend(("", f"{secao.ordem}. {secao.titulo}"))

            for item in secao.itens:
                linha = f"{item.rotulo}: {item.valor}"
                if item.formula_codigo:
                    linha += f" | Fórmula: {item.formula_codigo}"
                if item.fundamento:
                    linha += f" | Fundamento: {item.fundamento}"
                linhas.append(linha)

            for tabela in secao.tabelas:
                linhas.append(f"Tabela: {tabela.titulo}")
                for linha_tabela in tabela.linhas:
                    linhas.append(
                        f"{linha_tabela.chave} | "
                        f"{linha_tabela.descricao} | "
                        f"{linha_tabela.valor.moeda} "
                        f"{format(linha_tabela.valor.valor, 'f')}"
                    )
                linhas.append(
                    f"TOTAL | {tabela.total.moeda} "
                    f"{format(tabela.total.valor, 'f')}"
                )

        if self.observacoes:
            linhas.extend(("", "OBSERVAÇÕES TÉCNICAS"))
            for observacao in self.observacoes:
                linhas.append(
                    f"[{observacao.nivel.value}] "
                    f"{observacao.texto}"
                )

        return "\n".join(linhas)
