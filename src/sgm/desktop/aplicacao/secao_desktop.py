from enum import StrEnum


class SecaoDesktop(StrEnum):
    INICIO = "INICIO"
    PROCESSO = "PROCESSO"
    CONTRATO = "CONTRATO"
    EVENTOS = "EVENTOS"
    CALCULO = "CALCULO"
    MEMORIA = "MEMORIA"
    RELATORIO = "RELATORIO"
    EXPORTACAO = "EXPORTACAO"

    @property
    def titulo(self) -> str:
        return {
            SecaoDesktop.INICIO: "Início",
            SecaoDesktop.PROCESSO: "Processo",
            SecaoDesktop.CONTRATO: "Contrato de Trabalho",
            SecaoDesktop.EVENTOS: "Eventos Contratuais",
            SecaoDesktop.CALCULO: "Cálculo",
            SecaoDesktop.MEMORIA: "Memória de Cálculo",
            SecaoDesktop.RELATORIO: "Relatório Técnico",
            SecaoDesktop.EXPORTACAO: "Exportação",
        }[self]
