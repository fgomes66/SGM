# ADR-006 — Férias e terço como componentes separados

## Status

Aceita.

## Decisão

O valor das férias e o terço serão apurados como objetos monetários
distintos e consolidados somente ao final.

## Motivo

A separação permite:

- explicar cada parcela;
- aplicar incidências distintas futuramente;
- auditar arredondamentos;
- suportar cenários proporcionais;
- evitar mistura com dobra e abono pecuniário.
