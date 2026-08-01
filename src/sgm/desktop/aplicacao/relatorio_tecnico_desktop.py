from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from hashlib import sha256

from sgm.desktop.aplicacao.calculo_desktop import ResultadoCalculoDesktop
from sgm.desktop.aplicacao.contrato_trabalho import ContratoTrabalho
from sgm.desktop.aplicacao.evento_contratual_desktop import (
    EventoContratualDesktop,
)
from sgm.desktop.aplicacao.memoria_calculo_desktop import (
    ServicoMemoriaCalculoDesktop,
)
from sgm.desktop.aplicacao.premissas_tecnicas_desktop import (
    PremissasTecnicasBuilderDesktop,
)
from sgm.relatorio import IdentificacaoProcesso


def _moeda(valor: Decimal, casas: int = 2) -> str:
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def _numero(valor: Decimal, casas: int = 6) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def _data_br(data) -> str:
    return data.strftime("%d/%m/%Y")


@dataclass(frozen=True, slots=True)
class RelatorioTecnicoDesktop:
    referencia: str
    versao: str
    gerado_em: datetime
    conteudo: str
    identificador: str
    total_geral: Decimal

    def __post_init__(self) -> None:
        referencia = self.referencia.strip()
        versao = self.versao.strip()
        conteudo = self.conteudo.strip()
        identificador = self.identificador.strip().lower()

        object.__setattr__(self, "referencia", referencia)
        object.__setattr__(self, "versao", versao)
        object.__setattr__(self, "conteudo", conteudo)
        object.__setattr__(self, "identificador", identificador)

        if not referencia:
            raise ValueError("A referência do relatório é obrigatória.")
        if not versao:
            raise ValueError("A versão do relatório é obrigatória.")
        if not conteudo:
            raise ValueError("O conteúdo do relatório é obrigatório.")
        if len(identificador) != 64:
            raise ValueError("O identificador deve ser um SHA-256.")
        if not isinstance(self.total_geral, Decimal):
            raise TypeError("O total geral deve ser Decimal.")
        if self.total_geral < 0:
            raise ValueError("O total geral não pode ser negativo.")


