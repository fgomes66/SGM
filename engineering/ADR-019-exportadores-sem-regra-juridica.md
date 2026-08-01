# ADR-019 — Exportadores sem regra jurídica ou financeira

## Status

Aceita.

## Decisão

A camada de exportação receberá documentos prontos e somente os
serializará em formatos de arquivo.

## Motivo

Isso evita divergências entre cálculo e relatório, permite testar os
formatos isoladamente e mantém os exportadores substituíveis.
