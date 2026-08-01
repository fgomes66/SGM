# ADR-003 — Grafo de dependências entre verbas

## Status

Aceita.

## Decisão

As relações entre verbas serão registradas em um grafo dirigido
acíclico. A inclusão de uma relação que forme ciclo será rejeitada.

## Motivo

O grafo permite:

- determinar a ordem de cálculo;
- localizar verbas afetadas por alterações;
- evitar chamadas diretas e acoplamento entre serviços;
- preparar comparações de cenários e recálculos seletivos.
