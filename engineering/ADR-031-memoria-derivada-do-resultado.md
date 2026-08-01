# ADR-031 — Memória derivada do resultado homologado

## Status

Aceita.

## Decisão

A memória de cálculo será construída exclusivamente a partir do objeto de
resultado persistido.

## Consequência

A camada de apresentação não recalcula valores e não duplica fórmulas do
motor. Cálculo, memória e futuros relatórios permanecem consistentes.
