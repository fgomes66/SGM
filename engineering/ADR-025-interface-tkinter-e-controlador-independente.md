# ADR-025 — Tkinter e controlador independente da interface

## Status

Aceita.

## Decisão

A interface desktop utilizará Tkinter e manterá estado e navegação em
classes testáveis sem dependência de uma janela gráfica ativa.

## Motivo

Tkinter acompanha o Python no Windows, reduz dependências e permite que
a lógica de apresentação seja validada em ambientes sem monitor.
