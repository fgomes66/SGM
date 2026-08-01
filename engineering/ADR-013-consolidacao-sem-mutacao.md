# ADR-013 — Consolidação sem mutação dos resultados mensais

## Status

Aceita.

## Decisão

A consolidação apenas ordenará, somará e apresentará resultados mensais
imutáveis. Nenhum resultado de competência será recalculado ou alterado.

## Motivo

Isso preserva rastreabilidade, permite auditoria individual e separa a
execução mensal da etapa de totalização.
