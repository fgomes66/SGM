# ADR-027 — Persistência JSON com gravação atômica

## Status

Aceita.

## Decisão

A primeira persistência do SGM Desktop utilizará arquivos JSON, um por
processo, gravados por substituição atômica.

## Motivo

O formato é simples, auditável e suficiente antes da futura camada
SQLite. A gravação atômica reduz o risco de arquivo parcial.
