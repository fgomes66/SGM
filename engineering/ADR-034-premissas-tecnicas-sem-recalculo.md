# ADR-034 — Premissas técnicas sem recálculo

## Status

Aceita.

## Decisão

As premissas do relatório são construídas exclusivamente a partir do contrato,
dos eventos e dos resultados persistidos. O builder não executa o motor de
cálculo nem altera os objetos recebidos.

## Consequência

O relatório passa a documentar origem da base salarial, fórmula, versão,
fundamentos, arredondamento e fontes de dados sem criar divergência financeira.
