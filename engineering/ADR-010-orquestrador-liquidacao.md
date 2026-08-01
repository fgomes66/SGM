# ADR-010 — Orquestrador de liquidação

## Status

Aceita.

## Decisão

A integração entre os motores será realizada por um orquestrador que
recebe um plano integralmente parametrizado. Os motores especializados
permanecem independentes e não chamam uns aos outros diretamente.

## Consequências

- ordem de execução explícita;
- menor acoplamento;
- resultados intermediários preservados;
- memória única de ponta a ponta;
- possibilidade futura de cenários, auditoria e execução parcial.