class ServicoRelatorioTecnicoDesktop:
    VERSAO = "0.9.3-G1"
    MOTOR = "ServicoValorHora + ServicoHoraExtra"

    @classmethod
    def validar_dados(
        cls,
        referencia: str | None,
        identificacao: IdentificacaoProcesso | None,
        contrato: ContratoTrabalho | None,
        resultados: tuple[ResultadoCalculoDesktop, ...],
    ) -> tuple[str, ...]:
        erros: list[str] = []
        if not referencia or not referencia.strip():
            erros.append("Abra ou crie um processo.")
        if identificacao is None:
            erros.append("Registre os dados processuais.")
        if contrato is None:
            erros.append("Registre o contrato de trabalho.")
        if not resultados:
            erros.append("Execute ao menos um cálculo.")
        return tuple(erros)

    @classmethod
    def gerar(
        cls,
        referencia: str,
        identificacao: IdentificacaoProcesso,
        contrato: ContratoTrabalho,
        eventos: tuple[EventoContratualDesktop, ...],
        resultados: tuple[ResultadoCalculoDesktop, ...],
        gerado_em: datetime | None = None,
    ) -> RelatorioTecnicoDesktop:
        erros = cls.validar_dados(
            referencia,
            identificacao,
            contrato,
            resultados,
        )
        if erros:
            raise ValueError(" ".join(erros))

        instante = gerado_em or datetime.now()
        eventos_ordenados = tuple(
            sorted(eventos, key=lambda item: item.chave_ordenacao)
        )
        resultados_ordenados = tuple(
            sorted(
                resultados,
                key=lambda item: (item.competencia, str(item.id)),
            )
        )
        total = sum(
            (item.valor_total for item in resultados_ordenados),
            Decimal("0"),
        )

        linhas: list[str] = [
            "=" * 72,
            "RELATÓRIO TÉCNICO DE CÁLCULOS TRABALHISTAS",
            "=" * 72,
            "",
            f"SGM Desktop — Versão {cls.VERSAO}",
            f"Emissão: {instante.strftime('%d/%m/%Y %H:%M:%S')}",
            "",
            "-" * 72,
            "1. IDENTIFICAÇÃO DO PROCESSO",
            "-" * 72,
            f"Referência interna: {referencia.strip()}",
            f"Processo CNJ: {identificacao.numero_processo}",
            f"Tribunal: {identificacao.orgao_julgador.tribunal}",
            f"Região do TRT: {identificacao.orgao_julgador.regiao_trt}",
            f"Vara: {identificacao.orgao_julgador.vara}",
            (
                "Localidade: "
                f"{identificacao.orgao_julgador.municipio}/"
                f"{identificacao.orgao_julgador.uf}"
            ),
            f"Classe processual: {identificacao.classe_processual}",
            f"Reclamante: {identificacao.reclamante}",
            f"Reclamada: {identificacao.reclamada}",
        ]

        if identificacao.magistrado:
            linhas.append(f"Magistrado(a): {identificacao.magistrado}")
        if identificacao.perito:
            linhas.append(f"Perito/Calculista: {identificacao.perito}")

        linhas.extend(
            [
                "",
                "-" * 72,
                "2. SÍNTESE DO CONTRATO DE TRABALHO",
                "-" * 72,
                f"Admissão: {_data_br(contrato.data_admissao)}",
                (
                    "Desligamento: "
                    + (
                        _data_br(contrato.data_desligamento)
                        if contrato.data_desligamento
                        else "não informado"
                    )
                ),
                f"Tipo de contrato: {contrato.tipo_contrato.titulo}",
                f"Cargo: {contrato.cargo}",
                f"Função: {contrato.funcao}",
                f"CBO: {contrato.cbo or 'não informado'}",
                f"Salário inicial: R$ {_moeda(contrato.salario_inicial)}",
                (
                    "Jornada semanal: "
                    f"{_numero(contrato.jornada_semanal_horas, 2)} horas"
                ),
                f"Divisor contratual: {_numero(contrato.divisor_jornada, 2)}",
                f"Sindicato: {contrato.sindicato or 'não informado'}",
                (
                    "Norma coletiva: "
                    f"{contrato.norma_coletiva or 'não informada'}"
                ),
                "",
                "-" * 72,
                "3. EVENTOS CONTRATUAIS CONSIDERADOS",
                "-" * 72,
            ]
        )

        if not eventos_ordenados:
            linhas.append("Nenhum evento contratual adicional registrado.")
        else:
            for indice, evento in enumerate(eventos_ordenados, start=1):
                periodo = _data_br(evento.data_inicio)
                if evento.data_fim:
                    periodo += f" a {_data_br(evento.data_fim)}"
                linhas.extend(
                    [
                        f"{indice}. {evento.tipo.titulo} — {periodo}",
                        f"   Descrição: {evento.descricao}",
                        f"   Fundamento/Motivo: {evento.fundamento}",
                    ]
                )
                if evento.valor is not None:
                    linhas.append(
                        f"   Valor: R$ {_moeda(evento.valor)}"
                    )
                if evento.documento:
                    linhas.append(f"   Documento: {evento.documento}")
                for chave, valor in evento.dados.items():
                    linhas.append(f"   {chave}: {valor}")

        linhas.extend(
            [
                "",
                "-" * 72,
                "4. PREMISSAS TÉCNICAS",
                "-" * 72,
            ]
        )

        for indice, resultado in enumerate(resultados_ordenados, start=1):
            premissas = PremissasTecnicasBuilderDesktop.construir(
                contrato,
                eventos_ordenados,
                resultado,
            )
            linhas.extend(
                [
                    "",
                    f"4.{indice}. {premissas.verba.upper()}",
                    f"Competência: {_data_br(premissas.competencia)}",
                    f"Motor: {premissas.motor}",
                    f"Versão do Engine: {premissas.versao_motor}",
                    f"Fórmula oficial: {premissas.formula}",
                    f"Versão da fórmula: {premissas.versao_formula}",
                    (
                        "Salário originalmente contratado: R$ "
                        f"{_moeda(premissas.salario_inicial)}"
                    ),
                    (
                        "Salário vigente na competência: R$ "
                        f"{_moeda(premissas.salario_vigente)}"
                    ),
                    f"Origem da base salarial: {premissas.origem_base}",
                ]
            )
            if premissas.evento_base:
                linhas.append(f"Evento considerado: {premissas.evento_base}")
            linhas.extend(
                [
                    f"Divisor contratual: {_numero(premissas.divisor, 2)}",
                    (
                        "Jornada semanal: "
                        f"{_numero(premissas.jornada_semanal, 2)} horas"
                    ),
                    (
                        "Quantidade utilizada: "
                        f"{_numero(premissas.quantidade, 2)} horas"
                    ),
                    (
                        "Percentual aplicado: "
                        f"{_numero(premissas.adicional_percentual * 100, 2)}%"
                    ),
                    (
                        "Critério de arredondamento: "
                        f"{premissas.criterio_arredondamento}"
                    ),
                    (
                        "Precisão intermediária: "
                        f"{premissas.precisao_intermediaria} casas decimais"
                    ),
                    (
                        "Precisão monetária: "
                        f"{premissas.precisao_monetaria} casas decimais"
                    ),
                    "Fundamentação jurídica:",
                ]
            )
            linhas.extend(
                f"  • {item.descricao}" for item in premissas.fundamentos
            )
            linhas.append("Fontes de dados utilizadas:")
            linhas.extend(
                f"  ✓ {item.descricao}" for item in premissas.fontes
            )

        linhas.extend(
            [
                "",
                "-" * 72,
                "5. DEMONSTRATIVO FINANCEIRO",
                "-" * 72,
                "Código | Verba | Competência | Base salarial | Valor",
            ]
        )
        for resultado in resultados_ordenados:
            linhas.append(
                f"{resultado.formula_codigo} | Horas Extras | "
                f"{_data_br(resultado.competencia)} | "
                f"R$ {_moeda(resultado.salario_base)} | "
                f"R$ {_moeda(resultado.valor_total)}"
            )
        linhas.append(f"TOTAL GERAL | R$ {_moeda(total)}")

        linhas.extend(
            [
                "",
                "-" * 72,
                "6. MEMÓRIA TÉCNICA RESUMIDA",
                "-" * 72,
            ]
        )
        for indice, resultado in enumerate(resultados_ordenados, start=1):
            memoria = ServicoMemoriaCalculoDesktop.gerar(resultado)
            linhas.extend(
                [
                    "",
                    f"6.{indice}. HORAS EXTRAS",
                    f"Competência: {_data_br(resultado.competencia)}",
                    f"Fórmula: {resultado.formula_codigo}",
                    f"Fundamento: {resultado.fundamento}",
                    f"Valor da hora normal: R$ {_numero(resultado.valor_hora, 6)}",
                    (
                        "Valor da hora extra: R$ "
                        f"{_numero(resultado.valor_hora_com_adicional, 6)}"
                    ),
                    f"Resultado: R$ {_moeda(resultado.valor_total)}",
                ]
            )
            for passo in memoria.passos:
                linhas.extend(
                    [
                        f"  Passo {passo.ordem} — {passo.titulo}",
                        f"  Expressão: {passo.expressao}",
                        f"  Resultado: {passo.resultado}",
                    ]
                )

        linhas.extend(
            [
                "",
                "-" * 72,
                "7. CONCLUSÃO TÉCNICA",
                "-" * 72,
                (
                    "Com base nos dados processuais e contratuais "
                    "registrados, nos eventos considerados e nos resultados "
                    "produzidos pelo motor do SGM Desktop, apura-se o total "
                    f"de R$ {_moeda(total)} para os cálculos demonstrados."
                ),
                (
                    "Este relatório reproduz os resultados persistidos e "
                    "suas memórias técnicas, sem executar novo cálculo nem "
                    "alterar bases, critérios ou valores."
                ),
                "",
                "-" * 72,
                "8. RASTREABILIDADE",
                "-" * 72,
                f"Motor: {cls.MOTOR}",
                f"Versão do relatório: {cls.VERSAO}",
                (
                    "Origem dos dados: Processo → Contrato → Eventos → "
                    "Cálculo → Memória"
                ),
                "Documento gerado automaticamente pelo SGM Desktop.",
            ]
        )

        conteudo_sem_id = "\n".join(linhas)
        identificador = sha256(
            conteudo_sem_id.encode("utf-8")
        ).hexdigest()
        linhas.extend(
            [
                f"Identificador SHA-256: {identificador}",
                "=" * 72,
            ]
        )
        conteudo = "\n".join(linhas)

        return RelatorioTecnicoDesktop(
            referencia=referencia,
            versao=cls.VERSAO,
            gerado_em=instante,
            conteudo=conteudo,
            identificador=identificador,
            total_geral=total,
        )
