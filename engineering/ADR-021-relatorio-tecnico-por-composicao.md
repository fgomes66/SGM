# ADR-021 — Relatório técnico por composição

## Status

Aceita.

## Decisão

O gerador montará o relatório por seções independentes, consumindo
somente documentos e metadados previamente homologados.

## Motivo

A composição mantém as responsabilidades separadas, evita duplicação de
regras e permite que renderizadores futuros usem uma única fonte textual.
