from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from sgm.desktop.aplicacao.contrato_trabalho import ContratoTrabalho, TipoContratoTrabalho

@dataclass(frozen=True, slots=True)
class DadosContratoFormulario:
    data_admissao: str = ""
    data_desligamento: str = ""
    tipo_contrato: str = TipoContratoTrabalho.INDETERMINADO.value
    cargo: str = ""
    funcao: str = ""
    cbo: str = ""
    salario_inicial: str = ""
    jornada_semanal_horas: str = "44"
    divisor_jornada: str = "220"
    motivo_desligamento: str = ""
    sindicato: str = ""
    norma_coletiva: str = ""
    observacoes: str = ""

    def __post_init__(self):
        for campo in self.__dataclass_fields__:
            object.__setattr__(self,campo,getattr(self,campo).strip())

    @staticmethod
    def _data(texto: str, obrigatoria: bool=True):
        if not texto:
            if obrigatoria: raise ValueError("Informe a data de admissão.")
            return None
        try: return date.fromisoformat(texto)
        except ValueError as exc: raise ValueError("Use datas no formato AAAA-MM-DD.") from exc

    @staticmethod
    def _decimal(texto: str, nome: str) -> Decimal:
        try: return Decimal(texto.replace('.','').replace(',','.')) if ',' in texto else Decimal(texto)
        except (InvalidOperation, ValueError) as exc: raise ValueError(f"Informe {nome} válido.") from exc

    def criar_contrato(self) -> ContratoTrabalho:
        try: tipo=TipoContratoTrabalho(self.tipo_contrato)
        except ValueError as exc: raise ValueError("Selecione um tipo de contrato válido.") from exc
        return ContratoTrabalho(
            data_admissao=self._data(self.data_admissao),
            data_desligamento=self._data(self.data_desligamento, False),
            tipo_contrato=tipo, cargo=self.cargo, funcao=self.funcao, cbo=self.cbo or None,
            salario_inicial=self._decimal(self.salario_inicial,'um salário inicial'),
            jornada_semanal_horas=self._decimal(self.jornada_semanal_horas,'uma jornada semanal'),
            divisor_jornada=self._decimal(self.divisor_jornada,'um divisor de jornada'),
            motivo_desligamento=self.motivo_desligamento or None, sindicato=self.sindicato or None,
            norma_coletiva=self.norma_coletiva or None, observacoes=self.observacoes or None,
        )

    def validar(self) -> tuple[str,...]:
        erros=[]
        try: self.criar_contrato()
        except (TypeError,ValueError) as exc: erros.append(str(exc))
        return tuple(erros)
