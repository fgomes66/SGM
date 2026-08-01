# ADR-032 — Autosave transacional do caso

## Status

Aceita.

## Decisão

Toda mutação válida do caso será seguida de persistência automática do
registro completo.

## Consequência

Processo, contrato, eventos e resultados permanecem sincronizados no
mesmo arquivo. A interface não depende mais exclusivamente da sessão.
