# ADR-001 — Serviços de domínio não executam matemática

## Status

Aceita.

## Decisão

Serviços de domínio coordenam objetos e fluxos. Operações monetárias
permanecem no Core Financeiro.

## Aplicação na versão 0.8.1

`ServicoValorHora` chama `ValorMonetario.dividir()` e encapsula o
resultado em `ValorHora`.

## Consequência

A operação financeira permanece centralizada, testável, auditável e
reutilizável.
