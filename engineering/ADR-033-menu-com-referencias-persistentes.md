# ADR-033 — Menus Tk com referências persistentes

## Status
Aceita.

## Decisão
A janela manterá referências de instância para a barra de menu e seus
submenus, além de oferecer comandos equivalentes em uma barra visível.

## Consequência
O gerenciamento de processos permanece acessível mesmo em ambientes onde
o menu nativo do Tk apresente comportamento inconsistente.
