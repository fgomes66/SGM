# ADR-005 — FGTS separado da multa rescisória

## Status

Aceita.

## Decisão

O motor desta release calcula exclusivamente o valor do FGTS sobre uma
base de incidência parametrizada. A multa rescisória será objeto próprio.

## Motivo

Depósito de FGTS e multa rescisória possuem bases, momentos e critérios
potencialmente distintos. Mantê-los separados melhora rastreabilidade,
testabilidade e explicabilidade.
