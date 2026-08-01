# ADR-012 — Execução isolada por competência

## Status

Aceita.

## Decisão

Cada competência será calculada por um plano próprio e produzirá um
resultado imutável. O motor por competência delega o cálculo financeiro
ao motor integrado 0.9.0.

## Motivo

A delegação evita duplicar fórmulas e garante que alterações em uma
competência não modifiquem competências anteriores.
