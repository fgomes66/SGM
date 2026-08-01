# ADR-033 — Teste executável da composição da GUI

## Status

Aceita.

## Decisão

Métodos de composição da interface serão executados em testes com widgets
simulados, além da inspeção estrutural já existente.

## Consequência

Erros de atributo durante a inicialização da janela são detectados sem
depender de um servidor gráfico.
