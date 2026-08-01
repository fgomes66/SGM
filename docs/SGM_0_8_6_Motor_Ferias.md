# SGM 0.8.6 — Motor de Férias

## Fórmulas

```text
FM-FER-001

férias = base de férias × avos ÷ 12
```

```text
FM-FER-002

terço = férias apuradas × percentual do terço
```

```text
total = férias + terço
```

## Componentes

- `ParametrosFerias`
- `FeriasApuradas`
- `ServicoFerias`

## Regras

- a base deve ser do tipo `FERIAS`;
- os avos devem estar entre 0 e 12;
- o percentual do terço é parametrizado;
- cada parcela da base deve possuir regra de incidência explícita;
- os resultados são arredondados para centavos nas etapas monetárias.

## Limites desta release

Esta entrega não calcula:

- dobra de férias;
- abono pecuniário;
- férias vencidas em períodos múltiplos;
- redução de dias por faltas;
- indenizações específicas;
- descontos previdenciários ou fiscais.

Esses cenários serão modelados separadamente.
