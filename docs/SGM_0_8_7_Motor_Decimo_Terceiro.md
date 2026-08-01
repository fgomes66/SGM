# SGM 0.8.7 — Motor do 13º Salário

## Fórmula

```text
FM-13-001

13º salário = base do 13º × avos ÷ 12
```

## Componentes

- `ParametrosDecimoTerceiro`
- `DecimoTerceiroApurado`
- `ServicoDecimoTerceiro`

## Regras

- a base deve ser do tipo `DECIMO_TERCEIRO`;
- os avos devem estar entre 0 e 12;
- cada parcela da base deve possuir regra de incidência explícita;
- o valor é arredondado para centavos ao final.

## Limites desta release

Esta entrega não calcula:

- primeira parcela ou adiantamento;
- segunda parcela;
- descontos;
- médias por competência;
- 13º rescisório com regras específicas;
- tributação previdenciária ou fiscal.

Esses cenários serão modelados separadamente.
