# SGM 0.8.8 — Motor do Aviso-Prévio

## Fórmula

```text
FM-AVP-001

aviso-prévio =
    base do aviso
    × dias do aviso
    ÷ dias do mês de cálculo
```

## Componentes

- `TipoAvisoPrevio`
- `ParametrosAvisoPrevio`
- `AvisoPrevioApurado`
- `ServicoAvisoPrevio`

## Regras

- a base deve ser do tipo `AVISO_PREVIO`;
- o tipo pode ser trabalhado ou indenizado;
- a quantidade de dias é parametrizada;
- o divisor mensal é parametrizado;
- nenhuma quantidade de dias é presumida;
- o resultado é arredondado para centavos ao final.

## Limites desta release

Esta entrega não calcula:

- projeção do contrato;
- reflexos da projeção;
- indenização adicional;
- desconto por ausência de cumprimento;
- redução de jornada;
- repercussões em férias, 13º ou FGTS;
- regras rescisórias específicas.

Esses cenários serão modelados separadamente.
