# ADR-015 — Pipeline temporal completo

## Status

Aceita.

## Decisão

O fluxo temporal será composto por serviços especializados e imutáveis:

- aplicação de eventos;
- cálculo mensal;
- consolidação;
- memória final.

## Motivo

A separação permite testar cada fase isoladamente e, simultaneamente,
executar um caso completo sem duplicar regras financeiras ou temporais.
