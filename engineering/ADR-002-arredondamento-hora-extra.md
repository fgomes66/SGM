# ADR-002 — Arredondamento das horas extras

## Status

Aceita.

## Decisão

O valor da hora normal e o valor da hora com adicional permanecem com
precisão interna `Decimal`. O arredondamento para centavos ocorre apenas
após a multiplicação pela quantidade total da verba.

## Motivo

Arredondamentos intermediários podem produzir diferenças acumuladas,
especialmente em períodos longos ou quantidades fracionárias.

## Aplicação

`ServicoHoraExtra` executa:

1. acréscimo percentual;
2. conversão exata de minutos para horas;
3. multiplicação;
4. arredondamento final.
