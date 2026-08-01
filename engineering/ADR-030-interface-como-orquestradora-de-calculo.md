# ADR-030 — Interface como orquestradora de cálculo

## Status

Aceita.

## Decisão

A interface não reproduzirá fórmulas. Ela preparará os objetos de domínio
e chamará os serviços já homologados de valor-hora e horas extras.

## Consequência

As fórmulas permanecem centralizadas e auditáveis no backend.
