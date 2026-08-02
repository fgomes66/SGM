from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import StrEnum


class IntencaoTrabalhista(StrEnum):
    RESCISAO = "RESCISAO"
    HORAS_EXTRAS = "HORAS_EXTRAS"
    FERIAS = "FERIAS"
    DECIMO_TERCEIRO = "DECIMO_TERCEIRO"
    FGTS = "FGTS"
    AVISO_PREVIO = "AVISO_PREVIO"
    DESCONHECIDA = "DESCONHECIDA"


class TipoRescisao(StrEnum):
    SEM_JUSTA_CAUSA = "SEM_JUSTA_CAUSA"
    JUSTA_CAUSA = "JUSTA_CAUSA"
    PEDIDO_DEMISSAO = "PEDIDO_DEMISSAO"
    ACORDO = "ACORDO"


@dataclass(frozen=True, slots=True)
class DadosTrabalhistasExtraidos:
    intencao: IntencaoTrabalhista
    datas: tuple[date, ...] = ()
    valores: tuple[Decimal, ...] = ()
    tipo_rescisao: TipoRescisao | None = None


class InterpretadorTrabalhista:
    """Interpreta solicitações trabalhistas sem depender de provedor externo."""

    _PADROES_INTENCAO: tuple[tuple[IntencaoTrabalhista, tuple[str, ...]], ...] = (
        (
            IntencaoTrabalhista.HORAS_EXTRAS,
            ("hora extra", "horas extras", "jornada extraordinaria", "sobrejornada"),
        ),
        (
            IntencaoTrabalhista.AVISO_PREVIO,
            ("aviso previo", "aviso indenizado", "aviso trabalhado"),
        ),
        (
            IntencaoTrabalhista.DECIMO_TERCEIRO,
            ("decimo terceiro", "13 salario", "13o salario", "gratificacao natalina"),
        ),
        (IntencaoTrabalhista.FERIAS, ("ferias", "terco constitucional")),
        (IntencaoTrabalhista.FGTS, ("fgts", "fundo de garantia", "multa de 40")),
        (
            IntencaoTrabalhista.RESCISAO,
            (
                "rescisao",
                "verbas rescisorias",
                "dispensado",
                "demitido",
                "mandado embora",
                "pedi demissao",
            ),
        ),
    )

    _PADROES_RESCISAO: tuple[tuple[TipoRescisao, tuple[str, ...]], ...] = (
        (
            TipoRescisao.SEM_JUSTA_CAUSA,
            ("sem justa causa", "dispensado", "mandado embora", "demitido sem justa"),
        ),
        (TipoRescisao.JUSTA_CAUSA, ("justa causa", "demitido por justa")),
        (TipoRescisao.PEDIDO_DEMISSAO, ("pedi demissao", "pedido de demissao")),
        (TipoRescisao.ACORDO, ("acordo 484", "acordo entre as partes", "rescisao por acordo")),
    )

    _DATA = re.compile(r"(?<!\d)(\d{1,2})[\-/\.](\d{1,2})[\-/\.](\d{4})(?!\d)")
    _VALOR = re.compile(
        r"(?:R\$\s*)?(?<!\d)(\d{1,3}(?:\.\d{3})*,\d{2}|\d+(?:,\d{2})?)(?!\d)",
        re.IGNORECASE,
    )

    def interpretar(self, texto: str) -> DadosTrabalhistasExtraidos:
        texto_limpo = texto.strip()
        if not texto_limpo:
            raise ValueError("O texto para interpretação não pode ser vazio.")

        normalizado = self._normalizar(texto_limpo)
        return DadosTrabalhistasExtraidos(
            intencao=self._classificar_intencao(normalizado),
            datas=self._extrair_datas(texto_limpo),
            valores=self._extrair_valores(texto_limpo),
            tipo_rescisao=self._classificar_rescisao(normalizado),
        )

    @staticmethod
    def _normalizar(texto: str) -> str:
        sem_acentos = "".join(
            caractere
            for caractere in unicodedata.normalize("NFD", texto.casefold())
            if unicodedata.category(caractere) != "Mn"
        )
        return " ".join(sem_acentos.split())

    def _classificar_intencao(self, texto: str) -> IntencaoTrabalhista:
        for intencao, padroes in self._PADROES_INTENCAO:
            if any(padrao in texto for padrao in padroes):
                return intencao
        return IntencaoTrabalhista.DESCONHECIDA

    def _classificar_rescisao(self, texto: str) -> TipoRescisao | None:
        for tipo, padroes in self._PADROES_RESCISAO:
            if any(padrao in texto for padrao in padroes):
                return tipo
        return None

    def _extrair_datas(self, texto: str) -> tuple[date, ...]:
        datas: list[date] = []
        for dia, mes, ano in self._DATA.findall(texto):
            try:
                valor = date(int(ano), int(mes), int(dia))
            except ValueError:
                continue
            if valor not in datas:
                datas.append(valor)
        return tuple(datas)

    def _extrair_valores(self, texto: str) -> tuple[Decimal, ...]:
        valores: list[Decimal] = []
        for bruto in self._VALOR.findall(texto):
            # Evita capturar partes de datas simples e anos isolados.
            if "," not in bruto and "." not in bruto:
                continue
            normalizado = bruto.replace(".", "").replace(",", ".")
            try:
                valor = Decimal(normalizado)
            except InvalidOperation:
                continue
            if valor not in valores:
                valores.append(valor)
        return tuple(valores)
