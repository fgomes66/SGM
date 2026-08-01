# ADR-009 — Fatores externos para correção e juros

## Status

Aceita.

## Decisão

O domínio financeiro receberá fatores acumulados já identificados por
período, fonte e fundamento. Índices e taxas não serão codificados como
constantes jurídicas.

## Motivo

Critérios de atualização podem mudar por título, período e decisão.
Separar a obtenção do fator da operação matemática evita regras ocultas
e preserva a reprodutibilidade.
