from __future__ import annotations

from sgm.dominio.trabalhista.atualizacao import ServicoAtualizacao
from sgm.dominio.trabalhista.aviso_previo import ServicoAvisoPrevio
from sgm.dominio.trabalhista.decimo_terceiro import (
    ServicoDecimoTerceiro,
)
from sgm.dominio.trabalhista.dependencias import CodigoVerba
from sgm.dominio.trabalhista.dsr import ServicoReflexoDSR
from sgm.dominio.trabalhista.ferias import ServicoFerias
from sgm.dominio.trabalhista.fgts import ServicoFGTS
from sgm.dominio.trabalhista.horas_extras_financeiras import (
    ServicoHoraExtra,
)
from sgm.dominio.trabalhista.incidencias import (
    ParcelaIncidencia,
    ServicoComposicaoBase,
    TipoBaseIncidencia,
)
from sgm.dominio.trabalhista.jornada_financeira import (
    ServicoValorHora,
)
from sgm.dominio.trabalhista.liquidacao.liquidacao_trabalhista import (
    LiquidacaoTrabalhista,
)
from sgm.dominio.trabalhista.liquidacao.memoria_calculo import (
    MemoriaCalculo,
)
from sgm.dominio.trabalhista.liquidacao.plano_liquidacao_integrada import (
    PlanoLiquidacaoIntegrada,
)
from sgm.dominio.trabalhista.liquidacao.verba_liquidada import (
    VerbaLiquidada,
)


