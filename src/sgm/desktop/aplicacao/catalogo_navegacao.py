from __future__ import annotations

from sgm.desktop.aplicacao.modelo_item_navegacao import (
    ItemNavegacao,
)
from sgm.desktop.aplicacao.secao_desktop import SecaoDesktop


def criar_catalogo_navegacao() -> tuple[ItemNavegacao, ...]:
    descricoes = {
        SecaoDesktop.INICIO: "Visão geral do caso trabalhista.",
        SecaoDesktop.PROCESSO: "Juízo, processo e partes.",
        SecaoDesktop.CONTRATO: "Dados do vínculo e da jornada.",
        SecaoDesktop.EVENTOS: "Alterações na linha do tempo contratual.",
        SecaoDesktop.CALCULO: "Parâmetros e execução dos cálculos.",
        SecaoDesktop.MEMORIA: "Memória detalhada e auditável.",
        SecaoDesktop.RELATORIO: "Relatório técnico final.",
        SecaoDesktop.EXPORTACAO: "Arquivos TXT, MD, HTML, PDF e DOCX.",
        SecaoDesktop.IA: (
            "Importação inteligente de processos e apoio por IA."
        ),
    }
    return tuple(
        ItemNavegacao(
            secao=secao,
            rotulo=secao.titulo,
            descricao=descricoes[secao],
        )
        for secao in SecaoDesktop
    )
