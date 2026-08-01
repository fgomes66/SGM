from enum import StrEnum


class TipoBaseIncidencia(StrEnum):
    FGTS = "FGTS"
    FERIAS = "FERIAS"
    DECIMO_TERCEIRO = "DECIMO_TERCEIRO"
    AVISO_PREVIO = "AVISO_PREVIO"
    INSS = "INSS"
    IRRF = "IRRF"