class MotorLiquidacaoTrabalhista:
    VERSAO = "0.9.0"

    @classmethod
    def _configuracao(
        cls,
        plano: PlanoLiquidacaoIntegrada,
        verba: CodigoVerba,
        base: TipoBaseIncidencia,
    ):
        encontradas = tuple(
            item
            for item in plano.configuracoes_incidencia
            if item.verba_origem == verba
            and item.regra.base_destino == base
        )

        if len(encontradas) != 1:
            raise ValueError(
                "Deve existir exatamente uma configuração para "
                f"{verba.value} → {base.value}."
            )

        return encontradas[0]

    @classmethod
    def _compor_base(
        cls,
        plano: PlanoLiquidacaoIntegrada,
        base_destino: TipoBaseIncidencia,
        horas_extras,
        dsr,
    ):
        config_he = cls._configuracao(
            plano,
            CodigoVerba.HORA_EXTRA,
            base_destino,
        )
        config_dsr = cls._configuracao(
            plano,
            CodigoVerba.DSR,
            base_destino,
        )

        parcelas = (
            ParcelaIncidencia(
                verba=CodigoVerba.HORA_EXTRA,
                valor=horas_extras.valor_total,
                regra=config_he.regra,
                descricao="Horas extras apuradas",
            ),
            ParcelaIncidencia(
                verba=CodigoVerba.DSR,
                valor=dsr.valor,
                regra=config_dsr.regra,
                descricao="Reflexo das horas extras em DSR",
            ),
        )

        return ServicoComposicaoBase.compor(
            base_destino,
            parcelas,
        )

    @classmethod
    def calcular(
        cls,
        plano: PlanoLiquidacaoIntegrada,
    ) -> LiquidacaoTrabalhista:
        valor_hora = ServicoValorHora.calcular(
            plano.base_remuneratoria,
            plano.divisor_jornada,
        )

        horas_extras = ServicoHoraExtra.calcular(
            valor_hora,
            plano.quantidade_horas_extras,
            plano.adicional_hora_extra,
        )

        dsr = ServicoReflexoDSR.calcular(
            horas_extras,
            plano.parametros_dsr,
        )

        base_fgts = cls._compor_base(
            plano,
            TipoBaseIncidencia.FGTS,
            horas_extras,
            dsr,
        )
        fgts = ServicoFGTS.calcular(
            base_fgts,
            plano.aliquota_fgts,
        )

        base_ferias = cls._compor_base(
            plano,
            TipoBaseIncidencia.FERIAS,
            horas_extras,
            dsr,
        )
        ferias = ServicoFerias.calcular(
            base_ferias,
            plano.parametros_ferias,
        )

        base_decimo = cls._compor_base(
            plano,
            TipoBaseIncidencia.DECIMO_TERCEIRO,
            horas_extras,
            dsr,
        )
        decimo = ServicoDecimoTerceiro.calcular(
            base_decimo,
            plano.parametros_decimo_terceiro,
        )

        base_aviso = cls._compor_base(
            plano,
            TipoBaseIncidencia.AVISO_PREVIO,
            horas_extras,
            dsr,
        )
        aviso = ServicoAvisoPrevio.calcular(
            base_aviso,
            plano.parametros_aviso_previo,
        )

        verbas = (
            VerbaLiquidada(
                CodigoVerba.HORA_EXTRA,
                "Horas extras",
                horas_extras.valor_total,
                horas_extras.formula_codigo,
            ),
            VerbaLiquidada(
                CodigoVerba.DSR,
                "Reflexo em DSR",
                dsr.valor,
                dsr.formula_codigo,
            ),
            VerbaLiquidada(
                CodigoVerba.FGTS,
                "FGTS",
                fgts.valor,
                fgts.formula_codigo,
            ),
            VerbaLiquidada(
                CodigoVerba.FERIAS,
                "Férias acrescidas do terço",
                ferias.valor_total,
                ferias.formula_ferias_codigo,
            ),
            VerbaLiquidada(
                CodigoVerba.DECIMO_TERCEIRO,
                "13º salário",
                decimo.valor,
                decimo.formula_codigo,
            ),
            VerbaLiquidada(
                CodigoVerba.AVISO_PREVIO,
                "Aviso-prévio",
                aviso.valor,
                aviso.formula_codigo,
            ),
        )

        subtotal = verbas[0].valor
        for verba in verbas[1:]:
            subtotal = subtotal.somar(verba.valor)
        subtotal = subtotal.arredondar_centavos()

        atualizacao = ServicoAtualizacao.aplicar_correcao_e_juros(
            subtotal,
            plano.fator_correcao,
            plano.fator_juros,
        )

        linhas = [
            f"Processo: {plano.processo_referencia}",
            f"Modo: {plano.modo.value}",
            f"Versão do motor: {cls.VERSAO}",
            "",
            "1. VALOR DA HORA",
            *valor_hora.memoria_resumida(),
            "",
            "2. HORAS EXTRAS",
            *horas_extras.memoria_resumida(),
            "",
            "3. REFLEXO EM DSR",
            *dsr.memoria_resumida(),
            "",
            "4. FGTS",
            *fgts.memoria_resumida(),
            "",
            "5. FÉRIAS",
            *ferias.memoria_resumida(),
            "",
            "6. 13º SALÁRIO",
            *decimo.memoria_resumida(),
            "",
            "7. AVISO-PRÉVIO",
            *aviso.memoria_resumida(),
            "",
            "8. RESUMO DAS VERBAS",
        ]

        for verba in verbas:
            linhas.append(
                f"{verba.descricao}: "
                f"{verba.valor.moeda} "
                f"{format(verba.valor.valor, 'f')}"
            )

        linhas.extend(
            (
                (
                    "Subtotal: "
                    f"{subtotal.moeda} "
                    f"{format(subtotal.valor, 'f')}"
                ),
                "",
                "9. ATUALIZAÇÃO E JUROS",
                *atualizacao.memoria_resumida(),
            )
        )

        memoria = MemoriaCalculo(
            titulo="MEMÓRIA DE CÁLCULO — SGM",
            linhas=tuple(linhas),
            lema=plano.lema_memoria,
        )

        return LiquidacaoTrabalhista(
            plano=plano,
            valor_hora=valor_hora,
            horas_extras=horas_extras,
            dsr=dsr,
            base_fgts=base_fgts,
            fgts=fgts,
            base_ferias=base_ferias,
            ferias=ferias,
            base_decimo_terceiro=base_decimo,
            decimo_terceiro=decimo,
            base_aviso_previo=base_aviso,
            aviso_previo=aviso,
            verbas=verbas,
            subtotal=subtotal,
            atualizacao=atualizacao,
            valor_final=atualizacao.valor_final,
            memoria=memoria,
            versao_motor=cls.VERSAO,
        )
