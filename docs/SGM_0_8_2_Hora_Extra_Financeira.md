# SGM 0.8.2 — Serviço de Horas Extras

## Fórmula

```text
FM-HE-001

Valor total =
    valor da hora normal
    × (1 + adicional)
    × quantidade exata de horas
```

## Conversão da quantidade

A quantidade continua armazenada em minutos. A conversão financeira é:

```text
horas exatas = minutos ÷ 60
```

O serviço não utiliza a propriedade de exibição em horas decimais
arredondadas. Isso evita perda de precisão em quantidades fracionárias.

## Arredondamento

- valor da hora normal: não arredondado;
- valor da hora com adicional: não arredondado;
- multiplicação pela quantidade: não arredondada;
- total da verba: arredondado para centavos por `ROUND_HALF_UP`.

## Componentes

- `TipoAdicionalHoraExtra`
- `AdicionalHoraExtra`
- `HoraExtraFinanceira`
- `ServicoHoraExtra`

## Limites desta versão

A release calcula uma verba homogênea, com um único adicional e uma
quantidade já apurada. Ainda não separa domingos, feriados, faixas
noturnas, adicionais convencionais por período ou reflexos.
