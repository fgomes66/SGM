# ADR-026 — Formulário processual adaptado ao domínio

## Status

Aceita.

## Decisão

A interface coleta texto, mas a validação final e a normalização são
executadas pelos objetos `OrgaoJulgador` e `IdentificacaoProcesso`.

## Motivo

Isso impede que a interface replique ou contradiga regras já homologadas.
